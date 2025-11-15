/**
 * Holiday Popup Management
 * Handles holiday notifications and user interactions
 */

class HolidayPopup {
    constructor() {
        this.popupShown = false;
        this.checkInterval = null;
        this.init();
    }

    init() {
        // Only show holiday popup on pages where logged-in users would be
        // Skip on public pages like homepage, login, register, etc.
        const publicPages = ['/', '/login', '/register', '/blog', '/meal-plans', '/meal-calculator'];
        const currentPath = window.location.pathname;
        
        if (publicPages.includes(currentPath)) {
            console.log('Holiday popup disabled on public page:', currentPath);
            return;
        }
        
        // Check for holiday status on page load
        this.checkHolidayStatus();
        
        // Set up periodic checking (every 5 minutes)
        this.checkInterval = setInterval(() => {
            this.checkHolidayStatus();
        }, 5 * 60 * 1000);
    }

    async checkHolidayStatus() {
        try {
            const response = await fetch('/holiday/status');
            const data = await response.json();
            
            if (data.active && !this.popupShown) {
                this.showPopup(data.holiday);
            } else if (data.message) {
                // Log the reason why popup is not shown (for debugging)
                console.log('Holiday popup not shown:', data.message);
            }
        } catch (error) {
            console.error('Error checking holiday status:', error);
        }
    }

    showPopup(holiday) {
        // Create popup HTML
        const popupHTML = this.createPopupHTML(holiday);
        
        // Add to page
        document.body.insertAdjacentHTML('beforeend', popupHTML);
        
        // Show popup with animation
        const popup = document.getElementById('holiday-popup');
        const overlay = document.getElementById('holiday-overlay');
        
        setTimeout(() => {
            popup.classList.add('show');
            overlay.classList.add('show');
        }, 100);
        
        this.popupShown = true;
        
        // Set up event listeners
        this.setupEventListeners(holiday);
    }

    createPopupHTML(holiday) {
        const optionsHTML = holiday.options.map(option => 
            `<button class="holiday-option-btn" data-response="${option}">
                <i class="fas fa-check-circle"></i> ${option}
            </button>`
        ).join('');
        
        return `
            <div id="holiday-overlay" class="holiday-overlay"></div>
            <div id="holiday-popup" class="holiday-popup">
                <div class="holiday-popup-header">
                    <h3><i class="fas fa-calendar-day"></i> ${holiday.name}</h3>
                    <button class="holiday-close-btn" onclick="holidayPopup.closePopup()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="holiday-popup-body">
                    ${holiday.description ? `<p class="holiday-description">${holiday.description}</p>` : ''}
                    ${holiday.message ? `<p class="holiday-message">${holiday.message}</p>` : ''}
                    <div class="holiday-info">
                        <p><i class="fas fa-clock"></i> Days remaining: ${holiday.days_remaining}</p>
                        ${holiday.protect_meals ? '<p><i class="fas fa-shield-alt"></i> Meals are protected during this period</p>' : ''}
                        <p><i class="fas fa-calendar-check"></i> Holiday period: ${this.formatDate(holiday.start_date)} - ${this.formatDate(holiday.end_date)}</p>
                    </div>
                </div>
                <div class="holiday-popup-footer">
                    <div class="holiday-options">
                        ${optionsHTML}
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners(holiday) {
        // Option button clicks
        document.querySelectorAll('.holiday-option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const response = e.target.dataset.response;
                this.handleResponse(holiday.id, response);
            });
        });

        // Overlay click to close
        document.getElementById('holiday-overlay').addEventListener('click', () => {
            this.closePopup();
        });

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closePopup();
            }
        });
    }

    async handleResponse(holidayId, response) {
        try {
            const responseData = await fetch('/holiday/response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    holiday_id: holidayId,
                    response: response
                })
            });
            
            const result = await responseData.json();
            
            if (result.success) {
                // Show success message
                this.showSuccessMessage(response);
                
                // Close popup after delay
                setTimeout(() => {
                    this.closePopup();
                }, 2000);
            } else {
                console.error('Error handling holiday response:', result.error);
            }
        } catch (error) {
            console.error('Error sending holiday response:', error);
        }
    }

    showSuccessMessage(response) {
        const popup = document.getElementById('holiday-popup');
        const body = popup.querySelector('.holiday-popup-body');
        
        body.innerHTML = `
            <div class="holiday-success">
                <i class="fas fa-check-circle"></i>
                <p>Thank you for your response: "${response}"</p>
            </div>
        `;
    }

    closePopup() {
        const popup = document.getElementById('holiday-popup');
        const overlay = document.getElementById('holiday-overlay');
        
        if (popup && overlay) {
            popup.classList.remove('show');
            overlay.classList.remove('show');
            
            // Remove from DOM after animation
            setTimeout(() => {
                popup.remove();
                overlay.remove();
            }, 300);
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    destroy() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
    }
}

// Initialize holiday popup when DOM is ready
let holidayPopup;
document.addEventListener('DOMContentLoaded', () => {
    holidayPopup = new HolidayPopup();
});

// Export for global access
window.holidayPopup = holidayPopup;
