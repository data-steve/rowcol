# Oodaloo Calculation Logic Inventory

## Executive Summary

This document inventories all calculation-related methods across Oodaloo's services to identify duplication, establish canonical APIs, and guide the refactoring effort to centralize core calculations in `runway/core/services/`.

---

## 1. **TrayService** (`runway/tray/services/tray.py`)

### Calculation Methods:
- **`calculate_priority_score(item: TrayItem) -> int`**
  - **What it calculates:** Priority score (0-100) for tray items based on urgency, amount, and business impact
  - **Inputs:** TrayItem object with due_date, type, amount
  - **Outputs:** Integer score (0-100)
  - **Used by:** `get_tray_items()`, `get_tray_summary()`
  - **Business Logic:** Time-based urgency scoring + type-based weights + cap at 100

- **`categorize_bill_urgency(bill_data: Dict) -> str`**
  - **What it calculates:** Bill payment urgency categorization ("must_pay" vs "can_delay")
  - **Inputs:** Bill data dict (amount, due_date, vendor_name, type)
  - **Outputs:** String ("must_pay" or "can_delay")
  - **Used by:** `get_payment_decision_analysis()`, `get_enhanced_tray_items()`
  - **Business Logic:** Complex rules for overdue bills, critical vendors, runway impact thresholds
  - **⚠️ DUPLICATION:** Similar logic exists in `RunwayCalculator.categorize_bill_urgency()`

- **`get_payment_decision_analysis(bill_data: Dict) -> Dict`**
  - **What it calculates:** Comprehensive payment decision analysis with scenarios and recommendations
  - **Inputs:** Bill data dict (amount, due_date, vendor_name)
  - **Outputs:** Dict with category, runway_impact, scenarios, recommendation, decision_factors
  - **Used by:** `get_enhanced_tray_items()`
  - **Business Logic:** Runway calculations, scenario modeling, recommendation generation
  - **⚠️ DUPLICATION:** Similar logic exists in `RunwayCalculator.get_payment_decision_analysis()`

- **`_calculate_runway_impact(item: TrayItem) -> Dict`**
  - **What it calculates:** Runway impact of resolving a tray item
  - **Inputs:** TrayItem object
  - **Outputs:** Dict with cash_impact and days_impact
  - **Used by:** `get_tray_items()`, `get_tray_summary()`
  - **Business Logic:** Delegates to data provider (should delegate to RunwayCalculator)

- **`_get_decision_factors(bill_data, category, current_runway, days_until_due) -> List[str]`**
  - **What it calculates:** List of factors that influenced payment decision
  - **Inputs:** Bill data, category, runway metrics, timing
  - **Outputs:** List of human-readable decision factors
  - **Used by:** `get_payment_decision_analysis()`
  - **Business Logic:** Factor identification based on thresholds and business rules
  - **⚠️ DUPLICATION:** Similar logic exists in `RunwayCalculator._get_decision_factors()`

---

## 2. **DigestService** (`runway/digest/services/digest.py`)

### Calculation Methods:
- **`calculate_runway(business_id: str) -> Dict[str, float]`**
  - **What it calculates:** Runway metrics for weekly digest
  - **Inputs:** Business ID
  - **Outputs:** Dict with runway_days, cash, ar_overdue, ap_due_soon, burn_rate, net_position
  - **Used by:** `generate_and_send_digest()`, `get_digest_preview()`
  - **Business Logic:** Cash + AR - AP / (burn_rate / 30)
  - **⚠️ DUPLICATION:** Similar logic exists in `RunwayCalculator.calculate_current_runway()`

---

## 3. **RunwayCalculator** (`runway/core/services/runway_calculator.py`)

### Core Calculation Methods:
- **`calculate_current_runway(qbo_data: Optional[Dict]) -> Dict`**
  - **What it calculates:** Current runway based on latest financial data
  - **Inputs:** Optional QBO data dict
  - **Outputs:** Comprehensive runway analysis dict
  - **Used by:** Multiple services, scenario analysis, historical analysis
  - **Business Logic:** Cash position + AR - AP / daily burn rate + optimization impact

- **`calculate_scenario_impact(scenario: Dict, qbo_data: Optional[Dict]) -> Dict`**
  - **What it calculates:** Runway impact of specific scenarios
  - **Inputs:** Scenario description dict, optional QBO data
  - **Outputs:** Scenario impact analysis dict
  - **Used by:** What-if analysis features
  - **Business Logic:** Baseline vs modified scenario comparison

