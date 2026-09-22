# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import math

size = (256, 256)
img = Image.new("RGBA", size, (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Outer rounded rectangle background
# Gradient simulation
for i in range(128):
    alpha = int(255 * (1 - i/200.0))
    # Dark obsidian slate background with purple/indigo glow
    r = int(14 + (24 - 14) * (i / 128))
    g = int(16 + (30 - 16) * (i / 128))
    b = int(24 + (45 - 24) * (i / 128))

# Draw smooth rounded square
corner_radius = 48
draw.rounded_rectangle([8, 8, 248, 248], radius=corner_radius, fill=(16, 19, 28, 255), outline=(99, 102, 241, 200), width=4)

# Inner neon glow border
draw.rounded_rectangle([14, 14, 242, 242], radius=42, outline=(6, 182, 212, 100), width=2)

# Central Symbol: Quantum Builder Hammer & Gear / Rocket Anvil
# Hammer handle
draw.line([(80, 180), (160, 100)], fill=(200, 210, 255, 255), width=14)
draw.line([(82, 178), (158, 102)], fill=(99, 102, 241, 255), width=8)

# Hammer head
# Polygon head
head_poly = [
    (140, 60),
    (195, 115),
    (180, 130),
    (125, 75)
]
draw.polygon(head_poly, fill=(6, 182, 212, 255), outline=(255, 255, 255, 240))

# Claw/Back of head
draw.polygon([(120, 80), (135, 65), (105, 55), (95, 75)], fill=(129, 140, 248, 255), outline=(255, 255, 255, 220))

# Energy sparks
spark_coords = [
    (185, 50), (205, 70), (160, 35), (215, 100), (70, 195)
]
for sx, sy in spark_coords:
    draw.line([(sx-4, sy), (sx+4, sy)], fill=(250, 204, 21, 255), width=2)
    draw.line([(sx, sy-4), (sx, sy+4)], fill=(250, 204, 21, 255), width=2)

# Bottom badge "GEN BUILDER"
try:
    font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 20)
except Exception:
    font = ImageFont.load_default()

text = "BUILDER"
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
draw.rounded_rectangle([(128 - tw//2 - 12), 200, (128 + tw//2 + 12), 230], radius=8, fill=(99, 102, 241, 230))
draw.text((128 - tw//2, 204), text, fill=(255, 255, 255, 255), font=font)

png_path = "/home/ryan/heo-harness/assets/builder_icon.png"
img.save(png_path, "PNG")

# Also copy to workplace
os.system(f"cp {png_path} /home/ryan/Documents/Ryan-Workplace/Heo-Harness/assets/builder_icon.png 2>/dev/null || true")

# Write SVG vector icon as well
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#141824"/>
      <stop offset="100%" stop-color="#0a0c12"/>
    </linearGradient>
    <linearGradient id="neonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="50%" stop-color="#06b6d4"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  
  <rect x="10" y="10" width="236" height="236" rx="46" fill="url(#bgGrad)" stroke="#6366f1" stroke-width="4" filter="url(#glow)"/>
  <rect x="18" y="18" width="220" height="220" rx="38" fill="none" stroke="rgba(6, 182, 212, 0.4)" stroke-width="2"/>
  
  <!-- Central Icon: Hammer & Compass / Circuit -->
  <g transform="translate(18, 12)">
    <line x1="60" y1="170" x2="140" y2="90" stroke="#a5b4fc" stroke-width="12" stroke-linecap="round"/>
    <line x1="62" y1="168" x2="138" y2="92" stroke="#6366f1" stroke-width="6" stroke-linecap="round"/>
    
    <polygon points="120,50 175,105 160,120 105,65" fill="#06b6d4" stroke="#ffffff" stroke-width="3"/>
    <polygon points="100,70 115,55 85,45 75,65" fill="#818cf8" stroke="#ffffff" stroke-width="2"/>
    
    <!-- Sparkles -->
    <path d="M 165 40 L 165 50 M 160 45 L 170 45" stroke="#facc15" stroke-width="3" stroke-linecap="round"/>
    <path d="M 190 75 L 190 85 M 185 80 L 195 80" stroke="#facc15" stroke-width="3" stroke-linecap="round"/>
    <path d="M 50 185 L 50 195 M 45 190 L 55 190" stroke="#06b6d4" stroke-width="3" stroke-linecap="round"/>
  </g>
  
  <!-- Badge -->
  <rect x="68" y="196" width="120" height="30" rx="8" fill="#6366f1"/>
  <text x="128" y="217" font-family="system-ui, sans-serif" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle" letter-spacing="1.5">BUILDER</text>
</svg>"""

with open("/home/ryan/heo-harness/assets/builder_icon.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Generated builder_icon.png and builder_icon.svg successfully!")
