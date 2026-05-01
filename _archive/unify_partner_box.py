import glob
import re

# We will replace the entire "Mission: Thai Focus" partner section with a unified capsule.
# Current structure in all files:
# <div class="flex flex-col gap-3">
#     <div class="w-fit flex items-center gap-6 ..."> ... </div>
#     <div class="w-fit flex items-center gap-6 ..."> ... </div>
# </div>

unified_html = """                    <div class="bg-white/5 p-6 lg:p-8 rounded-[2.5rem] border border-white/5 w-fit">
                        <div class="flex items-center gap-8">
                            <!-- Logos Column -->
                            <div class="flex flex-col gap-6 items-center border-r border-white/10 pr-8">
                                <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-10 lg:h-12 w-auto">
                                <img src="assets/กศร.svg" alt="กศร." class="h-10 lg:h-12 w-auto">
                            </div>
                            <!-- Texts Column -->
                            <div class="flex flex-col gap-6">
                                <div>
                                    <span class="text-[9px] lg:text-[10px] font-bold text-[#FF4E45] tracking-wide block mb-1">สนับสนุนโดย</span>
                                    <span class="text-[11px] lg:text-[12px] text-gray-300 font-medium leading-tight">สำนักงานศิลปวัฒนธรรมร่วมสมัย (สศร.)</span>
                                </div>
                                <div>
                                    <span class="text-[9px] lg:text-[10px] font-bold text-[#FF4E45] tracking-wide block mb-1">ร่วมสนับสนุนการวิจัยโดย</span>
                                    <span class="text-[11px] lg:text-[12px] text-gray-300 font-medium leading-tight">กองทุนส่งเสริมศิลปะร่วมสมัย (กศร.)</span>
                                </div>
                            </div>
                        </div>
                    </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the container we just made in the previous turn
    pattern = r'<div class="flex flex-col gap-3">.*?<img src="assets/กศร.svg" alt="กศร." class="h-12 lg:h-14 w-auto shrink-0">.*?</div>\s*</div>'
    
    # Let's be more precise with re.DOTALL
    new_content = re.sub(r'<div class="flex flex-col gap-3">.*?<img src="assets/กศร.svg".*?</div>\s*</div>', unified_html, content, flags=re.DOTALL)
    
    if new_content == content:
        # Fallback if first regex failed due to different height in previous turno
        new_content = re.sub(r'<div class="flex flex-col gap-3">.*?<img src="assets/กศร.svg".*?</div>\s*</div>', unified_html, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
