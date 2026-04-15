let currentLang = 'th';

const toThaiDigits = (num) => {
    const thaiNumbers = ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙'];
    return num.toString().split('').map(char => thaiNumbers[char] || char).join('');
};

let RECORDS = [];
const CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvalU42uqVFSoJ3O-WkoaQCBVmiawl7DHNO-DNsYL3iiWfxKERjiQI4SpiVqDxzEYLPlLFJTqSFCy/pub?gid=494156669&single=true&output=csv&t=' + new Date().getTime(); 

/**
 * LOAD DATA: หัวใจหลักของระบบ
 * ทำการดึงข้อมูลจากไฟล์ CSV (หรือ Google Sheets) 
 * และแปลงข้อมูลให้อยู่ในรูปแบบที่เว็บไซต์เข้าใจ
 */
async function loadData() {
    return new Promise((resolve) => {
        Papa.parse(CSV_URL, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: function (results) {
                const mappedData = results.data.map(row => {
                    const images = [];
                    if (row['Image Main']) images.push({ url: row['Image Main'], type: 'original' });
                    if (row['Image Vector']) images.push({ url: row['Image Vector'], type: 'vector' });
                    if (row['Image Context']) images.push({ url: row['Image Context'], type: 'original' }); // Default to original for display
                    if (row['Image Mid']) images.push({ url: row['Image Mid'], type: 'original' });
                    if (row['Image Detail']) images.push({ url: row['Image Detail'], type: 'original' });

                    return {
                        id: row['Symbol ID'] || Object.values(row)[0] || "Unknown ID",
                        title: { th: row['Title (TH)'] || "", en: row['Title (EN)'] || "" },
                        category: row['Category'] || "Uncategorized",
                        location: row['Location'] || "-",
                        confidence: row['Confidence'] || "Verified",
                        ethics: row['Ethics'] || "low",
                        connotation: { th: row['Connotation (TH)'] || "", en: row['Connotation (EN)'] || "" },
                        protocol: { preserve: row['Protocol Preserve'] || "", donot: row['Protocol Do Not'] || "" },
                        morphemes: {
                            th: (row['Morphemes (TH)'] || "").split('|').map(s => s.trim()).filter(s => s),
                            en: (row['Morphemes (EN)'] || "").split('|').map(s => s.trim()).filter(s => s)
                        },
                        tags: (row['Tags'] || "").split(',').map(s => s.trim()).filter(s => s),
                        images: images.length > 0 ? images : [{ url: "https://placehold.co/800x600/0F2C59/D4AF37?text=No+Image", type: "original" }]
                    };
                });
                RECORDS = mappedData.filter(item => item.id !== "Unknown ID" && item.id.trim() !== "");
                resolve(RECORDS);
            },
            error: function (err) {
                console.warn("CSV Loading failed, using fallback data. Error:", err);
                // Fallback can be defined here if needed
                resolve([]);
            }
        });
    });
}





const CATEGORIES = [
    "All", 
    "Nature & Botany", 
    "Fauna & Mythical", 
    "Geometric & Synthetic", 
    "Sacred & Belief"
];
const CATEGORY_LABEL = {
    "All": { th: "ทั้งหมด", en: "All Patterns" },
    "Nature & Botany": { th: "พรรณพฤกษาและธรรมชาติ", en: "Nature & Botany" },
    "Fauna & Mythical": { th: "สรรพสัตว์และสัตว์หิมพานต์", en: "Fauna & Mythical" },
    "Geometric & Synthetic": { th: "เรขาคณิตและลวดลายประดิษฐ์", en: "Geometric & Synthetic" },
    "Sacred & Belief": { th: "ความเชื่อและสิ่งศักดิ์สิทธิ์", en: "Sacred & Belief" }
};
let activeCategory = "All", activeRecord = null, currentSlideIndex = 0, currentViewMode = "original";

async function init() {
    initParticles();
    await loadData(); // Load CSV data before rendering

    updateCounters(); // Sync totals to UI
    renderCategories();
    renderGrid();
    updateLegend();
    setupHeroGlow();

    // Clear preloader once data is loaded
    const preloader = document.getElementById('preloader');
    if (preloader) {
        setTimeout(() => {
            preloader.classList.add('opacity-0');
            setTimeout(() => preloader.style.display = 'none', 500);
        }, 300);
    }
}

