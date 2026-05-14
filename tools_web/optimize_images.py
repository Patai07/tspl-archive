import os
from PIL import Image, ImageFilter

ASSETS_DIR = 'assets/images/database'
TARGET_RATIO = 4 / 3
TARGET_WIDTH = 1200
TARGET_HEIGHT = int(TARGET_WIDTH / TARGET_RATIO) # 900

def process_image(path):
    try:
        img = Image.open(path)
        # Convert to RGB if it's RGBA or P
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        orig_w, orig_h = img.size
        orig_ratio = orig_w / orig_h
        
        # If it's too big or wrong ratio
        needs_resize = orig_w > TARGET_WIDTH or orig_h > TARGET_HEIGHT
        # We consider ratio "wrong" if it's off by more than 5%
        needs_ratio_fix = abs(orig_ratio - TARGET_RATIO) > 0.05
        
        if not needs_resize and not needs_ratio_fix and os.path.getsize(path) < 500000:
            if path.lower().endswith('.png') and img.format == 'JPEG':
                print(f"⚠️ [Format Mismatch] Repairing PNG container for {path}")
            else:
                print(f"✅ [Already Optimized] {path} ({os.path.getsize(path)/1024:.1f}KB)")
                return False # already optimized enough
            
        print(f"Processing {path} (Size: {os.path.getsize(path)/1024/1024:.2f}MB, {orig_w}x{orig_h})")
        
        if needs_ratio_fix:
            # Create a 4:3 canvas
            new_img = Image.new('RGB', (TARGET_WIDTH, TARGET_HEIGHT), (10, 10, 10))
            
            # Resize image to fit inside 4:3
            if orig_ratio > TARGET_RATIO:
                # Wider than 4:3 -> fit width
                new_w = TARGET_WIDTH
                new_h = int(new_w / orig_ratio)
            else:
                # Taller than 4:3 -> fit height
                new_h = TARGET_HEIGHT
                new_w = int(new_h * orig_ratio)
                
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Optional: Blurred background
            # Resize original to fill the canvas to use as blurred background
            bg_w = TARGET_WIDTH
            bg_h = int(bg_w / orig_ratio)
            if bg_h < TARGET_HEIGHT:
                bg_h = TARGET_HEIGHT
                bg_w = int(bg_h * orig_ratio)
            bg_img = img.resize((bg_w, bg_h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(20))
            # crop to target
            left = (bg_w - TARGET_WIDTH)/2
            top = (bg_h - TARGET_HEIGHT)/2
            bg_img = bg_img.crop((left, top, left+TARGET_WIDTH, top+TARGET_HEIGHT))
            
            new_img.paste(bg_img, (0,0))
            
            # Paste the original inside
            offset_x = (TARGET_WIDTH - new_w) // 2
            offset_y = (TARGET_HEIGHT - new_h) // 2
            new_img.paste(img_resized, (offset_x, offset_y))
            img = new_img
        else:
            # Just resize
            img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            
        # Save compressed
        if path.lower().endswith('.png'):
            img.save(path, 'PNG', optimize=True)
        else:
            img.save(path, 'JPEG', quality=80, optimize=True)
        print(f" -> Optimized to {os.path.getsize(path)/1024:.2f}KB")
        return True
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def main():
    if not os.path.exists(ASSETS_DIR):
        print(f"Directory {ASSETS_DIR} not found.")
        return
        
    count = 0
    for root, dirs, files in os.walk(ASSETS_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(root, file)
                if process_image(path):
                    count += 1
    print(f"Optimized {count} images.")

if __name__ == '__main__':
    main()