- **`calculate_historical_runway(weeks_back: int = 4) -> List[Dict]`**
  - **What it calculates:** Historical runway analysis for trend analysis
  - **Inputs:** Number of weeks to analyze
  - **Outputs:** List of weekly runway data
  - **Used by:** Runway Replay, trend analysis
  - **Business Logic:** Simulated historical data analysis (TODO: real historical data)

### Helper Calculation Methods:
- **`_calculate_cash_position(qbo_data: Dict) -> float`**
- **`_calculate_burn_rate(qbo_data: Dict) -> Dict`**
- **`_calculate_ar_position(qbo_data: Dict) -> float`**
- **`_calculate_ap_position(qbo_data: Dict) -> float`**
- **`_calculate_optimization_impact(qbo_data: Dict, daily_burn: float) -> Dict`**
- **`_determine_runway_status(runway_days: float) -> str`**
- **`_assess_forecast_accuracy(qbo_data: Dict) -> Dict`**

### Duplicated Methods (Added for Tray delegation):
- **`get_tray_item_impact(item: Any) -> Dict`** ⚠️ DUPLICATION
- **`categorize_bill_urgency(bill_data: Dict) -> str`** ⚠️ DUPLICATION
- **`get_payment_decision_analysis(bill_data: Dict) -> Dict`** ⚠️ DUPLICATION
- **`_get_decision_factors(bill_data, category, current_runway, days_until_due) -> List[str]`** ⚠️ DUPLICATION

---

## 4. **DataQualityAnalyzer** (`runway/core/services/data_quality_analyzer.py`)

### Calculation Methods:
- **`calculate_hygiene_score(qbo_data: Dict) -> Dict`**
  - **What it calculates:** Comprehensive data hygiene score (0-100)
  - **Inputs:** QBO data dict
  - **Outputs:** Hygiene analysis dict with score, issues, impact, recommendations
  - **Used by:** Test Drive, Digest, Console
  - **Business Logic:** Issue detection + runway impact calculation + scoring

- **`validate_data_consistency(qbo_data: Dict) -> Dict`**
  - **What it calculates:** Data consistency analysis across QBO entities
  - **Inputs:** QBO data dict
  - **Outputs:** Consistency analysis dict
  - **Used by:** Data quality monitoring
  - **Business Logic:** Orphaned references, name mismatches, consistency scoring

- **`analyze_completeness(qbo_data: Dict) -> Dict`**
  - **What it calculates:** Data completeness analysis by entity type
  - **Inputs:** QBO data dict
  - **Outputs:** Completeness analysis dict
  - **Used by:** Data quality monitoring
  - **Business Logic:** Field completeness analysis, scoring by entity type

### Helper Methods:
- **`_assess_health_level(hygiene_score: int) -> Dict`**
- **`_generate_hygiene_summary(score, issues_count, impact_days) -> str`**
- **`_analyze_entity_completeness(entities, required_fields) -> Dict`**
- **`generate_summary_for_context(hygiene_analysis, context) -> str`**

---

## 5. **PaymentPriorityIntelligenceService** (`domains/ap/services/payment_priority.py`)

### Calculation Methods:
- **`prioritize_bills_for_payment(bills: List[Dict]) -> List[Dict]`**
  - **What it calculates:** Bill prioritization with priority scores
  - **Inputs:** List of bill dictionaries
  - **Outputs:** Sorted list with priority_score and priority fields added
  - **Used by:** AP workflow, payment scheduling
  - **Business Logic:** Multi-factor priority scoring + sorting

- **`calculate_payment_priority_score(bill: Dict) -> float`**
  - **What it calculates:** Priority score (0-100) for individual bills
  - **Inputs:** Bill data dict
  - **Outputs:** Float priority score
  - **Used by:** `prioritize_bills_for_payment()`
  - **Business Logic:** Due date urgency + amount factor + vendor relationship factor
  - **⚠️ OVERLAP:** Similar urgency logic as TrayService.calculate_priority_score()

- **`determine_priority_level(score: float) -> str`**
  - **What it calculates:** Priority level categorization
  - **Inputs:** Priority score (0-100)
  - **Outputs:** String priority level ('urgent', 'high', 'medium', 'low')
  - **Used by:** `prioritize_bills_for_payment()`
  - **Business Logic:** Score-based thresholds

