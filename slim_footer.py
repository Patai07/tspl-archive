import glob
import re

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Revert to the two separate partner capsules layout (Horizontal version)
    # The user liked seeing them as separate entities but "Row ไม่เยอะ"
    # Actually, I'll put the two capsules side-by-side in a flex-row to keep it low.
    
    revert_partners = """                    <div class="flex flex-wrap gap-4">
                        <div class="w-fit flex items-center gap-x-4 bg-white/5 p-3 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                            <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-8 w-auto">
                            <div class="flex flex-col">
                                <span class="text-[8px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                <span class="text-[10px] text-gray-300 font-medium leading-tight">สศร.</span>
                            </div>
                        </div>
                        <div class="w-fit flex items-center gap-x-4 bg-white/5 p-3 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]">
                            <img src="assets/กศร.svg" alt="กศร." class="h-8 w-auto">
                            <div class="flex flex-col">
                                <span class="text-[8px] font-bold text-[#FF4E45] tracking-wide block leading-none mb-1">สนับสนุนโดย</span>
                                <span class="text-[10px] text-gray-300 font-medium leading-tight">กศร.</span>
                            </div>
                        </div>
                    </div>"""

    # Replace the unified box from previous turn
    content = re.sub(r'<div class="bg-white/5 p-4 rounded-2xl border border-white/5 w-fit">.*?</div>\s*</div>', revert_partners, content, flags=re.DOTALL)

    # 2. Make Contact row horizontal
    # Find: <div class="flex flex-col gap-4 lg:gap-6">
    content = content.replace('flex flex-col gap-4 lg:gap-6', 'flex flex-row flex-wrap gap-6 lg:gap-10')

    # 3. Make Institution / Location horizontal
    # The institution block and location are in same div.
    # Find: <div class="space-y-4"> ... Institution Block ... Location Block ... </div>
    # Actually, let's just target the institution block and make it more horizontal.
    content = content.replace('flex items-center gap-6 bg-white/5 p-4 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]', 'w-fit flex items-center gap-4 bg-white/5 p-3 rounded-2xl border border-white/5 group transition-all hover:bg-white/[0.08]')

    # 4. Make footer grid 1col on mobile, but on md: maybe we need to adjust to keep height low.
    # We already have md:grid-cols-3.

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
