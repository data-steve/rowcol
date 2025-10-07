# QBO MVP Implementation Handoff Script

## **🎯 Mission**
Implement QBO-only MVP using existing codebase with feature gating. **Critical**: Remove QBO execution assumptions and implement strategic feature gating.

## **📋 Remaining Tasks**

### **P0: Critical QBO Execution Audit (15h)**
- [ ] **Audit Payment Service** (`domains/ap/services/payment.py`)
  - **Issue**: Lines 104-133 assume QBO can execute payments (it can't!)
  - **Action**: Remove QBO execution code, keep QBO sync for read-only operations
  - **Impact**: This is a **blocking issue** - MVP won't work without this fix

- [ ] **Audit Scheduled Payment Service** (`runway/services/0_data_orchestrators/scheduled_payment_service.py`)
  - **Issue**: May assume QBO can execute scheduled payments
  - **Action**: Verify and fix any QBO execution assumptions
  - **Impact**: Reserve management depends on this

- [ ] **Audit Other Services** (Scan for QBO execution assumptions)
  - **Files to check**: All services in `runway/services/` and `domains/ap/services/`
  - **Pattern**: Look for `qbo_payment_id`, `execute_payment`, `create_payment_immediate`
  - **Action**: Document and fix any QBO execution assumptions

### **P1: Feature Gating Implementation (25h)**
- [ ] **Create Feature Gates Config** (`infra/config/feature_gates.py`)
  - **Pattern**: Follow existing config structure (see `infra/config/__init__.py`)
  - **Features**: QBO, Ramp, Plaid, Stripe integration flags
  - **Capabilities**: Reserve management, payment execution, multi-rail hygiene
  - **Environment**: Use `.env` variables for easy switching

- [ ] **Update Core Services with Gating**
  - [ ] **Digest Service** (`runway/services/2_experiences/digest.py`)
    - **Gate**: Multi-rail data sources, client-facing vs advisor-facing
    - **QBO-only**: Show QBO data only, hide multi-rail features
  - [ ] **Hygiene Tray** (`runway/services/2_experiences/tray.py`)
    - **Gate**: Ramp bill hygiene, multi-rail data sources
    - **QBO-only**: Show QBO bill quality issues only
  - [ ] **Decision Console** (`runway/services/2_experiences/console.py`)
    - **Gate**: Ramp execution, multi-rail decision orchestration
    - **QBO-only**: Show bill approval workflow, hide execution
  - [ ] **Reserve Runway** (`runway/services/0_data_orchestrators/reserve_runway.py`)
    - **Gate**: Hold out completely in QBO-only MVP
    - **Reason**: Requires Ramp for payment execution
  - [ ] **Scheduled Payment** (`runway/services/0_data_orchestrators/scheduled_payment_service.py`)
    - **Gate**: Ramp execution, multi-rail scheduling
    - **QBO-only**: Show QBO scheduled payments only

### **P2: Rail-Specific Config Separation (10h)**
- [ ] **Extract QBO Settings** from `infra/config/core_thresholds.py`
  - **Current**: QBO API settings mixed with product thresholds
  - **Target**: Create `infra/config/rail_configs.py`
  - **Move**: `QBOSettings` class and related QBO configs
  - **Keep**: Product thresholds in `core_thresholds.py`

### **P3: QBO-Only Golden Dataset (20h)**
- [ ] **Leverage Existing Sandbox** (`tests/sandbox/`)
  - **Files**: `create_multi_rail_sandbox_data.py`, `scenario_data.py`, `scenario_runner.py`
  - **Action**: Extend for QBO-only MVP scenarios
  - **Coverage**: All services need realistic test data

- [ ] **Create QBO-Only Test Scenarios**
  - **Businesses**: 3-5 realistic business profiles
  - **Data**: Bills, invoices, balances, vendors, transactions
  - **Scenarios**: Healthy, warning, critical runway states
  - **Integration**: Connect with existing scenario framework

### **P4: UI Dashboard Creation (30h)**
- [ ] **Combine Core Services** into unified dashboard
  - **Components**: Digest + Hygiene + Console
  - **Layout**: Single-page dashboard for QBO-only MVP
  - **Features**: Show/hide based on feature gates
  - **Responsive**: Mobile-friendly for advisor use

### **P5: Strategic Test Gating (15h)**
- [ ] **Implement Test Gating** (not blanket silencing)
  - **Pattern**: Use feature gates to control test execution
  - **Strategy**: Gate multi-rail tests, keep QBO tests
  - **Documentation**: Document why each test is gated
  - **Future**: Plan when to enable each test

## **🔍 Critical Context**

### **What You Have Built (80% Reusable)**
- **Runway Calculator**: Pure, stateless, data-agnostic - perfect for MVP
- **Base API Client**: Comprehensive foundation for all integrations
- **Vendor Normalization**: Sophisticated system ready for multi-rail
- **Core Services**: Digest, Hygiene, Console - solid logic, need gating
- **Infrastructure**: Job storage, smart sync, QBO config - ready to extend

### **Critical Issues to Fix**
1. **QBO Execution Assumptions**: Payment service assumes QBO can execute payments (it can't!)
2. **Mixed Configurations**: QBO API settings buried in core_thresholds.py
3. **Test Strategy**: Need principled gating, not blanket silencing

### **Strategic Approach**
- **Phase 0.5**: QBO-only MVP using existing code with gating (115h)
- **Phase 1**: Add Ramp by extending existing services (110h)
- **Phase 2**: Add Plaid + Stripe using same patterns (125h)
- **Total**: 350h (9-12 weeks) vs 540h (13-14 weeks) for full build

## **🛠️ Implementation Guidance**

### **Feature Gating Pattern**
```python
# In services, use feature gates to control functionality
from infra.config import feature_gates

def get_console_data(self, business_id: str):
    data = {}
    
    # Always include QBO bill approval
    data['qbo_bills'] = self._get_qbo_bills_for_approval()
    
    # Only include execution if Ramp is enabled
    if feature_gates.can_use_feature("payment_execution"):
        data['execution_options'] = self._get_ramp_execution_options()
    else:
        data['execution_options'] = []
        
    return data
```

### **QBO Execution Fix Pattern**
```python
# BEFORE (assumes QBO can execute)
qbo_response = await self.smart_sync.create_payment_immediate(qbo_payment_data)

# AFTER (QBO sync only, no execution)
if feature_gates.can_use_feature("payment_execution"):
    # Use Ramp for execution
    ramp_response = await self.ramp_client.execute_payment(payment_data)
else:
    # QBO-only: just sync the payment record
    qbo_response = await self.smart_sync.sync_payment_record(payment_data)
```

### **Test Gating Pattern**
```python
# In test files, gate based on feature flags
@pytest.mark.skipif(not feature_gates.can_use_feature("payment_execution"), 
                   reason="Payment execution requires Ramp integration")
def test_payment_execution():
    # Ramp-specific tests

@pytest.mark.skipif(not feature_gates.can_use_feature("reserve_management"),
                   reason="Reserve management requires Ramp integration")
def test_reserve_management():
    # Reserve-specific tests
```

## **📁 Key Files to Modify**

### **Critical Files (Must Fix)**
- `domains/ap/services/payment.py` - Remove QBO execution assumptions
- `runway/services/0_data_orchestrators/scheduled_payment_service.py` - Audit for QBO execution
- `infra/config/core_thresholds.py` - Extract QBO settings

### **Feature Gating Files (Add Gating)**
- `runway/services/2_experiences/digest.py` - Gate multi-rail features
- `runway/services/2_experiences/tray.py` - Gate Ramp hygiene
- `runway/services/2_experiences/console.py` - Gate Ramp execution
- `runway/services/0_data_orchestrators/reserve_runway.py` - Hold out completely

### **New Files to Create**
- `infra/config/feature_gates.py` - Feature gating configuration
- `infra/config/rail_configs.py` - Rail-specific configurations
- `tests/sandbox/qbo_only_scenarios.py` - QBO-only test scenarios

## **🎯 Success Criteria**

### **QBO-Only MVP Working**
- [ ] All QBO execution assumptions removed
- [ ] Feature gating controls multi-rail functionality
- [ ] QBO-only dashboard loads and functions
- [ ] All tests pass with strategic gating
- [ ] Realistic test data covers all scenarios

### **Ready for Ramp Integration**
- [ ] Feature gates ready for Ramp enablement
- [ ] Services structured for easy Ramp extension
- [ ] Test framework ready for multi-rail testing
- [ ] Configuration separated by rail

## **💡 Key Insights**

- **Preserve Investment**: 80% of existing code is reusable
- **Enable Learning**: QBO-only MVP lets you learn before expanding
- **Maintain Quality**: Principled gating vs random patching
- **Set Up Success**: Each phase builds on the previous one

This approach gives you a working QBO-only MVP in 3-4 weeks while preserving your investment and setting up clean expansion to multi-rail.

## **🚀 Next Steps**

1. **Start with QBO Execution Audit** - this is blocking
2. **Create Feature Gates Config** - foundation for everything else
3. **Update Core Services** - add gating to existing services
4. **Create QBO-Only Test Data** - leverage existing sandbox framework
5. **Build Unified Dashboard** - combine services into single interface
6. **Implement Test Gating** - strategic, not blanket silencing

**Total Effort**: 115h (3-4 weeks) for QBO-only MVP
**Next Phase**: Add Ramp integration (110h, 3-4 weeks)
**Final Phase**: Add Plaid + Stripe (125h, 3-4 weeks)
