// PWA Install Prompt Handler
class PWAInstallPrompt {
    constructor() {
        this.deferredPrompt = null;
        this.installButton = null;
        this.installPopup = null;
        this.isPopupVisible = false;
        
        this.init();
    }

    init() {
        // Create the install popup
        this.createInstallPopup();
        
        // Listen for the beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('PWA install prompt available');
            e.preventDefault();
            this.deferredPrompt = e;
            
            // Show install button in UI
            this.showInstallButtons();
        });

        // Listen for successful installation
        window.addEventListener('appinstalled', () => {
            console.log('PWA was installed');
            this.hideInstallPrompt();
            this.hideInstallButtons();
            this.deferredPrompt = null;
        });

        // Check if app is already installed
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            console.log('App is already installed');
            this.hideInstallPrompt();
            this.hideInstallButtons();
        }
    }

    showInstallButtons() {
        // Show any install buttons in the UI
        const installButtons = document.querySelectorAll('[data-pwa-install]');
        installButtons.forEach(button => {
            button.style.display = 'block';
            button.addEventListener('click', () => this.showInstallPrompt());
        });
    }

    hideInstallButtons() {
        // Hide install buttons since app is installed
        const installButtons = document.querySelectorAll('[data-pwa-install]');
        installButtons.forEach(button => {
            button.style.display = 'none';
        });
    }

    createInstallPopup() {
        // Create popup container
        this.installPopup = document.createElement('div');
        this.installPopup.id = 'pwa-install-popup';
        this.installPopup.innerHTML = `
            <div class="pwa-popup-overlay"></div>
            <div class="pwa-popup-content">
                <div class="pwa-popup-header">
                    <img src="/static/images/pwa_icons/icon-72x72.png" alt="HealthyRizz" class="pwa-logo">
                    <h3>Install HealthyRizz App</h3>
                    <button class="pwa-close-btn" id="pwa-close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="pwa-popup-body">
                    <p>Get the best experience with our native app!</p>
                    <ul class="pwa-features">
                        <li><i class="fas fa-check"></i> Quick access from home screen</li>
                        <li><i class="fas fa-check"></i> Works offline</li>
                        <li><i class="fas fa-check"></i> Faster loading</li>
                        <li><i class="fas fa-check"></i> Push notifications</li>
                        <li><i class="fas fa-check"></i> No app store required</li>
                    </ul>
                </div>
                <div class="pwa-popup-footer">
                    <button class="pwa-install-btn" id="pwa-install-btn">
                        <i class="fas fa-download"></i>
                        Install App
                    </button>
                    <button class="pwa-dismiss-btn" id="pwa-dismiss-btn">
                        Maybe Later
                    </button>
                </div>
            </div>
        `;

        // Add styles
        this.addStyles();
        
        // Add to body
        document.body.appendChild(this.installPopup);
        
        // Add event listeners
        this.installButton = document.getElementById('pwa-install-btn');
        const closeBtn = document.getElementById('pwa-close-btn');
        const dismissBtn = document.getElementById('pwa-dismiss-btn');
        
        this.installButton.addEventListener('click', () => this.installApp());
        closeBtn.addEventListener('click', () => this.hideInstallPrompt());
        dismissBtn.addEventListener('click', () => this.hideInstallPrompt());
        
        // Close on overlay click
        this.installPopup.querySelector('.pwa-popup-overlay').addEventListener('click', () => {
            this.hideInstallPrompt();
        });
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #pwa-install-popup {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 9999;
                display: none;
                align-items: center;
                justify-content: center;
                padding: 1rem;
            }

            .pwa-popup-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(4px);
            }

            .pwa-popup-content {
                position: relative;
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 1rem;
                max-width: 400px;
                width: 100%;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.8);
                animation: pwa-slide-up 0.3s ease-out;
            }

            @keyframes pwa-slide-up {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .pwa-popup-header {
                display: flex;
                align-items: center;
                padding: 1.5rem 1.5rem 1rem;
                border-bottom: 1px solid #333;
                position: relative;
            }

            .pwa-logo {
                width: 40px;
                height: 40px;
                border-radius: 8px;
                margin-right: 1rem;
            }

            .pwa-popup-header h3 {
                margin: 0;
                color: #ffffff;
                font-size: 1.25rem;
                font-weight: 600;
                flex: 1;
            }

            .pwa-close-btn {
                background: none;
                border: none;
                color: #888;
                font-size: 1.25rem;
                cursor: pointer;
                padding: 0.5rem;
                border-radius: 0.5rem;
                transition: all 0.2s;
            }

            .pwa-close-btn:hover {
                background: #333;
                color: #ffffff;
            }

            .pwa-popup-body {
                padding: 1.5rem;
            }

            .pwa-popup-body p {
                color: #ccc;
                margin: 0 0 1rem 0;
                line-height: 1.5;
            }

            .pwa-features {
                list-style: none;
                padding: 0;
                margin: 0;
            }

            .pwa-features li {
                display: flex;
                align-items: center;
                color: #ccc;
                margin-bottom: 0.75rem;
                font-size: 0.9rem;
            }

            .pwa-features li i {
                color: #10b981;
                margin-right: 0.75rem;
                font-size: 0.8rem;
            }

            .pwa-popup-footer {
                padding: 1rem 1.5rem 1.5rem;
                display: flex;
                gap: 0.75rem;
                flex-direction: column;
            }

            .pwa-install-btn {
                background: #10b981;
                color: white;
                border: none;
                padding: 0.875rem 1.5rem;
                border-radius: 0.5rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }

            .pwa-install-btn:hover {
                background: #059669;
                transform: translateY(-1px);
            }

            .pwa-dismiss-btn {
                background: transparent;
                color: #888;
                border: 1px solid #444;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                cursor: pointer;
                transition: all 0.2s;
            }

            .pwa-dismiss-btn:hover {
                background: #333;
                color: #ffffff;
            }

            /* Mobile responsive */
            @media (max-width: 480px) {
                #pwa-install-popup {
                    padding: 0.5rem;
                }

                .pwa-popup-content {
                    max-width: none;
                    margin: 0;
                }

                .pwa-popup-header {
                    padding: 1rem;
                }

                .pwa-popup-body {
                    padding: 1rem;
                }

                .pwa-popup-footer {
                    padding: 1rem;
                }
            }

            /* Show popup */
            #pwa-install-popup.show {
                display: flex;
            }
        `;
        document.head.appendChild(style);
    }

    showInstallPrompt() {
        if (this.deferredPrompt && !this.isPopupVisible) {
            this.isPopupVisible = true;
            this.installPopup.classList.add('show');
        } else if (!this.deferredPrompt) {
            // Show manual instructions if no prompt available
            this.showManualInstallInstructions();
        }
    }

    hideInstallPrompt() {
        this.isPopupVisible = false;
        this.installPopup.classList.remove('show');
    }

    async installApp() {
        if (this.deferredPrompt) {
            this.installButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Installing...';
            this.installButton.disabled = true;
            
            try {
                // Show the install prompt
                this.deferredPrompt.prompt();
                
                // Wait for the user to respond to the prompt
                const { outcome } = await this.deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                    this.hideInstallPrompt();
                } else {
                    console.log('User dismissed the install prompt');
                    this.installButton.innerHTML = '<i class="fas fa-download"></i> Install App';
                    this.installButton.disabled = false;
                }
                
                this.deferredPrompt = null;
            } catch (error) {
                console.error('Error during PWA installation:', error);
                this.installButton.innerHTML = '<i class="fas fa-download"></i> Install App';
                this.installButton.disabled = false;
            }
        }
    }

    // Manual install method for footer link
    manualInstall() {
        if (this.deferredPrompt) {
            this.showInstallPrompt();
        } else {
            // Show instructions for manual installation
            this.showManualInstallInstructions();
        }
    }

    showManualInstallInstructions() {
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isAndroid = /Android/.test(navigator.userAgent);
        
        let message = '';
        let title = 'Install HealthyRizz App';
        
        if (isIOS) {
            message = 'To install the app on iOS:\n\n1. Tap the Share button (📤) in Safari\n2. Scroll down and tap "Add to Home Screen"\n3. Tap "Add" to confirm';
        } else if (isAndroid) {
            message = 'To install the app on Android:\n\n1. Tap the menu button (⋮) in Chrome\n2. Tap "Add to Home screen"\n3. Tap "Add" to confirm';
        } else {
            message = 'To install the app on desktop:\n\n1. Look for the install icon (📥) in your browser\'s address bar\n2. Click "Install" to confirm\n\nOr use the browser menu to find "Install" or "Add to Home Screen"';
        }
        
        alert(`${title}\n\n${message}`);
    }
}

// Global functions for compatibility
window.showPWAInstallPopup = function() {
    if (window.pwaInstallPrompt) {
        window.pwaInstallPrompt.manualInstall();
    } else {
        // Fallback for manual instructions
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
        
        alert(`Install HealthyRizz App\n\n${message}`);
    }
};

window.installPWA = window.showPWAInstallPopup; // Alias for compatibility

// Initialize PWA install prompt when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the PWA install prompt
    window.pwaInstallPrompt = new PWAInstallPrompt();
    
    // Add data attributes to install buttons for automatic handling
    const installLinks = document.querySelectorAll('a[href="#"][onclick*="showPWAInstallPopup"], a[href="#"][onclick*="installPWA"]');
    installLinks.forEach(link => {
        link.setAttribute('data-pwa-install', 'true');
        link.addEventListener('click', (e) => {
            e.preventDefault();
            window.showPWAInstallPopup();
        });
    });
}); 