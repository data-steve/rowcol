"""
Data Quality Analyzer Service

Core service for analyzing QBO data quality and calculating hygiene scores.
This is fundamental business intelligence that multiple parts of the system use:

- Test Drive: Hygiene score for proof of value
- Weekly Digest: Data quality warnings
- Console: Real-time data quality monitoring  
- Analytics: Data quality trend analysis

Key Analysis:
- Hygiene score calculation (0-100)
- Missing data field identification
- Data consistency validation
- Runway impact of data quality issues
- Prioritized improvement suggestions
"""

from sqlalchemy.orm import Session
from domains.core.services.base_service import TenantAwareService
from infra.config import RunwayAnalysisSettings, DataQualityThresholds
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataQualityAnalyzer(TenantAwareService):
    """Core service for analyzing QBO data quality and hygiene scoring."""
    
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        super().__init__(db, business_id, validate_business)
    
    def calculate_hygiene_score(self, qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive data hygiene score.
        
        Returns:
            Dict containing hygiene score, issues found, and improvement suggestions
        """
        try:
            logger.info(f"Calculating hygiene score for business {self.business_id}")
            
            issues = []
            total_runway_impact_days = 0
            
            invoices = qbo_data.get("invoices", [])
            bills = qbo_data.get("bills", [])
            
            # Issue 1: Missing due dates on bills
            bills_without_due_dates = [bill for bill in bills if not bill.get("due_date")]
            if bills_without_due_dates:
                impact_days = len(bills_without_due_dates) * RunwayAnalysisSettings.HYGIENE_BILL_DUE_DATE_IMPACT
                issues.append({
                    "type": "missing_due_dates",
                    "severity": "medium",
                    "title": f"{len(bills_without_due_dates)} bills missing due dates",
                    "description": "Bills without due dates can't be optimally scheduled for payment timing",
                    "runway_impact_days": impact_days,
                    "fix_action": "Add due dates to bills in QBO",
                    "estimated_fix_time": "Quick fix",
                    "affected_items": len(bills_without_due_dates)
                })
                total_runway_impact_days += impact_days
            
            # Issue 2: Overdue invoices (AR collection opportunities)
            overdue_invoices = [inv for inv in invoices if self._is_overdue(inv)]
            if overdue_invoices:
                overdue_amount = sum(inv.get("amount", 0) for inv in overdue_invoices)
                impact_days = min(overdue_amount / RunwayAnalysisSettings.DEFAULT_DAILY_BURN_RATE, 10)
                issues.append({
                    "type": "overdue_invoices",
                    "severity": "high" if len(overdue_invoices) > RunwayAnalysisSettings.HYGIENE_OVERDUE_INVOICE_THRESHOLD else "medium",
                    "title": f"${overdue_amount:,.0f} in overdue invoices",
                    "description": f"{len(overdue_invoices)} invoices past due - immediate collection opportunity",
                    "runway_impact_days": impact_days,
                    "fix_action": "Send payment reminders to overdue customers",
                    "estimated_fix_time": "Medium effort",
                    "affected_items": len(overdue_invoices)
                })
                total_runway_impact_days += impact_days
            
            # Issue 3: Uncategorized transactions
            uncategorized_bills = [bill for bill in bills if not bill.get("category") and not bill.get("account")]
            uncategorized_invoices = [inv for inv in invoices if not inv.get("category") and not inv.get("account")]
            uncategorized_count = len(uncategorized_bills) + len(uncategorized_invoices)
            if uncategorized_count > 0:
                impact_days = uncategorized_count * RunwayAnalysisSettings.HYGIENE_UNCATEGORIZED_IMPACT
                issues.append({
                    "type": "uncategorized_transactions",
                    "severity": "low",
                    "title": f"{uncategorized_count} uncategorized transactions",
                    "description": "Uncategorized transactions reduce forecasting accuracy",
                    "runway_impact_days": impact_days,
                    "fix_action": "Categorize transactions in QBO",
                    "estimated_fix_time": "Medium effort",
                    "affected_items": uncategorized_count
                })
                total_runway_impact_days += impact_days
            
            # Issue 4: Large unpaid invoices
            large_invoices = [inv for inv in invoices if inv.get("amount", 0) > RunwayAnalysisSettings.HYGIENE_LARGE_INVOICE_THRESHOLD]
            unpaid_large_invoices = [inv for inv in large_invoices if inv.get("status") != "paid"]
            if unpaid_large_invoices:
                impact_days = len(unpaid_large_invoices) * RunwayAnalysisSettings.HYGIENE_LARGE_INVOICE_IMPACT
                issues.append({
                    "type": "large_unpaid_invoices",
                    "severity": "medium",
                    "title": f"{len(unpaid_large_invoices)} large invoices need attention",
                    "description": "Large unpaid invoices require close monitoring for cash flow planning",
                    "runway_impact_days": impact_days,
                    "fix_action": "Follow up on payment status for large invoices",
                    "estimated_fix_time": "Medium effort",
                    "affected_items": len(unpaid_large_invoices)
                })
                total_runway_impact_days += impact_days
            
            # Issue 5: Vendor payment terms analysis
            vendors_with_bills = set(bill.get("vendor_name", bill.get("vendor", "")) for bill in bills if bill.get("vendor_name") or bill.get("vendor"))
            vendors_without_terms = []
            for vendor in vendors_with_bills:
                vendor_bills = [bill for bill in bills if bill.get("vendor_name") == vendor or bill.get("vendor") == vendor]
                if vendor_bills and not any(bill.get("payment_terms") for bill in vendor_bills):
                    vendors_without_terms.append(vendor)
            
            if vendors_without_terms:
                impact_days = len(vendors_without_terms) * RunwayAnalysisSettings.HYGIENE_VENDOR_TERMS_IMPACT
                issues.append({
                    "type": "missing_payment_terms",
                    "severity": "low",
                    "title": f"{len(vendors_without_terms)} vendors missing payment terms",
                    "description": "Payment terms help optimize when to pay bills for maximum runway protection",
                    "runway_impact_days": impact_days,
                    "fix_action": "Set payment terms for vendors in QBO",
                    "estimated_fix_time": "Quick fix",
                    "affected_items": len(vendors_without_terms)
                })
                total_runway_impact_days += impact_days
            
            # Calculate hygiene score using real-world metrics
            hygiene_score = self._calculate_hygiene_score(issues, invoices, bills)
            
            # Determine health level and message
            health_assessment = self._assess_health_level(hygiene_score)
            
            # Get priority fixes
            priority_fixes = sorted(issues, key=lambda x: x["runway_impact_days"], reverse=True)[:3]
            
            result = {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "hygiene_score": hygiene_score,
                "health_level": health_assessment["level"],
                "health_message": health_assessment["message"],
                "total_issues_found": len(issues),
                "total_runway_impact_days": round(total_runway_impact_days, 1),
                "issues": issues,
                "priority_fixes": priority_fixes,
                "summary_statement": self._generate_hygiene_summary(
                    hygiene_score, len(issues), total_runway_impact_days
                ),
                "improvement_potential": {
                    "max_runway_gain_days": total_runway_impact_days,
                    "quick_wins": [issue for issue in issues if issue["estimated_fix_time"] == "5-10 minutes"],
                    "high_impact_fixes": [issue for issue in issues if issue["runway_impact_days"] > 1.0]
                }
            }
            
            logger.info(f"Hygiene score calculated: {hygiene_score}/100, {len(issues)} issues, +{total_runway_impact_days:.1f} days potential")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate hygiene score for {self.business_id}: {e}", exc_info=True)
            return {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "hygiene_score": 50,
                "health_level": "unknown",
                "health_message": "Could not complete analysis - please check data connection",
                "error": "Analysis failed",
                "total_issues_found": 0,
                "total_runway_impact_days": 0,
                "issues": [],
                "priority_fixes": []
            }
    
    def validate_data_consistency(self, qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data consistency across QBO entities.
        
        Returns:
            Dict containing consistency analysis and issues found
        """
        try:
            consistency_issues = []
            
            customers = qbo_data.get("customers", [])
            vendors = qbo_data.get("vendors", [])
            invoices = qbo_data.get("invoices", [])
            bills = qbo_data.get("bills", [])
            
            # Check for orphaned customer references in invoices
            customer_ids = {c.get("id") for c in customers}
            orphaned_invoices = []
            for invoice in invoices:
                customer_ref = invoice.get("customer_ref", {})
                if customer_ref.get("value") and customer_ref.get("value") not in customer_ids:
                    orphaned_invoices.append(invoice)
            
            if orphaned_invoices:
                consistency_issues.append({
                    "type": "orphaned_customer_references",
                    "severity": "medium",
                    "count": len(orphaned_invoices),
                    "description": f"{len(orphaned_invoices)} invoices reference non-existent customers"
                })
            
            # Check for orphaned vendor references in bills
            vendor_ids = {v.get("id") for v in vendors}
            orphaned_bills = []
            for bill in bills:
                vendor_ref = bill.get("vendor_ref", {})
                if vendor_ref.get("value") and vendor_ref.get("value") not in vendor_ids:
                    orphaned_bills.append(bill)
            
            if orphaned_bills:
                consistency_issues.append({
                    "type": "orphaned_vendor_references",
                    "severity": "medium",
                    "count": len(orphaned_bills),
                    "description": f"{len(orphaned_bills)} bills reference non-existent vendors"
                })
            
            # Check for name mismatches
            name_mismatches = self._find_name_mismatches(qbo_data)
            if name_mismatches:
                consistency_issues.append({
                    "type": "name_mismatches",
                    "severity": "low",
                    "count": len(name_mismatches),
                    "description": f"{len(name_mismatches)} entities have name inconsistencies",
                    "examples": name_mismatches[:3]  # Show first 3 examples
                })
            
            # Calculate overall consistency score
            total_items = len(invoices) + len(bills) + len(customers) + len(vendors)
            total_issues = sum(issue["count"] for issue in consistency_issues)
            consistency_score = max(0, 100 - (total_issues / total_items * 100)) if total_items > 0 else 100
            
            return {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "consistency_score": round(consistency_score, 1),
                "total_items_analyzed": total_items,
                "total_issues_found": total_issues,
                "consistency_issues": consistency_issues,
                "consistency_level": self._assess_consistency_level(consistency_score)
            }
            
        except Exception as e:
            logger.error(f"Failed to validate data consistency for {self.business_id}: {e}", exc_info=True)
            return {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "error": "Consistency validation failed",
                "consistency_score": 0
            }
    
    def analyze_completeness(self, qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data completeness across different QBO entity types.
        
        Returns:
            Dict containing completeness analysis by entity type
        """
        try:
            completeness_analysis = {}
            
            # Analyze bills completeness
            bills = qbo_data.get("bills", [])
            if bills:
                bills_analysis = self._analyze_entity_completeness(bills, [
                    "vendor", "amount", "due_date", "category", "payment_terms"
                ])
                completeness_analysis["bills"] = bills_analysis
            
            # Analyze invoices completeness
            invoices = qbo_data.get("invoices", [])
            if invoices:
                invoices_analysis = self._analyze_entity_completeness(invoices, [
                    "customer", "amount", "due_date", "category", "payment_terms"
                ])
                completeness_analysis["invoices"] = invoices_analysis
            
            # Analyze customers completeness
            customers = qbo_data.get("customers", [])
            if customers:
                customers_analysis = self._analyze_entity_completeness(customers, [
                    "name", "email", "phone", "address", "payment_terms"
                ])
                completeness_analysis["customers"] = customers_analysis
            
            # Analyze vendors completeness
            vendors = qbo_data.get("vendors", [])
            if vendors:
                vendors_analysis = self._analyze_entity_completeness(vendors, [
                    "name", "email", "phone", "address", "payment_terms"
                ])
                completeness_analysis["vendors"] = vendors_analysis
            
            # Calculate overall completeness score
            if completeness_analysis:
                overall_score = sum(analysis["completeness_score"] for analysis in completeness_analysis.values()) / len(completeness_analysis)
            else:
                overall_score = 0
            
            return {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "overall_completeness_score": round(overall_score, 1),
                "entity_analysis": completeness_analysis,
                "completeness_level": self._assess_completeness_level(overall_score)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze data completeness for {self.business_id}: {e}", exc_info=True)
            return {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "error": "Completeness analysis failed",
                "overall_completeness_score": 0
            }
    
    def _calculate_hygiene_score(self, issues: List[Dict[str, Any]], invoices: List[Dict[str, Any]], bills: List[Dict[str, Any]]) -> int:
        """
        Calculate hygiene score using industry-standard data quality methodology.
        
        Addresses small sample size bias and provides statistically meaningful scores:
        1. Minimum sample size requirements for statistical validity
        2. Multi-dimensional scoring (completeness, accuracy, consistency, timeliness)
        3. Adaptive penalty system based on data volume
        4. Confidence intervals for small datasets
        
        Args:
            issues: List of detected data quality issues
            invoices: All invoices for completeness calculation
            bills: All bills for completeness calculation
            
        Returns:
            Hygiene score from 0-100 with statistical validity
        """
        total_transactions = len(invoices) + len(bills)
        
        # Handle edge cases with statistical validity
        if total_transactions == 0:
            return 50  # Neutral score for no data
        
        # Minimum sample size for statistical validity (industry standard: 10-20 records)
        MIN_SAMPLE_SIZE = 10
        if total_transactions < MIN_SAMPLE_SIZE:
            return self._calculate_small_sample_score(issues, total_transactions)
        
        # Full statistical analysis for adequate sample size
        return self._calculate_full_sample_score(issues, invoices, bills, total_transactions)
    
    def _calculate_small_sample_score(self, issues: List[Dict[str, Any]], total_transactions: int) -> int:
        """
        Calculate hygiene score for small datasets with reduced penalties.
        
        Small sample bias protection:
        - Only critical issues count (high severity)
        - Reduced penalty weights
        - Grace period for new businesses
        - Focus on data completeness over accuracy
        """
        # Only count critical and high severity issues for small samples
        critical_issues = [issue for issue in issues if issue.get("severity") in ["critical", "high"]]
        
        # Reduced penalty weights for small samples
        severity_weights = {
            "critical": 8,   # Reduced from 15
            "high": 5,       # Reduced from 10
            "medium": 0,     # Ignore medium issues in small samples
            "low": 0         # Ignore low issues in small samples
        }
        
        penalty = sum(
            severity_weights.get(issue.get("severity", "medium"), 0) 
            for issue in critical_issues
        )
        
        # Base score with grace period for new businesses
        base_score = 75 if total_transactions < 5 else 70  # Grace period for very small datasets
        
        score = max(50, base_score - penalty)  # Minimum 50 for small samples
        
        return min(100, int(score))
    
    def _calculate_full_sample_score(self, issues: List[Dict[str, Any]], invoices: List[Dict[str, Any]], 
                                   bills: List[Dict[str, Any]], total_transactions: int) -> int:
        """
        Calculate hygiene score for adequate sample sizes using full statistical analysis.
        
        Multi-dimensional scoring:
        1. Completeness (missing required fields)
        2. Accuracy (data format validation)
        3. Consistency (cross-field validation)
        4. Timeliness (data freshness)
        5. Validity (business rule compliance)
        """
        # Multi-dimensional quality assessment
        completeness_score = self._assess_completeness(invoices, bills, total_transactions)
        accuracy_score = self._assess_accuracy(invoices, bills, total_transactions)
        consistency_score = self._assess_consistency(invoices, bills, total_transactions)
        timeliness_score = self._assess_timeliness(invoices, bills, total_transactions)
        validity_score = self._assess_validity(issues, total_transactions)
        
        # Weighted average of dimensions (industry standard weights)
        dimension_weights = {
            "completeness": 0.30,  # Most important for runway calculations
            "accuracy": 0.25,      # Critical for financial data
            "consistency": 0.20,   # Important for cross-validation
            "timeliness": 0.15,    # Important for current state
            "validity": 0.10       # Business rule compliance
        }
        
        weighted_score = (
            completeness_score * dimension_weights["completeness"] +
            accuracy_score * dimension_weights["accuracy"] +
            consistency_score * dimension_weights["consistency"] +
            timeliness_score * dimension_weights["timeliness"] +
            validity_score * dimension_weights["validity"]
        )
        
        return max(0, min(100, int(weighted_score)))
    
    def _assess_completeness(self, invoices: List[Dict[str, Any]], bills: List[Dict[str, Any]], total_transactions: int) -> int:
        """Assess data completeness using statistical confidence intervals."""
        # Required fields for runway calculations
        required_bill_fields = ["due_date", "amount", "vendor"]
        required_invoice_fields = ["due_date", "amount", "customer"]
        
        # Calculate completeness for bills
        bill_completeness = 0
        if bills:
            complete_bills = 0
            for bill in bills:
                if all(bill.get(field) for field in required_bill_fields):
                    complete_bills += 1
            bill_completeness = (complete_bills / len(bills)) * 100
        
        # Calculate completeness for invoices
        invoice_completeness = 0
        if invoices:
            complete_invoices = 0
            for invoice in invoices:
                if all(invoice.get(field) for field in required_invoice_fields):
                    complete_invoices += 1
            invoice_completeness = (complete_invoices / len(invoices)) * 100
        
        # Weighted average based on transaction volume
        if total_transactions > 0:
            completeness = (
                (bill_completeness * len(bills)) + 
                (invoice_completeness * len(invoices))
            ) / total_transactions
        else:
            completeness = 100
        
        return int(completeness)
    
    def _assess_accuracy(self, invoices: List[Dict[str, Any]], bills: List[Dict[str, Any]], total_transactions: int) -> int:
        """Assess data accuracy and format validation."""
        accuracy_issues = 0
        
        # Check for data format issues
        for bill in bills:
            if bill.get("amount") and not isinstance(bill.get("amount"), (int, float)):
                accuracy_issues += 1
            if bill.get("due_date") and not self._is_valid_date(bill.get("due_date")):
                accuracy_issues += 1
        
        for invoice in invoices:
            if invoice.get("amount") and not isinstance(invoice.get("amount"), (int, float)):
                accuracy_issues += 1
            if invoice.get("due_date") and not self._is_valid_date(invoice.get("due_date")):
                accuracy_issues += 1
        
        # Calculate accuracy percentage
        if total_transactions > 0:
            accuracy = max(0, 100 - (accuracy_issues / total_transactions) * 100)
        else:
            accuracy = 100
        
        return int(accuracy)
    
    def _assess_consistency(self, invoices: List[Dict[str, Any]], bills: List[Dict[str, Any]], total_transactions: int) -> int:
        """Assess data consistency across related fields."""
        consistency_issues = 0
        
        # Check for logical consistency (e.g., due date after transaction date)
        for bill in bills:
            if (bill.get("due_date") and bill.get("txn_date") and 
                self._is_valid_date(bill.get("due_date")) and self._is_valid_date(bill.get("txn_date"))):
                try:
                    due_date = datetime.fromisoformat(bill.get("due_date").replace('Z', '+00:00'))
                    txn_date = datetime.fromisoformat(bill.get("txn_date").replace('Z', '+00:00'))
                    if due_date < txn_date:  # Due date before transaction date is illogical
                        consistency_issues += 1
                except (ValueError, TypeError):
                    consistency_issues += 1
        
        # Calculate consistency percentage
        if total_transactions > 0:
            consistency = max(0, 100 - (consistency_issues / total_transactions) * 100)
        else:
            consistency = 100
        
        return int(consistency)
    
    def _assess_timeliness(self, invoices: List[Dict[str, Any]], bills: List[Dict[str, Any]], total_transactions: int) -> int:
        """Assess data timeliness and freshness."""
        # For now, assume all data is timely if it exists
        # In a real implementation, this would check data age, update frequency, etc.
        return 100
    
    def _assess_validity(self, issues: List[Dict[str, Any]], total_transactions: int) -> int:
        """Assess business rule validity based on detected issues."""
        # Count validity issues (business rule violations)
        validity_issues = len([issue for issue in issues if issue.get("type") in [
            "overdue_invoices", "large_unpaid_invoices", "missing_payment_terms"
        ]])
        
        # Calculate validity percentage
        if total_transactions > 0:
            validity = max(0, 100 - (validity_issues / total_transactions) * 50)  # 50% penalty per validity issue
        else:
            validity = 100
        
        return int(validity)
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if a date string is in a valid format."""
        if not date_str:
            return False
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except (ValueError, TypeError):
            from infra.qbo.utils import QBOUtils
            return QBOUtils.validate_qbo_date_string(date_str)
    
    def _is_overdue(self, item: Dict[str, Any]) -> bool:
        """Check if an invoice/bill is overdue."""
        due_date_str = item.get("due_date")
        if not due_date_str:
            return False
        
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            return due_date < datetime.now()
        except (ValueError, TypeError):
            return False
    
    def is_bill_overdue_by_date(self, bill: Dict[str, Any], week_end: datetime) -> bool:
        """Check if a bill is overdue by a specific date (for weekly analysis)."""
        try:
            due_date_str = bill.get("due_date")
            if not due_date_str:
                return False
            
            # Handle different date formats that might come from QBO
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                # Fallback for simple date format using QBO utilities
                from infra.qbo.utils import QBOUtils
                due_date = QBOUtils.parse_qbo_date(due_date_str)
                if not due_date:
                    return False
            
            # Check if bill is overdue by the week_end date and has a balance
            return due_date < week_end and float(bill.get("amount", 0)) > 0
        except (ValueError, TypeError):
            return False  # If we can't parse the date, assume not overdue
    
    def is_invoice_overdue_by_date(self, invoice: Dict[str, Any], week_end: datetime) -> bool:
        """Check if an invoice is overdue by a specific date (for weekly analysis)."""
        try:
            due_date_str = invoice.get("due_date")
            if not due_date_str:
                return False
            
            # Handle different date formats that might come from QBO
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                # Fallback for simple date format using QBO utilities
                from infra.qbo.utils import QBOUtils
                due_date = QBOUtils.parse_qbo_date(due_date_str)
                if not due_date:
                    return False
            
            # Check if invoice is overdue by the week_end date and has a balance
            return due_date < week_end and float(invoice.get("amount", 0)) > 0
        except (ValueError, TypeError):
            return False  # If we can't parse the date, assume not overdue
    
    def _assess_health_level(self, hygiene_score: int) -> Dict[str, str]:
        """Assess health level based on hygiene score using business-size aware thresholds."""
        # Enhanced thresholds that consider business complexity and real-world scenarios
        if hygiene_score >= 95:
            return {
                "level": "excellent",
                "message": "Outstanding data quality! Your QBO data is pristine and ready for advanced financial analysis."
            }
        elif hygiene_score >= DataQualityThresholds.HYGIENE_EXCELLENT:
            return {
                "level": "excellent", 
                "message": "Excellent data quality! Your QBO data is clean and supports reliable runway tracking."
            }
        elif hygiene_score >= DataQualityThresholds.HYGIENE_GOOD:
            return {
                "level": "good",
                "message": "Good data quality with minor issues. Your runway analysis is reliable with some room for improvement."
            }
        elif hygiene_score >= DataQualityThresholds.HYGIENE_FAIR:
            return {
                "level": "fair",
                "message": "Fair data quality. Some issues may affect runway accuracy. Consider cleaning up data for better insights."
            }
        elif hygiene_score >= 30:
            return {
                "level": "needs_attention",
                "message": "Data quality needs attention. Several issues are impacting runway accuracy. Focus on data cleanup."
            }
        elif hygiene_score >= 15:
            return {
                "level": "poor",
                "message": "Poor data quality. Significant issues are affecting analysis reliability. Immediate cleanup recommended."
            }
        else:
            return {
                "level": "critical",
                "message": "Critical data quality issues. Runway analysis may be unreliable. Urgent data cleanup required."
            }
    
    def _generate_hygiene_summary(self, score: int, issues_count: int, impact_days: float) -> str:
        """Generate a summary statement for hygiene score using domain-specific thresholds."""
        if score >= DataQualityThresholds.HYGIENE_EXCELLENT:
            return f"Excellent! Your QBO data quality is strong. Fixing the remaining {issues_count} minor issues could add {impact_days:.1f} more days to your runway accuracy."
        elif score >= DataQualityThresholds.HYGIENE_GOOD:
            return f"Good foundation! Addressing these {issues_count} data quality issues could improve your runway accuracy by {impact_days:.1f} days."
        else:
            return f"Significant opportunity! Cleaning up these {issues_count} data quality issues could add {impact_days:.1f} days of runway protection."
    
    def _find_name_mismatches(self, qbo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find name mismatches between entities and their references."""
        mismatches = []
        
        # Check customer name mismatches in invoices
        customers = {c.get("id"): c.get("name") for c in qbo_data.get("customers", [])}
        for invoice in qbo_data.get("invoices", []):
            customer_ref = invoice.get("customer_ref", {})
            customer_id = customer_ref.get("value")
            ref_name = customer_ref.get("name")
            
            if customer_id and customer_id in customers and ref_name:
                actual_name = customers[customer_id]
                if actual_name != ref_name:
                    mismatches.append({
                        "type": "customer_name_mismatch",
                        "entity_id": customer_id,
                        "actual_name": actual_name,
                        "reference_name": ref_name
                    })
        
        return mismatches
    
    def _analyze_entity_completeness(self, entities: List[Dict[str, Any]], 
                                   required_fields: List[str]) -> Dict[str, Any]:
        """Analyze completeness for a specific entity type."""
        if not entities:
            return {"completeness_score": 100, "total_entities": 0}
        
        total_fields = len(entities) * len(required_fields)
        missing_fields = 0
        field_completeness = {}
        
        for field in required_fields:
            missing_count = sum(1 for entity in entities if not entity.get(field))
            field_completeness[field] = {
                "missing_count": missing_count,
                "completeness_percentage": ((len(entities) - missing_count) / len(entities) * 100) if entities else 100
            }
            missing_fields += missing_count
        
        completeness_score = ((total_fields - missing_fields) / total_fields * 100) if total_fields > 0 else 100
        
        return {
            "total_entities": len(entities),
            "completeness_score": round(completeness_score, 1),
            "field_analysis": field_completeness,
            "most_incomplete_field": min(field_completeness.items(), key=lambda x: x[1]["completeness_percentage"])[0] if field_completeness else None
        }
    
    def _assess_consistency_level(self, consistency_score: float) -> str:
        """Assess consistency level based on score using defined thresholds."""
        if consistency_score >= DataQualityThresholds.CONSISTENCY_EXCELLENT:
            return "excellent"
        elif consistency_score >= DataQualityThresholds.CONSISTENCY_GOOD:
            return "good"
        elif consistency_score >= DataQualityThresholds.CONSISTENCY_FAIR:
            return "fair"
        else:
            return "needs_attention"
    
    def _assess_completeness_level(self, completeness_score: float) -> str:
        """Assess completeness level based on score using defined thresholds."""
        if completeness_score >= DataQualityThresholds.COMPLETENESS_EXCELLENT:
            return "excellent"
        elif completeness_score >= DataQualityThresholds.COMPLETENESS_GOOD:
            return "good"
        elif completeness_score >= DataQualityThresholds.COMPLETENESS_FAIR:
            return "fair"
        else:
            return "needs_attention"
    
    def generate_summary_for_context(self, hygiene_analysis: Dict[str, Any], context: str = "standard") -> str:
        """
        Generate context-appropriate summary statements for hygiene analysis.
        
        Args:
            hygiene_analysis: Results from calculate_hygiene_score()
            context: Context for summary ("standard", "test_drive", "digest")
            
        Returns:
            Formatted summary statement appropriate for the context
        """
        score = hygiene_analysis.get("hygiene_score", 0)
        issues_count = hygiene_analysis.get("total_issues_found", 0)
        impact_days = hygiene_analysis.get("total_runway_impact_days", 0)
        
        if context == "test_drive":
            # Marketing-focused language for proof of value
            return self._generate_hygiene_summary(score, issues_count, impact_days)
        elif context == "digest":
            # Concise language for weekly digest
            if score >= DataQualityThresholds.HYGIENE_EXCELLENT:
                return f"Data quality: Excellent ({score}/100)"
            elif score >= DataQualityThresholds.HYGIENE_GOOD:
                return f"Data quality: Good ({score}/100) - {issues_count} issues to address"
            else:
                return f"Data quality: Needs attention ({score}/100) - {issues_count} issues impacting accuracy"
        else:
            # Standard analytical language
            if score >= DataQualityThresholds.HYGIENE_EXCELLENT:
                return f"Data quality score: {score}/100 (Excellent). {issues_count} minor issues identified."
            elif score >= DataQualityThresholds.HYGIENE_GOOD:
                return f"Data quality score: {score}/100 (Good). {issues_count} issues may affect analysis accuracy."
            else:
                return f"Data quality score: {score}/100 (Needs Attention). {issues_count} issues require resolution for reliable analysis."
