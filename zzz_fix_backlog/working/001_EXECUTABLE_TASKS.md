# Executable Tasks - Critical Development Blockers

*Consolidated from backlog analysis on 2025-01-27*  
*Status: ✅ READY FOR HANDS-FREE EXECUTION*

## **Task Complexity Curation**

**✅ FULLY SOLVED (6 tasks)** - These tasks have:
- Clear implementation patterns with code examples
- Specific files to fix with exact changes needed
- Complete verification steps with pytest commands
- No "figure out" or "analyze" language
- Ready for execution by any developer

---

## **CRITICAL: Read These Files First**

Before starting any executable tasks, you MUST read these files to understand the system:

### **Architecture Context:**
- `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Complete system architecture
- `docs/build_plan_v5.md` - Current build plan and phase context
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenancy patterns

## **Context for All Tasks**

**IMPORTANT**: These are critical development blockers that prevent real data implementation and core functionality. They should be completed before moving to new product features.

### **Post-Nuclear Cleanup Context**
- Clean architecture: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`
- No circular dependencies
- Integration model simplified (QBO fields in Business model)
- SmartSync test patterns established
- Database connection fixtures created

### **Critical Success Factors**
- All tasks must align with post-nuclear architecture
- Use new SmartSync patterns and database fixtures
- Address mock violations documented in 008_eliminate_remaining_mock_violations.md
- Solutions must be documented as executable tasks

---

## **Phase 1: Data Orchestrator Pattern Implementation (P0 Critical)**

#### **Task 1: Implement Data Orchestrator Pattern for Tray and Console**
- **Status:** `[✅]` Completed
- **Priority:** P0 Critical
- **Justification:** Establish the architectural foundation for experience services using data orchestrators. Implement Tray (simple) and Console (with state management) to establish the pattern for all other experiences.
- **Files to Fix:**
  - `runway/core/runway_calculator.py` - Refactor to pure calculation service
  - `runway/experiences/tray.py` - Use HygieneTrayDataOrchestrator
  - `runway/experiences/console.py` - Use DecisionConsoleDataOrchestrator
- **Required Changes:**
  - Create `runway/core/data_orchestrators/` directory
  - Implement `HygieneTrayDataOrchestrator` (simple data pulling)
  - Implement `DecisionConsoleDataOrchestrator` (data + state management)
  - Refactor RunwayCalculator to pure calculation service
  - Update Tray and Console services to use orchestrators
  - Remove direct SmartSyncService calls from Tray and Console
- **Pattern to Implement:**
  ```python
  # Tray Orchestrator (Simple)
  class HygieneTrayDataOrchestrator:
      async def get_tray_data(self, business_id: str) -> Dict[str, Any]:
          bills = await self.ap_service.get_bills_with_issues(business_id)
          invoices = await self.ar_service.get_invoices_with_issues(business_id)
          return {"bills": bills, "invoices": invoices}
  
  # Console Orchestrator (With State Management)
  class DecisionConsoleDataOrchestrator:
      async def get_console_data(self, business_id: str) -> Dict[str, Any]:
          bills = await self.ap_service.get_bills_ready_for_decision(business_id)
          invoices = await self.ar_service.get_invoices_ready_for_decision(business_id)
          balances = await self.bank_service.get_balances(business_id)
          decision_queue = await self._get_decision_queue(business_id)
          return {"bills": bills, "invoices": invoices, "balances": balances, "decision_queue": decision_queue}
      
      async def add_decision(self, business_id: str, decision: Dict) -> Dict:
          await self._store_decision(business_id, decision)
          return await self.get_console_data(business_id)
  
  # Update experience services
  class HygieneTrayService:
      def __init__(self, db: Session):
          self.db = db
          self.orchestrator = HygieneTrayDataOrchestrator()
      
      async def get_tray_items(self, business_id: str) -> List[Dict]:
          data = await self.orchestrator.get_tray_data(business_id)
          return data["bills"] + data["invoices"]
  
  class DecisionConsoleService:
      def __init__(self, db: Session):
          self.db = db
          self.orchestrator = DecisionConsoleDataOrchestrator()
      
      async def get_console_data(self, business_id: str) -> Dict[str, Any]:
          return await self.orchestrator.get_console_data(business_id)
      
      async def add_decision(self, business_id: str, decision: Dict) -> Dict[str, Any]:
          return await self.orchestrator.add_decision(business_id, decision)
  ```
