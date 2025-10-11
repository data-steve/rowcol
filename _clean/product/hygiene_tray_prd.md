# Hygiene Tray PRD
*Data Quality & Cleanup Interface*

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: MVP Ready  

---

## **Product Overview**

The Hygiene Tray is the data quality control center for advisors managing multiple clients. It identifies bills and invoices with missing or incomplete data, sync issues, and data inconsistencies, then provides one-click cleanup suggestions to prepare data for decision-making.

### **Core Value Proposition**
- **For Advisors**: Quickly identify and fix data quality issues across all clients
- **For Clients**: Ensures clean, complete financial data for accurate decision-making
- **For Business**: Reduces reconciliation errors and improves data reliability

---

## **User Stories**

### **Primary User: CAS Advisor**
- **As an advisor**, I want to see all data quality issues across my client portfolio so I can prioritize cleanup efforts
- **As an advisor**, I want one-click fixes for common data problems so I can resolve issues quickly
- **As an advisor**, I want to filter issues by client and severity so I can focus on the most important problems
- **As an advisor**, I want to see the runway impact of fixing each issue so I can prioritize by business value

### **Secondary User: Client (via Advisor)**
- **As a client**, I want my financial data to be clean and complete so my advisor can make accurate recommendations
- **As a client**, I want to know when data issues are resolved so I can trust the insights I receive

---

## **Core Features**

### **1. Data Quality Detection**

#### **Post-Ramp Era Issues (Primary Focus)**
- **Sync & Integration Problems**: Ramp ↔ QBO sync failures, invoice system issues
- **Vendor Normalization Edge Cases**: QBO handles first-time normalization, but ongoing issues persist
- **Plaid Data Quality Issues**: Transaction categorization errors, date discrepancies
- **Cross-System Validation**: Data inconsistencies between QBO, Ramp, Plaid, and other systems
- **Manual Entry Errors**: Bills entered outside Ramp workflow

#### **Traditional Data Quality Issues (Secondary Focus)**
- **Missing Vendor Information**: Bills/invoices without vendor names or IDs
- **Incomplete Amounts**: Bills/invoices with zero, negative, or missing amounts
- **Missing Dates**: Bills/invoices without due dates, issue dates, or payment dates
- **Duplicate Records**: Potential duplicate bills or invoices
- **Orphaned Records**: Bills without corresponding invoices or vice versa

### **2. Issue Prioritization**
- **Severity Levels**: Critical, High, Medium, Low based on business impact
- **Runway Impact**: Shows how fixing each issue affects cash runway
- **Client Impact**: Prioritizes issues that affect multiple clients
- **Urgency**: Time-sensitive issues (bills due soon, overdue invoices)

### **3. One-Click Cleanup**
- **Auto-Fill Suggestions**: AI-powered suggestions for missing data
- **Bulk Operations**: Fix multiple similar issues at once
- **Validation Rules**: Prevent new data quality issues
- **Undo Capability**: Revert changes if needed

### **4. Progress Tracking**
- **Issue Count**: Total issues by client and severity
- **Resolution Rate**: Track cleanup progress over time
- **Quality Score**: Overall data quality metric per client (integrates with `DataQualityCalculator`)
- **Trend Analysis**: See improvement over time
- **Runway Impact**: Quantify how data quality affects cash runway calculations

### **5. Product-Specific Clean Definitions**
- **Integration with `runway/services/calculators`**: Uses existing `DataQualityCalculator` for hygiene scoring
- **Integration with `infra/config`**: Leverages `multi_rail_hygiene` feature gates
- **Custom Validation Rules**: Advisors can define client-specific "clean" criteria
- **Cross-System Validation**: Validates data consistency across all integrated systems

---

## **User Interface Design**

