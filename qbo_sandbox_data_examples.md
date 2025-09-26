# QBO Sandbox Data Service Examples

This file contains mock data examples that should be moved to the future QBO Sandbox Data Service.

## Current Mock Data in `domains/qbo/client.py`

### Small Business Data (1-10 employees, <$1M revenue)
```python
def _get_small_business_data(self) -> Dict[str, Any]:
    """Mock data for small business (1-10 employees, <$1M revenue)."""
    return {
        "bills": [
            {
                "Id": "bill_001",
                "VendorRef": {"name": "Office Depot", "value": "vendor_001"},
                "TotalAmt": 150.00,
                "Balance": 150.00,
                "DueDate": "2025-10-15",
                "TxnDate": "2025-09-15",
                "DocNumber": "BILL-001",
                "Line": [{"Id": "1", "Amount": 150.00, "DetailType": "AccountBasedExpenseLineDetail"}]
            },
            # ... more bills
        ],
        "invoices": [
            {
                "Id": "invoice_001",
                "CustomerRef": {"name": "Client A", "value": "customer_001"},
                "TotalAmt": 2500.00,
                "Balance": 2500.00,
                "DueDate": "2025-10-20",
                "TxnDate": "2025-09-20",
                "DocNumber": "INV-001",
                "Line": [{"Id": "1", "Amount": 2500.00, "DetailType": "SalesItemLineDetail"}]
            },
            # ... more invoices
        ],
        "customers": [
            {
                "Id": "customer_001",
                "Name": "Client A",
                "Active": True,
                "Email": "clienta@example.com",
                "CompanyName": "Client A Corp"
            },
            # ... more customers
        ],
        "vendors": [
            {
                "Id": "vendor_001", 
                "Name": "Office Depot",
                "Active": True,
                "Email": "billing@officedepot.com",
                "CompanyName": "Office Depot Inc."
            },
            # ... more vendors
        ],
        "accounts": [
            {
                "Id": "account_001",
                "Name": "Business Checking",
                "AccountType": "Bank",
                "AccountSubType": "Checking",
                "CurrentBalance": 15000.00
            },
            # ... more accounts
        ],
        "company_info": [
            {
                "Id": "1",
                "CompanyName": "Small Business LLC",
                "LegalName": "Small Business LLC",
                "Country": "US",
                "FiscalYearStartMonth": "1",
                "SyncToken": "1"
            }
        ]
    }
```

### Medium Business Data (11-50 employees, $1M-$10M revenue)
```python
def _get_medium_business_data(self) -> Dict[str, Any]:
    """Mock data for medium business (11-50 employees, $1M-$10M revenue)."""
    return {
        "bills": [
            {
                "Id": "bill_001",
                "VendorRef": {"name": "Office Supplies Co", "value": "vendor_001"},
                "TotalAmt": 2500.00,
                "Balance": 2500.00,
                "DueDate": "2025-10-15",
                "TxnDate": "2025-09-15",
                "DocNumber": "BILL-001",
                "Line": [{"Id": "1", "Amount": 2500.00, "DetailType": "AccountBasedExpenseLineDetail"}]
            },
            # ... more bills
        ],
        # ... similar structure for invoices, customers, vendors, accounts, company_info
    }
```

### Large Business Data (50+ employees, $10M+ revenue)
```python
def _get_large_business_data(self) -> Dict[str, Any]:
    """Mock data for large business (50+ employees, $10M+ revenue)."""
    return {
        "bills": [
            {
                "Id": "bill_001",
                "VendorRef": {"name": "Enterprise Software", "value": "vendor_001"},
                "TotalAmt": 25000.00,
                "Balance": 25000.00,
                "DueDate": "2025-10-15",
                "TxnDate": "2025-09-15",
                "DocNumber": "BILL-001",
                "Line": [{"Id": "1", "Amount": 25000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
            },
            # ... more bills
        ],
        # ... similar structure for invoices, customers, vendors, accounts, company_info
    }
```

## Mock Response Methods

### Individual Mock Response
```python
def _get_mock_response(self, endpoint: str, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Return realistic mock QBO data for testing across different business sizes."""
    business_size = self._determine_business_size()
    mock_data = self._get_realistic_mock_data(business_size)
    
    if endpoint == "query":
        if params and "Bill" in str(params.get("query", "")):
            return {"QueryResponse": {"Bill": mock_data["bills"]}}
        elif params and "Invoice" in str(params.get("query", "")):
            return {"QueryResponse": {"Invoice": mock_data["invoices"]}}
        # ... more entity types
    elif endpoint == "companyinfo/1":
        return {"QueryResponse": {"CompanyInfo": mock_data["company_info"]}}
    else:
        return {"QueryResponse": {"Bill": mock_data["bills"]}}
```

### Batch Mock Response
```python
def _get_mock_batch_response(self, batch_queries: List[Dict[str, str]]) -> Dict[str, Any]:
    """Return realistic mock batch response for testing."""
    business_size = self._determine_business_size()
    mock_data = self._get_realistic_mock_data(business_size)
    
    batch_responses = []
    for query in batch_queries:
        bId = query.get("bId", "")
        query_text = query.get("Query", "")
        
        if bId == "bills" or "Bill" in query_text:
            batch_responses.append({
                "bId": "bills",
                "QueryResponse": {"Bill": mock_data["bills"]}
            })
        # ... more entity types
    
    return {"BatchItemResponse": batch_responses}
```

## Future Sandbox Data Service Structure

This data should be moved to `infra/qbo/sandbox_data_service.py` with:

1. **Business Size Detection** - Based on actual business metrics
2. **Industry-Specific Scenarios** - Different data for different industries
3. **Realistic Data Generation** - More sophisticated than static mock data
4. **QBO Entity Coverage** - All QBO entities (bills, invoices, customers, vendors, accounts, etc.)
5. **Data Relationships** - Proper foreign key relationships between entities
6. **Temporal Data** - Historical data with proper date ranges
7. **Data Quality Variations** - Some incomplete or inconsistent data for testing

## Current Issues to Fix

1. **Remove all mock methods** from `domains/qbo/client.py`
2. **Remove mock environment checks** (`if qbo_config.environment == "mock"`)
3. **Remove mock response calls** (`return self._get_mock_response(...)`)
4. **Clean up auth service** - Fix Integration model references
