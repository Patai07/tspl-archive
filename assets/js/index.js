let currentLang = 'th';

const toThaiDigits = (num) => {
    const thaiNumbers = ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙'];
    return num.toString().split('').map(char => thaiNumbers[char] || char).join('');
};

// --- MASTER DATASET ---
const RECORDS = [
    {
        id: "TSP-PLK-CHM-026",
        title: { th: "ลายหงส์ปูนปั้น (วัดจุฬามณี)", en: "Stucco Hong Pattern" },
        category: "Architecture / Stucco",
        location: "วัดจุฬามณี จ.พิษณุโลก (สมัยอยุธยาตอนต้น)",
        confidence: "Verified",
        images: [
            { url: "https://images.unsplash.com/photo-1574169208507-84376144848b?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1590483736622-39854bcbc8b6?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&q=80&w=1200", type: "vector" },
            { url: "https://images.unsplash.com/photo-1584992236310-6edddc08acff?auto=format&fit=crop&q=80&w=1200", type: "application" }
        ],
        morphemes: {
            th: ["M01 ลำตัวหงส์คอเชิดสูง ทรงรีตั้งผสมเส้นโค้ง S", "M02 หางกนกสะบัดพลิ้ว ทรงพุ่มข้าวบิณฑ์", "M03 ปีกหงส์ซ้อนขนาน นูนต่ำสไตล์อยุธยา"],
            en: ["M01 High neck body, S-curve posture", "M02 Flicked Kanok tail motif", "M03 Parallel wings in bas-relief"]
        },
        connotation: {
            th: "สัญลักษณ์ความเป็นทิพย์และความบริสุทธิ์ ทำหน้าที่แบกรับเขาพระสุเมรุตามคติไตรภูมิ",
            en: "Symbolizes divinity and purity, supporting the sacred Mount Meru."
        },
        ethics: "low",
        protocol: { preserve: "เอกลักษณ์คอเชิดและหางกนกสัดส่วนเดิม", donot: "ห้ามใช้ประดับในตำแหน่งเท้า หรือสิ่งทอช่วงล่าง" },
        tags: ["#หงส์", "#วัดจุฬามณี", "#อยุธยา"]
    },
    {
        id: "TSP-UNK-OBS-001",
        title: { th: "ลายเครือเถาก้านขดดอกกลาง", en: "Floral Scroll with Rosette" },
        category: "Architecture / Stone",
        location: "ชิ้นส่วนประดับโบราณสถาน (Unknown Location)",
        confidence: "Reconstructed",
        images: [
            { url: "https://images.unsplash.com/photo-1604871000636-074fa5117945?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?auto=format&fit=crop&q=80&w=1200", type: "vector" }
        ],
        morphemes: {
            th: ["M01 กรอบแผงสี่เหลี่ยมขอบคู่ขนาน", "M02 ดอกกลางโรเซตซ้อนชั้นศูนย์กลาง", "M03 ก้านเถาโค้งเชื่อมโยงจังหวะ"],
            en: ["M01 Double-lined horizontal frame", "M02 Layered central rosette motif", "M03 Rhythmic S-curve vine path"]
        },
        connotation: { th: "สัญลักษณ์ความงอกงามและความต่อเนื่อง", en: "Symbolizes prosperity and growth continuity." },
        ethics: "low",
        protocol: { preserve: "แกนสมมาตรและดอกกลางโรเซต", donot: "ตัดทอนองค์ประกอบศูนย์กลางจนเสียสมดุล" },
        tags: ["#เครือเถา", "#สมมาตร"]
    },
    {
        id: "TSP-AYT-NGA-001",
        title: { th: "ลายพญานาคทรงเครื่อง", en: "Regal Naga Motif" },
        category: "Architecture / Stucco",
        location: "วัดไชยวัฒนาราม จ.พระนครศรีอยุธยา",
        confidence: "Fragment",
        images: [
            { url: "https://images.unsplash.com/photo-1628032549721-68db0c749b38?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1580130718646-9f694209b207?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=1200", type: "vector" }
        ],
        morphemes: {
            th: ["M01 เศียรนาคสวมมงกุฎ ทรงสูงสง่า มีครีบหูแผ่", "M02 ลำตัวโค้งงอเป็น S-curve", "M03 หางเป็นปลา มีเกล็ดนูนต่ำเรียงเป็นจังหวะ"],
            en: ["M01 Crowned naga head with flared hood", "M02 Sinuous S-curve body", "M03 Fishtail end with rhythmic low-relief scales"]
        },
        connotation: { th: "ผู้พิทักษ์พระพุทธศาสนาและสิ่งศักดิ์สิทธิ์ สื่อถึงพลังแห่งน้ำ", en: "Guardian of Buddhism and sacred sites, embodying water power." },
        ethics: "medium",
        protocol: { preserve: "ความสง่างามของเศียรและครีบหู", donot: "ห้ามทำให้เศียรนาคดูดุร้ายเกินไป" },
        tags: ["#พญานาค", "#ราวบันได", "#ผู้พิทักษ์"]
    },
    {
        id: "TSP-LNA-WOD-012",
        title: { th: "ลายหน้าบันไม้จำหลัก", en: "Wooden Gable Pattern" },
        category: "Architecture / Wood",
        location: "วัดพระธาตุลำปางหลวง จ.ลำปาง",
        confidence: "Hypothetical",
        images: [
            { url: "https://images.unsplash.com/photo-1583313264627-7ba7f2cb243a?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?auto=format&fit=crop&q=80&w=1200", type: "vector" }
        ],
        morphemes: {
            th: ["M01 ลายพรรณพฤกษาพันเกี่ยว", "M02 การเซาะร่องลึกแบบช่างไม้ล้านนา", "M03 โครงสร้างกรอบสามเหลี่ยมหน้าจั่ว"],
            en: ["M01 Intertwining botanical motifs", "M02 Deep gouge carving techniques", "M03 Triangular structural framing"]
        },
        connotation: { th: "การจำลองป่าหิมพานต์อันเป็นดินแดนศักดิ์สิทธิ์", en: "Representation of the mythical Himmapan forest." },
        ethics: "high",
        protocol: { preserve: "ร่องรอยการแกะสลักที่ดูเป็นธรรมชาติ", donot: "ปรับเส้นสายให้แข็งทื่อแบบเรขาคณิต" },
        tags: ["#หน้าบัน", "#ไม้แกะสลัก", "#ล้านนา"]
    },
    {
        id: "TSP-SUK-LOT-008",
        title: { th: "ลายดอกบัวตูมสุโขทัย", en: "Sukhothai Lotus Bud" },
        category: "Architecture / Stucco",
        location: "อุทยานประวัติศาสตร์สุโขทัย",
        confidence: "High",
        images: [
            { url: "https://images.unsplash.com/photo-1516961642265-531546e84af2?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1552250575-e508473b090f?auto=format&fit=crop&q=80&w=1200", type: "vector" }
        ],
        morphemes: {
            th: ["M01 รูปทรงดอกบัวตูมแหลม", "M02 กลีบบัวซ้อนชั้น 3 ระดับ", "M03 ฐานรองดอกทรงกลมเรียบ"],
            en: ["M01 Pointed lotus bud silhouette", "M02 Three-tiered overlapping petals", "M03 Smooth circular base support"]
        },
        connotation: { th: "ความบริสุทธิ์และการตรัสรู้ตามคติพุทธศาสนาเถรวาท", en: "Purity and enlightenment in Theravada Buddhism." },
        ethics: "low",
        protocol: { preserve: "สัดส่วนความโค้งของกลีบบัว", donot: "ห้ามปรับสัดส่วนจนคล้ายหยดน้ำ" },
        tags: ["#บัวตูม", "#สุโขทัย", "#พุทธศิลป์"]
    },
    {
        id: "TSP-KHM-LIN-044",
        title: { th: "ลายทับหลังนารายณ์", en: "Narayana Lintel Carving" },
        category: "Architecture / Stone",
        location: "ปราสาทหินพนมรุ้ง จ.บุรีรัมย์",
        confidence: "High",
        images: [
            { url: "https://images.unsplash.com/photo-1531685250784-7569952593d2?auto=format&fit=crop&q=80&w=1200", type: "original" },
            { url: "https://images.unsplash.com/photo-1571781526291-c477eb31405e?auto=format&fit=crop&q=80&w=1200", type: "vector" }
        ],
        morphemes: {
            th: ["M01 องค์ประธานตรงกลาง (นารายณ์)", "M02 ลายหน้ากาลคายพวงอุบะ", "M03 ลายก้านขดแบ่งระนาบซ้ายขวา"],
            en: ["M01 Central presiding deity", "M02 Kala face spewing garlands", "M03 Symmetrical scrolling vines"]
        },
        connotation: { th: "การปกปักรักษาศาสนสถานและพลังอำนาจแห่งเทพเจ้า", en: "Protection of the sanctuary and divine authority." },
        ethics: "medium",
        protocol: { preserve: "ความสมมาตรและรายละเอียดของหน้ากาล", donot: "ดัดแปลงองค์ประกอบจนผิดหลักเทววิทยา" },
        tags: ["#ทับหลัง", "#พนมรุ้ง", "#ขอม"]
    },
    {
        id: "TSP-RAT-KBT-001",
        title: { th: "ลายกนกใบเทศ (กาบใบโพธิ์)", en: "Kranok Bai Tet Motif" },
        category: "Architecture / Stucco",
        location: "วัดพระศรีรัตนศาสดาราม กรุงเทพฯ",
        confidence: "Medium",
        images: [
            { url: "https://images.unsplash.com/photo-1563492065599-3520f775eeed?auto=format&fit=crop&q=80&w=1200", type: "original" }
        ],
        morphemes: {
            th: ["M01 ใบโพธิ์แหลมยาว", "M02 ก้านกลางหนานูนต่ำ", "M03 ขอบใบประดับกนกเล็กๆ"],
            en: ["M01 Elongated pointed Bodhi leaf", "M02 Thick central vein", "M03 Leaf edges with miniature kanoks"]
        },
        connotation: { th: "สัญลักษณ์แห่งการตรัสรู้และปัญญา", en: "Symbol of enlightenment and wisdom." },
        ethics: "low",
        protocol: { preserve: "รูปทรงใบแหลมยาว", donot: "ห้ามทำให้ใบกลมหรือสั้นเกินไป" },
        tags: ["#กนกใบเทศ", "#ใบโพธิ์", "#รัตนโกสินทร์"]
    },
    {
        id: "TSP-LAN-MUR-009",
        title: { th: "ลายปูนปั้นประดับซุ้มประตู", en: "Stucco Arch Motif" },
        category: "Architecture / Stucco",
        location: "วัดภูมินทร์ จ.น่าน",
        confidence: "High",
        images: [
            { url: "https://images.unsplash.com/photo-1580130718646-9f694209b207?auto=format&fit=crop&q=80&w=1200", type: "original" }
        ],
        morphemes: {
            th: ["M01 ลายเครือล้านนาแบบอิสระ", "M02 การเว้นช่องไฟที่โปร่งตา", "M03 เทคนิคปั้นสดไม่ใช้แม่พิมพ์"],
            en: ["M01 Free-form Lanna flora", "M02 Breathable negative space", "M03 Free-hand stucco techniques"]
        },
        connotation: { th: "ความเรียบง่ายและศรัทธาของช่างพื้นบ้านล้านนา", en: "Simplicity and devotion of local Lanna artisans." },
        ethics: "low",
        protocol: { preserve: "ความอ่อนช้อยที่ไม่สมมาตรเป๊ะ", donot: "ทำซ้ำ (Duplicate) ให้เหมือนกันทุกกระเบียดนิ้ว" },
        tags: ["#ซุ้มประตู", "#ปูนปั้น", "#น่าน"]
    }
];

