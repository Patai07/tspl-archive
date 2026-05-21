/**
 * TSPL AI Prompt Generator JS
 * ===========================
 * Handles the interactive prompt-building logic, containing the 100 styles dataset,
 * dynamic pattern loading from Google Sheet CSV, and UI event binding.
 */

// 1. 100 Styles Dataset
const STYLES_DATASET = {
    "photography": {
        "titleTH": "ภาพถ่ายสมจริง",
        "titleEN": "Photography",
        "icon": "ph-camera",
        "styles": [
            { "id": 1, "nameTH": "ภาพถ่ายมาโคร", "nameEN": "Macro Photography", "keywords": "macro photography, close-up shot, extreme detail, micro textures, sharp focus, shallow depth of field" },
            { "id": 2, "nameTH": "ภาพถ่ายแนวสตรีท", "nameEN": "Street Photography", "keywords": "street photography, candid shot, urban life scene, raw emotion, cinematic color grading, natural street light" },
            { "id": 3, "nameTH": "ภาพแอบถ่ายปาปารัสซี่", "nameEN": "Paparazzi Shot", "keywords": "paparazzi photography style, high-flash, direct light, candid capture, slight motion blur, low-angle snapshot" },
            { "id": 4, "nameTH": "ภาพถ่ายแฟชั่นนิตยสาร", "nameEN": "Editorial Fashion", "keywords": "editorial fashion photography, high fashion model, avant-garde styling, dramatic studio lighting, minimalist backdrops" },
            { "id": 5, "nameTH": "ภาพสัตว์ป่าธรรมชาติ", "nameEN": "Wildlife National Geographic", "keywords": "wildlife photography, National Geographic style, telephoto lens capture, animal in natural habitat, sharp details, realistic textures" },
            { "id": 6, "nameTH": "ภาพถ่ายสถาปัตยกรรม", "nameEN": "Architectural Photography", "keywords": "architectural photography, symmetrical composition, leading lines, clean geometric shadows, wide-angle lens" },
            { "id": 7, "nameTH": "ภาพถ่ายเปิดหน้ากล้องนาน", "nameEN": "Long Exposure", "keywords": "long exposure photography, motion trails, silky smooth water textures, light streaks, dynamic motion capture" },
            { "id": 8, "nameTH": "ภาพถ่ายใต้น้ำ", "nameEN": "Underwater Photography", "keywords": "underwater photography, light rays refracting through clear water, bubble particles, aquatic atmosphere, blue-green color tones" },
            { "id": 9, "nameTH": "ภาพถ่ายมุมสูงจากโดรน", "nameEN": "Drone/Aerial View", "keywords": "aerial view, drone photography, bird's-eye view, topographic patterns, vast landscape composition" },
            { "id": 10, "nameTH": "ภาพถ่ายกล้องโพลารอยด์", "nameEN": "Polaroid/Instax", "keywords": "Polaroid photo, vintage film grain, high contrast, warm color cast, iconic white border frame texture" }
        ]
    },
    "fine_art": {
        "titleTH": "ศิลปะคลาสสิก",
        "titleEN": "Fine Art",
        "icon": "ph-paint-brush",
        "styles": [
            { "id": 11, "nameTH": "ภาพวาดสีน้ำมัน", "nameEN": "Oil Painting", "keywords": "oil painting style, thick impasto brushstrokes, rich physical paint textures, visible canvas weave" },
            { "id": 12, "nameTH": "ภาพวาดสีน้ำ", "nameEN": "Watercolor", "keywords": "watercolor painting, bleeding colors, soft wash textures, splashed pigments, clean white paper background texture" },
            { "id": 13, "nameTH": "ภาพสเก็ตช์ถ่าน", "nameEN": "Charcoal Sketch", "keywords": "charcoal sketch, rough textured paper background, smudge details, high contrast cross-hatching, hand-drawn look" },
            { "id": 14, "nameTH": "ภาพพิมพ์ไม้ญี่ปุ่น", "nameEN": "Ukiyo-e", "keywords": "Ukiyo-e woodblock print style, flat color areas, distinct black outlines, traditional Japanese art aesthetic" },
            { "id": 15, "nameTH": "ศิลปะเรอเนซองส์", "nameEN": "Renaissance", "keywords": "Renaissance painting style, sfumato technique, dramatic chiaroscuro lighting, classical composition, Rembrandt style" },
            { "id": 16, "nameTH": "ศิลปะลัทธิประทับใจ", "nameEN": "Impressionism", "keywords": "Impressionist painting, loose visible brushstrokes, emphasis on light and color movement, outdoor lighting, Monet style" },
            { "id": 17, "nameTH": "ศิลปะเหนือจริง", "nameEN": "Surrealism", "keywords": "surrealist art style, dreamlike scene, melting objects, bizarre juxtapositions, Salvador Dali style" },
            { "id": 18, "nameTH": "ศิลปะบาศกนิยม", "nameEN": "Cubism", "keywords": "Cubist style painting, geometric abstraction, multiple viewpoints, fragmented planes, Picasso style" },
            { "id": 19, "nameTH": "ภาพวาดปูนเปียกผนังโบสถ์", "nameEN": "Fresco", "keywords": "mural fresco painting style, weathered plaster wall texture, pastel mineral pigments, antique church art" },
            { "id": 20, "nameTH": "กระจกสีโบสถ์วิหาร", "nameEN": "Stained Glass", "keywords": "stained glass window style, leaded glass outlines, vibrant translucent colors glowing with light shining through" }
        ]
    },
    "digital_art": {
        "titleTH": "งานดิจิทัลและเกม",
        "titleEN": "Digital Art & Gaming",
        "icon": "ph-game-controller",
        "styles": [
            { "id": 21, "nameTH": "พิกเซลอาร์ต 8-bit", "nameEN": "8-bit / Pixel Art", "keywords": "8-bit pixel art style, retro video game graphics, limited color palette, blocky pixel grids" },
            { "id": 22, "nameTH": "งานบล็อกสามมิติ", "nameEN": "Voxel Art", "keywords": "voxel art style, 3D pixel block style, Minecraft aesthetic, clean isometric rendering" },
            { "id": 23, "nameTH": "กราฟิกเอนจินยุคใหม่", "nameEN": "Unreal Engine 5", "keywords": "Unreal Engine 5 render, highly realistic game graphics, ray tracing, global illumination, atmospheric fog, detailed 3D model" },
            { "id": 24, "nameTH": "ไซเบอร์พังก์", "nameEN": "Cyberpunk", "keywords": "cyberpunk style, glowing neon signs, futuristic city streets, rainy night reflections, dark teal and magenta color scheme" },
            { "id": 25, "nameTH": "โมเดลโพลีต่ำ", "nameEN": "Low Poly", "keywords": "low poly 3D model style, geometric facets, clean shaded rendering, flat stylized materials" },
            { "id": 26, "nameTH": "ภาพแนวคิดเกมและภาพยนตร์", "nameEN": "Concept Art", "keywords": "video game concept art, digital painting, dramatic layout, mood-focused illustration, speed painting style" },
            { "id": 27, "nameTH": "มุมมองสามมิติเฉียง", "nameEN": "Isometric Art", "keywords": "isometric 3D art, diagonal grid view, orthographic projection, stylized miniature model presentation" },
            { "id": 28, "nameTH": "ภาพฉากหลังอลังการ", "nameEN": "Digital Matte Painting", "keywords": "matte painting, epic scale cinematic background, grand fantasy landscape, photorealistic digital composite" },
            { "id": 29, "nameTH": "ศิลปะความเพี้ยนสัญญาณ", "nameEN": "Glitch Art", "keywords": "glitch art style, digital static, chromatic aberration, broken video signals, scanlines, technological failure aesthetic" },
            { "id": 30, "nameTH": "ซินธ์เวฟย้อนยุค 80s", "nameEN": "Synthwave/Retro", "keywords": "synthwave aesthetic, retro-futurism, wireframe landscape, grid horizon, glowing sun, neon pink and purple gradients" }
        ]
    },
    "animation": {
        "titleTH": "แอนิเมชันและตัวการ์ตูน",
        "titleEN": "Animation & Illustration",
        "icon": "ph-palette",
        "styles": [
            { "id": 31, "nameTH": "การ์ตูนสตูดิโอจิบลิ", "nameEN": "Studio Ghibli Style", "keywords": "Studio Ghibli anime style, hand-painted watercolor backgrounds, warm nostalgia, whimsical characters, soft lighting, Hayao Miyazaki aesthetic" },
            { "id": 32, "nameTH": "แอนิเมชัน 3D ดีสนีย์/พิกซาร์", "nameEN": "Disney/Pixar 3D", "keywords": "stylized 3D animation, Pixar characters look, clay-like smooth textures, expressive lighting, friendly shapes, vibrant color keys" },
            { "id": 33, "nameTH": "อนิเมะย้อนยุคปี 90s", "nameEN": "90s Retro Anime", "keywords": "1990s retro anime style, cel-shaded animation, hand-drawn feel, VHS tape grain, retro pastel colors" },
            { "id": 34, "nameTH": "ภาพประกอบเรียบง่ายแบนๆ", "nameEN": "Flat Illustration", "keywords": "modern flat design illustration, minimalist vector art, solid geometric shapes, vector graphics, clean lines, corporate web aesthetic" },
            { "id": 35, "nameTH": "ภาพประกอบนิทานเด็ก", "nameEN": "Children’s Book", "keywords": "whimsical children's book illustration, textured pencil shading, soft colors, playful characters, warm storybook feel" },
            { "id": 36, "nameTH": "ตัวการ์ตูนจิบิหัวโต", "nameEN": "Chibi", "keywords": "cute Chibi character style, super deformed proportion, large expressive eyes, small cute body, colorful and adorable" },
            { "id": 37, "nameTH": "คอมิกส์การ์ตูนช่องฮีโร่", "nameEN": "Comic Book Art", "keywords": "vintage comic book style, bold ink outlines, halftone dot shading patterns, action-packed panel feel, pop art colors" },
            { "id": 38, "nameTH": "ภาพวาดล้อเลียนหน้าผวน", "nameEN": "Caricature", "keywords": "stylized caricature drawing, exaggerated facial features, playful portrait, expressive lines, ink and wash sketch" },
            { "id": 39, "nameTH": "ศิลปะการตัดกระดาษซ้อนชั้น", "nameEN": "Paper Cutout", "keywords": "paper cutout art style, layered papercraft, drop shadows creating 3D depth, textured colored paper sheets" },
            { "id": 40, "nameTH": "ดินน้ำมันหยุดเคลื่อนไหว", "nameEN": "Claymation", "keywords": "claymation style, stop-motion plasticine clay model, hand-formed fingerprints, tactile textures, Wallace and Gromit style" }
        ]
    },
    "design_graphics": {
        "titleTH": "งานออกแบบและกราฟิก",
        "titleEN": "Design & Graphics",
        "icon": "ph-layout",
        "styles": [
            { "id": 41, "nameTH": "โลโก้มินิมอล", "nameEN": "Minimalist Logo", "keywords": "minimalist line art logo, vector graphic icon, simple clean shapes, high contrast, white background" },
            { "id": 42, "nameTH": "ศิลปะการจัดวางอักษร", "nameEN": "Typography Art", "keywords": "typography portrait art, words forming the shape, variable font weights, creative lettering composition, black and white" },
            { "id": 43, "nameTH": "อินโฟกราฟิก", "nameEN": "Infographic", "keywords": "modern flat infographic design, clean layout, explanatory diagrams, minimalist icons, vector graphics" },
            { "id": 44, "nameTH": "หน้าจอแอปมือถือ", "nameEN": "UI/UX Mobile App", "keywords": "clean UI/UX mobile application dashboard design, modern interface layout, sleek cards, dark mode option" },
            { "id": 45, "nameTH": "ออกแบบฉลากบรรจุภัณฑ์", "nameEN": "Product Packaging", "keywords": "premium product packaging label mockup, elegant typography, minimalist pattern, clean mockup presentation" },
            { "id": 46, "nameTH": "โปสเตอร์สไตล์อาร์ตเดโค", "nameEN": "Poster Art Deco", "keywords": "vintage Art Deco poster style, geometric decorative lines, metallic gold accents, sleek typography, 1920s luxury aesthetic" },
            { "id": 47, "nameTH": "ป๊อปอาร์ตสไตล์วอร์ฮอล", "nameEN": "Pop Art", "keywords": "pop art screenprint style, screen halftone patterns, bold primary colors, high contrast, Andy Warhol style" },
            { "id": 48, "nameTH": "ภาพซ้อนภาพศิลปะ", "nameEN": "Double Exposure", "keywords": "double exposure photography, overlay of two images, silhouette blending, artistic juxtaposition" },
            { "id": 49, "nameTH": "แบบแปลนพิมพ์เขียว", "nameEN": "Blueprint", "keywords": "technical blueprint drawing, blueprint cyan grid paper, white drafting lines, construction schematic plans, engineering layout" },
            { "id": 50, "nameTH": "ชุดไอคอนแบบเส้น", "nameEN": "Icons Set", "keywords": "set of minimalist vector outline icons, uniform stroke weight, clean grid layout, black outline on white background" }
        ]
    },
    "interior_scenery": {
        "titleTH": "ตกแต่งภายในและทิวทัศน์",
        "titleEN": "Interior & Scenery",
        "icon": "ph-house",
        "styles": [
            { "id": 51, "nameTH": "ตกแต่งบ้านแบบสแกนดิเนเวียน", "nameEN": "Scandinavian Interior", "keywords": "Scandinavian style room design, minimalist light wood furniture, clean white walls, warm cozy textiles, natural lighting" },
            { "id": 52, "nameTH": "อินดัสเทรียลลอฟต์ปูนเปลือย", "nameEN": "Industrial Loft", "keywords": "industrial loft interior, exposed brick walls, polished concrete floor, matte black steel beams, large windows, rustic wood accents" },
            { "id": 53, "nameTH": "สวนหินสไตล์เซน", "nameEN": "Zen Garden", "keywords": "Japanese Zen rock garden, raked white gravel wave patterns, basalt rocks, moss patches, bonsai tree, peaceful outdoor setting" },
            { "id": 54, "nameTH": "โลกหลังภัยพิบัติตึกร้าง", "nameEN": "Post-Apocalyptic", "keywords": "post-apocalyptic city ruins, skyscrapers covered in overgrown climbing vines, cracked asphalt road, post-apocalyptic cinematic lighting" },
            { "id": 55, "nameTH": "พังค์เครื่องจักรไอน้ำทองแดง", "nameEN": "Steampunk", "keywords": "steampunk environment, copper pipes, brass steam valves, complex gear mechanisms, warm gaslight illumination, Victorian machinery room" },
            { "id": 56, "nameTH": "ระบบนิเวศน์จิ๋วในโหลแก้ว", "nameEN": "Terrarium", "keywords": "miniature ecosystem inside a sealed glass jar terrarium, lush green moss, tiny ferns, moist soil layers, macro glass reflections" },
            { "id": 57, "nameTH": "เกาะลอยฟ้าแฟนตาซี", "nameEN": "Floating Island", "keywords": "whimsical floating island in the sky, waterfalls cascading into clouds, castle ruins, soft fantasy clouds, dreamlike scenery" },
            { "id": 58, "nameTH": "สถาปัตยกรรมกอทิกหม่นๆ", "nameEN": "Gothic Architecture", "keywords": "Gothic cathedral interior, ribbed vaulting ceiling, pointed arches, stone carvings, light rays streaming through stained glass" },
            { "id": 59, "nameTH": "ตึกพฤกษาสีเขียวรักษ์โลก", "nameEN": "Biophilic Design", "keywords": "modern biophilic skyscraper architecture, vertical gardens integrated into building facade, sustainable urban green space" },
            { "id": 60, "nameTH": "อวกาศและหมอกแก๊สเนบิวลา", "nameEN": "Space Nebula", "keywords": "vibrant cosmic space nebula, colorful glowing gas clouds in deep space, sparkling stars, galaxies, astronomical wallpaper" }
        ]
    },
    "materials_textures": {
        "titleTH": "วัสดุและพื้นผิว",
        "titleEN": "Materials & Textures",
        "icon": "ph-spheres",
        "styles": [
            { "id": 61, "nameTH": "ไหมพรมหรือโครเชต์ถัก", "nameEN": "Knitted / Crochet", "keywords": "knitted yarn texture, cozy crochet pattern, wool fibers, warm fabric weave details" },
            { "id": 62, "nameTH": "พับกระดาษญี่ปุ่นโอริกามิ", "nameEN": "Origami", "keywords": "origami paper folding art, sharp folded paper edges, clean geometric folds, matte colored paper shadows" },
            { "id": 63, "nameTH": "ผิวสะท้อนรุ้งโฮโลแกรม", "nameEN": "Holographic", "keywords": "holographic metallic finish, iridescent rainbow sheen, glossy liquid metal reflections, pearlescent colors" },
            { "id": 64, "nameTH": "กระจกฝ้าหรูหรา", "nameEN": "Frosted Glass", "keywords": "semi-transparent frosted glass sheet, blurry glass refraction behind it, minimalist mockup, sleek modern material" },
            { "id": 65, "nameTH": "โครเมียมเหลวสะท้อนเงา", "nameEN": "Liquid Metal", "keywords": "molten liquid chrome metal ripples, smooth reflective mercury surfaces, fluid metallic flow, high contrast specular highlights" },
            { "id": 66, "nameTH": "ลายปักผ้าด้วยด้ายสีสรรค์", "nameEN": "Embroidered", "keywords": "embroidered fabric texture, intricate thread stitching pattern, colorful decorative sewing on canvas base" },
            { "id": 67, "nameTH": "ห่อพลาสติกใสย่นๆ", "nameEN": "Plastic Wrap", "keywords": "sealed plastic wrap texture, glossy plastic crinkles, shrink-wrapped packaging, reflections and highlights on plastic surface" },
            { "id": 68, "nameTH": "ประติมากรรมทรายหาด", "nameEN": "Sand Sculpture", "keywords": "detailed sand sculpture, fine sand grain texture, hand-carved sand castle details, sunlit beach setting" },
            { "id": 69, "nameTH": "แกะสลักน้ำแข็งใสโปร่งแสง", "nameEN": "Ice Sculpture", "keywords": "translucent ice sculpture carving, frozen air bubbles inside, glowing light refraction through clear ice block" },
            { "id": 70, "nameTH": "หลอดไฟนีออนดัด", "nameEN": "Neon Tube", "keywords": "luminous neon tube sign light art, bent glass glowing neon tubes, electrical wire connections, ambient wall glow" }
        ]
    },
    "scientific_fx": {
        "titleTH": "เทคนิคพิเศษและวิทยาศาสตร์",
        "titleEN": "Scientific & Special FX",
        "icon": "ph-atom",
        "styles": [
            { "id": 71, "nameTH": "ภาพถ่ายรังสีเอกซเรย์", "nameEN": "X-Ray", "keywords": "X-ray imaging style, glowing skeletal structure, semi-transparent bones, diagnostic medical film, high contrast blue-cyan hue" },
            { "id": 72, "nameTH": "ภาพส่องกล้องจุลทรรศน์", "nameEN": "Microscopic", "keywords": "microscopic slide image, extreme magnification, electron microscope texture, cellular details, biological organism structure" },
            { "id": 73, "nameTH": "ภาพถ่ายกล้องจับความร้อน", "nameEN": "Thermal Imaging", "keywords": "thermal imaging infrared camera style, heat signature visualization, hot red and cold blue thermal color spectrum map" },
            { "id": 74, "nameTH": "ภาพวาดกายวิภาคเชิงการแพทย์", "nameEN": "Anatomical Drawing", "keywords": "vintage anatomical illustration, detailed muscle and bone structure layout, vintage aged paper background, ink sketch notes" },
            { "id": 75, "nameTH": "เส้นแสงทางเดินอนุภาคฟิสิกส์", "nameEN": "Particle Physics", "keywords": "subatomic particle collision trails, spiral energy paths, glowing light streaks, physics laboratory data visual" },
            { "id": 76, "nameTH": "หยดน้ำหมึกกระจายตัวในน้ำ", "nameEN": "Ink in Water", "keywords": "ink diffusion in clear water, colored ink cloud swirling, abstract fluid dynamics, slow motion liquid movement" },
            { "id": 77, "nameTH": "การระเบิดฝุ่นควันและหินปลิว", "nameEN": "Explosion/Dust", "keywords": "dramatic dust explosion debris, flying rock debris, smoke clouds, high shutter speed action shot, dramatic spotlighting" },
            { "id": 78, "nameTH": "ภาพเบลอจากการเคลื่อนที่เร็ว", "nameEN": "Motion Blur", "keywords": "high speed motion blur, dynamic panning shot, streaking background lines, sense of rapid velocity" },
            { "id": 79, "nameTH": "รูปร่างสั่นสะเทือนคลื่นเสียงบนทราย", "nameEN": "Cymatics", "keywords": "cymatics sound wave pattern on sand, geometric frequency vibration shape, scientific physics experiment, sand on metal plate" },
            { "id": 80, "nameTH": "ก้นหอยฟิโบนัชชีทองคำ", "nameEN": "Fibonacci Spiral", "keywords": "perfect Fibonacci golden spiral composition in nature, mathematical spiral geometry, organic pattern layout" }
        ]
    },
    "fantasy_horror": {
        "titleTH": "จินตนาการและสัตว์ประหลาด",
        "titleEN": "Fantasy & Horror",
        "icon": "ph-ghost",
        "styles": [
            { "id": 81, "nameTH": "สัตว์ประหลาดต่างมิติเลิฟคราฟต์", "nameEN": "Lovecraftian Horror", "keywords": "Lovecraftian cosmic horror style, ancient monster with writhing tentacles, glowing eyes in deep dark ocean depth, misty dread, eerie atmosphere" },
            { "id": 82, "nameTH": "แฟนตาซีโทนมืดมนหม่นดำ", "nameEN": "Dark Fantasy", "keywords": "dark fantasy theme, grim and gritty medieval fantasy atmosphere, dark shadows, moody gothic ruins, dark magic aesthetic" },
            { "id": 83, "nameTH": "สัตว์ในเทพนิยายและตำนาน", "nameEN": "Mythological Creature", "keywords": "epic mythological creature drawing, legendary creature, glowing aura, fantasy landscape setting, high detail" },
            { "id": 84, "nameTH": "วิญญาณโปร่งแสงลอยละล่อง", "nameEN": "Ghostly Apparition", "keywords": "translucent ghostly apparition, wispy ethereal energy trails, glowing spirit form, misty haunted forest setting" },
            { "id": 85, "nameTH": "ชีววิทยาสิ่งมีชีวิตต่างดาว", "nameEN": "Alien Biology", "keywords": "alien creature biology study, exotic bioluminescent alien flora, foreign planet landscape, science fiction concept art" },
            { "id": 86, "nameTH": "ครึ่งมนุษย์ครึ่งเครื่องจักรกล", "nameEN": "Cyborg/Android", "keywords": "futuristic cyborg android model, exposed cybernetic implants, glowing fiber optic wires, biomechanical details" },
            { "id": 87, "nameTH": "เทพผู้ทำจากแสงบริสุทธิ์จักรวาล", "nameEN": "Ethereal Being", "keywords": "divine ethereal being made of pure golden light energy, glowing celestial form, cosmic background, celestial aura" },
            { "id": 88, "nameTH": "ป่าเวทมนตร์นางฟ้าและภูตจิ๋ว", "nameEN": "Gnome/Fairy Core", "keywords": "enchanted gnome fairytale forest core, mossy tree trunks, glowing mushrooms, tiny fairy houses, mystical light dust" },
            { "id": 89, "nameTH": "ซอมบี้ล้างโลกและเมืองร้าง", "nameEN": "Zombie Apocalypse", "keywords": "gory zombie apocalypse scene, decayed zombies walking down overgrown city street, ruined buildings, horror cinematic shot" },
            { "id": 90, "nameTH": "พื้นผิวเกล็ดมังกรวาวโลหะ", "nameEN": "Dragon Scales", "keywords": "macro shot of iridescent dragon scales texture, overlapping reptilian armor plating, metallic finish details" }
        ]
    },
    "lifestyle_misc": {
        "titleTH": "ไลฟ์สไตล์และแฟชั่น",
        "titleEN": "Lifestyle & Misc",
        "icon": "ph-t-shirt",
        "styles": [
            { "id": 91, "nameTH": "จัดวางสิ่งของแล้วถ่ายจากมุมบน", "nameEN": "Flat Lay", "keywords": "flat lay photography style, items neatly arranged on a clean flat surface, shot from directly above, organized styling" },
            { "id": 92, "nameTH": "นายแบบเสื้อผ้าแนวสตรีทในตรอก", "nameEN": "Streetwear Lookbook", "keywords": "urban streetwear fashion lookbook model, modeling trendy streetwear clothing in a city alleyway, dynamic lighting" },
            { "id": 93, "nameTH": "ภาพร่างลายสักสีหมึกดำ", "nameEN": "Tattoo Design", "keywords": "flash tattoo design drawing, bold black lines, stippling dotwork shading, blackwork style, on white paper background" },
            { "id": 94, "nameTH": "ภาพสติกเกอร์ไดคัทขอบขาว", "nameEN": "Sticker Art", "keywords": "die-cut sticker art style, cute vector graphic illustration, clean thick white outer stroke boundary border, flat color" },
            { "id": 95, "nameTH": "สไตล์โบฮีเมียนสีเอิร์ธโทนอบอุ่น", "nameEN": "Bohemian Style", "keywords": "bohemian lifestyle aesthetic, macrame wall hangings, textured rugs, houseplants, earthy warm tones, sunset room lighting" },
            { "id": 96, "nameTH": "ชีวิตบ้านไร่และชนบทแสนสุข", "nameEN": "Cottagecore", "keywords": "cottagecore countryside lifestyle aesthetic, rustic brick cottage, blooming flower garden, sunlit afternoon meadow, cozy and peaceful" },
            { "id": 97, "nameTH": "เวเปอร์เวฟย้อนยุคสีม่วงพาสเทล", "nameEN": "Vaporwave", "keywords": "vaporwave aesthetic art, pink and cyan gradient skies, wireframe grids, classical Greek bust statue, nostalgic 1980s low-fi vibe" },
            { "id": 98, "nameTH": "ภาพโมเสกปูกระเบื้องแก้วชิ้นเล็ก", "nameEN": "Mosaic", "keywords": "colorful tile mosaic mural art, small glass and ceramic tiles forming the image, grout lines, textured surface" },
            { "id": 99, "nameTH": "ภาพจุดพู่กันสีดำสติปปลิง", "nameEN": "Stippling", "keywords": "stippling ink drawing, image created entirely using tiny black ink dots, varying dot density for shading, fine pen art" },
            { "id": 100, "nameTH": "โซลาร์พังก์เทคโนโลยีสีเขียว", "nameEN": "Solarpunk", "keywords": "solarpunk future city scene, lush sky gardens on skyscrapers, solar panel roof domes, clean green energy technology, bright sunny day" }
        ]
    }
};

