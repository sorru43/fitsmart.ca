// Mobile App Menu Controller
document.addEventListener('DOMContentLoaded', function() {
    initializeMobileAppMenu();
});

function initializeMobileAppMenu() {
    const mobileMenu = document.getElementById('mobile-app-menu');
    const menuItems = document.querySelectorAll('.mobile-app-menu-item');
    
    if (!mobileMenu) return;
    
    // Show menu on mobile devices
    if (window.innerWidth <= 768) {
        mobileMenu.classList.add('show');
    }
    
    // Update active state based on current page
    updateActiveMenuItem();
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            mobileMenu.classList.add('show');
        } else {
            mobileMenu.classList.remove('show');
        }
    });
    
    // Add ripple effect to menu items
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            addRippleEffect(this, e);
        });
    });
    
    // Add haptic feedback for supported devices
    if ('vibrate' in navigator) {
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                navigator.vibrate(50); // Short vibration
            });
        });
    }
}

function updateActiveMenuItem() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.mobile-app-menu-item');
    
    menuItems.forEach(item => {
        item.classList.remove('active');
        
        const href = item.getAttribute('href');
        if (href && href !== '#') {
            // Extract path from href
            const linkPath = new URL(href, window.location.origin).pathname;
            
            if (currentPath === linkPath || 
                (currentPath === '/' && linkPath === '/') ||
                (currentPath.startsWith('/meal-plans') && linkPath.includes('meal-plans')) ||
                (currentPath.startsWith('/profile') && linkPath.includes('profile')) ||
                (currentPath.startsWith('/meal-calculator') && linkPath.includes('meal-calculator'))) {
                item.classList.add('active');
            }
        }
    });
}

function addRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        background-color: rgba(255, 255, 255, 0.3);
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        pointer-events: none;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Add notification badge functionality
function updateNotificationBadge(menuItem, count) {
    const existingBadge = menuItem.querySelector('.mobile-app-menu-badge');
    
    if (count > 0) {
        if (!existingBadge) {
            const badge = document.createElement('span');
            badge.className = 'mobile-app-menu-badge';
            badge.textContent = count > 99 ? '99+' : count;
            menuItem.appendChild(badge);
        } else {
            existingBadge.textContent = count > 99 ? '99+' : count;
        }
    } else if (existingBadge) {
        existingBadge.remove();
    }
}

// Export functions for global use
window.updateMobileMenuNotification = updateNotificationBadge;
window.updateActiveMenuItem = updateActiveMenuItem; 