- **Dependencies:** None
- **Verification:**
  - Run `grep -r "SmartSyncService" runway/experiences/` - should return no results
  - Run `grep -r "get_.*_for_digest" runway/core/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest tests/runway/` - should pass without import failures
- **Definition of Done:**
  - All experiences use their specific data orchestrator
  - No direct SmartSyncService calls from experiences
  - RunwayCalculator is pure calculation service
  - No runtime errors from broken method calls
  - Domain separation maintained (ADR-001 compliance)
- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed
- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_orchestrators/ runway/experiences/`
  - `git commit -m "feat: implement data orchestrator pattern for experience services"`
- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state
- **Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Remove Obsolete Files:** Delete any files that are no longer needed
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references
  - **Verification Cleanup:** Run cleanup verification commands

#### **Task 1.2: Refactor RunwayCalculator Service Architecture - Foundation for Priority Scoring**
- **Status:** `[✅]` Completed
- **Note:** Priority leveling thresholds (80/50) are temporary - proper solutioning needed for nuanced, business-context aware thresholds per build plan Phase 3
- **Priority:** P1 High
- **Justification:** RunwayCalculator has scope creep with mixed responsibilities violating ADR-001. Need to refactor into focused services that serve as foundation for priority scoring and other runway calculations. Current design mixes pure runway calculations with entity-specific calculations, making it unclear what belongs where.
- **Files to Fix:**
  - `runway/core/runway_calculator.py` - Rename to `runway_calculation_service.py` and remove entity-specific methods
  - `runway/core/bill_impact_calculator.py` - Create new stateless service for bill impact calculations
  - `runway/core/tray_item_impact_calculator.py` - Create new stateless service for tray item impact calculations
  - `runway/core/payment_priority_calculator.py` - Remove (merge into PriorityCalculationService)
  - `runway/core/tray_priority_calculator.py` - Remove (merge into PriorityCalculationService)
  - `runway/experiences/tray.py` - Update to use both data orchestrator AND calculation services directly
  - `runway/experiences/console.py` - Update to use both data orchestrator AND calculation services directly
  - `runway/experiences/digest.py` - Update to use both data orchestrator AND calculation services directly
  - `runway/experiences/test_drive.py` - Update to use both data orchestrator AND calculation services directly
- **Required Changes:**
  - Rename `RunwayCalculator` to `RunwayCalculationService` (pure runway calculations only)
  - Create `BillImpactCalculator` (stateless, receives runway context as parameter)
  - Create `TrayItemImpactCalculator` (stateless, handles bills/invoices with blocking data quality issues)
  - Consolidate priority logic into existing `PriorityCalculationService`
  - Remove duplicate priority services (`PaymentPriorityCalculator`, `TrayPriorityCalculator`)
  - Update all experience services to use both orchestrators AND calculation services directly
  - Ensure no circular dependencies (entity calculators are stateless)
- **Service Architecture to Implement:**
  ```python
  # 1. Pure Runway Calculations (rename existing)
  class RunwayCalculationService:
      def calculate_current_runway(self, qbo_data: Dict) -> Dict
      def calculate_scenario_impact(self, scenario: Dict, qbo_data: Dict) -> Dict  
      def calculate_historical_runway(self, weeks_back: int, qbo_data: Dict) -> List[Dict]
      def calculate_weekly_analysis(self, week_start: datetime, week_end: datetime, qbo_data: Dict) -> Dict
      def calculate_daily_burn_rate(self, qbo_data: Dict) -> float
      def calculate_cash_position(self, qbo_data: Dict) -> float
      def calculate_ar_position(self, qbo_data: Dict) -> float
      def calculate_ap_position(self, qbo_data: Dict) -> float
  
  # 2. Entity Impact Calculators (stateless, no circular dependencies)
  class BillImpactCalculator:
      def calculate_bill_runway_impact(self, bill_data: Dict, runway_context: Dict) -> Dict
      def calculate_payment_impact(self, payment_data: Dict, runway_context: Dict) -> Dict
  
  class TrayItemImpactCalculator:
      def calculate_tray_item_runway_impact(self, item_data: Dict, runway_context: Dict) -> Dict
      # Handles bills/invoices with blocking data quality issues:
      # AP: missing due dates, vendor info, line item details, malformed data
      # AR: incomplete customer data, missing line items, unmatched payments, malformed data
  
  # 3. Centralized Priority Scoring (consolidate existing)
  class PriorityCalculationService:
      def calculate_bill_priority_score(self, bill_data: Dict) -> float
      def calculate_invoice_priority_score(self, invoice_data: Dict) -> float
      def calculate_collection_priority_score(self, customer_data: Dict) -> float
      def calculate_tray_item_priority(self, item_data: Dict) -> Dict
  
  # 4. Experience Integration Pattern
  class TrayService:
      def __init__(self, db: Session, business_id: str):
          self.data_orchestrator = HygieneTrayDataOrchestrator(db, business_id)
          self.runway_calculator = RunwayCalculationService(db, business_id)
          self.priority_calculator = PriorityCalculationService(db, business_id)
          self.bill_impact_calculator = BillImpactCalculator()  # Stateless
          self.tray_item_impact_calculator = TrayItemImpactCalculator()  # Stateless
      
      def get_tray_items(self, business_id: str) -> List[Dict]:
          qbo_data = await self.data_orchestrator.get_tray_data(business_id)
          runway_context = self.runway_calculator.calculate_current_runway(qbo_data)
          bill_impacts = self.bill_impact_calculator.calculate_bill_runway_impact(bills, runway_context)
          tray_impacts = self.tray_item_impact_calculator.calculate_tray_item_runway_impact(items, runway_context)
          priorities = self.priority_calculator.calculate_tray_item_priority(items)
          return self._combine_results(qbo_data, runway_context, bill_impacts, tray_impacts, priorities)
  ```
- **Dependencies:** Task 1 (Data Orchestrator Pattern) must be completed first
- **Verification:**
  - Run `grep -r "calculate_bill_runway_impact\|calculate_tray_item_runway_impact" runway/core/runway_calculation_service.py` - should return no results
  - Run `grep -r "PaymentPriorityCalculator\|TrayPriorityCalculator" runway/` - should return no results
  - Run `grep -r "RunwayCalculator" runway/experiences/` - should return no results (should be RunwayCalculationService)
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest tests/runway/` - should pass without import failures
- **Definition of Done:**
  - Clear separation between pure runway calculations and entity-specific calculations
  - Single source of truth for priority calculations (PriorityCalculationService only)
  - No circular dependencies between services (entity calculators are stateless)
  - All experiences use consistent calculation patterns (orchestrator + calculation services)
  - ADR-001 compliance maintained (domain-specific logic separated from pure business logic)
  - Easy to test and extend (each service can be tested independently)
- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed
- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/runway_calculation_service.py runway/core/bill_impact_calculator.py runway/core/tray_item_impact_calculator.py runway/experiences/`
  - `git commit -m "feat: refactor runway calculator service architecture for priority scoring foundation"`
- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state
- **Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Remove Obsolete Files:** Delete any files that are no longer needed
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references
  - **Verification Cleanup:** Run cleanup verification commands

#### **Task 1.3: Implement TestDrive Data Orchestrator - PLG Experience Data Management**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** TestDrive needs data orchestrator following ADR-006 pattern for PLG experience. Currently uses `RunwayCalculator` directly and mixes real data with demo data. Need proper orchestrator for 4-week historical analysis and sandbox demo data.
- **Files to Create:**
  - `runway/core/data_orchestrators/test_drive_data_orchestrator.py` - TestDrive data orchestrator
- **Files to Fix:**
  - `runway/experiences/test_drive.py` - Use TestDriveDataOrchestrator AND calculation services (following Task 1.2 pattern)
- **Required Implementation:**
  ```python
  # runway/core/data_orchestrators/test_drive_data_orchestrator.py
  class TestDriveDataOrchestrator:
      """Data orchestrator for TestDrive PLG experience - handles both real and demo data."""
      
      async def get_test_drive_data(self, business_id: str = None, use_sandbox: bool = False) -> Dict[str, Any]:
          """Get test drive data - real historical data or sandbox demo data."""
          if use_sandbox or business_id is None:
              return await self._get_sandbox_data()
          else:
              return await self._get_historical_data(business_id)
      
      async def _get_historical_data(self, business_id: str) -> Dict[str, Any]:
          """Pull 4 weeks of historical data for real business analysis."""
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
          """Use existing sandbox data generation for demos."""
          return await self._generate_sandbox_data()

  # runway/experiences/test_drive.py - Updated to follow Task 1.2 pattern
  class TestDriveService:
      def __init__(self, db: Session, business_id: str):
          # Data orchestrator for data pulling + state management
          self.data_orchestrator = TestDriveDataOrchestrator(db, business_id)
          
          # Calculation services for business logic
          self.runway_calculator = RunwayCalculationService(db, business_id)
          self.priority_calculator = PriorityCalculationService(db, business_id)
      
      async def get_test_drive_analysis(self, business_id: str, use_sandbox: bool = False):
          # Get data from orchestrator
          qbo_data = await self.data_orchestrator.get_test_drive_data(business_id, use_sandbox)
          
          # Get runway context using calculation services
          runway_context = self.runway_calculator.calculate_historical_runway(4, qbo_data)
          
          # Calculate priorities and impacts
          priorities = self.priority_calculator.calculate_tray_item_priority(qbo_data.get('bills', []))
          
          return self._combine_results(qbo_data, runway_context, priorities)
  ```
- **Pattern to Replace:**
  ```python
  # Instead of: runway_calculator = self._get_runway_calculator(business_id)
  # Use: 
  # 1. data = await self.data_orchestrator.get_test_drive_data(business_id)
  # 2. runway_context = self.runway_calculator.calculate_historical_runway(4, data)
  # 3. priorities = self.priority_calculator.calculate_tray_item_priority(data.get('bills', []))
  ```
- **Dependencies:** Task 1 (Data Orchestrator Pattern) must be completed first
- **Verification:**
  - Run `grep -r "RunwayCalculator" runway/experiences/test_drive.py` - should return no results
  - Run `grep -r "TestDriveDataOrchestrator" runway/experiences/test_drive.py` - should show usage
  - Run `grep -r "RunwayCalculationService\|PriorityCalculationService" runway/experiences/test_drive.py` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - TestDriveDataOrchestrator created with real historical data and sandbox demo data support
  - TestDrive experience uses BOTH orchestrator AND calculation services (following Task 1.2 pattern)
  - Proper separation between real business data and demo data
  - 4-week historical analysis working with real data
  - PLG demo experience working with sandbox data
- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed
- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_orchestrators/test_drive_data_orchestrator.py runway/experiences/test_drive.py`
  - `git commit -m "feat: implement TestDrive data orchestrator for PLG experience"`

