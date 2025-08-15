-- Seed data for the Close domain in Stage 2 of the Escher project
-- Adds preclose_checks, exceptions, pbc_requests, close_checklists tables
-- References: Stage 2 requirements, domains/core/data/seed_data.sql

CREATE TABLE IF NOT EXISTS preclose_checks (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    period TIMESTAMP NOT NULL,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    evidence_refs JSON DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE IF NOT EXISTS exceptions (
    exception_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    period TIMESTAMP NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE IF NOT EXISTS pbc_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    period TIMESTAMP NOT NULL,
    item_type TEXT NOT NULL,
    owner TEXT NOT NULL,
    due_date TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'pending',
    reminders JSON DEFAULT '[]',
    task_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE TABLE IF NOT EXISTS close_checklists (
    checklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id TEXT NOT NULL,
    client_id INTEGER,
    period TIMESTAMP NOT NULL,
    items JSON DEFAULT '[]',
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (firm_id) REFERENCES firms(firm_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

INSERT INTO preclose_checks (
    firm_id, client_id, period, type, status, evidence_refs
) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-31 00:00:00', 'bank_rec', 'fail', '[]'),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-31 00:00:00', 'pbc_complete', 'fail', '[]'),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-02-28 00:00:00', 'bank_rec', 'pass', '[]'),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-02-28 00:00:00', 'pbc_complete', 'pass', '[]');

INSERT INTO exceptions (
    firm_id, client_id, period, type, description
) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-31 00:00:00', 'unmatched_txn', 'Unmatched bank transactions for January'),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-31 00:00:00', 'missing_pbc', 'Missing bank statement for January'),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-02-28 00:00:00', 'unmatched_txn', 'Unmatched payroll batch for February');

INSERT INTO pbc_requests (
    firm_id, client_id, period, item_type, owner, due_date, status, task_id
) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-31 00:00:00', 'bank_stmt', 'client@example.com', '2025-01-30 00:00:00', 'pending', 1),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-31 00:00:00', 'payroll', 'client@example.com', '2025-01-30 00:00:00', 'pending', 2),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-02-28 00:00:00', 'bank_stmt', 'client@example.com', '2025-02-27 00:00:00', 'received', 3);

INSERT INTO close_checklists (
    firm_id, client_id, period, items, status
) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-01-31 00:00:00', '[1, 2]', 'blocked'),
('550e8400-e29b-41d4-a716-446655440000', 1, '2025-02-28 00:00:00', '[3, 4]', 'ready');
