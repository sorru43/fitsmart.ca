#!/usr/bin/env python3
"""
Test VPS Template Fix
"""
from app import create_app

def test_template_rendering():
    """Test if templates render without errors"""
    try:
        app = create_app()
        with app.app_context():
            # Test basic template rendering
            from flask import render_template_string
            
            # Test simple template
            template = "{{ csrf_token() if csrf_token else 'no-csrf' }}"
            result = render_template_string(template)
            print(f"✅ Template test passed: {result}")
            return True
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_template_rendering()
    exit(0 if success else 1)
