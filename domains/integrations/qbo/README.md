# QBO Integration

QuickBooks Online integration with automatic token management and real API testing.

## Quick Start

1. **Get QBO tokens:**
   ```bash
   poetry run python domains/integrations/qbo/get_qbo_tokens.py
   ```

2. **Test the connection:**
   ```bash
   poetry run pytest tests/integration/test_qbo_api_direct.py -m qbo_real_api
   ```

## Files

- **`auth.py`** - Token management (auto-refresh, OAuth flow)
- **`client.py`** - QBO API calls with retry logic
- **`service.py`** - High-level sync orchestration
- **`health.py`** - Background health monitoring
- **`config.py`** - Centralized configuration
- **`get_qbo_tokens.py`** - Developer tool for token setup

## Configuration

Required `.env` variables:
```bash
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_ENVIRONMENT=sandbox
```

## Token Management

- **Access tokens**: Auto-refresh every hour
- **Refresh tokens**: Last 101 days, stored in database
- **Manual refresh**: Run `get_qbo_tokens.py` when needed

## Testing

- **Real API tests**: `pytest -m qbo_real_api` (requires valid tokens)
- **Mock tests**: `pytest -m "not qbo_real_api"` (fast, no tokens needed)

## Architecture

```
QBOAuthService (auth.py) → QBOAPIProvider (client.py) → QBO REST API
                    ↓
              Database (tokens)
```

**Last Updated**: 2025-01-24