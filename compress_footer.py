import glob
import re

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Reduce footer vertical padding
    content = content.replace('pt-16 md:pt-24 pb-12', 'pt-10 md:pt-14 pb-8')

    # 2. Reduce gap between footer columns
    content = content.replace('grid-cols-1 md:grid-cols-3 gap-16 mb-16 pb-16', 'grid-cols-1 md:grid-cols-3 gap-8 mb-10 pb-10')

    # 3. Shrink the Unified Partner Box padding and rounding
    content = content.replace('p-6 lg:p-8 rounded-[2.5rem]', 'p-4 lg:p-5 rounded-[1.5rem]')
    content = content.replace('gap-8', 'gap-4 lg:gap-6') # gap between logos and text
    content = content.replace('pr-8', 'pr-4 lg:pr-6') # pr for logos column

    # 4. Shrink the Logos in the unified box
    content = content.replace('h-10 lg:h-12 w-auto', 'h-8 lg:h-9 w-auto')

    # 5. Shrink other capsules (Institution)
    content = content.replace('p-5 rounded-3xl', 'p-4 rounded-2xl')
    
    # 6. Reduce vertical gaps in list/contact sections
    content = content.replace('gap-8', 'gap-4') # gap in contact section
    content = content.replace('space-y-8', 'space-y-4') # vertical spacing in columns

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
