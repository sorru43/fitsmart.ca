#!/usr/bin/env python3
"""
Script to test if banner is being displayed on the website
"""
import requests
from bs4 import BeautifulSoup

def test_banner_display():
    print("🧪 Testing banner display on website...")
    
    try:
        # Get the homepage
        response = requests.get('http://localhost:5000')
        
        if response.status_code == 200:
            print("✅ Website is accessible")
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the promo banner
            promo_banner = soup.find('div', id='promo-banner')
            
            if promo_banner:
                print("✅ Promotional banner found on website!")
                print(f"   Banner content: {promo_banner.get_text(strip=True)}")
                
                # Check for banner styling
                banner_classes = promo_banner.get('class', [])
                if 'promo-banner' in banner_classes:
                    print("✅ Banner has correct CSS class")
                
                # Check for close button
                close_button = promo_banner.find('button', id='close-banner')
                if close_button:
                    print("✅ Banner has close button")
                
                # Check for link
                banner_link = promo_banner.find('a')
                if banner_link:
                    print(f"✅ Banner has link: {banner_link.get_text(strip=True)}")
                    print(f"   Link URL: {banner_link.get('href')}")
                else:
                    print("ℹ️  Banner has no link")
                
            else:
                print("❌ No promotional banner found on website")
                print("   This could mean:")
                print("   1. No active banner in database")
                print("   2. Banner is not active")
                print("   3. Banner dates are not valid")
                print("   4. Context processor is not working")
                
                # Check if there's any banner-related HTML
                banner_related = soup.find_all(text=lambda text: text and 'banner' in text.lower())
                if banner_related:
                    print(f"   Found banner-related text: {banner_related}")
                
        else:
            print(f"❌ Website returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to website. Make sure Flask app is running.")
    except Exception as e:
        print(f"❌ Error testing banner display: {e}")

if __name__ == "__main__":
    test_banner_display() 