// 2. 180 Patterns Fallback list (extracted from academic brief)
const ACADEMIC_PATTERNS = [
    // 1. Botanical & Natural (54 items)
    { id: "TSP-LST-NAT-001", nameTH: "กระหนกสามตัว", nameEN: "Kanok Sam Tua" },
    { id: "TSP-LST-NAT-002", nameTH: "กระหนกเปลว", nameEN: "Kanok Plew" },
    { id: "TSP-LST-NAT-003", nameTH: "กระหนกใบเทศ", nameEN: "Kanok Bai Thet" },
    { id: "TSP-LST-NAT-004", nameTH: "กระหนกหางหงส์", nameEN: "Kanok Hang Hong" },
    { id: "TSP-LST-NAT-005", nameTH: "กระหนกนารี", nameEN: "Kanok Naree" },
    { id: "TSP-LST-NAT-006", nameTH: "กระหนกผักกาด", nameEN: "Kanok Phakkad" },
    { id: "TSP-LST-NAT-007", nameTH: "ลายใบระกา", nameEN: "Bai Raka Motif" },
    { id: "TSP-LST-NAT-008", nameTH: "ลายหางโต", nameEN: "Hang To Motif" },
    { id: "TSP-LST-NAT-009", nameTH: "ลายเครือเถา", nameEN: "Vine Motif (Kruea Thao)" },
    { id: "TSP-LST-NAT-010", nameTH: "ลายก้านขด", nameEN: "Scrolling Foliage (Kan Khot)" },
    { id: "TSP-LST-NAT-011", nameTH: "ลายก้านขดหางโต", nameEN: "Scrolling Foliage with Hang To" },
    { id: "TSP-LST-NAT-012", nameTH: "ลายก้านขดใบเทศ", nameEN: "Scrolling Foliage with Bai Thet" },
    { id: "TSP-LST-NAT-013", nameTH: "ลายก้านต่อดอก", nameEN: "Kan Tor Dok Motif" },
    { id: "TSP-LST-NAT-014", nameTH: "ลายดอกพิกุล", "nameEN": "Pikul Flower Motif" },
    { id: "TSP-LST-NAT-015", nameTH: "ลายดอกจัน", "nameEN": "Dok Chan Motif" },
    { id: "TSP-LST-NAT-016", nameTH: "ลายดอกสี่กลีบ", "nameEN": "Four-Petal Flower Motif" },
    { id: "TSP-LST-NAT-017", nameTH: "ลายดอกบัว", "nameEN": "Lotus Motif (Dok Bua)" },
    { id: "TSP-LST-NAT-018", nameTH: "ลายบัวคว่ำ", "nameEN": "Downturned Lotus Motif (Bua Kwam)" },
    { id: "TSP-LST-NAT-019", nameTH: "ลายบัวหงาย", "nameEN": "Upturned Lotus Motif (Bua Ngai)" },
    { id: "TSP-LST-NAT-020", nameTH: "ลายบัวปากชาม", "nameEN": "Bua Pak Charn Motif" },
    { id: "TSP-LST-NAT-021", nameTH: "ลายบัวจงกล", "nameEN": "Bua Jongkol Motif" },
    { id: "TSP-LST-NAT-022", nameTH: "ลายบัวกลุ่ม", "nameEN": "Lotus Group Motif" },
    { id: "TSP-LST-NAT-023", nameTH: "ลายดอกพุดตาน", "nameEN": "Cotton Rose Motif (Phuttan)" },
    { id: "TSP-LST-NAT-024", nameTH: "ลายพุ่มข้าวบิณฑ์ใบเทศ", "nameEN": "Phum Khao Bin with Bai Thet" },
    { id: "TSP-LST-NAT-025", nameTH: "ลายรวงข้าว", "nameEN": "Rice Ear Motif" },
    { id: "TSP-LST-NAT-026", nameTH: "ลายกล้วยไม้ท้องถิ่น", "nameEN": "Wild Orchid Motif" },
    { id: "TSP-LST-NAT-027", nameTH: "ลายใบโพธิ์", "nameEN": "Bodhi Leaf Motif" },
    { id: "TSP-LST-NAT-028", nameTH: "ลายดอกไม้ประดิษฐ์ (สังคโลก)", "nameEN": "Sangkhalok Floral Motif" },
    { id: "TSP-LST-NAT-029", nameTH: "ลายช่อหางโต", "nameEN": "Hang To Bouquet" },
    { id: "TSP-LST-NAT-030", nameTH: "ลายกระหนกหางกินรี", "nameEN": "Kanok Hang Kinnaree" },
    { id: "TSP-LST-NAT-031", nameTH: "ลายเปลวรัศมี", "nameEN": "Flame Ray Motif" },
    { id: "TSP-LST-NAT-032", nameTH: "ลายคลื่นน้ำ", "nameEN": "Water Wave Motif" },
    { id: "TSP-LST-NAT-033", nameTH: "ลายก้อนเมฆ (อิทธิพลจีน)", "nameEN": "Cloud Motif (Chinese Influence)" },
    { id: "TSP-LST-NAT-034", nameTH: "ลายเปลวไฟประดิษฐ์", "nameEN": "Stylized Flame Motif" },
    { id: "TSP-LST-NAT-035", nameTH: "ลายใบไม้ร่วง", "nameEN": "Falling Leaves Motif" },
    { id: "TSP-LST-NAT-036", nameTH: "ลายช่อเปลว", "nameEN": "Chor Plew Motif" },
    { id: "TSP-LST-NAT-037", nameTH: "ลายก้านต่อยอด", "nameEN": "Kan Tor Yod Motif" },
    { id: "TSP-LST-NAT-038", nameTH: "ลายพฤกษาล้อมเพชร", "nameEN": "Foliage Enclosing Diamond" },
    { id: "TSP-LST-NAT-039", nameTH: "ลายใบกนกเอียง", "nameEN": "Slanted Kanok Leaf Motif" },
    { id: "TSP-LST-NAT-040", nameTH: "ลายดอกลำดวน", "nameEN": "Lamduan Flower Motif" },
    { id: "TSP-LST-NAT-041", nameTH: "ลายมะลิเลื้อย", "nameEN": "Creeping Jasmine Motif" },
    { id: "TSP-LST-NAT-042", nameTH: "ลายกิ่งไม้ประดิษฐ์", "nameEN": "Stylized Branch Motif" },
    { id: "TSP-LST-NAT-043", nameTH: "ลายดอกรัก", "nameEN": "Crown Flower Motif (Dok Rak)" },
    { id: "TSP-LST-NAT-044", nameTH: "ลายเฟื่องอุบะ (พฤกษา)", "nameEN": "Foliage Festoon (Feuang Uba)" },
    { id: "TSP-LST-NAT-045", nameTH: "ลายดอกสร้อย", "nameEN": "Dok Soi Motif" },
    { id: "TSP-LST-NAT-046", nameTH: "ลายกลีบมะเฟือง", "nameEN": "Starfruit Petal Motif" },
    { id: "TSP-LST-NAT-047", nameTH: "ลายบัวเชิงพื้น", "nameEN": "Lower Border Lotus Motif" },
    { id: "TSP-LST-NAT-048", nameTH: "ลายพุ่มพฤกษา", "nameEN": "Bushy Foliage Motif" },
    { id: "TSP-LST-NAT-049", nameTH: "ลายเครือวัลย์", "nameEN": "Kruea Wan Motif" },
    { id: "TSP-LST-NAT-050", nameTH: "ลายกนกช่อหางโตยอดสะบัด", "nameEN": "Kanok Chor Hang To with Flicked Tip" },

    // 2. Fauna & Mythical (50 items)
    { id: "TSP-LST-FAU-001", nameTH: "ลายปลาสังคโลก", nameEN: "Sangkhalok Fish Motif" },
    { id: "TSP-LST-FAU-002", nameTH: "ลายปลากา (ปลาคู่)", nameEN: "Pa Ka Twin Fish Motif" },
    { id: "TSP-LST-FAU-003", nameTH: "ลายปลาว่ายวน (หมุนเวียน)", nameEN: "Circulating Swirling Fish Motif" },
    { id: "TSP-LST-FAU-004", nameTH: "ลายหงส์", nameEN: "Swan Motif (Hong)" },
    { id: "TSP-LST-FAU-005", nameTH: "ลายหงส์คาบพวงมาลัย", nameEN: "Swan Holding Garland" },
    { id: "TSP-LST-FAU-006", nameTH: "ลายหงส์ประคองฉัตร", nameEN: "Swan Supporting Tiered Umbrella" },
    { id: "TSP-LST-FAU-007", nameTH: "ลายหงส์รำ", nameEN: "Dancing Swan" },
    { id: "TSP-LST-FAU-008", nameTH: "ลายครุฑ", nameEN: "Garuda Motif" },
    { id: "TSP-LST-FAU-009", nameTH: "ลายครุฑยุดนาค", nameEN: "Garuda Grasping Naga" },
    { id: "TSP-LST-FAU-010", nameTH: "ลายนาค", nameEN: "Naga Motif" },
    { id: "TSP-LST-FAU-011", nameTH: "ลายนาคสะดุ้ง", nameEN: "Naga Sadung Motif" },
    { id: "TSP-LST-FAU-012", nameTH: "ลายนาคเกี้ยว", nameEN: "Intertwined Nagas" },
    { id: "TSP-LST-FAU-013", nameTH: "ลายขดหางนาค", nameEN: "Naga Tail Coil Motif" },
    { id: "TSP-LST-FAU-014", nameTH: "ลายสิงห์", nameEN: "Singha Motif" },
    { id: "TSP-LST-FAU-015", nameTH: "ลายราชสีห์", nameEN: "Royal Lion (Rajasingha)" },
    { id: "TSP-LST-FAU-016", nameTH: "ลายคชสีห์", nameEN: "Kojasingha (Elephant Lion)" },
    { id: "TSP-LST-FAU-017", nameTH: "ลายช้าง", nameEN: "Elephant Motif (Chang)" },
    { id: "TSP-LST-FAU-018", nameTH: "ลายช้างเอราวัณ", nameEN: "Erawan Three-headed Elephant" },
    { id: "TSP-LST-FAU-019", nameTH: "ลายกระต่ายชมจันทร์", nameEN: "Rabbit Admiring Moon Motif" },
    { id: "TSP-LST-FAU-020", nameTH: "ลายกวางเหลียวหลัง", nameEN: "Deer Looking Back Motif" },
    { id: "TSP-LST-FAU-021", nameTH: "ลายมยุรา (นกยูง)", nameEN: "Peacock Motif (Mayura)" },
    { id: "TSP-LST-FAU-022", nameTH: "ลายกินนร", nameEN: "Kinnara (Half-bird Half-man)" },
    { id: "TSP-LST-FAU-023", nameTH: "ลายกินรี", nameEN: "Kinnaree (Half-bird Half-woman)" },
    { id: "TSP-LST-FAU-024", nameTH: "ลายเทพนรสิงห์", nameEN: "Thep Norasingha Motif" },
    { id: "TSP-LST-FAU-025", nameTH: "ลายเหมราช", nameEN: "Hemaraj Mythical Creature" },
    { id: "TSP-LST-FAU-026", nameTH: "ลายวารีกุญชร", nameEN: "Waree Kunjorn (Water Elephant)" },
    { id: "TSP-LST-FAU-027", nameTH: "ลายมัจฉานุ", nameEN: "Macchanu Motif" },
    { id: "TSP-LST-FAU-028", nameTH: "ลายสุพรรณมัจฉา", nameEN: "Suphannamacha (Golden Mermaid)" },
    { id: "TSP-LST-FAU-029", nameTH: "ลายมังกรประดิษฐ์ (สังคโลก)", nameEN: "Sangkhalok Dragon Motif" },
    { id: "TSP-LST-FAU-030", nameTH: "ลายกิเลน (อิทธิพลจีน)", nameEN: "Qilin Motif (Chinese Influence)" },

    // 3. Geometric & Synthetic (50 items)
    { id: "TSP-LST-GEO-001", nameTH: "ลายประจำยาม", nameEN: "Prajamyam (Four-petal Flower)" },
    { id: "TSP-LST-GEO-002", nameTH: "ลายประจำยามก้านแย่ง", nameEN: "Prajamyam Kan Yaeng Motif" },
    { id: "TSP-LST-GEO-003", nameTH: "ลายกระจัง", nameEN: "Krajang Motif" },
    { id: "TSP-LST-GEO-004", nameTH: "ลายกระจังตาอ้อย", nameEN: "Krajang Ta Oi (Sugarcane Bud)" },
    { id: "TSP-LST-GEO-005", nameTH: "ลายกระจังรวน", nameEN: "Krajang Ruan Motif" },
    { id: "TSP-LST-GEO-006", nameTH: "ลายกระจังเจิม", nameEN: "Krajang Joem Motif" },
    { id: "TSP-LST-GEO-007", nameTH: "ลายกระจังปฏิญาณ", nameEN: "Krajang Patiyarn Motif" },
    { id: "TSP-LST-GEO-008", nameTH: "ลายฟันปลา", nameEN: "Zigzag / Fish Tooth Motif" },
    { id: "TSP-LST-GEO-009", nameTH: "ลายกรวยเชิง", "nameEN": "Kruai Choeng Border Motif" },
    { id: "TSP-LST-GEO-010", nameTH: "ลายกรวยเชิงพุ่มข้าวบิณฑ์", nameEN: "Kruai Choeng with Phum Khao Bin" },
    { id: "TSP-LST-GEO-011", nameTH: "ลายพุ่มข้าวบิณฑ์", nameEN: "Phum Khao Bin Motif" },
    { id: "TSP-LST-GEO-012", nameTH: "ลายข้าวหลามตัด", nameEN: "Lozenge / Diamond Motif" },
    { id: "TSP-LST-GEO-013", nameTH: "ลายลูกฟัก", nameEN: "Paneling Motif (Luk Fak)" },
    { id: "TSP-LST-GEO-014", nameTH: "ลายแก้วชิงดวง", nameEN: "Overlapping Circles Motif" },
    { id: "TSP-LST-GEO-015", nameTH: "ลายย่อมุมสิบสอง", nameEN: "Twelve-cornered Redented Design" },
    { id: "TSP-LST-GEO-016", nameTH: "ลายแข้งสิงห์", nameEN: "Khaeng Singha Lion Leg Border" },
    { id: "TSP-LST-GEO-017", nameTH: "ลายดาวเพดาน", nameEN: "Ceiling Star Motif" },
    { id: "TSP-LST-GEO-018", nameTH: "ลายดาวล้อมเดือน", nameEN: "Star Surrounding Moon Motif" },

    // 4. Sacred & Belief (30 items)
    { id: "TSP-LST-SAC-001", nameTH: "ลายธรรมจักร", nameEN: "Dharmachakra (Wheel of Dhamma)" },
    { id: "TSP-LST-SAC-002", nameTH: "ลายบัวสามเหล่า", nameEN: "Three Lotus Categories Symbol" },
    { id: "TSP-LST-SAC-003", nameTH: "ลายยันต์ประดิษฐ์", nameEN: "Stylized Sacred Yantra Motif" },
    { id: "TSP-LST-SAC-004", nameTH: "ลายเทวดาพนมมือ", nameEN: "Kneeling Devata in Anjali Mudra" },
    { id: "TSP-LST-SAC-005", nameTH: "ลายเทพพนม", nameEN: "Thepphanom Motif" },
    { id: "TSP-LST-SAC-006", nameTH: "ลายอุณาโลม", nameEN: "Unalome Sacred Symbol" },
    { id: "TSP-LST-SAC-007", nameTH: "ลายฉัตร", nameEN: "Tiered Sacred Umbrella" },
    { id: "TSP-LST-SAC-008", nameTH: "ลายรอยพระพุทธบาท", nameEN: "Buddha's Footprint Outline" },
    { id: "TSP-LST-SAC-009", nameTH: "ลายเจดีย์ทรงพุ่มข้าวบิณฑ์", nameEN: "Lotus Bud Chedi Silhouette" },
    { id: "TSP-LST-SAC-010", nameTH: "ลายจักรวาลคติ", nameEN: "Buddhist Cosmology Map Schematic" }
];

const CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvalU42uqVFSoJ3O-WkoaQCBVmiawl7DHNO-DNsYL3iiWfxKERjiQI4SpiVqDxzEYLPlLFJTqSFCy/pub?gid=494156669&single=true&output=csv&t=' + new Date().getTime();

// State variables
let patternsList = [];
let selectedSubject = "";
let selectedSubjectTH = "";
let selectedStyleName = "";
let selectedStyleKeywords = "";
let selectedEngine = "general";
let customSubject = "";

// Presets options
const ANGLE_PRESETS = [
    { value: "", labelTH: "ปกติ (ไม่ระบุ)", labelEN: "Not specified" },
    { value: "eye-level shot", labelTH: "ระดับสายตา (Eye-level)", labelEN: "Eye-level view" },
    { value: "macro shot, extreme close-up view", labelTH: "ซูมใกล้พิเศษ (Macro/Extreme close-up)", labelEN: "Macro/Close-up" },
    { value: "low angle shot, dramatic look", labelTH: "มุมเงย (Low angle)", labelEN: "Low angle view" },
    { value: "high angle view, bird's-eye view", labelTH: "มุมก้มมุมสูง (Bird's-eye view)", labelEN: "Bird's-eye view" },
    { value: "front symmetrical view", labelTH: "มุมมองสมมาตรตรงหนา (Symmetrical view)", labelEN: "Symmetrical front" }
];

