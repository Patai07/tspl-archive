import glob
import re

# Goal: Enlarge logos in the super-slim footer layout
# Pattern to match the existing super-slim layout

old_supporters_pattern = r'<div class="grid grid-cols-2 gap-x-4 gap-y-1.5 w-fit mt-3">.*?<img src="https://www\.ocac\.go\.th/.*?class="h-5 w-auto">.*?<img src="assets/กศร\.svg".*?class="h-5 w-auto">.*?</div>'

new_supporters_html = """<div class="grid grid-cols-2 gap-x-4 gap-y-2 w-fit mt-4">
                        <div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group">
                            <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-8 md:h-9 w-auto">
                            <span class="text-[11px] text-white font-black group-hover:text-[#FF4E45] transition-colors">สศร.</span>
                        </div>
                        <div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group">
                            <img src="assets/กศร.svg" alt="กศร." class="h-8 md:h-9 w-auto">
                            <span class="text-[11px] text-white font-black group-hover:text-[#FF4E45] transition-colors">กศร.</span>
                        </div>
                        <span class="text-[8px] text-gray-600 leading-[1.3] px-1">สำนักงานศิลปวัฒนธรรมร่วมสมัย</span>
                        <span class="text-[8px] text-gray-600 leading-[1.3] px-1">กองทุนส่งเสริมศิลปะร่วมสมัย</span>
                    </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(old_supporters_pattern, new_supporters_html, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
    else:
        print(f"No match in {filepath}")