const CATEGORIES = ["All", "Architecture / Stucco", "Architecture / Stone", "Architecture / Wood"];
const CATEGORY_LABEL = {
    "All": { th: "ทั้งหมด", en: "All" },
    "Architecture / Stucco": { th: "สถาปัตย์ / ปูนปั้น", en: "Architecture / Stucco" },
    "Architecture / Stone": { th: "สถาปัตย์ / หิน", en: "Architecture / Stone" },
    "Architecture / Wood": { th: "สถาปัตย์ / ไม้", en: "Architecture / Wood" },
};
let activeCategory = "All", activeRecord = null, currentSlideIndex = 0, currentViewMode = "original";

function init() {
    initParticles();
    initParallax();

    renderCategories();
    renderGrid();
    updateLegend();
    setupHeroGlow();
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

function renderGrid(filterText = "") {
    const container = document.getElementById('grid-container');
    if (!container) return;
    container.innerHTML = '';

    let filtered = RECORDS.filter(r => {
        const matchesCat = activeCategory === "All" || r.category === activeCategory;
        const titleText = (currentLang === 'th' ? r.title.th : r.title.en) || "";
        return matchesCat && (titleText.toLowerCase().includes(filterText.toLowerCase()) || r.id.toLowerCase().includes(filterText.toLowerCase()));
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

        // Category-based placeholder palette
        const palettes = {
            'Architecture / Stucco': { bg: 'from-[#0F2C59] to-[#1a3f7a]', icon: 'ph-building-apartment', accent: '#D4AF37' },
            'Architecture / Stone': { bg: 'from-[#2d1f3d] to-[#4a2f6a]', icon: 'ph-pyramid', accent: '#B8A0D4' },
            'Architecture / Wood': { bg: 'from-[#2d1a0e] to-[#5c3416]', icon: 'ph-tree-evergreen', accent: '#D4A574' },
        };
        const palette = palettes[record.category] || { bg: 'from-[#1a1a2e] to-[#16213e]', icon: 'ph-shapes', accent: '#D4AF37' };

        item.innerHTML = `
                    <div class="relative aspect-[4/3] overflow-hidden bg-gradient-to-br ${palette.bg} flex items-center justify-center">
                        <div class="absolute inset-0 bg-grid-pattern opacity-[0.05] pointer-events-none"></div>
                        <!-- Decorative Pattern Placeholder -->
                        <div class="flex flex-col items-center gap-3 opacity-20 group-hover:opacity-30 transition-opacity duration-500">
                            <i class="ph-thin ${palette.icon} text-7xl" style="color:${palette.accent}"></i>
                            <div class="w-12 h-px" style="background:${palette.accent}"></div>
                            <span class="text-[8px] font-bold tracking-[0.4em] uppercase" style="color:${palette.accent}">${currentLang === "th" ? "ตัวอย่างลวดลาย" : "Pattern Specimen"}</span>
                        </div>
                        <!-- Status Badge -->
                        <div class="absolute top-5 left-5 z-20">
                            <span class="px-3 py-1 text-[7px] font-bold uppercase tracking-[0.2em] rounded bg-black/30 backdrop-blur-sm border border-white/10">
                                <span class="${statusColor}">${statusText}</span>
                            </span>
                        </div>
                        <!-- Hover CTA -->
                        <div class="absolute bottom-5 right-5 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
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
                        <div class="flex items-center gap-2 text-[9px] text-gray-400 font-normal mt-4 pt-4 border-t border-gray-100 group-hover:text-[#0F2C59] transition-colors">
                            <i class="ph-fill ph-map-pin text-[#FFD200] shrink-0"></i><span class="truncate">${record.location}</span>
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
                <div class="w-2.5 h-2.5 rounded-full bg-[#FFD200] mt-1.5 shrink-0 shadow-[0_0_10px_rgba(255,210,0,0.4)] group-hover/item:scale-125 transition-transform"></div>
                <p class="text-[15px] text-[#0F2C59] font-medium leading-relaxed">${m}</p>
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
        <div class="p-8 rounded-[2rem] border border-gray-100 bg-gray-50 flex items-center gap-6 group hover:border-[#0F2C59]/10 transition-colors">
            <div class="w-4 h-4 rounded-full ${ec.color} shadow-[0_0_15px_rgba(0,0,0,0.1)] shrink-0 group-hover:scale-110 transition-transform"></div>
            <div>
                <p class="text-[#0F2C59] text-[15px] font-black uppercase tracking-tight mb-1">${currentLang === 'th' ? ec.th : ec.en}</p>
                <p class="text-gray-400 text-[12px] font-medium">${currentLang === 'th' ? ec.desc.th : ec.desc.en}</p>
            </div>
        </div>
    `;
    if (document.getElementById('modal-ethics-container')) document.getElementById('modal-ethics-container').innerHTML = ethicsHTML;

    if (document.getElementById('modal-tags')) document.getElementById('modal-tags').innerHTML = record.tags.map(t => `<span class="px-5 py-2.5 bg-[#f8fafc] text-gray-400 text-[10px] font-black uppercase rounded-xl border border-gray-100 hover:border-[#0F2C59]/20 hover:text-[#0F2C59] transition-all cursor-default">${t}</span>`).join('');

    updateModalDisplay();
    const modal = document.getElementById('modal');
    if (modal) {
        modal.classList.remove('hidden');
        setTimeout(() => { modal.classList.remove('opacity-0'); modal.classList.add('opacity-100'); }, 10);
    }
    document.body.classList.add('modal-open');
}

function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.classList.remove('opacity-100');
        modal.classList.add('opacity-0');
        setTimeout(() => { modal.classList.add('hidden'); activeRecord = null; document.body.classList.remove('modal-open'); }, 300);
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
        if (btn) btn.className = "px-6 lg:px-8 py-3 text-[9px] font-black uppercase tracking-[0.2em] rounded-xl text-white/40 hover:text-white transition-all duration-300 whitespace-nowrap";
    });

    if (mode === 'original' && btnOrig) {
        btnOrig.className = "px-6 lg:px-8 py-3 text-[9px] font-black uppercase tracking-[0.2em] rounded-xl bg-white text-[#0F2C59] shadow-2xl transition-all duration-300 whitespace-nowrap";
    } else if (mode === 'vector' && btnVec) {
        btnVec.className = "px-6 lg:px-8 py-3 text-[9px] font-black uppercase tracking-[0.2em] rounded-xl bg-white text-[#0F2C59] shadow-2xl transition-all duration-300 whitespace-nowrap";
    } else if (mode === 'application' && btnApp) {
        btnApp.className = "px-6 lg:px-8 py-3 text-[9px] font-black uppercase tracking-[0.2em] rounded-xl bg-white text-[#0F2C59] shadow-2xl transition-all duration-300 whitespace-nowrap";
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
                vecEl.style.filter = 'drop-shadow(0px 0px 20px rgba(212,175,55,0.8)) contrast(1.5)';
                eviEl.style.opacity = '0.15';
                eviEl.style.filter = 'grayscale(100%) blur(4px)';
            } else {
                vecEl.style.opacity = '0';
                eviEl.style.opacity = '1';
                eviEl.style.filter = 'grayscale(0%) blur(0px)';
            }
        }
    }
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



