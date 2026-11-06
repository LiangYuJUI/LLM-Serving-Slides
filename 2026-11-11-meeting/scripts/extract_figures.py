#!/usr/bin/env python3
"""Extract original vector figures from the meeting's SIGMETRICS PDF.

Coordinates are PDF points in PyMuPDF's top-left coordinate system.
Keep panel captions but omit the paper's outer figure captions and prose.
"""
from pathlib import Path
import hashlib
import json
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'GreenCache-Research-Meeting-2026-11-11/GreenCache-Carbon-Aware-KV-Caching-SIGMETRICS2026.pdf'
FIGDIR = PAPER.parent / 'Figures-PDF'
# figure: (one-based paper page, bounding rectangle)
CROPS = {
    '01': (4, (45, 82, 442, 175)),
    '02': (5, (42, 80, 443, 192)),
    '03': (6, (42, 80, 249, 189)),
    '04': (6, (260, 80, 443, 189)),
    '05': (7, (42, 80, 239, 190)),
    '06': (7, (248, 80, 443, 190)),
    '07': (8, (42, 80, 443, 190)),
    '08': (9, (42, 80, 443, 180)),
    '09': (10, (47, 82, 159, 221)),
    '10': (10, (202, 92, 443, 209)),
    '11': (11, (42, 80, 443, 211)),
    '12': (16, (41, 81, 443, 317)),
    '13': (17, (42, 81, 443, 314)),
    '14': (18, (42, 81, 443, 407)),
    '15': (19, (42, 80, 443, 190)),
    '16': (19, (309, 222, 443, 313)),
    '17': (20, (41, 80, 443, 190)),
    '18': (20, (41, 218, 443, 326)),
    '19': (21, (44, 82, 443, 188)),
    '20': (21, (44, 221, 443, 328)),
    '12a': (16, (41, 81, 443, 205)),
    '12b': (16, (41, 205, 443, 317)),
    '12-legend': (16, (135, 81, 347, 95)),
    '13a': (17, (42, 81, 443, 209)),
    '13b': (17, (42, 207, 443, 314)),
    '13-legend': (17, (105, 82, 383, 104)),
    '14a': (18, (42, 81, 443, 250)),
    '14b': (18, (42, 250, 443, 407)),
    '14-legend': (18, (100, 82, 391, 96)),
}
# Rows and centered panel captions overlap vertically in the paper. Separate
# clips keep adjacent-row tick labels out without redrawing any figure content.
PARTS = {
    '12a': [(41, 81, 443, 192), (170, 193, 315, 205)],
    '12b': [(41, 205, 443, 301), (173, 303, 313, 317)],
    '13a': [(42, 81, 443, 194), (210, 196, 276, 209)],
    '13b': [(42, 207, 443, 298), (210, 300, 276, 314)],
}


def make_figure(paper, key):
    if key == '12-legend':
        # The legend and the upper axis ticks overlap vertically. Isolate the
        # original legend Form XObject instead of capturing those stray ticks.
        isolated = fitz.open()
        isolated.insert_pdf(paper, from_page=15, to_page=15)
        page = isolated[0]
        page.set_mediabox(fitz.Rect(0, 0, 1080, 21.6))
        content = isolated.get_new_xref()
        isolated.update_object(content, '<<>>')
        isolated.update_stream(content, b'q /Im16 Do Q')
        page.set_contents(content)
        result = fitz.open()
        clip = fitz.Rect(250, 0, 835, 21.6)
        result.new_page(width=clip.width, height=clip.height).show_pdf_page(
            fitz.Rect(0, 0, clip.width, clip.height), isolated, 0, clip=clip)
        isolated.close()
        return result
    page_number, bounds = CROPS[key]
    box = fitz.Rect(bounds)
    result = fitz.open()
    page = result.new_page(width=box.width, height=box.height)
    for part in PARTS.get(key, [bounds]):
        clip = fitz.Rect(part)
        target = clip - (box.x0, box.y0, box.x0, box.y0)
        page.show_pdf_page(target, paper, page_number - 1, clip=clip)
    return result


def main():
    FIGDIR.mkdir(exist_ok=True)
    with fitz.open(PAPER) as paper:
        for key in CROPS:
            with make_figure(paper, key) as figure:
                figure.save(FIGDIR / f'GreenCache-Fig{key}.pdf', garbage=4, deflate=True)
    manifest = {
        'source': str(PAPER.relative_to(ROOT)),
        'source_sha256': hashlib.sha256(PAPER.read_bytes()).hexdigest(),
        'coordinate_system': 'PDF points, top-left origin',
        'isolated_forms': {'12-legend': {'page': 16, 'name': 'Im16',
                                       'clip': [250, 0, 835, 21.6]}},
        'figures': {key: {'page': page, 'bounds': bounds,
                          'parts': PARTS.get(key, [bounds])}
                    for key, (page, bounds) in CROPS.items()},
    }
    (FIGDIR / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Extracted {len(CROPS)} vector figure assets from {PAPER.name}.')


if __name__ == '__main__':
    main()
