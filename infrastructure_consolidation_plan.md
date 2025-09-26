# Infrastructure Consolidation Plan

## 🏗️ **Proposed Consolidated Infrastructure**

```
infrastructure/
├── cache/                         # Caching layer
│   ├── redis_cache.py
│   ├── memory_cache.py
│   └── base_cache.py
├── queue/                         # Queue management
│   ├── base_queue.py
│   ├── idempotency.py
│   ├── deduplication.py
│   └── priority_queue.py
├── scheduler/                     # Job scheduling
│   ├── job_runner.py
│   ├── providers.py
│   ├── base_job.py
│   └── cron_scheduler.py
├── storage/                       # Storage backends
│   ├── redis_provider.py
│   ├── memory_provider.py
│   └── base_provider.py
├── database/                      # Database infrastructure
│   ├── base.py                    # SQLAlchemy Base
│   ├── session.py                 # Session management
│   ├── transaction.py             # Transaction utilities
│   ├── migrations.py              # Migration utilities
│   └── health.py                  # Database health checks
├── auth/                          # Authentication & security
│   ├── jwt.py                     # JWT token management
│   ├── middleware.py              # Auth middleware
│   ├── permissions.py             # Permission system
│   └── encryption.py              # Encryption utilities
├── api/                           # External API clients
│   ├── base_client.py             # Base API client
│   ├── qbo_client.py              # QBO API client
│   ├── plaid_client.py            # Plaid API client
│   └── rate_limiter.py            # Rate limiting
├── config/                        # Configuration management
│   ├── base_config.py             # Base configuration
│   ├── business_rules.py          # Business rules
│   ├── environment.py             # Environment management
│   └── validation.py              # Config validation
├── files/                         # File & document management
│   ├── storage.py                 # File storage
│   ├── processing.py              # Document processing
│   ├── validation.py              # File validation
│   └── compression.py             # File compression
├── notifications/                 # Email & notifications
│   ├── email.py                   # Email service
│   ├── sms.py                     # SMS service
│   ├── webhooks.py                # Webhook service
│   └── templates.py               # Message templates
├── monitoring/                    # Monitoring & health
│   ├── health_checks.py           # Health check system
│   ├── metrics.py                 # Metrics collection
│   ├── logging.py                 # Centralized logging
│   └── alerts.py                  # Alert system
├── utils/                         # Generic utilities
│   ├── retry.py                   # Retry logic
│   ├── backoff.py                 # Backoff strategies
│   ├── validation.py              # Data validation
│   ├── serialization.py           # Serialization utilities
│   └── crypto.py                  # Cryptographic utilities
└── testing/                       # Testing infrastructure
    ├── fixtures.py                # Test fixtures
    ├── mocks.py                   # Mock utilities
    ├── factories.py               # Test data factories
    └── helpers.py                 # Test helpers
```

## 📊 **Migration Phases**

### **Phase 1: Core Infrastructure (4-6 hours)**
1. **Database** - Move `db/` to `infrastructure/database/`
2. **Auth** - Move middleware to `infrastructure/auth/`
3. **Config** - Move `config/` to `infrastructure/config/`
4. **Jobs** - Move to `infrastructure/scheduler/`

### **Phase 2: API Clients (2-3 hours)**
1. **QBO Client** - Move to `infrastructure/api/`
2. **Plaid Client** - Move to `infrastructure/api/`
3. **Update imports** - Update all references

### **Phase 3: Utilities (2-3 hours)**
1. **File Management** - Consolidate scattered file code
2. **Notifications** - Consolidate email/SMS code
3. **Monitoring** - Consolidate health check code

### **Phase 4: Testing (1-2 hours)**
1. **Test Infrastructure** - Move test utilities
2. **Update tests** - Update test imports
3. **Cleanup** - Remove old scattered code

## 🎯 **Current Status**

### **✅ Completed (Phase 1)**
- Database infrastructure moved to `infra/database/`
- Auth middleware moved to `infra/auth/`
- Config moved to `infra/config/`
- Jobs moved to `infra/scheduler/`
- Base API client created in `infra/api/base_client.py`

### **✅ Completed (Phase 2)**
- Plaid integration moved to `infra/plaid/`
- Plaid identity_graph functionality moved to `infra/queue/deduplication.py`
- SmartSync refactored - utilities extracted to `infra/scheduler/sync_strategies.py` and `infra/cache/sync_cache.py`
- Runway calculators updated to use new infra utilities directly
- SmartSync removed from domains - no longer needed

### **⚠️ Constraints Discovered**
- **QBO Integration**: Moved back to `domains/qbo/` due to circular import issues
  - QBO has complex dependencies on domain models and services
  - Circular imports prevent clean separation into `infra/`
  - Solution: Keep QBO in `domains/` but use `infra/api/base_client.py` for common patterns
- **Import Strategy**: Use IDE find/replace for import updates rather than automated scripts

### **🔄 In Progress (Phase 3)**
- File processing utilities consolidation
- Notifications infrastructure
- Monitoring and health checks
- Generic utilities (validation, serialization, crypto)

### **⏳ Next Steps**
- Complete Phase 3 utilities consolidation (files, notifications, monitoring, utils)
- Phase 4 testing infrastructure and final cleanup
- Update documentation to reflect circular import constraints
