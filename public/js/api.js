// ==============================================================================
// Enterprise Timecard & Leave Management Portal - Client API & Offline Engine
// ==============================================================================

const API_BASE = '/api/v1';

// Session state management
const AuthState = {
    getToken: () => localStorage.getItem('auth_token') || 'jwt_mock_token_usr_employee_01_EMPLOYEE',
    getUser: () => {
        const u = localStorage.getItem('auth_user');
        return u ? JSON.parse(u) : {
            id: 'usr_employee_01',
            name: 'Erin Employee',
            email: 'erin.employee@enterprise.com',
            role: 'EMPLOYEE',
            avatar_initials: 'EE'
        };
    },
    setUser: (user, token) => {
        if (user) localStorage.setItem('auth_user', JSON.stringify(user));
        if (token) localStorage.setItem('auth_token', token);
    },
    isOffline: () => !navigator.onLine
};

// ==============================================================================
// IndexedDB Offline Punch Storage
// ==============================================================================
const DB_NAME = 'TimecardOfflineDB';
const DB_VERSION = 1;
const STORE_NAME = 'offline_punches';

function openOfflineDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
            }
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function storeOfflinePunch(punchData) {
    const db = await openOfflineDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        store.add({
            ...punchData,
            client_timestamp: new Date().toISOString(),
            client_vector: Date.now()
        });
        tx.oncomplete = () => resolve(true);
        tx.onerror = () => reject(tx.error);
    });
}

async function getOfflinePunches() {
    const db = await openOfflineDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readonly');
        const store = tx.objectStore(STORE_NAME);
        const req = store.getAll();
        req.onsuccess = () => resolve(req.result || []);
        req.onerror = () => reject(req.error);
    });
}

async function clearOfflinePunches() {
    const db = await openOfflineDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        store.clear();
        tx.oncomplete = () => resolve(true);
        tx.onerror = () => reject(tx.error);
    });
}

// ==============================================================================
// REST Client Methods
// ==============================================================================
const Api = {
    async request(path, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };
        const token = AuthState.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const url = `${API_BASE}${path}`;
        try {
            const resp = await fetch(url, { ...options, headers });
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({ detail: 'API Request Failed' }));
                throw new Error(err.detail || `HTTP Error ${resp.status}`);
            }
            return await resp.json();
        } catch (e) {
            console.warn(`[Api.request] Failed to fetch ${url}:`, e);
            throw e;
        }
    },

    // Auth
    async login(email, role = 'EMPLOYEE') {
        const res = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, role })
        });
        AuthState.setUser(res.user, res.token);
        return res;
    },

    async getCurrentUser() {
        const user = AuthState.getUser();
        return await this.request(`/auth/me?user_id=${user.id}`);
    },

    async switchRole(role) {
        const res = await this.request(`/auth/switch-role?role=${encodeURIComponent(role)}`, {
            method: 'POST'
        });
        AuthState.setUser(res.user, res.token);
        return res;
    },

    // Punch & Sync
    async recordPunch(punchType) {
        const user = AuthState.getUser();
        const punchPayload = {
            punch_type: punchType,
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
            client_vector: Date.now(),
            offline_captured: !navigator.onLine
        };

        if (!navigator.onLine) {
            await storeOfflinePunch(punchPayload);
            return {
                punch_id: `offline_${Date.now()}`,
                status: 'stored_offline',
                punch_type: punchType,
                timestamp: punchPayload.timestamp,
                audit_hash: 'pending_sync'
            };
        }

        return await this.request(`/punches?user_id=${user.id}`, {
            method: 'POST',
            body: JSON.stringify(punchPayload)
        });
    },

    async syncOfflinePunches() {
        const user = AuthState.getUser();
        const pending = await getOfflinePunches();
        if (pending.length === 0) return { synced_count: 0 };

        const syncPayload = {
            punches: pending.map(p => ({
                punch_type: p.punch_type,
                timestamp: p.timestamp || p.client_timestamp,
                client_vector: p.client_vector || 1
            }))
        };

        const res = await this.request(`/punches/sync?user_id=${user.id}`, {
            method: 'POST',
            body: JSON.stringify(syncPayload)
        });

        await clearOfflinePunches();
        return res;
    },

    async getPunchStatus() {
        const user = AuthState.getUser();
        return await this.request(`/punches/status?user_id=${user.id}`);
    },

    async getTodayPunches() {
        const user = AuthState.getUser();
        return await this.request(`/punches/today?user_id=${user.id}`);
    },

    // Timecards
    async getCurrentTimecard() {
        const user = AuthState.getUser();
        return await this.request(`/timecards/current?user_id=${user.id}`);
    },

    async submitTimecard(timecardId) {
        const user = AuthState.getUser();
        return await this.request(`/timecards/submit?user_id=${user.id}`, {
            method: 'POST',
            body: JSON.stringify({ timecard_id: timecardId })
        });
    },

    // Leave
    async getLeaveBalances() {
        const user = AuthState.getUser();
        return await this.request(`/leave/balances?user_id=${user.id}`);
    },

    async submitLeaveRequest(data) {
        const user = AuthState.getUser();
        return await this.request(`/leave/requests?user_id=${user.id}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getMyLeaveRequests() {
        const user = AuthState.getUser();
        return await this.request(`/leave/requests/my?user_id=${user.id}`);
    },

    // Supervisor
    async getSupervisorSummary() {
        return await this.request('/supervisor/summary');
    },

    async getPendingTimesheets() {
        return await this.request('/supervisor/timesheets/pending');
    },

    async actOnTimesheet(id, action, comments = '') {
        const user = AuthState.getUser();
        return await this.request(`/supervisor/timesheets/${id}/action?supervisor_id=${user.id}`, {
            method: 'POST',
            body: JSON.stringify({ action, comments })
        });
    },

    async bulkApproveTimesheets() {
        const user = AuthState.getUser();
        return await this.request(`/supervisor/timesheets/bulk-approve?supervisor_id=${user.id}`, {
            method: 'POST'
        });
    },

    async getPendingLeave() {
        return await this.request('/supervisor/leave/pending');
    },

    async actOnLeave(id, action, comments = '') {
        const user = AuthState.getUser();
        return await this.request(`/supervisor/leave/${id}/action?supervisor_id=${user.id}`, {
            method: 'POST',
            body: JSON.stringify({ action, comments })
        });
    },

    async bulkApproveLeave() {
        const user = AuthState.getUser();
        return await this.request(`/supervisor/leave/bulk-approve?supervisor_id=${user.id}`, {
            method: 'POST'
        });
    }
};

// Online / Offline Connectivity Listener
window.addEventListener('online', async () => {
    console.log('[PWA Network] Back online. Synchronizing offline queue...');
    const banner = document.getElementById('offline-banner');
    if (banner) banner.style.display = 'none';
    try {
        const res = await Api.syncOfflinePunches();
        if (res.synced_count > 0) {
            console.log(`[PWA Network] Successfully synced ${res.synced_count} punches.`);
            if (typeof refreshDashboardData === 'function') refreshDashboardData();
        }
    } catch (e) {
        console.error('[PWA Network] Sync failed:', e);
    }
});

window.addEventListener('offline', () => {
    console.log('[PWA Network] Device is currently offline.');
    const banner = document.getElementById('offline-banner');
    if (banner) banner.style.display = 'flex';
});

// Expose globally
window.Api = Api;
window.AuthState = AuthState;