### **Main Tray View**
```
┌─────────────────────────────────────────────────────────┐
│ Hygiene Tray - Client: Acme Corp                        │
├─────────────────────────────────────────────────────────┤
│ 🔴 Critical (3)  🟡 High (7)  🟢 Medium (12)  ⚪ Low (5) │
├─────────────────────────────────────────────────────────┤
│ [Filter: All] [Client: Acme Corp] [Sort: Impact]        │
├─────────────────────────────────────────────────────────┤
│ 🔴 Missing Vendor - $5,000 Rent Bill                    │
│    Due: Oct 15 | Impact: +2 days runway                │
│    [Auto-Fill] [Manual Fix] [Ignore]                    │
├─────────────────────────────────────────────────────────┤
│ 🟡 Missing Due Date - $2,500 Office Supplies            │
│    Vendor: Staples | Impact: +1 day runway              │
│    [Set Oct 20] [Set Oct 25] [Ignore]                   │
├─────────────────────────────────────────────────────────┤
│ 🟢 Duplicate Bill - $1,200 Utilities                    │
│    Duplicate of Bill #1234 | Impact: +0.5 days runway   │
│    [Merge] [Delete] [Keep Both]                         │
└─────────────────────────────────────────────────────────┘
```

### **Client Portfolio View**
```
┌─────────────────────────────────────────────────────────┐
│ Hygiene Tray - Portfolio Overview                       │
├─────────────────────────────────────────────────────────┤
│ Client Name          | Issues | Score | Last Updated    │
├─────────────────────────────────────────────────────────┤
│ Acme Corp            | 27     | 85%   | 2 hours ago     │
│ Beta LLC             | 12     | 92%   | 1 day ago       │
│ Gamma Inc             | 8      | 95%   | 3 days ago      │
│ Delta Partners        | 15     | 88%   | 4 hours ago     │
└─────────────────────────────────────────────────────────┘
```

---

## **Technical Requirements**

### **Data Sources**
- **QBO Bills**: Vendor, amount, due date, issue date, status
- **QBO Invoices**: Customer, amount, due date, issue date, status
- **QBO Payments**: Payment date, amount, reference number
- **Sync Logs**: Last sync time, error messages, retry attempts

### **Data Quality Rules**
- **Vendor Validation**: Must have name and valid QBO vendor ID
- **Amount Validation**: Must be positive number, not zero
- **Date Validation**: Due dates must be in future, issue dates in past
- **Sync Validation**: Data must be within 24 hours of last sync
- **Duplicate Detection**: Similar amounts, dates, and vendors

### **Performance Requirements**
- **Load Time**: < 2 seconds for client list, < 1 second for issue list
- **Real-time Updates**: Issues update within 30 seconds of data changes
- **Bulk Operations**: Handle up to 100 issues at once
- **Concurrent Users**: Support 50+ advisors simultaneously

---

## **Success Metrics**

### **Advisor Engagement**
- **Daily Active Users**: 80% of advisors use hygiene tray daily
- **Issue Resolution Rate**: 70% of issues resolved within 24 hours
- **Time to Resolution**: Average 5 minutes per issue
- **Bulk Operation Usage**: 60% of issues resolved via bulk operations

### **Data Quality Improvement**
- **Quality Score Improvement**: 20% improvement in client data quality scores
- **Issue Reduction**: 50% reduction in recurring data quality issues
- **Sync Success Rate**: 95% successful sync rate across all clients
- **Error Reduction**: 80% reduction in reconciliation errors

### **Business Impact**
- **Advisor Efficiency**: 2 hours saved per week per advisor
- **Client Satisfaction**: 90% of clients report improved data accuracy
- **Revenue Impact**: 15% increase in advisor capacity
- **Support Reduction**: 40% reduction in data-related support tickets

---

## **MVP Scope**

### **Phase 1: Core Detection (Weeks 1-2)**
- Basic data quality detection (missing vendor, amounts, dates)
- Simple issue prioritization by severity
- Manual fix interface
- Client filtering and sorting

### **Phase 2: Smart Cleanup (Weeks 3-4)**
- AI-powered auto-fill suggestions
- Bulk operations for similar issues
- Progress tracking and quality scores
- Undo capability

### **Phase 3: Advanced Features (Weeks 5-6)**
- Duplicate detection and merging
- Sync issue detection and resolution
- Trend analysis and reporting
- Integration with decision console

---

## **Future Enhancements**

### **Advanced AI Features**
- **Predictive Cleanup**: Suggest fixes before issues occur
- **Pattern Recognition**: Learn from advisor cleanup patterns
- **Smart Validation**: Context-aware validation rules
- **Automated Resolution**: Auto-fix common issues without human intervention