const LIGHTING_PRESETS = [
    { value: "", labelTH: "ปกติ (ไม่ระบุ)", labelEN: "Not specified" },
    { value: "cinematic lighting", labelTH: "แสงภาพยนตร์ (Cinematic)", labelEN: "Cinematic lighting" },
    { value: "golden hour warm light", labelTH: "แสงสีทองอบอุ่น (Golden hour)", labelEN: "Golden hour light" },
    { value: "rim lighting, glowing edge", labelTH: "แสงจับขอบวัตถุเด่น (Rim lighting)", labelEN: "Rim lighting" },
    { value: "flat white lighting, no shadows, no texture", labelTH: "แสงเรียบ ขจัดมิติเงา (Flat B&W for trace)", labelEN: "Flat light (B&W)" },
    { value: "soft diffused lighting", labelTH: "แสงฟุ้งกระจายอ่อนนุ่ม (Soft diffused)", labelEN: "Soft diffused" }
];

const BG_PRESETS = [
    { value: "", labelTH: "ปกติ (ไม่ระบุ)", labelEN: "Not specified" },
    { value: "on a clean solid white background", labelTH: "พื้นหลังสีขาวสะอาด (Solid white)", labelEN: "Solid white" },
    { value: "on a dark atmospheric background with subtle smoke", labelTH: "พื้นหลังมืดสลัวมีควันจางๆ (Dark backdrop)", labelEN: "Dark backdrop" },
    { value: "in a contemporary minimal showroom interior", labelTH: "ห้องจัดแสดงร่วมสมัยแบบมินิมอล (Minimal interior)", labelEN: "Minimal interior" },
    { value: "with golden bokeh patterns", labelTH: "พื้นหลังโบเก้ประกายทอง (Golden bokeh)", labelEN: "Golden bokeh" },
    { value: "integrated seamlessly into a modern architectural wall", labelTH: "ประดับบนผนังอาคารสไตล์โมเดิร์น (Wall integration)", labelEN: "Wall integration" }
];

