# Eliminate Remaining Mock Violations

**Status:** Needs Solving  
**Priority:** P0 Critical  
**Effort:** 12h  
**Type:** Data Quality & No Mocks Commitment  

## Problem Statement

We have committed to "no more mocks" but still have multiple hardcoded mock values in `runway/routes/kpis.py` that violate this commitment. These functions return fake data instead of implementing real calculations based on actual QBO data.

## Current Mock Violations

### 1. Data Quality Scoring
```python
def _calculate_data_quality_score(qbo_data: Dict) -> float:
    return 85.0  # Mock score - VIOLATION
```

### 2. Sync Health Scoring  
```python
def _calculate_sync_health_score(smart_sync) -> float:
    return 92.0  # Mock score - VIOLATION
```

### 3. Runway Trend Analysis
```python
def _calculate_runway_trend(runway_calc: Dict) -> str:
    return "stable"  # Mock trend - VIOLATION
```

### 4. Payment Cycle Analysis
```python
def _calculate_avg_payment_cycle(bills_data: List[Dict]) -> float:
    return 25.5  # Mock average - VIOLATION
```

### 5. Collection Cycle Analysis
```python
def _calculate_avg_collection_cycle(invoices_data: List[Dict]) -> float:
    return 32.1  # Mock average - VIOLATION
```

### 6. Collection Efficiency
```python
def _calculate_collection_efficiency(invoices_data: List[Dict]) -> float:
    return 78.5  # Mock efficiency score - VIOLATION
```

### 7. QBO Integration Test Mocks
```python
# In tests/integration/qbo/test_qbo_integration.py
mock_provider.get_all_data_batch.return_value = {
    "bills": [],
    "invoices": [], 
    "customers": [],
    "vendors": [],
    "accounts": [],
    "company_info": {}
}  # Mock data - VIOLATION
```

### 8. Test Drive Mock Data
```python
# In runway/experiences/test_drive.py
qbo_data = {
    "bills": [],
    "invoices": [],
    "customers": [],
    "vendors": []
}  # Mock data - VIOLATION
```

### 9. Scenario Runner Mock Data
```python
# In sandbox/scenario_runner.py
qbo_data = {
    "bills": [],
    "invoices": [],
    "customers": [],
    "vendors": []
}  # Mock data - VIOLATION
```

### 10. Test Drive Mock Data
```python
# In runway/experiences/test_drive.py
qbo_data = {
    "bills": [],
    "invoices": [],
    "customers": [],
    "vendors": []
}  # Mock data - VIOLATION
```

### 11. Sandbox Data Creation Mock Tokens
```python
# In sandbox/create_sandbox_data.py
business.qbo_access_token = "mock_access_token"  # Mock token - VIOLATION
business.qbo_refresh_token = "mock_refresh_token"  # Mock token - VIOLATION
```

### 12. Test Fixture Mock Data
```python
# In tests/conftest.py
test_business.qbo_access_token = "mock_qbo_token"  # Mock token - VIOLATION
test_business.qbo_refresh_token = "mock_qbo_refresh"  # Mock token - VIOLATION
```

### 13. Test Drive Mock Integration
```python
# In tests/runway/unit/test_drive/test_test_drive.py
mock_business.qbo_realm_id = "realm-123"  # Mock realm - VIOLATION
mock_business.qbo_status = "connected"  # Mock status - VIOLATION
```

### 14. Integration Test Mock Data
```python
# In tests/integration/test_qbo_integration.py
mock_provider.get_all_data_batch.return_value = {
    "bills": [],
    "invoices": [],
    "customers": [],
    "vendors": [],
    "accounts": [],
    "company_info": {}
}  # Mock data - VIOLATION
```

## Required Implementation

### Phase 1: Immediate Fix (2h)
- ✅ **Replace all mock returns with NotImplementedError** - COMPLETED
- ✅ **Add descriptive error messages** pointing to backlog tasks - COMPLETED
- ✅ **Document each violation** with specific implementation requirements - COMPLETED

### Phase 2: Real Implementation (10h)

#### 2.1 Data Quality Scoring (2h)
- **Analyze QBO data completeness**: Required fields present vs missing
- **Validate data accuracy**: Check for obvious data quality issues
- **Calculate quality percentage**: Based on completeness and accuracy metrics
- **Integration**: Use existing `QBODataService` for data analysis

#### 2.2 Sync Health Scoring (2h)
- **Track sync metrics**: Frequency, success rate, latency, error patterns
- **Calculate health score**: Weighted composite of all metrics
- **Integration**: Extend `SmartSyncService` with health tracking
- **Storage**: Store metrics in database for historical analysis

#### 2.3 Runway Trend Analysis (2h)
- **Historical runway data**: Store runway calculations over time
- **Trend calculation**: Compare current vs previous periods
- **Trend classification**: Improving, declining, stable, volatile
- **Integration**: Use existing `RunwayCalculator` historical data

