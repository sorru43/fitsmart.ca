/**
 * SIMPLIFIED CSS Loading Fix for FitSmart
 * This script ensures CSS loads fresh without causing multiple refreshes
 */

(function() {
    'use strict';
    
    // Load fresh CSS once on page load
    function loadFreshCSS() {
        console.log('🎯 Loading fresh CSS...');
        
        const links = document.querySelectorAll('link[rel="stylesheet"]');
        let updatedCount = 0;
        
        links.forEach(link => {
            if (link.href.includes('/static/css/')) {
                const url = new URL(link.href);
                const timestamp = Date.now();
                
                // Add cache-busting parameters
                url.searchParams.set('_fresh', timestamp);
                url.searchParams.set('v', '3.0.0');
                
                // Create new link element with fresh URL
                const newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = url.toString();
                
                // Replace old link
                link.parentNode.replaceChild(newLink, link);
                updatedCount++;
            }
        });
        
        console.log(`✅ Updated ${updatedCount} CSS files`);
    }
    
    // Force Service Worker update once
    function forceServiceWorkerUpdate() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistration().then(registration => {
                if (registration && registration.waiting) {
                    registration.waiting.postMessage({ type: 'SKIP_WAITING' });
                    console.log('🚀 Forced Service Worker activation');
                }
            });
        }
    }
    
    // Initialize only once when DOM is ready
    function initialize() {
        console.log('🚀 Initializing CSS fix...');
        
        // Force Service Worker update
        forceServiceWorkerUpdate();
        
        // Load fresh CSS once
        loadFreshCSS();
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // DOM is already ready
        initialize();
    }
    
    // Expose function globally for manual use
    window.loadFreshCSS = loadFreshCSS;
    
    console.log('🎯 CSS Fix script loaded successfully');
})(); 