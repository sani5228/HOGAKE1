/**
 * FASAL Shared Common Utilities
 * Provides reusable UI functions, toast notifications, auth checks, formatters, and modals.
 */

// Toast Notifications
function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 380px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `fasal-toast toast-${type}`;
    
    let bg = '#3B2C1F'; // soil
    let icon = '🌾';
    if (type === 'success') { bg = '#4E7A38'; icon = '✅'; }
    else if (type === 'error') { bg = '#A8442C'; icon = '⚠️'; }
    else if (type === 'warning') { bg = '#C97A2B'; icon = '🔔'; }

    toast.style.cssText = `
        background: ${bg};
        color: #fff;
        padding: 12px 18px;
        border-radius: 8px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        display: flex;
        align-items: center;
        gap: 10px;
        pointer-events: auto;
        animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        transition: opacity 0.25s ease, transform 0.25s ease;
    `;

    toast.innerHTML = `
        <span style="font-size: 1.1rem;">${icon}</span>
        <div style="flex: 1; line-height: 1.35;">${message}</div>
        <button style="background: none; border: none; color: rgba(255,255,255,0.7); cursor: pointer; font-size: 1.1rem; padding: 0 4px;" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Authentication & Role Checking Guard
function checkAuthGuard(requiredRole = null) {
    const token = api.getToken();
    const user = api.getCurrentUser();

    if (!token || !user) {
        if (requiredRole === 'admin') window.location.href = '/admin/login.html';
        else if (requiredRole === 'center') window.location.href = '/center/login.html';
        else window.location.href = '/farmer/login.html';
        return false;
    }

    if (requiredRole && user.role !== requiredRole) {
        showToast(`Unauthorized access. Expected role: ${requiredRole}`, 'error');
        setTimeout(() => {
            if (user.role === 'admin') window.location.href = '/admin/dashboard.html';
            else if (user.role === 'center') window.location.href = '/center/dashboard.html';
            else window.location.href = '/farmer/dashboard.html';
        }, 1200);
        return false;
    }

    return true;
}

// Formatters
function formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) return '₹0.00';
    return '₹ ' + Number(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
    } catch {
        return dateStr;
    }
}

function formatTime(timeStr) {
    if (!timeStr) return '';
    const parts = timeStr.split(':');
    if (parts.length < 2) return timeStr;
    let hour = parseInt(parts[0], 10);
    const min = parts[1];
    const ampm = hour >= 12 ? 'PM' : 'AM';
    hour = hour % 12 || 12;
    return `${hour}:${min} ${ampm}`;
}

function formatStatusBadge(status) {
    const s = (status || '').toUpperCase();
    let badgeClass = 'badge-pending';
    if (['SCHEDULED', 'ACTIVE', 'PAID', 'VERIFIED'].includes(s)) badgeClass = 'badge-scheduled';
    else if (['ARRIVED', 'PROCUREMENT', 'IN_PROGRESS', 'PENDING_VERIFICATION'].includes(s)) badgeClass = 'badge-arrived';
    else if (['COMPLETED'].includes(s)) badgeClass = 'badge-completed';
    else if (['CANCELLED', 'SUSPENDED', 'FAILED', 'REJECTED'].includes(s)) badgeClass = 'badge-cancelled';

    return `<span class="badge ${badgeClass}">${status.replace(/_/g, ' ')}</span>`;
}

// Modal Helpers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Global modal close on click backdrop
document.addEventListener('click', (e) => {
    if (e.target.classList && e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});
