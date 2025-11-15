/**
 * Enhanced Video Player System
 * Supports both YouTube and uploaded videos with improved UX
 */

class VideoCarousel {
    constructor() {
        this.currentSlide = 0;
        this.totalSlides = 0;
        this.videoSlides = [];
        this.contentSlides = [];
        this.nextPreviews = [];
        this.autoAdvanceInterval = null;
        this.isPlaying = false;
        this.currentVideo = null;
        
        this.init();
    }

    init() {
        // Initialize DOM elements
        this.videoSlides = document.querySelectorAll('.video-slide');
        this.contentSlides = document.querySelectorAll('.content-slide');
        this.nextPreviews = document.querySelectorAll('.next-preview');
        this.totalSlides = this.videoSlides.length;
        
        if (this.totalSlides === 0) {
            console.warn('No video slides found');
            return;
        }

        // Set up event listeners
        this.setupEventListeners();
        
        // Start auto-advance
        this.startAutoAdvance();
        
        // Initialize first slide
        this.updateCarousel();
        
        console.log(`Video carousel initialized with ${this.totalSlides} slides`);
    }

    setupEventListeners() {
        const carouselContainer = document.querySelector('.video-carousel-container');
        
        if (carouselContainer) {
            // Mouse events
            carouselContainer.addEventListener('mouseenter', () => this.pauseAutoAdvance());
            carouselContainer.addEventListener('mouseleave', () => this.startAutoAdvance());
            
            // Touch events for mobile
            this.setupTouchEvents(carouselContainer);
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                this.prevSlide();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                this.nextSlide();
            } else if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // Modal background clicks
        this.setupModalListeners();
    }