function updateCounters() {
    const totalRecords = RECORDS.length;
    let totalMorphemes = 0;
    RECORDS.forEach(r => {
        totalMorphemes += (r.morphemes.th ? r.morphemes.th.length : 0);
    });

    // Update Hero Stats
    const morphemeCounter = document.querySelector('.counter[data-target="180"]');
    const recordCounter = document.querySelector('.counter[data-target="45"]');

    if (morphemeCounter) morphemeCounter.dataset.target = totalMorphemes;
    if (recordCounter) recordCounter.dataset.target = totalRecords;

    // Update Ticker values if they exist
    document.querySelectorAll('.ticker-item-value').forEach(el => {
        if (el.innerText.includes('ระเบียนข้อมูล') && el.innerText.includes('+')) {
            el.innerText = (currentLang === 'th' ? toThaiDigits(totalRecords) : totalRecords) + "+ ระเบียนข้อมูล";
        }
    });
}

function setupHeroGlow() {
    const glow = document.getElementById('hero-glow');
    document.addEventListener('mousemove', (e) => {
        if (glow) { glow.style.left = e.clientX + 'px'; glow.style.top = e.clientY + 'px'; glow.style.opacity = 1; }
    });
}

function animateCounters() {
    document.querySelectorAll('.counter').forEach(c => {
        const target = +c.dataset.target, increment = target / 300;
        let curr = 0;
        const update = () => {
            curr += increment;
            if (curr < target) {
                const val = Math.ceil(curr);
                c.innerText = currentLang === 'th' ? toThaiDigits(val) : val;
                requestAnimationFrame(update);
            } else {
                c.innerText = currentLang === 'th' ? toThaiDigits(target) : target;
            }
        };
        update();
    });
}

function updateLegend() {
    const container = document.getElementById('status-legend');
    if (!container) return;
    const items = [
        { color: 'bg-emerald-500', th: 'ตรวจสอบแล้ว', en: 'Verified' },
        { color: 'bg-blue-500', th: 'สันนิษฐานรูปแบบ', en: 'Reconstructed' },
        { color: 'bg-amber-500', th: 'ส่วนชิ้นส่วน', en: 'Fragment' },
        { color: 'bg-purple-500', th: 'สมมติฐาน', en: 'Hypothetical' }
    ];
    container.innerHTML = items.map(i => `<div class="flex items-center gap-3"><span class="w-2.5 rounded-full h-2.5 ${i.color}"></span><span class="text-[#0F2C59] font-bold uppercase tracking-widest text-[8px]">${currentLang === 'th' ? i.th : i.en}</span></div>`).join('');
}

/**
 * RENDER CATEGORIES: สร้างแถบเลือกหมวดหมู่ด้านบน
 * ดึงชื่อหมวดหมู่ที่ใช้ได้มาจาก CSV และสร้างปุ่มกรองข้อมูล
 */
function renderCategories() {
    const container = document.getElementById('categories-container');
    if (!container) return;
    container.innerHTML = `<span class="text-[9px] font-bold text-gray-400 mr-2 tracking-[0.3em] uppercase">${currentLang === "th" ? "กรองหมวด" : "Filter"}</span>`;
    CATEGORIES.forEach(cat => {
        const btn = document.createElement('button');
        const isActive = cat === activeCategory;
        btn.className = `px-5 py-2 rounded-lg text-[9px] font-bold uppercase tracking-widest transition-all border ${isActive ? 'bg-[#0F2C59] text-white border-[#0F2C59] shadow-md' : 'bg-white text-gray-500 border-gray-200 hover:border-[#0F2C59]/30 hover:text-[#0F2C59]'}`;
        btn.innerText = (CATEGORY_LABEL[cat] ? CATEGORY_LABEL[cat][currentLang] : cat);
        btn.onclick = () => { activeCategory = cat; renderCategories(); renderGrid(); };
        container.appendChild(btn);
    });
}

/**
 * RENDER GRID: ส่วนที่ทำหน้าที่ "วาด" ลวดลายลงบนหน้าเว็บ
 * มีการจัดการเรื่องสัดส่วนรูปภาพ 4:3 และการค้นหาแบบ Real-time
 */