const COLOR_PRESETS = [
    { value: "", labelTH: "ปกติ (ไม่ระบุ)", labelEN: "Not specified" },
    { value: "monochromatic, pure black and white high contrast", labelTH: "ขาวดำบริสุทธิ์ คอนทราสต์สูง (Pure B&W)", labelEN: "Monochromatic B&W" },
    { value: "royal gold and deep crimson red color palette", labelTH: "สีทองคำพรีเมียมคู่กับแดงเข้ม (Royal Gold & Crimson)", labelEN: "Royal Gold & Crimson" },
    { value: "muted earth tones, copper and bronze accents", labelTH: "โทนสีธรรมชาติ ทองแดง และสัมฤทธิ์ (Earth Tones & Bronze)", labelEN: "Muted Earth Tones" },
    { value: "vibrant neon color scheme, glowing cyan and magenta", labelTH: "นีออนจัดจ้าน ฟ้าครามและชมพูบานเย็น (Neon Cyan & Magenta)", labelEN: "Neon Color Scheme" },
    { value: "antique aged parchment patina, vintage sepia colors", labelTH: "สีสเปียกระดาษเก่าแอนทีค (Vintage Sepia)", labelEN: "Antique Sepia" }
];

// Initialize dynamic pattern database
async function loadPatterns() {
    return new Promise((resolve) => {
        if (typeof Papa === 'undefined') {
            console.warn("PapaParse not loaded, using academic fallback.");
            patternsList = [...ACADEMIC_PATTERNS];
            resolve();
            return;
        }

        Papa.parse(CSV_URL, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: function (results) {
                const sheetRows = results.data;
                const dynamicList = [];
                const seenEN = new Set();

                // 1. Process from Live sheet
                sheetRows.forEach(row => {
                    const id = row['Symbol ID'] || '';
                    let th = row['Title (TH)'] || '';
                    let en = row['Title (EN)'] || '';

                    // Clean symbols
                    id.trim();
                    th = th.replace(/^#/, '').trim();
                    en = en.replace(/^#/, '').trim();

                    if (th && en) {
                        dynamicList.push({ id, nameTH: th, nameEN: en });
                        seenEN.add(en.toLowerCase());
                    }
                });

                // 2. Merge with academic brief fallback to ensure full 180 listing coverage
                ACADEMIC_PATTERNS.forEach(item => {
                    if (!seenEN.has(item.nameEN.toLowerCase())) {
                        dynamicList.push(item);
                        seenEN.add(item.nameEN.toLowerCase());
                    }
                });

                patternsList = dynamicList;
                resolve();
            },
            error: function (err) {
                console.error("Sheet loading failed for Prompt Lab, falling back to academic list:", err);
                patternsList = [...ACADEMIC_PATTERNS];
                resolve();
            }
        });
    });
}

// Generate Prompt based on standard formula
function constructPrompt() {
    // Subject formulation
    let subjectPart = "";
    const selectedSubjElement = document.getElementById("subj-select");
    const customSubjElement = document.getElementById("custom-subj");

    if (customSubjElement && customSubjElement.value.trim() !== "") {
        subjectPart = customSubjElement.value.trim();
    } else if (selectedSubjElement && selectedSubjElement.value !== "") {
        const itemIndex = parseInt(selectedSubjElement.value);
        if (!isNaN(itemIndex) && patternsList[itemIndex]) {
            const item = patternsList[itemIndex];
            subjectPart = `A simplified graphic motif of ${item.nameEN} (Thai ${item.nameTH} pattern)`;
        } else {
            subjectPart = "A beautiful Thai traditional pattern";
        }
    } else {
        subjectPart = "A beautiful Thai traditional pattern";
    }

    // Formula components
    let stylePart = selectedStyleKeywords ? `${selectedStyleKeywords}` : "design graphic";
    
    const angleEl = document.getElementById("angle-select");
    let anglePart = angleEl ? angleEl.value : "";

    const lightingEl = document.getElementById("lighting-select");
    let lightingPart = lightingEl ? lightingEl.value : "";

    const bgEl = document.getElementById("bg-select");
    let bgPart = bgEl ? bgEl.value : "";

    const colorEl = document.getElementById("color-select");
    let colorPart = colorEl ? colorEl.value : "";

    // Special instruction overlay based on "Round 1 B&W Stencil" preset if checked
    const stencilCheck = document.getElementById("stencil-mode");
    const isStencil = stencilCheck ? stencilCheck.checked : false;

    if (isStencil) {
        // Enforce pure black & white, flat shadows, suitable for vector trace
        stylePart = "pure black and white stencil vector logo, clean vector shapes";
        lightingPart = "flat white lighting, no shadows, no texture, no anti-aliasing gray pixels";
        bgPart = "on a clean solid white background";
        colorPart = "monochromatic, pure solid black silhouette on paper white background";
    }

    // Build the array
    const parts = [subjectPart];
    if (stylePart) parts.push(`in ${stylePart} style`);
    if (bgPart) parts.push(bgPart);
    if (lightingPart) parts.push(lightingPart);
    if (anglePart) parts.push(anglePart);
    if (colorPart) parts.push(colorPart);
    
    // Add default high quality anchors unless it's a stencil mode
    if (!isStencil) {
        parts.push("highly detailed, clean shapes");
    }

    let finalPrompt = parts.join(", ");

    // Engine specific formatting suffix
    if (selectedEngine === "midjourney") {
        if (isStencil) {
            finalPrompt += " --style raw --v 6.0 --ar 1:1";
        } else {
            finalPrompt += " --style raw --v 6.0 --ar 4:3";
        }
    } else if (selectedEngine === "stable_diffusion") {
        finalPrompt += " -d 0.8 -n \"low quality, blurry, shadows, gradient, 3d render, photo\"";
    }

    // Display
    const outputEl = document.getElementById("prompt-output-text");
    if (outputEl) {
        outputEl.innerText = finalPrompt;
    }
}

// Populate UI options
function setupUI() {
    // Populate Subjects dropdown
    const subjSelect = document.getElementById("subj-select");
    if (subjSelect) {
        subjSelect.innerHTML = '<option value="">-- เลือกองค์ประกอบลายไทย (Subject) --</option>';
        patternsList.forEach((item, index) => {
            const opt = document.createElement("option");
            opt.value = index;
            opt.innerText = `[${item.id.split('-').pop()}] ${item.nameTH} (${item.nameEN})`;
            subjSelect.appendChild(opt);
        });
    }

    // Populate drop down menus for attributes
    populateDropdown("angle-select", ANGLE_PRESETS);
    populateDropdown("lighting-select", LIGHTING_PRESETS);
    populateDropdown("bg-select", BG_PRESETS);
    populateDropdown("color-select", COLOR_PRESETS);

    // Bind Category / Style list UI
    renderCategories();

    // Bind Events
    bindEventHandlers();

    // Init first compile
    constructPrompt();
}

function populateDropdown(elId, presets) {
    const el = document.getElementById(elId);
    if (el) {
        el.innerHTML = "";
        presets.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.value;
            opt.innerText = `${p.labelTH} (${p.labelEN})`;
            el.appendChild(opt);
        });
    }
}

