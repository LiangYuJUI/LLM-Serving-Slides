#!/usr/bin/env python3
"""Inspect actual PDF destinations and image pixels, render every page and montages."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-dir', type=Path, default=ROOT / 'output/qa/pages')
    args = parser.parse_args()
    text = (ROOT / '2026-11-04-Helix.tex').read_text()
    frames = re.findall(r'\\begin\{frame\}\[c,label=([^]]+)\]\{([^\n]+?)\}(.*?)\\end\{frame\}', text, re.S)
    doc = fitz.open(ROOT / 'output/pdf/2026-11-04-Helix.pdf')
    assert len(frames) == len(doc) == 57
    expected = {label: i for i, (label, _, _) in enumerate(frames)}
    destinations = doc.resolve_names()
    for label, page in expected.items():
        assert destinations[label]['page'] == page, (label, destinations[label])
    links = []
    for i, (label, title, body) in enumerate(frames):
        actual = doc[i].get_links()
        for link in actual:
            target = link.get('nameddest')
            assert target in destinations, (i + 1, link)
            assert link['page'] == destinations[target]['page'], (i + 1, link)
            assert 0 <= link['page'] < len(doc)
            assert doc[i].rect.contains(link['from']), (i + 1, 'link outside page')
            links.append({'from_page': i + 1, 'destination': target, 'to_page': link['page'] + 1})
        requested = re.findall(r'\\nav\{([^}]+)\}', body)
        back = re.findall(r'\\back\{([^}]+)\}', body)
        if i >= 15:
            assert len(back) == 1, label
            assert back[0].startswith('M')
            requested += back + ['INDEX']
        requested += ['INDEX']  # persistent footer
        for target in requested:
            assert any(l.get('nameddest') == target and l['page'] == expected[target] for l in actual), (label, target)
        # Text clipping / footer clearance. Footline is below y=244 pt.
        for block in doc[i].get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    r = fitz.Rect(span['bbox'])
                    assert r.x0 >= -0.5 and r.x1 <= doc[i].rect.width + .5, (i + 1, span)
                    assert r.y0 >= 0 and r.y1 <= doc[i].rect.height, (i + 1, span)
                    if r.y0 < 242:
                        assert r.y1 < 243, (i + 1, 'content touches footer', span)
    files = sorted((ROOT / 'Helix/Without-Caption').glob('*.png'))
    assert len(files) == 12
    hashes = {}
    for path in files:
        pixels = Image.open(path).convert('RGB').tobytes()
        hashes[hashlib.md5(pixels).digest()] = path.name
    used = set()
    occurrences = []
    for i, page in enumerate(doc):
        for item in page.get_image_info(hashes=True):
            assert item['digest'] in hashes, (i + 1, 'image does not match a supplied caption-free PNG')
            name = hashes[item['digest']]
            used.add(name)
            occurrences.append({'page': i + 1, 'file': name, 'bbox': list(item['bbox'])})
    assert used == set(hashes.values())
    assert not re.search(r'\{Helix/Helix_Figure', text)
    assert r'\caption{' not in text
    assert not any(ord(c)<32 and c not in '\n\r' for c in text), 'Unexpected control character'
    qa = ROOT / 'output/qa'
    qa.mkdir(exist_ok=True)
    args.render_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(args.render_dir / f'page-{i+1:02}.png')
    for start, stop, name in [(0, 15, 'main-montage'), (15, len(doc), 'backup-montage')]:
        canvas = Image.new('RGB', (1600, ((stop-start+3)//4)*250), '#d6d6d6')
        for j, i in enumerate(range(start, stop)):
            im = Image.open(args.render_dir / f'page-{i+1:02}.png')
            im.thumbnail((396, 223))
            xy = ((j % 4)*400, (j // 4)*250)
            canvas.paste(im, xy)
            ImageDraw.Draw(canvas).text((xy[0]+6, xy[1]+227), f'PDF {i+1}', fill='black')
        canvas.save(qa / f'{name}.jpg', quality=92)
    report = {
        'pdf_pages': len(doc), 'main_pages': 15, 'discussion_pages_including_index': 42,
        'internal_links_checked': len(links), 'caption_free_figures_matched_by_pixel_hash': len(used),
        'figures': occurrences, 'links': links,
        'frames': [{'page': i+1, 'label': label, 'title': title, 'back_to_main': re.findall(r'\\back\{([^}]+)\}', body)}
                   for i, (label, title, body) in enumerate(frames)],
        'rendered_pages': len(doc), 'manual_visual_review': 'Required separately; montage generation is not visual proof.'}
    (qa / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(doc)} pages, {len(links)} actual PDF links, 12 source image pixel hashes, all pages rendered.')


if __name__ == '__main__':
    main()
