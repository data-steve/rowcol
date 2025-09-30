# QBO Infrastructure Module

## Overview

This module provides raw QBO HTTP client and orchestration services for the Oodaloo platform. It follows strict architectural principles to prevent circular dependencies and maintain clean separation of concerns.

## Architecture Principles

### 1. No Domain Model Dependencies

**CRITICAL**: Infrastructure modules must NEVER directly import or query domain models from `domains/` packages.

```python
# ❌ WRONG - Infrastructure querying domain models
from domains.core.models.business import Business
business = self.db.query(Business).filter(Business.business_id == business_id).first()

# ✅ CORRECT - Infrastructure accepting data as parameters
async def get_business_health_details(self, business_id: str, business_name: str = None):
    # Use the provided data, don't query domain models
```

### 2. Data Transfer Objects (DTOs)

Use DTOs for data transfer between layers instead of direct domain model access:

```python
# infra/qbo/dtos.py
@dataclass
class QBOIntegrationDTO:
    business_id: str
    status: str
    platform: str = "qbo"
    access_token: Optional[str] = None
    # ... other fields
```

### 3. Lazy Initialization for Circular Dependencies

Use lazy initialization to break circular import chains:

```python
class SmartSyncService:
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        self.qbo_client = None  # Lazy initialization
    
    def _get_qbo_client(self):
        """Lazy initialization to avoid circular imports."""
        if self.qbo_client is None:
            from .client import QBORawClient  # Imported here
            self.qbo_client = QBORawClient(self.business_id, self.realm_id, self.db_session)
        return self.qbo_client
```

### 4. Parameter-Based Data Access

Infrastructure services should accept data as parameters rather than querying it:

```python
# ❌ WRONG - Infrastructure querying data
async def get_business_health_details(self, business_id: str):
    business = self.db.query(Business).filter(Business.business_id == business_id).first()
    business_name = business.name if business else "Unknown"

# ✅ CORRECT - Infrastructure accepting data
async def get_business_health_details(self, business_id: str, business_name: str = None, integration_details: Dict[str, Any] = None):
    return {
        "business_id": business_id,
        "business_name": business_name or "Unknown",
        "integration_details": integration_details or {}
    }
```

## Module Structure

```
infra/qbo/
├── README.md              # This file - architectural principles
├── __init__.py           # Module exports
├── client.py             # QBORawClient - raw HTTP calls
├── smart_sync.py         # SmartSyncService - orchestration layer
├── auth.py               # QBOAuthService - authentication
├── setup.py              # QBOSetupService - connection setup
├── health.py             # QBOHealthMonitor - health monitoring
├── config.py             # QBO configuration
└── dtos.py               # Data Transfer Objects
```

## Service Responsibilities

### QBORawClient
- **Purpose**: Raw HTTP calls to QBO API
- **Responsibilities**: HTTP requests, response parsing, error handling
- **Dependencies**: None (pure HTTP client)

### SmartSyncService
- **Purpose**: QBO orchestration and resilience
- **Responsibilities**: Rate limiting, retry logic, deduplication, caching
- **Dependencies**: QBORawClient (lazy loaded), DTOs only

### QBOAuthService
- **Purpose**: QBO authentication and token management
- **Responsibilities**: OAuth flow, token refresh, connection status
- **Dependencies**: DTOs only, no domain models

### QBOHealthMonitor
- **Purpose**: Health monitoring and alerting
- **Responsibilities**: Connection health, alerts, metrics
- **Dependencies**: Accepts data as parameters, no domain queries

## Circular Dependency Prevention

The key insight is that **infrastructure should not query domain models**. Instead:

1. **Domain services** query domain models and pass data to infrastructure
2. **Infrastructure services** accept data as parameters
3. **DTOs** provide data transfer between layers
4. **Lazy initialization** breaks import cycles when necessary

## Testing

All services in this module should be testable without database dependencies:

```python
# Test with mock data
health_monitor = QBOHealthMonitor(db)
result = await health_monitor.get_business_health_details(
    business_id="test-123",
    business_name="Test Business",
    integration_details={"status": "connected"}
)
```

## Migration Notes

This module was created during the "Nuclear Cleanup" of QBO architecture to resolve circular dependencies. The key changes:

1. Moved from `domains/qbo/` to `infra/qbo/`
2. Removed all `domains/` dependencies
3. Introduced DTOs for data transfer
4. Implemented lazy initialization patterns
5. Made services accept data as parameters

## Future Considerations

- Consider moving DTOs to a shared `common/dtos/` package if used across multiple modules
- Implement proper token storage and refresh mechanisms
- Add comprehensive health monitoring and alerting
- Consider caching strategies for frequently accessed data
