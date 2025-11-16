// Performance Optimizer - Load non-critical resources asynchronously
(function() {
    'use strict';
    
    // Function to load CSS asynchronously
    function loadCSS(href) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.media = 'print';
        link.onload = function() {
            this.media = 'all';
        };
        document.head.appendChild(link);
    }
    
    // Load non-critical CSS after page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            loadNonCriticalResources();
        });
    } else {
        loadNonCriticalResources();
    }
    
    function loadNonCriticalResources() {
        // These are already loaded via preload, just ensure they're applied
        // The browser will handle preloaded resources automatically
    }
    
    // Optimize image loading
    if ('loading' in HTMLImageElement.prototype) {
        // Native lazy loading supported
        var images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(function(img) {
            img.src = img.dataset.src || img.src;
        });
    } else {
        // Fallback for browsers without native lazy loading
        var script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
        document.body.appendChild(script);
    }
})();

