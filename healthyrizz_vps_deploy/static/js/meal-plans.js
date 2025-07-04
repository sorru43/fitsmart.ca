/**
 * Meal Plans JavaScript File
 * Handles meal plan UI interactions and animations
 */

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Log debug information
    if (typeof debug === 'function') {
        debug('Initializing meal plans JavaScript');
    }
    
    // Check if there are any meal cards
    const mealCards = document.querySelectorAll('.meal-card');
    console.log('Found ' + mealCards.length + ' meal cards');
    
    // Make sure all cards are visible first
    mealCards.forEach(card => {
        card.style.opacity = '1';
    });
    
    initializePlanToggle();
    initializeMealCards();
    initializeCompareFeature();
});

/**
 * Initialize the weekly/monthly plan toggle
 */
function initializePlanToggle() {
    const weeklyToggle = document.getElementById('toggle-weekly');
    const monthlyToggle = document.getElementById('toggle-monthly');
    const togglePill = document.querySelector('.toggle-pill');
    const plans = document.querySelectorAll('.meal-card');

    if (!weeklyToggle || !monthlyToggle) return;

    console.log("Initializing plan toggle");

    // Set default state (weekly)
    updatePriceDisplay('weekly');
    updateSubscribeButtonURLs('weekly');
    
    weeklyToggle.addEventListener('click', function() {
        console.log("Weekly toggle clicked");
        togglePill.style.transform = 'translateX(0)';
        weeklyToggle.classList.add('active');
        monthlyToggle.classList.remove('active');
        updatePriceDisplay('weekly');
        updateSubscribeButtonURLs('weekly');
    });
    
    monthlyToggle.addEventListener('click', function() {
        console.log("Monthly toggle clicked");
        togglePill.style.transform = 'translateX(100%)';
        monthlyToggle.classList.add('active');
        weeklyToggle.classList.remove('active');
        updatePriceDisplay('monthly');
        updateSubscribeButtonURLs('monthly');
    });
}

/**
 * Update the displayed prices based on selected plan type
 * @param {string} planType - 'weekly' or 'monthly'
 */
function updatePriceDisplay(planType) {
    const pricingElements = document.querySelectorAll('.plan-pricing');
    
    pricingElements.forEach(element => {
        const weeklyPrice = element.getAttribute('data-weekly-price');
        const monthlyPrice = element.getAttribute('data-monthly-price');
        const savingsElement = element.nextElementSibling;
        
        if (planType === 'weekly') {
            element.querySelector('.price-amount').textContent = weeklyPrice;
            element.querySelector('.price-period').textContent = '/week';
            if (savingsElement) savingsElement.classList.add('hidden');
        } else {
            element.querySelector('.price-amount').textContent = monthlyPrice;
            element.querySelector('.price-period').textContent = '/month';
            if (savingsElement) savingsElement.classList.remove('hidden');
        }
        
        // Apply animation
        element.classList.add('price-change-animation');
        setTimeout(() => {
            element.classList.remove('price-change-animation');
        }, 300);
    });
    
    // Update hidden input for subscription form
    const subscriptionTypeInput = document.getElementById('subscription_type');
    if (subscriptionTypeInput) {
        subscriptionTypeInput.value = planType;
    }
}

/**
 * Initialize the meal card animations and interactions
 */
function initializeMealCards() {
    const mealCards = document.querySelectorAll('.meal-card');
    
    mealCards.forEach((card, index) => {
        // Add fade in animation with delay
        card.style.opacity = '1'; // Set opacity to 1 to show the cards
        card.classList.add('fadeInUp');
        
        // Reveal nutrition details on click
        const detailsBtn = card.querySelector('.details-toggle');
        const detailsContent = card.querySelector('.nutrition-details');
        
        if (detailsBtn && detailsContent) {
            detailsBtn.addEventListener('click', function(e) {
                e.preventDefault();
                detailsContent.classList.toggle('hidden');
                const isHidden = detailsContent.classList.contains('hidden');
                detailsBtn.innerHTML = isHidden ? 'View Details <i class="fas fa-chevron-down"></i>' : 'Hide Details <i class="fas fa-chevron-up"></i>';
            });
        }
        
        // Subscribe button animation
        const subscribeBtn = card.querySelector('.subscribe-btn');
        if (subscribeBtn) {
            subscribeBtn.addEventListener('mouseenter', function() {
                this.classList.add('scale-105');
            });
            
            subscribeBtn.addEventListener('mouseleave', function() {
                this.classList.remove('scale-105');
            });
        }
    });
}

