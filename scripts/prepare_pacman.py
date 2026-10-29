#!/usr/bin/env python3
"""Validate Pac-Man output and animate an empty calendar without inventing activity."""
from pathlib import Path
import xml.etree.ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def prepare(path: Path) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != f'{{{NS}}}svg' or path.stat().st_size < 1000:
        raise ValueError(f'Invalid contribution graph: {path}')
    frames = root.find(f'.//{{{NS}}}frames')
    if frames is None:
        raise ValueError('Pac-Man metadata changed; inspect upstream output')
    if int(frames.text or '0') > 0:
        return
    # An empty GitHub calendar produces a stationary Pac-Man. Keep its empty cells
    # truthful, and move the existing character in a separate, labelled idle lane.
    root.set('height', '250')
    root.set('viewBox', '0 0 1166 250')
    background = root.find(f'{{{NS}}}rect')
    if background is not None:
        background.set('height', '250')
    dark = '-dark' in path.stem
    text = ET.SubElement(root, f'{{{NS}}}text', {
        'x': '16', 'y': '205', 'font-size': '12',
        'font-family': 'Arial,Helvetica,sans-serif',
        'fill': '#8b949e' if dark else '#57606a',
    })
    text.text = 'No public contributions returned for this period — Pac-Man idle animation.'
    pacman = root.find(f".//{{{NS}}}path[@id='pacman']")
    if pacman is None:
        raise ValueError('Pac-Man element missing')
    for anim in pacman.findall(f'{{{NS}}}animateTransform'):
        anim.set('dur', '16s')
        anim.set('keyTimes', '0;0.48;0.50;0.98;1')
        if anim.get('type') == 'translate':
            anim.set('values', '10,220;1130,220;1130,220;10,220;10,220')
        elif anim.get('type') == 'rotate':
            anim.set('values', '0 10 10;0 10 10;180 10 10;180 10 10;0 10 10')
    tree.write(path, encoding='unicode')
    print(f'Added labelled idle animation: {path}')


if __name__ == '__main__':
    for filename in ('pacman-contribution-graph.svg', 'pacman-contribution-graph-dark.svg'):
        prepare(Path('dist') / filename)
