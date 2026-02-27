document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.querySelector('.navbar');
    const hero = document.querySelector('.hero');
    let lastScrollY = window.scrollY;

    function hidePreloader() {
        const loadingScreen = document.getElementById('loading-screen');
        if (!loadingScreen) return;
        loadingScreen.style.opacity = '0';
        setTimeout(function () {
            loadingScreen.style.display = 'none';
            document.body.classList.add('loaded');
        }, 400);
    }

    window.addEventListener('load', hidePreloader);

    function onScroll() {
        if (navbar) {
            const scrollingDown = window.scrollY > lastScrollY;
            navbar.classList.toggle('scrolled', window.scrollY > 20);
            navbar.style.transform = scrollingDown && window.scrollY > 220 ? 'translateY(-100%)' : 'translateY(0)';
        }

        if (hero && window.innerWidth > 768) {
            const y = Math.min(window.scrollY * 0.2, 120);
            hero.style.backgroundPosition = `center calc(50% + ${y}px)`;
        }

        updateProgressBar();
        lastScrollY = window.scrollY;
    }

    function updateProgressBar() {
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = docHeight > 0 ? (window.scrollY / docHeight) * 100 : 0;
        let progressBar = document.getElementById('reading-progress');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.id = 'reading-progress';
            progressBar.style.cssText = 'position:fixed;top:0;left:0;height:3px;z-index:1001;background:linear-gradient(90deg,var(--primary-color),var(--accent-color));';
            document.body.appendChild(progressBar);
        }
        progressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
    }

    let scrollTimer;
    window.addEventListener('scroll', function () {
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(onScroll, 20);
    });

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        },
        { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.service-card, .gallery-item, .testimonial-card, .stat-item').forEach(function (el) {
        observer.observe(el);
    });

    onScroll();
});

