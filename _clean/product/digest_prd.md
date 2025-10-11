# Digest PRD
*Advisor Overview Dashboard*

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: MVP Ready  

---

## **Product Overview**

The Digest is the first tab in the advisor UI, providing a comprehensive overview of the most important hygiene issues, decisions, and KPIs across all clients. It serves as the advisor's command center, offering insights and recommendations to guide focused action in the Hygiene Tray and Decision Console.

### **Core Value Proposition**
- **For Advisors**: Single-pane-of-glass view of critical issues across all clients
- **For Clients**: Ensures advisors have complete visibility into their financial health
- **For Business**: Enables advisors to scale efficiently across multiple clients

---

## **User Stories**

### **Primary User: CAS Advisor**
- **As an advisor**, I want to see the most critical issues across all my clients so I can prioritize my time effectively
- **As an advisor**, I want to understand the runway impact of each issue so I can focus on high-value fixes
- **As an advisor**, I want to see trends and patterns across my client portfolio so I can identify systemic issues
- **As an advisor**, I want quick access to detailed views so I can drill down into specific problems

### **Secondary User: Client (via Advisor)**
- **As a client**, I want my advisor to have complete visibility into my financial health so they can provide better guidance
- **As a client**, I want to know when my advisor identifies and resolves issues so I can trust their expertise

---

## **Core Features**

### **1. Portfolio Overview**
- **Client Status Grid**: Red/yellow/green status indicators for each client
- **Critical Issues Count**: Number of high-priority issues per client
- **Runway Status**: Days of runway remaining for each client
- **Last Updated**: When data was last refreshed for each client

### **2. Priority Issues Dashboard**
- **Most Costly Issues**: Issues with highest runway impact across all clients
- **Urgent Actions**: Items requiring immediate attention
- **Trending Problems**: Issues that are increasing in frequency
- **Resolution Progress**: Track progress on issue resolution

### **3. KPI Summary**
- **Data Quality Score**: Overall data quality across all clients
- **Sync Health**: Status of data synchronization with QBO
- **Issue Resolution Rate**: How quickly issues are being resolved
- **Client Satisfaction**: Feedback and satisfaction metrics

### **4. Quick Actions**
- **Jump to Hygiene Tray**: Direct access to data quality issues
- **Jump to Decision Console**: Direct access to decision-ready items
- **Bulk Operations**: Perform actions across multiple clients
- **Export Reports**: Generate summary reports for clients

---

## **User Interface Design**

### **Main Digest View**
```
┌─────────────────────────────────────────────────────────┐
│ Digest - Advisor Overview                               │
├─────────────────────────────────────────────────────────┤
│ 📊 Portfolio Health: 85% | 🔄 Last Sync: 2 min ago     │
├─────────────────────────────────────────────────────────┤
│ 🚨 Critical Issues (12)  | ⚡ Urgent Actions (5)        │
│ 🟡 High Priority (23)    | 📈 Trending Up (3)           │
├─────────────────────────────────────────────────────────┤
│ Client Name          | Status | Issues | Runway | Score │
├─────────────────────────────────────────────────────────┤
│ Acme Corp            | 🔴     | 8      | 12d    | 75%   │
│ Beta LLC             | 🟡     | 3      | 28d    | 92%   │
│ Gamma Inc             | 🟢     | 1      | 45d    | 98%   │
│ Delta Partners        | 🔴     | 5      | 8d     | 80%   │
├─────────────────────────────────────────────────────────┤
│ 🎯 Top Issues by Runway Impact                         │
│ • Acme Corp: Missing $15k vendor data → +3 days        │
│ • Delta Partners: Overdue $8k invoice → +2 days        │
│ • Beta LLC: Sync error on bills → +1 day               │
├─────────────────────────────────────────────────────────┤
│ [Open Hygiene Tray] [Open Decision Console] [Export]    │
└─────────────────────────────────────────────────────────┘
```

### **Issue Detail View**
```
┌─────────────────────────────────────────────────────────┐
│ Issue Detail: Missing Vendor Data - Acme Corp           │
├─────────────────────────────────────────────────────────┤
│ Impact: +3 days runway | Priority: Critical             │
│ Affected: 5 bills totaling $15,000                     │
│ Last Updated: 2 hours ago                              │
├─────────────────────────────────────────────────────────┤
│ Bills Missing Vendor:                                   │
│ • $5,000 Rent Bill (Due Oct 15)                        │
│ • $3,000 Utilities (Due Oct 20)                        │
│ • $2,000 Office Supplies (Due Oct 25)                  │
│ • $3,000 Insurance (Due Oct 30)                        │
│ • $2,000 Marketing (Due Nov 5)                         │
├─────────────────────────────────────────────────────────┤
│ [Fix in Hygiene Tray] [View in QBO] [Ignore]            │
└─────────────────────────────────────────────────────────┘
```

---

## **Technical Requirements**

### **Data Sources**
- **Hygiene Tray**: Data quality issues and resolution status
- **Decision Console**: Decision-ready items and runway calculations
- **QBO Sync**: Real-time data freshness and sync status
- **Client Management**: Client information and relationship data

