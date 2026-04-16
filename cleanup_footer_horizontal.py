import glob
import re

# Precise replacement for the partner section to avoid leftovers
# We'll target the whole "Mission" column content to be safe and clean it up.

mission_column_content = """<div class="space-y-4">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 bg-[#FF4E45]/20 rounded-lg flex items-center justify-center border border-[#FF4E45]/40 shadow-[0_0_15px_rgba(255,78,69,0.2)]">
                            <i class="ph-fill ph-book-open text-[#FF4E45] text-xl"></i>
                        </div>
                        <h3 class="text-white font-bold tracking-wide text-sm">พันธกิจระดับมรดก</h3>
                    </div>
                    <p class="text-[13px] leading-relaxed text-gray-400 font-light font-th">
                        คลังข้อมูลการวิจัยเชิงสร้างสรรค์เพื่อการบริหารจัดการมรดกทางวัฒนธรรม เพื่อสืบสานอัตลักษณ์ไทยสู่เศรษฐกิจสร้างสรรค์
                    </p>
                    <div class="flex flex-wrap gap-3">
                        <div class="w-fit flex items-center gap-x-3 bg-white/5 p-2.5 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                            <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-7 w-auto">
                            <div class="flex flex-col">
                                <span class="text-[7px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                <span class="text-[9px] text-gray-300 font-medium leading-tight">สศร.</span>
                            </div>
                        </div>
                        <div class="w-fit flex items-center gap-x-3 bg-white/5 p-2.5 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                            <img src="assets/กศร.svg" alt="กศร." class="h-7 w-auto">
                            <div class="flex flex-col">
                                <span class="text-[7px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                <span class="text-[9px] text-gray-300 font-medium leading-tight">กศร.</span>
                            </div>
                        </div>
                    </div>
                </div>"""

contact_column_content = """<div class="space-y-4">
                    <h4 class="text-white text-[10px] font-bold tracking-wide border-l-2 border-[#FF4E45] pl-6 leading-none py-1">ช่องทางการติดต่อ</h4>
                    <div class="flex flex-row flex-wrap gap-8 items-center bg-white/5 p-4 rounded-3xl border border-white/5">
                        <div class="flex items-center gap-4 group cursor-pointer">
                            <div class="w-9 h-9 rounded-full bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-[#FF4E45]/10 group-hover:border-[#FF4E45]/30 transition-all">
                                <i class="ph-fill ph-envelope-simple text-gray-500 group-hover:text-[#FF4E45] text-lg"></i>
                            </div>
                            <div class="flex flex-col">
                                <span class="text-[12px] text-gray-300 group-hover:text-white transition-colors">samaporn@example.com</span>
                            </div>
                        </div>
                        <div class="flex items-center gap-4 group cursor-pointer">
                            <div class="w-9 h-9 rounded-full bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-[#FF4E45]/10 group-hover:border-[#FF4E45]/30 transition-all">
                                <i class="ph-fill ph-globe text-gray-500 group-hover:text-[#FF4E45] text-lg"></i>
                            </div>
                            <div class="flex flex-col">
                                <span class="text-[12px] text-gray-300 group-hover:text-white transition-colors">www.samaporn.com</span>
                            </div>
                        </div>
                    </div>
                </div>"""

institution_column_content = """<div class="space-y-4">
                    <h4 class="text-white text-[10px] font-bold tracking-wide border-l-2 border-[#FF4E45] pl-6 leading-none py-1">หน่วยงานร่วมวิจัย</h4>
                    <div class="flex flex-row flex-wrap gap-6 items-center bg-white/5 p-4 rounded-3xl border border-white/5">
                        <div class="flex items-center gap-4 group transition-all">
                            <img src="assets/nu_logo.png" alt="NU Logo" class="h-9 w-auto object-contain">
                            <span class="text-[11px] text-gray-200 font-bold leading-tight">คณะสถาปัตยกรรมศาสตร์ฯ มหาวิทยาลัยนเรศวร</span>
                        </div>
                        <div class="flex items-center gap-3 border-l border-white/10 pl-6">
                            <i class="ph-fill ph-map-pin text-[#FF4E45]/60 text-sm"></i>
                            <span class="text-[8px] font-bold text-gray-500 tracking-wide uppercase">Phitsanulok, Thailand</span>
                        </div>
                    </div>
                </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We'll replace the entire 3-column grid to ensure perfect cleanup and height reduction
    # Pattern to match the whole grid section
    grid_pattern = r'<!-- Mission: Thai Focus -->.*?<!-- Contact: Premium Layout -->.*?<!-- Institution: Subtler Style -->.*?(?=<div class="flex flex-col md:flex-row justify-between)'
    
    new_grid_html = f"""<!-- Mission: Thai Focus -->
                {mission_column_content}

                <!-- Contact: Premium Layout -->
                {contact_column_content}

                <!-- Institution: Subtler Style -->
                {institution_column_content}
            </div>

            <!-- Bottom Copyright & Sila Jaruek Gimmick -->
            """
            
    # Need to catch the closing tag of the grid as well
    content = re.sub(r'<div class="grid grid-cols-1 md:grid-cols-3.*?mb-10 pb-10 border-b border-white/5">.*?<!-- Bottom Copyright & Sila Jaruek Gimmick -->', 
                     f'<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6 pb-6 border-b border-white/5">{new_grid_html}', 
                     content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