#### **Task 1.4: Implement Digest Data Orchestrator - Bulk Processing for Weekly Analysis**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Digest needs data orchestrator following ADR-006 pattern for bulk processing across multiple businesses. Currently uses `RunwayCalculator` directly and has sequential processing. Need proper orchestrator for Friday morning jobs with bulk operations.
- **Files to Create:**
  - `runway/core/data_orchestrators/digest_data_orchestrator.py` - Digest data orchestrator
- **Files to Fix:**
  - `runway/experiences/digest.py` - Use DigestDataOrchestrator AND calculation services (following Task 1.2 pattern)
  - `infra/scheduler/digest_jobs.py` - Update to use orchestrator for bulk processing
- **Required Implementation:**
  ```python
  # runway/core/data_orchestrators/digest_data_orchestrator.py
  class DigestDataOrchestrator:
      """Data orchestrator for Digest weekly analysis - handles bulk processing across businesses."""
      
      async def get_digest_data(self, business_id: str) -> Dict[str, Any]:
          """Get digest data for single business."""
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
          """Process multiple businesses for Friday morning jobs."""
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

  # runway/experiences/digest.py - Updated to follow Task 1.2 pattern
  class DigestService:
      def __init__(self, db: Session, business_id: str):
          # Data orchestrator for data pulling + state management
          self.data_orchestrator = DigestDataOrchestrator(db, business_id)
          
          # Calculation services for business logic
          self.runway_calculator = RunwayCalculationService(db, business_id)
          self.priority_calculator = PriorityCalculationService(db, business_id)
      
      async def get_digest_analysis(self, business_id: str):
          # Get data from orchestrator
          qbo_data = await self.data_orchestrator.get_digest_data(business_id)
          
          # Get runway context using calculation services
          runway_context = self.runway_calculator.calculate_current_runway(qbo_data)
          
          # Calculate priorities and impacts
          bill_priorities = self.priority_calculator.calculate_bill_priority_score(qbo_data.get('bills', []))
          invoice_priorities = self.priority_calculator.calculate_invoice_priority_score(qbo_data.get('invoices', []))
          
          return self._combine_results(qbo_data, runway_context, bill_priorities, invoice_priorities)
  ```
