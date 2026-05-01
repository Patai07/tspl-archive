import glob
import re

# Refined supporters HTML structure
# - Centered text below capsule
# - Uniform width containers for better alignment
# - Balanced spacing

refined_supporters_html = """                    <div class="flex flex-wrap gap-x-10 gap-y-8 mt-6">
                        <!-- Supporter 1: OCAC -->
                        <div class="flex flex-col items-center gap-3 w-fit max-w-[160px]">
                            <div class="w-full flex items-center justify-center gap-x-4 bg-white/5 p-3 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                                <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-8 w-auto grayscale group-hover:grayscale-0 transition-all opacity-80 group-hover:opacity-100">
                                <div class="flex flex-col items-start">
                                    <span class="text-[7px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                    <span class="text-[13px] text-white font-black leading-none">สศร.</span>
                                </div>
                            </div>
                            <span class="text-[10px] text-gray-500 font-medium leading-tight text-center px-1">สำนักงานศิลปวัฒนธรรมร่วมสมัย</span>
                        </div>
                        
                        <!-- Supporter 2: GSR -->
                        <div class="flex flex-col items-center gap-3 w-fit max-w-[160px]">
                            <div class="w-full flex items-center justify-center gap-x-4 bg-white/5 p-3 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                                <img src="assets/กศร.svg" alt="กศร." class="h-8 w-auto grayscale group-hover:grayscale-0 transition-all opacity-80 group-hover:opacity-100">
                                <div class="flex flex-col items-start">
                                    <span class="text-[7px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                    <span class="text-[13px] text-white font-black leading-none">กศร.</span>
                                </div>
                            </div>
                            <span class="text-[10px] text-gray-500 font-medium leading-tight text-center px-1">กองทุนส่งเสริมศิลปะร่วมสมัย</span>
                        </div>
                    </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match the previous layout I just added
    pattern = r'<div class="flex flex-wrap gap-6 mt-4">.*?<img src="https://www\.ocac\.go\.th/.*?<img src="assets/กศร\.svg".*?</div>\s*</div>\s*</div>'
    
    new_content = re.sub(pattern, refined_supporters_html, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