function renderCategories() {
    const catContainer = document.getElementById("categories-tabs");
    const styleContainer = document.getElementById("styles-grid");

    if (!catContainer || !styleContainer) return;

    catContainer.innerHTML = "";
    styleContainer.innerHTML = "";

    // Generate tabs
    Object.keys(STYLES_DATASET).forEach((key, index) => {
        const cat = STYLES_DATASET[key];
        const tabBtn = document.createElement("button");
        tabBtn.className = `flex items-center gap-2 px-5 py-3 rounded-xl border text-[11px] font-extrabold uppercase tracking-wider transition-all duration-300 ${
            index === 0 
            ? 'bg-[#FF4E45] border-[#FF4E45] text-white shadow-[0_0_15px_rgba(255,78,69,0.3)]' 
            : 'bg-slate-900/60 border-slate-800 text-gray-400 hover:border-slate-700 hover:text-white'
        }`;
        tabBtn.dataset.category = key;
        tabBtn.innerHTML = `<i class="ph-bold ${cat.icon} text-sm"></i> ${cat.titleTH}`;
        
        tabBtn.onclick = () => {
            // Deactivate other tabs
            catContainer.querySelectorAll("button").forEach(b => {
                b.className = b.className.replace('bg-[#FF4E45] border-[#FF4E45] text-white shadow-[0_0_15px_rgba(255,78,69,0.3)]', 'bg-slate-900/60 border-slate-800 text-gray-400 hover:border-slate-700 hover:text-white');
                if (!b.className.includes('bg-slate-900/60')) {
                    b.className += ' bg-slate-900/60 border-slate-800 text-gray-400 hover:border-slate-700 hover:text-white';
                }
            });
            // Activate current
            tabBtn.className = tabBtn.className.replace('bg-slate-900/60 border-slate-800 text-gray-400 hover:border-slate-700 hover:text-white', 'bg-[#FF4E45] border-[#FF4E45] text-white shadow-[0_0_15px_rgba(255,78,69,0.3)]');
            
            // Render styles
            renderStyles(key);
        };

        catContainer.appendChild(tabBtn);
    });

    // Render first category initially
    renderStyles(Object.keys(STYLES_DATASET)[0]);
}

