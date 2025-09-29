# Solutioning Progress - Digest Data Orchestrator

*Status: 🔍 ANALYSIS PHASE*

## **Problem Statement**

Digest needs a data orchestrator following the ADR-006 pattern, but with specific requirements for bulk processing across multiple businesses.

## **Digest Requirements Analysis**

### **What Digest Does**
- **Purpose**: Weekly email analysis for all businesses
- **Data Scope**: All data (bills, invoices, balances) for each business
- **Processing**: Bulk operations across multiple businesses
- **Timing**: Friday morning jobs (async batch processing)

### **Key Questions to Resolve**

1. **Bulk Processing Architecture**: How to orchestrate data pulling for multiple businesses?
   - Process businesses sequentially or in parallel?
   - How to handle failures for individual businesses?
   - What's the relationship to existing `digest_jobs.py`?

2. **Data Aggregation**: How to efficiently pull data for all businesses?
   - Use existing `digest_jobs.py` patterns?
   - Create new bulk orchestration service?
   - How to coordinate with `infra/scheduler/`?

3. **Error Handling**: How to handle QBO failures during bulk processing?
   - Skip failed businesses and continue?
   - Retry failed businesses?
   - How to report failures?

4. **Performance**: How to optimize bulk data pulling?
   - Rate limiting for QBO API?
   - Caching strategies?
   - Parallel processing limits?

## **Discovery Commands to Run**

```bash
# Check current Digest implementation
grep -r "digest" runway/experiences/
grep -r "DigestService" runway/
grep -r "bulk" runway/experiences/digest.py

# Check existing bulk processing
grep -r "digest_jobs" infra/scheduler/
grep -r "bulk" infra/
grep -r "send_all_digests" infra/

# Check QBO bulk operations
grep -r "QBOBulkScheduledService" domains/
grep -r "bulk" domains/qbo/
```

## **Files to Read First**

- `runway/experiences/digest.py` - Current implementation
- `infra/scheduler/digest_jobs.py` - Existing bulk processing
- `infra/jobs/` - Job processing infrastructure
- `domains/qbo/` - QBO bulk operations

## **Proposed Solution Pattern**

```python
class DigestDataOrchestrator:
    async def get_digest_data(self, business_id: str) -> Dict[str, Any]:
        # Pull all data for single business
        bills = await self.ap_service.get_bills_for_digest(business_id)
        invoices = await self.ar_service.get_invoices_for_digest(business_id)
        balances = await self.bank_service.get_balances_for_digest(business_id)
        
        return {
            "bills": bills,
            "invoices": invoices,
            "balances": balances,
            "business_id": business_id,
            "synced_at": datetime.utcnow().isoformat()
        }
    
    async def process_bulk_digest(self, business_ids: List[str]) -> Dict[str, Any]:
        # Process multiple businesses
        results = {"successful": 0, "failed": 0, "errors": []}
        
        for business_id in business_ids:
            try:
                data = await self.get_digest_data(business_id)
                # Process digest for this business
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"business_id": business_id, "error": str(e)})
        
        return results
```

## **Discovery Results**

### **What Actually Exists:**
- **Digest Service**: `runway/experiences/digest.py` - Simple service using `RunwayCalculator`
- **Bulk Processing**: `infra/scheduler/digest_jobs.py` - Job scheduler for weekly digests
- **Current Pattern**: `DigestService.send_digest_to_all_businesses()` - Sequential processing
- **Job Runner**: Uses `JobRunner` for scheduling and execution
- **Email Service**: Commented out but referenced for email delivery

### **What the Task Assumed:**
- Digest needs a data orchestrator following ADR-006 pattern
- Digest needs bulk processing across multiple businesses
- Digest needs coordination with existing job infrastructure

### **Assumptions That Were Wrong:**
- Digest already has bulk processing via `send_digest_to_all_businesses()`
- Digest uses `RunwayCalculator` directly, not broken methods
- Digest has job scheduling infrastructure already

### **Architecture Mismatches:**
- Digest calls `RunwayCalculator.calculate_current_runway()` which has broken methods
- Digest doesn't follow ADR-006 data orchestrator pattern
- Digest mixes data calculation and email sending in same service

### **Task Scope Issues:**
- Digest needs orchestrator for data pulling, not just calculation
- Digest needs to work with existing job scheduler
- Digest needs to handle both single business and bulk processing

## **Proposed Solution**

### **DigestDataOrchestrator Pattern:**
```python
class DigestDataOrchestrator:
    async def get_digest_data(self, business_id: str) -> Dict[str, Any]:
        # Pull all data for single business
        bills = await self.ap_service.get_bills_for_digest(business_id)
        invoices = await self.ar_service.get_invoices_for_digest(business_id)
        balances = await self.bank_service.get_balances_for_digest(business_id)
        
        return {
            "bills": bills,
            "invoices": invoices,
            "balances": balances,
            "business_id": business_id,
            "synced_at": datetime.utcnow().isoformat()
        }
    
    async def process_bulk_digest(self, business_ids: List[str]) -> Dict[str, Any]:
        # Process multiple businesses using existing job infrastructure
        results = {"successful": 0, "failed": 0, "errors": []}
        
        for business_id in business_ids:
            try:
                data = await self.get_digest_data(business_id)
                # Process digest for this business
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"business_id": business_id, "error": str(e)})
        
        return results
```

### **Integration with Existing Infrastructure:**
- **Job Scheduler**: Use existing `DigestJobScheduler` for scheduling
- **Bulk Processing**: Use existing `send_digest_to_all_businesses()` pattern
- **Error Handling**: Use existing job retry and error handling
- **Email Service**: Integrate with existing email service when available

## **Status: ✅ SOLUTION COMPLETE**

Digest solution is ready for execution. The orchestrator will handle both single business and bulk processing, integrating with existing job infrastructure.