#### 2.4 Payment Cycle Analysis (2h)
- **Bill analysis**: Calculate days between bill date and payment date
- **Statistical analysis**: Mean, median, standard deviation
- **Outlier detection**: Identify unusual payment patterns
- **Integration**: Use `PaymentService` for payment history

#### 2.5 Collection Cycle Analysis (2h)
- **Invoice analysis**: Calculate days between invoice date and payment received
- **Customer patterns**: Analyze per-customer collection timing
- **Seasonal analysis**: Account for business seasonality
- **Integration**: Use `CollectionsService` for collection data

#### 2.6 Collection Efficiency Analysis (2h)
- **Success rate calculation**: Percentage of invoices collected vs written off
- **Timing efficiency**: How quickly collections are completed
- **Customer segmentation**: Efficiency by customer type/size
- **Integration**: Use `CollectionsService` and `CustomerService`

#### 2.7 Test Data Mock Violations (2h)
- **Test Drive Mock Data**: Replace mock QBO data in `runway/experiences/test_drive.py`
- **Scenario Runner Mock Data**: Replace mock QBO data in `sandbox/scenario_runner.py`
- **Integration Test Mocks**: Replace mock data in `tests/integration/qbo/test_qbo_integration.py`
- **Implementation**: Use real domain service calls instead of hardcoded mock data
- **Integration**: Connect to actual `SmartSyncService` methods for test data

#### 2.8 Comprehensive Test Data Service Solution (8h)
- **Problem**: All test files use hardcoded mock data instead of real QBO sandbox data
- **Root Cause**: No centralized test data service for QBO sandbox integration
- **Solution**: Create `infra/qbo/test_data_service.py` with:
  - Real QBO sandbox connection using `infra/qbo/config.py` credentials
  - Proper test data fixtures that use actual QBO API calls
  - Test data caching and cleanup mechanisms
  - Integration with `SmartSyncService` for consistent data access
- **Files to Update**:
  - `tests/conftest.py` - Replace mock fixtures with real QBO fixtures
  - `sandbox/create_sandbox_data.py` - Use real QBO credentials from config
  - `runway/experiences/test_drive.py` - Use test data service
  - `sandbox/scenario_runner.py` - Use test data service
  - All integration test files - Use real QBO sandbox data
- **Dependencies**: QBO sandbox credentials must be available in environment
- **Verification**: All tests pass with real QBO sandbox data, no mock violations remain

## Implementation Strategy

### Database Schema Updates
```sql
-- Sync health metrics
CREATE TABLE sync_health_metrics (
    id SERIAL PRIMARY KEY,
    business_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    sync_attempted_at TIMESTAMP NOT NULL,
    success BOOLEAN NOT NULL,
    duration_seconds FLOAT,
    error_type VARCHAR(100),
    error_message TEXT
);

-- Historical runway data
CREATE TABLE runway_history (
    id SERIAL PRIMARY KEY,
    business_id VARCHAR(255) NOT NULL,
    calculated_at TIMESTAMP NOT NULL,
    runway_days FLOAT NOT NULL,
    cash_balance DECIMAL(15,2) NOT NULL,
    ar_balance DECIMAL(15,2) NOT NULL,
    ap_balance DECIMAL(15,2) NOT NULL
);
```

### Service Extensions
- **SmartSyncService**: Add health tracking methods
- **RunwayCalculator**: Add historical data storage
- **PaymentService**: Add cycle analysis methods
- **CollectionsService**: Add efficiency analysis methods

## Dependencies

- **Phase 3 Data Quality Enhancement**: This should be included in the comprehensive data quality session
- **QBOHealthMonitor**: Integration with existing health monitoring
- **Database migrations**: New tables for metrics storage
- **Historical data**: Need to start collecting historical metrics

## Success Criteria

- ✅ **Zero mock values** in KPI calculations
- ✅ **Real data analysis** based on actual QBO data
- ✅ **Meaningful metrics** that provide business value
- ✅ **Performance**: All calculations complete in <2 seconds
- ✅ **Accuracy**: Metrics reflect actual business performance
- ✅ **Integration**: Seamless integration with existing services

## Related Tasks

- **007_implement_real_sync_health_scoring.md**: Specific sync health implementation
- **Phase 3 Data Quality Enhancement**: Comprehensive data quality improvement
- **No More Mocks Commitment**: Core architectural principle

## Notes

This task is **P0 Critical** because it directly violates our "no more mocks" commitment. These mock values provide no real value to users and undermine the credibility of our analytics. All KPI calculations must be based on real data analysis.

The implementation should prioritize the most valuable metrics first (data quality, sync health) and then move to operational metrics (payment cycles, collection efficiency).