function renderStyles(catKey) {
    const styleContainer = document.getElementById("styles-grid");
    if (!styleContainer) return;

    styleContainer.innerHTML = "";
    const cat = STYLES_DATASET[catKey];

    cat.styles.forEach(s => {
        const styleCard = document.createElement("button");
        styleCard.className = `flex flex-col text-left p-4 rounded-xl border border-slate-800/80 bg-slate-900/40 hover:border-[#FF4E45]/40 hover:bg-slate-900/70 hover:shadow-md transition-all duration-300 ${
            selectedStyleName === s.nameEN ? 'ring-2 ring-[#FF4E45] border-transparent' : ''
        }`;
        
        styleCard.innerHTML = `
            <span class="text-[7px] text-slate-500 font-mono mb-1 font-bold">#${String(s.id).padStart(3, '0')}</span>
            <span class="text-[12px] font-extrabold text-white leading-tight mb-0.5">${s.nameTH}</span>
            <span class="text-[9px] text-[#FF4E45] font-extrabold uppercase tracking-wide leading-none mb-2">${s.nameEN}</span>
            <span class="text-[9px] text-slate-400 leading-normal line-clamp-2">${s.keywords}</span>
        `;

        styleCard.onclick = () => {
            // Remove active outlines
            styleContainer.querySelectorAll("button").forEach(b => {
                b.className = b.className.replace('ring-2 ring-[#FF4E45] border-transparent', '');
            });
            // Add outline
            styleCard.className += ' ring-2 ring-[#FF4E45] border-transparent';
            
            selectedStyleName = s.nameEN;
            selectedStyleKeywords = s.keywords;
            
            // Uncheck stencil if choosing other artistic style
            const stencilCheck = document.getElementById("stencil-mode");
            if (stencilCheck && stencilCheck.checked) {
                stencilCheck.checked = false;
            }

            constructPrompt();
        };

        styleContainer.appendChild(styleCard);
    });
}

