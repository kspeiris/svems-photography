document.addEventListener('DOMContentLoaded', function () {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const mobileOverlay = document.getElementById('mobileOverlay');
    const navbar = document.querySelector('.navbar');
    const loadingScreen = document.getElementById('loading-screen');
    const mobileMenuTarget = mobileOverlay || navMenu;

    function closeMenu() {
        if (!navToggle) return;
        if (navMenu) navMenu.classList.remove('active');
        if (mobileOverlay) {
            mobileOverlay.classList.remove('is-open', 'translate-x-0');
            mobileOverlay.classList.add('hidden', 'translate-x-full', 'pointer-events-none');
            mobileOverlay.setAttribute('aria-hidden', 'true');
        }
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('menu-open');
        document.body.style.overflow = '';
    }

    if (navToggle) {
        navToggle.addEventListener('click', function () {
            const isOpen = navToggle.classList.toggle('active');
            if (navMenu) navMenu.classList.toggle('active', isOpen);
            if (mobileOverlay) {
                mobileOverlay.classList.remove('hidden');
                mobileOverlay.classList.toggle('is-open', isOpen);
                mobileOverlay.classList.toggle('translate-x-0', isOpen);
                mobileOverlay.classList.toggle('translate-x-full', !isOpen);
                mobileOverlay.classList.toggle('pointer-events-none', !isOpen);
                if (!isOpen) {
                    mobileOverlay.classList.add('hidden');
                }
                mobileOverlay.setAttribute('aria-hidden', String(!isOpen));
            }
            navToggle.classList.toggle('active', isOpen);
            navToggle.setAttribute('aria-expanded', String(isOpen));
            document.body.classList.toggle('menu-open', isOpen);
            document.body.style.overflow = isOpen ? 'hidden' : '';
        });

        document.querySelectorAll('.mobile-link, #navMenu .nav-link').forEach(function (link) {
            link.addEventListener('click', closeMenu);
        });

        document.addEventListener('click', function (event) {
            const clickedOutsideToggle = !navToggle.contains(event.target);
            const clickedOutsideMenu = !mobileMenuTarget || !mobileMenuTarget.contains(event.target);
            if (clickedOutsideToggle && clickedOutsideMenu) {
                closeMenu();
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') closeMenu();
        });
    }

    window.addEventListener('scroll', function () {
        if (!navbar) return;
        navbar.classList.toggle('scrolled', window.scrollY > 20);
    });

    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (event) {
            const href = anchor.getAttribute('href');
            if (!href) return;
            if (href === '#') {
                event.preventDefault();
                return;
            }
            const target = document.querySelector(href);
            if (!target) return;

            event.preventDefault();
            const headerOffset = 80;
            const top = target.getBoundingClientRect().top + window.scrollY - headerOffset;
            window.scrollTo({ top, behavior: 'smooth' });
        });
    });

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                const img = entry.target;
                const src = img.getAttribute('data-src');
                if (src) img.src = src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            });
        });

        document.querySelectorAll('img[data-src]').forEach(function (img) {
            imageObserver.observe(img);
        });
    }

    const hasDedicatedLightbox = Boolean(document.getElementById('lightbox'));
    if (!hasDedicatedLightbox) {
        document.querySelectorAll('.gallery-item').forEach(function (item) {
            item.addEventListener('click', function () {
                const img = item.querySelector('img');
                if (!img) return;

                const titleElement = item.querySelector('h3');
                const title = titleElement ? titleElement.textContent.trim() : '';

                const overlay = document.createElement('div');
                overlay.className = 'lightbox-overlay';
                overlay.innerHTML = `
                    <div class="lightbox-content">
                        <button type="button" class="lightbox-close" aria-label="Close lightbox">&times;</button>
                        <img src="${img.src}" alt="${title}">
                        <div class="lightbox-caption">${title}</div>
                    </div>
                `;

                function closeLightbox() {
                    overlay.remove();
                    document.body.style.overflow = '';
                    document.removeEventListener('keydown', onKeyDown);
                }

                function onKeyDown(event) {
                    if (event.key === 'Escape') closeLightbox();
                }

                overlay.addEventListener('click', function (event) {
                    if (event.target === overlay || event.target.classList.contains('lightbox-close')) {
                        closeLightbox();
                    }
                });

                document.addEventListener('keydown', onKeyDown);
                document.body.appendChild(overlay);
                document.body.style.overflow = 'hidden';
            });
        });
    }

    function setViewportUnit() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    setViewportUnit();
    window.addEventListener('resize', setViewportUnit);
    window.addEventListener('orientationchange', setViewportUnit);

    function updateNetworkStatus() {
        document.body.classList.toggle('online', navigator.onLine);
        document.body.classList.toggle('offline', !navigator.onLine);

        let banner = document.getElementById('networkBanner');
        if (!navigator.onLine && !banner) {
            banner = document.createElement('div');
            banner.id = 'networkBanner';
            banner.textContent = 'You are offline. Some features may not be available.';
            banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:10000;background:#b91c1c;color:#fff;padding:10px;text-align:center;';
            document.body.appendChild(banner);
        }
        if (navigator.onLine && banner) {
            banner.remove();
        }
    }

    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    updateNetworkStatus();

    document.querySelectorAll('.flash-close').forEach(function (button) {
        button.addEventListener('click', function () {
            const flash = button.closest('.flash-message');
            if (flash) flash.remove();
        });
    });

    window.addEventListener('load', function () {
        if (!loadingScreen) return;
        setTimeout(function () {
            loadingScreen.style.opacity = '0';
            setTimeout(function () {
                loadingScreen.style.display = 'none';
            }, 400);
        }, 400);
    });
});