### **Real-time Updates**
- **WebSocket Connection**: Live updates for critical changes
- **Polling Fallback**: 30-second polling for data refresh
- **Cache Strategy**: 5-minute cache for non-critical data
- **Error Handling**: Graceful degradation when services unavailable

### **Performance Requirements**
- **Load Time**: < 1 second for main digest view
- **Update Frequency**: Critical issues update within 30 seconds
- **Concurrent Users**: Support 100+ advisors simultaneously
- **Data Volume**: Handle 1000+ clients per advisor

---

## **Success Metrics**

### **Advisor Engagement**
- **Daily Active Users**: 90% of advisors check digest daily
- **Time to Action**: 60% of issues acted upon within 1 hour
- **Drill-down Rate**: 70% of advisors drill down into issue details
- **Bulk Action Usage**: 40% of actions performed via bulk operations

### **Issue Resolution**
- **Resolution Time**: 50% reduction in time to resolve critical issues
- **Issue Prevention**: 30% reduction in recurring issues
- **Client Satisfaction**: 85% of clients report improved service quality
- **Advisor Efficiency**: 3 hours saved per week per advisor

### **Business Impact**
- **Client Retention**: 95% client retention rate
- **Advisor Capacity**: 20% increase in clients per advisor
- **Revenue Growth**: 25% increase in advisor revenue
- **Support Reduction**: 50% reduction in support tickets

---

## **MVP Scope**

### **Phase 1: Basic Overview (Weeks 1-2)**
- Client status grid with basic metrics
- Critical issues list with runway impact
- Simple filtering and sorting
- Basic drill-down to detailed views

### **Phase 2: Smart Insights (Weeks 3-4)**
- AI-powered issue prioritization
- Trend analysis and pattern recognition
- Bulk operations and quick actions
- Export and reporting capabilities

### **Phase 3: Advanced Features (Weeks 5-6)**
- Real-time updates and notifications
- Advanced analytics and forecasting
- Custom dashboards and preferences
- Integration with external tools

---

## **Future Enhancements**

### **Advanced Analytics**
- **Predictive Insights**: Forecast potential issues before they occur
- **Pattern Recognition**: Identify systemic issues across clients
- **Benchmarking**: Compare client performance to industry standards
- **ROI Analysis**: Calculate return on investment for different actions

### **Collaboration Features**
- **Team Dashboards**: Multi-advisor team views
- **Client Sharing**: Share insights with clients directly
- **Comment System**: Add notes and context to issues
- **Workflow Management**: Assign and track issue resolution

---

## **Competitive Analysis**

### **Current Solutions**
- **QBO Dashboard**: Basic financial overview, no issue prioritization
- **Spreadsheets**: Manual tracking, no real-time updates
- **Generic Tools**: Not designed for financial advisory workflow

### **Our Advantages**
- **Financial Context**: Understands runway impact and business value
- **Multi-Client Focus**: Designed for advisors managing multiple clients
- **Real-time Updates**: Live data refresh and issue tracking
- **Integrated Experience**: Seamless connection to hygiene tray and console

---

## **Risk Mitigation**

### **Data Accuracy Risk**
- **Validation**: Multiple validation checks for all calculations
- **Audit Trail**: Complete history of all data changes
- **Testing**: Comprehensive testing with real client data
- **Monitoring**: Real-time alerts for data inconsistencies

### **Performance Risk**
- **Caching**: Intelligent caching strategy for frequently accessed data
- **Pagination**: Large datasets paginated for performance
- **Background Processing**: Heavy calculations run in background
- **Load Balancing**: Distribute load across multiple servers

---

## **Acceptance Criteria**

### **Must Have**
- [ ] Client status grid with red/yellow/green indicators
- [ ] Critical issues list with runway impact
- [ ] Basic filtering and sorting capabilities
- [ ] Drill-down to detailed issue views
- [ ] Quick access to hygiene tray and decision console
- [ ] Real-time data refresh and updates

### **Should Have**
- [ ] AI-powered issue prioritization
- [ ] Trend analysis and pattern recognition
- [ ] Bulk operations and quick actions
- [ ] Export and reporting capabilities
- [ ] Customizable dashboard preferences
- [ ] Advanced analytics and insights

### **Could Have**
- [ ] Predictive issue forecasting
- [ ] Team collaboration features
- [ ] Client sharing capabilities
- [ ] Advanced benchmarking
- [ ] Mobile-optimized interface
- [ ] Voice-activated commands

---

## **Dependencies**

### **Technical Dependencies**
- Hygiene Tray service for issue data
- Decision Console service for decision-ready items
- QBO sync service for real-time data
- Client management system for portfolio data

### **Product Dependencies**
- User authentication and authorization
- Data quality rules engine
- Runway calculation engine
- Reporting and analytics system

---

## **Timeline**

### **Week 1-2: Foundation**
- Basic client status grid
- Critical issues list
- Simple filtering and sorting
- Basic drill-down functionality

### **Week 3-4: Smart Features**
- AI-powered prioritization
- Trend analysis
- Bulk operations
- Export capabilities

### **Week 5-6: Polish**
- Real-time updates
- Advanced analytics
- Performance optimization
- User testing and feedback

---

**This PRD provides a complete specification for the Digest, ensuring it serves as the central command center for advisors while providing maximum value and efficiency.**