- **Pattern to Replace:**
  ```python
  # Instead of: runway_calculator = RunwayCalculationService(self.db, business_id)
  # Use: 
  # 1. data = await self.data_orchestrator.get_digest_data(business_id)
  # 2. runway_context = self.runway_calculator.calculate_current_runway(data)
  # 3. priorities = self.priority_calculator.calculate_bill_priority_score(data.get('bills', []))
  ```
- **Dependencies:** Task 1 (Data Orchestrator Pattern) must be completed first
- **Verification:**
  - Run `grep -r "RunwayCalculator" runway/experiences/digest.py` - should return no results
  - Run `grep -r "DigestDataOrchestrator" runway/experiences/digest.py` - should show usage
  - Run `grep -r "RunwayCalculationService\|PriorityCalculationService" runway/experiences/digest.py` - should show usage
  - Run `grep -r "DigestDataOrchestrator" infra/scheduler/digest_jobs.py` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - DigestDataOrchestrator created with single business and bulk processing support
  - Digest experience uses BOTH orchestrator AND calculation services (following Task 1.2 pattern)
  - Friday morning jobs use orchestrator for bulk processing
  - Proper error handling for individual business failures
  - Integration with existing job scheduler infrastructure
- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed
- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_orchestrators/digest_data_orchestrator.py runway/experiences/digest.py infra/scheduler/digest_jobs.py`
  - `git commit -m "feat: implement Digest data orchestrator for bulk weekly analysis"`

---

## **Phase 2: QBO Data Mapping Implementation (P1 High)**

#### **Task 2: Implement QBOMapper for Consistent Field Mapping**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** QBO field names (`TotalAmt`, `DueDate`, `VendorRef`) are scattered throughout the codebase with inconsistent access patterns. Need centralized mapping layer for consistent field access and easier maintenance when QBO API changes.
- **Files to Create:**
  - `runway/core/data_mappers/` - Directory for data mappers
  - `runway/core/data_mappers/qbo_mapper.py` - QBO field mapping service
- **Files to Fix:**
  - `runway/routes/collections.py` - Replace direct QBO field access with mapper
  - `runway/routes/invoices.py` - Replace direct QBO field access with mapper
  - `runway/experiences/test_drive.py` - Replace direct QBO field access with mapper
  - `runway/core/scheduled_payment_service.py` - Replace direct QBO field access with mapper
  - `domains/ap/services/payment.py` - Replace direct QBO field access with mapper
  - `domains/ap/services/bill_ingestion.py` - Replace direct QBO field access with mapper
  - `domains/ar/services/collections.py` - Replace direct QBO field access with mapper
  - `domains/ar/services/invoice.py` - Replace direct QBO field access with mapper
- **Required Implementation:**
  ```python
  # runway/core/data_mappers/qbo_mapper.py
  class QBOMapper:
      """Centralized QBO field mapping for consistent data access."""
      
      @staticmethod
      def map_bill_data(qbo_bill: Dict) -> Dict:
          """Map QBO bill data to runway field names."""
          return {
              'qbo_id': qbo_bill.get('Id'),
              'doc_number': qbo_bill.get('DocNumber'),
              'amount': float(qbo_bill.get('TotalAmt', 0)),
              'balance': float(qbo_bill.get('Balance', 0)),
              'due_date': qbo_bill.get('DueDate'),
              'txn_date': qbo_bill.get('TxnDate'),
              'vendor': {
                  'id': qbo_bill.get('VendorRef', {}).get('value'),
                  'name': qbo_bill.get('VendorRef', {}).get('name', 'Unknown')
              },
              'private_note': qbo_bill.get('PrivateNote'),
              'sync_token': qbo_bill.get('SyncToken')
          }
      
      @staticmethod
      def map_invoice_data(qbo_invoice: Dict) -> Dict:
          """Map QBO invoice data to runway field names."""
          return {
              'qbo_id': qbo_invoice.get('Id'),
              'doc_number': qbo_invoice.get('DocNumber'),
              'amount': float(qbo_invoice.get('TotalAmt', 0)),
              'balance': float(qbo_invoice.get('Balance', 0)),
              'due_date': qbo_invoice.get('DueDate'),
              'txn_date': qbo_invoice.get('TxnDate'),
              'customer': {
                  'id': qbo_invoice.get('CustomerRef', {}).get('value'),
                  'name': qbo_invoice.get('CustomerRef', {}).get('name', 'Unknown')
              },
              'private_note': qbo_invoice.get('PrivateNote'),
              'sync_token': qbo_invoice.get('SyncToken')
          }
      
      @staticmethod
      def map_payment_data(qbo_payment: Dict) -> Dict:
          """Map QBO payment data to runway field names."""
          return {
              'qbo_id': qbo_payment.get('Id'),
              'amount': float(qbo_payment.get('TotalAmt', 0)),
              'txn_date': qbo_payment.get('TxnDate'),
              'payment_ref_num': qbo_payment.get('PaymentRefNum'),
              'private_note': qbo_payment.get('PrivateNote'),
              'sync_token': qbo_payment.get('SyncToken')
          }
  ```
- **Pattern to Replace:**
  ```python
  # Instead of: invoice_data.get("CustomerRef", {}).get("name", "Unknown")
  # Use: QBOMapper.map_invoice_data(invoice_data)['customer']['name']
  
  # Instead of: float(invoice_data.get("TotalAmt", 0))
  # Use: QBOMapper.map_invoice_data(invoice_data)['amount']
  ```
- **Dependencies:** None
- **Verification:**
  - Run `grep -r "TotalAmt\|DueDate\|VendorRef\|CustomerRef" runway/` - should return no results
  - Run `grep -r "TotalAmt\|DueDate\|VendorRef\|CustomerRef" domains/` - should return no results
  - Run `grep -r "QBOMapper" runway/` - should show usage
  - Run `grep -r "QBOMapper" domains/` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - Centralized QBOMapper service created with all QBO field mappings
  - All QBO field access replaced with mapper calls
  - Consistent field naming across runway and domain services
  - Easy to maintain when QBO API changes
  - All obsolete files removed
  - All imports cleaned up
  - All references updated
- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed
- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_mappers/ runway/routes/ runway/experiences/ domains/`
  - `git commit -m "feat: implement QBOMapper for consistent QBO field mapping"`
- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state
- **Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Remove Obsolete Files:** Delete any files that are no longer needed
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references
  - **Verification Cleanup:** Run cleanup verification commands

---

## **Phase 3: Mock Violations & Real Data Implementation (P0 Critical)**

#### **Task 2: Eliminate Mock Violations in Experience Services**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** Experience services still have hardcoded mock data that violates our "no more mocks" commitment. This prevents real data implementation and testing.
- **Files to Fix:**
  - `runway/experiences/test_drive.py` - Mock QBO data violations
  - `sandbox/scenario_runner.py` - Mock QBO data violations
  - `tests/integration/qbo/test_qbo_integration.py` - Mock data violations
- **Required Changes:**
  - Replace mock QBO data with real SmartSyncService calls
  - Use database fixtures from `tests/conftest.py`
  - Implement proper error handling for missing QBO data
- **Pattern to Implement:**
  ```python
  # Instead of: mock_qbo_data = {"bills": [], "invoices": []}
  # Use: 
  from infra.qbo.smart_sync import SmartSyncService
  smart_sync = SmartSyncService(business_id)
  bills = await smart_sync.get_bills()
  invoices = await smart_sync.get_invoices()
  ```
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "mock.*qbo" runway/experiences/` - should return no results
  - Run `grep -r "mock.*qbo" sandbox/` - should return no results
  - Run `grep -r "mock.*qbo" tests/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - All mock QBO data replaced with real SmartSyncService calls
  - Experience services use real QBO data
  - Proper error handling for missing QBO data
  - No mock violations remain in experience services
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

