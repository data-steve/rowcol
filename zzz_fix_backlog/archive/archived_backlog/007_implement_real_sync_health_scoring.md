# Implement Real Sync Health Scoring

**Status:** Needs Solving  
**Priority:** P1 High  
**Effort:** 8h  
**Type:** Data Quality & Monitoring  

## Problem Statement

The `_calculate_sync_health_score()` function in `runway/routes/kpis.py` currently returns a hardcoded mock value of `92.0`, violating our "no more mocks" commitment. This function should calculate real sync health based on actual QBO sync frequency and success rates.

## Current State

```python
def _calculate_sync_health_score(smart_sync) -> float:
    """Calculate QBO sync health score."""
    # TODO: Implement sync health scoring based on sync frequency and success rates
    return 92.0  # Mock score - VIOLATES NO MOCKS COMMITMENT
```

## Required Implementation

### 1. Sync Health Metrics Collection (4h)
- **Track sync frequency**: How often QBO syncs are attempted vs. expected frequency
- **Track success rates**: Percentage of successful vs. failed sync operations
- **Track sync latency**: Time taken for sync operations to complete
- **Track error patterns**: Types and frequency of sync errors

### 2. Health Score Algorithm (3h)
- **Frequency Score**: 0-100 based on sync frequency vs. expected (e.g., daily, hourly)
- **Success Rate Score**: 0-100 based on successful syncs over time window
- **Latency Score**: 0-100 based on sync operation speed
- **Error Pattern Score**: 0-100 based on error frequency and types
- **Composite Score**: Weighted average of all metrics

### 3. SmartSyncService Integration (1h)
- **Add health tracking methods** to `SmartSyncService`:
  - `record_sync_attempt(platform, success, duration, error_type=None)`
  - `get_sync_health_metrics(platform, time_window_days=30)`
  - `calculate_sync_health_score(platform)`

## Implementation Details

### Health Score Calculation
```python
def calculate_sync_health_score(self, platform: str, time_window_days: int = 30) -> float:
    """Calculate comprehensive sync health score."""
    metrics = self.get_sync_health_metrics(platform, time_window_days)
    
    # Frequency score (40% weight)
    expected_frequency = self.get_expected_sync_frequency(platform)
    actual_frequency = metrics['sync_attempts'] / time_window_days
    frequency_score = min(100, (actual_frequency / expected_frequency) * 100)
    
    # Success rate score (30% weight)
    success_rate = metrics['successful_syncs'] / metrics['total_syncs']
    success_score = success_rate * 100
    
    # Latency score (20% weight)
    avg_latency = metrics['avg_latency_seconds']
    max_acceptable_latency = 30  # seconds
    latency_score = max(0, 100 - (avg_latency / max_acceptable_latency) * 100)
    
    # Error pattern score (10% weight)
    error_rate = metrics['error_count'] / metrics['total_syncs']
    error_score = max(0, 100 - (error_rate * 100))
    
    # Weighted composite score
    health_score = (
        frequency_score * 0.4 +
        success_score * 0.3 +
        latency_score * 0.2 +
        error_score * 0.1
    )
    
    return round(health_score, 1)
```

### Health Metrics Storage
- **Database table**: `sync_health_metrics` with columns:
  - `id`, `business_id`, `platform`, `sync_attempted_at`
  - `success`, `duration_seconds`, `error_type`, `error_message`
- **Retention policy**: Keep metrics for 90 days, aggregate older data

## Dependencies

- **SmartSyncService**: Must have health tracking methods implemented
- **Database**: Need sync_health_metrics table created
- **QBOHealthMonitor**: Should integrate with existing health monitoring

## Success Criteria

- ✅ No more hardcoded mock values in sync health scoring
- ✅ Real-time sync health calculation based on actual metrics
- ✅ Health score reflects actual QBO sync performance
- ✅ Integration with existing QBOHealthMonitor infrastructure
- ✅ Health score updates in real-time as syncs occur

## Related Tasks

- **Phase 3 Data Quality Enhancement**: This task should be included in the comprehensive data quality improvement session
- **QBOHealthMonitor Integration**: Ensure sync health scoring integrates with existing health monitoring
- **No More Mocks Commitment**: This addresses one of the remaining mock violations

## Notes

This task is critical for maintaining our "no more mocks" commitment and providing real value to users. The sync health score should be a key indicator of system reliability and QBO integration health.
