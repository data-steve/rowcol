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
('Vendor Categorization', 'categorization', 'bookkeeping', '{"description_contains": ["office", "supplies", "staples"]}', '["assign_account": "5000-Office Supplies", "flag_for_review": false]', 1),
('Travel Expense Rule', 'categorization', 'bookkeeping', '{"description_contains": ["uber", "lyft", "hotel", "airline"]}', '["assign_account": "6000-Travel & Entertainment", "require_receipt": true]', 2),
('Meal Expense Rule', 'categorization', 'bookkeeping', '{"description_contains": ["restaurant", "lunch", "dinner", "coffee"]}', '["assign_account": "6050-Meals & Entertainment", "limit_amount": 50]', 3),
('Software Subscription Rule', 'categorization', 'bookkeeping', '{"description_contains": ["subscription", "software", "saas"]}', '["assign_account": "7000-Software & Technology", "flag_for_review": true]', 4),
('Payroll Rule', 'categorization', 'payroll', '{"description_contains": ["payroll", "salary", "wages"]}', '["assign_account": "6090-Payroll Services", "require_approval": true]', 1),
('Tax Payment Rule', 'categorization', 'tax_preparation', '{"description_contains": ["tax", "irs", "state"]}', '["assign_account": "6100-Tax Services", "flag_for_review": true]', 1);

-- Vendor Categories
CREATE TABLE IF NOT EXISTS vendor_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    description TEXT,
    default_account TEXT,
    risk_level TEXT DEFAULT 'low',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO vendor_categories (category_name, description, default_account, risk_level) VALUES
('Office Supplies', 'General office supplies and stationery', '5000-Office Supplies', 'low'),
('Professional Services', 'Legal, accounting, consulting services', '6000-Professional Services', 'medium'),
('Technology', 'Software, hardware, IT services', '7000-Software & Technology', 'medium'),
('Travel & Entertainment', 'Travel expenses, meals, entertainment', '6050-Meals & Entertainment', 'high'),
('Payroll Services', 'Payroll processing and tax services', '6090-Payroll Services', 'low'),
('Tax Services', 'Tax preparation and filing services', '6100-Tax Services', 'low'),
('Insurance', 'Business insurance policies', '8000-Insurance', 'medium'),
('Utilities', 'Electric, water, internet, phone', '4000-Utilities', 'low');

-- Chart of Accounts Templates
CREATE TABLE IF NOT EXISTS coa_templates (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    parent_account TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO coa_templates (account_number, account_name, account_type, parent_account, description) VALUES
-- Assets
('1000', 'Cash & Cash Equivalents', 'asset', NULL, 'Bank accounts and petty cash'),
('1100', 'Accounts Receivable', 'asset', NULL, 'Money owed by customers'),
('1200', 'Inventory', 'asset', NULL, 'Product inventory'),
('1300', 'Prepaid Expenses', 'asset', NULL, 'Prepaid insurance, rent, etc.'),

-- Liabilities
('2000', 'Accounts Payable', 'liability', NULL, 'Money owed to vendors'),
('2100', 'Credit Cards', 'liability', NULL, 'Credit card balances'),
('2200', 'Loans Payable', 'liability', NULL, 'Business loans and lines of credit'),
('2300', 'Accrued Expenses', 'liability', NULL, 'Accrued payroll, taxes, etc.'),

-- Equity
('3000', 'Owner Equity', 'equity', NULL, 'Owner investments and retained earnings'),
('3100', 'Retained Earnings', 'equity', NULL, 'Cumulative net income/loss'),

-- Revenue
('4000', 'Service Revenue', 'revenue', NULL, 'Revenue from services provided'),
('4100', 'Product Revenue', 'revenue', NULL, 'Revenue from product sales'),
('4200', 'Other Income', 'revenue', NULL, 'Interest, refunds, other income'),

-- Expenses
('5000', 'Office Supplies', 'expense', NULL, 'Office supplies and stationery'),
('6000', 'Professional Services', 'expense', NULL, 'Legal, accounting, consulting'),
('6050', 'Meals & Entertainment', 'expense', NULL, 'Business meals and entertainment'),
('6090', 'Payroll Services', 'expense', NULL, 'Payroll processing and tax services'),
('6100', 'Tax Services', 'expense', NULL, 'Tax preparation and filing'),
('7000', 'Software & Technology', 'expense', NULL, 'Software subscriptions and IT services'),
('8000', 'Insurance', 'expense', NULL, 'Business insurance policies'),
('9000', 'Other Expenses', 'expense', NULL, 'Miscellaneous business expenses');

-- Bank Transactions
CREATE TABLE IF NOT EXISTS bank_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    account_id TEXT,
    source TEXT,
    status TEXT DEFAULT 'pending',
    suggestion_id INTEGER,
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO bank_transactions (firm_id, client_id, amount, date, description, account_id, source, status) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, 150.00, '2025-01-15', 'Starbucks Purchase', '6050-Meals & Entertainment', 'qbo_feed', 'categorized'),
('550e8400-e29b-41d4-a716-446655440000', 1, -2500.00, '2025-01-15', 'Client Payment - ABC Corp', '4000-Service Revenue', 'qbo_feed', 'categorized'),
('550e8400-e29b-41d4-a716-446655440000', 1, 89.99, '2025-01-16', 'Office Depot', '5000-Office Supplies', 'qbo_feed', 'categorized'),
('550e8400-e29b-41d4-a716-446655440000', 1, -150.00, '2025-01-16', 'Starbucks Refund', '6050-Meals & Entertainment', 'qbo_feed', 'categorized'),
('550e8400-e29b-41d4-a716-446655440000', 1, 299.99, '2025-01-17', 'QuickBooks Subscription', '7000-Software & Technology', 'qbo_feed', 'categorized'),
('550e8400-e29b-41d4-a716-446655440000', 1, -5000.00, '2025-01-17', 'Payroll Processing', '6090-Payroll Services', 'qbo_feed', 'categorized'),
('550e8400-e29b-41d4-a716-446655440000', 1, 1500.00, '2025-01-18', 'Tax Preparation Services', '6100-Tax Services', 'qbo_feed', 'categorized');

