/**
 * Firebase Utility Functions
 * Provides helper functions for Firebase services
 */

// Check if Firebase is initialized
function isFirebaseInitialized() {
    return typeof window.firebaseApp !== 'undefined' && window.firebaseApp !== null;
}

// Get Firebase Analytics instance
function getFirebaseAnalytics() {
    if (isFirebaseInitialized()) {
        return window.firebaseAnalytics;
    }
    console.warn('Firebase Analytics not initialized');
    return null;
}

// Log custom event to Firebase Analytics
function logFirebaseEvent(eventName, eventParams = {}) {
    if (typeof window.firebaseAnalytics !== 'undefined' && window.firebaseAnalytics) {
        try {
            // Use the logEvent function from the analytics module
            // This will be available after Firebase is initialized
            if (typeof window.logFirebaseEventDirect === 'function') {
                window.logFirebaseEventDirect(window.firebaseAnalytics, eventName, eventParams);
            } else {
                // Fallback: import logEvent dynamically
                import('https://www.gstatic.com/firebasejs/10.11.1/firebase-analytics.js')
                    .then(({ logEvent }) => {
                        logEvent(window.firebaseAnalytics, eventName, eventParams);
                    })
                    .catch(error => {
                        console.error('Error logging Firebase event:', error);
                    });
            }
        } catch (error) {
            console.error('Error logging Firebase event:', error);
        }
    } else {
        console.warn('Firebase Analytics not initialized. Event not logged:', eventName);
    }
}

// Track page view
function trackPageView(pagePath, pageTitle) {
    logFirebaseEvent('page_view', {
        page_path: pagePath,
        page_title: pageTitle
    });
}

// Track user action
function trackUserAction(action, category = 'user_interaction', value = null) {
    logFirebaseEvent('user_action', {
        action: action,
        category: category,
        value: value
    });
}

// Track purchase
function trackPurchase(value, currency = 'CAD', items = []) {
    logFirebaseEvent('purchase', {
        value: value,
        currency: currency,
        items: items
    });
}

// Track subscription
function trackSubscription(planName, value, currency = 'CAD') {
    logFirebaseEvent('subscription', {
        plan_name: planName,
        value: value,
        currency: currency
    });
}

// Export functions
if (typeof window !== 'undefined') {
    window.firebaseUtils = {
        isFirebaseInitialized,
        getFirebaseAnalytics,
        logFirebaseEvent,
        trackPageView,
        trackUserAction,
        trackPurchase,
        trackSubscription
    };
}

