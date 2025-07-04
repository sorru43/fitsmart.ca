from PIL import Image, ImageDraw, ImageFont
import os

def create_default_avatar():
    # Create a 200x200 image with a light gray background
    img = Image.new('RGB', (200, 200), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    draw.ellipse([20, 20, 180, 180], fill='#e0e0e0')
    
    # Draw a person silhouette
    draw.ellipse([70, 50, 130, 110], fill='#808080')  # Head
    draw.rectangle([85, 110, 115, 160], fill='#808080')  # Body
    
    # Save the image
    os.makedirs('static/images', exist_ok=True)
    img.save('static/images/default-avatar.png')

def create_default_meal_plan():
    # Create a 400x300 image with a light gray background
    img = Image.new('RGB', (400, 300), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw a plate
    draw.ellipse([100, 50, 300, 250], fill='#e0e0e0')
    
    # Draw some food items
    draw.ellipse([150, 100, 250, 200], fill='#a0a0a0')  # Main dish
    draw.ellipse([120, 150, 180, 210], fill='#808080')  # Side dish
    draw.ellipse([220, 150, 280, 210], fill='#808080')  # Side dish
    
    # Save the image
    os.makedirs('static/images', exist_ok=True)
    img.save('static/images/default-meal-plan.png')

if __name__ == '__main__':
    create_default_avatar()
    create_default_meal_plan()
    print("Default images generated successfully!") 