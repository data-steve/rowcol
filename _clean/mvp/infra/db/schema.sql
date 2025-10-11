-- RowCol MVP Database Schema
-- SQLite schema for Smart Sync pattern with Transaction Log and State Mirror

-- Append-only transaction log (audit, retry/replay)
CREATE TABLE IF NOT EXISTS integration_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  direction TEXT CHECK(direction IN ('OUTBOUND','INBOUND')) NOT NULL,
  rail TEXT NOT NULL,           -- 'qbo'
  operation TEXT NOT NULL,      -- 'list_bills', 'post_bill_payment'
  idem_key TEXT,                -- stable key for writes
  http_code INTEGER,
  status TEXT,                  -- 'OK','RETRY','FAILED'
  payload_json TEXT,            -- raw rail payload
  source_version TEXT,          -- etag or change token if available
  advisor_id TEXT NOT NULL,     -- primary identifier (advisor-first model)
  business_id TEXT NOT NULL,    -- foreign key to business
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- State mirrors (fast reads) - all include advisor_id for data isolation
CREATE TABLE IF NOT EXISTS mirror_bills (
  bill_id TEXT PRIMARY KEY,
  advisor_id TEXT NOT NULL,     -- primary identifier
  business_id TEXT NOT NULL,    -- foreign key to business
  vendor_id TEXT,
  vendor_name TEXT,
  due_date TEXT,
  amount NUMERIC,
  status TEXT,                  -- 'OPEN','SCHEDULED','PAID'
  source_version TEXT,
  last_synced_at DATETIME,
  data_json TEXT                -- full QBO data as JSON
);

CREATE INDEX IF NOT EXISTS idx_mirror_bills_advisor_business ON mirror_bills (advisor_id, business_id);

CREATE TABLE IF NOT EXISTS mirror_invoices (
  invoice_id TEXT PRIMARY KEY,
  advisor_id TEXT NOT NULL,     -- primary identifier
  business_id TEXT NOT NULL,    -- foreign key to business
  customer_id TEXT,
  customer_name TEXT,
  due_date TEXT,
  amount NUMERIC,
  status TEXT,                  -- 'OPEN','PARTIAL','PAID'
  source_version TEXT,
  last_synced_at DATETIME,
  data_json TEXT                -- full QBO data as JSON
);

CREATE INDEX IF NOT EXISTS idx_mirror_invoices_advisor_business ON mirror_invoices (advisor_id, business_id);

CREATE TABLE IF NOT EXISTS mirror_balances (
  account_id TEXT PRIMARY KEY,
  advisor_id TEXT NOT NULL,     -- primary identifier
  business_id TEXT NOT NULL,    -- foreign key to business
  account_name TEXT,
  available NUMERIC,
  current NUMERIC,
  source_version TEXT,
  last_synced_at DATETIME,
  data_json TEXT                -- full QBO data as JSON
);

CREATE INDEX IF NOT EXISTS idx_mirror_balances_advisor_business ON mirror_balances (advisor_id, business_id);

-- Advisor-Business relationship table
CREATE TABLE IF NOT EXISTS advisor_businesses (
  advisor_id TEXT NOT NULL,
  business_id TEXT NOT NULL,
  business_name TEXT,
  qbo_realm_id TEXT,            -- QBO company ID
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (advisor_id, business_id)
);

-- Entity policy configuration for TTL management
CREATE TABLE IF NOT EXISTS entity_policy (
  entity TEXT PRIMARY KEY,      -- 'bills', 'invoices', 'balances'
  soft_ttl_seconds INTEGER NOT NULL,
  hard_ttl_seconds INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System-level integration tokens (for all rails: QBO, Stripe, Plaid, etc.)
CREATE TABLE IF NOT EXISTS system_integration_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rail TEXT NOT NULL,                    -- 'qbo', 'stripe', 'plaid', 'ramp'
  environment TEXT NOT NULL,             -- 'sandbox', 'production', 'development'
  external_id TEXT NOT NULL,             -- realm_id, account_id, etc.
  access_token TEXT NOT NULL,
  refresh_token TEXT,
  access_expires_at DATETIME,
  refresh_expires_at DATETIME,
  scope TEXT,                            -- OAuth scopes or permissions
  status TEXT DEFAULT 'active',          -- 'active', 'expired', 'revoked', 'error'
  metadata_json TEXT,                    -- Additional rail-specific data
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(rail, environment, external_id)
);

-- Index for efficient token lookups
CREATE INDEX IF NOT EXISTS idx_system_tokens_rail_env ON system_integration_tokens (rail, environment);
CREATE INDEX IF NOT EXISTS idx_system_tokens_status ON system_integration_tokens (status);
CREATE INDEX IF NOT EXISTS idx_system_tokens_expires ON system_integration_tokens (access_expires_at, refresh_expires_at);

-- Insert default entity policies
INSERT OR IGNORE INTO entity_policy (entity, soft_ttl_seconds, hard_ttl_seconds) VALUES
('bills', 300, 3600),      -- 5min soft, 1hr hard
('invoices', 900, 3600),    -- 15min soft, 1hr hard
('balances', 120, 600);     -- 2min soft, 10min hard
