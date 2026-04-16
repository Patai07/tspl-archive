import glob
import re

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The current string to replace
    old_str = '''                            <div class="h-9 lg:h-10 w-12 flex items-center justify-center shrink-0">
                                <img src="assets/กศร.svg" alt="กศร." class="max-h-full max-w-full brightness-0 invert opacity-80 hover:opacity-100 transition-opacity duration-300">
                            </div>'''
    
    new_str = '''                            <img src="assets/กศร.svg" alt="กศร." class="h-9 lg:h-10 w-auto shrink-0">'''

    content = content.replace(old_str, new_str)
    
    # Let's also bump js/css versions to bypass cache
    content = re.sub(r'\.css\?v=[\d\.]+', '.css?v=2.5', content)
    content = re.sub(r'\.js\?v=[\d\.]+', '.js?v=6.11', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