/**
 * Initialize the meal plan comparison feature
 */
function initializeCompareFeature() {
    const compareCheckboxes = document.querySelectorAll('.compare-checkbox');
    const compareButton = document.getElementById('compare-plans-btn');
    const comparisonModal = document.getElementById('comparison-modal');
    
    if (!compareCheckboxes.length || !compareButton || !comparisonModal) return;
    
    // Track selected plans
    let selectedPlans = [];
    
    compareCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const planId = this.value;
            
            if (this.checked) {
                if (selectedPlans.length >= 3) {
                    // Limit selection to 3 plans
                    this.checked = false;
                    showToast('You can compare up to 3 plans at a time');
                    return;
                }
                selectedPlans.push(planId);
            } else {
                selectedPlans = selectedPlans.filter(id => id !== planId);
            }
            
            // Update compare button state
            if (selectedPlans.length >= 2) {
                compareButton.classList.remove('opacity-50', 'cursor-not-allowed');
                compareButton.classList.add('btn-3d');
                compareButton.disabled = false;
            } else {
                compareButton.classList.add('opacity-50', 'cursor-not-allowed');
                compareButton.classList.remove('btn-3d');
                compareButton.disabled = true;
            }
        });
    });
    
    // Handle compare button click
    compareButton.addEventListener('click', function() {
        if (selectedPlans.length < 2) return;
        
        // Get data from selected meal plan cards
        const mealCards = document.querySelectorAll('.meal-card');
        const selectedCardData = [];
        
        mealCards.forEach(card => {
            const checkbox = card.querySelector('.compare-checkbox');
            if (checkbox && checkbox.checked) {
                const name = card.querySelector('h3').textContent.trim();
                const weeklyPrice = card.querySelector('.plan-pricing').getAttribute('data-weekly-price');
                const monthlyPrice = card.querySelector('.plan-pricing').getAttribute('data-monthly-price');
                
                // Get nutrition data
                const nutritionBoxes = card.querySelectorAll('.nutrition-box');
                const calories = nutritionBoxes[0].querySelector('.font-semibold').textContent.trim();
                const protein = nutritionBoxes[1].querySelector('.font-semibold').textContent.trim();
                const carbs = nutritionBoxes[2].querySelector('.font-semibold').textContent.trim() || 'N/A';
                const fat = nutritionBoxes[3].querySelector('.font-semibold').textContent.trim() || 'N/A';
                
                // Get dietary type (tag)
                const tagElem = card.querySelector('.bg-green-100');
                const tag = tagElem ? tagElem.textContent.trim() : 'Standard';
                
                // Check if includes breakfast
                const includesBreakfast = card.textContent.includes('With Breakfast');
                
                selectedCardData.push({
                    name: name,
                    weeklyPrice: weeklyPrice,
                    monthlyPrice: monthlyPrice,
                    calories: calories,
                    protein: protein,
                    carbs: carbs,
                    fat: fat,
                    includesBreakfast: includesBreakfast,
                    dietaryType: tag
                });
            }
        });
        
        // Update comparison modal with the actual selected plan data
        updateComparisonModal(selectedCardData);
        
        // Show the modal
        comparisonModal.classList.remove('hidden');
        
        // Add background blur and modal-backdrop class
        document.querySelector('.absolute.inset-0').classList.add('modal-backdrop');
        document.body.style.overflow = 'hidden'; // Prevent scrolling while modal is open
    });
    
    // Close comparison modal
    const closeModalButtons = document.querySelectorAll('.close-modal');
    if (closeModalButtons.length) {
        closeModalButtons.forEach(button => {
            button.addEventListener('click', function() {
                comparisonModal.classList.add('hidden');
                document.querySelector('.absolute.inset-0').classList.remove('modal-backdrop');
                document.body.style.overflow = ''; // Restore scrolling
            });
        });
    }
    
    // Also close modal when clicking outside
    document.querySelector('.absolute.inset-0').addEventListener('click', function() {
        comparisonModal.classList.add('hidden');
        this.classList.remove('modal-backdrop');
        document.body.style.overflow = '';
    });
}

/**
 * Update the comparison modal with selected plan data
 * @param {Array} planData - Array of plan data objects
 */
