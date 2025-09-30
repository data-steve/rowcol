# ADR-008: Agentic Automation Architecture

**Date**: 2025-09-30  
**Status**: Draft (Pending Implementation)  
**Decision**: Position Oodaloo as agentic cash flow console with Smart Policies/Budgets as intelligence layer

---

## Context

Intuit is rolling out AI agents in QuickBooks (Nov 2025+) that automate transaction categorization, reconciliation, bill scheduling, and AR reminders. This creates both threat and opportunity:

**Threat**: Any product positioned as "QBO hygiene tool" will be commoditized
**Opportunity**: Position Oodaloo as "agentic decision orchestration layer" above task automation

**Key Insight**: Oodaloo IS already agentic—the OODA loop (Observe, Orient, Decide, Act) is the same pattern modern AI agents use. We just need to position it that way and build Smart Policies/Budgets to make the intelligence obvious.

---

## Decision

**Position Oodaloo as "Agentic Cash Flow Console"** with three architectural layers:

### **1. Agentic Foundation (Already Built)**
The OODA loop pattern is already implemented through Data Orchestrators → Calculators → Experiences:
- **Sense** (Observe): Data Orchestrators pull AR/AP/balance from QBO
- **Think** (Orient): Calculators analyze runway impact, prioritize decisions
- **Act** (Decide): Experience Services stage Must Pay/Can Delay
- **Review** (Act): Human approval → execute to QBO

### **2. Intelligence Layer (Smart Policies/Budgets - Phase 1)**
Policy engine that makes agentic behavior obvious:
- **Policy Rules**: "AI learns your payment preferences"
- **Budget Constraints**: "AI enforces spending limits"
- **Adaptive Learning**: "AI adjusts based on your approvals"
- **Vacation Mode**: "AI auto-pilots essential payments"

### **3. Agent Integration Layer (QBO Agents - Phase 2)**
Consume QBO agent outputs as inputs to agentic console:
- **Clean Data**: QBO agents categorize → Oodaloo orchestrates decisions
- **Task Automation**: QBO agents suggest → Oodaloo optimizes by runway
- **Complementary Layers**: Task-level (QBO) + Decision-level (Oodaloo)

---

## Architectural Patterns

### **Pattern 1: Agentic Loop (OODA Loop)**

**Implementation**:
```python
# runway/services/0_data_orchestrators/agentic_loop.py
class AgenticCashFlowOrchestrator:
    """
    Implements the OODA loop (agentic pattern) for weekly cash call.
    
    Sense → Think → Act → Review
    """
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        self.data_orchestrator = DigestDataOrchestrator(db)
        self.impact_calculator = ImpactCalculator(db, business_id)
        self.policy_engine = PolicyEngine(db, business_id)
    
    async def run_weekly_ritual(self) -> AgenticDecisionPackage:
        """
        Run the complete agentic loop for weekly cash call.
        
        Returns structured decision package for human review.
        """
        # 1. SENSE: Pull and stage raw data from QBO
        raw_data = await self.data_orchestrator.get_digest_data(self.business_id)
        
        # 2. THINK: Analyze runway impact, apply policies, prioritize
        decisions = self.impact_calculator.calculate_decisions(raw_data)
        policy_filtered = self.policy_engine.apply_policies(decisions)
        prioritized = self._prioritize_by_runway_impact(policy_filtered)
        
        # 3. ACT: Stage decisions for human review
        staged_package = self._stage_decision_package(prioritized)
        
        # 4. REVIEW: Return for human approval (not automated)
        return staged_package
```

**Agentic Characteristics**:
- ✅ Autonomous data gathering (Sense)
- ✅ Intelligent reasoning (Think)
- ✅ Action proposal (Act)
- ✅ Human-in-the-loop (Review)

### **Pattern 2: Policy Engine (Agent Rules)**

**Implementation**:
```python
# domains/policy/services/policy_engine.py
class PolicyEngine:
    """
    Enforces business rules and learns from user behavior.
    
    THIS IS WHERE AGENTIC INTELLIGENCE BECOMES OBVIOUS.
    """
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        self.learning_service = PolicyLearningService(db, business_id)
    
    def apply_policies(self, decisions: List[Decision]) -> List[Decision]:
        """
        Apply policy rules to filter and prioritize decisions.
        
        Policies = Agent Constraints
        """
        policies = self._get_active_policies()
        filtered_decisions = []
        
        for decision in decisions:
            # Check policy rules
            if self._passes_policy_checks(decision, policies):
                # Apply priority boost/penalty based on policies
                decision.priority_score = self._adjust_priority(
                    decision, 
                    policies
                )
                filtered_decisions.append(decision)
            else:
                # Queue for manual review
                decision.requires_override = True
                filtered_decisions.append(decision)
        
        # Learn from past approvals/rejections
        self.learning_service.update_policy_scores(filtered_decisions)
        
        return filtered_decisions
    
    def _get_active_policies(self) -> List[Policy]:
        """Get business policies with learned preferences."""
        return self.db.query(Policy).filter(
            Policy.business_id == self.business_id,
            Policy.is_active == True
        ).all()
```

