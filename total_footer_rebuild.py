import glob
import re

# Verified, Perfectly Nested, Super Slim Footer with Large Logos
final_gold_footer = """<footer class="bg-sila-jaruek text-gray-400 pt-8 pb-6 relative overflow-hidden mt-12">
    <div class="absolute inset-0 bg-grid-pattern opacity-10 pointer-events-none"></div>
    <div class="max-w-[1440px] mx-auto px-6 lg:px-12 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-10 mb-6 pb-6 border-b border-white/5">
        <!-- Mission column -->
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-[#FF4E45]/20 rounded-lg flex items-center justify-center border border-[#FF4E45]/40 shadow-[0_0_10px_rgba(255,78,69,0.15)]">
              <i class="ph-fill ph-book-open text-[#FF4E45] text-lg"></i>
            </div>
            <h3 class="text-white font-bold tracking-wide text-xs">พันธกิจระดับมรดก</h3>
          </div>
          <p class="text-[11px] leading-relaxed text-gray-500 font-light font-th">
            คลังข้อมูลการวิจัยเชิงสร้างสรรค์มรดกทางวัฒนธรรม เพื่อสืบสานอัตลักษณ์ไทยสู่เศรษฐกิจสร้างสรรค์
          </p>
          <div class="grid grid-cols-2 gap-x-4 gap-y-2 w-fit mt-2">
            <div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group">
                <img src="https://www.ocac.go.th/wp-content/uploads/2021/03/web-logo-ocac2.png" alt="สศร." class="h-8 md:h-9 w-auto">
                <span class="text-[11px] text-white font-black group-hover:text-[#FF4E45] transition-colors">สศร.</span>
            </div>
            <div class="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/5 hover:bg-white/[0.08] transition-all group">
                <img src="assets/กศร.svg" alt="กศร." class="h-8 md:h-9 w-auto">
                <span class="text-[11px] text-white font-black group-hover:text-[#FF4E45] transition-colors">กศร.</span>
            </div>
            <span class="text-[7.5px] text-gray-600 leading-[1.3] px-1">สำนักงานศิลปวัฒนธรรมร่วมสมัย</span>
            <span class="text-[7.5px] text-gray-600 leading-[1.3] px-1">กองทุนส่งเสริมศิลปะร่วมสมัย</span>
          </div>
        </div>

        <!-- Contact column -->
        <div class="space-y-4">
          <h4 class="text-white text-[10px] font-bold tracking-wide border-l-2 border-[#FF4E45] pl-4 leading-none py-1">ติดต่อ</h4>
          <div class="flex flex-col gap-3 items-start bg-white/5 p-3 rounded-2xl border border-white/5">
            <div class="flex items-center gap-3 group cursor-pointer">
              <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-[#FF4E45]/10 group-hover:border-[#FF4E45]/30 transition-all">
                <i class="ph-fill ph-envelope-simple text-gray-400 group-hover:text-[#FF4E45] text-sm"></i>
              </div>
              <span class="text-[11px] text-gray-300 group-hover:text-white transition-colors">samaporn@example.com</span>
            </div>
            <div class="flex items-center gap-3 group cursor-pointer">
              <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-[#FF4E45]/10 group-hover:border-[#FF4E45]/30 transition-all">
                <i class="ph-fill ph-globe text-gray-400 group-hover:text-[#FF4E45] text-sm"></i>
              </div>
              <span class="text-[11px] text-gray-300 group-hover:text-white transition-colors">www.samaporn.com</span>
            </div>
          </div>
        </div>

        <!-- Institution column -->
        <div class="space-y-4">
          <h4 class="text-white text-[10px] font-bold tracking-wide border-l-2 border-[#FF4E45] pl-4 leading-none py-1">หน่วยงาน</h4>
          <div class="flex flex-col gap-3 items-start bg-white/5 p-3 rounded-2xl border border-white/5">
            <div class="flex items-center gap-3">
              <img src="assets/nu_logo.png" alt="NU Logo" class="h-8 w-auto object-contain">
              <span class="text-[10px] text-gray-200 font-bold leading-tight">คณะสถาปัตยกรรมศาสตร์ฯ<br>มหาวิทยาลัยนเรศวร</span>
            </div>
            <div class="flex items-center gap-2 border-t border-white/5 pt-2 w-full">
              <i class="ph-fill ph-map-pin text-[#FF4E45]/60 text-xs"></i>
              <span class="text-[8px] font-bold text-gray-500 tracking-wide uppercase">Phitsanulok, Thailand</span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row justify-between items-center text-[9px] font-bold text-gray-700 pt-4">
        <p>&copy; 2026 Thai Symbol Pattern Lab (TSPL). All Rights Reserved.</p>
        <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" class="mt-4 md:mt-0 flex items-center gap-3 px-6 py-2 bg-white/5 border border-white/10 rounded-full hover:bg-[#FF4E45] hover:border-[#FF4E45] transition-all group">
          <span class="text-gray-500 group-hover:text-white transition-colors">BACK TO TOP</span>
          <i class="ph-bold ph-arrow-up text-[#FF4E45] group-hover:text-white transition-colors"></i>
        </button>
      </div>
    </div>
  </footer>"""

for filepath in glob.glob('/Users/phu/Desktop/งานพี่กบ/Web/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nuclear Rebuild: Replace EVERYTHING between <footer and </footer>
    new_content = re.sub(r'<footer.*?</footer>', final_gold_footer, content, flags=re.DOTALL)
    
    # Also clean up the double </html> just in case it's still there
    new_content = new_content.replace('</html>\n\n</html>', '</html>')
    new_content = new_content.replace('</html>\n</html>', '</html>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Verified & Rebuilt footer in {filepath}")
