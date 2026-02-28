let currentLang = 'th';

function setLanguage(lang) {
    currentLang = lang;
    document.querySelectorAll('.lang-th').forEach(el => currentLang === 'en' ? el.classList.add('hidden') : el.classList.remove('hidden'));
    document.querySelectorAll('.lang-en').forEach(el => currentLang === 'th' ? el.classList.add('hidden') : el.classList.remove('hidden'));

    const btnTh = document.getElementById('lang-btn-th');
    const btnEn = document.getElementById('lang-btn-en');
    if (btnTh && btnEn) {
        if (currentLang === 'en') {
            btnEn.className = "px-3 py-1 rounded-full transition-all bg-[#0F2C59] text-white shadow-sm font-bold uppercase";
            btnTh.className = "px-3 py-1 rounded-full text-gray-500 font-bold hover:text-[#0F2C59] transition-all";
        } else {
            btnTh.className = "px-3 py-1 rounded-full transition-all bg-[#0F2C59] text-white shadow-sm font-bold";
            btnEn.className = "px-3 py-1 rounded-full text-gray-500 font-bold uppercase hover:text-[#0F2C59] transition-all";
        }
    }
}

function revealInit() {
    const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => entry.target.classList.add('active'), i * 80);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(r => observer.observe(r));
}

document.addEventListener('DOMContentLoaded', revealInit);