/**
 * Enterprise HRMS Client API SDK
 * Connects UI views to backend REST endpoints
 */
const API_BASE = '/api/v1';

const HRMS_API = {
  // Container & Database Health
  async getHealth() {
    const res = await fetch('/health');
    return res.json();
  },

  // Auth & Session
  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`);
    return res.json();
  },

  // Dashboard Metrics
  async getDashboardMetrics() {
    const res = await fetch(`${API_BASE}/dashboard/metrics`);
    return res.json();
  },

  // Employee Directory
  async getEmployees(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/employees?${query}`);
    return res.json();
  },

  async getEmployeeById(id) {
    const res = await fetch(`${API_BASE}/employees/${id}`);
    return res.json();
  },

  async createEmployee(data) {
    const res = await fetch(`${API_BASE}/employees`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create employee');
    }
    return res.json();
  },

  // Leave Management
  async getLeaveBalances(employeeId) {
    const q = employeeId ? `?employeeId=${employeeId}` : '';
    const res = await fetch(`${API_BASE}/leave/balances${q}`);
    return res.json();
  },

  async getLeaveRequests(employeeId) {
    const q = employeeId ? `?employeeId=${employeeId}` : '';
    const res = await fetch(`${API_BASE}/leave/requests${q}`);
    return res.json();
  },

  async submitLeaveRequest(data) {
    const res = await fetch(`${API_BASE}/leave/requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to submit leave request');
    }
    return res.json();
  },

  async updateLeaveStatus(id, status, comment = '') {
    const res = await fetch(`${API_BASE}/leave/requests/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, comment }),
    });
    return res.json();
  },

  // Attendance & Timesheet
  async getAttendance(employeeId) {
    const q = employeeId ? `?employeeId=${employeeId}` : '';
    const res = await fetch(`${API_BASE}/attendance${q}`);
    return res.json();
  },

  async clockIn(employeeId) {
    const res = await fetch(`${API_BASE}/attendance/check-in`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employeeId }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to clock in');
    }
    return res.json();
  },

  async clockOut(employeeId) {
    const res = await fetch(`${API_BASE}/attendance/check-out`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employeeId }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to clock out');
    }
    return res.json();
  },

  // Document Vault
  async getDocuments(employeeId, category) {
    let url = `${API_BASE}/documents?`;
    if (employeeId) url += `employeeId=${employeeId}&`;
    if (category) url += `category=${category}&`;
    const res = await fetch(url);
    return res.json();
  },

  async getUploadUrl(data) {
    const res = await fetch(`${API_BASE}/documents/upload-url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async getDownloadUrl(id) {
    const res = await fetch(`${API_BASE}/documents/${id}/download-url`);
    return res.json();
  },

  // Payroll
  async getPayrollLedger(employeeId, year) {
    let url = `${API_BASE}/payroll/ledger?`;
    if (employeeId) url += `employeeId=${employeeId}&`;
    if (year) url += `year=${year}&`;
    const res = await fetch(url);
    return res.json();
  },
};

window.HRMS_API = HRMS_API;
