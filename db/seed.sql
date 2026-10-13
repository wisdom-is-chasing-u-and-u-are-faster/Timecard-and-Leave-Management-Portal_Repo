-- ==============================================================================
-- Baseline Enterprise Data Seeding
-- ==============================================================================

-- 1. Users
INSERT OR REPLACE INTO users (id, name, email, role, avatar_initials, department, hourly_rate) VALUES
('usr_employee_01', 'Erin Employee', 'erin.employee@enterprise.com', 'EMPLOYEE', 'EE', 'Engineering', 28.50),
('usr_supervisor_01', 'Sarah Manager', 'sarah.manager@enterprise.com', 'SUPERVISOR', 'SM', 'Management', 45.00),
('usr_employee_02', 'David Chen', 'david.chen@enterprise.com', 'EMPLOYEE', 'DC', 'Operations', 26.00),
('usr_employee_03', 'Maria Garcia', 'maria.garcia@enterprise.com', 'EMPLOYEE', 'MG', 'Logistics', 24.50),
('usr_employee_04', 'Michael Scott', 'michael.scott@enterprise.com', 'EMPLOYEE', 'MS', 'Sales', 30.00),
('usr_employee_05', 'Jim Halpert', 'jim.halpert@enterprise.com', 'EMPLOYEE', 'JH', 'Sales', 27.50);

-- 2. Leave Balances
INSERT OR REPLACE INTO leave_balances (id, user_id, vacation_hours, sick_hours, unpaid_hours, accrual_rate_per_period) VALUES
('bal_01', 'usr_employee_01', 87.50, 40.00, 0.00, 3.75),
('bal_02', 'usr_supervisor_01', 120.00, 48.00, 0.00, 4.50),
('bal_03', 'usr_employee_02', 64.00, 32.00, 0.00, 3.75),
('bal_04', 'usr_employee_03', 45.00, 24.00, 0.00, 3.75),
('bal_05', 'usr_employee_04', 92.00, 36.00, 0.00, 3.75),
('bal_06', 'usr_employee_05', 78.00, 40.00, 0.00, 3.75);

-- 3. Pre-existing Timecards
INSERT OR REPLACE INTO timecards (id, user_id, pay_period_start, pay_period_end, total_hours, regular_hours, overtime_hours, double_time_hours, gross_pay_estimate, status, submitted_at) VALUES
('tc_current_01', 'usr_employee_01', '2023-10-16', '2023-10-31', 40.13, 40.00, 0.13, 0.00, 1144.28, 'DRAFT', NULL),
('tc_sub_01', 'usr_employee_02', '2023-10-01', '2023-10-15', 80.50, 80.00, 0.50, 0.00, 2099.50, 'SUBMITTED', '2023-10-15 18:00:00'),
('tc_sub_02', 'usr_employee_03', '2023-10-01', '2023-10-15', 79.00, 79.00, 0.00, 0.00, 1935.50, 'SUBMITTED', '2023-10-15 17:30:00');

-- 4. Timecard Entries for Current Timecard
INSERT OR REPLACE INTO timecard_entries (id, timecard_id, work_date, punch_in_1, punch_out_1, punch_in_2, punch_out_2, hours, regular_hours, overtime_hours, double_time_hours, notes) VALUES
('tce_01', 'tc_current_01', '2023-10-16', '08:57 AM', '01:00 PM', '01:30 PM', '05:32 PM', 8.08, 8.00, 0.08, 0.00, 'Regular shift'),
('tce_02', 'tc_current_01', '2023-10-17', '09:01 AM', '01:05 PM', '01:33 PM', '05:29 PM', 7.97, 7.97, 0.00, 0.00, 'Regular shift'),
('tce_03', 'tc_current_01', '2023-10-18', '08:55 AM', '12:30 PM', '01:00 PM', '05:30 PM', 8.08, 8.00, 0.08, 0.00, 'Regular shift'),
('tce_04', 'tc_current_01', '2023-10-19', '09:05 AM', '01:00 PM', '01:30 PM', '05:35 PM', 8.00, 8.00, 0.00, 0.00, 'Regular shift'),
('tce_05', 'tc_current_01', '2023-10-20', NULL, NULL, NULL, NULL, 8.00, 8.00, 0.00, 0.00, 'APPROVED LEAVE - 8h');

-- 5. Pending Leave Requests for Supervisor Review
INSERT OR REPLACE INTO leave_requests (id, user_id, leave_type, start_date, end_date, total_hours, comments, status, submitted_at) VALUES
('lr_01', 'usr_employee_04', 'Vacation', '2023-11-20', '2023-11-24', 40.00, 'Thanksgiving family vacation', 'PENDING', '2023-10-12 10:15:00'),
('lr_02', 'usr_employee_05', 'Sick Leave', '2023-10-23', '2023-10-23', 8.00, 'Doctor appointment', 'PENDING', '2023-10-12 11:30:00'),
('lr_03', 'usr_employee_02', 'Vacation', '2023-12-22', '2023-12-26', 24.00, 'Holiday time off', 'PENDING', '2023-10-12 14:00:00');

-- 6. Initial Audit Ledger Genesis Block
INSERT OR REPLACE INTO audit_ledger (id, event_type, actor_id, actor_email, payload, previous_hash, block_hash, timestamp) VALUES
('gen_block_01', 'SYSTEM_INITIALIZATION', 'usr_supervisor_01', 'system@enterprise.internal', '{"action":"GENESIS_INITIALIZATION"}', '0', 'GENESIS_CHAIN_BLOCK_HASH', '2023-10-01 00:00:00');
