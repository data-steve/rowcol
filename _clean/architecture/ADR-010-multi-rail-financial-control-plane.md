# ADR-010: Multi-Rail Financial Control Plane Architecture

**Date**: 2025-01-27  
**Status**: Accepted  
**Decision**: Implement hub-and-spoke multi-rail architecture with verification loop across RowCol (operational hub), QBO (ledger hub), Ramp (A/P execution), Plaid (cash verification), and Stripe (A/R insights) to enable Financial Control Plane for CAS 2.0 firms.

## Context

**Strategic Pivot**: RowCol is pivoting from QBO-centric architecture to Financial Control Plane for CAS 2.0 firms, requiring orchestration across multiple external rails using a hub-and-spoke model.

**Market Reality**: CAS 2.0 firms have moved to Ramp for bill pay execution, making QBO-only approach obsolete. QBO API limitations (ledger-only, no execution capabilities) require multi-rail orchestration.

**Architecture Challenge**: Current `domains/` architecture is QBO-centric, with all domain services assuming single external system. This creates fundamental mismatch with Financial Control Plane requirements where multiple rails operate on same domain primitives.

**Solution**: Hub-and-spoke architecture where each rail has specific role, RowCol orchestrates verification loop, and chain of custody ensures auditability across rails.

## Decision

**Hub-and-Spoke Multi-Rail Architecture**: Implement Financial Control Plane using hub-and-spoke model where QBO serves as ledger hub, external rails handle specific operations, and RowCol orchestrates verification loop with chain of custody tracking.

### **Rail Responsibilities**
- **QBO (Ledger Hub)**: Single source of truth for ledger data (bills, invoices, payments, audit trail)
- **Ramp (Execution Rail)**: A/P execution (bill approval, payment processing, webhooks)
- **Plaid (Verification Rail)**: Cash verification (real-time balances, guardrails, cash truth)
- **Stripe (Insights Rail)**: A/R insights (invoice tracking, payment analysis, CSV processing)

### **Key Patterns**
- **Hub-and-Spoke Architecture**: Clear separation of concerns, each rail does one thing well
- **Verification Loop**: Orchestrates multi-rail operations with clear state transitions
- **Chain of Custody**: Tracks state ownership and transitions across rails
- **Event-Driven Reconciliation**: Uses webhooks and refresh-on-demand to minimize API calls
- **Domain Gateway Pattern**: Rail-agnostic interfaces with rail-specific implementations

## Architecture Patterns

### Pattern 1: Verification Loop (Approve → Execute → Verify → Record)

**Implementation**:
```python
# Runway Service orchestrates domain gateways
class TrayService:
    def __init__(self, bills_gateway: BillsGateway, balances_gateway: BalancesGateway, 
                 ramp_gateway: RampGateway, plaid_gateway: PlaidGateway):
        self.bills = bills_gateway
        self.balances = balances_gateway
        self.ramp = ramp_gateway
        self.plaid = plaid_gateway

    async def approve_bill(self, advisor_id: str, bill_id: str, business_id: str):
        # 1. Approve (RowCol) - Check guardrails via Plaid
        balance = self.balances.get(BalancesQuery(client_id=business_id, freshness_hint="STRICT"))
        if not self.apply_guardrails(balance, bill_id):
            raise ValueError("Guardrail violation")
        
        # 2. Execute (Ramp) - Schedule payment via Ramp gateway
        payment_id = self.ramp.schedule_payment(bill_id, amount, due_date)
        
        # 3. Verify (RowCol) - Confirm execution via webhooks
        await self.verify_execution(payment_id, business_id)
        
        # 4. Record (QBO) - Update ledger via QBO gateway
        self.bills.record_payment(bill_id, payment_id, amount, due_date)
        
        return {"status": "approved", "payment_id": payment_id}

    async def verify_execution(self, payment_id: str, business_id: str):
        # Verify via Ramp webhook and Plaid balance check
        ramp_status = self.ramp.get_payment_status(payment_id)
        balance = self.balances.get(BalancesQuery(client_id=business_id, freshness_hint="STRICT"))
        
        if ramp_status == "paid" and balance.is_valid:
            self.bills.mark_verified(payment_id)
        else:
            self.bills.flag_discrepancy(payment_id, "Payment verification failed")
```

**Characteristics**:
- ✅ Clear state ownership (Ramp: execution, QBO: ledger, Plaid: cash, RowCol: approvals)
- ✅ Auditability via logged state transitions
- ✅ Domain gateway pattern for rail-agnostic orchestration

### Pattern 2: Event-Driven Reconciliation

**Implementation**:
```python
# Webhook handler using domain gateways
class WebhookHandler:
    def __init__(self, bills_gateway: BillsGateway, balances_gateway: BalancesGateway):
        self.bills = bills_gateway
        self.balances = balances_gateway

    async def handle_ramp_webhook(self, webhook_data: dict):
        bill_id = webhook_data["bill_id"]
        business_id = webhook_data["business_id"]
        status = webhook_data["status"]
        
        # Use domain gateways for verification
        if status == "paid":
            balance = self.balances.get(BalancesQuery(client_id=business_id, freshness_hint="STRICT"))
            if balance.is_valid:
                self.bills.mark_verified(bill_id)
            else:
                self.bills.flag_discrepancy(bill_id, "Balance verification failed")
```

