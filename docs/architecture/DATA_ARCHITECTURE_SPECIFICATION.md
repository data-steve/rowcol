# Data Architecture Specification

*Version 2.0 - Multi-Rail Data Architecture for RowCol Financial Control Plane*

## **Overview**

This document defines the foundational data architecture patterns for RowCol's Financial Control Plane, specifying what data to mirror locally vs query live, sync patterns, and service boundaries. The architecture supports progressive implementation from QBO-only MVP to full multi-rail integration.

## **Architecture Principles**

### **1. Data Ownership Strategy**
- **Multi-Rail Source of Truth**: Each rail owns its domain (QBO=ledger, Ramp=A/P execution, Plaid=verification, Stripe=A/R execution)
- **RowCol is Control Plane**: We orchestrate decisions and provide insights across rails
- **Local Mirror for Performance**: Cache frequently accessed data for fast multi-client operations
- **Live Query for Accuracy**: Query real-time data when accuracy is critical
- **Progressive Implementation**: Start with QBO-only MVP, add rails incrementally

### **2. System-Wide Data Requirements**
- **Multi-Rail Reconciliation**: Cross-rail entity mapping and data consistency validation
- **Chain of Custody**: Complete audit trails for Approve → Execute → Verify → Record workflow
- **Compliance**: SOC2 audit requirements with immutable transaction logs
- **Data Integrity**: Zero data loss tolerance across all rails
- **Performance**: Fast multi-client operations (100+ clients) with proper tenant isolation

### **3. Service Boundaries**
- **Domain Services**: Own business logic and data models, rail-specific or rail-agnostic
- **Infrastructure Services**: Handle external API integration and data sync per rail
- **Runway Services**: Orchestrate user experiences and workflows across rails
- **Data Orchestrators**: Aggregate data from domain services for specific experiences
- **No Circular Dependencies**: Infrastructure never queries domain models directly

### **4. Sync Service Architecture**
*Note: Detailed sync service architecture moved to `comprehensive_architecture_multi_rail.md`*

**Key Patterns**:
- **BaseSyncService** (`infra/jobs/`): Generic orchestration, rate limiting, retry logic
- **RailSyncService** (`domains/*/services/`): Rail-specific business logic and convenience methods  
- **RailClient** (`infra/*/`): Raw API integration and technical concerns
- **RailOnboarding** (`domains/*/services/`): Authentication and account linking logic

## **System-Wide Data Requirements**

### **Multi-Rail Reconciliation Data**
- **Cross-Rail Entity Mapping**: QBO bill ID ↔ Ramp bill ID, QBO vendor ID ↔ Ramp vendor ID
- **Vendor Normalization**: Consistent vendor identity across all rails
- **Transaction Reconciliation**: Cross-rail transaction matching and validation
- **Data Consistency Validation**: Flag discrepancies between rails

### **Compliance and Audit Data**
- **Transaction Logs**: Immutable append-only logs for all financial data changes
- **Chain of Custody**: Complete audit trail for Approve → Execute → Verify → Record workflow
- **SOC2 Compliance**: Complete change tracking with who/what/when/where
- **Data Lineage**: Track data flow across all rails

### **Performance and Scale Data**
- **Multi-Client Isolation**: Tenant separation for 100+ clients per advisor
- **Fast Portfolio Queries**: Optimized queries for multi-client console
- **Caching Strategies**: Cross-rail data caching with appropriate TTL
- **Batch Operations**: Efficient bulk operations across clients

## **Data Storage Patterns**

### **Pattern 1: Mirror Locally (Database)**
**When to Use**: Data needed for frequent operations, calculations, or offline access

**Data Types**:
- **Bills**: For runway calculations, decision making, historical analysis
- **Invoices**: For AR analysis, variance tracking, client reporting
- **Vendors**: For normalization, categorization, compliance tracking
- **Customers**: For client management, payment terms, aging analysis
- **Historical Data**: For trend analysis, reporting, audit trails

