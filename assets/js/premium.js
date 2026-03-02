/**
 * TSPL Premium Micro-Interactions — v7 (Optimized)
 * ==================================================
 * - Reduced layout thrashing: getBoundingClientRect minimized.
 * - IntersectionObserver used to only process visible elements.
 * - Unified RAF loop with early exits for performance.
 */

document.addEventListener('DOMContentLoaded', () => {
    const isMobile = window.matchMedia('(pointer: coarse)').matches;
    const heroEl = document.querySelector('header');
    if (!heroEl && !document.querySelector('.apple-scroll') && !document.querySelector('.parallax-vertical')) return;

    // --- Performance Tracking ---
    const inViewElements = new Set();
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                inViewElements.add(entry.target);
            } else {
                inViewElements.delete(entry.target);
            }
        });
    }, { threshold: 0, rootMargin: '100px' });

    document.querySelectorAll('.apple-scroll, .backdrop-blur-md, .parallax-vertical, .parallax-horizontal').forEach(el => {
        observer.observe(el);
    });

    // --- Specular Sheen Logic ---
    let mouseX = 0, mouseY = 0;
    let specularActive = false;

    if (heroEl && !isMobile) {
        heroEl.addEventListener('mousemove', e => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            specularActive = true;
        }, { passive: true });
        heroEl.addEventListener('mouseleave', () => {
            specularActive = false;
            heroEl.querySelectorAll('.backdrop-blur-md').forEach(c => c.classList.remove('has-specular'));
        });
    }

    // --- Scroll Transforms Logic ---
    const heroH1 = document.querySelector('header h1');
    let targetScroll = window.scrollY;
    let lerpedScroll = targetScroll;
    let scrollVel = 0;
    let tilt = 0;

    window.addEventListener('scroll', () => {
        const current = window.scrollY;
        scrollVel = (current - targetScroll) * 0.4;
        targetScroll = current;
    }, { passive: true });

    // --- Core RAF Loop ---
    function loop() {
        // Smooth Lerp for momentum
        lerpedScroll += (targetScroll - lerpedScroll) * 0.1;
        const vh = window.innerHeight;

        // 1. Specular Card Sheen (Throttled by RAF)
        if (specularActive && heroEl) {
            inViewElements.forEach(card => {
                if (card.classList.contains('backdrop-blur-md')) {
                    const r = card.getBoundingClientRect();
                    card.style.setProperty('--mx', `${((mouseX - r.left) / r.width * 100).toFixed(1)}%`);
                    card.style.setProperty('--my', `${((mouseY - r.top) / r.height * 100).toFixed(1)}%`);
                    card.classList.add('has-specular');
                }
            });
        }

        // 2. Apple-Style Scroll Transforms + Parallax
        inViewElements.forEach(el => {
            // Apply parallax with momentum and opacity fade
            if (el.classList.contains('parallax-horizontal')) {
                const speed = parseFloat(el.getAttribute('data-parallax-speed')) || 0.1;
                const op = Math.max(0, 1 - (lerpedScroll / 600)).toFixed(2);
                el.style.transform = `translate3d(${(lerpedScroll * speed).toFixed(1)}px, 0, 0)`;
                el.style.opacity = op;
            }

            if (el.classList.contains('parallax-vertical')) {
                const speed = parseFloat(el.getAttribute('data-parallax-speed')) || 0.1;
                const sc = Math.max(0.95, 1 - (lerpedScroll / 5000)).toFixed(4);
                const op = Math.max(0, 1 - (lerpedScroll / 800)).toFixed(2);
                el.style.transform = `translate3d(0, ${(lerpedScroll * speed).toFixed(1)}px, 0) scale(${sc})`;
                el.style.opacity = op;
            }

            if (el.classList.contains('apple-scroll')) {
                const rect = el.getBoundingClientRect();
                const elementTop = rect.top;
                const elementBottom = rect.bottom;

                let progress = 0;
                const threshold = vh * 0.15;

                if (elementBottom < threshold) {
                    progress = Math.min(Math.abs(elementBottom - threshold) / threshold, 1);
                } else if (elementTop > vh - threshold) {
                    progress = Math.min(Math.abs(elementTop - (vh - threshold)) / threshold, 1);
                }

                if (progress > 0) {
                    const scale = (1 - (progress * 0.02)).toFixed(3);
                    const opacity = (1 - (progress * 1.5)).toFixed(2);
                    const blur = (progress * 12).toFixed(1);
                    el.style.transform = `scale(${scale}) translateY(${(progress * 10).toFixed(1)}px)`;
                    el.style.opacity = Math.max(opacity, 0);
                    el.style.filter = `blur(${blur}px)`;
                } else {
                    el.style.transform = 'none';
                    el.style.opacity = '1';
                    el.style.filter = 'none';
                }
            }
        });

        // 3. Hero Tilt Physics
        if (heroH1 && !isMobile) {
            scrollVel *= 0.86;
            tilt += (Math.min(Math.max(scrollVel, -10), 10) - tilt) * 0.10;

            if (Math.abs(tilt) > 0.05) {
                const speed = parseFloat(heroH1.getAttribute('data-parallax-speed') || 0);
                const px = (lerpedScroll * speed).toFixed(1);
                heroH1.style.transform = `perspective(900px) rotateX(${(-tilt * 0.5).toFixed(2)}deg) translateX(${px}px)`;
            }
        }

        requestAnimationFrame(loop);
    }

    requestAnimationFrame(loop);
});