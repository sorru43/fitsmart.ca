function checkDeliveryLocation() {
    const postalCode = document.getElementById('postal_code').value.trim();
    const city = document.getElementById('city').value.trim();
    const province = document.getElementById('province').value.trim();
    
    if (!postalCode || !city || !province) {
        showLocationMessage('Please fill in all location fields', 'error');
        return;
    }
    
    // Show loading state
    const checkButton = document.getElementById('check-location-btn');
    const originalText = checkButton.innerHTML;
    checkButton.innerHTML = 'Checking...';
    checkButton.disabled = true;
    
    // Make AJAX request
    fetch('/check-location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({
            postal_code: postalCode,
            city: city,
            province: province
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.is_available) {
                showLocationMessage(data.message, 'success');
                // Enable the continue button or form submission
                document.getElementById('continue-btn').disabled = false;
            } else {
                showLocationMessage(data.message, 'error');
                // Disable the continue button or form submission
                document.getElementById('continue-btn').disabled = true;
            }
        } else {
            showLocationMessage(data.message, 'error');
            // Disable the continue button or form submission
            document.getElementById('continue-btn').disabled = true;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showLocationMessage('An error occurred while checking your location', 'error');
        // Disable the continue button or form submission
        document.getElementById('continue-btn').disabled = true;
    })
    .finally(() => {
        // Restore button state
        checkButton.innerHTML = originalText;
        checkButton.disabled = false;
    });
}

function showLocationMessage(message, type) {
    const messageDiv = document.getElementById('location-message');
    messageDiv.textContent = message;
    messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageDiv.style.display = 'block';
}

// Add event listeners when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    const checkButton = document.getElementById('check-location-btn');
    if (checkButton) {
        checkButton.addEventListener('click', checkDeliveryLocation);
    }
    
    // Add input validation for postal code
    const postalCodeInput = document.getElementById('postal_code');
    if (postalCodeInput) {
        postalCodeInput.addEventListener('input', function(e) {
            // Convert to uppercase and remove spaces
            let value = e.target.value.toUpperCase().replace(/\s+/g, '');
            // Format as A1A 1A1
            if (value.length > 3) {
                value = value.slice(0, 3) + ' ' + value.slice(3);
            }
            e.target.value = value;
        });
    }
}); 