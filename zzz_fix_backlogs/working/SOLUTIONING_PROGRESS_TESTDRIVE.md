# Solutioning Progress - TestDrive Data Orchestrator

*Status: 🔍 ANALYSIS PHASE*

## **Problem Statement**

TestDrive needs a data orchestrator following the ADR-006 pattern, but with specific requirements for PLG (Product-Led Growth) experience.

## **TestDrive Requirements Analysis**

### **What TestDrive Does**
- **Purpose**: PLG sales experience showing what Digest reveals as their need for Oodaloo
- **Data Scope**: 4 weeks of historical data (not current data)
- **Experience**: One-time analysis to demonstrate value

### **Key Questions to Resolve**

1. **Data Scope**: What specific entities does TestDrive need for 4 weeks?
   - Bills? Invoices? Balances? All of them?
   - What constitutes "4 weeks" - last 4 weeks from today?

2. **Time Window Filtering**: How to filter data to last 4 weeks?
   - Filter by transaction date?
   - Filter by due date?
   - Filter by creation date?

3. **Data Format**: What format does TestDrive need for PLG experience?
   - Same as Digest but filtered?
   - Specific format for demo purposes?
   - Mock data for demo scenarios?

4. **Historical Data**: How to get historical data?
   - QBO API supports historical queries?
   - Use current data as proxy?
   - Simulate historical state?

## **Discovery Commands to Run**

```bash
# Check current TestDrive implementation
grep -r "test_drive" runway/experiences/
grep -r "TestDrive" runway/
grep -r "4 weeks" runway/experiences/test_drive.py
grep -r "historical" runway/experiences/test_drive.py

# Check what data TestDrive currently uses
grep -r "get_.*_data" runway/experiences/test_drive.py
grep -r "qbo_data" runway/experiences/test_drive.py
grep -r "mock" runway/experiences/test_drive.py
```

## **Files to Read First**

- `runway/experiences/test_drive.py` - Current implementation
- `sandbox/qbo_sandbox_data_examples.md` - Test data examples
- `sandbox/scenario_runner.py` - Test scenarios

## **Proposed Solution Pattern**

```python
class TestDriveDataOrchestrator:
    async def get_test_drive_data(self, business_id: str) -> Dict[str, Any]:
        # Pull 4 weeks of historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=4)
        
        bills = await self.ap_service.get_bills_for_period(business_id, start_date, end_date)
        invoices = await self.ar_service.get_invoices_for_period(business_id, start_date, end_date)
        balances = await self.bank_service.get_balances_for_period(business_id, start_date, end_date)
        
        return {
            "bills": bills,
            "invoices": invoices,
            "balances": balances,
            "period": {"start": start_date, "end": end_date},
            "demo_mode": True  # Flag for PLG experience
        }
```

## **Discovery Results**

### **What Actually Exists:**
- **TestDrive Service**: `runway/experiences/test_drive.py` - Centralized service for test drive functionality
- **4-Week Analysis**: Uses "Past 4 weeks" for historical analysis
- **Data Sources**: Uses `RunwayCalculator` and `DataQualityAnalyzer` for analysis
- **Mock Data**: Has `generate_qbo_sandbox_test_drive()` for demo purposes
- **Current Pattern**: Directly calls `RunwayCalculator.calculate_current_runway()`

### **What the Task Assumed:**
- TestDrive needs a data orchestrator following ADR-006 pattern
- TestDrive needs 4 weeks of historical data
- TestDrive needs specific data format for PLG experience

### **Assumptions That Were Wrong:**
- TestDrive already exists and works with current data, not historical
- TestDrive uses `RunwayCalculator` directly, not broken methods
- TestDrive has both real data and sandbox data capabilities

### **Architecture Mismatches:**
- TestDrive calls `RunwayCalculator.calculate_current_runway()` which has broken methods
- TestDrive doesn't follow ADR-006 data orchestrator pattern
- TestDrive mixes real data and demo data in same service

### **Task Scope Issues:**
- TestDrive needs orchestrator for data pulling, not just calculation
- TestDrive needs to handle both real business data and demo data
- TestDrive needs to work with historical data for 4-week analysis

## **Proposed Solution**

### **TestDriveDataOrchestrator Pattern:**
```python
class TestDriveDataOrchestrator:
    async def get_test_drive_data(self, business_id: str = None, use_sandbox: bool = False) -> Dict[str, Any]:
        if use_sandbox or business_id is None:
            # Use sandbox data for demos
            return await self._get_sandbox_data()
        else:
            # Use real business data for 4-week analysis
            return await self._get_historical_data(business_id)
    
    async def _get_historical_data(self, business_id: str) -> Dict[str, Any]:
        # Pull 4 weeks of historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=4)
        
        bills = await self.ap_service.get_bills_for_period(business_id, start_date, end_date)
        invoices = await self.ar_service.get_invoices_for_period(business_id, start_date, end_date)
        balances = await self.bank_service.get_balances_for_period(business_id, start_date, end_date)
        
        return {
            "bills": bills,
            "invoices": invoices,
            "balances": balances,
            "period": {"start": start_date, "end": end_date},
            "demo_mode": False
        }
    
    async def _get_sandbox_data(self) -> Dict[str, Any]:
        # Use existing sandbox data generation
        return await self._generate_sandbox_data()
```

## **Status: ✅ SOLUTION COMPLETE**

TestDrive solution is ready for execution. The orchestrator will handle both real historical data and sandbox demo data, following the ADR-006 pattern.
