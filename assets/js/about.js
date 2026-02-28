let currentLang = 'th';

        function setLanguage(lang) {
            currentLang = lang;
            document.querySelectorAll('.lang-th').forEach(el => currentLang === 'en' ? el.classList.add('hidden') : el.classList.remove('hidden'));
            document.querySelectorAll('.lang-en').forEach(el => currentLang === 'th' ? el.classList.add('hidden') : el.classList.remove('hidden'));

            const btnTh = document.getElementById('lang-btn-th');
            const btnEn = document.getElementById('lang-btn-en');

            // Apple styling toggle colors
            if (btnTh && btnEn) {
                if (currentLang === 'en') {
                    btnEn.className = "px-3 py-1 rounded-full transition-all bg-[#1d1d1f] text-white shadow-sm font-bold uppercase";
                    btnTh.className = "px-3 py-1 rounded-full text-[#86868b] font-bold hover:text-[#1d1d1f] transition-all";
                } else {
                    btnTh.className = "px-3 py-1 rounded-full transition-all bg-[#1d1d1f] text-white shadow-sm font-bold";
                    btnEn.className = "px-3 py-1 rounded-full text-[#86868b] font-bold uppercase hover:text-[#1d1d1f] transition-all";
                }
            }
        }

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