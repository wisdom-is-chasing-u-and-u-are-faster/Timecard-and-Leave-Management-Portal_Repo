-- Realistic baseline mock data for Enterprise HRMS Platform

INSERT INTO departments (id, name, code) VALUES
('dept-eng', 'Engineering', 'ENG'),
('dept-hr', 'People & Culture', 'HR'),
('dept-fin', 'Finance & Payroll', 'FIN')
ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, email, name, role, azure_ad_oid, is_active) VALUES
('usr-admin', 'admin@enterprise-hrms.internal', 'HR Administrator', 'ADMIN', 'aad-oid-001', TRUE),
('usr-mgr-1', 'john.doe@enterprise-hrms.internal', 'John Doe', 'MANAGER', 'aad-oid-002', TRUE),
('usr-emp-1', 'jane.smith@enterprise-hrms.internal', 'Jane Smith', 'EMPLOYEE', 'aad-oid-003', TRUE),
('usr-emp-2', 'robert.chen@enterprise-hrms.internal', 'Robert Chen', 'EMPLOYEE', 'aad-oid-004', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO employees (id, employee_id, first_name, last_name, email, title, department_id, manager_id, user_id, hire_date, status) VALUES
('emp-001', 'EMP-1001', 'John', 'Doe', 'john.doe@enterprise-hrms.internal', 'Engineering Director', 'dept-eng', NULL, 'usr-mgr-1', '2022-01-15', 'ACTIVE'),
('emp-002', 'EMP-1002', 'Jane', 'Smith', 'jane.smith@enterprise-hrms.internal', 'Senior Software Engineer', 'dept-eng', 'emp-001', 'usr-emp-1', '2023-03-01', 'ACTIVE'),
('emp-003', 'EMP-1003', 'Robert', 'Chen', 'robert.chen@enterprise-hrms.internal', 'HR Operations Lead', 'dept-hr', NULL, 'usr-emp-2', '2021-08-20', 'ACTIVE')
ON CONFLICT (id) DO NOTHING;

INSERT INTO leave_balances (id, employee_id, leave_type, allocated, used, remaining, year) VALUES
('lb-001', 'emp-002', 'Paid Time Off (PTO)', 20.00, 5.00, 15.00, 2026),
('lb-002', 'emp-002', 'Sick Leave', 10.00, 2.00, 8.00, 2026),
('lb-003', 'emp-002', 'Casual Leave', 5.00, 0.00, 5.00, 2026)
ON CONFLICT (id) DO NOTHING;

INSERT INTO leave_requests (id, employee_id, leave_type, start_date, end_date, days, reason, status, approver_id, approver_comment) VALUES
('lr-001', 'emp-002', 'Paid Time Off (PTO)', '2026-11-10', '2026-11-12', 3.00, 'Family vacation trip', 'APPROVED', 'emp-001', 'Approved, enjoy!'),
('lr-002', 'emp-002', 'Sick Leave', '2026-11-20', '2026-11-20', 1.00, 'Dental checkup', 'PENDING', 'emp-001', NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO attendance_logs (id, employee_id, work_date, check_in, check_out, total_hours, status) VALUES
('att-001', 'emp-002', '2026-10-27', '2026-10-27 09:00:00+00', '2026-10-27 17:30:00+00', 8.50, 'COMPLETED'),
('att-002', 'emp-002', '2026-10-28', '2026-10-28 08:55:00+00', NULL, 0.00, 'IN_PROGRESS')
ON CONFLICT (id) DO NOTHING;

INSERT INTO document_vault (id, employee_id, file_name, gcs_uri, category, mime_type, file_size, is_encrypted) VALUES
('doc-001', 'emp-002', 'employment_agreement_signed.pdf', 'gs://persistent-genai-tf-state/hrms-vault/emp-002/agreement.pdf', 'Contracts', 'application/pdf', 1048576, TRUE),
('doc-002', 'emp-002', 'w4_tax_form_2026.pdf', 'gs://persistent-genai-tf-state/hrms-vault/emp-002/w4.pdf', 'Tax', 'application/pdf', 524288, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO payroll_records (id, employee_id, month, base_salary, allowances, deductions, net_pay, status) VALUES
('pay-001', 'emp-002', '2026-09', 11500.00, 800.00, 2650.00, 9650.00, 'PAID'),
('pay-002', 'emp-002', '2026-10', 11500.00, 800.00, 2650.00, 9650.00, 'PAID')
ON CONFLICT (id) DO NOTHING;
