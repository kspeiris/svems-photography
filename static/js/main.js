document.addEventListener('DOMContentLoaded', function() {
    // ===== MOBILE NAVIGATION =====
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        });
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => closeMenu());
        });
        
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                closeMenu();
            }
        });
    }
    
    // Close the menu
    function closeMenu() {
        navMenu.classList.remove('active');
        navToggle.classList.remove('active');
        document.body.style.overflow = '';
    }

    // ===== TOUCH-OPTIMIZED GALLERY =====
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.querySelectorAll('.gallery-item, .portfolio-item').forEach(item => {
        item.addEventListener('touchstart', (e) => touchStartX = e.changedTouches[0].screenX);
        item.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) showNextImage();  // Swipe left
            else showPrevImage();           // Swipe right
        }
    }

    // ===== MOBILE-FRIENDLY LIGHTBOX =====
    function openLightbox(item) {
        const img = item.querySelector('img');
        const title = item.querySelector('h3')?.textContent || '';

        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox-overlay';
        lightbox.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.95); display: flex; align-items: center;
            justify-content: center; z-index: 9999; opacity: 0; transition: opacity 0.3s ease;
        `;

        lightbox.innerHTML = `
            <div class="lightbox-content">
                <span class="lightbox-close">×</span>
                <img src="${img.src}" alt="${title}" class="lightbox-img">
                <div class="lightbox-caption">${title}</div>
            </div>
        `;

        document.body.appendChild(lightbox);
        setTimeout(() => lightbox.style.opacity = '1', 10);
        document.body.style.overflow = 'hidden';

        lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);

        lightbox.addEventListener('touchmove', (e) => {
            if (e.touches[0].clientY - touchStartY > 100) closeLightbox();
        });

        // Keyboard Navigation (Escape to close)
        document.addEventListener('keydown', function closeOnEscape(e) {
            if (e.key === 'Escape') closeLightbox();
        });
    }

    function closeLightbox() {
        const lightbox = document.querySelector('.lightbox-overlay');
        lightbox.style.opacity = '0';
        setTimeout(() => {
            if (lightbox) lightbox.remove();
            document.body.style.overflow = '';
        }, 300);
    }

    // ===== GALLERY INTERACTIONS =====
    document.querySelectorAll('.gallery-item, .portfolio-item').forEach(item => {
        item.addEventListener('click', function(e) {
            if (!this.classList.contains('admin-gallery-item')) {
                e.preventDefault();
                openLightbox(this);
            }
        });

        // Touch feedback on gallery items
        item.addEventListener('touchstart', () => item.style.transform = 'scale(0.98)');
        item.addEventListener('touchend', () => item.style.transform = '');
    });

    // ===== FORM ENHANCEMENTS =====
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            if (window.innerWidth <= 768) {
                setTimeout(() => this.scrollIntoView({ behavior: 'smooth', block: 'center' }), 300);
            }
        });
    });

    // ===== PERFORMANCE OPTIMIZATION (Lazy Loading Images) =====
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
    }

    // ===== SMOOTH SCROLLING =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ===== MOBILE-SPECIFIC STYLES =====
    function setVH() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    setVH();
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', setVH);

    // ===== LOADING OPTIMIZATION =====
    window.addEventListener('load', function() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.style.opacity = '0';
                setTimeout(() => loadingScreen.style.display = 'none', 500);
            }
        }, 1000);

        document.body.classList.add('loaded');
    });

    // ===== NETWORK STATUS DETECTION =====
    function updateNetworkStatus() {
        const status = navigator.onLine ? 'online' : 'offline';
        document.body.classList.toggle('online', navigator.onLine);
        document.body.classList.toggle('offline', !navigator.onLine);
        
        if (!navigator.onLine) {
            showOfflineMessage();
        }
    }

    function showOfflineMessage() {
        const offlineMsg = document.createElement('div');
        offlineMsg.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; background: #f56565; 
            color: white; padding: 10px; text-align: center; z-index: 10000;
            font-weight: 500;
        `;
        offlineMsg.textContent = 'You are currently offline. Some features may not be available.';
        document.body.appendChild(offlineMsg);

        setTimeout(() => offlineMsg.remove(), 5000);
    }

    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    updateNetworkStatus();
});
