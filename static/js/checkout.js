// Checkout form handling script
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const paymentForm = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    const buttonText = document.getElementById('button-text');
    const spinner = document.getElementById('spinner');
    const frequencyInput = document.getElementById('frequency-input');
    const totalPriceInput = document.getElementById('total-price-input');
    const selectedVegDaysInput = document.getElementById('selected-veg-days');
    const breakfastCheckbox = document.getElementById('includes_breakfast');
    const breakfastPriceSpan = document.getElementById('breakfast_price');
    const province = document.getElementById('province');
    const city = document.getElementById('city');
    const otherLocation = document.getElementById('other_location');
    const otherLocationContainer = document.getElementById('other-location-container');
    
    // Get price data from form
    const weeklyPrice = parseFloat(paymentForm.dataset.weeklyPrice);
    const monthlyPrice = parseFloat(paymentForm.dataset.monthlyPrice);
    
    // Initialize price display
    let currentFrequency = frequencyInput.value;
    let currentPrice = currentFrequency === 'weekly' ? weeklyPrice : monthlyPrice;
    
    updatePriceDisplay();
    
    // Handle frequency changes
    document.querySelectorAll('input[name="frequency"]').forEach(radio => {
        radio.addEventListener('change', function() {
            currentFrequency = this.value;
            frequencyInput.value = currentFrequency;
            updatePriceDisplay();
        });
    });
    
    // Handle vegetarian days selection
    document.querySelectorAll('input[name="veg_days"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const selectedDays = Array.from(document.querySelectorAll('input[name="veg_days"]:checked'))
                .map(checkbox => checkbox.value);
            selectedVegDaysInput.value = selectedDays.join(',');
        });
    });
    
    // Handle city selection
    if (city) {
        city.addEventListener('change', function() {
            if (this.value === 'Other') {
                otherLocationContainer.style.display = 'block';
                otherLocation.required = true;
            } else {
                otherLocationContainer.style.display = 'none';
                otherLocation.required = false;
            }
        });
    }
    
    // Handle coupon code
    const couponCode = document.getElementById('coupon_code');
    const applyCouponButton = document.getElementById('apply-coupon');
    
    if (applyCouponButton && couponCode) {
        applyCouponButton.addEventListener('click', async function() {
            const code = couponCode.value.trim();
            if (!code) {
                alert('Please enter a coupon code');
                return;
            }
            
            try {
                const response = await fetch(`/api/validate-coupon/${code}`);
                const data = await response.json();
                
                if (data.valid) {
                    // Update price with discount
                    const originalPrice = parseFloat(totalPriceInput.value);
                    const discount = originalPrice * (data.discount_percent / 100);
                    const finalPrice = originalPrice - discount;
                    
                    // Update display
                    document.getElementById('summary-discount').textContent = `-$${discount.toFixed(2)}`;
                    document.getElementById('summary-total').textContent = `$${finalPrice.toFixed(2)}`;
                    
                    // Store coupon info
                    paymentForm.dataset.couponCode = code;
                    paymentForm.dataset.discountPercent = data.discount_percent;
                    
                    alert('Coupon applied successfully!');
                } else {
                    alert(data.message || 'Invalid coupon code');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error applying coupon code. Please try again.');
            }
        });
    }
    
    // Update price display based on current selections
    function updatePriceDisplay() {
        // Calculate base price
        const basePrice = currentFrequency === 'weekly' ? weeklyPrice : monthlyPrice;
        
        // Update total price
        totalPriceInput.value = basePrice.toFixed(2);
        
        // Update price display
        const priceDisplay = document.getElementById('price-display');
        if (priceDisplay) {
            priceDisplay.textContent = `$${basePrice.toFixed(2)}`;
        }
        
        // Update frequency label
        const frequencyLabel = document.getElementById('frequency-label');
        if (frequencyLabel) {
            frequencyLabel.textContent = `/${currentFrequency}`;
        }
        
        // Update summary section
        const summarySubtotal = document.getElementById('summary-subtotal');
        const summaryTotal = document.getElementById('summary-total');
        if (summarySubtotal) {
            summarySubtotal.textContent = `$${basePrice.toFixed(2)}`;
        }
        if (summaryTotal) {
            summaryTotal.textContent = `$${basePrice.toFixed(2)}`;
        }
        
        // Update plan frequency display
        const planFrequencyDisplay = document.getElementById('plan-frequency-display');
        if (planFrequencyDisplay) {
            const planName = document.querySelector('.plan-name').textContent;
            planFrequencyDisplay.textContent = `${planName} (${currentFrequency})`;
        }
    }
    
    // Initialize Razorpay
    const razorpay = new Razorpay({
        key: document.querySelector('meta[name="razorpay-key"]').content,
        currency: 'INR',
        name: 'Fit Smart',
        description: 'Meal Plan Subscription',
        image: '/static/images/logo.png',
        handler: function (response) {
            // Handle successful payment
            const form = document.getElementById('payment-form');
            const paymentIdInput = document.createElement('input');
            paymentIdInput.type = 'hidden';
            paymentIdInput.name = 'razorpay_payment_id';
            paymentIdInput.value = response.razorpay_payment_id;
            form.appendChild(paymentIdInput);
            form.submit();
        },
        prefill: {
            name: document.getElementById('customer-name').value,
            email: document.getElementById('customer-email').value,
            contact: document.getElementById('customer-phone').value
        },
        theme: {
            color: '#10B981'
        }
    });

    // Handle form submission
    document.getElementById('payment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            return;
        }
        
        // Show loading state
        const submitButton = document.getElementById('submit-button');
        const buttonText = document.getElementById('button-text');
        const spinner = document.getElementById('spinner');
        
        submitButton.disabled = true;
        buttonText.textContent = 'Processing...';
        spinner.classList.remove('hidden');
        
        // Get form data
        const formData = new FormData(this);
        const data = {
            amount: parseFloat(formData.get('total_price')) * 100, // Convert to paise
            currency: 'INR',
            receipt: 'receipt_' + Date.now(),
            notes: {
                plan_id: formData.get('plan_id'),
                frequency: formData.get('frequency'),
                customer_name: formData.get('customer_name'),
                customer_email: formData.get('customer_email'),
                customer_phone: formData.get('customer_phone'),
                customer_address: formData.get('customer_address'),
                customer_city: formData.get('customer_city'),
                customer_state: formData.get('customer_state'),
                customer_pincode: formData.get('customer_pincode'),
                delivery_instructions: formData.get('delivery_instructions'),
                coupon_code: formData.get('coupon_code'),
                discount_amount: formData.get('discount_amount'),
                vegetarian_days: formData.get('vegetarian_days'),
                includes_breakfast: formData.get('includes_breakfast')
            }
        };
        
        // Create Razorpay order
        fetch('/api/create-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrf_token')
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Open Razorpay checkout
            razorpay.open({
                order_id: data.order_id,
                amount: data.amount,
                currency: data.currency
            });
        })
        .catch(error => {
            // Handle error
            const messageElement = document.getElementById('payment-message');
            messageElement.textContent = error.message;
            messageElement.classList.remove('hidden');
            
            // Reset button state
            submitButton.disabled = false;
            buttonText.textContent = 'Proceed to Payment';
            spinner.classList.add('hidden');
        });
    });

    // Form validation
    function validateForm() {
        const phone = document.getElementById('customer-phone').value;
        const pincode = document.getElementById('customer-pincode').value;
        
        // Validate Indian phone number
        const phoneRegex = /^[6-9]\d{9}$/;
        if (!phoneRegex.test(phone.replace(/\D/g, ''))) {
            showError('Please enter a valid Indian mobile number');
            return false;
        }
        
        // Validate PIN code
        const pincodeRegex = /^\d{6}$/;
        if (!pincodeRegex.test(pincode)) {
            showError('Please enter a valid 6-digit PIN code');
            return false;
        }
        
        return true;
    }

    function showError(message) {
        const messageElement = document.getElementById('payment-message');
        messageElement.textContent = message;
        messageElement.classList.remove('hidden');
        setTimeout(() => {
            messageElement.classList.add('hidden');
        }, 5000);
    }

    // Calculate total with GST
    function calculateTotal(amount) {
        const gstRate = 0.05; // 5% GST
        const gstAmount = amount * gstRate;
        return {
            subtotal: amount,
            gst: gstAmount,
            total: amount + gstAmount
        };
    }

    // Update price display
    function updatePriceDisplay(price) {
        const totals = calculateTotal(price);
        
        // Update subtotal
        summarySubtotal.textContent = `₹${totals.subtotal.toFixed(2)}`;
        
        // Update GST
        const gstElement = document.getElementById('gst-amount');
        if (gstElement) {
            gstElement.textContent = `₹${totals.gst.toFixed(2)}`;
        }
        
        // Update total
        summaryTotal.textContent = `₹${totals.total.toFixed(2)}`;
        totalPriceInput.value = totals.total.toFixed(2);
    }

    // Handle frequency change
    const frequencyButtons = document.querySelectorAll('input[name="frequency"]');
    frequencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const frequency = this.dataset.frequency;
            
            // Update active state
            frequencyButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-primary', 'text-white');
                btn.classList.add('bg-gray-800', 'hover:bg-gray-700', 'text-white');
            });
            this.classList.remove('bg-gray-800', 'hover:bg-gray-700', 'text-white');
            this.classList.add('active', 'bg-primary', 'text-white');
            
            // Update price based on frequency
            currentPrice = frequency === 'weekly' ? weeklyPrice : monthlyPrice;
            updatePriceDisplay(currentPrice);
            
            // Update the frequency label
            const frequencyLabel = document.getElementById('frequency-label');
            if (frequencyLabel) {
                frequencyLabel.textContent = `/${frequency}`;
            }
            
            // Update hidden input
            frequencyInput.value = frequency;
            
            // Reset coupon if one was applied
            if (couponApplied) {
                resetCoupon();
            }
        });
    });

    // Handle coupon application
    applyCouponButton.addEventListener('click', function() {
        const couponCode = couponInput.value.trim();
        if (!couponCode) return;
        
        // Show loading state
        this.disabled = true;
        this.textContent = 'Applying...';
        
        fetch('/api/validate-coupon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: JSON.stringify({
                coupon_code: couponCode,
                amount: currentPrice
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                // Update with discount
                const totals = calculateTotal(currentPrice - data.discount_amount);
                updateWithDiscount(data.discount_amount, data.description, totals.total);
                couponApplied = true;
            } else {
                showError(data.message || 'Invalid coupon code');
            }
        })
        .catch(error => {
            showError('Error applying coupon. Please try again.');
        })
        .finally(() => {
            // Reset button state
            this.disabled = false;
            this.textContent = 'Apply';
        });
    });
});