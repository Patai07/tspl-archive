import glob
import re
import os

target_html = """                    <div class="flex flex-col gap-3">
                        <div class="flex items-center gap-6 bg-white/5 p-4 lg:p-5 rounded-3xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                            <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร."
                                class="h-9 lg:h-10 w-auto">
                            <div class="flex flex-col">
                                <span class="text-[9px] lg:text-[10px] font-bold text-[#FF4E45] tracking-wide">สนับสนุนโดย</span>
                                <span class="text-[10px] text-gray-300 font-medium leading-tight">สำนักงานศิลปวัฒนธรรมร่วมสมัย<br class="block sm:hidden lg:block">(สศร.)</span>
                            </div>
                        </div>
                        <div class="flex items-center gap-6 bg-white/5 p-4 lg:p-5 rounded-3xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                            <div class="h-9 lg:h-10 w-12 flex items-center justify-center shrink-0">
                                <img src="assets/กศร.svg" alt="กศร." class="max-h-full max-w-full brightness-0 invert opacity-80 hover:opacity-100 transition-opacity duration-300">
                            </div>
                            <div class="flex flex-col">
                                <span class="text-[9px] lg:text-[10px] font-bold text-[#FF4E45] tracking-wide">ร่วมสนับสนุนการวิจัยโดย</span>
                                <span class="text-[10px] text-gray-300 font-medium leading-tight">กองทุนส่งเสริมศิลปะร่วมสมัย<br class="block sm:hidden lg:block">(กศร.)</span>
                            </div>
                        </div>
                    </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply changes to about.html colors
    content = content.replace('border-[#D4AF37]/30', 'border-gray-100')
    content = content.replace('text-[#D4AF37]', 'text-[#FF4E45]')
    
    # Revert index.html colors
    content = content.replace('text-4xl sm:text-5xl font-bold text-[#FF4E45] tracking-tighter tabular-nums leading-none', 'text-4xl sm:text-5xl font-bold text-white tracking-tighter tabular-nums leading-none')
    
    # Replace the specific block created by the previous replace script or sed
    # It might have varying spacing, so regex to catch the whole block
    pattern = r'<div class="flex items-center gap-6 bg-white/5 p-5 rounded-3xl border border-white/5">\s*<img src="https://www\.ocac\.go\.th/[^"]*"\s*alt="สศร\."\s*class="[^"]*">\s*<div class="w-px h-8 bg-white/10"></div>\s*<img src="assets/กศร\.svg" alt="กศร\." class="[^"]*">\s*<div class="flex flex-col">\s*<span class="text-\[10px\] font-bold text-\[#FF4E45\] tracking-wide">สนับสนุนโดย</span>\s*<span class="text-\[10px\] text-gray-300 font-medium">สำนักงานศิลปวัฒนธรรมร่วมสมัย\s*\(สศร\.\)</span>\s*</div>\s*</div>'
    
    content = re.sub(pattern, target_html, content)
    
    # Just in case there are still drop-shadow text
    content = re.sub(r' drop-shadow-\[[^\]]+\]', '', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