**Policy Types**:
```python
# domains/policy/models/policy.py
class PolicyType(str, Enum):
    """Types of agent policies."""
    PAYMENT_RULE = "payment_rule"      # "Always pay vendor X early"
    BUDGET_LIMIT = "budget_limit"      # "Cap SaaS spend at $5k/mo"
    APPROVAL_THRESHOLD = "threshold"   # "Auto-approve < $500"
    VENDOR_PREFERENCE = "vendor_pref"  # "Prioritize vendor Y"
    VACATION_MODE = "vacation"         # "Auto-pilot essentials only"
    COLLECTION_STRATEGY = "collection" # "Gentle reminders for client Z"

class Policy(Base):
    """
    Business policy (agent rule).
    
    Policies define how the agent should behave.
    """
    policy_id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"))
    policy_type = Column(Enum(PolicyType))
    name = Column(String(255))
    description = Column(Text)
    
    # Policy logic
    conditions = Column(JSON)  # {"vendor_id": "123", "amount": {"<": 1000}}
    actions = Column(JSON)     # {"auto_approve": true, "priority_boost": 10}
    
    # Learning
    confidence_score = Column(Float, default=0.5)  # AI learns from approvals
    last_applied = Column(DateTime)
    approval_rate = Column(Float)  # Track how often human approves
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### **Pattern 3: Agent Integration (QBO Agents)**

**Implementation**:
```python
# infra/qbo/agent_integration.py
class QBOAgentIntegrationService:
    """
    Integrate with QBO agents as input sources.
    
    QBO Agents = Task-Level Automation (categorize, reconcile)
    Oodaloo = Decision-Level Orchestration (compress, optimize)
    
    These are complementary layers, not competing systems.
    """
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.smart_sync = SmartSyncService(business_id, "", None)
    
    async def get_agent_cleaned_data(self) -> Dict[str, Any]:
        """
        Pull data that QBO agents have already cleaned.
        
        QBO agents categorize/reconcile → Oodaloo orchestrates decisions
        """
        # Get bills that QBO agents have categorized
        bills = await self.smart_sync.get_bills_for_digest()
        
        # Get invoices with QBO agent matching
        invoices = await self.smart_sync.get_invoices_for_digest()
        
        # QBO agents provide cleaner inputs
        return {
            "bills": self._filter_agent_processed(bills),
            "invoices": self._filter_agent_processed(invoices),
            "agent_confidence": self._get_agent_confidence_scores(bills, invoices)
        }
    
    def _filter_agent_processed(self, items: List[Dict]) -> List[Dict]:
        """Prioritize items that QBO agents have processed."""
        # Items with high agent confidence get processed faster
        return sorted(
            items,
            key=lambda x: x.get("agent_confidence_score", 0),
            reverse=True
        )
```

**Integration Architecture**:
```
QBO Agents (Task-Level)
    ↓ (Clean Data)
SmartSyncService (Orchestration)
    ↓ (Structured Data)
Data Orchestrators (Sense)
    ↓ (Raw Decisions)
Calculators + Policy Engine (Think)
    ↓ (Prioritized Decisions)
Experience Services (Act)
    ↓ (Staged Package)
Human Review (Approve)
    ↓ (Execution)
QBO API (Execute)
```

---

## Implementation Phases

### **Phase 0: Agentic Positioning (Immediate - Q4 2025)**
**Goal**: Position existing architecture as agentic

**Actions**:
- Update all product messaging to "Agentic Cash Flow Console"
- Add "powered by AI" indicators to UI
- Emphasize OODA loop = agentic loop in documentation
- Register oodaloo.ai domain

**Technical Changes**: Minimal (messaging only)

### **Phase 1: Smart Policies/Budgets (Q1 2026)**
**Goal**: Build intelligence layer that makes agentic behavior obvious

**Actions**:
- Implement Policy Engine with learning capabilities
- Build Budget constraint system
- Create Vacation Mode (auto-pilot essentials)
- Add policy-based decision filtering

**Technical Changes**:
```
domains/policy/
├── models/
│   ├── policy.py (NEW - agent rules)
│   ├── budget.py (NEW - spending constraints)
│   └── policy_learning.py (NEW - adaptive learning)
├── services/
│   ├── policy_engine.py (NEW - apply policies)
│   ├── policy_learning_service.py (NEW - learn from approvals)
│   └── budget_enforcement_service.py (NEW - enforce limits)
└── routes/
    └── policy_management.py (NEW - manage policies)
