import glob
import re

def fix_footer(content):
    # Fix Email
    email_pattern = r'(<div class="flex items-center gap-3 group cursor-pointer">\s*<div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-\[#FF4E45\]/10 group-hover:border-\[#FF4E45\]/30 transition-all">\s*<i class="ph-fill ph-envelope-simple text-gray-400 group-hover:text-\[#FF4E45\] text-sm"></i>\s*</div>\s*<span class="text-\[11px\] text-gray-300 group-hover:text-white transition-colors">)(.*?)(</span>\s*</div>)'
    
    def replace_email(match):
        prefix = match.group(1)
        email = match.group(2)
        suffix = match.group(3)
        new_prefix = prefix.replace('<div class="flex items-center gap-3 group cursor-pointer">', f'<a href="mailto:{email}" class="flex items-center gap-3 group cursor-pointer text-inherit no-underline">')
        new_suffix = suffix.replace('</div>', '</a>')
        return new_prefix + email + new_suffix

    content = re.sub(email_pattern, replace_email, content, flags=re.DOTALL)

    # Fix Website
    web_pattern = r'(<div class="flex items-center gap-3 group cursor-pointer">\s*<div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-\[#FF4E45\]/10 group-hover:border-\[#FF4E45\]/30 transition-all">\s*<i class="ph-fill ph-globe text-gray-400 group-hover:text-\[#FF4E45\] text-sm"></i>\s*</div>\s*<span class="text-\[11px\] text-gray-300 group-hover:text-white transition-colors">)(.*?)(</span>\s*</div>)'

    def replace_web(match):
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)
        full_url = url if url.startswith('http') else f'http://{url}'
        new_prefix = prefix.replace('<div class="flex items-center gap-3 group cursor-pointer">', f'<a href="{full_url}" target="_blank" class="flex items-center gap-3 group cursor-pointer text-inherit no-underline">')
        new_suffix = suffix.replace('</div>', '</a>')
        return new_prefix + url + new_suffix

    content = re.sub(web_pattern, replace_web, content, flags=re.DOTALL)

    # Fix OCAC Logo
    ocac_pattern = r'(<div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/\[0\.08\] transition-all group">\s*<img src="https://www\.ocac\.go\.th/.*?alt="สศร\.".*?>\s*<span class="text-\[11px\] text-white font-black group-hover:text-\[#FF4E45\] transition-colors">สศร\.</span>\s*</div>)'
    
    def replace_ocac(match):
        inner = match.group(1)
        new_inner = inner.replace('<div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group">', 
                                  '<a href="https://www.ocac.go.th" target="_blank" class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group no-underline">')
        new_inner = new_inner.replace('</div>', '</a>')
        return new_inner

    content = re.sub(ocac_pattern, replace_ocac, content, flags=re.DOTALL)

    # Fix Culture Fund Logo
    fund_pattern = r'(<div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/\[0\.08\] transition-all group">\s*<img src="assets/กศร\.svg" alt="กศร\.".*?>\s*<span class="text-\[11px\] text-white font-black group-hover:text-\[#FF4E45\] transition-colors">กศร\.</span>\s*</div>)'

    def replace_fund(match):
        inner = match.group(1)
        new_inner = inner.replace('<div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group">', 
                                  '<a href="https://www.culturefund.go.th" target="_blank" class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group no-underline">')
        new_inner = new_inner.replace('</div>', '</a>')
        return new_inner

    content = re.sub(fund_pattern, replace_fund, content, flags=re.DOTALL)

    return content

html_files = glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html')
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = fix_footer(content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed footer links in {filepath}")
    else:
        print(f"No changes needed for {filepath}")