**Sync Strategy**: 
- **Frequency**: Every 15 minutes via SmartSyncService
- **Trigger**: Scheduled jobs + webhook notifications
- **Deduplication**: SmartSyncService handles duplicate prevention
- **Error Handling**: Retry logic with exponential backoff

### **Pattern 2: Query Live (API)**
**When to Use**: Real-time data where accuracy is critical, or data that changes frequently

**Data Types**:
- **Current Balances**: For real-time cash position
- **Live Transactions**: For immediate updates
- **Connection Status**: For health monitoring
- **User Permissions**: For security checks

**Query Strategy**:
- **Frequency**: On-demand via SmartSyncService
- **Caching**: Short TTL (5-15 minutes) for performance
- **Error Handling**: Graceful degradation with cached data
- **Rate Limiting**: Respect API limits with backoff

### **Pattern 3: Transaction Logs (Append-Only Audit Trail)**
**When to Use**: Financial data changes requiring immutable audit trails for compliance

**Data Types**:
- **Bill Changes**: Amount changes, status updates, approval decisions
- **Payment Events**: Execution, reconciliation, failure events
- **Vendor Updates**: Information changes, compliance status updates
- **Cross-Rail Events**: Reconciliation decisions, data consistency checks

**Strategy**:
- **Append-Only**: Never update or delete transaction logs
- **Complete Snapshots**: Store full data state at time of change
- **Change Tracking**: Record what changed and why
- **Source Attribution**: Track which rail or user initiated the change

### **Pattern 4: Hybrid (Mirror + Live Query)**
**When to Use**: Data that needs both historical context and real-time accuracy

**Data Types**:
- **Bills**: Mirror for calculations, query live for current status
- **Invoices**: Mirror for reporting, query live for payment status
- **Balances**: Mirror for trends, query live for current position

**Strategy**:
- **Mirror**: Historical data, calculations, reporting
- **Live Query**: Current status, real-time updates
- **Sync**: Keep mirror updated with live data

## **Sync Patterns**

### **SmartSyncService Configuration**

#### **Data Fetching (Calculations/Dashboards)**
```python
strategy=SyncStrategy.DATA_FETCH
priority=SyncPriority.MEDIUM
use_cache=True
max_attempts=3
backoff_factor=1.5
```

#### **User Actions (Immediate Response)**
```python
strategy=SyncStrategy.USER_ACTION
priority=SyncPriority.HIGH
use_cache=False
max_attempts=3
backoff_factor=2.0
```

#### **Bulk Operations (Background Processing)**
```python
strategy=SyncStrategy.BULK_OPERATION
priority=SyncPriority.LOW
use_cache=True
max_attempts=2
backoff_factor=3.0
```

### **Sync Triggers**

#### **Scheduled Sync**
- **Frequency**: Every 15 minutes
- **Data**: Bills, invoices, vendors, customers
- **Purpose**: Keep local mirror current

#### **Webhook Sync**
- **Trigger**: QBO webhook notifications
- **Data**: Real-time changes
- **Purpose**: Immediate updates for critical data

#### **On-Demand Sync**
- **Trigger**: User actions, calculations
- **Data**: Current balances, live transactions
- **Purpose**: Real-time accuracy when needed

## **Service Responsibilities**

### **Domain Services (`domains/*/services/`)**
- **Own**: Business logic, data models, CRUD operations
- **Query**: Local database for mirrored data
- **Call**: Infrastructure services for live data
- **Never**: Query external APIs directly

### **Infrastructure Services (`infra/*/`)**
- **Own**: External API integration, data sync, caching
- **Provide**: Clean interfaces to domain services
- **Handle**: Rate limiting, retry logic, error handling
- **Never**: Query domain models directly

### **Runway Services (`runway/services/`)**
- **Own**: User experiences, workflows, orchestration
- **Use**: Domain services for business logic
- **Use**: Infrastructure services for data access
- **Never**: Query external APIs or domain models directly

