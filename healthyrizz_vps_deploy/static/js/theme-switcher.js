/**
 * Theme Switcher for HealthyRizz
 * Handles switching between light and dark themes
 */

// Wait for DOM content to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme switcher
    initializeThemeSwitcher();
});

/**
 * Initialize the theme switcher functionality
 */
function initializeThemeSwitcher() {
    // Get theme toggle buttons
    const themeSwitcher = document.getElementById('theme-switcher');
    const mobileThemeSwitcher = document.getElementById('mobile-theme-switcher');
    const htmlElement = document.documentElement;
    const bodyElement = document.body;
    const currentTheme = localStorage.getItem('theme') || 'dark';
    
    // Set initial theme based on localStorage or default to dark
    setTheme(currentTheme);
    
    // Update toggle button appearance based on current theme
    updateThemeSwitcherAppearance(currentTheme);
    
    // Add click event listener to desktop theme toggle button
    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', function() {
            // Toggle between light and dark themes
            const newTheme = htmlElement.classList.contains('dark-theme') ? 'light' : 'dark';
            setTheme(newTheme);
            updateThemeSwitcherAppearance(newTheme);
            
            // Save theme preference to localStorage
            localStorage.setItem('theme', newTheme);
        });
    }
    
    // Add click event listener to mobile theme toggle button
    if (mobileThemeSwitcher) {
        mobileThemeSwitcher.addEventListener('click', function() {
            // Toggle between light and dark themes
            const newTheme = htmlElement.classList.contains('dark-theme') ? 'light' : 'dark';
            setTheme(newTheme);
            updateThemeSwitcherAppearance(newTheme);
            
            // Save theme preference to localStorage
            localStorage.setItem('theme', newTheme);
            
            // Close mobile menu if it's open
            const mobileMenu = document.getElementById('mobile-menu');
            if (mobileMenu && mobileMenu.classList.contains('show')) {
                mobileMenu.classList.remove('show');
                const mobileMenuButton = document.getElementById('mobile-menu-button');
                if (mobileMenuButton) {
                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                }
            }
        });
    }
}

/**
 * Set the theme for the website
 * @param {string} theme - The theme to set ('light' or 'dark')
 */
function setTheme(theme) {
    const htmlElement = document.documentElement;
    const bodyElement = document.body;
    
    if (theme === 'light') {
        htmlElement.classList.remove('dark-theme');
        htmlElement.classList.add('light-theme');
        bodyElement.classList.remove('dark-theme');
        bodyElement.classList.add('light-theme');
        
        // Handle logo switch if needed
        const logoElements = document.querySelectorAll('.logo-switch');
        logoElements.forEach(logo => {
            if (logo.dataset.darkSrc && logo.dataset.lightSrc) {
                logo.src = logo.dataset.lightSrc;
            }
        });
    } else {
        htmlElement.classList.remove('light-theme');
        htmlElement.classList.add('dark-theme');
        bodyElement.classList.remove('light-theme');
        bodyElement.classList.add('dark-theme');
        
        // Handle logo switch if needed
        const logoElements = document.querySelectorAll('.logo-switch');
        logoElements.forEach(logo => {
            if (logo.dataset.darkSrc && logo.dataset.lightSrc) {
                logo.src = logo.dataset.darkSrc;
            }
        });
    }
}

/**
 * Update the theme switcher button appearance based on current theme
 * @param {string} theme - The current theme ('light' or 'dark')
 */
function updateThemeSwitcherAppearance(theme) {
    // Update desktop theme switcher
    const themeSwitcher = document.getElementById('theme-switcher');
    const sunIcon = document.getElementById('theme-sun-icon');
    const moonIcon = document.getElementById('theme-moon-icon');
    
    if (themeSwitcher && sunIcon && moonIcon) {
        if (theme === 'light') {
            // Show moon icon when in light mode (to switch to dark)
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        } else {
            // Show sun icon when in dark mode (to switch to light)
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    }
    
    // Update mobile theme switcher
    const mobileSunIcon = document.getElementById('mobile-theme-sun-icon');
    const mobileMoonIcon = document.getElementById('mobile-theme-moon-icon');
    
    if (mobileSunIcon && mobileMoonIcon) {
        if (theme === 'light') {
            // Show moon icon when in light mode (to switch to dark)
            mobileSunIcon.classList.add('hidden');
            mobileMoonIcon.classList.remove('hidden');
        } else {
            // Show sun icon when in dark mode (to switch to light)
            mobileSunIcon.classList.remove('hidden');
            mobileMoonIcon.classList.add('hidden');
        }
    }
}
