#!/usr/bin/env python3
"""
Generate PWA icons in different sizes from an SVG source
"""
import os
import subprocess
from pathlib import Path

def generate_icons():
    """Generate PWA icons for the HealthyRizz application"""
    print("Generating PWA icons...")
    
    # Define icon sizes needed for PWA
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # Source SVG
    svg_path = Path("static/icons/healthyrizz-logo.svg")
    if not svg_path.exists():
        print(f"Error: Source SVG not found at {svg_path}")
        return False
    
    # Check for Inkscape or ImageMagick
    has_inkscape = subprocess.run(['which', 'inkscape'], capture_output=True).returncode == 0
    has_imagemagick = subprocess.run(['which', 'convert'], capture_output=True).returncode == 0
    
    if not (has_inkscape or has_imagemagick):
        print("Error: Neither Inkscape nor ImageMagick found. Cannot convert SVG to PNG.")
        print("Please install one of these tools:")
        print("  - sudo apt-get install inkscape")
        print("  - sudo apt-get install imagemagick")
        return False
    
    # Ensure output directory exists
    output_dir = Path("static/icons")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate icons
    for size in icon_sizes:
        output_path = output_dir / f"icon-{size}x{size}.png"
        print(f"Generating {output_path}...")
        
        if has_inkscape:
            # Use Inkscape for conversion
            cmd = [
                'inkscape',
                '--export-filename', str(output_path),
                '--export-width', str(size),
                '--export-height', str(size),
                str(svg_path)
            ]
        else:
            # Use ImageMagick for conversion
            cmd = [
                'convert',
                '-background', 'none',
                '-resize', f"{size}x{size}",
                str(svg_path),
                str(output_path)
            ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            print(f"Error generating icon size {size}x{size}:")
            print(result.stderr.decode())
        else:
            print(f"✅ Generated icon size {size}x{size}")
    
    # Also generate a favicon.ico
    if has_imagemagick:
        favicon_path = Path("static/favicon.ico")
        print(f"Generating {favicon_path}...")
        
        cmd = [
            'convert',
            '-background', 'none',
            '-define', 'icon:auto-resize=16,32,48',
            str(svg_path),
            str(favicon_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            print(f"Error generating favicon.ico:")
            print(result.stderr.decode())
        else:
            print(f"✅ Generated favicon.ico")
    
    print("Icon generation complete!")
    return True

if __name__ == "__main__":
    generate_icons()