function renderGrid(filterText = "") {
    const container = document.getElementById('grid-container');
    if (!container) return;
    container.innerHTML = '';

    let filtered = RECORDS.filter(r => {
        const matchesCat = activeCategory === "All" || r.category === activeCategory;
        const titleText = ((r.title.th || "") + (r.title.en || "")).toLowerCase();
        const idText = (r.id || "").toLowerCase();
        const locationText = (r.location || "").toLowerCase();
        const tagsText = (r.tags || []).join(" ").toLowerCase();
        
        const searchTarget = `${titleText} ${idText} ${locationText} ${tagsText}`;
        return matchesCat && searchTarget.includes(filterText.toLowerCase());
    });

    // Limit to 8 items on index.html
    const isArchivePage = window.location.pathname.includes('archive.html');
    if (!isArchivePage) {
        filtered = filtered.slice(0, 8);
    }

    if (filtered.length === 0) {
        container.innerHTML = `
                    <div class="col-span-full py-20 flex flex-col items-center justify-center text-center w-full">
                        <i class="ph ph-magnifying-glass text-6xl text-gray-300 mb-4"></i>
                        <p class="text-[#0F2C59] font-bold text-lg mb-2">${currentLang === 'th' ? 'ไม่พบระเบียนข้อมูลที่ตรงกับคำค้นหา' : 'No Records Found'}</p>
                        <p class="text-gray-400 text-sm">${currentLang === 'th' ? 'ลองปรับเปลี่ยนคำค้นหาหรือหมวดหมู่ใหม่' : 'Try adjusting your search or category filter.'}</p>
                    </div>
                `;
        return;
    }

    filtered.forEach(record => {
        const item = document.createElement('div');
        item.className = "pattern-card group relative cursor-pointer flex flex-col bg-white rounded-3xl overflow-hidden text-[#0F2C59]";
        item.tabIndex = 0;
        item.onclick = () => openModal(record);
        item.onkeydown = (e) => { if (e.key === 'Enter') openModal(record); };

        const confidenceMap = {
            'Verified': { th: 'ตรวจสอบแล้ว', en: 'Verified', color: 'text-emerald-600', dot: 'bg-emerald-500' },
            'Reconstructed': { th: 'สันนิษฐานรูปแบบ', en: 'Reconstructed', color: 'text-blue-600', dot: 'bg-blue-500' },
            'Fragment': { th: 'ส่วนชิ้นส่วน', en: 'Fragment', color: 'text-amber-600', dot: 'bg-amber-500' },
            'Hypothetical': { th: 'สมมติฐาน', en: 'Hypothetical', color: 'text-purple-600', dot: 'bg-purple-500' }
        };
        let statusInfo = confidenceMap[record.confidence] || confidenceMap['Verified'];
        let statusText = currentLang === 'th' ? statusInfo.th : statusInfo.en;
        let statusColor = statusInfo.color;

        item.innerHTML = `
                    <div class="relative aspect-[4/3] overflow-hidden">
                        <img src="${record.images[0].url}" alt="${record.title[currentLang]}" 
                             class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-[cubic-bezier(0.23,1,0.32,1)]">
                        <div class="absolute inset-0 bg-gradient-to-t from-[#0F172A]/80 via-transparent to-transparent opacity-60"></div>
                        
                        <!-- Confidence Marker -->
                        <div class="absolute top-5 left-5">
                            <span class="px-3 py-1.5 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 text-[7px] font-black uppercase tracking-[0.2em] text-white flex items-center gap-2">
                                <span class="w-1.5 h-1.5 rounded-full ${statusColor} shadow-[0_0_8px_currentColor]"></span>
                                <span class="opacity-80">${statusText}</span>
                            </span>
                        </div>
                            <div class="bg-white/15 backdrop-blur-md text-white px-4 py-2 rounded-xl text-[8px] font-bold uppercase tracking-[0.3em] flex items-center gap-2 border border-white/20">
                                ${currentLang === "th" ? "วิเคราะห์" : "Analysis"} <i class="ph ph-arrow-right" style="color:${palette.accent}"></i>
                            </div>
                        </div>
                        <!-- ID Watermark -->
                        <div class="absolute bottom-5 left-5 text-[7px] font-mono tracking-widest opacity-30 text-white">${record.id}</div>
                    </div>
                    <div class="p-6 md:p-8">
                        <div class="text-[9px] text-gray-400 font-mono mb-2 uppercase tracking-[0.2em] font-bold"><span class="scramble-hover" data-text="${record.id}">${record.id}</span></div>
                        <h3 class="text-base font-bold text-[#0F2C59] mb-3 leading-[1.25] tracking-tight uppercase">${record.title[currentLang]}</h3>
                        <div class="flex items-center gap-2 text-[8px] text-gray-400 font-bold mt-2 pt-4 border-t border-gray-50 group-hover:text-[#FF4E45] transition-colors">
                            <i class="ph-fill ph-map-pin text-[#FF4E45] shrink-0"></i>
                            <span class="truncate uppercase tracking-wider">${record.location}</span>
                        </div>
                    </div>`;
        container.appendChild(item);
    });
}