## **Data Flow Patterns**

### **Pattern 1: Read Operations**
```
User Request → Runway Service → Domain Service → Local DB (mirrored data)
```

### **Pattern 2: Real-time Operations**
```
User Request → Runway Service → Domain Service → Infrastructure Service → Live API
```

### **Pattern 3: Write Operations**
```
User Action → Runway Service → Domain Service → Infrastructure Service → External API → Sync Back
```

### **Pattern 4: Background Sync**
```
Scheduled Job → Infrastructure Service → External API → Local DB Update
```

## **MVP Data Requirements**

### **QBO Ledger Rail MVP Data Needs**

#### **Mirror Locally (Database)**
- **Bills**: Due dates, amounts, vendors, categories, status
- **Invoices**: Outstanding AR, due dates, amounts, customers
- **Vendors**: Vendor information, payment terms, compliance status
- **Customers**: Customer information, payment terms, aging data
- **Historical Data**: Previous weeks' data for variance analysis

#### **Query Live (API)**
- **Current Balances**: Real-time cash position
- **Connection Status**: QBO integration health
- **Live Transactions**: Recent activity for verification

#### **Hybrid (Mirror + Live)**
- **Bills**: Mirror for calculations, query live for current status
- **Invoices**: Mirror for reporting, query live for payment status

### **Data Quality Requirements**

#### **Hygiene Validation**
- **Stale Data**: Flag data older than 24 hours
- **Missing Data**: Identify incomplete records
- **Data Consistency**: Validate cross-rail data alignment
- **Connection Health**: Monitor API connectivity

#### **Data Freshness**
- **Critical Data**: 15-minute sync frequency
- **Standard Data**: 1-hour sync frequency
- **Historical Data**: Daily sync frequency
- **Real-time Data**: On-demand query

## **Progressive Implementation Strategy**

### **Phase 1: QBO Ledger Rail MVP**
**Data Sources**: QBO ledger rail only
**Mirror Strategy**: Bills, invoices, balances from QBO with historical preservation
**Domain Services**: `domains/qbo/` for QBO-specific business logic
**Infrastructure**: `infra/qbo/` with SmartSyncService
**Experiences**: Digest, hygiene tray, decision console (ledger operations enabled)
**Operations**: Bill approvals, payment matching, hygiene fixes

### **Phase 2: Add Ramp Integration**
**Data Sources**: QBO (ledger) + Ramp (execution)
**Mirror Strategy**: Add Ramp bills and payment data
**Domain Services**: `domains/ramp/` for Ramp-specific business logic
**Infrastructure**: `infra/ramp/` with RampSmartSyncService
**Experiences**: Add bill approval and payment execution

### **Phase 3: Add Plaid Integration**
**Data Sources**: QBO + Ramp + Plaid (verification)
**Mirror Strategy**: Add Plaid bank data and transactions
**Domain Services**: `domains/plaid/` for Plaid-specific business logic
**Infrastructure**: `infra/plaid/` with PlaidSmartSyncService
**Experiences**: Add real-time balance verification

### **Phase 4: Add Stripe Integration**
**Data Sources**: QBO + Ramp + Plaid + Stripe (insights)
**Mirror Strategy**: Add Stripe AR data and payment insights
**Domain Services**: `domains/stripe/` for Stripe-specific business logic
**Infrastructure**: `infra/stripe/` with StripeSmartSyncService
**Experiences**: Add AR insights and payment analysis

## **Multi-Rail Data Orchestration**

### **Rail Responsibilities**
- **QBO (Ledger Rail)**: Ledger data, hygiene validation, audit trail, AR collections via QBO Payments
- **Ramp (A/P Execution Rail)**: Bill payment, payment processing, vendor management
- **Plaid (Verification Rail)**: Bank balances, transaction matching, cash verification, ACH payments
- **Stripe (A/R Execution Rail)**: AR payment processing, customer management, payment insights

