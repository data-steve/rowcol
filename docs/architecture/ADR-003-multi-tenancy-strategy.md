# ADR-003: Multi-Tenancy Strategy

**Date**: 2025-09-17  
**Status**: Accepted  
**Deciders**: Steve Simpson, Claude (AI Assistant)  
**Technical Story**: Phase 0 Data Architecture Foundation  

## Context

Oodaloo needs to support multiple business customers with complete data isolation, while maintaining performance and development simplicity. The system must handle:

1. **Single-tenant businesses** using Runway directly (Phase 0-1)
2. **Multi-tenant CAS firms** managing multiple clients via RowCol (Phase 2+)
3. **Data isolation** ensuring businesses never see each other's data
4. **Performance** at scale with thousands of businesses
5. **Development simplicity** without over-engineering early phases

## Decision

We will implement a **Single-Database Multi-Tenancy** strategy using `business_id` as the primary tenant identifier, with a migration path to **Database-per-Tenant** for enterprise CAS firms.

### **Primary Tenancy Model**

**Business-Centric Tenancy**:
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

### **Tenant Hierarchy**

```
Business (Primary Tenant)
├── Users (business owners, staff)
├── QBO Integration (one per business)
├── Bank Accounts (from QBO)
├── Transactions (from QBO)
├── Runway Reserves (Oodaloo-specific)
├── Tray Items (Oodaloo-specific)
└── Digest Settings (Oodaloo-specific)

Future: CAS Firm (Secondary Tenant)
├── Multiple Businesses (sub-tenants)
├── Firm-level Users (accountants, admins)
├── Firm-level Reporting (across businesses)
└── RBAC (role-based access control)
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

### **Phase 2+: CAS Firm Multi-Tenancy**

**Future Implementation**:
- CAS firms manage multiple business sub-tenants
- Firm-level users with RBAC permissions
- Cross-business reporting and analytics
- Hierarchical data access patterns

```python
# Future: Hierarchical tenant model
class CASFirm(Base):
    firm_id = Column(String(36), primary_key=True)
    name = Column(String(255))
    subscription_tier = Column(String(50))

class Business(Base):
    business_id = Column(String(36), primary_key=True)
    firm_id = Column(String(36), ForeignKey("cas_firms.firm_id"), nullable=True)
    # Null firm_id = direct Runway customer
    # Non-null firm_id = RowCol sub-tenant
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

**Last Updated**: 2025-09-17  
**Next Review**: Phase 2 planning (RowCol multi-tenancy implementation)
