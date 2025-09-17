# QBO Integration Guide

Complete guide for QuickBooks Online integration setup, configuration, and safety protocols.

## Quick Start

### Development Setup (Sandbox)

1. **Environment Variables**:
   ```bash
   # .env file
   QBO_CLIENT_ID=your_sandbox_client_id
   QBO_CLIENT_SECRET=your_sandbox_client_secret
   QBO_REALM_ID=your_sandbox_company_id
   QBO_ACCESS_TOKEN=your_sandbox_access_token
   QBO_REFRESH_TOKEN=your_sandbox_refresh_token
   QBO_SANDBOX=true
   
   # Safety gates
   USE_MOCK_QBO=true
   EXTERNAL_WRITE_ENABLED=false
   ```

2. **Test Connection**:
   ```bash
   poetry run python scripts/validate_qbo_sandbox.py --scenario marketing_agency
   ```

### Production Setup

1. **Environment Variables**:
   ```bash
   # Production .env
   QBO_CLIENT_ID=your_production_client_id
   QBO_CLIENT_SECRET=your_production_client_secret
   QBO_SANDBOX=false
   
   # Production safety gates
   USE_MOCK_QBO=false
   EXTERNAL_WRITE_ENABLED=true
   QBO_RATE_LIMIT_ENABLED=true
   ```

## Configuration Contract

### Required Environment Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `QBO_CLIENT_ID` | ✅ Required | ✅ Required | QBO App Client ID |
| `QBO_CLIENT_SECRET` | ✅ Required | ✅ Required | QBO App Client Secret |
| `QBO_REALM_ID` | ✅ Required | ✅ Required | QBO Company ID |
| `QBO_ACCESS_TOKEN` | ✅ Required | ✅ Required | OAuth Access Token |
| `QBO_REFRESH_TOKEN` | ✅ Required | ✅ Required | OAuth Refresh Token |
| `QBO_SANDBOX` | `true` | `false` | Use sandbox environment |
| `USE_MOCK_QBO` | `true` | `false` | Mock QBO responses |
| `EXTERNAL_WRITE_ENABLED` | `false` | `true` | Allow QBO writes |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QBO_RATE_LIMIT_ENABLED` | `true` | Respect QBO rate limits |
| `QBO_TIMEOUT_SECONDS` | `30` | API request timeout |
| `QBO_MAX_RETRIES` | `3` | Max retry attempts |
| `QBO_WEBHOOK_TOKEN` | `null` | Webhook verification token |

## Safety Gates

### Write Protection

**Development (Default)**:
```python
# All QBO writes are blocked by default
USE_MOCK_QBO=true
EXTERNAL_WRITE_ENABLED=false
```

**Production (Explicit)**:
```python
# Writes require explicit enablement
USE_MOCK_QBO=false
EXTERNAL_WRITE_ENABLED=true
```

### Dry-Run Mode

All write operations support dry-run mode:

```python
# API endpoint with dry-run
POST /runway/tray/items/123/confirm
{
    "action": "approve_payment",
    "dry_run": true  # Preview changes without executing
}

# Response includes preview
{
    "preview": {
        "qbo_operations": ["mark_bill_paid", "create_payment"],
        "estimated_impact": {"cash_change": -1500.00}
    },
    "would_execute": false
}
```

### Rate Limiting

QBO API limits: **100 requests per minute**

```python
# Automatic rate limiting
QBO_RATE_LIMIT_ENABLED=true  # Enforces 100 req/min
QBO_RATE_LIMIT_BUFFER=10     # Leave 10 req/min buffer
```

## API Usage Examples

### Basic Data Fetching

```python
from domains.core.services.data_ingestion import DataIngestionService
from db.session import SessionLocal

db = SessionLocal()
data_service = DataIngestionService(db)

# Fetch transactions (respects mock/real setting)
result = data_service.sync_qbo(business_id="123")
print(f"Fetched {result['transactions_stored']} transactions")
```

### Tray Item Actions

```python
from runway.tray.services.tray import TrayService

tray_service = TrayService(db)

# Approve bill payment (with dry-run option)
result = tray_service.confirm_action(
    business_id="123",
    tray_item_id=456,
    action="approve_payment",
    confirmation_data={"dry_run": False}
)

print(f"QBO sync status: {result['qbo_sync_status']}")
```

### Onboarding QBO Connection

```python
from runway.services.onboarding import OnboardingService

onboarding_service = OnboardingService(db)

# Connect QBO (mocked in development)
result = onboarding_service.connect_qbo(
    business_id="123",
    auth_code="sandbox_auth_code"
)

print(f"QBO connected: {result['qbo_connected']}")
```

## Testing Strategy

### Mock-First Development

**Development Flow**:
1. Build with mocked QBO responses
2. Validate business logic with realistic test data
3. Test API contracts with mock providers
4. Switch to sandbox for integration testing
5. Deploy to production with real QBO

**Test Data Sources**:
- `tests/qbo_integration/test_scenarios.py` - Realistic business scenarios
- `scripts/validate_qbo_sandbox.py` - Comprehensive validation

### Sandbox Testing

```bash
# Test specific business scenario
poetry run python scripts/validate_qbo_sandbox.py --scenario construction --real-qbo

