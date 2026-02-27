document.addEventListener('DOMContentLoaded', function() {
    // ===== PORTFOLIO FILTERING =====
    const filterButtons = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    const portfolioGrid = document.getElementById('portfolioGrid');
    const filterContainer = document.querySelector('.category-filter');
    const portfolioCount = document.getElementById('portfolioCount');

    if (!portfolioGrid) {
        return;
    }

    // Delegate filter button clicks for performance
    filterContainer?.addEventListener('click', function(e) {
        const clickedButton = e.target.closest('.filter-btn');
        if (!clickedButton) return;

        filterButtons.forEach(button => button.classList.remove('active'));
        clickedButton.classList.add('active');
        filterButtons.forEach(button => button.setAttribute('aria-pressed', button === clickedButton ? 'true' : 'false'));

        const filterValue = clickedButton.getAttribute('data-filter');
        let visibleCount = 0;

        portfolioItems.forEach(item => {
            if (filterValue === 'all' || item.getAttribute('data-category') === filterValue) {
                showItem(item);
                visibleCount += 1;
            } else {
                hideItem(item);
            }
        });

        if (portfolioCount) {
            portfolioCount.textContent = `${visibleCount} image${visibleCount === 1 ? '' : 's'}`;
        }
    });

    function showItem(item) {
        item.style.display = 'block';
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'scale(1)';
        }, 100);
    }

    function hideItem(item) {
        item.style.opacity = '0';
        item.style.transform = 'scale(0.8)';
        setTimeout(() => {
            item.style.display = 'none';
        }, 300);
    }

    // ===== LIGHTBOX FUNCTIONALITY =====
    const lightbox = document.getElementById('lightbox');
    const lightboxImage = document.getElementById('lightbox-image');
    const lightboxTitle = document.getElementById('lightbox-title');
    const lightboxDescription = document.getElementById('lightbox-description');
    const lightboxClose = document.querySelector('.lightbox-close');
    const lightboxPrev = document.querySelector('.lightbox-prev');
    const lightboxNext = document.querySelector('.lightbox-next');

    let currentImageIndex = 0;
    const images = Array.from(portfolioItems);

    function openLightbox(index) {
        if (!lightbox || !lightboxImage || !lightboxTitle || !lightboxDescription) return;
        const item = images[index];
        if (!item) return;
        const img = item.querySelector('img');
        if (!img) return;
        const title = item.querySelector('h3').textContent;
        const description = item.querySelector('p').textContent;

        lightboxImage.src = img.src;
        lightboxTitle.textContent = title;
        lightboxDescription.textContent = description;
        currentImageIndex = index;

        lightbox.style.display = 'flex';
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        if (!lightbox) return;
        lightbox.style.display = 'none';
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = 'auto';
    }

    function showNextImage() {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        openLightbox(currentImageIndex);
    }

    function showPrevImage() {
        currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
        openLightbox(currentImageIndex);
    }

    portfolioItems.forEach((item, index) => {
        item.addEventListener('click', () => openLightbox(index));
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openLightbox(index);
            }
        });
    });

    lightboxClose?.addEventListener('click', closeLightbox);
    lightboxNext?.addEventListener('click', showNextImage);
    lightboxPrev?.addEventListener('click', showPrevImage);

    document.addEventListener('keydown', function(e) {
        if (lightbox.style.display === 'flex') {
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowRight') showNextImage();
            if (e.key === 'ArrowLeft') showPrevImage();
        }
    });

    lightbox?.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    // ===== IMAGE LAZY LOADING WITH INTERSECTION OBSERVER =====
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

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // ===== TOUCH EVENTS FOR GALLERY ITEMS =====
    const galleryItems = document.querySelectorAll('.gallery-item, .portfolio-item');
    galleryItems.forEach(item => {
        item.addEventListener('touchstart', () => {
            item.style.transform = 'scale(0.98)';
        });
        item.addEventListener('touchend', () => {
            item.style.transform = '';
        });
    });
});
