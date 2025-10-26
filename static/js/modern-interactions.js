// Modern 2025 JavaScript Interactions
class ModernPhotographySite {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupMagneticElements();
        this.setupImageReveal();
        this.setupParticleSystem();
        this.setup3DEffects();
        this.setupCursorEffects();
        this.setupPageTransitions();
    }

    // Scroll-triggered animations
    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    
                    // Stagger children animations
                    if (entry.target.classList.contains('stagger-container')) {
                        const children = entry.target.children;
                        Array.from(children).forEach((child, index) => {
                            setTimeout(() => {
                                child.classList.add('animate-in');
                            }, index * 100);
                        });
                    }
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        document.querySelectorAll('.scroll-reveal, .stagger-container').forEach(el => {
            observer.observe(el);
        });

        // Scroll progress
        window.addEventListener('scroll', () => {
            const progress = document.querySelector('.scroll-progress');
            if (progress) {
                const winHeight = window.innerHeight;
                const docHeight = document.documentElement.scrollHeight;
                const scrollTop = window.pageYOffset;
                const scrollPercent = (scrollTop / (docHeight - winHeight)) * 100;
                progress.style.transform = `scaleX(${scrollPercent / 100})`;
            }
        });
    }

    // Magnetic cursor effects
    setupMagneticElements() {
        const magneticElements = document.querySelectorAll('.magnetic-element');
        
        magneticElements.forEach(element => {
            element.addEventListener('mousemove', (e) => {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const deltaX = (x - centerX) / centerX;
                const deltaY = (y - centerY) / centerY;
                
                element.style.transform = `translate(${deltaX * 10}px, ${deltaY * 10}px)`;
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.transform = 'translate(0, 0)';
            });
        });
    }

    // Image reveal on load
    setupImageReveal() {
        const images = document.querySelectorAll('.image-reveal');
        
        images.forEach(img => {
            img.addEventListener('load', () => {
                img.classList.add('revealed');
            });
        });
    }

    // Dynamic particle system
    setupParticleSystem() {
        const hero = document.querySelector('.hero-2025');
        if (!hero) return;

        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles-container';
        hero.appendChild(particlesContainer);

        for (let i = 0; i < 20; i++) {
            this.createParticle(particlesContainer);
        }
    }

    createParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        const size = Math.random() * 6 + 2;
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        const delay = Math.random() * 5;
        const duration = Math.random() * 10 + 5;
        
        particle.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${posX}%;
            top: ${posY}%;
            animation-delay: ${delay}s;
            animation-duration: ${duration}s;
            opacity: ${Math.random() * 0.3 + 0.1};
        `;
        
        container.appendChild(particle);
    }

    // 3D transform effects
    setup3DEffects() {
        const cards = document.querySelectorAll('.card-3d');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateY = (x - centerX) / 10;
                const rotateX = (centerY - y) / 10;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            });
        });
    }

    // Custom cursor effects
    setupCursorEffects() {
        if (window.matchMedia('(pointer: fine)').matches) {
            const cursor = document.createElement('div');
            cursor.className = 'custom-cursor';
            document.body.appendChild(cursor);

            document.addEventListener('mousemove', (e) => {
                cursor.style.left = e.clientX + 'px';
                cursor.style.top = e.clientY + 'px';
            });

            document.querySelectorAll('a, button, .magnetic-element').forEach(el => {
                el.addEventListener('mouseenter', () => {
                    cursor.classList.add('hover');
                });
                el.addEventListener('mouseleave', () => {
                    cursor.classList.remove('hover');
                });
            });
        }
    }

    // Smooth page transitions
    setupPageTransitions() {
        document.querySelectorAll('a[href^="/"]').forEach(link => {
            link.addEventListener('click', (e) => {
                if (link.href && !link.target && link.hostname === window.location.hostname) {
                    e.preventDefault();
                    
                    // Add page transition
                    document.body.style.opacity = '0';
                    document.body.style.transition = 'opacity 0.3s ease';
                    
                    setTimeout(() => {
                        window.location.href = link.href;
                    }, 300);
                }
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ModernPhotographySite();
});

// Add modern loading states
document.addEventListener('DOMContentLoaded', () => {
    // Add loading states to buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function() {
            this.classList.add('loading');
            setTimeout(() => {
                this.classList.remove('loading');
            }, 2000);
        });
    });
});