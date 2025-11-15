// Tracking Pixels Management for fitsmart.ca
// Handles Facebook Pixel (Meta Pixel) and Google Analytics

class TrackingPixels {
    constructor() {
        this.fbq = null;
        this.gtag = null;
        this.isInitialized = false;
    }

    // Initialize Facebook Pixel
    initFacebookPixel(pixelId) {
        if (!pixelId || this.fbq) return;

        // Facebook Pixel Code
        !function(f,b,e,v,n,t,s)
        {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};
        if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
        n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t,s)}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
        
        fbq('init', pixelId);
        fbq('track', 'PageView');
        
        this.fbq = fbq;
        console.log('Facebook Pixel initialized with ID:', pixelId);
    }

    // Initialize Google Analytics
    initGoogleAnalytics(measurementId) {
        if (!measurementId || this.gtag) return;

        // Google Analytics Code
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', measurementId);
        
        this.gtag = gtag;
        console.log('Google Analytics initialized with ID:', measurementId);
    }

    // Initialize all tracking pixels
    init(pixelSettings) {
        if (this.isInitialized) return;

        const { facebook_pixel_id, google_analytics_id } = pixelSettings;

        // Initialize Facebook Pixel
        if (facebook_pixel_id) {
            this.initFacebookPixel(facebook_pixel_id);
        }

        // Initialize Google Analytics
        if (google_analytics_id) {
            this.initGoogleAnalytics(google_analytics_id);
        }

        this.isInitialized = true;
    }

    // Facebook Pixel Events
    trackPageView() {
        if (this.fbq) {
            this.fbq('track', 'PageView');
        }
    }

    trackPurchase(value, currency = 'INR') {
        if (this.fbq) {
            this.fbq('track', 'Purchase', {
                value: value,
                currency: currency
            });
        }
        if (this.gtag) {
            this.gtag('event', 'purchase', {
                value: value,
                currency: currency
            });
        }
    }

    trackAddToCart(value, currency = 'INR') {
        if (this.fbq) {
            this.fbq('track', 'AddToCart', {
                value: value,
                currency: currency
            });
        }
        if (this.gtag) {
            this.gtag('event', 'add_to_cart', {
                value: value,
                currency: currency
            });
        }
    }

    trackInitiateCheckout(value, currency = 'INR') {
        if (this.fbq) {
            this.fbq('track', 'InitiateCheckout', {
                value: value,
                currency: currency
            });
        }
        if (this.gtag) {
            this.gtag('event', 'begin_checkout', {
                value: value,
                currency: currency
            });
        }
    }

    trackLead() {
        if (this.fbq) {
            this.fbq('track', 'Lead');
        }
        if (this.gtag) {
            this.gtag('event', 'generate_lead');
        }
    }

    trackContact() {
        if (this.fbq) {
            this.fbq('track', 'Contact');
        }
        if (this.gtag) {
            this.gtag('event', 'contact');
        }
    }

    trackNewsletterSignup() {
        if (this.fbq) {
            this.fbq('track', 'CompleteRegistration');
        }
        if (this.gtag) {
            this.gtag('event', 'sign_up', {
                method: 'newsletter'
            });
        }
    }

    trackCustomEvent(eventName, parameters = {}) {
        if (this.fbq) {
            this.fbq('track', eventName, parameters);
        }
        if (this.gtag) {
            this.gtag('event', eventName, parameters);
        }
    }
}

// Global instance
window.trackingPixels = new TrackingPixels();

// Initialize tracking pixels when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get tracking settings from data attributes or global variables
    const pixelSettings = {
        facebook_pixel_id: window.FACEBOOK_PIXEL_ID || null,
        google_analytics_id: window.GOOGLE_ANALYTICS_ID || null
    };

    // Initialize tracking pixels
    window.trackingPixels.init(pixelSettings);
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TrackingPixels;
}
