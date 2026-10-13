-- ==============================================================================
-- Enterprise Timecard & Leave Management Portal - Relational Database Schema
-- Compatible with SQLite 3 and PostgreSQL 16
-- ==============================================================================

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('EMPLOYEE', 'SUPERVISOR', 'ADMIN')),
    avatar_initials TEXT NOT NULL,
    department TEXT DEFAULT 'Engineering',
    hourly_rate REAL DEFAULT 25.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS punches (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    punch_type TEXT NOT NULL CHECK(punch_type IN ('CLOCK_IN', 'CLOCK_OUT', 'MEAL_IN', 'MEAL_OUT')),
    timestamp TIMESTAMP NOT NULL,
    client_vector INTEGER DEFAULT 1,
    offline_captured BOOLEAN DEFAULT 0,
    audit_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_punches_user_time ON punches(user_id, timestamp);

CREATE TABLE IF NOT EXISTS timecards (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    total_hours REAL DEFAULT 0.0,
    regular_hours REAL DEFAULT 0.0,
    overtime_hours REAL DEFAULT 0.0,
    double_time_hours REAL DEFAULT 0.0,
    gross_pay_estimate REAL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'DRAFT' CHECK(status IN ('DRAFT', 'SUBMITTED', 'APPROVED', 'DENIED')),
    submitted_at TIMESTAMP,
    action_by TEXT REFERENCES users(id),
    action_at TIMESTAMP,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_timecards_user_period ON timecards(user_id, pay_period_start);

CREATE TABLE IF NOT EXISTS timecard_entries (
    id TEXT PRIMARY KEY,
    timecard_id TEXT NOT NULL REFERENCES timecards(id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    punch_in_1 TEXT,
    punch_out_1 TEXT,
    punch_in_2 TEXT,
    punch_out_2 TEXT,
    hours REAL DEFAULT 0.0,
    regular_hours REAL DEFAULT 0.0,
    overtime_hours REAL DEFAULT 0.0,
    double_time_hours REAL DEFAULT 0.0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS leave_balances (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL REFERENCES users(id),
    vacation_hours REAL DEFAULT 80.0,
    sick_hours REAL DEFAULT 40.0,
    unpaid_hours REAL DEFAULT 0.0,
    accrual_rate_per_period REAL DEFAULT 3.75,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leave_requests (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    leave_type TEXT NOT NULL CHECK(leave_type IN ('Vacation', 'Sick Leave', 'Unpaid Time Off')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_hours REAL NOT NULL,
    comments TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'APPROVED', 'DENIED')),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_by TEXT REFERENCES users(id),
    action_at TIMESTAMP,
    action_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_leave_requests_user ON leave_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status);

CREATE TABLE IF NOT EXISTS audit_ledger (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    actor_email TEXT NOT NULL,
    payload TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    block_hash TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS outbox_events (
    id TEXT PRIMARY KEY,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    target_system TEXT NOT NULL CHECK(target_system IN ('WORKDAY', 'SAP', 'ADP', 'RABBITMQ')),
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'PROCESSED', 'FAILED')),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
