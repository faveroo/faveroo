#!/usr/bin/env python3
"""Build the original, code-only profile GIF. Requires Pillow (pip install Pillow)."""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
FONT = ImageFont.truetype(FONT_PATH, 19)
SMALL = ImageFont.truetype(FONT_PATH, 13)
BG, PANEL, BORDER = '#0d1117', '#161b22', '#303845'
TEXT, MUTED, RED, GREEN = '#c6cfdb', '#8390a3', '#ff818c', '#a5d6a7'
CODE = """<?php
$developer = [
    'name'    => 'Gabriel Favero Hoffmann',
    'focus'   => ['PHP', 'Laravel', 'APIs'],
    'mindset' => 'Always learning.',
];

echo $developer['mindset'] . PHP_EOL;"""
TOKENS = re.compile(r"'[^']*'?|\$[A-Za-z_]+|<\?php|\becho\b|\bPHP_EOL\b|.")

def draw_code(draw, text, x, y):
    for token in TOKENS.findall(text):
        color = GREEN if token.startswith("'") else RED if token in ('<?php', 'echo') else '#a5c9ff' if token.startswith('$') else TEXT
        draw.text((x, y), token, font=FONT, fill=color)
        x += draw.textlength(token, font=FONT)
    return x

def frame(visible, command='', output=False, cursor=False):
    im = Image.new('RGB', (960, 420), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 959, 419), outline=BORDER)
    d.rectangle((1, 1, 958, 45), fill=PANEL)
    d.rectangle((1, 1, 4, 45), fill=RED)
    d.text((25, 15), 'profile.php', font=SMALL, fill=TEXT)
    d.text((738, 15), 'PHP / @faveroo', font=SMALL, fill=MUTED)
    d.line((1, 45, 958, 45), fill=BORDER)
    lines = visible.split('\n')
    for i in range(8):
        y = 62 + i * 28
        d.text((27, y+3), str(i+1), font=SMALL, fill=MUTED)
        if i < len(lines):
            end = draw_code(d, lines[i], 68, y)
            if cursor and i == len(lines)-1:
                d.rectangle((end+3, y+2, end+5, y+22), fill=RED)
    d.line((1, 307, 958, 307), fill=BORDER)
    d.text((25, 319), 'TERMINAL', font=SMALL, fill=MUTED)
    if command:
        d.text((25, 346), '>', font=FONT, fill=RED)
        d.text((50, 346), command, font=FONT, fill=TEXT)
    if output:
        d.text((25, 379), 'Always learning.', font=FONT, fill=GREEN)
    return im

def main():
    frames, durations = [frame('')], [600]
    for n in range(3, len(CODE)+3, 3):
        frames.append(frame(CODE[:n], cursor=n < len(CODE)))
        durations.append(65)
    command = 'php profile.php'
    for n in range(1, len(command)+1):
        frames.append(frame(CODE, command[:n]))
        durations.append(75)
    frames.append(frame(CODE, command, output=True))
    durations.append(3200)
    output = ROOT / 'assets/coding.gif'
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True, disposal=1)
    print(f'{output}: {len(frames)} frames, {output.stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
