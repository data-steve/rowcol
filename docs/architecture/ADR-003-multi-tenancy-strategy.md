# ADR-003: Multi-Tenancy Strategy (Firm-First)

**Date**: 2025-09-30 (Updated from 2025-09-17)  
**Status**: Accepted  
**Decision**: Single-Database Multi-Tenancy with **Firm-First hierarchy**: `firm_id` → `client_id` (business_id)

## Context

**STRATEGIC PIVOT (2025-09-30)**: Based on market feedback from Levi Morehouse (Aiwyn.ai President), Oodaloo is **pivoting to CAS firms as primary ICP**, not individual business owners.

**Why**: 
- Owners won't maintain data completeness (missing bills = broken trust)
- CAS firms can ensure data quality and enforce the ritual
- $50/mo per client scales better than $99/mo per owner
- Weekly cash call is unaddressed opportunity for CAS firms

**Multi-tenancy must now support firm-first from Phase 3** (not Phase 4+). CAS firms manage 20-100 clients, with firm-level users, RBAC, and batch workflows.

## Decision

**Single-Database Multi-Tenancy** using `business_id` as primary tenant identifier, with migration path to **Database-per-Tenant** for enterprise CAS firms.

### **Primary Tenancy Model**
**Pattern**: Business-Centric Tenancy + Row-Level Security
- `business_id` is the primary tenant identifier
- All domain models include `business_id` foreign key
- Row-level security enforced at application and database levels
- QBO integrations are per-business (each business has own QBO connection)

```python
# All domain models follow this pattern
class Bill(Base):
    __tablename__ = "bills"
    
    bill_id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    qbo_bill_id = Column(String(50))  # QBO-specific ID
    vendor_name = Column(String(255))
    amount_cents = Column(Integer)
    
    # Automatic tenant filtering in queries
    __table_args__ = (
        Index('idx_bills_business_id', 'business_id'),
    )
```

### **Tenant Hierarchy (Firm-First)**
```
Firm (Primary Tenant) - CAS accounting firm
├── Firm Staff (admins, staff, view-only)
├── Clients (Businesses) - Sub-tenants
│   ├── QBO Integration (one per client)
│   ├── Bank Accounts (from QBO + Plaid)
│   ├── Transactions (from QBO)
│   ├── Runway Reserves (Oodaloo-specific)
│   ├── Tray Items (Oodaloo-specific)
│   └── Digest Settings (Oodaloo-specific)
├── Firm Dashboard (batch runway view across clients)
├── Data Quality Scoring (per-client completeness)
└── Firm Reporting (aggregate analytics)

Future: Direct Owner (business.firm_id = NULL)
└── Same as Client structure, but no firm association
```

## Implementation Strategy

### **Phase 0-1: Single Business Tenancy**

**Current Implementation**:
- Each business is an independent tenant
- Direct QBO connection per business
- Simple user authentication (business owner only)
- No cross-business data sharing

```python
# Tenant context in API routes
@router.get("/runway/tray/items")
async def get_tray_items(
    business_id: str = Depends(get_current_business_id),
    db: Session = Depends(get_db)
):
    # Automatic tenant filtering
    items = db.query(TrayItem).filter(
        TrayItem.business_id == business_id
    ).all()
    return items
```

### **Phase 3: Firm-First Multi-Tenancy** 🔴 CURRENT PRIORITY

**Immediate Implementation** (Weeks 1-2, 40h):
- CAS firms manage multiple business sub-tenants
- Firm-level users with RBAC permissions
- Cross-business reporting and analytics
- Hierarchical data access patterns

```python
# Phase 3: Firm-first hierarchical model
class Firm(Base):
    __tablename__ = "firms"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    clients = relationship("Business", back_populates="firm")
    staff = relationship("FirmStaff", back_populates="firm")

class FirmStaff(Base):
    __tablename__ = "firm_staff"
    id = Column(Integer, primary_key=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)  # admin, staff, view_only
    active = Column(Boolean, default=True)
    
    # Relationships
    firm = relationship("Firm", back_populates="staff")
    user = relationship("User")

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    # NULL firm_id = direct owner (future Phase 7+)
    # Non-NULL firm_id = CAS firm client
    name = Column(String(255), nullable=False)
    qbo_realm_id = Column(String(255))
    
    # Relationships
    firm = relationship("Firm", back_populates="clients")
```