- **`get_payment_ready_bills(max_amount: Optional[float]) -> List[Dict]`**
  - **What it calculates:** Prioritized list of payment-ready bills
  - **Inputs:** Optional maximum amount constraint
  - **Outputs:** Prioritized bill list within budget
  - **Used by:** Payment processing workflows
  - **Business Logic:** Database query + prioritization + budget filtering

---

## 6. **RunwayReserveService** (`runway/reserves/services/runway_reserve_service.py`)

### Calculation Methods:
- **`calculate_runway_with_reserves(business_id: str) -> RunwayCalculationWithReserves`**
  - **What it calculates:** Runway calculation including reserve impact
  - **Inputs:** Business ID
  - **Outputs:** Enhanced runway calculation with reserve data
  - **Used by:** Reserve management, enhanced runway analysis
  - **Business Logic:** Base runway + reserve allocation impact
  - **⚠️ DUPLICATION:** Overlaps with RunwayCalculator.calculate_current_runway()

### Hardcoded Helper Methods (⚠️ CRITICAL ISSUE):
- **`_get_business_cash_balance(business_id: str) -> Decimal`** - Returns hardcoded $100,000
- **`_calculate_monthly_burn_rate(business_id: str) -> Decimal`** - Returns hardcoded $15,000
- **`_get_monthly_revenue(business_id: str) -> Decimal`** - Returns hardcoded $25,000
- **`_get_monthly_expenses(business_id: str) -> Decimal`** - Returns hardcoded $15,000
- **`_get_employee_count(business_id: str) -> int`** - Returns hardcoded 5

---

## 7. **Critical Issues Identified**

### **Duplication Problems:**
1. **Runway Calculations:** `DigestService.calculate_runway()` vs `RunwayCalculator.calculate_current_runway()` vs `RunwayReserveService.calculate_runway_with_reserves()`
2. **Bill Urgency Logic:** `TrayService.categorize_bill_urgency()` vs `RunwayCalculator.categorize_bill_urgency()`
3. **Payment Decision Analysis:** `TrayService.get_payment_decision_analysis()` vs `RunwayCalculator.get_payment_decision_analysis()`
4. **Priority Scoring:** `TrayService.calculate_priority_score()` vs `PaymentPriorityIntelligenceService.calculate_payment_priority_score()`

### **Hardcoded Values:**
1. **RunwayReserveService:** All helper methods return hardcoded values instead of real QBO data
2. **Business Rules:** Magic numbers scattered across services instead of centralized in config/business_rules

### **Architectural Violations:**
1. **Experience Services Doing Calculations:** TrayService and DigestService contain core business logic
2. **Missing Delegation:** Services not using canonical calculation methods
3. **Inconsistent APIs:** Similar calculations have different input/output formats

---

## 8. **Recommended Canonical API**

### **Core Calculation Services (runway/core/services/):**

#### **RunwayCalculator** (Already exists, needs cleanup):
- `calculate_current_runway(qbo_data: Optional[Dict]) -> Dict`
- `calculate_scenario_impact(scenario: Dict, qbo_data: Optional[Dict]) -> Dict`
- `calculate_historical_runway(weeks_back: int) -> List[Dict]`
- `calculate_runway_with_reserves(business_id: str, reserve_data: Dict) -> Dict`

#### **PaymentPriorityCalculator** (New service):
- `calculate_bill_priority_score(bill_data: Dict) -> float`
- `categorize_bill_urgency(bill_data: Dict) -> str`
- `prioritize_bills_for_payment(bills: List[Dict]) -> List[Dict]`
- `get_payment_decision_analysis(bill_data: Dict) -> Dict`

#### **TrayPriorityCalculator** (New service):
- `calculate_tray_item_priority(item: Dict) -> float`
- `calculate_tray_item_runway_impact(item: Dict) -> Dict`

### **Experience Services Should Only:**
- **TrayService:** Orchestrate tray interactions, delegate calculations
- **DigestService:** Format and send digests, delegate calculations
- **PaymentPriorityIntelligenceService:** Orchestrate payment workflows, delegate calculations

---

## 9. **Next Steps**

1. **Create canonical calculation services** in `runway/core/services/`
2. **Refactor experience services** to delegate to canonical services
3. **Replace hardcoded values** in RunwayReserveService with real QBO integration
4. **Centralize business rules** and remove magic numbers
5. **Update tests** to validate canonical API usage
6. **Document APIs** with clear input/output specifications

---

**Status:** ✅ **INVENTORY COMPLETE** - Ready for canonical API design phase.