// --- SCROLL PARALLAX (APPLE STYLE) ---
function initParallax() {
    const hElements = document.querySelectorAll('.parallax-horizontal');
    const vElements = document.querySelectorAll('.parallax-vertical');

    if (!hElements.length && !vElements.length) return;

    let targetScrollY = window.pageYOffset || document.documentElement.scrollTop;
    let currentScrollY = targetScrollY;
    let isUpdating = false;

    window.addEventListener('scroll', () => {
        targetScrollY = window.pageYOffset || document.documentElement.scrollTop;
        if (!isUpdating) {
            isUpdating = true;
            requestAnimationFrame(update);
        }
    }, { passive: true });

    const update = () => {
        // LERP for smooth dampening (0.1 means 10% towards target every frame)
        currentScrollY += (targetScrollY - currentScrollY) * 0.1;

        // If target reached (within 0.5px), stop looping to save CPU
        if (Math.abs(targetScrollY - currentScrollY) < 0.5) {
            currentScrollY = targetScrollY;
            isUpdating = false;
        } else {
            requestAnimationFrame(update);
        }

        // Optimization: pause heavy calculations if outside viewport
        if (currentScrollY > window.innerHeight * 1.5) return;

        hElements.forEach(el => {
            const speed = parseFloat(el.getAttribute('data-parallax-speed') || 0);
            const x = currentScrollY * speed;
            const op = Math.max(0, 1 - (currentScrollY / 600));

            el.style.transform = `translate3d(${x.toFixed(2)}px, 0, 0)`;
            el.style.opacity = op < 0.99 ? op.toFixed(3) : '1';
        });

        vElements.forEach(el => {
            const speed = parseFloat(el.getAttribute('data-parallax-speed') || 0);
            const y = currentScrollY * speed;
            const sc = Math.max(0.95, 1 - (currentScrollY / 5000));
            const op = Math.max(0, 1 - (currentScrollY / 800));

            el.style.transform = `translate3d(0, ${y.toFixed(2)}px, 0) scale(${sc.toFixed(4)})`;
            el.style.opacity = op < 0.99 ? op.toFixed(3) : '1';
        });
    };

    if (targetScrollY > 0) {
        isUpdating = true;
        requestAnimationFrame(update);
    }
}


// --- SCROLL REVEAL ---
function revealInit() {
    const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('active');
                }, (entry.target.dataset.revealDelay || i) * 150);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    reveals.forEach(r => observer.observe(r));

    // Pipeline scroll-merge observer removed in favor of sticky card stack
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
        "ลายพุ่มข้าวบิณฑ์", "ลานนา", "อยุธยา", "หลักฐานชั้นต้น",
        "M01", "M02", "M03", "TSPL CORE", "CREATIVE ECONOMY",
        "ประยุกต์ใช้", "ระบบพิกัด", "ARCHIVE", "VERIFIED", "VECTOR"
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

// Run page transitions right away (no waiting for images/onload)
initPageTransitions();