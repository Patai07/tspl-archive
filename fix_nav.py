import glob
import re

nav_template = '''\
            <div class="flex items-center gap-4 md:gap-6 text-[10px] font-bold uppercase tracking-[0.2em] text-gray-400">
                <a href="archive.html" class="nav-link hover:text-[#0F2C59] transition-colors" data-page="archive.html"><span class="lang-th">คลัง</span><span class="lang-en hidden">Explorer</span></a>
                
                <div class="relative group py-4 -my-4 flex items-center nav-link-group" data-group="pipeline">
                    <button class="hover:text-[#0F2C59] transition-colors flex items-center gap-1 uppercase tracking-[0.2em] font-bold outline-none">
                        <span class="lang-th">กระบวนการ</span><span class="lang-en hidden">Pipeline</span>
                        <i class="ph-bold ph-caret-down text-[10px] transition-transform group-hover:rotate-180"></i>
                    </button>
                    <!-- Dropdown -->
                    <div class="absolute top-10 left-1/2 -translate-x-1/2 w-48 bg-white/95 backdrop-blur-md border border-gray-100 rounded-xl shadow-[0_12px_40px_rgba(0,0,0,0.12)] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 py-2 flex flex-col z-[70]">
                        <a href="capture.html" class="px-5 py-2.5 hover:bg-gray-50 hover:text-[#0F2C59] text-gray-500 transition-colors flex items-center gap-3 text-[9px] font-bold border-b border-gray-50">
                            <i class="ph-bold ph-camera text-[#0F2C59]/60 text-sm"></i> 01. Capture
                        </a>
                        <a href="decode.html" class="px-5 py-2.5 hover:bg-gray-50 hover:text-[#D4AF37] text-gray-500 transition-colors flex items-center gap-3 text-[9px] font-bold border-b border-gray-50">
                            <i class="ph-bold ph-fingerprint text-[#D4AF37]/60 text-sm"></i> 02. Decode
                        </a>
                        <a href="digitize.html" class="px-5 py-2.5 hover:bg-gray-50 hover:text-[#0F2C59] text-gray-500 transition-colors flex items-center gap-3 text-[9px] font-bold">
                            <i class="ph-bold ph-bezier-curve text-[#0F2C59]/60 text-sm"></i> 03. Digitize
                        </a>
                    </div>
                </div>

                <a href="methodology.html" class="nav-link hover:text-[#0F2C59] transition-colors" data-page="methodology.html"><span class="lang-th">ระเบียบวิธี</span><span class="lang-en hidden">Methodology</span></a>
                <a href="about.html" class="nav-link hover:text-[#0F2C59] transition-colors" data-page="about.html"><span class="lang-th">ผู้วิจัย</span><span class="lang-en hidden">Biography</span></a>
                <div class="flex items-center bg-gray-100 p-1 rounded-full border border-gray-200 ml-2 shadow-inner">'''

files = glob.glob('*.html')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match the navigation links block before the language toggle
    pattern = re.compile(r'<div\s+class="flex items-center gap-4 md:gap-8[^>]+>.*?(?=<div class="flex items-center bg-gray-100)', re.DOTALL)
    
    new_content = pattern.sub(nav_template, content)
    
    # Optional: Highlight active link based on current page
    # It replaces the class of the matched data-page to be active (text-[#0F2C59])
    if file in ['archive.html', 'methodology.html', 'about.html']:
        active_str = f'data-page="{file}"'
        new_content = new_content.replace(
            f'class="nav-link hover:text-[#0F2C59] transition-colors" {active_str}',
            f'class="nav-link text-[#0F2C59] transition-colors" {active_str}'
        )
    elif file in ['capture.html', 'decode.html', 'digitize.html']:
        # Keep Pipeline menu highlighted if we are inside capture, decode, digitize
        new_content = new_content.replace(
            '<button class="hover:text-[#0F2C59]',
            '<button class="text-[#0F2C59]'
        )
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Navigation hierarchy updated across all files.")
