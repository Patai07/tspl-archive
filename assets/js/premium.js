/**
 * TSPL Premium Micro-Interactions — v6 (Clean)
 * ==================================================
 * Aurora blobs removed — design is now crisp & dark.
 *
 * Kept effects:
 *  - Specular card sheen (mousemove → RAF-batched)
 *  - Scroll momentum warp (single RAF, 30fps)
 */

document.addEventListener('DOMContentLoaded', () => {
    const isMobile = window.matchMedia('(pointer: coarse)').matches;
    const heroEl = document.querySelector('header');


    // ====================================================
    // EFFECT 2: SPECULAR CARD SHEEN
    // CSS custom properties updated on mousemove, consumed
    // by a ::after pseudo-element — no layout cost.
    // ====================================================
    let specularPending = false;
    let mouseX = 0, mouseY = 0;

    if (heroEl && !isMobile) {
        heroEl.addEventListener('mousemove', e => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            specularPending = true;
        });
        heroEl.addEventListener('mouseleave', () => {
            heroEl.querySelectorAll('.backdrop-blur-md').forEach(c => c.classList.remove('has-specular'));
        });
    }

    // ====================================================
    // EFFECT 3: SCROLL MOMENTUM WARP
    // Spring-physics tilt on hero H1. Only uses transform
    // (compositor property) — no layout triggered.
    // ====================================================
    const heroH1 = document.querySelector('header h1');
    let prevScroll = window.scrollY;
    let scrollVel = 0;
    let tilt = 0;
    let frameCount = 0;

    window.addEventListener('scroll', () => {
        scrollVel = (window.scrollY - prevScroll) * 0.4;
        prevScroll = window.scrollY;
    }, { passive: true });

    // ====================================================
    // EFFECT 4: APPLE-STYLE SCROLL TRANSFORMS
    // ====================================================
    const revealElements = document.querySelectorAll('.reveal');
    const appleScrollElements = document.querySelectorAll('.apple-scroll');
    const parallaxHorizontal = document.querySelectorAll('.parallax-horizontal');
    const parallaxVertical = document.querySelectorAll('.parallax-vertical');

    const updateScrollEffects = () => {
        const scrolled = window.scrollY;
        const viewportHeight = window.innerHeight;

        // Apple-style Transition (Triggered near Top 15% and Bottom 15%)
        appleScrollElements.forEach(el => {
            const rect = el.getBoundingClientRect();
            const elementTop = rect.top;
            const elementBottom = rect.bottom;
            const elementHeight = rect.height;

            let progress = 0; // 0 is clear, 1 is fully blurred/out

            // CASE 1: Exiting Top (Top 15% of viewport height)
            const topThreshold = viewportHeight * 0.15;
            if (elementBottom < topThreshold) {
                // How far is the bottom of the element from the top margin?
                progress = Math.min(Math.abs(elementBottom - topThreshold) / topThreshold, 1);
            }

            // CASE 2: Entering/Exiting Bottom (Bottom 15% of viewport height)
            const bottomThreshold = viewportHeight * 0.85;
            if (elementTop > bottomThreshold) {
                // How far is the top of the element from the bottom margin?
                progress = Math.min(Math.abs(elementTop - bottomThreshold) / (viewportHeight - bottomThreshold), 1);
            }

            if (progress > 0) {
                const scale = 1 - (progress * 0.02); // Subtle scale
                const opacity = 1 - (progress * 1.5);
                const blur = progress * 12;
                el.style.transform = `scale(${scale.toFixed(3)}) translateY(${(progress * 10).toFixed(1)}px)`;
                el.style.opacity = Math.max(opacity, 0).toFixed(2);
                el.style.filter = `blur(${blur.toFixed(1)}px)`;
            } else {
                el.style.transform = 'scale(1) translateY(0)';
                el.style.opacity = '1';
                el.style.filter = 'none';
            }
        });

        // Horizontal Parallax
        parallaxHorizontal.forEach(el => {
            const speed = parseFloat(el.getAttribute('data-parallax-speed')) || 0.1;
            const shift = scrolled * speed;
            el.style.transform = `translateX(${shift.toFixed(1)}px)`;
        });

        // Vertical Parallax
        parallaxVertical.forEach(el => {
            const speed = parseFloat(el.getAttribute('data-parallax-speed')) || 0.1;
            const shift = scrolled * speed;
            const existingScale = el.style.transform.includes('scale') ? el.style.transform.split('translateY')[0] : '';
            el.style.transform = `${existingScale} translateY(${shift.toFixed(1)}px)`;
        });
    };

    // Single unified RAF loop — only scroll + specular
    (function loop() {
        frameCount++;

        // Specular: every frame
        if (specularPending && heroEl) {
            specularPending = false;
            heroEl.querySelectorAll('.backdrop-blur-md').forEach(card => {
                const r = card.getBoundingClientRect();
                card.style.setProperty('--mx', `${((mouseX - r.left) / r.width * 100).toFixed(1)}%`);
                card.style.setProperty('--my', `${((mouseY - r.top) / r.height * 100).toFixed(1)}%`);
                card.classList.add('has-specular');
            });
        }

        // Scroll transforms: every frame for absolute smoothness
        updateScrollEffects();

        // Hero Tilt Physics: every frame for better sync with parallax
        if (heroH1 && !isMobile) {
            scrollVel *= 0.86;
            tilt += (Math.min(Math.max(scrollVel, -10), 10) - tilt) * 0.10;

            const parallaxX = heroH1.classList.contains('parallax-horizontal')
                ? parseFloat(heroH1.getAttribute('data-parallax-speed') || 0) * window.scrollY
                : 0;

            if (Math.abs(tilt) > 0.05) {
                heroH1.style.transform = `perspective(900px) rotateX(${(-tilt * 0.5).toFixed(2)}deg) translateX(${parallaxX.toFixed(1)}px)`;
            } else {
                heroH1.style.transform = `translateX(${parallaxX.toFixed(1)}px)`;
            }
        }

        requestAnimationFrame(loop);
    })();
});