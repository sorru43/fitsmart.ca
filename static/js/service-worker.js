// Service Worker for FitSmart PWA - PERMANENT FIX VERSION
const CACHE_VERSION = 'v3.1.0'; // Updated version to force cache refresh
const CACHE_NAME = `fitsmart-${CACHE_VERSION}`;
const CSS_CACHE_NAME = `fitsmart-css-${CACHE_VERSION}`;

// Files that should NEVER be cached (always network-first)
const NEVER_CACHE = [
  '/static/css/main.min.css'  // Main bundled CSS - always fresh
];

// Files that can be cached normally
const urlsToCache = [
  '/',
  '/static/js/main.js',
  '/static/js/testimonials.js',
  '/static/js/pwa-install.js',
  '/static/js/mobile-app-menu.js',
  '/static/images/logo_20250629_170145_black_bg.gif',
  '/static/images/FSSAI.png',
  '/static/favicon.ico',
  '/static/manifest.json'
  // Note: main.min.css is NOT cached (network-first strategy)
];

// Force immediate activation and skip waiting
self.addEventListener('install', event => {
    console.log('🔄 New Service Worker installing (Permanent Fix)...');
    event.waitUntil(
        Promise.all([
            caches.open(CACHE_NAME),
            caches.open(CSS_CACHE_NAME)
        ]).then(([mainCache, cssCache]) => {
            console.log('✅ Caches opened');
            // Only cache non-CSS files
            return mainCache.addAll(urlsToCache);
        }).then(() => {
            // Force immediate activation
            return self.skipWaiting();
        })
    );
});

// Force immediate takeover and clear ALL old caches
self.addEventListener('activate', event => {
    console.log('🚀 Service Worker activating (Permanent Fix)...');
    event.waitUntil(
        // Delete ALL old caches including CSS caches
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName !== CSS_CACHE_NAME) {
                        console.log('🗑️ Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            // Force immediate takeover of all clients
            return self.clients.claim();
        })
    );
});

// PERMANENT FIX: Network-first strategy for CSS files, cache-first for others
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    const requestUrl = event.request.url;
    
    // PERMANENT FIX: CSS files - ALWAYS network-first, never cache
    if (NEVER_CACHE.some(cssFile => requestUrl.includes(cssFile))) {
        console.log('🎯 CSS file detected, using network-first:', requestUrl);
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Always return fresh CSS from network
                    return response;
                })
                .catch(() => {
                    // Only fallback to cache if network completely fails
                    console.log('⚠️ Network failed for CSS, using cache fallback:', requestUrl);
                    return caches.match(event.request);
                })
        );
        return;
    }
    
    // Static assets (non-CSS) - network-first with caching
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // If network request succeeds, cache it
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // If network fails, try cache
                    return caches.match(event.request);
                })
        );
    }
    
    // For other requests, use cache-first
    else {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    return response || fetch(event.request);
                })
        );
    }
});

// Listen for messages from the main thread
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    // PERMANENT FIX: Handle CSS refresh requests
    if (event.data && event.data.type === 'REFRESH_CSS') {
        console.log('🔄 CSS refresh requested');
        // Clear CSS cache immediately
        caches.open(CSS_CACHE_NAME).then(cache => {
            cache.keys().then(requests => {
                requests.forEach(request => {
                    cache.delete(request);
                });
            });
        });
    }
});

// Background sync for offline functionality
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Handle background sync tasks
  console.log('Background sync triggered');
  return Promise.resolve();
}

// Push notification handling
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'New notification from FitSmart',
    icon: '/static/images/pwa_icons/icon-144x144.png',
    badge: '/static/images/pwa_icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/static/images/pwa_icons/icon-72x72.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/images/pwa_icons/icon-72x72.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('FitSmart', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
}); 