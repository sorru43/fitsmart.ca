/**
 * Hero Section Animations
 * This file contains special animations for the hero section on the home page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initCounterAnimations();
    initScrollReveal();
});

/**
 * Animate number counters with smooth counting effect
 */
function initCounterAnimations() {
    const counters = document.querySelectorAll('.counter-animate');
    
    const animateCounter = (counter, target) => {
        const duration = 2000; // Animation duration in milliseconds
        const steps = 50; // Number of steps in the animation
        const stepDuration = duration / steps;
        const increment = target / steps;
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            const value = Math.round(current);
            counter.textContent = value + (counter.textContent.includes('+') ? '+' : '');
            
            if (current < target) {
                setTimeout(updateCounter, stepDuration);
            }
        };
        
        updateCounter();
    };
    
    // Create an Intersection Observer to start counter animations when in view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.textContent);
                animateCounter(counter, target);
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

/**
 * Initialize scroll-based reveal animations
 */
function initScrollReveal() {
    const revealElements = document.querySelectorAll('.fade-in, .slide-up');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    revealElements.forEach(el => observer.observe(el));
}
