# S04: Data Ownership and Storage Strategy Architecture

## Problem Statement
**CRITICAL ARCHITECTURAL GAP DISCOVERED**: RowCol's data ownership and storage strategy is undefined, creating inconsistent patterns where some services query local databases while others orchestrate external APIs. This fundamental architectural decision affects every service, data orchestrator, and SmartSyncService method, making it impossible to fix the current architecture without first resolving the core data strategy.

**Root Cause**: The comprehensive architecture document describes RowCol as a "Financial Control Plane" but doesn't specify whether RowCol should store its own copy of data or just orchestrate external API calls. This has led to inconsistent implementation patterns across the codebase.

**Impact**: 
- Domain services mix local database queries with SmartSyncService API calls
- SmartSyncService only provides QBO API methods but domain services expect local data
- Data orchestrators pull from external APIs but calculators expect local data
- No clear guidance on what data RowCol owns vs what it orchestrates
- Impossible to fix S01, S02, or any other architecture issues without this foundation

## User Story
As a developer working on the QBO MVP, I need a clear data ownership and storage strategy so that I know whether domain services should query local databases, orchestrate external APIs, or use a hybrid approach. This will enable me to fix SmartSyncService methods, data orchestrator patterns, and service boundaries correctly.

## Solution Overview
Design and implement a comprehensive data ownership and storage strategy that:
1. **Defines data ownership boundaries** - What data does RowCol own vs orchestrate?
2. **Establishes storage patterns** - Local database vs API-only vs hybrid approach
3. **Creates sync strategies** - How to keep local data in sync with external sources
4. **Defines service boundaries** - Which services do CRUD vs API orchestration
5. **Scopes SmartSyncService** - What it should orchestrate vs what should be local
6. **Provides implementation guidance** - Clear patterns for all current services

## Execution Status
- **Type**: Solutioning Task
- **Status**: ✅ **RESOLVED** - Architecture fully defined
- **Estimated Effort**: 0 hours (architecture complete)
- **Priority**: P0 (foundational for all other architecture fixes)
- **Resolution Date**: 2025-01-27

## Architecture Resolution
**✅ RESOLVED**: The DATA_ARCHITECTURE_SPECIFICATION.md provides the complete data ownership and storage strategy:

### **Data Ownership Strategy (Defined)**
- **Multi-Rail Source of Truth**: Each rail owns its domain (QBO=ledger, Ramp=execution, Plaid=verification, Stripe=insights)
- **RowCol is Control Plane**: We orchestrate decisions and provide insights across rails
- **Local Mirror for Performance**: Cache frequently accessed data for fast multi-client operations
- **Live Query for Accuracy**: Query real-time data when accuracy is critical
- **Progressive Implementation**: Start with QBO-only MVP, add rails incrementally

### **Storage Patterns (Defined)**
- **Mirror Locally**: Bills, invoices, balances for frequent operations and historical analysis
- **Query Live**: Current balances, connection status for real-time accuracy
- **Hybrid**: Mirror for calculations, query live for current status

### **Sync Strategies (Defined)**
- **Frequency**: Every 15 minutes via background jobs
- **Trigger**: Scheduled jobs + webhook notifications
- **Scope**: All clients in advisor portfolio
- **Storage**: PostgreSQL with proper indexing

### **Service Boundaries (Defined)**
- **Domain Services**: Query local DB + SmartSyncService for live data
- **Data Orchestrators**: Aggregate from domain services for specific experiences
- **Runway Services**: Use data orchestrators only
- **Infrastructure Services**: Handle external API integration and data sync per rail

### **SmartSyncService Scope (Defined)**
- **Purpose**: Infrastructure orchestration layer for external API calls
- **Responsibilities**: Rate limiting, retry logic, caching, error handling
- **Scope**: QBO API orchestration (Phase 1), multi-rail orchestration (Phase 2+)

### **Implementation Guidance (Defined)**
- **Progressive Implementation**: QBO-only MVP → Add Ramp → Add Plaid → Add Stripe
- **Code Organization**: Rail-specific domains and infrastructure
- **Migration Path**: Clear steps to fix inconsistent services

## Success Criteria
- **Clear data ownership boundaries** - ✅ Every data type has defined ownership
- **Unified storage patterns** - ✅ Consistent approach across all services
- **Clear service boundaries** - ✅ Each service has defined responsibilities
- **Scoped SmartSyncService** - ✅ Clear definition of what it orchestrates
- **Implementation guidance** - ✅ Clear patterns for all current services
- **Migration path** - ✅ Clear steps to fix inconsistent services

## Next Steps
1. **✅ S04 Complete** - Data ownership strategy fully defined
2. **Resume S02** - Data Orchestrator Architecture Fix (implementation tasks)
3. **Resume S01** - QBO Sandbox Testing Strategy (now that architecture is solid)

## Related Tasks
- **S01**: QBO Sandbox Testing Strategy (ON HOLD - waiting for architecture completion)
- **S02**: Data Orchestrator Architecture Fix (ON HOLD - waiting for S04 completion)
- **S03**: SmartSyncService Architecture Fix (✅ COMPLETED)
- **S05**: MVP Product-to-Code Alignment (✅ RESOLVED by architecture docs)

---

*The data ownership and storage strategy is now fully defined in DATA_ARCHITECTURE_SPECIFICATION.md. All architectural questions have been answered.*