### **Cross-Rail Sync Strategy**
- **Data Consistency**: Each rail syncs to QBO as source of truth
- **Conflict Resolution**: QBO wins for ledger data, execution rails win for their domain
- **Audit Trail**: All changes tracked across rails with timestamps and sources
- **Error Handling**: Graceful degradation when rails are unavailable

### **Service Architecture Evolution**
- **Current**: `domains/qbo/` + `infra/qbo/` + `runway/services/`
- **Future**: `domains/{qbo,ramp,plaid,stripe}/` + `infra/{qbo,ramp,plaid,stripe}/` + `runway/services/`
- **Shared**: `domains/core/` for rail-agnostic business logic

### **Domain Service Integration Patterns**

#### **Domain Service + Sync Service Integration**
```python
# Domain Service Pattern
class BillService:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use QBOSyncService for sync operations
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    def get_payment_ready_bills(self) -> List[Bill]:
        """Business logic - query mirror models."""
        return self.db.query(Bill).filter(
            Bill.business_id == self.business_id,
            Bill.status == 'unpaid',
            Bill.amount > 0
        ).all()
    
    async def sync_bills_from_qbo(self) -> Dict[str, Any]:
        """Sync operation - delegate to QBOSyncService."""
        return await self.qbo_sync.get_bills()
```

#### **Transaction Log Integration**
```python
# Domain Service with Transaction Log Integration
class BillService:
    async def create_bill(self, bill_data: Dict[str, Any]) -> Bill:
        """Create bill with transaction log."""
        # Create mirror model
        bill = Bill(
            business_id=self.business_id,
            vendor_name=bill_data['vendor_name'],
            amount=bill_data['amount'],
            due_date=bill_data['due_date']
        )
        self.db.add(bill)
        self.db.commit()
        
        # Create transaction log entry
        await self.qbo_sync.transaction_log_service.log_bill_creation(
            bill=bill,
            bill_data=bill_data,
            source="user",
            created_by_user_id=bill_data.get('user_id')
        )
        
        return bill
```

#### **Data Orchestrator Integration**
```python
# Data Orchestrator Pattern
class DigestDataOrchestrator:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        # Use domain services for business logic
        self.bill_service = BillService(db, business_id)
        self.invoice_service = InvoiceService(db, business_id)
        # Use sync service for sync operations
        self.qbo_sync = QBOSyncService(business_id, "", db)
    
    async def get_digest_data(self) -> Dict[str, Any]:
        """Aggregate data from domain services and sync service."""
        # Get business logic data from domain services
        payment_ready_bills = self.bill_service.get_payment_ready_bills()
        overdue_invoices = self.invoice_service.get_overdue_invoices()
        
        # Get sync data from QBOSyncService
        bills_data = await self.qbo_sync.get_bills()
        invoices_data = await self.qbo_sync.get_invoices()
        
        return {
            "payment_ready_bills": payment_ready_bills,
            "overdue_invoices": overdue_invoices,
            "bills_data": bills_data,
            "invoices_data": invoices_data
        }
```

### **Multi-Rail Domain Organization**

#### **Phase 1: QBO-Only MVP (Current)**
```
domains/
├── qbo/                    # QBO-specific business logic
│   └── services/
│       └── sync_service.py # QBOSyncService
├── ap/                     # A/P domain (QBO-honest)
│   └── services/
│       └── bill_service.py # Basic CRUD, no execution
├── ar/                     # A/R domain (QBO-honest)
│   └── services/
│       └── invoice_service.py # Basic CRUD, no execution
└── bank/                   # Bank domain (QBO-honest)
    └── services/
        └── balance_service.py # Basic CRUD, no execution

_parked/                    # QBO-incompatible features
├── domains/
│   ├── ap/
│   │   └── services/
│   │       └── bill_execution.py # Payment execution (Ramp)
│   ├── ar/
│   │   └── services/
│   │       └── invoice_execution.py # Invoice creation (Stripe)
│   └── bank/
│       └── services/
│           └── bank_management.py # Bank account management (Plaid)
└── runway/
    └── services/
        └── policy/         # Policy engine (moved from domains/)
```

