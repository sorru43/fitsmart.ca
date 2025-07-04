#!/usr/bin/env python3
"""
Create placeholder PNG files for PWA icons
This script creates simple colored boxes as placeholder icons in different sizes
"""
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_placeholder_icons():
    """Create placeholder PNG files for PWA icons"""
    print("Creating placeholder PWA icons...")
    
    # Define icon sizes needed for PWA
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # New branding colors
    background_color = (0, 0, 0)  # Black background
    spoon_color = (55, 151, 119)  # #379777 - Green spoon color
    circle_color = (255, 255, 255)  # White circle
    
    # Ensure output directory exists
    output_dir = Path("static/icons")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate icons
    for size in icon_sizes:
        output_path = output_dir / f"icon-{size}x{size}.png"
        print(f"Creating {output_path}...")
        
        # Create a new image with black background
        img = Image.new('RGBA', (size, size), background_color)
        draw = ImageDraw.Draw(img)
        
        # Create a white circle at the center (70% of icon size)
        circle_size = int(size * 0.7)
        circle_pos = (size - circle_size) // 2
        draw.ellipse(
            (circle_pos, circle_pos, 
             circle_pos + circle_size, circle_pos + circle_size), 
            fill=circle_color
        )
        
        # Draw a green spoon symbol in the center
        spoon_width = int(size * 0.25)
        spoon_height = int(size * 0.5)
        spoon_x = (size - spoon_width) // 2
        spoon_y = (size - spoon_height) // 2
        
        # Spoon head (circle)
        draw.ellipse(
            (spoon_x, spoon_y, 
             spoon_x + spoon_width, spoon_y + spoon_width), 
            fill=spoon_color
        )
        
        # Spoon handle (rectangle)
        draw.rectangle(
            (spoon_x + spoon_width//3, spoon_y + spoon_width, 
             spoon_x + 2*spoon_width//3, spoon_y + spoon_height), 
            fill=spoon_color
        )
        
        # Save the icon
        img.save(output_path)
        print(f"✅ Created placeholder icon {size}x{size}")
    
    # Also create a simple favicon.ico
    favicon_path = Path("static/favicon.ico")
    favicon_png_path = Path("static/favicon.png")
    favicon_sizes = [16, 32, 48]
    favicon_images = []
    
    for size in favicon_sizes:
        img = Image.new('RGBA', (size, size), background_color)
        draw = ImageDraw.Draw(img)
        
        # For very small icons, make a simpler version
        if size < 32:
            # Simple green square with white border
            draw.rectangle(
                (0, 0, size, size),
                fill=spoon_color
            )
            if size >= 16:
                border_width = max(1, int(size * 0.1))
                draw.rectangle(
                    (border_width, border_width,
                     size - border_width, size - border_width),
                    outline=circle_color,
                    width=1
                )
        else:
            # Create a white circle
            circle_size = int(size * 0.7)
            circle_pos = (size - circle_size) // 2
            draw.ellipse(
                (circle_pos, circle_pos, 
                 circle_pos + circle_size, circle_pos + circle_size), 
                fill=circle_color
            )
            
            # Draw a simple green spoon
            spoon_width = int(size * 0.25)
            spoon_height = int(size * 0.5)
            spoon_x = (size - spoon_width) // 2
            spoon_y = (size - spoon_height) // 2
            
            # Spoon head (circle)
            draw.ellipse(
                [(spoon_x, spoon_y), 
                 (spoon_x + spoon_width, spoon_y + spoon_width)], 
                fill=spoon_color
            )
            
            # Spoon handle (rectangle)
            draw.rectangle(
                (spoon_x + spoon_width//3, spoon_y + spoon_width, 
                 spoon_x + 2*spoon_width//3, spoon_y + spoon_height), 
                fill=spoon_color
            )
        
        favicon_images.append(img)
    
    # Save a larger PNG version as favicon.png
    favicon_png_size = 64
    img = Image.new('RGBA', (favicon_png_size, favicon_png_size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Create a white circle
    circle_size = int(favicon_png_size * 0.7)
    circle_pos = (favicon_png_size - circle_size) // 2
    draw.ellipse(
        [(circle_pos, circle_pos), 
         (circle_pos + circle_size, circle_pos + circle_size)], 
        fill=circle_color
    )
    
    # Draw a green spoon
    spoon_width = int(favicon_png_size * 0.25)
    spoon_height = int(favicon_png_size * 0.5)
    spoon_x = (favicon_png_size - spoon_width) // 2
    spoon_y = (favicon_png_size - spoon_height) // 2
    
    # Spoon head (circle)
    draw.ellipse(
        [(spoon_x, spoon_y), 
         (spoon_x + spoon_width, spoon_y + spoon_width)], 
        fill=spoon_color
    )
    
    # Spoon handle (rectangle)
    draw.rectangle(
        (spoon_x + spoon_width//3, spoon_y + spoon_width, 
         spoon_x + 2*spoon_width//3, spoon_y + spoon_height), 
        fill=spoon_color
    )
    
    # Save as PNG
    img.save(favicon_png_path)
    print(f"✅ Created favicon.png ({favicon_png_size}x{favicon_png_size})")
    
    # Add the larger favicon to the ico images
    favicon_images.append(img)
    
    # Save multi-size favicon
    favicon_images[0].save(
        favicon_path,
        format='ICO',
        sizes=[(size, size) for size in favicon_sizes],
        append_images=favicon_images[1:]
    )
    print(f"✅ Created favicon.ico")
    
    print("Placeholder icon creation complete!")
    return True

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
        create_placeholder_icons()
    except ImportError:
        print("Error: Pillow library not installed. Please install it with:")
        print("pip install pillow")