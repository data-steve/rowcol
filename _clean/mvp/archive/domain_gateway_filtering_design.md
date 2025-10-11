# Domain Gateway Filtering Design

## **Analysis of Existing Patterns**

### **QBOSyncService Convenience Methods (Good Reference):**
- `get_bills_by_due_days(due_days: int = 30)` - Filter bills by due date
- `get_bills_by_date(since_date: datetime)` - Filter bills by date range  
- `get_invoices_by_aging_days(aging_days: int = 30)` - Filter invoices by aging
- `get_invoices_by_date(since_date: datetime)` - Filter invoices by date range
- `get_qbo_data_for_digest()` - Combined data for digest

### **Data Orchestrator Problems (What We Need to Fix):**
- **Indiscriminate Pulling**: Both orchestrators call `smart_sync.get_bills()` and `smart_sync.get_invoices()` with no filtering
- **Post-Processing Filtering**: All filtering happens in the experience services after getting ALL data
- **No API-Level Filtering**: QBO API calls don't use filters, everything is pulled then filtered

### **Experience Service Filtering (What We Need to Replace):**
- **TrayService**: Filters for data quality issues (missing vendor, amounts, dates)
- **ConsoleService**: Filters for decision-ready items (complete data, valid status)
- **Feature Gating**: Uses feature flags to control what data is shown

## **Proposed Domain Gateway Filtering Methods**

### **BillsGateway Extensions:**
```python
class BillsGateway(Protocol):
    # Existing methods
    def list(self, query: ListBillsQuery) -> List[Bill]: ...
    def get_by_id(self, advisor_id: str, business_id: str, bill_id: str) -> Optional[Bill]: ...
    def update_bill(self, request: UpdateBillRequest) -> bool: ...
    
    # New filtering methods (based on QBOSyncService patterns)
    def list_incomplete(self, query: ListBillsQuery) -> List[Bill]:
        """For Hygiene Tray: Only bills with missing data"""
        ...
    
    def list_decision_ready(self, query: ListBillsQuery) -> List[Bill]:
        """For Decision Console: Only bills ready for decision-making"""
        ...
    
    def list_by_due_days(self, query: ListBillsQuery, due_days: int = 30) -> List[Bill]:
        """Filter bills by due date range (replaces get_bills_by_due_days)"""
        ...
    
    def list_by_date_range(self, query: ListBillsQuery, since_date: Optional[datetime] = None) -> List[Bill]:
        """Filter bills by date range (replaces get_bills_by_date)"""
        ...
    
    # Bookkeeping methods (QBO-appropriate)
    def get_payment_history(self, bill_id: str) -> List[Dict[str, Any]]:
        """Get payment history for a bill (read-only)"""
        ...
```

### **InvoicesGateway Extensions:**
```python
class InvoicesGateway(Protocol):
    # Existing methods
    def list(self, query: ListInvoicesQuery) -> List[Invoice]: ...
    def get_by_id(self, advisor_id: str, business_id: str, invoice_id: str) -> Optional[Invoice]: ...
    def update_invoice(self, request: UpdateInvoiceRequest) -> bool: ...
    def record_payment(self, advisor_id: str, business_id: str, invoice_id: str, amount: Decimal, payment_date: date) -> str: ...
    
    # New filtering methods (based on QBOSyncService patterns)
    def list_incomplete(self, query: ListInvoicesQuery) -> List[Invoice]:
        """For Hygiene Tray: Only invoices with missing data"""
        ...
    
    def list_decision_ready(self, query: ListInvoicesQuery) -> List[Invoice]:
        """For Decision Console: Only invoices ready for decision-making"""
        ...
    
    def list_by_aging_days(self, query: ListInvoicesQuery, aging_days: int = 30) -> List[Invoice]:
        """Filter invoices by aging days (replaces get_invoices_by_aging_days)"""
        ...
    
    def list_by_date_range(self, query: ListInvoicesQuery, since_date: Optional[datetime] = None) -> List[Invoice]:
        """Filter invoices by date range (replaces get_invoices_by_date)"""
        ...
    
    # Bookkeeping methods (QBO-appropriate)
    def get_payment_history(self, invoice_id: str) -> List[Dict[str, Any]]:
        """Get payment history for an invoice (read-only)"""
        ...
```