function handleSearch() {
    const val = (document.getElementById('search-input') || document.getElementById('search-input-nav') || {}).value || '';
    const clearBtn = document.getElementById('clear-search');
    if (clearBtn) {
        if (val.length > 0) clearBtn.classList.remove('hidden');
        else clearBtn.classList.add('hidden');
    }
    renderGrid(val);
}

function clearSearch() {
    const input = document.getElementById('search-input') || document.getElementById('search-input-nav');
    if (input) {
        input.value = '';
        handleSearch();
        input.focus();
    }
}

function openModal(record) {
    activeRecord = record; currentSlideIndex = 0; currentViewMode = 'original';
    const confidenceMap = {
        'Verified': { th: 'ตรวจสอบแล้ว', en: 'Verified', bg: 'bg-emerald-600' },
        'Reconstructed': { th: 'สันนิษฐานรูปแบบ', en: 'Reconstructed', bg: 'bg-blue-600' },
        'Fragment': { th: 'ส่วนชิ้นส่วน', en: 'Fragment', bg: 'bg-amber-600' },
        'Hypothetical': { th: 'สมมติฐาน', en: 'Hypothetical', bg: 'bg-purple-600' }
    };
    let statusInfo = confidenceMap[record.confidence] || confidenceMap['Verified'];
    let statusText = currentLang === 'th' ? statusInfo.th : statusInfo.en;

    const badge = document.getElementById('modal-confidence-badge');
    if (badge) {
        badge.innerText = statusText;
        badge.className = `px-5 py-2 text-[9px] font-black uppercase tracking-[0.2em] rounded-full ${statusInfo.bg.replace('bg-', 'bg-')}/10 ${statusInfo.bg.replace('bg-', 'text-')} border ${statusInfo.bg.replace('bg-', 'border-')}/20 backdrop-blur-md`;
    }
    if (document.getElementById('modal-record-id')) document.getElementById('modal-record-id').innerText = `${record.id}`;
    if (document.getElementById('modal-category')) document.getElementById('modal-category').innerText = record.category;
    if (document.getElementById('modal-location')) document.getElementById('modal-location').innerText = record.location;
    if (document.getElementById('modal-title')) document.getElementById('modal-title').innerText = record.title[currentLang];
    if (document.getElementById('modal-morphemes')) {
        document.getElementById('modal-morphemes').innerHTML = record.morphemes[currentLang].map(m => `
            <li class="flex items-start gap-4 group/item">
                <div class="w-1.5 h-1.5 rounded-full bg-[#FF4E45]/60 mt-2 shrink-0 group-hover/item:scale-125 transition-transform"></div>
                <p class="text-[15px] text-[#0F172A] font-medium leading-relaxed">${m}</p>
            </li>`).join('');
    }
    if (document.getElementById('modal-connotation')) document.getElementById('modal-connotation').innerText = record.connotation[currentLang];
    if (document.getElementById('modal-preserve')) document.getElementById('modal-preserve').innerText = record.protocol.preserve;
    if (document.getElementById('modal-donot')) document.getElementById('modal-donot').innerText = record.protocol.donot;

    // Cultural Ethics Leveling
    const ethicsInfo = {
        'low': { th: 'ลวดลายทั่วไป', en: 'General Pattern', desc: { th: 'ใช้เชิงพาณิชย์ได้ + ระบุที่มา', en: 'Commercial Use Allowed + Attribution' }, color: 'bg-emerald-400' },
        'medium': { th: 'ลายพิธีกรรม', en: 'Ritual Pattern', desc: { th: 'ต้องขออนุญาตชุมชนก่อน', en: 'Community Permission Required' }, color: 'bg-amber-400' },
        'high': { th: 'ลายศักดิ์สิทธิ์', en: 'Sacred Pattern', desc: { th: 'ห้ามนำไปใช้เชิงพาณิชย์', en: 'No Commercial Use' }, color: 'bg-rose-400' }
    };
    const ec = ethicsInfo[record.ethics] || ethicsInfo['low'];
    const ethicsHTML = `
        <div class="p-6 rounded-2xl border border-[#0F2C59]/5 bg-gray-50/50 flex items-center gap-6 group hover:border-[#0F2C59]/10 transition-colors">
            <div class="w-3 h-3 rounded-full ${ec.color} shadow-[0_0_15px_rgba(0,0,0,0.1)] shrink-0 group-hover:scale-110 transition-transform border-2 border-white"></div>
            <div>
                <p class="text-[#0F172A] text-[15px] font-black uppercase tracking-tight mb-0.5">${currentLang === 'th' ? ec.th : ec.en}</p>
                <p class="text-gray-400 text-[11px] font-medium uppercase tracking-widest">${currentLang === 'th' ? ec.desc.th : ec.desc.en}</p>
            </div>
        </div>
    `;
    if (document.getElementById('modal-ethics-container')) document.getElementById('modal-ethics-container').innerHTML = ethicsHTML;

    if (document.getElementById('modal-tags')) document.getElementById('modal-tags').innerHTML = record.tags.map(t => `<span class="px-5 py-2.5 bg-[#f8fafc] text-gray-400 text-[10px] font-black uppercase rounded-xl border border-gray-100 hover:border-[#0F2C59]/20 hover:text-[#0F2C59] transition-all cursor-default">${t}</span>`).join('');

    updateModalDisplay();
    const modal = document.getElementById('modal');
    const container = document.getElementById('modal-container');
    if (modal) {
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.remove('opacity-0');
            modal.classList.add('opacity-100');
            if (container) {
                container.classList.remove('scale-95');
                container.classList.add('scale-100');
            }
        }, 10);
    }
    document.body.classList.add('modal-open');
}

