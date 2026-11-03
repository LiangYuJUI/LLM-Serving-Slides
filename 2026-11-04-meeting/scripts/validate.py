#!/usr/bin/env python3
"""Inspect actual PDF destinations and image pixels, render every page and montages."""
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-dir', type=Path, help='Optional persistent page renders; defaults to an automatically cleaned temporary directory')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="helix-render-") as tmp:
        validate(args.render_dir or Path(tmp))


def validate(render_dir):
    text = (ROOT / '2026-11-04-Helix.tex').read_text()
    frames = re.findall(r'\\begin\{frame\}\[c,label=([^]]+)\]\{([^\n]+?)\}(.*?)\\end\{frame\}', text, re.S)
    doc = fitz.open(ROOT / 'output/pdf/2026-11-04-Helix.pdf')
    assert len(frames) == len(doc) == 58
    expected = {label: i for i, (label, _, _) in enumerate(frames)}
    main_count = expected['INDEX']
    assert main_count == 16
    section_starts = []
    page_count = 0
    for token in re.finditer(r'\\section\{|\\begin\{frame\}', text):
        if token[0].startswith(r'\section'):
            section_starts.append(page_count + 1)
        else:
            page_count += 1
    destinations = doc.resolve_names()
    for label, page in expected.items():
        assert destinations[label]['page'] == page, (label, destinations[label])
    links = []
    for i, (label, title, body) in enumerate(frames):
        actual = doc[i].get_links()
        if label != 'INDEX':
            assert 'Source: Helix,' in doc[i].get_text(), (label, 'missing source')
        # Retain the blue title and small illustrative layer diagram, but no
        # wide SoftBlue panel in the body (the former takeaway treatment).
        for drawing in doc[i].get_drawings():
            fill = drawing.get('fill')
            rect = drawing['rect']
            softblue = (233/255, 242/255, 249/255)
            if fill and len(fill) == 3 and max(abs(a-b) for a,b in zip(fill, softblue)) < .005:
                assert rect.y0 < 30 or rect.width < 150, (label, 'blue body panel')
        for link in actual:
            target = link.get('nameddest')
            assert target in destinations, (i + 1, link)
            assert link['page'] == destinations[target]['page'], (i + 1, link)
            assert 0 <= link['page'] < len(doc)
            assert doc[i].rect.contains(link['from']), (i + 1, 'link outside page')
            links.append({'from_page': i + 1, 'destination': target, 'to_page': link['page'] + 1})
        requested = re.findall(r'\\(?:nav|hyperlink)\{([^}]+)\}', body)
        back = re.findall(r'\\back(?:\[.*?\])?\{([^}]+)\}', body)
        if i >= main_count:
            assert len(back) == 1, label
            assert expected[back[0]] < main_count
            requested += back + ['INDEX']
        requested += ['INDEX']  # persistent footer
        section_start = max(p for p in section_starts if p <= i + 1)
        requested += [f'Navigation{section_start}']
        assert Counter(l.get('nameddest') for l in actual) == Counter(requested), (label, 'link multiplicity')
        for target in requested:
            assert any(l.get('nameddest') == target and l['page'] == (expected[target] if target in expected else section_start - 1) for l in actual), (label, target)
        # Text clipping / footer clearance. Footline is below y=244 pt.
        for block in doc[i].get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    r = fitz.Rect(span['bbox'])
                    assert r.x0 >= -0.5 and r.x1 <= doc[i].rect.width + .5, (i + 1, span)
                    assert r.y0 >= 0 and r.y1 <= doc[i].rect.height, (i + 1, span)
                    if r.y0 < 242:
                        assert r.y1 < 243, (i + 1, 'content touches footer', span)
    # Every appendix page must be reachable by clicking from a main slide.
    graph = {i: {link['page'] for link in doc[i].get_links()
                 if not link.get('nameddest', '').startswith('Navigation')}
             for i in range(len(doc))}
    reached = set(range(main_count))
    pending = list(reached)
    while pending:
        for target in graph[pending.pop()] - reached:
            reached.add(target)
            pending.append(target)
    assert reached == set(range(len(doc))), ('unreachable pages', sorted(set(range(len(doc))) - reached))
    # A shared detail page must offer an explicit return to every main entry point.
    for origin in range(main_count):
        for target in graph[origin]:
            if target > expected['INDEX']:
                assert origin in graph[target], ('missing return', origin + 1, target + 1)
    assert r'\takeaway' not in text
    required_claims = {
        expected['M03'] + 1: ['throughput', 'latency', 'percentiles'],
        expected['M06'] + 1: ['Pruning', 'timed solving', 'global optimality'],
        expected['M10'] + 1: ['Offline:', 'saturate the cluster', 'Online:', 'Azure Conversation', '75%', 'not always saturated'],
        expected['B26'] + 1: ['1.86', '1.69', 'average latency higher'],
        expected['M11'] + 1: ['Throughput', 'larger gains over SP', 'larger model', 'Latency', 'does not consistently outperform both baselines'],
        expected['M12'] + 1: ['42-node simulation', '70B', 'higher throughput', 'greater GPU heterogeneity', 'does not consistently improve latency'],
    }
    required_claims[expected['BASELINES'] + 1] = [
        'Helix', 'Swarm', 'SP', 'Petals', 'Placement-only',
        'no end-to-end', 'Fix the Helix scheduler', 'vary placement']
    for page, claims in required_claims.items():
        content = ' '.join(doc[page-1].get_text().split())
        for claim in claims:
            assert claim in content, (page, 'missing claim', claim)
    patterns = [line.strip() for line in (ROOT / '.gitignore').read_text().splitlines()
                if line.startswith('*.')]
    intermediates = sorted(str(p.relative_to(ROOT)) for pattern in patterns for p in ROOT.rglob(pattern))
    assert not intermediates, ('LaTeX intermediates remain', intermediates)
    files = sorted((ROOT / 'Helix/Without-Caption').glob('*.png'))
    assert len(files) == 12
    original_fig6 = ROOT / 'Helix/Helix_Figure_06_Single_Cluster_Results.png'
    original_fig7 = ROOT / 'Helix/Helix_Figure_07_Geo_Distributed_Cluster_Results.png'
    originals = {str(original_fig6.relative_to(ROOT)): 'M10',
                 str(original_fig7.relative_to(ROOT)): 'M11'}
    files.extend([original_fig6, original_fig7])
    hashes = {}
    for path in files:
        pixels = Image.open(path).convert('RGB').tobytes()
        hashes[hashlib.md5(pixels).digest()] = str(path.relative_to(ROOT))
    used = set()
    occurrences = []
    for i, page in enumerate(doc):
        for item in page.get_image_info(hashes=True):
            assert item['digest'] in hashes, (i + 1, 'image does not match an approved source PNG')
            name = hashes[item['digest']]
            if name in originals:
                assert i == expected[originals[name]], (i + 1, 'original figure on wrong slide')
                rect = fitz.Rect(item['bbox'])
                assert doc[i].rect.contains(rect) and rect.y1 < 243, 'Original figure must fit in full'
            used.add(name)
            occurrences.append({'page': i + 1, 'file': name, 'bbox': list(item['bbox'])})
    assert used == set(hashes.values())
    assert re.findall(r'\{(Helix/Helix_Figure[^}]+)\}', text) == list(originals)
    assert r'\caption{' not in text
    assert not any(ord(c)<32 and c not in '\n\r' for c in text), 'Unexpected control character'
    qa = ROOT / 'output/qa'
    qa.mkdir(exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(render_dir / f'page-{i+1:02}.png')
    for start, stop, name in [(0, main_count, 'main-montage'), (main_count, len(doc), 'backup-montage')]:
        canvas = Image.new('RGB', (1600, ((stop-start+3)//4)*250), '#d6d6d6')
        for j, i in enumerate(range(start, stop)):
            im = Image.open(render_dir / f'page-{i+1:02}.png')
            im.thumbnail((396, 223))
            xy = ((j % 4)*400, (j // 4)*250)
            canvas.paste(im, xy)
            ImageDraw.Draw(canvas).text((xy[0]+6, xy[1]+227), f'PDF {i+1}', fill='black')
        canvas.save(qa / f'{name}.jpg', quality=92)
    report = {
        'latex_intermediates_remaining': intermediates, 'blue_takeaway_panels': 0,
        'source_pages_checked': len(doc) - 1, 'critical_claim_pages_checked': list(required_claims),
        'pdf_pages': len(doc), 'main_pages': main_count, 'discussion_pages_including_index': 42,
        'internal_links_checked': len(links), 'caption_free_figures_matched_by_pixel_hash': len(used) - len(originals),
        'original_figures_matched_by_pixel_hash': list(originals),
        'figures': occurrences, 'links': links,
        'frames': [{'page': i+1, 'label': label, 'title': title, 'back_to_main': re.findall(r'\\back(?:\[.*?\])?\{([^}]+)\}', body)}
                   for i, (label, title, body) in enumerate(frames)],
        'rendered_pages': len(doc), 'manual_visual_review': 'Required separately; montage generation is not visual proof.'}
    (qa / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(doc)} pages, {len(links)} actual PDF links, 14 source image pixel hashes (12 caption-free + original Figures 6 and 7), all pages rendered.')


if __name__ == '__main__':
    main()
