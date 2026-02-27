document.addEventListener('DOMContentLoaded', function () {
    const items = document.querySelectorAll('.home-gallery-item');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
        items.forEach(function (item) {
            item.classList.add('is-visible');
        });
        return;
    }

    items.forEach(function (item, index) {
        setTimeout(function () {
            item.classList.add('is-visible');
        }, 120 * index);
    });
});
