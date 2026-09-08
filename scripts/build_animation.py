#!/usr/bin/env python3
"""Build the decorative request-flow GIF. Requires Pillow (python -m pip install Pillow).

This is an illustrative animation, not a live system status or performance claim.
Fonts default to DejaVu Sans; pass PROFILE_FONT to use another local TrueType font.
"""
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = os.getenv('PROFILE_FONT', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
font = ImageFont.truetype(FONT, 16)
small = ImageFont.truetype(FONT, 11)
frames = []
for frame in range(80):
    im = Image.new('RGB', (880, 150), '#101115')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 879, 149), radius=16, outline='#303038')
    d.text((24, 15), 'BEHIND THE REQUEST', font=small, fill='#b7b7c2')
    d.text((688, 15), 'ILLUSTRATIVE FLOW', font=small, fill='#b7b7c2')
    centers = [92, 266, 440, 614, 788]
    d.line((92, 83, 788, 83), fill='#42424b', width=2)
    for idx, (x, label) in enumerate(zip(centers, ['Request', 'Route', 'Validate', 'Persist', 'Respond'])):
        d.rounded_rectangle((x-64, 57, x+64, 109), radius=10, fill='#1b1c23', outline='#42424b')
        d.text((x, 83), label, anchor='mm', font=font, fill='#f4f4f7')
    progress = frame / 80 * 4
    x = 92 + progress * 174
    d.ellipse((x-5, 119, x+5, 129), fill='#ff626f')
    idx = min(4, round(progress))
    cx = centers[idx]
    d.rounded_rectangle((cx-64, 57, cx+64, 109), radius=10, outline='#ff626f', width=2)
    frames.append(im)
frames[0].save(ROOT/'assets/request-flow.gif', save_all=True, append_images=frames[1:], duration=65, loop=0, optimize=True)
print('Generated assets/request-flow.gif')