function closeModal() {
    const modal = document.getElementById('modal');
    const container = document.getElementById('modal-container');
    if (modal) {
        modal.classList.remove('opacity-100');
        modal.classList.add('opacity-0');
        if (container) {
            container.classList.remove('scale-100');
            container.classList.add('scale-95');
        }
        setTimeout(() => { modal.classList.add('hidden'); activeRecord = null; document.body.classList.remove('modal-open'); }, 400);
    }
}

function changeSlide(dir) {
    if (!activeRecord) return;
    const originalSet = activeRecord.images.filter(img => img.type === 'original');
    const applicationSet = activeRecord.images.filter(img => img.type === 'application');
    const currentSet = currentViewMode === 'application' ? applicationSet : originalSet;

    if (currentSet.length === 0) return;
    currentSlideIndex = (currentSlideIndex + dir + currentSet.length) % currentSet.length;
    updateModalDisplay();
}

function toggleModalView(mode) {
    currentViewMode = mode; currentSlideIndex = 0;
    updateModalDisplay();

    const btnOrig = document.getElementById('btn-view-original');
    const btnVec = document.getElementById('btn-view-vector');
    const btnApp = document.getElementById('btn-view-application');

    [btnOrig, btnVec, btnApp].forEach(btn => {
        if (btn) btn.className = "flex-1 lg:flex-none px-4 lg:px-8 py-3.5 lg:py-3 text-[8px] lg:text-[9px] font-black uppercase tracking-[0.2em] rounded-xl text-white/30 hover:text-white transition-all duration-300 whitespace-nowrap";
    });

    if (mode === 'original' && btnOrig) {
        btnOrig.className = "flex-1 lg:flex-none px-4 lg:px-8 py-3.5 lg:py-3 text-[8px] lg:text-[9px] font-black uppercase tracking-[0.2em] rounded-xl bg-white text-[#0F2C59] shadow-xl transition-all duration-300 whitespace-nowrap";
    } else if (mode === 'vector' && btnVec) {
        btnVec.className = "flex-1 lg:flex-none px-4 lg:px-8 py-3.5 lg:py-3 text-[8px] lg:text-[9px] font-black uppercase tracking-[0.2em] rounded-xl bg-white text-[#0F2C59] shadow-xl transition-all duration-300 whitespace-nowrap";
    } else if (mode === 'application' && btnApp) {
        btnApp.className = "flex-1 lg:flex-none px-4 lg:px-8 py-3.5 lg:py-3 text-[8px] lg:text-[9px] font-black uppercase tracking-[0.2em] rounded-xl bg-white text-[#0F2C59] shadow-xl transition-all duration-300 whitespace-nowrap";
    }
}

