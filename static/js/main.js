/**
 * EFYS - Main JavaScript
 * Genel yardımcı fonksiyonlar
 */

// Sidebar toggle for mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

// Submenu toggle
function toggleSubmenu(element) {
    const submenu = element.nextElementSibling;
    const isExpanded = element.classList.contains('expanded');
    
    // Close all other submenus
    document.querySelectorAll('.nav-item.expanded').forEach(item => {
        if (item !== element) {
            item.classList.remove('expanded');
            const otherSubmenu = item.nextElementSibling;
            if (otherSubmenu && otherSubmenu.classList.contains('nav-submenu')) {
                otherSubmenu.style.maxHeight = '0';
            }
        }
    });
    
    // Toggle current submenu
    if (isExpanded) {
        element.classList.remove('expanded');
        if (submenu) submenu.style.maxHeight = '0';
    } else {
        element.classList.add('expanded');
        if (submenu) submenu.style.maxHeight = submenu.scrollHeight + 'px';
    }
}

// Format number with Turkish locale
function formatNumber(num, decimals = 0) {
    return new Intl.NumberFormat('tr-TR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
}

// Format currency (TRY)
function formatCurrency(amount) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(amount);
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('tr-TR');
}

// Format datetime
function formatDateTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString('tr-TR');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    const container = document.getElementById('toast-container') || document.body;
    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Confirm dialog
function confirmAction(message) {
    return confirm(message);
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Panoya kopyalandı', 'success');
    } catch (err) {
        showToast('Kopyalama başarısız', 'error');
    }
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-expand active menu
    const activeItem = document.querySelector('.nav-item.active');
    if (activeItem) {
        activeItem.classList.add('expanded');
        const submenu = activeItem.nextElementSibling;
        if (submenu && submenu.classList.contains('nav-submenu')) {
            submenu.style.maxHeight = submenu.scrollHeight + 'px';
        }
    }
});
