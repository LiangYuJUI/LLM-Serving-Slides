#!/usr/bin/env python3
"""Check GreenCache destinations, links, image pixels, and page renders."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import tempfile
from collections import Counter
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / '2026-11-11-GreenCache.tex'
PDF = ROOT / 'output/pdf/2026-11-11-GreenCache.pdf'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-dir', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='greencache-render-') as tmp:
        validate(args.render_dir or (ROOT / 'output/qa/pages'))


def validate(render_dir):
    text = TEX.read_text()
    frames = re.findall(
        r'\\begin\{frame\}\[(?:t|c),label=([^]]+)\](?:\{([^\n]+?)\})?(.*?)\\end\{frame\}',
        text, re.S)
    # Title frame has no brace title; the regex still captures it via the optional group.
    doc = fitz.open(PDF)
    assert len(frames) == len(doc), (len(frames), len(doc))
    expected = {label: i for i, (label, _, _) in enumerate(frames)}
    main_count = expected['INDEX']
    assert main_count == 15, main_count
    section_starts = []
    page_count = 0
    for token in re.finditer(r'\\section\{|\\begin\{frame\}', text):
        if token[0].startswith(r'\section'):
            section_starts.append(page_count + 1)
        else:
            page_count += 1
    destinations = doc.resolve_names()
    for label, page in expected.items():
        assert destinations[label]['page'] == page, (label, destinations.get(label))
    links = []
    graph = {}
    for i, (label, title, body) in enumerate(frames):
        actual = doc[i].get_links()
        graph[i] = set()
        if label != 'INDEX':
            assert 'Source: GreenCache,' in doc[i].get_text(), label
        for link in actual:
            target = link.get('nameddest')
            assert target in destinations, (i + 1, link)
            assert link['page'] == destinations[target]['page'], (i + 1, target)
            assert doc[i].rect.contains(fitz.Rect(link['from'])), (i + 1, 'link outside page')
            graph[i].add(link['page'])
            links.append({'from_page': i + 1, 'from_label': label,
                          'destination': target, 'to_page': link['page'] + 1})
        for block in doc[i].get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    r = fitz.Rect(span['bbox'])
                    assert r.x0 >= -1 and r.x1 <= doc[i].rect.width + 1, (i + 1, span['text'], span['bbox'])
                    assert r.y0 >= -1 and r.y1 <= doc[i].rect.height + 1, (i + 1, span['text'])
                    if r.y0 < 242:
                        assert r.y1 < 244, (i + 1, 'content touches footer', span['text'], span['bbox'])
        # Cropped figures keep the full PNG in the content stream, so the
        # reported image box is not the visible clip. Button clearance is
        # checked visually; this loop only rejects buttons that leave the page.
    # Every backup page is reachable from a main slide without section-nav links.
    reached = set(range(main_count))
    pending = list(reached)
    while pending:
        for target in graph[pending.pop()] - reached:
            if target is None:
                continue
            reached.add(target)
            pending.append(target)
    missing = sorted(set(range(len(doc))) - reached)
    assert not missing, ('unreachable pages', [expected and frames[p][0] for p in missing])
    for origin in range(main_count):
        for target in graph[origin]:
            if target > expected['INDEX']:
                assert origin in graph[target], ('missing return', frames[origin][0], frames[target][0])
    claims = {
        'M04': ['90%', 'amortized', 'at most 10%', 'evaluated separately',
                'hardware lifetime and usage time', 'configurations are fixed',
                'current performance feedback', 'preset SLO constraints',
                'the ILP decides the capacity'],
        'B00': ['1.7', '0.03', 'not an end-to-end'],
        'M02': ['manufacturing', 'electricity', 'allocation time', 'low request rates', 'shared across more prompts'],
        'M03': ['below 1', 'Above 1', 'Cleaner electricity', 'offset the SSD', 'generation mix', 'Low-CI hours', 'High-CI hours'],
        'M07': ['Lowest score', 'not a measured'],
        'M08': ['No standalone GPU-serving simulator', 'LMCache', 'RAPL', 'pyNVML'],
        'M10': ['12.6%', '9.4%', '5.6%', 'not the FR-only'],
        'M11': ['2.5', '15', 'not viable'],
        'M12': ['15.1%', '25.3%', '15 TB'],
        'M14': ['reused input tokens', '0.26', '0.35'],
        'M15': ['OUR INTERPRETATION', 'does not evaluate HBF'],
        'B09': ['above 1 is a benefit', 'opposite direction'],
        'B11': ['does not pick one', '4.0'],
    }
    for label, needles in claims.items():
        content = ' '.join(doc[expected[label]].get_text().split())
        for needle in needles:
            assert needle in content, (label, needle)
    files = sorted((ROOT / 'GreenCache-Research-Meeting-2026-11-11/With-Caption').glob('*.png'))
    assert len(files) == 20
    hashes = {}
    for path in files:
        pixels = Image.open(path).convert('RGB').tobytes()
        hashes[hashlib.md5(pixels).digest()] = str(path.relative_to(ROOT))
    used = set()
    occurrences = []
    for i, page in enumerate(doc):
        for item in page.get_image_info(hashes=True):
            assert item['digest'] in hashes, (i + 1, 'image is not a supplied With-Caption PNG')
            name = hashes[item['digest']]
            used.add(name)
            occurrences.append({'page': i + 1, 'file': name, 'bbox': [round(v, 1) for v in item['bbox']]})
    assert used == set(hashes.values()), sorted(set(hashes.values()) - used)
    qa = ROOT / 'output/qa'
    qa.mkdir(exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    whitespace = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        dest = render_dir / f'page-{i+1:02}.png'
        pix.save(dest)
        im = Image.open(dest).convert('RGB')
        w, h = im.size
        # Content band below the title and above the footer.
        band = im.crop((0, int(h * 0.58), w, int(h * 0.90)))
        pixels = list(band.getdata())
        empty = sum(1 for r, g, b in pixels if r > 248 and g > 248 and b > 246)
        ratio = empty / len(pixels)
        whitespace.append({'page': i + 1, 'label': frames[i][0], 'lower_empty_ratio': round(ratio, 3)})
    for start, stop, name in [(0, main_count, 'main-montage'), (main_count, len(doc), 'backup-montage')]:
        columns = 4
        thumb_w, thumb_h, label_h = 396, 223, 22
        rows = (stop - start + columns - 1) // columns
        canvas = Image.new('RGB', (columns * 400, rows * (thumb_h + label_h + 8)), '#d6d6d6')
        draw = ImageDraw.Draw(canvas)
        for j, i in enumerate(range(start, stop)):
            im = Image.open(render_dir / f'page-{i+1:02}.png')
            im.thumbnail((thumb_w, thumb_h))
            xy = ((j % columns) * 400 + 2, (j // columns) * (thumb_h + label_h + 8) + 2)
            canvas.paste(im, xy)
            draw.text((xy[0] + 4, xy[1] + thumb_h + 2), f'{frames[i][0]}  PDF {i+1}', fill='black')
        canvas.save(qa / f'{name}.jpg', quality=92)
    report = {
        'pdf_pages': len(doc),
        'main_pages': main_count,
        'backup_pages_including_index': len(doc) - main_count,
        'internal_links_checked': len(links),
        'figures_matched_by_pixel_hash': len(used),
        'whitespace': whitespace,
        'frames': [{'page': i + 1, 'label': label, 'title': title}
                   for i, (label, title, _) in enumerate(frames)],
        'figures': occurrences,
        'links': links,
    }
    (qa / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    empty_mains = [row for row in whitespace if row['page'] <= main_count and row['lower_empty_ratio'] > 0.72]
    print(f'PASS: {len(doc)} pages, {len(links)} links, {len(used)} figure hashes.')
    if empty_mains:
        print('LOWER-PAGE EMPTY CANDIDATES:')
        for row in empty_mains:
            print(f"  {row['label']} PDF {row['page']}: {row['lower_empty_ratio']}")


if __name__ == '__main__':
    main()
