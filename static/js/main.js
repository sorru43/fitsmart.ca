// Initialize promotional banner functionality
function initializePromoBanner() {
    const banner = document.getElementById('promo-banner');
    const closeButton = document.getElementById('close-banner');
    
    if (banner && closeButton) {
        // Set banner background and text colors if specified in data attributes
        const bgColor = banner.getAttribute('data-bg-color');
        const textColor = banner.getAttribute('data-text-color');
        
        if (bgColor) {
            banner.style.backgroundColor = bgColor;
        }
        
        if (textColor) {
            banner.style.color = textColor;
        }
        
        // Handle closing the banner
        closeButton.addEventListener('click', function() {
            banner.style.height = banner.offsetHeight + 'px';
            banner.style.overflow = 'hidden';
            
            setTimeout(() => {
                banner.style.height = '0';
                banner.style.padding = '0';
                banner.style.margin = '0';
                banner.style.opacity = '0';
                
                setTimeout(() => {
                    banner.style.display = 'none';
                }, 400);
            }, 10);
            
            // Store in session that the banner was closed
            localStorage.setItem('banner_closed', 'true');
        });
        
        // Check if banner was closed in this session
        if (localStorage.getItem('banner_closed') === 'true') {
            banner.style.display = 'none';
        }
    }
}

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any components that need JavaScript
    
    // Initialize promotional banner if present
    initializePromoBanner();

    // Mobile Menu Toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    
    function closeMobileMenu() {
        if (mobileMenu) {
            mobileMenu.classList.remove('show');
            mobileMenuButton?.setAttribute('aria-expanded', 'false');
            
            // Reset icon
            const icon = mobileMenuButton?.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        }
    }
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
            const isExpanded = mobileMenu.classList.contains('show');
            mobileMenuButton.setAttribute('aria-expanded', isExpanded);
            
            // Change icon based on menu state
            const icon = mobileMenuButton.querySelector('i');
            if (icon) {
                if (isExpanded) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }
    
    // Mobile Menu Close Button
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMobileMenu);
    }
    
    // Close mobile menu when any link inside it is clicked
    if (mobileMenu) {
        const mobileMenuLinks = mobileMenu.querySelectorAll('a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Add a small delay to allow navigation to start
                setTimeout(closeMobileMenu, 100);
            });
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (mobileMenu && mobileMenu.classList.contains('show') && 
            !mobileMenu.contains(event.target) && 
            !mobileMenuButton?.contains(event.target)) {
            closeMobileMenu();
        }
    });
    
    // Profile Dropdown Toggle
    const profileDropdownToggle = document.getElementById('profile-dropdown-toggle');
    const profileDropdown = document.getElementById('profile-dropdown');
    
    if (profileDropdownToggle && profileDropdown) {
        profileDropdownToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            profileDropdown.classList.toggle('show');
            const isExpanded = profileDropdown.classList.contains('show');
            profileDropdownToggle.setAttribute('aria-expanded', isExpanded);
            
            if (isExpanded) {
                document.body.classList.add('has-dropdown-open');
            } else {
                document.body.classList.remove('has-dropdown-open');
            }
        });
    }
    
    // Close profile dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (profileDropdown && profileDropdown.classList.contains('show') && 
            !profileDropdown.contains(event.target) && 
            !profileDropdownToggle.contains(event.target)) {
            profileDropdown.classList.remove('show');
            profileDropdownToggle.setAttribute('aria-expanded', 'false');
            document.body.classList.remove('has-dropdown-open');
        }
    });

    // Enable all Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            // Create a new bootstrap alert instance and close it
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Handle quantity increment/decrement in product pages
    const quantityControls = document.querySelectorAll('.quantity-control');
    quantityControls.forEach(control => {
        const input = control.querySelector('input');
        const incrementBtn = control.querySelector('.increment');
        const decrementBtn = control.querySelector('.decrement');

        if (incrementBtn && decrementBtn && input) {
            incrementBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                if (currentValue < parseInt(input.getAttribute('max'))) {
                    input.value = currentValue + 1;
                }
            });

            decrementBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                if (currentValue > parseInt(input.getAttribute('min'))) {
                    input.value = currentValue - 1;
                }
            });
        }
    });
    
    // Close promotional banner if present
    const closeBannerButton = document.getElementById('close-banner');
    const promoBanner = document.getElementById('promo-banner');
    
    if (closeBannerButton && promoBanner) {
        closeBannerButton.addEventListener('click', function() {
            promoBanner.style.display = 'none';
        });
    }
});

// Function to initialize the sample database (for development/testing)
function initializeDatabase() {
    fetch('/init_db')
        .then(response => response.json())
        .then(data => {
            console.log('Database initialized:', data);
            alert('Sample data has been loaded successfully. Refresh the page to see the meals.');
        })
        .catch(error => {
            console.error('Error initializing database:', error);
            alert('Error initializing database. See console for details.');
        });
}