    setupTouchEvents(container) {
        let startX = 0, startY = 0, endX = 0, endY = 0;
        
        container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        container.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Only respond to horizontal swipes with sufficient distance
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    this.nextSlide(); // Swipe left - next slide
                } else {
                    this.prevSlide(); // Swipe right - previous slide
                }
            }
        }, { passive: true });
    }

    setupModalListeners() {
        // Video modal
        const videoModal = document.getElementById('video-modal');
        if (videoModal) {
            videoModal.addEventListener('click', (e) => {
                if (e.target.id === 'video-modal') {
                    this.closeVideoModal();
                }
            });
        }

        // YouTube modal
        const youtubeModal = document.getElementById('youtube-modal');
        if (youtubeModal) {
            youtubeModal.addEventListener('click', (e) => {
                if (e.target.id === 'youtube-modal') {
                    this.closeYouTubeModal();
                }
            });
        }
    }

    nextSlide() {
        this.pauseCurrentVideo();
        this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
        this.updateCarousel();
    }

    prevSlide() {
        this.pauseCurrentVideo();
        this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
        this.updateCarousel();
    }

    updateCarousel() {
        // Add loading state
        this.showLoadingState();

        // Update video slides with smooth transitions
        this.videoSlides.forEach((slide, index) => {
            const isActive = index === this.currentSlide;
            
            slide.classList.toggle('opacity-100', isActive);
            slide.classList.toggle('z-20', isActive);
            slide.classList.toggle('opacity-0', !isActive);
            slide.classList.toggle('z-10', !isActive);
            
            // Add entrance animation for active slide
            if (isActive) {
                slide.classList.add('entering');
                setTimeout(() => slide.classList.remove('entering'), 700);
            }
        });
        
        // Update content slides
        this.contentSlides.forEach((slide, index) => {
            const isActive = index === this.currentSlide;
            slide.classList.toggle('hidden', !isActive);
            slide.classList.toggle('block', isActive);
        });
        
        // Update next video preview
        const nextIndex = (this.currentSlide + 1) % this.totalSlides;
        this.nextPreviews.forEach((preview, index) => {
            const isNext = index === nextIndex;
            preview.classList.toggle('hidden', !isNext);
            preview.classList.toggle('block', isNext);
        });

        // Hide loading state
        setTimeout(() => this.hideLoadingState(), 300);
    }

    showLoadingState() {
        const container = document.querySelector('.video-carousel-container');
        if (container && !container.querySelector('.video-loading')) {
            const loading = document.createElement('div');
            loading.className = 'video-loading';
            loading.innerHTML = '<div class="loading-spinner"></div>';
            container.appendChild(loading);
        }
    }

    hideLoadingState() {
        const loading = document.querySelector('.video-loading');
        if (loading) {
            loading.remove();
        }
    }

    startAutoAdvance() {
        if (!this.isPlaying && this.totalSlides > 1) {
            this.autoAdvanceInterval = setInterval(() => {
                this.nextSlide();
            }, 8000);
        }
    }

    pauseAutoAdvance() {
        if (this.autoAdvanceInterval) {
            clearInterval(this.autoAdvanceInterval);
            this.autoAdvanceInterval = null;
        }
    }

    pauseCurrentVideo() {
        if (this.currentVideo) {
            try {
                this.currentVideo.pause();
            } catch (e) {
                console.warn('Could not pause current video:', e);
            }
        }
    }

    // Video playback methods
    playUploadedVideo(videoId) {
        console.log('Playing uploaded video:', videoId);
        
        const videoElement = document.getElementById('video-' + videoId);
        const modal = document.getElementById('video-modal');
        const modalVideo = document.getElementById('modal-video');
        
        if (!videoElement || !modal || !modalVideo) {
            console.error('Video elements not found for ID:', videoId);
            this.showErrorMessage('Video not found. Please try again.');
            return;
        }
        
        try {
            // Copy video source to modal
            modalVideo.innerHTML = videoElement.innerHTML;
            modalVideo.load();
            
            // Show modal with animation
            modal.classList.remove('hidden');
            modal.classList.add('video-modal');
            document.body.style.overflow = 'hidden';
            
            // Play video
            modalVideo.play().then(() => {
                this.currentVideo = modalVideo;
                this.isPlaying = true;
                this.pauseAutoAdvance();
            }).catch(e => {
                console.error('Error playing video:', e);
                this.showErrorMessage('Unable to play video. Please check your connection and try again.');
                this.closeVideoModal();
            });
            
        } catch (e) {
            console.error('Error setting up video:', e);
            this.showErrorMessage('Video setup failed. Please try again.');
        }
    }

    playYouTubeVideo(videoId) {
        console.log('Playing YouTube video:', videoId);
        
        const modal = document.getElementById('youtube-modal');
        const playerDiv = document.getElementById('youtube-player');
        
        if (!modal || !playerDiv) {
            console.warn('YouTube modal not found, opening in new window');
            window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
            return;
        }
        
        try {
            // Show modal
            modal.classList.remove('hidden');
            modal.classList.add('video-modal');
            document.body.style.overflow = 'hidden';
            
            // Create enhanced iframe with better parameters
            playerDiv.innerHTML = `
                <iframe 
                    width="100%" 
                    height="100%" 
                    src="https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1&playsinline=1&enablejsapi=1" 
                    title="YouTube video player" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    allowfullscreen
                    style="border-radius: 8px;">
                </iframe>
            `;
            
            this.isPlaying = true;
            this.pauseAutoAdvance();
            
        } catch (e) {
            console.error('Error loading YouTube video:', e);
            this.showErrorMessage('Unable to load YouTube video. Please try again.');
        }
    }

    closeVideoModal() {
        const modal = document.getElementById('video-modal');
        const modalVideo = document.getElementById('modal-video');
        
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('video-modal');
        }
        
        document.body.style.overflow = 'auto';
        
        if (modalVideo) {
            modalVideo.pause();
            modalVideo.currentTime = 0;
            modalVideo.innerHTML = '';
        }
        
        this.currentVideo = null;
        this.isPlaying = false;
        this.startAutoAdvance();
    }

    closeYouTubeModal() {
        const modal = document.getElementById('youtube-modal');
        const playerDiv = document.getElementById('youtube-player');
        
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('video-modal');
        }
        
        document.body.style.overflow = 'auto';
        
        if (playerDiv) {
            playerDiv.innerHTML = '';
        }
        
        this.isPlaying = false;
        this.startAutoAdvance();
    }

    closeAllModals() {
        this.closeVideoModal();
        this.closeYouTubeModal();
        closeReelModal(); // Also close reel modal
    }

    showErrorMessage(message) {
        // Create a simple toast notification
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300';
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 5000);
    }

    // Public API methods
    goToSlide(index) {
        if (index >= 0 && index < this.totalSlides) {
            this.pauseCurrentVideo();
            this.currentSlide = index;
            this.updateCarousel();
        }
    }

    getCurrentSlide() {
        return this.currentSlide;
    }

    getTotalSlides() {
        return this.totalSlides;
    }
}

