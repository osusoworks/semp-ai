from PIL import Image, ImageDraw
import os
import math

def create_gear_icon(filename, color):
    size = (64, 64)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size[0] // 2, size[1] // 2
    outer_radius = 28
    inner_radius = 20
    hole_radius = 10
    num_teeth = 8
    
    # Draw teeth
    for i in range(num_teeth):
        angle = (2 * math.pi / num_teeth) * i
        tooth_w = 2 * math.pi / num_teeth * 0.5
        
        # Simple rectangular teeth protruding from inner radius to outer radius
        # But let's verify visual. 
        # Easier: Draw a thick circle for the main body/rim
        pass

    # Better approach for gear: 
    # Draw a circle for the rim
    # Draw rectangles for teeth rotated around center
    
    # Teeth
    tooth_len = 8
    tooth_width = 12
    
    for i in range(num_teeth):
        angle_deg = (360 / num_teeth) * i
        
        # Create a rectangle centered at (cx, cy) then rotate? 
        # PIL doesn't rotate primitives easily.
        # Calculate points.
        
        angle_rad = math.radians(angle_deg)
        dist = 24 # distance from center to tooth center
        
        # Tooth corners
        dx = math.cos(angle_rad) * dist
        dy = math.sin(angle_rad) * dist
        
        # Need to define a polygon for the tooth
        # Perpendicular vector for width
        p_dx = -math.sin(angle_rad) * (tooth_width/2)
        p_dy = math.cos(angle_rad) * (tooth_width/2)
        
        # Tooth outer edge center
        out_x = cx + math.cos(angle_rad) * (dist + tooth_len/2)
        out_y = cy + math.sin(angle_rad) * (dist + tooth_len/2)
        
        # Tooth inner base center
        in_x = cx + math.cos(angle_rad) * (dist - tooth_len/2)
        in_y = cy + math.sin(angle_rad) * (dist - tooth_len/2)
        
        # 4 points
        p1 = (out_x + p_dx, out_y + p_dy)
        p2 = (out_x - p_dx, out_y - p_dy)
        p3 = (in_x - p_dx, in_y - p_dy)
        p4 = (in_x + p_dx, in_y + p_dy)
        
        draw.polygon([p1, p2, p3, p4], fill=color)

    # Main ring
    rim_bbox = [cx - 22, cy - 22, cx + 22, cy + 22]
    draw.ellipse(rim_bbox, fill=color) # Outline is messy if filled separately, just fill it

    # Center hole (clear)
    hole_bbox = [cx - 12, cy - 12, cx + 12, cy + 12]
    draw.ellipse(hole_bbox, fill=(0,0,0,0), outline=None) # Erase center

    os.makedirs('assets', exist_ok=True)
    img.save(os.path.join('assets', filename))
    print(f"Created {filename}")

create_gear_icon('gear_icon_white.png', (255, 255, 255, 255))
