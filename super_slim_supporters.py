import glob
import re

# Goal: Supporters with names below but VERY COMPACT.
# Layout:
# [Logo 1][สศร.] | [Logo 2][กศร.]
# [FullName 1]   | [FullName 2]

supporters_compact_html = """<div class="grid grid-cols-2 gap-x-4 gap-y-2 w-fit">
                        <div class="flex items-center gap-2 bg-white/5 p-2 rounded-xl border border-white/5 group hover:bg-white/[0.08] transition-all">
                            <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-6 w-auto">
                            <span class="text-[10px] text-white font-extrabold uppercase">สศร.</span>
                        </div>
                        <div class="flex items-center gap-2 bg-white/5 p-2 rounded-xl border border-white/5 group hover:bg-white/[0.08] transition-all">
                            <img src="assets/กศร.svg" alt="กศร." class="h-6 w-auto">
                            <span class="text-[10px] text-white font-extrabold uppercase">กศร.</span>
                        </div>
                        <span class="text-[7.5px] text-gray-600 font-medium leading-none px-1">สำนักงานศิลปวัฒนธรรมร่วมสมัย</span>
                        <span class="text-[7.5px] text-gray-600 font-medium leading-none px-1">กองทุนส่งเสริมศิลปะร่วมสมัย</span>
                    </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Target the supporter flex container precisely
    # It has OCAC and GSR logos inside.
    pattern = r'<div class="flex flex-wrap gap-3">.*?<img src="https://www\.ocac\.go\.th/.*?<img src="assets/กศร\.svg".*?</div>\s*</div>'
    
    new_content = re.sub(pattern, supporters_compact_html, content, flags=re.DOTALL)
    
    # In case of index.html after some earlier edits (if not reverted perfectly)
    if new_content == content:
        pattern = r'<div class="flex flex-wrap gap-4">.*?<img src="https://www\.ocac\.go\.th/.*?<img src="assets/กศร\.svg".*?</div>\s*</div>'
        new_content = re.sub(pattern, supporters_compact_html, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