function updateModalDisplay() {
    if (!activeRecord) return;
    const originalSet = activeRecord.images.filter(img => img.type === 'original');
    const vectorSet = activeRecord.images.filter(img => img.type === 'vector');
    const applicationSet = activeRecord.images.filter(img => img.type === 'application');

    const eviEl = document.getElementById('modal-image-original');
    const vecEl = document.getElementById('modal-image-vector');
    const prevBtn = document.getElementById('slider-prev');
    const nextBtn = document.getElementById('slider-next');

    let currentSet = currentViewMode === 'application' ? applicationSet : originalSet;

    if (currentSet.length > 1) {
        if (prevBtn) prevBtn.classList.remove('hidden');
        if (nextBtn) nextBtn.classList.remove('hidden');
    } else {
        if (prevBtn) prevBtn.classList.add('hidden');
        if (nextBtn) nextBtn.classList.add('hidden');
    }

    if (eviEl && vecEl) {
        if (currentSet.length > 0) {
            eviEl.src = currentSet[currentSlideIndex].url;
            document.getElementById('modal-counter').innerText = `${currentSlideIndex + 1} / ${currentSet.length}`;
        } else {
            eviEl.src = "https://placehold.co/800x600/0F2C59/D4AF37?text=Data+Pending";
            document.getElementById('modal-counter').innerText = "0 / 0";
        }

        if (currentViewMode === 'application') {
            vecEl.style.opacity = '0';
            eviEl.style.opacity = '1';
            eviEl.style.filter = 'grayscale(0%) blur(0px)';
        } else {
            vecEl.src = vectorSet.length > 0 ? vectorSet[currentSlideIndex % vectorSet.length].url : eviEl.src;
            if (currentViewMode === 'vector') {
                vecEl.style.opacity = '1';
                vecEl.style.filter = 'drop-shadow(0px 0px 20px rgba(255,78,69,0.5)) contrast(1.1)';
                eviEl.style.opacity = '0.15';
                eviEl.style.filter = 'grayscale(100%) blur(4px)';
            } else {
                vecEl.style.opacity = '0';
                eviEl.style.opacity = '1';
                eviEl.style.filter = 'grayscale(0%) blur(0px)';
            }
        }
    }

    // Toggle Download Button
    const downloadBtn = document.getElementById('modal-download-vector');
    if (downloadBtn) {
        if (currentViewMode === 'vector' && vectorSet.length > 0) {
            downloadBtn.classList.remove('hidden', 'opacity-0');
            downloadBtn.classList.add('flex', 'opacity-100');
        } else {
            downloadBtn.classList.add('hidden', 'opacity-0');
            downloadBtn.classList.remove('flex', 'opacity-100');
        }
    }
}

