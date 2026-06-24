// Sidebar toggle for mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');

    if (window.innerWidth <= 768 &&
        sidebar.classList.contains('open') &&
        !sidebar.contains(event.target) &&
        !toggleBtn.contains(event.target)) {
        sidebar.classList.remove('open');
    }
});

// Modal functions
function openAddLinkModal() {
    document.getElementById('addLinkModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// Search functionality with debounce
let searchTimeout;
document.querySelector('.search-box input')?.addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (this.value.length >= 2 || this.value.length === 0) {
            this.closest('form').submit();
        }
    }, 300);
});

// Handle link removal with confirmation
function removeLink(index) {
    if (confirm('Are you sure you want to remove this link?')) {
        window.location.href = `/remove_link/${index}`;
    }
}

// Add animation to new links
document.addEventListener('DOMContentLoaded', function() {
    const linkCards = document.querySelectorAll('.link-card');
    linkCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
});

// Clipboard functionality for link URLs
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = 'Link copied to clipboard!';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    });
}