#### **Task 2: Implement Real Data in Tray Experience**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** `runway/experiences/tray.py` returns empty lists instead of real data. This is a core user-facing feature that needs real data.
- **Files to Fix:**
  - `runway/experiences/tray.py` - Connect to real domain services
  - `runway/experiences/digest.py` - Connect to real domain services
- **Required Changes:**
  - Connect tray experience to real domain services
  - Use SmartSyncService for QBO data
  - Implement proper data transformation from domain models to experience format
- **Pattern to Implement:**
  ```python
  # Instead of: return []
  # Use:
  from domains.ap.services.bill_service import BillService
  from domains.ar.services.invoice_service import InvoiceService
  
  bill_service = BillService(business_id)
  invoice_service = InvoiceService(business_id)
  
  bills = await bill_service.get_bills()
  invoices = await invoice_service.get_invoices()
  
  return transform_to_tray_format(bills, invoices)
  ```
- **Dependencies:** `Eliminate Mock Violations in Experience Services`
- **Verification:** 
  - Run `grep -r "return \[\]" runway/experiences/` - should return no results
  - Run `grep -r "SmartSyncService" runway/experiences/` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - Tray experience returns real data from domain services
  - Digest experience returns real data from domain services
  - All experience services use SmartSyncService for QBO data
  - No empty list returns in experience services
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

#### **Task 3: Create Comprehensive Test Data Service**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** Tests need real QBO sandbox data instead of hardcoded mocks. This is documented in 008_eliminate_remaining_mock_violations.md as a comprehensive solution.
- **Files to Create:**
  - `infra/qbo/test_data_service.py` - Centralized test data service
  - `tests/fixtures/qbo_data.py` - QBO data fixtures
- **Required Implementation:**
  ```python
  class QBOTestDataService:
      def __init__(self, business_id: str):
          self.smart_sync = SmartSyncService(business_id)
      
      async def get_test_bills(self) -> List[Dict]:
          """Get real QBO sandbox bills for testing."""
          return await self.smart_sync.get_bills()
      
      async def get_test_invoices(self) -> List[Dict]:
          """Get real QBO sandbox invoices for testing."""
          return await self.smart_sync.get_invoices()
      
      def create_mock_business(self) -> Business:
          """Create test business with QBO fields."""
          # Implementation here
  ```
