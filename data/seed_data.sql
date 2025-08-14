-- Seed data for Escher - replacing hardcoded mocks with real data

-- Compliance Requirements Templates
CREATE TABLE IF NOT EXISTS compliance_requirements (
    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_name TEXT NOT NULL,
    regulatory_source TEXT NOT NULL,
    frequency TEXT NOT NULL,
    deadline TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO compliance_requirements (requirement_name, regulatory_source, frequency, deadline, description) VALUES
('W-9 Collection', 'IRS', 'annual', 'Jan 31', 'Collect W-9 forms from all vendors paid over $600'),
('1099 Reporting', 'IRS', 'annual', 'Jan 31', 'File 1099-NEC forms for non-employee compensation'),
('State Tax Registration', 'State', 'annual', 'Varies by state', 'Register for state tax accounts'),
('Quarterly Estimates', 'IRS', 'quarterly', 'Apr 15, Jul 15, Oct 15, Jan 15', 'Pay quarterly estimated taxes'),
('Sales Tax Filing', 'State', 'monthly/quarterly', 'Varies by state', 'File and remit sales tax'),
('Payroll Tax Filing', 'IRS', 'quarterly', 'Apr 30, Jul 31, Oct 31, Jan 31', 'File quarterly payroll tax returns'),
('Business License Renewal', 'Local', 'annual', 'Varies by jurisdiction', 'Renew business licenses and permits'),
('Workers Comp Insurance', 'State', 'annual', 'Varies by state', 'Maintain workers compensation coverage'),
('General Liability Insurance', 'Private', 'annual', 'Varies by policy', 'Maintain general liability insurance'),
('Bank Reconciliation', 'Internal', 'monthly', 'Monthly', 'Reconcile bank statements monthly');

-- Service Type Compliance Mappings
CREATE TABLE IF NOT EXISTS service_compliance_mappings (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_type TEXT NOT NULL,
    requirement_id INTEGER NOT NULL,
    is_required BOOLEAN DEFAULT 1,
    priority INTEGER DEFAULT 1,
    FOREIGN KEY (requirement_id) REFERENCES compliance_requirements(requirement_id)
);

INSERT INTO service_compliance_mappings (service_type, requirement_id, is_required, priority) VALUES
-- Bookkeeping services
('bookkeeping', 1, 1, 1),      -- W-9 Collection
('bookkeeping', 2, 1, 2),      -- 1099 Reporting  
('bookkeeping', 3, 1, 3),      -- State Tax Registration
('bookkeeping', 10, 1, 4),     -- Bank Reconciliation

-- Tax preparation services
('tax_preparation', 1, 1, 1),  -- W-9 Collection
('tax_preparation', 2, 1, 2),  -- 1099 Reporting
('tax_preparation', 3, 1, 3),  -- State Tax Registration
('tax_preparation', 4, 1, 4),  -- Quarterly Estimates
('tax_preparation', 5, 1, 5),  -- Sales Tax Filing
('tax_preparation', 6, 1, 6),  -- Payroll Tax Filing

-- Payroll services
('payroll', 6, 1, 1),          -- Payroll Tax Filing
('payroll', 8, 1, 2),          -- Workers Comp Insurance
('payroll', 9, 1, 3),          -- General Liability Insurance

-- Audit services
('audit', 1, 1, 1),            -- W-9 Collection
('audit', 2, 1, 2),            -- 1099 Reporting
('audit', 3, 1, 3),            -- State Tax Registration
('audit', 10, 1, 4);           -- Bank Reconciliation

-- Task Templates
CREATE TABLE IF NOT EXISTS task_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    service_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    estimated_hours REAL DEFAULT 1.0,
    priority TEXT DEFAULT 'medium',
    dependencies TEXT, -- JSON array of dependent task IDs
    micro_tasks TEXT, -- JSON array of micro-tasks
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO task_templates (task_type, service_type, title, description, estimated_hours, priority, micro_tasks) VALUES
('intake', 'bookkeeping', 'Client Onboarding', 'Initial client setup and data collection', 2.0, 'high', '["collect_qbo_access", "collect_bank_statements", "collect_prior_year_tax_returns"]'),
('reconcile', 'bookkeeping', 'Monthly Reconciliation', 'Monthly bank and credit card reconciliation', 4.0, 'high', '["download_statements", "match_transactions", "investigate_discrepancies", "prepare_adjustments"]'),
('categorize', 'bookkeeping', 'Transaction Categorization', 'Categorize transactions according to chart of accounts', 3.0, 'medium', '["review_transactions", "apply_categories", "flag_uncategorized", "review_exceptions"]'),
('report', 'bookkeeping', 'Financial Reporting', 'Prepare monthly financial statements', 2.0, 'medium', '["generate_pnl", "generate_balance_sheet", "review_metrics", "prepare_notes"]'),

('intake', 'tax_preparation', 'Tax Document Collection', 'Collect all necessary tax documents', 3.0, 'high', '["collect_income_documents", "collect_expense_documents", "collect_deduction_documents"]'),
('prepare', 'tax_preparation', 'Tax Return Preparation', 'Prepare and review tax returns', 6.0, 'high', '["input_data", "calculate_tax", "review_deductions", "final_review"]'),
('file', 'tax_preparation', 'Tax Return Filing', 'File returns with appropriate agencies', 1.0, 'high', '["review_final_return", "submit_electronically", "confirm_receipt"]'),

('intake', 'payroll', 'Payroll Setup', 'Initial payroll system configuration', 4.0, 'high', '["setup_employees", "configure_tax_rates", "setup_direct_deposit"]'),
('process', 'payroll', 'Payroll Processing', 'Process bi-weekly or monthly payroll', 3.0, 'high', '["calculate_pay", "calculate_taxes", "generate_paychecks", "update_records"]');

-- Policy Rules Templates
CREATE TABLE IF NOT EXISTS policy_rule_templates (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    service_type TEXT NOT NULL,
    conditions TEXT NOT NULL, -- JSON object defining when rule applies
    actions TEXT NOT NULL,    -- JSON array of actions to take
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO policy_rule_templates (rule_name, rule_type, service_type, conditions, actions, priority) VALUES
('High Amount Review', 'categorization', 'bookkeeping', '{"amount_greater_than": 10000, "category": "expense"}', '["flag_for_review", "require_approval", "send_notification"]', 1),
('Vendor W-9 Required', 'compliance', 'bookkeeping', '{"amount_greater_than": 600, "vendor_type": "individual"}', '["collect_w9", "flag_incomplete", "send_reminder"]', 1),
('Unusual Transaction', 'fraud_detection', 'bookkeeping', '{"amount_deviation": "2_std", "category": "any"}', '["flag_suspicious", "require_documentation", "notify_manager"]', 2),
('Tax Filing Deadline', 'compliance', 'tax_preparation', '{"deadline_approaching": 30, "form_type": "1099"}', '["send_reminder", "escalate_priority", "notify_client"]', 1);

-- Vendor Categories
CREATE TABLE IF NOT EXISTS vendor_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    description TEXT,
    default_gl_account TEXT,
    risk_level TEXT DEFAULT 'low',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO vendor_categories (category_name, description, default_gl_account, risk_level) VALUES
('Office Supplies', 'Office supplies and equipment', '6000-Office Supplies', 'low'),
('Professional Services', 'Legal, accounting, consulting services', '6000-Professional Services', 'medium'),
('Technology', 'Software, hardware, IT services', '6000-Technology', 'medium'),
('Travel & Entertainment', 'Travel expenses and client entertainment', '6000-Travel & Entertainment', 'medium'),
('Marketing & Advertising', 'Marketing materials and advertising', '6000-Marketing & Advertising', 'medium'),
('Insurance', 'Business insurance policies', '6000-Insurance', 'low'),
('Utilities', 'Electric, water, internet, phone', '6000-Utilities', 'low'),
('Rent & Leasing', 'Office rent and equipment leasing', '6000-Rent & Leasing', 'low'),
('Payroll Services', 'Payroll processing and HR services', '6000-Payroll Services', 'low'),
('Tax Services', 'Tax preparation and filing services', '6000-Tax Services', 'low');

-- Chart of Accounts Templates
CREATE TABLE IF NOT EXISTS coa_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT NOT NULL,
    industry TEXT NOT NULL,
    account_number TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    parent_account TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO coa_templates (template_name, industry, account_number, account_name, account_type, parent_account) VALUES
-- Standard Chart of Accounts
('standard', 'general', '1000', 'Assets', 'header', NULL),
('standard', 'general', '1100', 'Current Assets', 'header', '1000'),
('standard', 'general', '1110', 'Cash and Cash Equivalents', 'asset', '1100'),
('standard', 'general', '1120', 'Accounts Receivable', 'asset', '1100'),
('standard', 'general', '1130', 'Inventory', 'asset', '1100'),
('standard', 'general', '1200', 'Fixed Assets', 'header', '1000'),
('standard', 'general', '1210', 'Equipment', 'asset', '1200'),
('standard', 'general', '1220', 'Furniture and Fixtures', 'asset', '1200'),
('standard', 'general', '2000', 'Liabilities', 'header', NULL),
('standard', 'general', '2100', 'Current Liabilities', 'header', '2000'),
('standard', 'general', '2110', 'Accounts Payable', 'liability', '2100'),
('standard', 'general', '2120', 'Accrued Expenses', 'liability', '2100'),
('standard', 'general', '3000', 'Equity', 'header', NULL),
('standard', 'general', '3100', 'Owner Equity', 'equity', '3000'),
('standard', 'general', '4000', 'Revenue', 'header', NULL),
('standard', 'general', '4100', 'Service Revenue', 'revenue', '4000'),
('standard', 'general', '5000', 'Cost of Goods Sold', 'header', NULL),
('standard', 'general', '6000', 'Expenses', 'header', NULL),
('standard', 'general', '6010', 'Office Supplies', 'expense', '6000'),
('standard', 'general', '6020', 'Professional Services', 'expense', '6000'),
('standard', 'general', '6030', 'Technology', 'expense', '6000'),
('standard', 'general', '6040', 'Travel & Entertainment', 'expense', '6000'),
('standard', 'general', '6050', 'Marketing & Advertising', 'expense', '6000'),
('standard', 'general', '6060', 'Insurance', 'expense', '6000'),
('standard', 'general', '6070', 'Utilities', 'expense', '6000'),
('standard', 'general', '6080', 'Rent & Leasing', 'expense', '6000'),
('standard', 'general', '6090', 'Payroll Services', 'expense', '6000'),
('standard', 'general', '6100', 'Tax Services', 'expense', '6000');


CREATE TABLE IF NOT EXISTS bank_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    external_id TEXT,
    amount REAL NOT NULL,
    date TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    account_id TEXT,
    source TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    rule_id INTEGER,
    confidence REAL DEFAULT 0.0,
    suggestion_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id),
    FOREIGN KEY (rule_id) REFERENCES rules(rule_id),
    FOREIGN KEY (suggestion_id) REFERENCES suggestions(suggestion_id)
);

