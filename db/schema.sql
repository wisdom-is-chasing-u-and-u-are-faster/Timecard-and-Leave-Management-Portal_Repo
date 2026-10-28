-- Enterprise HRMS Platform Core Database Schema
-- Dialect: PostgreSQL 16 (Cloud SQL)

CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(32) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'EMPLOYEE',
    azure_ad_oid VARCHAR(128) UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employees (
    id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(32) UNIQUE NOT NULL,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(128) NOT NULL,
    department_id VARCHAR(64) REFERENCES departments(id) ON DELETE SET NULL,
    manager_id VARCHAR(64) REFERENCES employees(id) ON DELETE SET NULL,
    user_id VARCHAR(64) REFERENCES users(id) ON DELETE SET NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leave_balances (
    id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(64) NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type VARCHAR(64) NOT NULL,
    allocated NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    used NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    remaining NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    year INTEGER NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_emp_leave_year UNIQUE (employee_id, leave_type, year)
);

CREATE TABLE IF NOT EXISTS leave_requests (
    id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(64) NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type VARCHAR(64) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days NUMERIC(5, 2) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    approver_id VARCHAR(64) REFERENCES employees(id) ON DELETE SET NULL,
    approver_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance_logs (
    id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(64) NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    check_in TIMESTAMP WITH TIME ZONE NOT NULL,
    check_out TIMESTAMP WITH TIME ZONE,
    total_hours NUMERIC(5, 2) DEFAULT 0.00,
    status VARCHAR(32) NOT NULL DEFAULT 'IN_PROGRESS',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_emp_work_date UNIQUE (employee_id, work_date)
);

CREATE TABLE IF NOT EXISTS document_vault (
    id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(64) NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    gcs_uri VARCHAR(1024) NOT NULL,
    category VARCHAR(64) NOT NULL,
    mime_type VARCHAR(128) NOT NULL,
    file_size INTEGER NOT NULL,
    is_encrypted BOOLEAN NOT NULL DEFAULT TRUE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payroll_records (
    id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(64) NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL,
    base_salary NUMERIC(12, 2) NOT NULL,
    allowances NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    deductions NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    net_pay NUMERIC(12, 2) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PAID',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_emp_payroll_month UNIQUE (employee_id, month)
);

CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance_logs(employee_id);
CREATE INDEX IF NOT EXISTS idx_documents_employee ON document_vault(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_employee ON payroll_records(employee_id);
