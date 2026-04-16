import glob
import re

# We want to target the partner logo boxes.
# They look like: <div class="flex items-center gap-6 bg-white/5 p-4 lg:p-5 rounded-3xl border border-white/5 group transition-all hover:bg-white/[0.08]">
# And the images inside: h-9 lg:h-10

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Enlarge logos: h-9 lg:h-10 -> h-12 lg:h-14
    # Note: OCAC logo has h-9 lg:h-10. กศร logo has h-9 lg:h-10.
    content = content.replace('class="h-9 lg:h-10 w-auto"', 'class="h-12 lg:h-14 w-auto"')
    content = content.replace('class="h-9 lg:h-10 w-auto shrink-0"', 'class="h-12 lg:h-14 w-auto shrink-0"')

    # 2. Reduce capsule width: add w-fit to the flex containers of logos
    # Target: <div class="flex items-center gap-6 bg-white/5 p-4 lg:p-5 rounded-3xl border border-white/5 group transition-all hover:bg-white/[0.08]">
    # Replace with: <div class="w-fit flex items-center gap-6 bg-white/5 p-4 lg:p-5 rounded-3xl border border-white/5 group transition-all hover:bg-white/[0.08]">
    content = content.replace('flex items-center gap-6 bg-white/5 p-4 lg:p-5 rounded-3xl border border-white/5 group', 'w-fit flex items-center gap-6 bg-white/5 p-4 lg:p-5 rounded-3xl border border-white/5 group')

    # Also check index.html special case if any
    content = content.replace('class="h-9 w-auto"', 'class="h-12 w-auto"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
