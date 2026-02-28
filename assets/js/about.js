let currentLang = 'th';

        function setLanguage(lang) { }

        // Add Gimmick: Scroll Reveal
        function revealInit() {
            const reveals = document.querySelectorAll('.reveal');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('active');
                    }
                });
            }, { threshold: 0.1 });

            reveals.forEach(r => observer.observe(r));
        }

        // Add Gimmick: Parallax
        function initParallax() {
            window.addEventListener('scroll', () => {
                const scrolled = window.scrollY;
                document.querySelectorAll('.parallax').forEach(el => {
                    const speed = el.getAttribute('data-speed') || 0.5;
                    el.style.transform = `translateY(${scrolled * speed}px)`;
                });
            });
        }

        window.onload = () => {
            revealInit();
            initParallax();
        };