INSERT INTO bank_transactions (
    firm_id, client_id, external_id, amount, date, description, account_id, source, status, confidence
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_001',
    150.0,
    '2025-01-15 10:00:00',
    'Starbucks Purchase',
    '6000-Expenses',
    'qbo_feed',
    'pending',
    0.9
), (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_002',
    500.0,
    '2025-01-16 12:00:00',
    'Amazon Purchase',
    '6000-Expenses',
    'qbo_feed',
    'pending',
    0.8
), (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_003',
    1000.0,
    '2025-01-17 09:00:00',
    'Transfer Out to Savings',
    '1110-Cash',
    'qbo_feed',
    'pending',
    0.7
), (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_004',
    -1000.0,
    '2025-01-17 09:05:00',
    'Transfer In from Checking',
    '1110-Cash',
    'qbo_feed',
    'pending',
    0.7
);

CREATE TABLE IF NOT EXISTS transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    source_transaction_id INTEGER NOT NULL,
    destination_transaction_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    date TIMESTAMP NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (source_transaction_id) REFERENCES bank_transactions(transaction_id),
    FOREIGN KEY (destination_transaction_id) REFERENCES bank_transactions(transaction_id)
);

INSERT INTO transfers (
    firm_id, source_transaction_id, destination_transaction_id, amount, date, description
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    3,
    4,
    1000.0,
    '2025-01-17 09:00:00',
    'Transfer between Checking and Savings'
);

INSERT INTO rules (
    firm_id, client_id, priority, match_type, pattern, output, scope
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    NULL,
    5,
    'contains',
    'Transfer',
    '{"account": "1110-Cash", "class": "Transfer", "confidence": 0.95}',
    'global'
);

INSERT INTO suggestions (
    firm_id, client_id, txn_id, top_k
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_003',
    '[{"account": "1110-Cash", "confidence": 0.95, "rule_id": "5", "rule_name": "Transfer Rule"}]'
), (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_004',
    '[{"account": "1110-Cash", "confidence": 0.95, "rule_id": "5", "rule_name": "Transfer Rule"}]'
);