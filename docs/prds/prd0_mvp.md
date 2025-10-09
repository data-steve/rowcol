# RowCol MVP Product Requirements Document (PRD)

## **🎯 MVP Vision**
**Goal**: Deliver a QBO-only weekly cash call dashboard that replaces manual spreadsheets for CAS 2.0 firms, proving the core value proposition before expanding to multi-rail.

**Success Metrics**:
- Advisors save 30+ minutes/client/week vs manual spreadsheet
- 50%+ of bills managed via RowCol (QBO-only initially)
- Eliminate spreadsheets by week 3
- Strengthen client trust with branded deliverables

## **👥 Target Users**
**Primary**: CAS 2.0 advisors managing 20-100 SMB clients ($1-5M revenue, 10-30 staff)
**Secondary**: CAS firm owners needing scalable advisory workflows

## **🎯 Core Jobs to Be Done (JTBD)**

### **JTBD 1: Weekly Cash Call Preparation**
**As a CAS advisor, I need to quickly assess each client's cash health so I can identify who needs attention and prepare for weekly cash calls.**

**Current Pain**: Manual spreadsheet aggregation takes 30-45 minutes/client
**RowCol Solution**: Automated dashboard showing runway, bills, and variances

**User Workflow**:
1. Open RowCol dashboard
2. See portfolio view with red/yellow/green status
3. Drill down to client details
4. Review runway, bills due, and variances
5. Identify clients needing attention

**Success Criteria**:
- Dashboard loads in <3 seconds
- Shows accurate runway calculations
- Highlights critical issues (red status)
- Enables quick client prioritization

### **JTBD 2: Client Cash Decision Making**
**As a CAS advisor, I need to make informed payment decisions with guardrails so I can approve bills safely and maintain client cash discipline.**

**Current Pain**: No guardrails, manual calculations, risk of cash flow issues
**RowCol Solution**: Decision console with runway impact and guardrails

**User Workflow**:
1. Review bills in decision console
2. See runway impact for each bill
3. Apply guardrails (14-day buffer, essential vs discretionary)
4. Approve or hold bills based on impact
5. Track decisions for client reporting

**Success Criteria**:
- Shows accurate runway impact calculations
- Enforces 14-day buffer guardrail
- Prioritizes essential bills (payroll, rent, taxes)
- Tracks all decisions for audit trail

### **JTBD 3: Client Deliverable Generation**
**As a CAS advisor, I need to generate branded weekly cash reports so I can prove proactive governance and justify client retainers.**

**Current Pain**: No branded deliverables, manual report creation
**RowCol Solution**: Automated weekly cash digest with audit trail

**User Workflow**:
1. Review weekly cash position
2. Generate branded digest report
3. Send to client with audit trail
4. Track client engagement and feedback

**Success Criteria**:
- Generates professional branded reports
- Includes audit trail of all decisions
- Shows variance analysis vs previous week
- Enables client engagement tracking

## **📊 Data Requirements**

### **QBO Data Sources (MVP)**
- **Bills**: Due dates, amounts, vendors, categories
- **Invoices**: Outstanding AR, due dates, amounts
- **Bank Accounts**: Current balances, transaction history
- **Vendors**: Vendor information, payment terms
- **Customers**: Customer information, payment terms

### **Calculated Metrics**
- **Runway Buffer**: Days of cash remaining at current burn rate
- **Bill Impact**: How each bill affects runway
- **Variance Analysis**: Changes vs previous week
- **Priority Scoring**: Essential vs discretionary bills

## **🔧 Technical Requirements**

### **Performance Requirements**
- Dashboard loads in <3 seconds
- Runway calculations complete in <1 second
- Supports 20-100 clients per advisor
- Handles 50+ bills per client

### **Data Freshness Requirements**
- QBO data synced every 15 minutes
- Real-time runway calculations
- Historical data for variance analysis
- Audit trail for all decisions

### **Integration Requirements**
- QBO API integration (ledger rail for MVP)
- Email delivery for client reports
- PDF generation for branded deliverables
- Multi-tenant architecture

## **🎨 User Experience Requirements**

### **Dashboard Layout**
- **Portfolio View**: Multi-client status overview
- **Client Detail**: Individual client cash analysis
- **Decision Console**: Bill approval interface
- **Reports**: Client deliverable generation

### **Key Features**
- **Red/Yellow/Green Status**: Quick visual health indicators
- **Runway Calculator**: Real-time cash flow analysis
- **Guardrail Enforcement**: Automatic safety checks
- **Audit Trail**: Complete decision history
- **Branded Reports**: Professional client deliverables

## **🚀 MVP Scope (QBO-Only)**

### **Included Features**
- QBO ledger rail integration and sync
- Runway calculation and visualization
- Bill approval workflow with guardrails (QBO ledger operations)
- Client digest generation and delivery
- Multi-client portfolio management
- Audit trail and decision tracking

### **Excluded Features (Future Phases)**
- Ramp payment execution (Phase 1)
- Plaid bank verification (Phase 1)
- Stripe AR insights (Phase 2)
- Multi-rail reconciliation (Phase 2)
- Advanced forecasting (Phase 2)

## **📈 Success Metrics**

### **Advisor Efficiency**
- Time per client: 5-10 minutes vs 30-45 minutes
- Bills managed via RowCol: 50%+ target
- Spreadsheet elimination: By week 3
- Client satisfaction: 90%+ approval

### **Business Impact**
- Client retention: Improved through better service
- Advisor capacity: 2-3x more clients per advisor
- Revenue growth: $5k-$10k/month retainers justified
- Competitive advantage: Unique multi-client capability

## **🔍 Validation Criteria**

### **Technical Validation**
- All QBO data syncs correctly
- Runway calculations are accurate
- Guardrails prevent unsafe decisions
- Reports generate without errors

### **User Validation**
- Advisors can complete weekly cash calls in <10 minutes
- Clients receive professional branded reports
- Decision audit trail is complete and accurate
- System handles realistic data volumes

## **📋 Implementation Phases**

### **Phase 0.5: QBO Ledger Rail MVP (3-4 weeks)**
- QBO ledger rail integration and sync
- Runway calculation engine
- Basic dashboard and decision console
- Client digest generation
- Multi-tenant architecture

### **Phase 1: Add Ramp (3-4 weeks)**
- Ramp payment execution
- Multi-rail bill management
- Enhanced decision workflow
- Ramp-specific hygiene issues

### **Phase 2: Add Plaid + Stripe (3-4 weeks)**
- Plaid bank verification
- Stripe AR insights
- Multi-rail reconciliation
- Advanced forecasting

## **💡 Key Insights**

### **Why QBO Ledger Rail MVP Works**
- **Proves Core Value**: Weekly cash calls are the primary pain point
- **Enables Learning**: Real user feedback before adding complexity
- **Preserves Investment**: 80% of existing code is reusable
- **Sets Up Success**: Each phase builds on the previous one

### **Why This Approach is Strategic**
- **Market Validation**: Prove value before building complexity
- **Technical Foundation**: Solid architecture for future expansion
- **User Learning**: Discover what CAS firms actually need
- **Competitive Advantage**: First-mover in multi-client cash discipline

This PRD bridges the gap between your vision and the software requirements, giving you the concrete foundation needed to align your code and build the MVP successfully.