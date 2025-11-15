
// Footer Visibility Test
document.addEventListener('DOMContentLoaded', function() {
    const footer = document.querySelector('footer');
    if (footer) {
        console.log('Footer element found:', footer);
        console.log('Footer classes:', footer.className);
        console.log('Footer display style:', window.getComputedStyle(footer).display);
        console.log('Footer visibility style:', window.getComputedStyle(footer).visibility);
        
        // Force footer visibility on desktop
        if (window.innerWidth >= 768) {
            footer.style.display = 'block';
            footer.style.visibility = 'visible';
            console.log('Forced footer visibility on desktop');
        }
    } else {
        console.log('Footer element not found');
    }
});
