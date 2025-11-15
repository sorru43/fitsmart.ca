#!/usr/bin/env python3
"""
Script to check and fix footer display issues
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_footer_css():
    """Check if footer CSS is properly loaded"""
    print("🔍 Checking footer CSS...")
    
    # Check if main.min.css exists
    css_path = "static/css/main.min.css"
    if os.path.exists(css_path):
        file_size = os.path.getsize(css_path)
        print(f"✅ main.min.css exists ({file_size:,} bytes)")
        
        # Check if it contains footer-related CSS
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'hidden' in content and 'md:block' in content:
                print("✅ Footer CSS classes found in main.min.css")
            else:
                print("❌ Footer CSS classes not found in main.min.css")
    else:
        print("❌ main.min.css not found")
    
    # Check if Tailwind CSS is loaded
    print("\n🔍 Checking Tailwind CSS...")
    tailwind_path = "static/css/tailwind/tailwind.min.css"
    if os.path.exists(tailwind_path):
        file_size = os.path.getsize(tailwind_path)
        print(f"✅ tailwind.min.css exists ({file_size:,} bytes)")
    else:
        print("❌ tailwind.min.css not found")

def create_footer_fix():
    """Create a CSS fix for footer display"""
    print("\n🛠️ Creating footer display fix...")
    
    fix_css = """
/* Footer Display Fix */
@media (min-width: 768px) {
    .md\\:block {
        display: block !important;
    }
    
    .hidden.md\\:block {
        display: block !important;
    }
}

/* Ensure footer is visible on desktop */
footer.hidden.md\\:block {
    display: block !important;
}

/* Fallback for footer visibility */
@media (min-width: 768px) {
    footer {
        display: block !important;
    }
}
"""
    
    # Create a footer fix CSS file
    with open("static/css/footer-fix.css", "w") as f:
        f.write(fix_css)
    
    print("✅ Created footer-fix.css")
    
    # Update base.html to include the fix
    base_html_path = "templates/base.html"
    if os.path.exists(base_html_path):
        with open(base_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if footer-fix.css is already included
        if 'footer-fix.css' not in content:
            # Add the CSS link after main.min.css
            content = content.replace(
                '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/main.min.css\') }}?v=20240716">',
                '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/main.min.css\') }}?v=20240716">\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/footer-fix.css\') }}">'
            )
            
            with open(base_html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Added footer-fix.css to base.html")
        else:
            print("✅ footer-fix.css already included in base.html")
    else:
        print("❌ base.html not found")

def test_footer_visibility():
    """Test footer visibility with JavaScript"""
    print("\n🧪 Creating footer visibility test...")
    
    test_js = """
// Footer Visibility Test
document.addEventListener('DOMContentLoaded', function() {
    const footer = document.querySelector('footer');
    if (footer) {
        console.log('Footer element found:', footer);
        console.log('Footer classes:', footer.className);
        console.log('Footer display style:', window.getComputedStyle(footer).display);
        console.log('Footer visibility style:', window.getComputedStyle(footer).visibility);
        
        // Force footer visibility on desktop
        if (window.innerWidth >= 768) {
            footer.style.display = 'block';
            footer.style.visibility = 'visible';
            console.log('Forced footer visibility on desktop');
        }
    } else {
        console.log('Footer element not found');
    }
});
"""
    
    # Create a footer test JavaScript file
    with open("static/js/footer-test.js", "w") as f:
        f.write(test_js)
    
    print("✅ Created footer-test.js")

def main():
    print("🚀 Starting footer display fix...")
    
    check_footer_css()
    create_footer_fix()
    test_footer_visibility()
    
    print("\n✅ Footer display fix completed!")
    print("\n📝 Next steps:")
    print("1. Restart your Flask application")
    print("2. Clear browser cache (Ctrl+F5)")
    print("3. Check if footer appears on desktop")
    print("4. Open browser console to see footer test results")

if __name__ == "__main__":
    main() 