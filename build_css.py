#!/usr/bin/env python3
"""
CSS Bundler for HealthyRizz
Bundles and minifies all CSS files into a single main.min.css
"""

import os
import re
import glob
from pathlib import Path

def minify_css(css_content):
    """Basic CSS minification"""
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Remove extra whitespace
    css_content = re.sub(r'\s+', ' ', css_content)
    
    # Remove whitespace around certain characters
    css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
    
    # Remove trailing semicolons before closing braces
    css_content = re.sub(r';+}', '}', css_content)
    
    # Remove leading/trailing whitespace
    css_content = css_content.strip()
    
    return css_content

def bundle_css():
    """Bundle all CSS files into main.min.css"""
    
    # Define the order of CSS files to bundle
    css_files = [
        'static/fonts/fonts.css',
        'static/css/tailwind/tailwind.min.css',
        'static/css/critical.css',
        'static/css/style.css',
        'static/css/animations.css',
        'static/css/dark-theme.css',
        'static/css/light-theme.css',
        'static/css/meal-plans.css',
        'static/css/subscriptions.css',
        'static/css/mobile-app-menu.css',
        'static/css/mobile-responsive.css',
        'static/css/mobile.css',
    ]
    
    bundled_css = []
    
    print("🔄 Bundling CSS files...")
    
    for css_file in css_files:
        if os.path.exists(css_file):
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    bundled_css.append(f"/* {css_file} */")
                    bundled_css.append(content)
                print(f"✅ Added: {css_file}")
            except Exception as e:
                print(f"❌ Error reading {css_file}: {e}")
        else:
            print(f"⚠️  File not found: {css_file}")
    
    # Combine all CSS
    combined_css = '\n\n'.join(bundled_css)
    
    # Minify the combined CSS
    print("🔧 Minifying CSS...")
    minified_css = minify_css(combined_css)
    
    # Write the bundled and minified CSS
    output_file = 'static/css/main.min.css'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(minified_css)
        
        # Get file size
        file_size = os.path.getsize(output_file)
        print(f"✅ Successfully created: {output_file}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error writing {output_file}: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 HealthyRizz CSS Bundler")
    print("=" * 40)
    
    if bundle_css():
        print("\n🎉 CSS bundling completed successfully!")
        print("💡 Don't forget to restart your Flask service:")
        print("   sudo systemctl restart healthyrizz")
    else:
        print("\n❌ CSS bundling failed!")
        exit(1) 