// ===== REEL FUNCTIONALITY =====

// Reel functionality for Instagram-like vertical videos
function playReel(videoId) {
    console.log('Playing reel:', videoId);
    
    // Find the video element
    const videoElement = document.getElementById('reel-video-' + videoId);
    const modal = document.getElementById('reel-modal');
    const modalVideo = document.getElementById('reel-modal-video');
    const modalTitle = document.getElementById('reel-modal-title');
    const modalDescription = document.getElementById('reel-modal-description');
    
    if (!videoElement || !modal || !modalVideo) {
        console.error('Reel elements not found');
        return;
    }
    
    try {
        // Copy video source to modal
        modalVideo.innerHTML = videoElement.innerHTML;
        modalVideo.load();
        
        // Get video data from the card
        const reelCard = videoElement.closest('.reel-card');
        if (reelCard) {
            const title = reelCard.querySelector('h3')?.textContent || 'FitSmart Reel';
            const description = reelCard.querySelector('p')?.textContent || '';
            
            modalTitle.textContent = title;
            modalDescription.textContent = description;
        }
        
        // Show modal
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Play video
        modalVideo.play().catch(e => {
            console.error('Error playing reel:', e);
        });
        
    } catch (e) {
        console.error('Error setting up reel:', e);
    }
}

function closeReelModal() {
    const modal = document.getElementById('reel-modal');
    const modalVideo = document.getElementById('reel-modal-video');
    
    if (modal) {
        modal.classList.add('hidden');
    }
    
    document.body.style.overflow = 'auto';
    
    if (modalVideo) {
        modalVideo.pause();
        modalVideo.currentTime = 0;
    }
}

function setupReelEventListeners() {
    // Close reel on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeReelModal();
        }
    });

    // Close reel on background click
    const reelModal = document.getElementById('reel-modal');
    if (reelModal) {
        reelModal.addEventListener('click', (e) => {
            if (e.target.id === 'reel-modal') {
                closeReelModal();
            }
        });
    }

    // Hover effects for reel cards - play preview on hover
    const reelCards = document.querySelectorAll('.reel-card');
    
    reelCards.forEach(card => {
        const video = card.querySelector('video');
        
        if (video) {
            // Play preview on hover (muted)
            card.addEventListener('mouseenter', () => {
                video.currentTime = 0; // Start from beginning
                video.play().catch(e => console.log('Preview play failed:', e));
            });
            
            // Pause preview when not hovering
            card.addEventListener('mouseleave', () => {
                video.pause();
                video.currentTime = 0;
            });
        }
    });
}

// Initialize video carousel when DOM is ready
let videoCarousel;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize video carousel
    videoCarousel = new VideoCarousel();
    
    // Make methods globally available for onclick handlers
    window.playUploadedVideo = (videoId) => videoCarousel.playUploadedVideo(videoId);
    window.playYouTubeVideo = (videoId) => videoCarousel.playYouTubeVideo(videoId);
    window.closeVideoModal = () => videoCarousel.closeVideoModal();
    window.closeYouTubeModal = () => videoCarousel.closeYouTubeModal();
    window.nextSlide = () => videoCarousel.nextSlide();
    window.prevSlide = () => videoCarousel.prevSlide();
    
    // Make reel functions globally available
    window.playReel = playReel;
    window.closeReelModal = closeReelModal;
    
    // Set up reel event listeners
    setupReelEventListeners();
    
    // Add quality indicators to videos
    addQualityIndicators();
    
    // Preload video metadata for better performance
    preloadVideoMetadata();
});

function addQualityIndicators() {
    const videoElements = document.querySelectorAll('video[id^="video-"]');
    videoElements.forEach(video => {
        if (!video.querySelector('.quality-indicator')) {
            const indicator = document.createElement('div');
            indicator.className = 'quality-indicator';
            indicator.textContent = 'HD';
            video.parentElement.appendChild(indicator);
        }
    });
}

function preloadVideoMetadata() {
    const videoElements = document.querySelectorAll('video[preload="metadata"]');
    videoElements.forEach(video => {
        video.addEventListener('loadedmetadata', () => {
            console.log(`Video metadata loaded for: ${video.id}`);
        });
        
        video.addEventListener('error', (e) => {
            console.warn(`Video loading error for ${video.id}:`, e);
        });
    });
}

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VideoCarousel;
} 
