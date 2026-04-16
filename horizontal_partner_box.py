import glob
import re

# Goal: Horizontal layout within a single box to keep it short (fewer rows).
# Layout: [Logo 1] [Text 1] [Vertical Divider] [Logo 2] [Text 2]

compact_unified_html = """                    <div class="bg-white/5 p-4 rounded-2xl border border-white/5 w-fit">
                        <div class="flex flex-wrap items-center gap-x-8 gap-y-4">
                            <!-- Support 1 -->
                            <div class="flex items-center gap-4">
                                <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-8 lg:h-9 w-auto">
                                <div class="flex flex-col">
                                    <span class="text-[9px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                    <span class="text-[10px] text-gray-300 font-medium leading-tight">สศร.</span>
                                </div>
                            </div>
                            <!-- Support 2 -->
                            <div class="w-px h-6 bg-white/10 hidden sm:block"></div>
                            <div class="flex items-center gap-4">
                                <img src="assets/กศร.svg" alt="กศร." class="h-8 lg:h-9 w-auto">
                                <div class="flex flex-col">
                                    <span class="text-[9px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                    <span class="text-[10px] text-gray-300 font-medium leading-tight">กศร.</span>
                                </div>
                            </div>
                        </div>
                    </div>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the previous unified box layout
    pattern = r'<div class="bg-white/5 p-4 lg:p-5 rounded-\[1\.5rem\] border border-white/5 w-fit">.*?<!-- Texts Column -->.*?</div>\s*</div>\s*</div>'
    
    new_content = re.sub(r'<div class="bg-white/5 p-4 lg:p-5 rounded-\[1\.5rem\].*?</div>\s*</div>\s*</div>', compact_unified_html, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
