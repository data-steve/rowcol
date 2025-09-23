# Oodaloo Canonical Calculation API Design

## Overview

This document defines the canonical API for all calculation logic in Oodaloo, establishing single sources of truth for each calculation type and eliminating the duplication identified in the inventory.

---

## **Core Principle: Single Responsibility**

- **Core Services** (`runway/core/services/`) own all calculation logic
- **Experience Services** (Tray, Digest, etc.) only orchestrate and present
- **Domain Services** handle entity-specific business logic, not calculations
- **No duplication** of calculation logic across services

---

## **1. RunwayCalculator** (`runway/core/services/runway_calculator.py`)

**Purpose:** All runway-related calculations and cash flow analysis

### **Core Methods (Keep & Enhance):**
```python
def calculate_current_runway(self, qbo_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calculate current runway based on latest financial data.
    
    Args:
        qbo_data: Optional QBO data dict. If None, fetches via SmartSync.
    
    Returns:
        {
            "business_id": str,
            "calculated_at": str,
            "cash_position": float,
            "ar_expected": float,
            "ap_due": float,
            "net_position": float,
            "burn_rate": {"daily_burn": float, "monthly_expenses": float, "calculation_method": str},
            "base_runway_days": float,
            "optimized_runway_days": float,
            "runway_status": str,  # "critical", "warning", "healthy", "excellent"
            "forecast_accuracy": Dict[str, Any]
        }
    """

def calculate_scenario_impact(self, scenario: Dict[str, Any], qbo_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Calculate runway impact of specific scenarios (what-if analysis)."""

def calculate_historical_runway(self, weeks_back: int = 4) -> List[Dict[str, Any]]:
    """Calculate historical runway for trend analysis and Runway Replay."""

def calculate_runway_with_reserves(self, reserve_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate runway including reserve impact.
    
    Args:
        reserve_data: Reserve allocation and availability data
    
    Returns:
        Enhanced runway calculation with reserve impact
    """
```

### **New Methods (Consolidate from other services):**
```python
def calculate_bill_runway_impact(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate runway impact of paying a specific bill.
    
    Args:
        bill_data: {"amount": float, "due_date": str, "vendor_name": str}
    
    Returns:
        {
            "impact_days": float,
            "runway_after_payment": float,
            "impact_percentage": float,
            "risk_level": str  # "low", "medium", "high"
        }
    """

def calculate_tray_item_runway_impact(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate runway impact of resolving a tray item."""
```

### **Remove (Duplicated Methods):**
- ❌ `categorize_bill_urgency()` → Move to PaymentPriorityCalculator
- ❌ `get_payment_decision_analysis()` → Move to PaymentPriorityCalculator
- ❌ `get_tray_item_impact()` → Replace with `calculate_tray_item_runway_impact()`
- ❌ `_get_decision_factors()` → Move to PaymentPriorityCalculator

---

## **2. PaymentPriorityCalculator** (`runway/core/services/payment_priority_calculator.py`)

**Purpose:** All payment prioritization and urgency calculations

