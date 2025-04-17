#!/usr/bin/env python3
"""
Create a professional Python developer-themed welcome image for the quiz application.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import numpy as np
import random

def create_python_quiz_image(output_path, width=800, height=600):
    """Create a professional Python developer-themed welcome image."""
    # Create a base image with a dark purple gradient background
    image = Image.new('RGB', (width, height), (45, 30, 64))  # Dark purple
    draw = ImageDraw.Draw(image)
    
    # Create a gradient background
    for y in range(height):
        r = int(45 + (y / height) * 30)
        g = int(30 + (y / height) * 20)
        b = int(64 + (y / height) * 30)
        for x in range(width):
            draw.point((x, y), fill=(r, g, b))
    
    # Add some binary code in the background (0s and 1s)
    small_font = ImageFont.truetype("DejaVuSans.ttf", 12)
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        digit = random.choice(["0", "1"])
        opacity = random.randint(50, 150)
        draw.text((x, y), digit, fill=(74, 175, 80, opacity), font=small_font)
    
    # Draw Python logo
    python_blue = (53, 114, 165)
    python_yellow = (255, 211, 67)
    
    # Draw a stylized Python logo (simplified)
    # Snake body
    draw.ellipse((width//2-80, height//2-60, width//2+80, height//2+60), 
                 fill=python_blue, outline=python_blue)
    
    # Snake head
    draw.ellipse((width//2+40, height//2-40, width//2+100, height//2+20), 
                 fill=python_yellow, outline=python_yellow)
    
    # Eye
    draw.ellipse((width//2+65, height//2-25, width//2+80, height//2-10), 
                 fill=(0, 0, 0), outline=(0, 0, 0))
    
    # Add quiz-related elements
    # Question mark
    large_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
    draw.text((width//4-30, height//2-80), "?", fill=(255, 255, 255, 180), font=large_font)
    
    # Add some code symbols
    code_font = ImageFont.truetype("DejaVuSansMono.ttf", 16)
    code_snippets = [
        "def quiz():",
        "    return knowledge",
        "class PythonMaster:",
        "    def __init__(self):",
        "        self.skills = []",
        "if __name__ == '__main__':",
        "    start_quiz()"
    ]
    
    for i, snippet in enumerate(code_snippets):
        y_pos = height//2 + 80 + i*20
        if y_pos < height - 20:  # Ensure it fits on the image
            draw.text((30, y_pos), snippet, fill=(200, 200, 200, 200), font=code_font)
    
    # Apply some effects
    # Add a slight blur for a professional look
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Enhance contrast slightly
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    # Save the image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
    print(f"Created welcome image: {output_path}")
    return output_path

if __name__ == "__main__":
    # Create the images directory if it doesn't exist
    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Create the welcome image
    create_python_quiz_image(os.path.join(images_dir, "welcome.png"))