## Data Isolation Patterns

### **Application-Level Isolation**

**Tenant Context Injection**:
```python
# Dependency injection for tenant context
def get_current_business_id(
    current_user: User = Depends(get_current_user)
) -> str:
    if not current_user.business_id:
        raise HTTPException(status_code=403, detail="No business access")
    return current_user.business_id

# Service layer with automatic tenant filtering
class TrayService:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
    
    def get_tray_items(self) -> List[TrayItem]:
        return self.db.query(TrayItem).filter(
            TrayItem.business_id == self.business_id
        ).all()
```

**Query Filtering**:
```python
# Base service class with tenant filtering
class TenantAwareService:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
    
    def _filter_by_tenant(self, query):
        """Add tenant filtering to any query."""
        return query.filter_by(business_id=self.business_id)
```

### **Database-Level Isolation**

**Row-Level Security (Future)**:
```sql
-- PostgreSQL RLS for additional security
CREATE POLICY business_isolation ON bills
    FOR ALL TO application_user
    USING (business_id = current_setting('app.current_business_id'));

ALTER TABLE bills ENABLE ROW LEVEL SECURITY;
```

**Indexes for Performance**:
```sql
-- Compound indexes for tenant + common queries
CREATE INDEX idx_bills_business_date ON bills(business_id, bill_date);
CREATE INDEX idx_transactions_business_type ON transactions(business_id, transaction_type);
CREATE INDEX idx_tray_items_business_status ON tray_items(business_id, status);
```

## Security Considerations

### **Tenant Data Leakage Prevention**

**API Route Security**:
```python
# All routes must verify tenant access
@router.get("/runway/businesses/{business_id}/tray")
async def get_business_tray(
    business_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user has access to this business
    if current_user.business_id != business_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Proceed with tenant-filtered queries
    tray_service = TrayService(db, business_id)
    return tray_service.get_tray_items()
```

**Service Layer Security**:
```python
# Services must validate tenant context
class DigestService:
    def generate_digest(self, business_id: str):
        # Verify business exists and user has access
        business = self.db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise BusinessNotFoundError(f"Business {business_id} not found")
        
        # All subsequent queries automatically tenant-filtered
        return self._calculate_runway_for_business(business_id)
```

### **QBO Integration Security**

Each business maintains its own QBO connection:

```python
# QBO integration per tenant
class SmartSyncService:  # Unified QBO coordinator
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.integration = self._get_business_integration(business_id)
    
    def _get_business_integration(self, business_id: str) -> Integration:
        integration = db.query(Integration).filter(
            Integration.business_id == business_id,
            Integration.platform == "qbo"
        ).first()
        
        if not integration:
            raise IntegrationError(f"QBO not connected for business {business_id}")
        
        return integration
```

## Performance Considerations

### **Database Performance**

**Indexing Strategy**:
- All tenant queries use `business_id` as first index column
- Compound indexes for common query patterns
- Partitioning by `business_id` for large tables (future)

**Query Optimization**:
```python
# Efficient tenant queries
def get_recent_transactions(business_id: str, days: int = 30):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    return db.query(Transaction).filter(
        Transaction.business_id == business_id,  # Use index
        Transaction.transaction_date >= cutoff_date
    ).order_by(Transaction.transaction_date.desc()).all()
```

### **Scaling Strategy**

**Phase 0-1**: Single database, business-level tenancy
- **Target**: 100-1000 businesses
- **Performance**: <100ms API response times
- **Storage**: SQLite → PostgreSQL migration

**Phase 2+**: Database-per-tenant for enterprise customers
- **Target**: Large CAS firms with 100+ clients
- **Performance**: Dedicated resources per major tenant
- **Storage**: Separate databases for enterprise tiers

## Migration Strategy

### **Current → Future Migration Path**

**Step 1**: Maintain current business-centric model
```python
# Current: Direct business tenancy
business_id = "direct_customer_123"
firm_id = None  # No firm association
```