### **New Canonical Service:**
```python
class PaymentPriorityCalculator(TenantAwareService):
    """Canonical service for all payment prioritization calculations."""
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.runway_calculator = RunwayCalculator(db, business_id)
    
    def calculate_bill_priority_score(self, bill_data: Dict[str, Any]) -> float:
        """
        Calculate priority score (0-100) for a bill.
        
        Args:
            bill_data: {
                "amount": float,
                "due_date": str,
                "vendor_name": str,
                "vendor_id": Optional[str],
                "bill_type": Optional[str]
            }
        
        Returns:
            float: Priority score (0-100, higher = more urgent)
        
        Business Logic:
            - Overdue: +30 base + 1.5 * days_overdue
            - Due within 7 days: +20
            - Due within 14 days: +10
            - High amount (>$5000): +10
            - Medium amount (>$2500): +5
            - Critical vendor: +15
            - High reliability vendor: +5
        """
    
    def categorize_bill_urgency(self, bill_data: Dict[str, Any]) -> str:
        """
        Categorize bill as 'must_pay' or 'can_delay'.
        
        Args:
            bill_data: Same as calculate_bill_priority_score
        
        Returns:
            str: "must_pay" or "can_delay"
        
        Business Logic:
            Must Pay Criteria (any one triggers):
            - Already overdue
            - Critical vendors (utilities, rent, payroll, taxes)
            - Critical bill types (payroll, tax, insurance, rent, utilities)
            - Large runway impact (>15% of current runway)
            - Due within 3 days
            - Would put runway below 30 days
            
            Can Delay Criteria:
            - Due >14 days with runway >60 days
            - Small amount (<5 days burn) with runway >45 days
            - Non-critical vendor with runway >90 days and due >7 days
        """
    
    def prioritize_bills_for_payment(self, bills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize list of bills for payment.
        
        Args:
            bills: List of bill data dicts
        
        Returns:
            List of bills with added fields:
            - priority_score: float
            - priority_level: str ("urgent", "high", "medium", "low")
            - urgency_category: str ("must_pay", "can_delay")
        """
    
    def get_payment_decision_analysis(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive payment decision analysis.
        
        Args:
            bill_data: Bill data dict
        
        Returns:
            {
                "category": str,  # "must_pay" or "can_delay"
                "priority_score": float,
                "priority_level": str,
                "runway_impact": Dict[str, Any],  # From RunwayCalculator
                "scenarios": {
                    "pay_now": Dict[str, Any],
                    "pay_on_due_date": Dict[str, Any],
                    "delay_30_days": Dict[str, Any]
                },
                "recommendation": str,
                "decision_factors": List[str]
            }
        """
    
    def get_decision_factors(self, bill_data: Dict[str, Any], category: str, runway_metrics: Dict[str, Any]) -> List[str]:
        """Generate human-readable decision factors."""
```

---

## **3. TrayPriorityCalculator** (`runway/core/services/tray_priority_calculator.py`)

**Purpose:** All tray item prioritization calculations

### **New Canonical Service:**
```python
class TrayPriorityCalculator(TenantAwareService):
    """Canonical service for tray item prioritization calculations."""
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.runway_calculator = RunwayCalculator(db, business_id)
        self.payment_priority_calculator = PaymentPriorityCalculator(db, business_id)
    
    def calculate_tray_item_priority(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate priority for any tray item type.
        
        Args:
            item_data: {
                "type": str,  # "overdue_bill", "overdue_invoice", etc.
                "amount": Optional[float],
                "due_date": Optional[str],
                "qbo_id": Optional[str],
                "metadata": Dict[str, Any]
            }
        
        Returns:
            {
                "priority_score": float,  # 0-100
                "priority_level": str,    # "urgent", "high", "medium", "low"
                "urgency_factors": List[str],
                "runway_impact": Dict[str, Any]
            }
        """
    
    def calculate_bill_tray_priority(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized priority calculation for bill-related tray items."""
    
    def calculate_invoice_tray_priority(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized priority calculation for invoice-related tray items."""
    
    def enhance_tray_items_with_priority(self, tray_items: List[Dict[str, Any]], qbo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhance tray items with priority and runway analysis.
        
        This replaces TrayService.get_enhanced_tray_items() calculation logic.
        """
```

---

## **4. DataQualityAnalyzer** (`runway/core/services/data_quality_analyzer.py`)

**Purpose:** All data quality and hygiene calculations

### **Keep Existing Methods (Already Well-Designed):**
- ✅ `calculate_hygiene_score(qbo_data: Dict) -> Dict`
- ✅ `validate_data_consistency(qbo_data: Dict) -> Dict`
- ✅ `analyze_completeness(qbo_data: Dict) -> Dict`
- ✅ `generate_summary_for_context(hygiene_analysis: Dict, context: str) -> str`

### **No Changes Needed:** This service is already well-architected as a canonical calculation service.

---

## **5. Experience Service Refactoring**

### **TrayService** (`runway/tray/services/tray.py`)