```

### **Phase 2: QBO Agent Integration (Q2 2026)**
**Goal**: Integrate with QBO agents as input sources

**Actions**:
- Build QBOAgentIntegrationService
- Consume agent-cleaned data
- Show agent confidence scores in UI
- Position as "complementary layers"

**Technical Changes**:
```
infra/qbo/
├── agent_integration.py (NEW)
└── agent_confidence_scoring.py (NEW)
```

### **Phase 3: Advanced Agentic Features (Q3 2026)**
**Goal**: Build truly intelligent features

**Actions**:
- Predictive runway scenarios
- Smart vendor negotiation suggestions
- Anomaly detection and alerting
- Auto-classification with learning

**Technical Changes**: TBD (depends on Phase 1/2 learnings)

---

## Success Metrics

### **Product Metrics**
- [ ] Weekly ritual adoption > 70% (users rely on AI staging)
- [ ] Automation rate > 80% (AI handles most prep work)
- [ ] Policy accuracy > 90% (AI learns preferences correctly)
- [ ] Approval time < 5 minutes (AI compression works)

### **Perception Metrics**
- [ ] NPS > 50 on "AI helps me decide with confidence"
- [ ] User surveys: "Agentic" positioning resonates
- [ ] Market perception: Oodaloo seen as "AI-native"
- [ ] Analyst coverage: "Agentic cash flow console" category

### **Technical Metrics**
- [ ] Policy learning accuracy > 85%
- [ ] Agent confidence scores correlate with human approvals
- [ ] Decision staging latency < 2 seconds
- [ ] QBO agent integration uptime > 99%

---

## Benefits

### **Strategic Benefits**
1. **Defensible Positioning**: Agentic console vs QBO task agents
2. **Premium Pricing**: AI-native tools command $99-$299/mo
3. **Future-Proof**: Works with or without QBO agents
4. **Category Creation**: "Agentic cash flow console" is new

### **Technical Benefits**
1. **Clean Architecture**: OODA loop already implemented
2. **Extensible**: Policy engine enables unlimited rules
3. **Scalable**: Works for single business or 1000+ clients (RowCol)
4. **Maintainable**: Clear separation between agent layers

### **Business Benefits**
1. **Higher Conversion**: "AI-powered" attracts tech-forward ICP
2. **Lower Churn**: Intelligence creates switching costs
3. **Upsell Opportunity**: Smart Policies = $99/mo add-on
4. **CAS Firm Appeal**: RowCol agentic console = $500k+ TAM

---

## Risks and Mitigations

### **Risk 1: "Agentic" feels like overhype**
**Mitigation**: 
- Be specific: "Domain-specific AI agent for cash flow"
- Show don't tell: Policy engine demonstrates intelligence
- Human-in-the-loop: Never claim "fully autonomous"

### **Risk 2: QBO agents make us redundant**
**Mitigation**:
- Position as complementary: Task-level vs Decision-level
- Own judgment layer: QBO can't productize the weekly ritual
- Scale to multi-client: RowCol is outside QBO's scope

### **Risk 3: Policy engine is hard to build**
**Mitigation**:
- Start simple: Rules-based policies first
- Add ML later: Learn from user behavior over time
- Show early wins: Budget constraints are easy and obvious

### **Risk 4: Users don't trust AI decisions**
**Mitigation**:
- Human-in-the-loop always: AI stages, humans approve
- Explainable AI: Show why AI prioritized each decision
- Override capability: Users can always reject AI suggestions

---

## Related ADRs

- **ADR-001**: Domains/Runway separation (enables policy engine in domains/)
- **ADR-005**: QBO API strategy (SmartSyncService orchestrates agent integration)
- **ADR-006**: Data Orchestrator pattern (implements OODA loop / agentic pattern)
- **ADR-010**: RowCol Multi-Client (scales agentic console to firms)

---

## References

- **ChatGPT Analysis**: Agentic commerce trends and QBO agent positioning
- **STRATEGIC_AGENTIC_THREAT_ANALYSIS.md**: Comprehensive threat/opportunity analysis
- **AGENTIC_POSITIONING_STRATEGY.md**: Product positioning and messaging

---

**Last Updated**: 2025-09-30  
**Next Review**: After Phase 1 (Smart Policies) implementation  
**Status**: Ready for implementation