**Step 2**: Add optional firm association
```python
# Future: Optional firm hierarchy
business_id = "client_of_cas_firm_456" 
firm_id = "cas_firm_789"  # Associated with CAS firm
```

**Step 3**: Implement hierarchical access
```python
# Future: Multi-level tenant access
def get_accessible_businesses(user: User) -> List[str]:
    if user.firm_id:
        # CAS firm user can access all firm businesses
        return get_firm_businesses(user.firm_id)
    else:
        # Direct customer accesses only their business
        return [user.business_id]
```

## Testing Strategy

Multi-tenancy testing approaches are covered in **ADR-002: Testing Strategy**, including tenant isolation verification, performance testing, and decoupled testing patterns for tenant-aware services.

## Benefits

### **Positive Outcomes**

✅ **Data Isolation**: Complete separation between businesses  
✅ **Development Simplicity**: Single codebase, single database (initially)  
✅ **Performance**: Efficient queries with proper indexing  
✅ **Scalability**: Clear migration path to database-per-tenant  
✅ **Security**: Application and database-level isolation  
✅ **Cost Efficiency**: Shared infrastructure for small businesses  

### **Business Value**

- **Customer Trust**: Guaranteed data isolation
- **Regulatory Compliance**: Meet data privacy requirements
- **Scalability**: Support growth from startup to enterprise
- **Development Velocity**: Single codebase maintenance

## Risks and Mitigations

### **Risk**: Tenant data leakage through application bugs
**Mitigation**: 
- Mandatory tenant filtering in all queries
- Automated testing for tenant isolation
- Code review requirements for tenant-aware code

### **Risk**: Performance degradation with scale
**Mitigation**:
- Database partitioning by tenant for large tables
- Migration to database-per-tenant for enterprise customers
- Comprehensive performance monitoring

### **Risk**: Complex tenant hierarchy in RowCol phase
**Mitigation**:
- Incremental implementation starting with simple business tenancy
- Clear service layer abstractions for tenant context
- Comprehensive RBAC system for hierarchical access

## Implementation Guidelines

### **All Models Must Include business_id**

```python
# Required pattern for all domain models
class DomainModel(Base):
    model_id = Column(String(36), primary_key=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    
    # Index for tenant queries
    __table_args__ = (
        Index(f'idx_{__tablename__}_business_id', 'business_id'),
    )
```

### **All Services Must Filter by Tenant**

```python
# Required pattern for all services
class DomainService:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
    
    def _base_query(self, model_class):
        return self.db.query(model_class).filter(
            model_class.business_id == self.business_id
        )
```

### **All Routes Must Verify Tenant Access**

```python
# Required pattern for all API routes
@router.get("/endpoint")
async def endpoint(
    business_id: str = Depends(get_current_business_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Tenant verification is automatic via get_current_business_id
    service = DomainService(db, business_id)
    return service.get_data()
```

## References

- **Multi-Tenant Architecture**: Guo, Lei. "Multi-Tenant SaaS Architecture"
- **Row-Level Security**: PostgreSQL Documentation
- **Oodaloo Models**: `domains/core/models/business.py`
- **Tenant Services**: `runway/services/`

---

**Last Updated**: 2025-09-30 (Firm-first pivot)  
**Next Review**: Phase 3 implementation (Weeks 1-2)

## Firm-First Implementation Priorities

### **Phase 3 (Weeks 1-2, 40h)** 🔴 P0 CRITICAL
1. Add Firm, FirmStaff models (16h)
2. Add firm_id to Business (nullable) (4h)
3. Firm-level authentication & RBAC (12h)
4. Firm-level routes (GET /firms/{firm_id}/clients) (8h)

### **What This Enables**
- CAS firms can manage 20-100 clients
- Batch runway views across all clients
- Firm staff with role-based access (admin/staff/view-only)
- Data quality scoring per client
- $50/mo per client pricing model

### **What's Deprioritized** (Phase 7+)
- Direct owner access (business.firm_id = NULL)
- QBO App Store distribution
- Agentic positioning / Smart Policies