function bindEventHandlers() {
    // Dropdowns changes
    const ids = ["subj-select", "angle-select", "lighting-select", "bg-select", "color-select"];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("change", () => {
                // Clear custom subject if dropdown selected
                if (id === "subj-select" && el.value !== "") {
                    const customEl = document.getElementById("custom-subj");
                    if (customEl) customEl.value = "";
                }
                constructPrompt();
            });
        }
    });

    // Custom subject input
    const customSubj = document.getElementById("custom-subj");
    if (customSubj) {
        customSubj.addEventListener("input", () => {
            // Reset dropdown to default if user types
            if (customSubj.value.trim() !== "") {
                const drop = document.getElementById("subj-select");
                if (drop) drop.value = "";
            }
            constructPrompt();
        });
    }

    // Engine buttons selection
    const engineBtns = document.querySelectorAll(".engine-btn");
    engineBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            engineBtns.forEach(b => {
                b.className = b.className.replace('bg-[#0F172A] text-white', 'bg-gray-100 text-gray-700');
            });
            btn.className = btn.className.replace('bg-gray-100 text-gray-700', 'bg-[#0F172A] text-white');
            selectedEngine = btn.dataset.engine;
            constructPrompt();
        });
    });

    // Stencil Mode checkbox
    const stencilMode = document.getElementById("stencil-mode");
    if (stencilMode) {
        stencilMode.addEventListener("change", () => {
            constructPrompt();
        });
    }

    // Copy to clipboard
    const copyBtn = document.getElementById("copy-btn");
    if (copyBtn) {
        copyBtn.addEventListener("click", () => {
            const promptText = document.getElementById("prompt-output-text").innerText;
            navigator.clipboard.writeText(promptText).then(() => {
                const origText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="ph-bold ph-check text-green-500"></i> คัดลอกแล้ว!';
                copyBtn.disabled = true;
                setTimeout(() => {
                    copyBtn.innerHTML = origText;
                    copyBtn.disabled = false;
                }, 2000);
            }).catch(err => {
                console.error("Clipboard copy failed: ", err);
            });
        });
    }
}

// App startup
document.addEventListener("DOMContentLoaded", async () => {
    // Check if we are on prompt generator page
    if (document.getElementById("prompt-output-text")) {
        await loadPatterns();
        setupUI();
    }
});
