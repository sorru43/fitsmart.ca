/**
 * Simplified Service Worker Update Script
 * This script ensures the service worker is up to date without causing refreshes
 */

(function() {
    'use strict';
    
    console.log('🔄 Service Worker Update Script Loaded');
    
    // Function to update service worker if needed
    function updateServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistration().then(registration => {
                if (registration) {
                    console.log('📋 Checking for service worker updates...');
                    registration.update();
                    
                    // Force activation if there's a waiting worker
                    if (registration.waiting) {
                        registration.waiting.postMessage({ type: 'SKIP_WAITING' });
                        console.log('🚀 Forced service worker activation');
                    }
                }
            });
        }
    }
    
    // Execute once on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 DOM loaded - updating service worker');
            updateServiceWorker();
        });
    } else {
        console.log('🚀 DOM already loaded - updating service worker');
        updateServiceWorker();
    }
    
    // Add global function for manual trigger
    window.updateServiceWorker = updateServiceWorker;
    
})(); 