#### **Phase 2: Multi-Rail Architecture (Future)**
```
domains/
├── qbo/                    # QBO ledger rail
│   └── services/
│       └── sync_service.py
├── ramp/                   # Ramp A/P execution rail
│   └── services/
│       └── payment_service.py
├── plaid/                  # Plaid verification rail
│   └── services/
│       └── verification_service.py
├── stripe/                 # Stripe A/R execution rail
│   └── services/
│       └── invoice_service.py
├── ap/                     # A/P domain (rail-agnostic)
│   └── services/
│       └── bill_service.py # Orchestrates across rails
├── ar/                     # A/R domain (rail-agnostic)
│   └── services/
│       └── invoice_service.py # Orchestrates across rails
└── bank/                   # Bank domain (rail-agnostic)
    └── services/
        └── balance_service.py # Orchestrates across rails
```

### **Service Responsibilities**

#### **Domain Services**
- **Business Logic**: Query mirror models, apply business rules
- **CRUD Operations**: Create, read, update, delete domain entities
- **Transaction Log Integration**: Create audit trails for business operations
- **Sync Delegation**: Delegate sync operations to rail-specific sync services

#### **Rail-Specific Sync Services**
- **Sync Operations**: Handle rail-specific API calls and data transformation
- **Transaction Log Integration**: Create audit trails for sync operations
- **Mirror State Updates**: Update mirror models with synced data
- **Error Handling**: Handle rail-specific errors and retry logic

#### **Data Orchestrators**
- **Data Aggregation**: Combine data from domain services and sync services
- **Purpose-Specific Filtering**: Filter data for specific experiences
- **Multi-Client Coordination**: Handle data for multiple clients
- **Experience Integration**: Provide data to runway services

## **Implementation Guidelines**

### **Database Schema**
- **Business ID**: All tables must include business_id for multi-tenancy
- **Sync Timestamps**: Track when data was last synced
- **Source Tracking**: Identify which rail provided the data
- **Version Control**: Handle data updates and conflicts

### **API Integration**
- **Rate Limiting**: Respect external API limits
- **Error Handling**: Graceful degradation with cached data
- **Retry Logic**: Exponential backoff for failed requests
- **Monitoring**: Track API health and performance

### **Caching Strategy**
- **Local Cache**: In-memory cache for frequently accessed data
- **Database Cache**: Persistent cache for historical data
- **TTL Management**: Appropriate expiration for different data types
- **Cache Invalidation**: Clear cache when data changes

## **Validation Criteria**

### **Data Accuracy**
- **Mirror Data**: Within 15 minutes of source
- **Live Data**: Real-time accuracy
- **Calculations**: Consistent with source data
- **Audit Trail**: Complete change tracking

### **Performance**
- **Dashboard Load**: <3 seconds for portfolio view
- **Calculations**: <1 second for runway calculations
- **Sync Operations**: Complete within 15 minutes
- **API Responses**: <300ms for user actions

### **Reliability**
- **Uptime**: 99.9% availability
- **Data Loss**: Zero data loss tolerance
- **Error Recovery**: Graceful handling of API failures
- **Monitoring**: Real-time health monitoring

## **Next Steps**

1. **Code Audit**: Review existing code against this architecture
2. **Gap Analysis**: Identify what needs to be implemented
3. **Implementation Plan**: Create tasks for missing patterns
4. **Testing Strategy**: Validate data accuracy and performance
5. **Monitoring Setup**: Track data quality and sync health

---

*This specification provides the foundation for implementing RowCol's data architecture patterns for the QBO-only MVP and future multi-rail expansion.*