-- Transfers
CREATE TABLE IF NOT EXISTS transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    source_transaction_id INTEGER,
    destination_transaction_id INTEGER,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Firms
CREATE TABLE IF NOT EXISTS firms (
    firm_id TEXT PRIMARY KEY,
    firm_name TEXT NOT NULL,
    tax_id TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO firms (firm_id, firm_name, tax_id, address, phone, email) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Escher Accounting', '12-3456789', '123 Main St, Anytown, USA', '555-0123', 'info@escheraccounting.com');

-- Clients
CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    tax_id TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    industry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id)
);

INSERT INTO clients (client_id, firm_id, client_name, tax_id, address, phone, email, industry) VALUES
(1, '550e8400-e29b-41d4-a716-446655440000', 'ABC Corporation', '98-7654321', '456 Business Ave, Anytown, USA', '555-9876', 'contact@abccorp.com', 'Technology'),
(2, '550e8400-e29b-41d4-a716-446655440000', 'XYZ Manufacturing', '87-6543210', '789 Industrial Blvd, Anytown, USA', '555-8765', 'info@xyzmanufacturing.com', 'Manufacturing');

-- Payroll Batches
CREATE TABLE IF NOT EXISTS payroll_batches (
    batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    total_amount REAL NOT NULL,
    payroll_date DATE NOT NULL,
    period_start DATE,
    period_end DATE,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

INSERT INTO payroll_batches (firm_id, client_id, total_amount, payroll_date, period_start, period_end, description, status) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, 5000.00, '2025-01-15', '2025-01-01', '2025-01-15', 'Bi-weekly payroll', 'processed'),
('550e8400-e29b-41d4-a716-446655440000', 2, 7500.00, '2025-01-15', '2025-01-01', '2025-01-15', 'Bi-weekly payroll', 'pending');

-- Payroll Remittances
CREATE TABLE IF NOT EXISTS payroll_remittances (
    remittance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    batch_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    tax_agency TEXT NOT NULL,
    remittance_date DATE NOT NULL,
    status TEXT DEFAULT 'pending',
    transaction_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (batch_id) REFERENCES payroll_batches(batch_id)
);

INSERT INTO payroll_remittances (firm_id, batch_id, amount, tax_agency, remittance_date, status) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, 1500.00, 'IRS', '2025-01-15', 'pending'),
('550e8400-e29b-41d4-a716-446655440000', 1, 500.00, 'State', '2025-01-15', 'pending');

-- CRITICAL MISSING TABLES FOR AR/AP SERVICES

-- Invoices (AR)
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    customer_id INTEGER NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total REAL NOT NULL,
    lines TEXT, -- JSON array of line items
    status TEXT DEFAULT 'open',
    attachment_refs TEXT, -- JSON array of document references
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (customer_id) REFERENCES clients(client_id)
);

INSERT INTO invoices (firm_id, customer_id, issue_date, due_date, total, lines, status) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-01', '2025-01-31', 2500.00, '[{"description": "Bookkeeping Services", "amount": 2000.00}, {"description": "Tax Preparation", "amount": 500.00}]', 'open'),
('550e8400-e29b-41d4-a716-446655440000', 2, '2025-01-05', '2025-02-05', 1500.00, '[{"description": "Monthly Reconciliation", "amount": 1500.00}]', 'open');

-- Credit Memos (AR)
CREATE TABLE IF NOT EXISTS credit_memos (
    credit_memo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    invoice_id INTEGER,
    amount REAL NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);

-- Bills (AP)
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    vendor_id INTEGER,
    amount REAL NOT NULL,
    due_date DATE NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id)
);

INSERT INTO bills (firm_id, vendor_id, amount, due_date, description, status) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, 500.00, '2025-01-31', 'Office Supplies', 'pending'),
('550e8400-e29b-41d4-a716-446655440000', 2, 1000.00, '2025-02-15', 'Software Subscription', 'pending');

-- Payments (AP)
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    bill_id INTEGER,
    amount REAL NOT NULL,
    payment_date DATE NOT NULL,
    payment_method TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

-- Suggestions
CREATE TABLE IF NOT EXISTS suggestions (
    suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    txn_id TEXT,
    top_k TEXT NOT NULL, -- JSON array of top suggestions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

INSERT INTO suggestions (
    firm_id, client_id, txn_id, top_k
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_005',
    '[{"account": "6090-Payroll Services", "confidence": 0.95, "rule_id": "6", "rule_name": "Payroll Rule"}]'
), (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    'qbo_txn_006',
    '[{"account": "6100-Tax Services", "confidence": 0.90, "rule_id": "7", "rule_name": "Tax Payment Rule"}]'
);