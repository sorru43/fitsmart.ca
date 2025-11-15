/**
 * Service Worker Registration
 * This script registers the service worker without causing page reloads
 */

(function() {
    'use strict';
    
    console.log('🔧 Registering Service Worker');
    
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/service-worker.js', {
            scope: '/'
        }).then(registration => {
            console.log('✅ Service worker registered:', registration.scope);
            
            // Force activation if there's a waiting worker
            if (registration.waiting) {
                console.log('🚀 Forcing activation of waiting service worker');
                registration.waiting.postMessage({ type: 'SKIP_WAITING' });
            }
            
            // Listen for updates
            registration.addEventListener('updatefound', () => {
                console.log('🔄 Service worker update found');
                const newWorker = registration.installing;
                
                newWorker.addEventListener('statechange', () => {
                    console.log('📊 Service worker state:', newWorker.state);
                    if (newWorker.state === 'installed') {
                        console.log('✅ New service worker installed - forcing activation');
                        newWorker.postMessage({ type: 'SKIP_WAITING' });
                    }
                });
            });
            
        }).catch(error => {
            console.error('❌ Service worker registration failed:', error);
        });
    } else {
        console.log('⚠️ Service Worker not supported');
    }
    
})(); 