# Test all scenarios with sandbox
poetry run python scripts/validate_qbo_sandbox.py --all-scenarios --real-qbo

# Validate webhook handling
poetry run python scripts/test_qbo_webhooks.py --sandbox
```

## Error Handling

### Common QBO Errors

| Error Code | Description | Handling |
|------------|-------------|----------|
| `401` | Invalid/expired token | Auto-refresh token |
| `429` | Rate limit exceeded | Exponential backoff |
| `500` | QBO server error | Retry with delay |
| `3200` | Duplicate transaction | Check idempotency |

### Error Response Format

```python
{
    "error": "QBO_API_ERROR",
    "code": 401,
    "message": "Token expired",
    "details": {
        "qbo_error": "AuthenticationFailed",
        "retry_after": 60,
        "should_refresh_token": true
    }
}
```

## Webhook Configuration

### Setup Webhook Endpoint

```python
# main.py
from domains.integrations.qbo.webhooks import qbo_webhook_router
app.include_router(qbo_webhook_router, prefix="/webhooks/qbo")
```

### Webhook Verification

```bash
# Environment setup
QBO_WEBHOOK_TOKEN=your_webhook_verification_token
QBO_WEBHOOK_ENDPOINT=https://yourdomain.com/webhooks/qbo
```

### Webhook Event Handling

```python
# Supported events
WEBHOOK_EVENTS = [
    "Customer",      # Customer changes
    "Vendor",        # Vendor changes  
    "Item",          # Product/service changes
    "Bill",          # Bill changes
    "Invoice",       # Invoice changes
    "Payment",       # Payment changes
    "Account"        # Chart of accounts changes
]
```

## Troubleshooting

### Connection Issues

**Problem**: `QBO_REALM_ID not found`
```bash
# Solution: Check .env file
cat .env | grep QBO_REALM_ID
# Should show: QBO_REALM_ID=123456789
```

**Problem**: `Token expired`
```bash
# Solution: Refresh OAuth tokens
poetry run python scripts/refresh_qbo_tokens.py
```

### Mock vs Real Data

**Problem**: Getting mock data in production
```bash
# Check environment
echo $USE_MOCK_QBO  # Should be 'false' in production
echo $ENVIRONMENT   # Should be 'production'
```

### Rate Limiting

**Problem**: `429 Too Many Requests`
```bash
# Solution: Check rate limiting settings
echo $QBO_RATE_LIMIT_ENABLED  # Should be 'true'
echo $QBO_MAX_RETRIES         # Should be '3'
```

## Security Considerations

### Token Management

1. **Never commit tokens to git**:
   ```bash
   # .gitignore should include:
   .env
   .env.*
   *.pem
   ```

2. **Rotate tokens regularly**:
   ```bash
   # QBO tokens expire every 180 days
   poetry run python scripts/check_token_expiry.py
   ```

3. **Use environment-specific tokens**:
   ```bash
   # Development
   QBO_CLIENT_ID=sandbox_client_id
   
   # Production  
   QBO_CLIENT_ID=production_client_id
   ```

### Webhook Security

1. **Verify webhook signatures**:
   ```python
   # Automatic signature verification
   QBO_WEBHOOK_TOKEN=your_secret_token
   ```

2. **Use HTTPS only**:
   ```bash
   # Webhook URLs must use HTTPS
   QBO_WEBHOOK_ENDPOINT=https://yourdomain.com/webhooks/qbo
   ```

## Monitoring and Observability

### Key Metrics

- **API Success Rate**: `>99%`
- **Average Response Time**: `<2 seconds`
- **Token Refresh Success**: `100%`
- **Webhook Processing**: `<5 seconds`

### Logging

```python
# Enable QBO integration logging
import logging
logging.getLogger("domains.integrations.qbo").setLevel(logging.INFO)
logging.getLogger("runway.services.digest").setLevel(logging.INFO)
```

### Health Checks

```bash
# Test QBO connectivity
curl http://localhost:8000/health/qbo

# Expected response
{
    "status": "healthy",
    "qbo_connection": "active",
    "last_sync": "2025-09-17T15:30:00Z",
    "token_expires": "2025-12-15T10:00:00Z"
}
```

## Support

### QBO Developer Resources

- [QBO API Documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting)
- [OAuth 2.0 Guide](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)
- [Webhook Guide](https://developer.intuit.com/app/developer/qbo/docs/develop/webhooks)

### Oodaloo QBO Integration

- **Architecture**: `docs/architecture/ADR-001-domains-runway-separation.md`
- **Testing**: `tests/qbo_integration/test_scenarios.py`
- **Validation**: `scripts/validate_qbo_sandbox.py`
