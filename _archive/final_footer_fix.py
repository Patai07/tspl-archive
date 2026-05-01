import glob
import re

# New supporters HTML structure (Horizontal with names below)
supporters_new_html = """<div class="flex flex-wrap gap-6 mt-4">
                        <!-- Supporter 1: OCAC -->
                        <div class="flex flex-col gap-2 w-fit">
                            <div class="w-fit flex items-center gap-x-3 bg-white/5 p-2.5 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                                <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-7 w-auto">
                                <div class="flex flex-col">
                                    <span class="text-[7px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                    <span class="text-[12px] text-white font-black leading-none">สศร.</span>
                                </div>
                            </div>
                            <span class="text-[9px] text-gray-500 font-medium leading-[1.4] pl-2 max-w-[140px]">สำนักงานศิลปวัฒนธรรมร่วมสมัย</span>
                        </div>
                        
                        <!-- Supporter 2: GSR -->
                        <div class="flex flex-col gap-2 w-fit">
                            <div class="w-fit flex items-center gap-x-3 bg-white/5 p-2.5 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                                <img src="assets/กศร.svg" alt="กศร." class="h-7 w-auto">
                                <div class="flex flex-col">
                                    <span class="text-[7px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                    <span class="text-[12px] text-white font-black leading-none">กศร.</span>
                                </div>
                            </div>
                            <span class="text-[9px] text-gray-500 font-medium leading-[1.4] pl-2 max-w-[140px]">กองทุนส่งเสริมศิลปะร่วมสมัย</span>
                        </div>
                    </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match the specific supporters block in the Mission column
    # Matches <div class="flex flex-wrap gap-3"> ... OCAC ... GSR ... </div>
    pattern = r'<div class="flex flex-wrap gap-3">.*?<img src="https://www\.ocac\.go\.th/.*?<img src="assets/กศร\.svg".*?</div>\s*</div>'
    
    new_content = re.sub(pattern, supporters_new_html, content, flags=re.DOTALL)
    
    # In case it's gap-4 (like in index.html after my first update)
    if new_content == content:
        pattern = r'<div class="flex flex-wrap gap-4">.*?<img src="https://www\.ocac\.go\.th/.*?<img src="assets/กศร\.svg".*?</div>\s*</div>'
        new_content = re.sub(pattern, supporters_new_html, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
