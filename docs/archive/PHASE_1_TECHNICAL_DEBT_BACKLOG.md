# Phase 1 Technical Debt Backlog

## **🎯 Phase 1: Ramp Integration (3-4 weeks)**

This document tracks technical debt items that need resolution during Ramp integration phase.

## **📋 Technical Debt Items**

### **TD-001: Scheduled Payment + Reserve Integration**
**Priority**: P1 (High)  
**Effort**: 15h  
**Phase**: Ramp Integration  

**Problem Statement:**
The relationship between `ScheduledPaymentService` and `RunwayReserveService` is complex and needs proper design with Ramp's actual reserve capabilities. Current implementation has several issues:

1. **Earmarking Strategy**: QBO doesn't support native earmarking, but Ramp might
2. **Reserve Allocation**: Current allocation logic is simplistic and needs Ramp context
3. **Payment Execution**: Scheduled payments need Ramp's execution capabilities
4. **Error Handling**: Complex failure scenarios between scheduling and reserves

**Current State:**
```python
# Current implementation is feature-gated but not properly designed
if feature_gates.can_use_feature("reserve_management"):
    allocation = self.runway_reserve_service.allocate_reserve(allocation_data)
else:
    logger.info("Reserve management not available - skipping reserve allocation")
```

**Target State:**
```python
# Proper integration with Ramp's reserve capabilities
if feature_gates.can_use_feature("reserve_management"):
    # Use Ramp's actual reserve management
    allocation = await self.ramp_reserve_service.allocate_reserve(allocation_data)
    # Schedule payment via Ramp with proper earmarking
    scheduled_payment = await self.ramp_payment_service.schedule_payment(payment_data)
else:
    # QBO-only mode with clear limitations
    self._handle_qbo_only_scheduling(bill, payment_date)
```

**Dependencies:**
- Ramp API integration for reserve management
- Ramp API integration for payment scheduling
- Understanding of Ramp's earmarking capabilities
- Error handling strategy for complex scenarios

**Acceptance Criteria:**
- [ ] Reserve allocation works with Ramp's actual capabilities
- [ ] Scheduled payments integrate properly with Ramp
- [ ] Earmarking strategy is clear and documented
- [ ] Error handling covers all failure scenarios
- [ ] QBO-only mode still works with clear limitations

---

### **TD-002: Reserve Management Architecture**
**Priority**: P1 (High)  
**Effort**: 20h  
**Phase**: Ramp Integration  

**Problem Statement:**
Current `RunwayReserveService` is designed for QBO-only mode and needs complete redesign for Ramp integration. Key issues:

1. **Reserve Types**: Need to understand Ramp's reserve types and capabilities
2. **Allocation Strategy**: Current allocation logic is too simplistic
3. **Integration Points**: Need proper integration with Ramp's reserve management
4. **Data Model**: Reserve models may need updates for Ramp compatibility

**Current State:**
```python
# Current service is completely disabled in QBO-only mode
if not feature_gates.can_use_feature("reserve_management"):
    raise ValidationError("Reserve management requires Ramp integration")
```

**Target State:**
```python
# Proper Ramp integration with fallback to QBO-only
if feature_gates.can_use_feature("reserve_management"):
    # Use Ramp's reserve management capabilities
    return await self.ramp_reserve_service.create_reserve(reserve_data)
else:
    # QBO-only mode with clear limitations
    return self._create_qbo_only_reserve_record(reserve_data)
```

**Dependencies:**
- Ramp API documentation for reserve management
- Understanding of Ramp's reserve types and capabilities
- Data model updates for Ramp compatibility
- Integration testing with Ramp sandbox

**Acceptance Criteria:**
- [ ] Reserve creation works with Ramp's actual capabilities
- [ ] Reserve allocation integrates with Ramp
- [ ] Reserve utilization works with Ramp payments
- [ ] QBO-only mode has appropriate fallback behavior
- [ ] Data models are compatible with Ramp

---

### **TD-003: Payment Execution Strategy**
**Priority**: P1 (High)  
**Effort**: 25h  
**Phase**: Ramp Integration  

**Problem Statement:**
Payment execution needs proper integration with Ramp's payment methods and approval flows. Current implementation is feature-gated but not properly designed:

1. **Payment Methods**: Need Ramp's actual payment methods (ACH, wire, check)
2. **Approval Flows**: Need Ramp's approval workflow integration
3. **Execution Timing**: Need proper integration with Ramp's execution timing
4. **Error Handling**: Need proper error handling for Ramp payment failures

**Current State:**
```python
# Current implementation is feature-gated but not properly designed
if feature_gates.can_use_feature("payment_execution"):
    # TODO: Implement Ramp payment execution
    payment.confirmation_number = f"RAMP-{payment.payment_id}"
else:
    # QBO-only mode with clear limitations
    payment.status = PaymentStatus.PENDING
```

**Target State:**
```python
# Proper Ramp integration with fallback to QBO-only
if feature_gates.can_use_feature("payment_execution"):
    # Use Ramp's payment execution capabilities
    ramp_response = await self.ramp_payment_service.execute_payment(payment_data)
    payment.confirmation_number = ramp_response.confirmation_number
    payment.status = PaymentStatus.EXECUTED
else:
    # QBO-only mode with clear limitations
    payment.status = PaymentStatus.PENDING
    await self.smart_sync.sync_payment_record(payment_data)
```

**Dependencies:**
- Ramp API integration for payment execution
- Understanding of Ramp's payment methods and approval flows
- Error handling strategy for payment failures
- Integration testing with Ramp sandbox

**Acceptance Criteria:**
- [ ] Payment execution works with Ramp's actual capabilities
- [ ] Payment methods are properly integrated with Ramp
- [ ] Approval flows work with Ramp
- [ ] Error handling covers all payment failure scenarios
- [ ] QBO-only mode has appropriate fallback behavior

---

## **📊 Phase 1 Summary**

**Total Effort**: 60h (15h + 20h + 25h)  
**Timeline**: 3-4 weeks  
**Dependencies**: Ramp API integration, sandbox testing  

**Key Success Metrics:**
- All technical debt items resolved
- Ramp integration working properly
- QBO-only mode still functional
- Clear upgrade path to multi-rail

**Risk Mitigation:**
- Feature gating protects existing functionality
- Clear error messages for unavailable features
- Comprehensive testing with Ramp sandbox
- Fallback behavior for QBO-only mode

This backlog ensures that technical debt is properly addressed during Ramp integration while maintaining the QBO-only MVP functionality.