### **Integration Features**
- **QBO Direct Fix**: Fix issues directly in QBO without switching apps
- **Client Notifications**: Notify clients when data issues are resolved
- **Audit Trail**: Complete history of all data quality fixes
- **Custom Rules**: Allow advisors to create custom validation rules

---

## **Competitive Analysis**

### **Current Solutions**
- **Keeper ($200-500/month)**: Bookkeeping automation with file review
  - Strength: QBO integration, automated error detection, client portal
  - Gap: Not advisor-focused, limited runway intelligence, expensive
- **ClientHub ($69/month)**: Practice management with client communication
  - Strength: Low cost, good client engagement, workflow automation
  - Gap: No data quality focus, basic bookkeeping features
- **QBO Built-in**: Basic validation, no prioritization or bulk operations
- **Ramp (99% accuracy)**: Excellent for bill data, but doesn't handle all edge cases
- **Plaid**: Real-time bank data, but has its own data quality issues
- **Spreadsheets**: Manual tracking, no automation or suggestions

### **Market Reality**
- **Ramp's 99% Accuracy**: Significantly reduces basic data quality issues
- **Plaid's Data Quality Issues**: Real-time bank data has its own accuracy problems
- **Vendor Normalization**: QBO handles first-time normalization, but ongoing issues persist
- **Cross-System Validation**: No tool validates data consistency across all systems
- **Advisor-Focused Intelligence**: No tool provides runway impact analysis for data issues

### **Our Advantages**
- **Financial Context**: Understands runway impact of data quality
- **Advisor Workflow**: Designed for multi-client management
- **Smart Suggestions**: AI-powered cleanup recommendations
- **Cross-System Focus**: Validates data across QBO, Ramp, Plaid, and other systems
- **Runway Intelligence**: Prioritizes issues by their impact on cash runway
- **Integrated Experience**: Part of complete advisor platform

---

## **Risk Mitigation**

### **Data Loss Risk**
- **Backup Strategy**: All changes backed up before application
- **Undo Capability**: Can revert any changes within 24 hours
- **Validation**: Multiple validation checks before applying changes
- **Testing**: Thorough testing with sample data before production

### **Performance Risk**
- **Caching**: Intelligent caching of data quality results
- **Pagination**: Large issue lists paginated for performance
- **Background Processing**: Heavy operations run in background
- **Monitoring**: Real-time performance monitoring and alerts

---

## **Acceptance Criteria**

### **Must Have**
- [ ] Detect missing vendor, amount, and date information
- [ ] Prioritize issues by severity and runway impact
- [ ] Provide one-click fixes for common issues
- [ ] Support bulk operations for similar issues
- [ ] Track progress and quality scores per client
- [ ] Filter and sort issues by client and severity

### **Should Have**
- [ ] AI-powered auto-fill suggestions
- [ ] Duplicate detection and merging
- [ ] Sync issue detection and resolution
- [ ] Undo capability for all changes
- [ ] Trend analysis and reporting
- [ ] Integration with decision console

### **Could Have**
- [ ] Predictive cleanup suggestions
- [ ] Custom validation rules
- [ ] Client notification system
- [ ] Advanced pattern recognition
- [ ] Automated resolution for common issues
- [ ] Complete audit trail

---

## **Dependencies**

### **Technical Dependencies**
- QBO API access for bill and invoice data
- Sync orchestrator for data freshness
- AI service for auto-fill suggestions
- Database for issue tracking and progress

### **Product Dependencies**
- Client management system for multi-client support
- User authentication and authorization
- Data quality rules engine
- Reporting and analytics system

---

## **Timeline**

### **Week 1-2: Foundation**
- Data quality detection engine
- Basic UI for issue display
- Manual fix interface
- Client filtering

### **Week 3-4: Smart Features**
- AI-powered suggestions
- Bulk operations
- Progress tracking
- Quality scores

### **Week 5-6: Polish**
- Duplicate detection
- Sync issue handling
- Performance optimization
- User testing and feedback

---

**This PRD provides a complete specification for the Hygiene Tray, ensuring it delivers maximum value to advisors while maintaining data quality and system performance.**
