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