function updateComparisonModal(planData) {
    const table = document.querySelector('#comparison-modal table');
    const thead = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');
    
    // Update header row with plan names
    const headerCells = thead.querySelectorAll('th');
    headerCells[0].textContent = 'Feature';
    
    // Update or clear the plan columns
    for (let i = 1; i < 4; i++) {
        if (i <= planData.length) {
            headerCells[i].textContent = planData[i-1].name;
            headerCells[i].classList.remove('hidden');
        } else {
            headerCells[i].classList.add('hidden');
        }
    }
    
    // Update table rows with plan data
    const rows = tbody.querySelectorAll('tr');
    
    // Weekly Price
    updateTableRow(rows[0], 'Weekly Price', planData, 'weeklyPrice', '$');
    
    // Monthly Price
    updateTableRow(rows[1], 'Monthly Price', planData, 'monthlyPrice', '$');
    
    // Calories
    updateTableRow(rows[2], 'Calories', planData, 'calories');
    
    // Protein
    updateTableRow(rows[3], 'Protein', planData, 'protein');
    
    // Carbs
    updateTableRow(rows[4], 'Carbs', planData, 'carbs');
    
    // Fat
    updateTableRow(rows[5], 'Fat', planData, 'fat');
    
    // Includes Breakfast
    const breakfastRow = rows[6];
    const breakfastCells = breakfastRow.querySelectorAll('td');
    breakfastCells[0].textContent = 'Includes Breakfast';
    
    for (let i = 1; i < 4; i++) {
        if (i <= planData.length) {
            breakfastCells[i].innerHTML = planData[i-1].includesBreakfast ? 
                '<i class="fas fa-check text-green-500"></i>' : 
                '<i class="fas fa-times text-red-500"></i>';
            breakfastCells[i].classList.remove('hidden');
        } else {
            breakfastCells[i].classList.add('hidden');
        }
    }
    
    // Dietary Type
    updateTableRow(rows[7], 'Dietary Type', planData, 'dietaryType');
}

/**
 * Update a table row with plan data
 * @param {Element} row - The table row element
 * @param {string} label - The label for the first cell
 * @param {Array} planData - Array of plan data objects
 * @param {string} property - The property to display in this row
 * @param {string} prefix - Optional prefix for the displayed value
 */
function updateTableRow(row, label, planData, property, prefix = '') {
    const cells = row.querySelectorAll('td');
    cells[0].textContent = label;
    
    for (let i = 1; i < 4; i++) {
        if (i <= planData.length) {
            cells[i].textContent = prefix + planData[i-1][property];
            cells[i].classList.remove('hidden');
        } else {
            cells[i].classList.add('hidden');
        }
    }
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast: 'success', 'error', or 'info'
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    
    let bgColor = 'bg-primary';
    if (type === 'error') {
        bgColor = 'bg-red-500';
    } else if (type === 'success') {
        bgColor = 'bg-green-600';
    }
    
    toast.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded-lg shadow-lg z-50 fadeInUp`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s ease';
        
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 500);
    }, 3000);
}



/**
 * Update the subscribe button URLs and form data based on selected frequency
 * @param {string} frequency - 'weekly' or 'monthly'
 */
function updateSubscribeButtonURLs(frequency) {
    // Update direct button links
    const subscribeButtons = document.querySelectorAll('.subscribe-btn');
    
    if (subscribeButtons.length > 0) {
        subscribeButtons.forEach(button => {
            const url = new URL(button.href);
            url.searchParams.set('frequency', frequency);
            button.href = url.toString();
        });
    }
    
    // Update hidden form inputs for all subscription forms
    const frequencyInputs = document.querySelectorAll('form[action*="subscribe"] input[name="frequency"]');
    
    if (frequencyInputs.length > 0) {
        console.log(`Updating ${frequencyInputs.length} frequency inputs to ${frequency}`);
        frequencyInputs.forEach(input => {
            input.value = frequency;
        });
    } else {
        console.log("No frequency form inputs found to update");
    }
}

/**
 * Handle subscription form submission
 * @param {number} planId - The selected plan ID
 * @param {string} frequency - The payment frequency (weekly/monthly)
 */
function subscribeToPlan(planId, frequency) {
    // Show loading animation
    const subscribeBtn = document.querySelector(`[data-plan-id="${planId}"] .subscribe-btn`);
    if (subscribeBtn) {
        subscribeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        subscribeBtn.disabled = true;
    }
    
    // This would normally send data to the server
    // For now, let's simulate a delay and redirect
    setTimeout(() => {
        window.location.href = `/checkout?plan=${planId}&frequency=${frequency}`;
    }, 1000);
}