**Characteristics**:
- ✅ Minimizes API calls using Ramp webhooks and Plaid refresh-on-demand
- ✅ Idempotent webhook processing to prevent duplicate actions
- ✅ Domain gateway pattern for consistent rail interaction

## Hub-and-Spoke Architecture

```
                    ┌─────────────────────────────────────┐
                    │            ROWCOL HUB               │
                    │     (Financial Control Plane)      │
                    │  • Multi-client orchestration      │
                    │  • Workflow-specific coordination  │
                    │  • Cross-rail verification         │
                    └─────────────┬───────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┼─────────────────────────┐
        │                         │                         │                         |
        │  A/P Workflow           │  A/R Workflow           │  Cash Workflow          │
        │  ┌─────────┐ ┌─────────┐│ ┌─────────┐ ┌─────────┐│  ┌─────────┐ ┌─────────┐ |
        │  │   QBO   │ │  RAMP   ││ │   QBO   │ │ STRIPE  ││  │   QBO   │ │ PLAID   │ |
        │  │(Ledger) │ │(Execute)││ │(Ledger) │ │(A/R)    ││  │(Ledger) │ │(Cash)   │ |
        │  └─────────┘ └─────────┘│ └─────────┘ └─────────┘│  └─────────┘ └─────────┘ |
        │                         │                         |                         |
        └─────────────────────────┼─────────────────────────┼─────────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │         PLAID (Cash)                │
                    │    • Balance verification           │
                    │    • Guardrail enforcement          │
                    │    • Cross-workflow validation      │
                    └─────────────────────────────────────┘
```

## Implementation Guidelines

### When to Use This Pattern:
- When orchestrating multi-rail operations (QBO, Ramp, Plaid) for bill payments
- When ensuring auditability for advisor-led cash discipline across 20–100 clients
- When implementing Financial Control Plane for CAS 2.0 firms

### Code Organization:
```
runway/services/
├── tray_service.py          # Verification loop orchestration
├── console_service.py       # Multi-client dashboard
└── webhook_handler.py       # Event-driven reconciliation

infra/gateways/
├── qbo_bills_gateway.py     # QBO ledger operations
├── ramp_bills_gateway.py    # Ramp execution operations
├── plaid_balances_gateway.py # Plaid verification operations
└── stripe_invoices_gateway.py # Stripe insights operations

domains/*/gateways.py
├── bills_gateway.py         # Rail-agnostic bill interfaces
├── balances_gateway.py      # Rail-agnostic balance interfaces
└── invoices_gateway.py      # Rail-agnostic invoice interfaces
```

### Required Patterns:
```python
# Domain Gateway Interface
class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> List[Bill]: ...
    def schedule_payment(self, client_id: str, bill_id: str, amount: Decimal, pay_on: date) -> str: ...
    def record_payment(self, bill_id: str, payment_id: str, amount: Decimal, due_date: date) -> None: ...
    def mark_verified(self, bill_id: str) -> None: ...
    def flag_discrepancy(self, bill_id: str, reason: str) -> None: ...

# Infra Gateway Implementation
class RampBillsGateway(BillsGateway):
    def schedule_payment(self, client_id: str, bill_id: str, amount: Decimal, pay_on: date) -> str:
        # Ramp-specific implementation with Smart Sync pattern
        pass
```

## Benefits

### Positive Outcomes
✅ **Auditability**: Every state transition (approval, verification) is logged for SOC2 compliance  
✅ **Reliability**: Webhook-driven reconciliation reduces state conflicts across rails  
✅ **Scalability**: Domain gateway pattern supports multiple rails without code duplication  
✅ **Maintainability**: Clear separation of concerns between orchestration and rail-specific logic

### Business Value
- Enables advisor trust by ensuring traceable, error-free cash discipline workflows
- Supports scalability to 100 clients with minimal reconciliation overhead
- Provides Financial Control Plane for CAS 2.0 firms

## Consequences

**Positive**: Clear state ownership simplifies debugging and auditing  
**Negative**: Webhook dependency increases reliance on external rail SLAs

**Risks & Mitigations**:
- **Risk**: Ramp webhook drops miss payment events  
  **Mitigation**: Implement retry queues and periodic QBO checks
- **Risk**: Plaid token errors disrupt balance verification  
  **Mitigation**: Notify advisors via hygiene tray, offer manual fallback
- **Risk**: Domain gateway complexity  
  **Mitigation**: Start with QBO-only, add rails incrementally

## Success Metrics
- **Reconciliation Accuracy**: 99% of payments verified without discrepancies
- **Webhook Latency**: 95% of Ramp webhooks processed within 1 second
- **Multi-Rail Support**: Seamless operation across QBO, Ramp, Plaid, Stripe
- **Advisor Trust**: 90%+ confidence in Financial Control Plane accuracy

## Related ADRs
- **ADR-001**: Domain separation principles (foundation)
- **ADR-005**: QBO API strategy (rail-specific patterns)
- **ADR-007**: Service boundaries (domain gateway pattern)
- **ADR-003**: Multi-tenancy strategy (firm-first hierarchy)

---

**Last Updated**: 2025-01-27  
**Next Review**: 2026-01-27