**Remove Calculation Methods:**
- ❌ `calculate_priority_score()` → Use `TrayPriorityCalculator.calculate_tray_item_priority()`
- ❌ `categorize_bill_urgency()` → Use `PaymentPriorityCalculator.categorize_bill_urgency()`
- ❌ `get_payment_decision_analysis()` → Use `PaymentPriorityCalculator.get_payment_decision_analysis()`
- ❌ `_calculate_runway_impact()` → Use `RunwayCalculator.calculate_tray_item_runway_impact()`
- ❌ `_get_decision_factors()` → Use `PaymentPriorityCalculator.get_decision_factors()`

**Keep Orchestration Methods:**
- ✅ `get_tray_items()` → Delegate calculations to canonical services
- ✅ `get_tray_summary()` → Delegate calculations to canonical services
- ✅ `get_enhanced_tray_items()` → Use `TrayPriorityCalculator.enhance_tray_items_with_priority()`

### **DigestService** (`runway/digest/services/digest.py`)

**Remove Calculation Methods:**
- ❌ `calculate_runway()` → Use `RunwayCalculator.calculate_current_runway()`

**Keep Orchestration Methods:**
- ✅ `generate_and_send_digest()` → Delegate runway calculation to RunwayCalculator
- ✅ `get_digest_preview()` → Delegate runway calculation to RunwayCalculator

### **PaymentPriorityIntelligenceService** (`domains/ap/services/payment_priority.py`) - **DEPRECATED**

**Status:** ❌ **DEPRECATED** - Moved to `_parked/deprecated/payment_priority_intelligence_deprecated.py`

**Reason:** All calculation logic moved to canonical `PaymentPriorityCalculator`. Database query functionality moved to `BillService.get_payment_ready_bills()`.

**Migration:**
- Database queries → Use `BillService.get_payment_ready_bills()`
- Priority calculations → Use `PaymentPriorityCalculator.prioritize_bills_for_payment()`

### **RunwayReserveService** (`runway/reserves/services/runway_reserve_service.py`)

**Fix Hardcoded Methods:**
- ❌ `_get_business_cash_balance()` → Use real QBO data via RunwayCalculator
- ❌ `_calculate_monthly_burn_rate()` → Use real QBO data via RunwayCalculator
- ❌ `_get_monthly_revenue()` → Use real QBO data via RunwayCalculator
- ❌ `_get_monthly_expenses()` → Use real QBO data via RunwayCalculator
- ❌ `_get_employee_count()` → Use real QBO data or move to config

**Refactor Calculation Methods:**
- 🔄 `calculate_runway_with_reserves()` → Delegate base runway to RunwayCalculator, add reserve logic

---

## **6. Implementation Priority**

### **Phase 1: Create New Canonical Services**
1. Create `PaymentPriorityCalculator`
2. Create `TrayPriorityCalculator`
3. Clean up `RunwayCalculator` (remove duplicated methods)

### **Phase 2: Refactor Experience Services**
1. Update `TrayService` to delegate calculations
2. Update `DigestService` to delegate calculations
3. Update `PaymentPriorityIntelligenceService` to delegate calculations

### **Phase 3: Fix Hardcoded Values**
1. Replace hardcoded helpers in `RunwayReserveService`
2. Integrate real QBO data throughout

### **Phase 4: Testing & Validation**
1. Update all tests to use canonical APIs
2. Validate no calculation logic duplication remains
3. Ensure all experience services work correctly

---

## **7. Business Rules Integration**

All calculation services should use centralized business rules from `config/business_rules/`:

- **PaymentPriorityCalculator** → `payment_rules.py`
- **TrayPriorityCalculator** → `core_thresholds.py`
- **RunwayCalculator** → `core_thresholds.py`, `runway_analysis_settings.py`
- **DataQualityAnalyzer** → `data_quality_thresholds.py`

---

## **8. Success Criteria**

✅ **No calculation logic duplication** across services  
✅ **Single source of truth** for each calculation type  
✅ **Experience services only orchestrate**, never calculate  
✅ **Consistent APIs** with clear input/output contracts  
✅ **Real QBO data** replaces all hardcoded values  
✅ **Centralized business rules** eliminate magic numbers  
✅ **All tests pass** with canonical API usage  

---

**Status:** 📋 **CANONICAL API DEFINED** - Ready for implementation phase.
