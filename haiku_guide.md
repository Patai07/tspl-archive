# 🤖 คู่มือการใช้งาน Claude Haiku (`claude-haiku-4-5-20251001`) สำหรับนักพัฒนา
คู่มือฉบับนี้สรุปวิธีการรวมระบบ (Integration) ของโมเดล **Claude Haiku** ล่าสุด ทั้งในแง่ของ **Text Extraction** (การดึงข้อมูลเชิงโครงสร้างจากเอกสาร) และ **Vision Classifier** (การวิเคราะห์ภาพถ่าย/ลวดลาย) พร้อมเทคนิคการเขียนโค้ดให้เสถียร ประหยัดทิป (Token) และปลอดภัยสำหรับการนำไปประยุกต์ใช้ในโปรเจกต์อื่นๆ

---

## 📌 สารบัญ (Table of Contents)
1. [การตั้งค่าเริ่มต้น (Setup & Installation)](#1-การตั้งค่าเริ่มต้น-setup--installation)
2. [การดึงข้อมูลตัวอักษรแบบมีโครงสร้าง (JSON Text Extraction)](#2-การดึงข้อมูลตัวอักษรแบบมีโครงสร้าง-json-text-extraction)
3. [การวิเคราะห์รูปภาพความเร็วสูง (Haiku Vision Classifier)](#3-การวิเคราะห์รูปภาพความเร็วสูง-haiku-vision-classifier)
4. [การรับมือข้อผิดพลาดและ Rate Limits (Robust Exception Handling & Retries)](#4-การรับมือข้อผิดพลาดและ-rate-limits-robust-exception-handling--retries)
5. [ข้อแนะนำในการเพิ่มประสิทธิภาพและความประหยัด (Best Practices & Cost Savings)](#5-ข้อแนะนำในการเพิ่มประสิทธิภาพและความประหยัด-best-practices--cost-savings)

---

## 1. การตั้งค่าเริ่มต้น (Setup & Installation)

ติดตั้ง Library ที่จำเป็นผ่าน pip:
```bash
pip install anthropic pillow
```

### การตั้งค่า Environment Variables หรือ Config
ควรกำหนด API Key ไว้ใน `config.json` หรือ `.env` เพื่อไม่ให้คีย์หลุดไปใน git:

```json
{
  "ANTHROPIC_API_KEY": "your-api-key-here"
}
```

ในโค้ด Python:
```python
import json
import anthropic

# โหลด API Key
with open('config.json', 'r') as f:
    config = json.load(f)

ANTHROPIC_API_KEY = config.get('ANTHROPIC_API_KEY')
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# สร้าง Client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
```

---

## 2. การดึงข้อมูลตัวอักษรแบบมีโครงสร้าง (JSON Text Extraction)

ในการดึงข้อมูลจากเอกสารประเภท `.txt`, `.docx` หรือ `.pdf` ให้กลายเป็น **JSON** ที่มีรูปแบบแน่นอน เพื่อให้ระบบหลังบ้านนำไปใช้งานต่อได้ง่าย มี 3 เทคนิคสำคัญคือ:
1. **การบังคับ JSON ใน Prompt:** สั่งอย่างชัดเจนว่าต้องการตอบเป็น JSON เท่านั้น
2. **การทำ JSON Clean-up:** ใช้ Regular Expression ในการตัดช่องว่างหรือ Markdown tags (เช่น \`\`\`json ... \`\`\`) ที่ Claude มักจะใส่แถมมา
3. **Fallback Mechanism:** กำหนดพฤติกรรมในกรณีกรองแล้วข้อมูลไม่สมบูรณ์

### ตัวอย่าง Code ฟังก์ชันสกัดข้อมูล:
```python
import re
import json
import anthropic

def clean_json(text: str) -> str:
    """กรองเอาเฉพาะเนื้อหาที่อยู่ภายในเครื่องหมายปีกกา { ... }"""
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

def extract_structured_data(content: str, filename: str) -> dict:
    """สกัดข้อมูลจากเนื้อหาเอกสารให้เป็นโครงสร้างตามที่กำหนด"""
    prompt = (
        f"คุณคือผู้เชี่ยวชาญด้านสัญศาสตร์และฐานข้อมูล "
        f"วิเคราะห์เนื้อหาจากเอกสารชื่อ '{filename}' แล้วสกัดข้อมูลออกมาเป็น JSON Object ดังนี้:\n\n"
        "- category: เลือกหนึ่งในหมวดหมู่เหล่านี้ [Nature, Fauna, Geometric, Sacred]\n"
        "- title_th: ชื่อหัวข้อภาษาไทย\n"
        "- title_en: ชื่อหัวข้อภาษาอังกฤษ\n"
        "- connotation_th: สรุปความหมายเชิงวัฒนธรรม 2-3 ประโยค\n"
        "- tags: คำค้นหา 5-8 คำ คั่นด้วยเครื่องหมายจุลภาค (,)\n\n"
        "🚨 สำคัญมาก: ตอบเป็น JSON object เท่านั้น ห้ามใส่ข้อความอธิบายใดๆ นอกเหนือจาก JSON\n\n"
        "เนื้อหาเอกสาร:\n" + content[:3000]  # ป้องกันเนื้อหายาวเกินไป
    )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # กรองและแปลงเป็น Dictionary
        json_text = clean_json(message.content[0].text)
        return json.loads(json_text)
    except Exception as e:
        print(f"❌ Extraction Error: {e}")
        return None
```

---

## 3. การวิเคราะห์รูปภาพความเร็วสูง (Haiku Vision Classifier)

Claude 4.5 Haiku รองรับโมเดลสายตา (Multimodal Vision) ซึ่งทำงานได้เร็วมาก เหมาะสำหรับงานจัดหมวดหมู่ภาพ การใส่แท็กอัตโนมัติ หรือตรวจสอบคุณภาพ

### 🚨 เทคนิคประหยัดเงิน: Image Preprocessing (การย่อรูป)
ก่อนส่งรูปเข้า API ของ Claude เราควรย่อขนาดรูปภาพให้อยู่ในระดับพอเหมาะ (เช่น ไม่เกิน **800px** ในด้านที่ยาวที่สุด) เพื่อ:
* **ลดขนาดไฟล์ Base64** ทำให้ส่งข้อมูลได้ไวขึ้น
* **ประหยัดค่า Token** ของ Input Image เนื่องจากรูปขนาดใหญ่จะถูกคิดราคา Token เพิ่มขึ้นตามพิกเซล

### ตัวอย่าง Code ฟังก์ชันย่อรูปและส่งให้ Haiku Vision:
```python
import base64
import io
from PIL import Image
import anthropic

MAX_IMAGE_PX = 800

def resize_image_bytes(data: bytes, max_px=MAX_IMAGE_PX) -> bytes:
    """Resize ภาพให้ไม่เกิน max_px บน longest side เพื่อประหยัด Token"""
    try:
        img = Image.open(io.BytesIO(data))
        img.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        # แปลงฟอร์แมตให้เป็นมาตรฐาน JPEG
        fmt = img.format if img.format in ('JPEG', 'PNG', 'GIF', 'WEBP') else 'JPEG'
        img.save(buf, format=fmt)
        return buf.getvalue()
    except Exception as e:
        print(f"⚠️ Resize ล้มเหลว ส่งรูปเดิม: {e}")
        return data

def classify_image(image_bytes: bytes, filename: str) -> dict:
    """ส่งภาพให้ Claude Haiku วิเคราะห์"""
    # 1. ย่อภาพก่อน
    optimized_bytes = resize_image_bytes(image_bytes)
    
    # 2. แปลงเป็น Base64
    data_b64 = base64.standard_b64encode(optimized_bytes).decode('utf-8')
    
    # 3. กำหนด MIME Type
    ext = filename.lower().rsplit('.', 1)[-1]
    media_type = {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png', 'gif': 'image/gif',
        'webp': 'image/webp'
    }.get(ext, 'image/jpeg')

    prompt = (
        "รูปภาพนี้คือภาพอะไร? โปรดระบุหมวดหมู่ที่เหมาะสมที่สุด และความมั่นใจของคุณ\n"
        "ตอบเป็น JSON Object เท่านั้น:\n"
        '{"guess": "ชื่อสิ่งที่เห็น", "category": "หมวดหมู่", "confidence": "high/medium/low"}'
    )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": data_b64,
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )
        
        # ถอดค่า JSON
        clean_text = clean_json(msg.content[0].text.strip())
        return json.loads(clean_text)
    except Exception as e:
        print(f"❌ Vision Error: {e}")
        return {"guess": "ERROR", "category": "Unknown", "confidence": "low"}
```

---

## 4. การรับมือข้อผิดพลาดและ Rate Limits (Robust Exception Handling & Retries)

ในระดับ Production การเจอ `RateLimitError` เป็นเรื่องปกติเนื่องจากมีลิมิตจำนวน Request ต่อนาที (RPM) หรือ Token ต่อนาที (TPM) เราควรสร้างกลไก **Retry แบบถอยหลังทวีคูณ (Exponential Backoff)**:

```python
import time
import anthropic

def safe_api_call(prompt: str, retries=3, initial_delay=30):
    """ส่งคำสั่งไปยัง Claude แบบมีระบบ Retry อัตโนมัติเมื่อเจอ Rate Limit"""
    delay = initial_delay
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for attempt in range(retries):
        try:
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except anthropic.RateLimitError:
            print(f"⚠️ Rate limit hit! พักเครื่อง {delay} วินาที (ครั้งที่ {attempt+1}/{retries})...")
            time.sleep(delay)
            delay *= 2  # ทวีคูณเวลารอขึ้นเป็นเท่าตัว
        except anthropic.AuthenticationError:
            print("❌ คีย์ API ผิดพลาด กรุณาตรวจสอบ!")
            break
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดร้ายแรง: {e}")
            break
            
    print("❌ เกินจำนวนครั้งที่กำหนด (Retry limit exceeded) ข้ามงานนี้")
    return None
```

---

## 5. ข้อแนะนำในการเพิ่มประสิทธิภาพและความประหยัด (Best Practices & Cost Savings)

| ข้อแนะนำ | วิธีปฏิบัติ | ประโยชน์ที่ได้รับ |
| :--- | :--- | :--- |
| **1. ย่อภาพทุกครั้งก่อนส่ง** | คุมกว้างยาวรูปภาพไม่ให้เกิน 800px ถึง 1000px | ประหยัดค่า Token Vision และส่งเสร็จไวกว่าเดิม 3-5 เท่า |
| **2. หุ้ม Prompt ด้วยตัวแปรคุมยาว** | ใช้ฟังก์ชันตัดคำเช่น `content[:3000]` ก่อนเข้า API | ป้องกันปัญหาลืมตัดเอกสารยาวแล้วทำให้โควต้า Token หมดไว |
| **3. ใส่คำว่า "ตอบเป็น JSON เท่านั้น"** | กำหนดโครงสร้างตัวอย่างและย้ำใน Prompt เสมอ | ป้องกันโมเดลเกริ่นนำ หรือเขียนอธิบายที่ทำให้ JSON พัง |
| **4. ใช้หน่วงเวลาที่พอดี** | ใส่คำสั่ง `time.sleep(1.0)` หรือ `time.sleep(2.0)` ทุกรอบลูป | ป้องกันการถูกระงับ API ชั่วคราว (Rate Limit) เมื่อทำงานแบบ Batch |
| **5. คัดกรองข้อมูลที่ไม่เข้าพวก** | วางเงื่อนไขคำตอบเช่น `'IRRELEVANT'` เพื่อให้สคริปต์กรองทิ้งอัตโนมัติ | ลดการบันทึกข้อมูลขยะหรือข้อมูลที่ผิดพลาดลงฐานข้อมูลหลัก |

---
*จัดทำเพื่ออ้างอิงเป็นโมเดลการพัฒนาในโปรเจกต์ถัดไปสำหรับระบบงานอัตโนมัติด้วย AI*
