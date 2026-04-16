import glob
import re

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply changes
    content = content.replace('text-heritage-gold', 'text-[#D4AF37]')
    content = content.replace('logo-gsr', 'brightness-0 invert opacity-80 hover:opacity-100 transition-opacity duration-300')
    
    # Bump cache strings
    content = re.sub(r'\.css\?v=[\d\.]+', '.css?v=2.4', content)
    content = re.sub(r'\.js\?v=[\d\.]+', '.js?v=6.10', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
