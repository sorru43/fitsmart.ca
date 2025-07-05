// Simple fade-in animation for the testimonial
function initializeTestimonialCarousel() {
    const testimonial = document.querySelector('.bg-dark-3');
    if (testimonial) {
        testimonial.style.opacity = '0';
        testimonial.style.transition = 'opacity 0.5s ease-in-out';
        
        // Fade in after a short delay
        setTimeout(() => {
            testimonial.style.opacity = '1';
        }, 300);
    }
} 