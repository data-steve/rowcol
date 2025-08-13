INSERT INTO services (firm_id, name, description, price, complexity_score, task_sequence, tier, automation_score, client_instructions)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'Monthly Bookkeeping', 'Reconcile accounts and prepare financial statements', 500.0, 2.5, '[{"step_type": "intake", "micro_tasks": ["collect_qbo_access", "verify_bank_statements"], "estimated_hours": 1.5}, {"step_type": "reconcile", "micro_tasks": ["match_transactions", "adjust_ledger"], "blockers": [{"task_id": 1, "step_type": "intake"}], "estimated_hours": 3.0}]', 'basic', 0.8, 'Provide QBO access and bank statements.'),
    ('00000000-0000-0000-0000-000000000001', 'Payroll Processing', 'Process payroll and generate reports', 300.0, 2.0, '[{"step_type": "intake", "micro_tasks": ["collect_employee_data"], "estimated_hours": 1.0}, {"step_type": "process", "micro_tasks": ["calculate_pay", "generate_slips"], "blockers": [{"task_id": 1, "step_type": "intake"}], "estimated_hours": 2.0}]', 'basic', 0.7, 'Upload employee data.');

-- Seed a firm and two clients to satisfy foreign keys
INSERT INTO firms (firm_id, name, pricing_tier, doc_volume, settings, qbo_id)
VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Firm', 'basic', 0, '{}', NULL);

INSERT INTO clients (firm_id, name, qbo_id, industry, policy_profile_id)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'Client A', NULL, 'retail', NULL),
    ('00000000-0000-0000-0000-000000000001', 'Client B', NULL, 'pro_services', NULL);

-- Insert engagements with the new schema (no entity_id or service_ids columns)
INSERT INTO engagements (firm_id, client_id, service_type, due_date, user_input, status, compliance_status, qbo_sync_status, allowance_overage, health_status)
VALUES
    ('00000000-0000-0000-0000-000000000001', 1, 'bookkeeping', '2025-12-31T23:59:59', '{"qbo_account": "12345"}', 'pending', 'pending', 'not_started', 0.0, 'healthy'),
    ('00000000-0000-0000-0000-000000000001', 2, 'payroll', '2025-12-31T23:59:59', '{"qbo_account": "67890"}', 'pending', 'pending', 'not_started', 0.0, 'healthy');

INSERT INTO tasks (firm_id, engagement_id, client_id, service_id, type, status, priority, micro_tasks, blockers, estimated_hours, priority_score, automation_eligibility, completion_level)
VALUES
    ('00000000-0000-0000-0000-000000000001', 1, 1, 1, 'intake', 'pending', 'medium', '["collect_qbo_access", "verify_bank_statements"]', '[]', 1.5, 0.8, 'partial', 0.0),
    ('00000000-0000-0000-0000-000000000001', 1, 1, 1, 'reconcile', 'pending', 'medium', '["match_transactions", "adjust_ledger"]', '[{"task_id": 1, "type": "intake"}]', 3.0, 0.6, 'manual', 0.0),
    ('00000000-0000-0000-0000-000000000001', 2, 2, 2, 'intake', 'pending', 'medium', '["collect_employee_data"]', '[]', 1.0, 0.7, 'partial', 0.0);