from PIL import Image, ImageDraw
import math

# Create professional purple background
width, height = 1400, 900
img = Image.new('RGB', (width, height), '#f8f6ff')
draw = ImageDraw.Draw(img)

# Purple gradient background
for y in range(height):
    ratio = y / height
    r = int(248 + (230 - 248) * ratio)
    g = int(246 + (220 - 246) * ratio)
    b = int(255 + (245 - 255) * ratio)
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# Add subtle geometric patterns
for i in range(0, width, 100):
    for j in range(0, height, 100):
        if (i + j) % 200 == 0:
            draw.ellipse([i-2, j-2, i+2, j+2], fill='#e6d9ff', outline=None)

# Professional abstract shapes
for i in range(5):
    x = 200 + i * 250
    y = 150 + (i % 2) * 100
    
    # Clean geometric shapes
    draw.ellipse([x-30, y-30, x+30, y+30], fill='#d4c5ff', outline='#b8a3ff', width=2)
    draw.rectangle([x-15, y-50, x+15, y+50], fill='#c9b8ff', outline='#a68fff', width=1)

# Bottom wave pattern
wave_points = []
for x in range(0, width + 50, 50):
    y = height - 100 + 30 * math.sin(x * 0.01)
    wave_points.extend([x, y])
wave_points.extend([width, height, 0, height])
draw.polygon(wave_points, fill='#e6d9ff')

# Save the image
img.save('static/background.jpg', 'JPEG', quality=95)
print("Professional purple background created: static/background.jpg")