### **BalancesGateway Extensions:**
```python
class BalancesGateway(Protocol):
    # Existing methods
    def list(self, query: ListBalancesQuery) -> List[AccountBalance]: ...
    def get_by_id(self, advisor_id: str, business_id: str, account_id: str) -> Optional[AccountBalance]: ...
    def get_total_available(self, advisor_id: str, business_id: str) -> Decimal: ...
    def get_total_current(self, advisor_id: str, business_id: str) -> Decimal: ...
    
    # New methods (based on QBOSyncService patterns)
    def get_company_info(self) -> Dict[str, Any]:
        """Get company info including balances (replaces get_company_info)"""
        ...
    
    def get_kpi_data(self) -> Dict[str, Any]:
        """Get KPI data for dashboard calculations (replaces get_kpi_data)"""
        ...
    
    def get_aging_report(self) -> Dict[str, Any]:
        """Get detailed aging report data (replaces get_aging_report)"""
        ...
```

### **Convenience Methods (Digest Support):**
```python
# In wiring.py or a separate service
def get_qbo_data_for_digest(advisor_id: str, business_id: str) -> Dict[str, Any]:
    """Get all QBO data needed for digest calculations (replaces get_qbo_data_for_digest)"""
    bills_gateway = create_bills_gateway(advisor_id, business_id)
    invoices_gateway = create_invoices_gateway(advisor_id, business_id)
    balances_gateway = create_balances_gateway(advisor_id, business_id)
    
    bills_data = bills_gateway.list_by_due_days(ListBillsQuery(advisor_id, business_id), due_days=30)
    invoices_data = invoices_gateway.list_by_aging_days(ListInvoicesQuery(advisor_id, business_id), aging_days=30)
    company_info = balances_gateway.get_company_info()
    
    return {
        "bills": bills_data,
        "invoices": invoices_data,
        "company_info": company_info
    }
```

## **Methods to Remove (QBO Execution Assumptions):**

### **❌ Remove These (QBO Can't Execute):**
- `create_payment_immediate()` - QBO can't execute payments
- `record_payment()` - QBO can't execute payments
- Any payment execution methods

### **✅ Keep These (QBO Bookkeeping Tasks):**
- `sync_payment_record()` - Read-only sync, no execution
- `get_payment_history()` - Historical data
- `get_aging_report()` - Reports and analytics
- `get_kpi_data()` - Dashboard calculations
- `get_status()` - Status checking
- `health_check()` - API health

## **Completeness Criteria**

### **Incomplete (Hygiene Tray):**
- Missing `vendor_id` or `vendor_name` (for bills)
- Missing `customer_id` or `customer_name` (for invoices)
- Missing `due_date`
- `amount` is zero or negative
- Missing `last_synced_at` (sync issues)
- `status` is unclear or invalid
- Missing required QBO fields

### **Decision-Ready (Decision Console):**
- Has `vendor_id` and `vendor_name` (for bills)
- Has `customer_id` and `customer_name` (for invoices)
- Has valid `due_date`
- Has positive `amount`
- Has recent `last_synced_at` (within 24 hours)
- `status` is `OPEN` or `SCHEDULED`
- All required QBO fields present

## **Implementation Strategy (ADR-Compliant)**

### **1. Extend Domain Gateway Interfaces (ADR-001 Compliant)**
- Add filtering methods to domain gateway protocols in `domains/*/gateways.py`
- Keep existing `list()` method for backward compatibility
- Add query parameters for filtering options
- **Key**: Domain gateways are rail-agnostic interfaces only

### **2. Implement in Infra Gateways (ADR-005 Compliant)**
- Add filtering logic to `QBOBillsGateway` and `QBOInvoicesGateway` in `infra/gateways/`
- **Use Sync Orchestrator** for all data access (Smart Sync Pattern)
- **Transaction Log Integration** - Log all data changes automatically
- **State Mirror Integration** - Use mirror for fast reads, sync from QBO API
- **Smart Switching Logic** - DB freshness checks → API fallback → Log INBOUND → Mirror upsert

### **3. Sync Orchestrator Integration (Smart Sync Pattern)**
```python
# infra/gateways/qbo/bills_gateway.py
class QBOBillsGateway(BillsGateway):
    def list_incomplete(self, query: ListBillsQuery) -> List[Bill]:
        return self.sync_orchestrator.read_refresh(
            entity="bills",
            client_id=query.advisor_id,
            hint=query.freshness_hint,
            mirror_is_fresh=lambda e, c, p: self.mirror_repo.is_fresh(query.advisor_id, query.business_id, p),
            fetch_remote=lambda: self.qbo_client.list_bills_incomplete(query.business_id),
            upsert_mirror=lambda raw, ver, ts: self.mirror_repo.upsert_many(query.advisor_id, query.business_id, raw, ver, ts),
            read_from_mirror=lambda: self.mirror_repo.list_incomplete(query.advisor_id, query.business_id),
            on_hygiene=lambda c, code: self.log_repo.flag_hygiene(c, code)
        )
```

