/**
 * FASAL Central API Client
 * Authoritative module for all frontend-to-backend REST API communication.
 * Architecture.md §6: Pages never call fetch() directly.
 */

const API_BASE_URL = window.location.origin.includes(':5500') 
    ? 'http://localhost:5000/api' 
    : '/api';

class ApiClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    getToken() {
        return localStorage.getItem('fasal_token');
    }

    setToken(token) {
        if (token) {
            localStorage.setItem('fasal_token', token);
        } else {
            localStorage.removeItem('fasal_token');
        }
    }

    getCurrentUser() {
        const user = localStorage.getItem('fasal_user');
        return user ? JSON.parse(user) : null;
    }

    setCurrentUser(user) {
        if (user) {
            localStorage.setItem('fasal_user', JSON.stringify(user));
        } else {
            localStorage.removeItem('fasal_user');
        }
    }

    logout() {
        this.setToken(null);
        this.setCurrentUser(null);
        window.location.href = '/index.html';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                // If unauthorized, clear token and redirect if protected
                if (response.status === 401 && !endpoint.includes('/auth/')) {
                    this.logout();
                }
                const error = new Error(data.message || 'An error occurred');
                error.status = response.status;
                error.code = data.error_code || 'ERROR';
                error.data = data;
                throw error;
            }

            return data;
        } catch (err) {
            console.error(`[API Error] ${options.method || 'GET'} ${endpoint}:`, err);
            throw err;
        }
    }

    // ================= AUTHENTICATION =================
    async sendOtp(mobileNumber, purpose = 'LOGIN') {
        return this.request('/auth/otp/send', {
            method: 'POST',
            body: JSON.stringify({ mobile_number: mobileNumber, purpose })
        });
    }

    async verifyOtp(mobileNumber, otp) {
        const res = await this.request('/auth/otp/verify', {
            method: 'POST',
            body: JSON.stringify({ mobile_number: mobileNumber, otp })
        });
        if (res.data && res.data.token) {
            this.setToken(res.data.token);
            this.setCurrentUser(res.data.farmer || { role: res.data.role, mobile: mobileNumber });
        }
        return res;
    }

    async loginCenter(username, password) {
        const res = await this.request('/auth/center/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        if (res.data && res.data.token) {
            this.setToken(res.data.token);
            this.setCurrentUser({ ...res.data.center, role: 'center' });
        }
        return res;
    }

    async loginAdmin(username, password) {
        const res = await this.request('/auth/admin/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        if (res.data && res.data.token) {
            this.setToken(res.data.token);
            this.setCurrentUser({ ...res.data.admin, role: 'admin' });
        }
        return res;
    }

    async getMe() {
        return this.request('/auth/me');
    }

    // ================= FARMER =================
    async registerFarmer(data) {
        const res = await this.request('/farmer/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (res.data && res.data.token) {
            this.setToken(res.data.token);
            this.setCurrentUser({ ...res.data.farmer, role: 'farmer' });
        }
        return res;
    }

    async getFarmerProfile() {
        return this.request('/farmer/me');
    }

    async updateFarmerCrops(cropIds) {
        return this.request('/farmer/me/crops', {
            method: 'PUT',
            body: JSON.stringify({ crop_ids: cropIds })
        });
    }

    async getFarmerBookings(status = null) {
        const query = status ? `?status=${status}` : '';
        return this.request(`/farmer/me/bookings${query}`);
    }

    async getFarmerProcurements() {
        return this.request('/farmer/me/procurement-history');
    }

    // ================= BOOKING =================
    async getEligibleCrops() {
        return this.request('/bookings/eligible-crops');
    }

    async estimateBooking(cropId, quantity) {
        return this.request(`/bookings/estimate?crop_id=${cropId}&quantity=${quantity}`);
    }

    async createBooking(cropId, quantity, channel = 'WEB') {
        return this.request('/bookings', {
            method: 'POST',
            body: JSON.stringify({
                crop_id: cropId,
                expected_quantity_quintal: quantity,
                channel
            })
        });
    }

    async getBooking(bookingId) {
        return this.request(`/bookings/${bookingId}`);
    }

    async cancelBooking(bookingId) {
        return this.request(`/bookings/${bookingId}/cancel`, {
            method: 'POST'
        });
    }

    async rebookBooking(bookingId, newQuantity = null) {
        return this.request(`/bookings/${bookingId}/rebook`, {
            method: 'POST',
            body: JSON.stringify({ expected_quantity_quintal: newQuantity })
        });
    }

    // ================= PROCUREMENT CENTER =================
    async registerCenter(data) {
        return this.request('/center/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getCenterProfile() {
        return this.request('/center/me');
    }

    async updateCenterCapacity(data) {
        return this.request('/center/me/capacity', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async updateCenterCrops(cropIds) {
        return this.request('/center/me/crops', {
            method: 'PUT',
            body: JSON.stringify({ crop_ids: cropIds })
        });
    }

    async getCenterSchedule(date = null) {
        const q = date ? `?date=${date}` : '';
        return this.request(`/center/me/schedule${q}`);
    }

    async getCenterBookings(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/center/me/bookings${query ? '?' + query : ''}`);
    }

    async verifyToken(tokenNumber) {
        return this.request('/procurement/verify-token', {
            method: 'POST',
            body: JSON.stringify({ token_number: tokenNumber })
        });
    }

    async markArrival(bookingId) {
        return this.request(`/procurement/${bookingId}/arrival`, {
            method: 'POST'
        });
    }

    async recordProcurement(bookingId, actualWeightQuintal) {
        return this.request(`/procurement/${bookingId}/record`, {
            method: 'POST',
            body: JSON.stringify({ actual_weight_quintal: actualWeightQuintal })
        });
    }

    async updatePaymentStatus(paymentId, status, transactionRef = null, mode = null) {
        return this.request(`/procurement/payment/${paymentId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status, transaction_ref: transactionRef, mode })
        });
    }

    // ================= ADMIN =================
    async getAdminStats() {
        return this.request('/admin/stats');
    }

    async listFarmers(search = '', status = '') {
        const q = new URLSearchParams({ search, status }).toString();
        return this.request(`/admin/farmers?${q}`);
    }

    async setFarmerStatus(farmerId, status) {
        return this.request(`/admin/farmers/${farmerId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
    }

    async listCenters(search = '', status = '') {
        const q = new URLSearchParams({ search, status }).toString();
        return this.request(`/admin/centers?${q}`);
    }

    async verifyCenter(centerId, action) {
        return this.request(`/admin/centers/${centerId}/verify`, {
            method: 'PUT',
            body: JSON.stringify({ action })
        });
    }

    async listCrops(season = null, activeOnly = false) {
        const q = new URLSearchParams();
        if (season) q.append('season', season);
        q.append('active_only', activeOnly ? 'true' : 'false');
        return this.request(`/admin/crops?${q.toString()}`);
    }

    async createCrop(data) {
        return this.request('/admin/crops', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateCrop(cropId, data) {
        return this.request(`/admin/crops/${cropId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteCrop(cropId) {
        return this.request(`/admin/crops/${cropId}`, {
            method: 'DELETE'
        });
    }

    async listAllBookings(params = {}) {
        const q = new URLSearchParams(params).toString();
        return this.request(`/admin/bookings?${q}`);
    }

    async listAllProcurements(centerId = null) {
        const q = centerId ? `?center_id=${centerId}` : '';
        return this.request(`/admin/procurement-records${q}`);
    }

    async getCapacityReport(date = null) {
        const q = date ? `?date=${date}` : '';
        return this.request(`/admin/reports/capacity-utilization${q}`);
    }

    async getAuditLogs(limit = 50) {
        return this.request(`/admin/audit-log?limit=${limit}`);
    }

    // ================= IVR SIMULATOR =================
    async startIvrSession(callerMobile) {
        return this.request('/ivr/session/start', {
            method: 'POST',
            body: JSON.stringify({ caller_mobile: callerMobile })
        });
    }

    async selectIvrLanguage(sessionId, digit) {
        return this.request(`/ivr/session/${sessionId}/select-language`, {
            method: 'POST',
            body: JSON.stringify({ digit })
        });
    }

    async selectIvrCrop(sessionId, digit) {
        return this.request(`/ivr/session/${sessionId}/select-crop`, {
            method: 'POST',
            body: JSON.stringify({ digit })
        });
    }

    async enterIvrQuantity(sessionId, quantity) {
        return this.request(`/ivr/session/${sessionId}/enter-quantity`, {
            method: 'POST',
            body: JSON.stringify({ quantity })
        });
    }

    async confirmIvrBooking(sessionId) {
        return this.request(`/ivr/session/${sessionId}/confirm-booking`, {
            method: 'POST'
        });
    }

    async cancelIvrBooking(sessionId, bookingId) {
        return this.request(`/ivr/session/${sessionId}/cancel`, {
            method: 'POST',
            body: JSON.stringify({ booking_id: bookingId })
        });
    }

    async rebookIvrBooking(sessionId, bookingId) {
        return this.request(`/ivr/session/${sessionId}/rebook`, {
            method: 'POST',
            body: JSON.stringify({ booking_id: bookingId })
        });
    }

    // ================= CHATBOT & NOTIFICATIONS =================
    async getChatbotIntents() {
        return this.request('/chatbot/intents');
    }

    async queryChatbot(query) {
        return this.request('/chatbot/query', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    }

    async getNotifications(farmerId) {
        return this.request(`/notifications/${farmerId}`);
    }
}

// Export singleton instance
const api = new ApiClient();
window.api = api;
