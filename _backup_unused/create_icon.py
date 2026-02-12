from PIL import Image, ImageDraw
import os

def create_mic_icon(filename, color):
    # Canvas size
    size = (64, 64)
    # Create transparent image
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Settings
    stroke_width = 4
    # Center x
    cx = size[0] // 2
    
    # Mic body (capsule)
    body_w = 16
    body_h = 24
    body_top = 8
    body_rect = [cx - body_w//2, body_top, cx + body_w//2, body_top + body_h]
    
    # Draw body (filled or outlined? User wanted "like that image", which was an outline)
    # Let's do outline with rounded corners
    # Simplified: Draw a thick line with rounded ends, or a rounded rectangle
    draw.rounded_rectangle(body_rect, radius=body_w//2, outline=color, width=stroke_width)
    
    # Mic stand (U-shape)
    u_w = 28
    u_h = 16
    u_top = body_top + body_h - 10 # Overlap slightly or start where body ends?
    # Actually the U shape starts around the middle/bottom of the mic
    
    # Let's draw an arc
    # Bounding box for the arc
    arc_box = [cx - u_w//2, body_rect[1] + 10, cx + u_w//2, body_rect[3] + 8]
    draw.arc(arc_box, start=0, end=180, fill=color, width=stroke_width)
    
    # Vertical stem
    stem_h = 8
    stem_top = arc_box[3] 
    draw.line([cx, stem_top, cx, stem_top + stem_h], fill=color, width=stroke_width)
    
    # Base
    base_w = 20
    base_y = stem_top + stem_h
    draw.line([cx - base_w//2, base_y, cx + base_w//2, base_y], fill=color, width=stroke_width)
    
    # Ensure assets dir exists
    os.makedirs('assets', exist_ok=True)
    img.save(os.path.join('assets', filename))
    print(f"Created {filename}")

# Create white icon (for dark button)
create_mic_icon('mic_icon_white.png', (255, 255, 255, 255))
