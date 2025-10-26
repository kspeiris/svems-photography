document.addEventListener('DOMContentLoaded', function () {

    // ===== PRELOADER ANIMATION =====
    function hidePreloader() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.transition = 'opacity 0.5s ease';
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
                document.body.classList.add('loaded');
            }, 500);
        }
    }

    window.addEventListener('load', hidePreloader);

    // ===== ADVANCED NAVIGATION =====
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;

    function toggleNavbarVisibility() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
            // Hide navbar on scroll down, show on scroll up
            if (window.scrollY > lastScrollY && window.scrollY > 200) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }
        } else {
            navbar.classList.remove('scrolled');
            navbar.style.transform = 'translateY(0)';
        }

        lastScrollY = window.scrollY;
    }

    // Debounced scroll handler for better performance
    let debounceTimer;
    window.addEventListener('scroll', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            toggleNavbarVisibility();
            parallaxEffect();
            updateProgressBar();
        }, 100);
    });

    // ===== Parallax Effect for Hero Section =====
    function parallaxEffect() {
        const hero = document.querySelector('.hero');
        if (hero) {
            const scrolled = window.pageYOffset;
            const parallaxSpeed = 0.5;
            hero.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
        }
    }

    // ===== Progress Bar =====
    function updateProgressBar() {
        const winHeight = window.innerHeight;
        const docHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset;
        const progress = (scrollTop / (docHeight - winHeight)) * 100;

        let progressBar = document.getElementById('reading-progress');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.id = 'reading-progress';
            progressBar.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                height: 3px;
                background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
                z-index: 1001;
                transition: width 0.1s ease;
            `;
            document.body.appendChild(progressBar);
        }
        progressBar.style.width = `${progress}%`;
    }

    // ===== SMOOTH SCROLLING ENHANCEMENT =====
    function smoothScrollTo(targetPosition, duration) {
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = easeInOutCubic(timeElapsed, startPosition, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        }

        function easeInOutCubic(t, b, c, d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t * t + b;
            t -= 2;
            return c / 2 * (t * t * t + 2) + b;
        }

        requestAnimationFrame(animation);
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                smoothScrollTo(offsetPosition, 800);
            }
        });
    });

    // ===== ADVANCED INTERSECTION OBSERVER =====
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const scrollObserver = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                animateChildElements(entry.target);
                animateSkillBars(entry.target);
            }
        });
    }, observerOptions);

    function animateChildElements(target) {
        if (target.classList.contains('gallery-grid') || target.classList.contains('services-grid')) {
            const children = target.children;
            Array.from(children).forEach((child, index) => {
                setTimeout(() => {
                    child.classList.add('animate-in');
                }, index * 100);
            });
        }
    }

    function animateSkillBars(target) {
        if (target.classList.contains('skill-level')) {
            const width = target.getAttribute('data-width') || target.style.width;
            target.style.width = '0';
            setTimeout(() => {
                target.style.width = width;
                target.style.transition = 'width 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
            }, 300);
        }
    }

    // Observe all animatable elements
    document.querySelectorAll(
        '.service-card, .gallery-item, .testimonial-card, .stat-item, .skill-level, .about-grid, .contact-grid, .gallery-grid, .services-grid'
    ).forEach(el => {
        scrollObserver.observe(el);
    });

    // ===== TYPING ANIMATION =====
    function initTypingAnimation() {
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle && !heroTitle.classList.contains('typed')) {
            const originalText = heroTitle.textContent;
            heroTitle.classList.add('typed');
            typeWriter(heroTitle, originalText, 80);
        }
    }

    function typeWriter(element, text, speed = 100) {
        let i = 0;
        element.innerHTML = '';
        element.style.borderRight = '2px solid var(--gold-color)';
        
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                setTimeout(() => {
                    element.style.borderRight = 'none';
                }, 500);
            }
        }
        type();
    }

    // ===== IMAGE LAZY LOADING WITH BLUR EFFECT =====
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.filter = 'blur(10px)';
                img.style.transition = 'filter 0.5s ease';
                img.src = img.dataset.src;
                img.classList.remove('lazy');

                img.addEventListener('load', () => {
                    img.style.filter = 'blur(0)';
                    setTimeout(() => {
                        img.style.transition = 'none';
                    }, 500);
                });

                observer.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        if (!img.src) {
            img.style.background = '#f0f0f0';
            img.style.minHeight = '200px';
        }
        imageObserver.observe(img);
    });

    // ===== PARTICLE EFFECT =====
    function createParticles() {
        const hero = document.querySelector('.hero');
        if (!hero) return;

        const existingParticles = hero.querySelectorAll('.particle');
        existingParticles.forEach(particle => particle.remove());

        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 6 + 2}px;
                height: ${Math.random() * 6 + 2}px;
                background: rgba(255, 255, 255, ${Math.random() * 0.4});
                border-radius: 50%;
                top: ${Math.random() * 100}%;
                left: ${Math.random() * 100}%;
                animation: floatParticle ${Math.random() * 15 + 10}s linear infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            hero.appendChild(particle);
        }
    }

    // ===== FORM ENHANCEMENTS =====
    function enhanceForms() {
        const formInputs = document.querySelectorAll('.form-group input, .form-group textarea');
        
        formInputs.forEach(input => {
            const label = input.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                input.addEventListener('focus', () => {
                    label.classList.add('active');
                    input.parentElement.classList.add('focused');
                });
                
                input.addEventListener('blur', () => {
                    if (!input.value) {
                        label.classList.remove('active');
                    }
                    input.parentElement.classList.remove('focused');
                });

                if (input.value) {
                    label.classList.add('active');
                }
            }

            input.addEventListener('input', function () {
                validateField(this);
            });
        });
    }

    function validateField(field) {
        const value = field.value.trim();
        
        if (field.type === 'email') {
            const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            field.classList.toggle('valid', isValid && value);
            field.classList.toggle('invalid', !isValid && value);
        }
        
        if (field.type === 'text' || field.tagName === 'TEXTAREA') {
            const isValid = value.length >= 2;
            field.classList.toggle('valid', isValid && value);
            field.classList.toggle('invalid', !isValid && value);
        }
    }

    // ===== INITIALIZE EVERYTHING =====
    function init() {
        initTypingAnimation();
        enhanceForms();
        createScrollToTop();
        createParticles();
    }

    // Start everything
    init();

});
