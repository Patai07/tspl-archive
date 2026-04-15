import re

html_to_insert = """    <!-- TSPL Factsheet Modal -->
    <div id="modal"
        class="hidden fixed inset-0 z-[200] flex items-center justify-center bg-[#0F172A]/80 backdrop-blur-3xl opacity-0 transition-opacity duration-300 p-0 lg:p-8">

        <!-- Refined Close Button -->
        <button onclick="closeModal()"
            class="absolute top-5 right-5 lg:top-8 lg:right-8 z-[300] w-12 h-12 bg-white/90 backdrop-blur-xl text-[#0F172A] rounded-full flex items-center justify-center hover:bg-white transition-all hover:scale-110 shadow-2xl group border border-gray-200">
            <i class="ph-bold ph-x text-xl group-hover:rotate-90 transition-transform duration-300"></i>
        </button>

        <div class="flex flex-col lg:flex-row w-full max-w-[1600px] h-full lg:h-[94vh] bg-white lg:rounded-[3rem] lg:overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.3)] relative transform transition-transform duration-500 scale-95 origin-center"
            id="modal-container">

            <!-- Left Pane: Visual Archive (Printed Catalog Style) -->
            <div class="w-full lg:w-[60%] h-[45%] lg:h-full bg-[#F8FAFC] relative overflow-hidden flex items-center justify-center border-r border-gray-100">
                <!-- Background Decoration -->
                <div class="absolute inset-0 bg-grid-pattern opacity-[0.03] pointer-events-none mix-blend-multiply"></div>
                <div class="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-white/80 to-transparent pointer-events-none"></div>

                <!-- Top Metadata Bar -->
                <div class="absolute top-6 inset-x-6 lg:top-10 lg:inset-x-12 flex justify-between items-center z-[100]">
                    <div class="flex items-center gap-6">
                        <div id="modal-record-id" class="text-[10px] lg:text-[12px] font-mono text-[#0F172A]/40 tracking-[0.3em] font-black uppercase">RECORD_ID</div>
                        <button id="modal-download-vector" onclick="downloadVector()" class="hidden items-center gap-2 px-4 py-1.5 bg-[#FF4E45] text-white rounded-lg text-[9px] font-black uppercase tracking-[0.2em] shadow-lg shadow-[#FF4E45]/30 hover:scale-105 transition-all">
                            <i class="ph-bold ph-download-simple"></i>
                            <span class="lang-th">ดาวน์โหลดลายเส้น</span>
                        </button>
                    </div>
                    <span id="modal-confidence-badge" class="px-4 py-1.5 lg:px-5 lg:py-2 text-[8px] lg:text-[9px] font-black uppercase tracking-[0.2em] rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 backdrop-blur-md">Validated</span>
                </div>

                <!-- Slider Navigation -->
                <div class="absolute inset-y-0 left-0 lg:left-6 flex items-center z-[100] pointer-events-none">
                    <button id="slider-prev" onclick="changeSlide(-1)" class="p-4 rounded-full bg-white/50 hover:bg-white text-[#0F172A]/40 hover:text-[#0F172A] transition-all pointer-events-auto border border-gray-200 shadow-sm opacity-0 lg:opacity-100 group">
                        <i class="ph-bold ph-caret-left text-2xl group-hover:-translate-x-1 transition-transform"></i>
                    </button>
                </div>
                <div class="absolute inset-y-0 right-0 lg:right-6 flex items-center z-[100] pointer-events-none">
                    <button id="slider-next" onclick="changeSlide(1)" class="p-4 rounded-full bg-white/50 hover:bg-white text-[#0F172A]/40 hover:text-[#0F172A] transition-all pointer-events-auto border border-gray-200 shadow-sm opacity-0 lg:opacity-100 group">
                        <i class="ph-bold ph-caret-right text-2xl group-hover:translate-x-1 transition-transform"></i>
                    </button>
                </div>

                <!-- View Switcher -->
                <div class="absolute bottom-6 lg:bottom-10 left-1/2 -translate-x-1/2 z-[100] flex bg-white/80 backdrop-blur-2xl p-1.5 rounded-2xl border border-gray-200 shadow-lg w-[calc(100%-3rem)] lg:w-max max-w-lg">
                    <button id="btn-view-original" onclick="toggleModalView('original')" class="flex-1 lg:flex-none px-4 lg:px-10 py-3.5 lg:py-3 text-[9px] lg:text-[10px] font-black uppercase tracking-[0.2em] rounded-xl bg-[#0F172A] text-white transition-all duration-300 whitespace-nowrap shadow-md"><span class="lang-th">ภาพต้นฉบับ</span></button>
                    <button id="btn-view-vector" onclick="toggleModalView('vector')" class="flex-1 lg:flex-none px-4 lg:px-10 py-3.5 lg:py-3 text-[9px] lg:text-[10px] font-black uppercase tracking-[0.2em] rounded-xl text-[#0F172A]/50 hover:text-[#0F172A] hover:bg-gray-100 transition-all duration-300 whitespace-nowrap"><span class="lang-th">ลายสกัด</span></button>
                    <button id="btn-view-application" onclick="toggleModalView('application')" class="flex-1 lg:flex-none px-4 lg:px-10 py-3.5 lg:py-3 text-[9px] lg:text-[10px] font-black uppercase tracking-[0.2em] rounded-xl text-[#0F172A]/50 hover:text-[#0F172A] hover:bg-gray-100 transition-all duration-300 whitespace-nowrap"><span class="lang-th">ประยุกต์ใข้</span></button>
                </div>

                <div id="modal-counter" class="absolute bottom-10 right-10 z-[100] text-[11px] font-mono font-bold text-[#0F172A]/30 tracking-widest hidden lg:block">1 / 1</div>

                <div class="relative w-full h-full flex justify-center items-center p-12 lg:p-32">
                    <img id="modal-image-original" src="" alt="Registry Visual" class="absolute max-w-[90%] max-h-[85%] lg:max-w-[85%] lg:max-h-[80%] object-contain mix-blend-multiply transition-all duration-700 ease-[cubic-bezier(0.23,1,0.32,1)] translate-z-0 filter contrast-125 saturate-150">
                    <img id="modal-image-vector" src="" alt="Vector Overlay" class="absolute max-w-[90%] max-h-[85%] lg:max-w-[85%] lg:max-h-[80%] object-contain transition-all duration-700 opacity-0 pointer-events-none mix-blend-multiply ease-[cubic-bezier(0.23,1,0.32,1)] translate-z-0" style="filter: drop-shadow(0 0 30px rgba(255,78,69,0.2)) contrast(1.8);">
                </div>
            </div>

            <!-- Right Pane: Factsheet -->
            <div class="w-full lg:w-[40%] flex flex-col h-[55%] lg:h-full bg-white overflow-y-auto custom-scrollbar">
                <div class="p-8 lg:p-14 xl:p-16 pt-10 pb-24 lg:pb-16">
                    <div id="modal-category" class="text-[10px] lg:text-[11px] font-black text-[#FF4E45] uppercase tracking-[0.3em] mb-3">Category</div>
                    <h2 id="modal-title" class="text-3xl md:text-5xl font-black text-[#0F172A] mb-8 tracking-tighter leading-[1.1] uppercase">ชื่อระเบียน</h2>

                    <div class="flex items-center gap-5 mb-10 py-5 bg-gray-50/80 px-6 rounded-2xl border border-gray-100 group">
                        <div class="w-12 h-12 rounded-xl bg-white flex items-center justify-center border border-gray-200 shadow-sm group-hover:scale-105 transition-transform"><i class="ph-fill ph-map-pin text-[#FF4E45] text-2xl"></i></div>
                        <div>
                            <p class="text-[9px] font-bold text-gray-400 uppercase tracking-[0.2em] leading-none mb-1.5">Provenance Location</p>
                            <span id="modal-location" class="text-sm text-[#0F172A] font-bold tracking-wide uppercase">Location Name</span>
                        </div>
                    </div>

                    <div class="space-y-12 lg:space-y-14">
                        <!-- 01. Visual Morphemes -->
                        <div>
                            <h4 class="text-[9px] font-black uppercase tracking-[0.3em] text-gray-400 mb-5 flex items-center gap-3"><span class="w-8 h-px bg-gray-200"></span>01. Visual Morphemes</h4>
                            <ul id="modal-morphemes" class="grid grid-cols-2 gap-4"></ul>
                        </div>

                        <!-- 02. Semiotic Context -->
                        <div>
                            <h4 class="text-[9px] font-black uppercase tracking-[0.3em] text-gray-400 mb-5 flex items-center gap-3"><span class="w-8 h-px bg-gray-200"></span>02. Semiotic Context</h4>
                            <p id="modal-connotation" class="text-[14px] lg:text-[15px] text-[#0F172A]/70 leading-relaxed font-medium bg-white border-l-2 border-[#FF4E45] pl-6 py-2"></p>
                        </div>

                        <!-- 03. Protocols -->
                        <div>
                            <h4 class="text-[9px] font-black uppercase tracking-[0.3em] text-gray-400 mb-6 flex items-center gap-3"><span class="w-8 h-px bg-gray-200"></span>03. Protocols</h4>
                            <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
                                <div class="bg-emerald-50/50 border border-emerald-100 p-5 rounded-2xl">
                                    <div class="flex items-center gap-2 mb-3"><i class="ph-fill ph-check-circle text-emerald-500 text-lg"></i><strong class="text-[#0F172A] text-[10px] font-black uppercase tracking-widest text-emerald-700">Must Preserve</strong></div>
                                    <p id="modal-preserve" class="text-xs text-[#0F172A]/70 font-medium leading-relaxed"></p>
                                </div>
                                <div class="bg-rose-50/50 border border-rose-100 p-5 rounded-2xl">
                                    <div class="flex items-center gap-2 mb-3"><i class="ph-fill ph-warning-circle text-rose-500 text-lg"></i><strong class="text-[#0F172A] text-[10px] font-black uppercase tracking-widest text-rose-700">Do Not</strong></div>
                                    <p id="modal-donot" class="text-xs text-[#0F172A]/70 font-medium leading-relaxed"></p>
                                </div>
                            </div>
                        </div>

                        <!-- 04. Cultural Ethics -->
                        <div>
                            <h4 class="text-[9px] font-black uppercase tracking-[0.3em] text-gray-400 mb-5 flex items-center gap-3"><span class="w-8 h-px bg-gray-200"></span>04. Cultural Ethics</h4>
                            <div id="modal-ethics-container"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>"""

for file_name in ['index.html', 'archive.html']:
    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(r'<!-- TSPL Factsheet Modal -->\s*<div id="modal".*?</div>\s*</div>\s*</div>\s*</div>', re.DOTALL)
    
    if pattern.search(content):
        new_content = pattern.sub(html_to_insert, content)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully updated {file_name}")
    else:
        print(f"Could not find modal section in {file_name}")

