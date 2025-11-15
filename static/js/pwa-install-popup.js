// PWA Install Popup Handler
// This file provides the missing dismissInstallPopup function for the old PWA popup system

// Global function to dismiss the PWA install popup
function dismissInstallPopup() {
    const popup = document.getElementById('pwa-install-popup');
    if (popup) {
        popup.classList.add('hidden');
        popup.setAttribute('aria-hidden', 'true');
    }
}

// Global function to show the PWA install popup
function showPWAInstallPopup() {
    const popup = document.getElementById('pwa-install-popup');
    if (popup) {
        popup.classList.remove('hidden');
        popup.setAttribute('aria-hidden', 'false');
    } else {
        // Fallback to the new PWA system if old popup doesn't exist
        if (window.pwaInstallPrompt) {
            window.pwaInstallPrompt.showInstallPrompt();
        } else if (typeof showPWAInstallPopup === 'function') {
            // Call the new system's function
            window.showPWAInstallPopup();
        }
    }
}

// Global function to install PWA (for compatibility)
function installPWA() {
    // Try the new PWA system first
    if (window.pwaInstallPrompt) {
        window.pwaInstallPrompt.installApp();
    } else if (window.deferredPrompt) {
        // Fallback to basic install prompt
        window.deferredPrompt.prompt();
        window.deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
                dismissInstallPopup();
            } else {
                console.log('User dismissed the install prompt');
            }
            window.deferredPrompt = null;
        });
    } else {
        // Show manual installation instructions
        showManualInstallInstructions();
    }
}

// Function to show manual installation instructions
function showManualInstallInstructions() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    
    let message = '';
    if (isIOS) {
        message = 'To install the app:\n\n1. Tap the Share button (📤) in Safari\n2. Scroll down and tap "Add to Home Screen"\n3. Tap "Add" to confirm';
    } else if (isAndroid) {
        message = 'To install the app:\n\n1. Tap the menu button (⋮) in Chrome\n2. Tap "Add to Home screen"\n3. Tap "Add" to confirm';
    } else {
        message = 'To install the app:\n\n1. Look for the install icon (📥) in your browser\'s address bar\n2. Click "Install" to confirm';
    }
    
    alert(`Install FitSmart App\n\n${message}`);
    dismissInstallPopup();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to the old PWA popup if it exists
    const popup = document.getElementById('pwa-install-popup');
    if (popup) {
        // Add click event to overlay to close popup
        const overlay = popup.querySelector('.pwa-popup-overlay');
        if (overlay) {
            overlay.addEventListener('click', dismissInstallPopup);
        }
        
        // Add escape key listener
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !popup.classList.contains('hidden')) {
                dismissInstallPopup();
            }
        });
    }
}); 