- **Dependencies:** `Implement Real Data in Tray Experience`
- **Verification:** 
  - Run `pytest tests/` - all tests should pass with real QBO data
  - Run `grep -r "mock.*qbo" tests/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - Centralized test data service created
  - All tests use real QBO sandbox data
  - No mock violations in test files
  - Test data service integrates with SmartSyncService
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

#### **Task 4: Fix Tray Experience Data Implementation**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** `runway/experiences/tray.py` returns empty lists instead of real data. This is a core user-facing feature that needs real data.
- **Files to Fix:**
  - `runway/experiences/tray.py` - Connect to real domain services
  - `runway/experiences/digest.py` - Connect to real domain services
- **Required Changes:**
  - Connect tray experience to real domain services
  - Use SmartSyncService for QBO data
  - Implement proper data transformation from domain models to experience format
- **Pattern to Implement:**
  ```python
  # Instead of: return []
  # Use:
  from domains.ap.services.bill_service import BillService
  from domains.ar.services.invoice_service import InvoiceService
  
  bill_service = BillService(business_id)
  invoice_service = InvoiceService(business_id)
  
  bills = await bill_service.get_bills()
  invoices = await invoice_service.get_invoices()
  
  return transform_to_tray_format(bills, invoices)
  ```
- **Dependencies:** `Eliminate Mock Violations in Experience Services`
- **Verification:** 
  - Run `grep -r "return \[\]" runway/experiences/` - should return no results
  - Run `grep -r "SmartSyncService" runway/experiences/` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - Tray experience returns real data from domain services
  - Digest experience returns real data from domain services
  - All experience services use SmartSyncService for QBO data
  - No empty list returns in experience services
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

## **Phase 2: Architecture Cleanup (P1 High)**

#### **Task 5: Refactor Business ID Dependency Injection Pattern**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Current `get_services()` pattern creates over-engineered dependency injection containers that are fragile and inconsistent.
- **Files to Fix:**
  - `runway/routes/` - All route files using `get_services()`
  - `infra/api/routes/` - All route files using `get_services()`
- **Required Changes:**
  - Replace `get_services()` pattern with direct service instantiation
  - Use `business_id` parameter directly in route functions
  - Remove over-engineered dependency injection containers
- **Pattern to Implement:**
  ```python
  # Instead of:
  def get_services(business_id: str = Depends(get_current_business_id)):
      return {"bill_service": BillService(business_id), ...}
  
  # Use:
  @router.get("/bills")
  async def get_bills(business_id: str = Depends(get_current_business_id)):
      bill_service = BillService(business_id)
      return await bill_service.get_bills()
  ```
- **Dependencies:** `Create Comprehensive Test Data Service`
- **Verification:** 
  - Run `grep -r "get_services" runway/routes/` - should return no results
  - Run `grep -r "get_services" infra/api/routes/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - All route files use direct service instantiation
  - No over-engineered dependency injection containers
  - Clean, simple route patterns
  - All tests pass
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

## **Summary**

- **Total Tasks:** 4
- **P0 Critical:** 1 task (data orchestrator pattern)
- **P1 High:** 3 tasks (QBO mapping, TestDrive orchestrator, Digest orchestrator)
- **Completed:** 2 tasks (data orchestrator pattern, runway calculator refactoring)
- **Ready for Execution:** 3 tasks (TestDrive orchestrator, Digest orchestrator, QBO mapping)

**Key Success Patterns:**
- Follow ADR-001 and ADR-006 architectural patterns
- Use data orchestrators for experience services
- Use calculation services for business logic
- **CRITICAL**: Experiences use BOTH orchestrators AND calculation services directly
- Maintain clean separation between domains/ and runway/

**Critical Success Factors:**
- All tasks must align with ADR-001 domain separation principles
- Use data orchestrator pattern for experience services
- Follow established architectural patterns
- **Follow Task 1.2 pattern**: Experience → DataOrchestrator + CalculationServices

**Architecture Foundation:**
- ✅ Data Orchestrator Pattern implemented
- ✅ RunwayCalculator service architecture refactored
- ✅ Domain service consolidation complete
- ✅ Service boundaries clarified (ADR-001 compliance)

**Ready for Next Phase:**
- Task 1.3: TestDrive Data Orchestrator (updated to follow Task 1.2 pattern)
- Task 1.4: Digest Data Orchestrator (updated to follow Task 1.2 pattern)
- Task 2: QBOMapper Implementation

**Remaining Solutioning Work:**
- Mock violations & real data implementation
- Comprehensive testing strategy
- Console payment decision workflow

This backlog contains only tasks that are **fully solved and ready for hands-free execution** by any developer familiar with the codebase.

**Note:** See `ARCHITECTURAL_FOUNDATION_SUMMARY.md` for complete architectural context and patterns.