### **4. Update Query Models**
- Extend `ListBillsQuery` and `ListInvoicesQuery` with filtering options
- Add completeness filter parameter
- Add date range parameters
- **Key**: Query models are domain models, not infra models

### **5. Replace Data Orchestrators (ADR-001 Compliant)**
- Update experience services to use domain gateways directly
- Remove data orchestrator dependencies
- Use composition root for dependency injection
- **Key**: Runway services → Domain gateways → Infra gateways → Sync orchestrator

## **Query Model Extensions**

### **ListBillsQuery Extensions:**
```python
class ListBillsQuery(BaseModel):
    advisor_id: str
    business_id: str
    status: str = "OPEN"
    freshness_hint: FreshnessHint = "CACHED_OK"
    
    # New filtering options
    completeness_filter: Optional[str] = None  # "incomplete", "decision_ready", "all"
    due_days: Optional[int] = None  # Filter by due date range
    since_date: Optional[datetime] = None  # Filter by date range
    vendor_id: Optional[str] = None  # Filter by specific vendor
```

### **ListInvoicesQuery Extensions:**
```python
class ListInvoicesQuery(BaseModel):
    advisor_id: str
    business_id: str
    status: str = "OPEN"
    freshness_hint: FreshnessHint = "CACHED_OK"
    
    # New filtering options
    completeness_filter: Optional[str] = None  # "incomplete", "decision_ready", "all"
    aging_days: Optional[int] = None  # Filter by aging days
    since_date: Optional[datetime] = None  # Filter by date range
    customer_id: Optional[str] = None  # Filter by specific customer
```

## **Architectural Compliance (ADR Alignment)**

### **ADR-005 QBO API Strategy Compliance:**
✅ **Sync Orchestrator Integration** - All data access goes through sync orchestrator  
✅ **Smart Sync Pattern** - DB freshness checks → API fallback → Log INBOUND → Mirror upsert  
✅ **Transaction Log Integration** - All data changes logged automatically  
✅ **State Mirror Integration** - Fast reads from mirror, sync from QBO API  
✅ **QBO Fragility Handling** - Rate limiting, retry logic, circuit breaker patterns  

### **ADR-001 Domains/Runway Separation Compliance:**
✅ **Three-Layer Architecture** - `runway/ → domains/ → infra/` (no back edges)  
✅ **Domain Gateways** - Rail-agnostic interfaces in `domains/*/gateways.py`  
✅ **Infra Gateways** - Rail-specific implementations in `infra/gateways/`  
✅ **Composition Root** - Single place for dependency injection in `runway/wiring.py`  
✅ **Import Rules** - No forbidden imports, no circular dependencies  

### **Smart Sync Pattern Lessons Learned:**
✅ **Fix Missing Connections** - Domain services → Sync Orchestrator (not direct DB queries)  
✅ **Implement Smart Switching** - DB freshness checks and API fallback  
✅ **Integrate Transaction Logs** - Log every data change automatically  
✅ **Fix Data Orchestrators** - Make them call domain gateways, not sync service directly  

## **Backward Compatibility**

### **Existing `list()` Method:**
- Keep existing `list()` method unchanged
- Add `completeness_filter="all"` as default behavior
- Existing code continues to work
- **Key**: Maintains ADR-001 compliance while adding new functionality

### **Migration Path (ADR-Compliant):**
1. **Phase 1**: Add filtering methods alongside existing methods (ADR-001 compliant)
2. **Phase 2**: Update experience services to use filtering methods (ADR-001 compliant)
3. **Phase 3**: Deprecate data orchestrators (ADR-001 compliant)
4. **Phase 4**: Remove data orchestrators (ADR-001 compliant)

## **Performance Considerations (Smart Sync Pattern)**

### **Smart Switching Strategy:**
- **Fresh Data**: Return from State Mirror (fast)
- **Stale Data**: Call QBO API, update State Mirror, return fresh data
- **Error Handling**: Log failure + hygiene flag + return stale mirror
- **Cache Strategy**: Use Sync Orchestrator's built-in caching

### **QBO API Optimization:**
- Use QBO API filters where possible (due_date, status)
- Implement pagination for large result sets
- Batch multiple queries when possible
- **Key**: All optimization happens in infra gateways, not domain gateways

### **Transaction Log Integration:**
- Log all INBOUND data changes automatically
- Log all OUTBOUND operations for audit trail
- Implement replayability for failed operations
- **Key**: Transaction logs integrated with sync orchestrator, not separate
