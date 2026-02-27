document.addEventListener('DOMContentLoaded', function () {
    const bars = document.querySelectorAll('.about-pro-skill-fill');
    const values = document.querySelectorAll('.about-pro-value-card');
    const steps = document.querySelectorAll('.about-pro-step');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const animateBars = function () {
        bars.forEach(function (bar) {
            const level = bar.getAttribute('data-level') || '0';
            bar.style.width = `${Math.max(0, Math.min(100, Number(level)))}%`;
        });
    };

    const revealList = function (elements, className, staggerMs) {
        elements.forEach(function (el, idx) {
            setTimeout(function () {
                el.classList.add(className);
            }, idx * staggerMs);
        });
    };

    if (prefersReducedMotion) {
        animateBars();
        revealList(values, 'is-visible', 0);
        revealList(steps, 'is-visible', 0);
        return;
    }

    if (!('IntersectionObserver' in window)) {
        animateBars();
        revealList(values, 'is-visible', 120);
        revealList(steps, 'is-visible', 120);
        return;
    }

    const expertiseObserver = new IntersectionObserver(
        function (entries, obs) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                animateBars();
                obs.disconnect();
            });
        },
        { threshold: 0.2 }
    );

    const section = document.querySelector('.about-pro-expertise');
    if (section) expertiseObserver.observe(section);

    const valuesSection = document.querySelector('.about-pro-values');
    if (valuesSection) {
        const valuesObserver = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    revealList(values, 'is-visible', 100);
                    obs.disconnect();
                });
            },
            { threshold: 0.2 }
        );
        valuesObserver.observe(valuesSection);
    }

    const processSection = document.querySelector('.about-pro-process');
    if (processSection) {
        const processObserver = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    revealList(steps, 'is-visible', 120);
                    obs.disconnect();
                });
            },
            { threshold: 0.2 }
        );
        processObserver.observe(processSection);
    }
});
