import glob
import re

# Refined Slim Footer for Process Pages
# - Fixed </div> nesting
# - 3 columns for minimal height (Mission, Contact, Institution)
# - Supporter names side-by-side

supporters_new_html = """<div class="grid grid-cols-2 gap-x-4 gap-y-1.5 w-fit mt-3">
                        <div class="flex items-center gap-2 bg-white/5 p-1.5 rounded-lg border border-white/5">
                            <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-5 w-auto">
                            <span class="text-[9px] text-white font-extrabold">สศร.</span>
                        </div>
                        <div class="flex items-center gap-2 bg-white/5 p-1.5 rounded-lg border border-white/5">
                            <img src="assets/กศร.svg" alt="กศร." class="h-5 w-auto">
                            <span class="text-[9px] text-white font-extrabold">กศร.</span>
                        </div>
                        <span class="text-[8px] text-gray-600 leading-none">สำนักงานศิลปวัฒนธรรมร่วมสมัย</span>
                        <span class="text-[8px] text-gray-600 leading-none">กองทุนส่งเสริมศิลปะร่วมสมัย</span>
                    </div>"""

for filename in ['capture.html', 'decode.html', 'digitize.html']:
    filepath = f'/Users/phu/Desktop/งานพี่กบ/Web/{filename}'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix the double </html> at the end
    content = content.replace('</html>\n\n</html>', '</html>')
    content = content.replace('</html>\n</html>', '</html>')

    # 2. Fix the broken <footer> structure.
    # We will replace from <footer to </footer> with a clean, one-row footer.
    
    clean_footer = f"""  <footer class="bg-sila-jaruek text-gray-400 pt-8 pb-6 relative overflow-hidden mt-12">
    <div class="absolute inset-0 bg-grid-pattern opacity-10 pointer-events-none"></div>
    <div class="max-w-[1440px] mx-auto px-6 lg:px-12 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-10 mb-6 pb-6 border-b border-white/5">
        <!-- Mission -->
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-[#FF4E45]/20 rounded-lg flex items-center justify-center border border-[#FF4E45]/40">
              <i class="ph-fill ph-book-open text-[#FF4E45] text-lg"></i>
            </div>
            <h3 class="text-white font-bold tracking-wide text-xs">พันธกิจระดับมรดก</h3>
          </div>
          <p class="text-[11px] leading-relaxed text-gray-500 font-light font-th">
            คลังข้อมูลการวิจัยเชิงสร้างสรรค์มรดกทางวัฒนธรรม เพื่อสืบสานอัตลักษณ์ไทยสู่เศรษฐกิจสร้างสรรค์
          </p>
          {supporters_new_html}
        </div>

        <!-- Contact (Now smaller) -->
        <div class="space-y-3">
          <h4 class="text-white text-[10px] font-bold tracking-wide border-l-2 border-[#FF4E45] pl-4 leading-none py-1">ติดต่อ</h4>
          <div class="flex flex-col gap-3 items-start bg-white/5 p-3 rounded-2xl border border-white/5">
            <div class="flex items-center gap-3">
              <i class="ph-fill ph-envelope-simple text-[#FF4E45] text-sm"></i>
              <span class="text-[11px] text-gray-300">samaporn@example.com</span>
            </div>
            <div class="flex items-center gap-3">
              <i class="ph-fill ph-globe text-[#FF4E45] text-sm"></i>
              <span class="text-[11px] text-gray-300">www.samaporn.com</span>
            </div>
          </div>
        </div>

        <!-- Institution -->
        <div class="space-y-3">
          <h4 class="text-white text-[10px] font-bold tracking-wide border-l-2 border-[#FF4E45] pl-4 leading-none py-1">หน่วยงาน</h4>
          <div class="flex flex-col gap-3 items-start bg-white/5 p-3 rounded-2xl border border-white/5">
            <div class="flex items-center gap-3">
              <img src="assets/nu_logo.png" alt="NU Logo" class="h-7 w-auto">
              <span class="text-[10px] text-gray-200 font-bold leading-tight">สถาปัตยกรรมศาสตร์ฯ ม.นเรศวร</span>
            </div>
            <div class="flex items-center gap-2 opacity-50">
              <i class="ph-fill ph-map-pin text-[#FF4E45] text-xs"></i>
              <span class="text-[8px] font-bold tracking-wide uppercase">Phitsanulok, Thailand</span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row justify-between items-center text-[9px] font-bold text-gray-600">
        <p>&copy; 2026 Thai Symbol Pattern Lab (TSPL). All Rights Reserved.</p>
        <button onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" class="mt-4 md:mt-0 flex items-center gap-2 text-[#FF4E45] opacity-60 hover:opacity-100 transition-opacity">
          <span>BACK TO TOP</span>
          <i class="ph-bold ph-arrow-up"></i>
        </button>
      </div>
    </div>
  </footer>"""

    content = re.sub(r'<footer.*?</footer>', clean_footer, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