function downloadVector() {
    if (!activeRecord) return;
    const vector = activeRecord.images.find(img => img.type === 'vector');
    if (!vector) return;

    // Build metadata-rich filename
    const id = activeRecord.id;
    const titleTH = activeRecord.title.th.replace(/[^ก-ฮ0-9a-z]/gi, '_');
    const titleEN = activeRecord.title.en.replace(/[^a-z0-9]/gi, '_');
    const filename = `TSPL_${id}_${titleTH}_${titleEN}.svg`;

    const link = document.createElement('a');
    link.href = vector.url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


function setLanguage(lang) { }

const originalRenderGrid = renderGrid;
renderGrid = function (filterText = "") {
    originalRenderGrid(filterText);
    // Re-initialize gimmicks slightly after render
    setTimeout(() => {
        initScramble();
    }, 50);
};

// --- PARTICLE BACKGROUND ---
function initParticles() {
    // Particle canvas removed — was running a full-screen 60fps RAF loop
    // consuming ~8ms/frame. The CSS aurora blobs in premium.js
    // provide the same ambient feel at zero JS cost.
    const canvas = document.getElementById('particle-canvas');
    if (canvas) canvas.style.display = 'none';
}



// --- SCROLL PARALLAX (REMOVED - CONSOLIDATED IN PREMIUM.JS) ---


// --- SCROLL REVEAL ---
function revealInit() {
    const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const delay = parseInt(el.dataset.revealDelay) || 0;

                setTimeout(() => {
                    el.classList.add('active');
                }, delay);

                observer.unobserve(el);
            }
        });
    }, {
        threshold: 0.05, // Lower threshold for faster trigger
        rootMargin: '0px 0px -50px 0px' // Trigger slightly before it enters fully
    });

    reveals.forEach(r => {
        // Initial check for elements already in view
        const rect = r.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            r.classList.add('active');
        } else {
            observer.observe(r);
        }
    });
}

// --- 3D TILT EFFECT (REMOVED) ---
function initTilt() {
    // Feature removed for editorial luxury
}

function initScramble() {
    const chars = 'กขคฆงจฉชซญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*';
    document.querySelectorAll('.pattern-card').forEach(card => {
        const el = card.querySelector('.scramble-hover');
        if (!el || el.dataset.scrambleInit) return;
        el.dataset.scrambleInit = true;

        card.addEventListener('mouseenter', () => {
            const originalText = el.getAttribute('data-text');
            let iterations = 0;
            clearInterval(el.scrambleInterval); // clear any running
            el.scrambleInterval = setInterval(() => {
                el.innerText = originalText.split('').map((letter, index) => {
                    if (index < iterations) return originalText[index];
                    return chars[Math.floor(Math.random() * chars.length)];
                }).join('');
                iterations += 0.5;
                if (iterations >= originalText.length) {
                    clearInterval(el.scrambleInterval);
                    el.innerText = originalText; // guarantee original text restored
                }
            }, 30);
        });

        // Ensure text is always restored on leave
        card.addEventListener('mouseleave', () => {
            clearInterval(el.scrambleInterval);
            el.innerText = el.getAttribute('data-text');
        });
    });
}


window.onload = () => {
    init();

    // --- CINEMATIC PRELOADER ---
    const p = document.getElementById('preloader');
    const percEl = document.getElementById('loading-perc');
    let perc = 0;

    const conceptKeywords = [
        "ถอดรหัสอัตลักษณ์", "สกัดรอยมรดกไทย", "สู่สินทรัพย์ดิจิทัล",
        "หน่วยคำทัศน์", "สัญวิทยา", "สถาปัตยกรรม", "การวิเคราะห์เชิงโครงสร้าง",
        "ลายพุ่มข้าวบิณฑ์", "ล้านนา", "อยุธยา", "หลักฐานชั้นต้น",
        "M01", "M02", "M03", "TSPL CORE", "CREATIVE ECONOMY",
        "ประยุกต์ใช้", "ระบบพิกัด", "ARCHIVE", "VERIFIED", "VECTOR",
        "กนกเปลว", "ลายหงส์", "ลายนาค", "ลายครุฑ", "ธรรมจักร",
        "พรรณพฤกษา", "สรรพสัตว์", "เรขาคณิต", "ความเชื่อ",
        "Vector Readiness", "Connotation", "180 PATTERNS", "TAXONOMY"
    ];
    let scatterInterval;


    const hasPlayed = sessionStorage.getItem('tspl_preloader_played');
    const navEntries = performance.getEntriesByType("navigation");
    const isReload = navEntries.length > 0 && navEntries[0].type === "reload";

    if (p && percEl && (!hasPlayed || isReload)) {
        sessionStorage.setItem('tspl_preloader_played', 'true');
        // Apple-style Scattered Concept Typography
        scatterInterval = setInterval(() => {
            const el = document.createElement('div');
            el.innerText = conceptKeywords[Math.floor(Math.random() * conceptKeywords.length)];
            el.className = 'scattered-log';

            // Random Alignment & Positions (Concept)
            const aligns = ['left', 'center', 'right'];
            el.style.textAlign = aligns[Math.floor(Math.random() * aligns.length)];
            el.style.top = Math.random() * 90 + '%';
            el.style.left = Math.random() * 80 + 10 + '%';

            // Random formatting for data depth illusion
            el.style.fontSize = Math.floor(Math.random() * 14 + 10) + 'px';
            el.style.letterSpacing = Math.floor(Math.random() * 8) + 'px';
            el.style.filter = `blur(${Math.random() * 2}px)`;

            p.appendChild(el);

            requestAnimationFrame(() => {
                el.classList.add('in');
            });

            // Auto Remove
            setTimeout(() => {
                el.classList.remove('in');
                setTimeout(() => el.remove(), 800);
            }, Math.random() * 1500 + 500);
        }, 100);

        const percInterval = setInterval(() => {
            perc += Math.floor(Math.random() * 4) + 1;
            if (perc >= 100) {
                perc = 100;
                percEl.innerText = toThaiDigits(perc) + "%";
                clearInterval(percInterval);
                clearInterval(scatterInterval);

                // Final Flash Effect
                const finalLog = document.createElement('div');
                finalLog.className = 'scattered-log in';
                finalLog.innerText = "> ACCESS GRANTED. เข้าสู่ฐานข้อมูล...";
                finalLog.style.top = 'auto';
                finalLog.style.bottom = '40px';
                finalLog.style.left = '40px';
                finalLog.style.transform = 'none';
                finalLog.style.textAlign = 'left';
                finalLog.style.fontSize = '10px';
                finalLog.style.letterSpacing = '4px';
                finalLog.style.color = '#10B981';
                finalLog.style.opacity = '1';
                finalLog.style.filter = 'none';
                p.appendChild(finalLog);

                setTimeout(() => {
                    p.style.opacity = '0';
                    p.style.transform = 'scale(1.1)';
                    p.style.filter = 'blur(10px)';

                    setTimeout(() => {
                        revealInit();
                        animateCounters();
                    }, 400);

                    setTimeout(() => p.style.visibility = 'hidden', 1800);
                }, 800);
            } else {
                percEl.innerText = toThaiDigits(perc) + "%";
            }
        }, 35);
    } else {
        if (p) {
            p.style.display = 'none';
        }
        revealInit();
        animateCounters();
    }
};
const modalOverlay = document.getElementById('modal');
if (modalOverlay) modalOverlay.addEventListener('click', function (e) { if (e.target === this) closeModal(); });

// --- PAGE TRANSITIONS LOGIC ---
function initPageTransitions() {
    const transitionTargets = document.querySelectorAll('main, header');

    // Add entrance animation locally to targets, not the body, so preloader functions aren't hidden
    transitionTargets.forEach(t => {
        t.style.opacity = '0';
        t.style.transform = 'translateY(15px)';
        // trigger reflow
        void t.offsetWidth;
        t.style.transition = 'opacity 0.8s cubic-bezier(0.23, 1, 0.32, 1), transform 0.8s cubic-bezier(0.23, 1, 0.32, 1)';
        t.style.opacity = '1';
        t.style.transform = 'translateY(0)';
    });

    // Intercept appropriate anchor clicks for exit animation
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', e => {
            const href = link.getAttribute('href');

            // Allow default for target blank or anchor links
            if (!href || href.startsWith('#') || link.target === '_blank') return;

            // If it's a relative html link or root
            if (href.endsWith('.html') || !href.startsWith('http')) {
                e.preventDefault();
                transitionTargets.forEach(t => {
                    t.style.transition = 'opacity 0.4s cubic-bezier(0.23, 1, 0.32, 1), transform 0.4s cubic-bezier(0.23, 1, 0.32, 1)';
                    t.style.opacity = '0';
                    t.style.transform = 'translateY(-15px)';
                });

                setTimeout(() => {
                    window.location.href = href;
                }, 400); // Mapped to CSS timing
            }
        });
    });
}

// Fix for Safari back/forward cache
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        document.querySelectorAll('main, header').forEach(t => {
            t.style.opacity = '1';
            t.style.transform = 'translateY(0)';
        });
    }
});

// Start the application
document.addEventListener('DOMContentLoaded', () => {
    // Only init if we are on a page that needs data
    if (document.getElementById('grid-container')) {
        init();
    }
});

// Run page transitions right away (no waiting for images/onload)
initPageTransitions();