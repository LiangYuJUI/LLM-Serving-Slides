#!/usr/bin/env python3
"""Check Carbon--SLO destinations, link meaning, image bounds, and page renders."""
from pathlib import Path
import hashlib
import json
import math
import re
from collections import Counter
import pymupdf as fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / '2026-11-18-CarbonSLO.tex'
PDF = ROOT / 'output/pdf/2026-11-18-CarbonSLO.pdf'
CONTRACTS = ROOT / 'scripts/navigation-contracts.json'


def phrase_in(haystack, needle):
    hay = ' '.join(haystack.split())
    ned = ' '.join(needle.split())
    return re.search(r'(?<!\w)' + re.escape(ned) + r'(?!\w)', hay) is not None


def main():
    validate(ROOT / 'output/qa/pages')


def validate(render_dir):
    text = TEX.read_text()
    build_report = json.loads((ROOT / 'output/qa/build-validation.json').read_text())
    for key, path in [('pdf_sha256', PDF), ('source_sha256', TEX),
                      ('zip_sha256', ROOT / 'output/overleaf/CarbonSLO.zip')]:
        assert build_report[key] == hashlib.sha256(path.read_bytes()).hexdigest(), ('stale build', key)
    frames = re.findall(
        r'\\begin\{frame\}\[(?:t|c),label=([^]]+)\](?:\{([^\n]+?)\})?(.*?)\\end\{frame\}',
        text, re.S)
    doc = fitz.open(PDF)
    assert len(frames) == len(doc), (len(frames), len(doc))
    expected = {label: i for i, (label, _, _) in enumerate(frames)}
    assert len(expected) == len(frames), 'Duplicate frame labels'
    main_labels = [f'M{i:02d}' for i in range(1, 20)]
    backup_labels = [f'B{i:02d}' for i in range(1, 11)]
    assert [frames[i][0] for i in range(19)] == main_labels
    assert frames[19][0] == 'INDEX'
    assert [frames[i][0] for i in range(20, 30)] == backup_labels
    assert len(doc) == 30
    for target in re.findall(r'\\(?:hyperlink|nav|kw)\{([^}]+)\}', text):
        if target.startswith('#'):
            continue
        assert target in expected, ('missing source target', target)
    destinations = doc.resolve_names()
    for label, page in expected.items():
        assert destinations[label]['page'] == page, (label, destinations.get(label))

    links = []
    graph = {}
    for i, (label, title, body) in enumerate(frames):
        actual = doc[i].get_links()
        graph[i] = set()
        page_text = doc[i].get_text()
        if label != 'INDEX':
            assert 'Source: Topcu et al.,' in page_text, label
        if label.startswith('M'):
            assert f'Main {int(label[1:]):02d} / 19' in page_text, label
        if label.startswith('B'):
            assert label in page_text, label
        for link in actual:
            target = link.get('nameddest')
            assert target in destinations, (i + 1, link)
            assert link['page'] == destinations[target]['page'], (i + 1, target)
            assert doc[i].rect.contains(fitz.Rect(link['from'])), (i + 1, 'link outside page')
            graph[i].add(link['page'])
            links.append({'from_page': i + 1, 'from_label': label,
                          'destination': target, 'to_page': link['page'] + 1,
                          'text': ' '.join(doc[i].get_textbox(link['from']).split())})
        for block in doc[i].get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    r = fitz.Rect(span['bbox'])
                    assert r.x0 >= -1 and r.x1 <= doc[i].rect.width + 1, (i + 1, span['text'], span['bbox'])
                    assert r.y0 >= -1 and r.y1 <= doc[i].rect.height + 1, (i + 1, span['text'])
                    if r.y0 < 242:
                        assert r.y1 < 246, (i + 1, 'content touches footer', span['text'], span['bbox'])
        page_links = doc[i].get_links()
        for j, link in enumerate(page_links):
            for other in page_links[j + 1:]:
                overlap = fitz.Rect(link['from']) & fitz.Rect(other['from'])
                assert overlap.get_area() < 0.5, (label, 'overlapping click areas', link, other)

    def visible_link(label, words, target):
        page = doc[expected[label]]
        hits = page.search_for(words)
        boxes = [fitz.Rect(link['from']) for link in page.get_links()
                 if link.get('nameddest') == target]
        return any(box.intersects(hit) and hit.y1 < page.rect.height - 14
                   for box in boxes for hit in hits)

    contracts = json.loads(CONTRACTS.read_text())
    full_text = '\n'.join(page.get_text() for page in doc)
    assert 'Figure 8' not in full_text and 'Fig. 8' not in full_text
    assert 'does not power off' in doc[expected['M12']].get_text()
    assert '16 physical datacenters' in doc[expected['M09']].get_text()
    assert 'single-node' in doc[expected['M09']].get_text()
    assert 'up to 60' in doc[expected['M14']].get_text().lower()
    assert 'average' in doc[expected['M14']].get_text().lower() or 'average' in doc[expected['M14']].get_text()
    assert '55' in doc[expected['M14']].get_text()
    assert 'not an author result' in doc[expected['M19']].get_text()
    assert 'Go to Conclusion (M19)' in doc[expected['INDEX']].get_text()
    assert 'Back to Main' not in doc[expected['INDEX']].get_text()

    backup_audit = []
    for label, title, body in frames:
        if not label.startswith('B'):
            continue
        match = re.search(r'\\back(?:\[.*?\])?\{(M\d+)\}', body, re.S)
        assert match, (label, 'missing standard back macro')
        primary = match[1]
        assert visible_link(label, f'Back to Main {int(primary[1:])}', primary), (label, 'visible main return')
        assert visible_link(label, 'Discussion Index', 'INDEX'), (label, 'visible index button')
        targets = sorted({x['destination'] for x in links if x['from_label'] == label}
                         - {primary, 'INDEX'})
        backup_audit.append(dict(label=label, page=expected[label] + 1, title=title,
                                 primary_main=primary, back_to_main=True,
                                 discussion_index=True, cross_links=targets))

    actual_pairs = []
    for i, (label, _, _) in enumerate(frames[:19]):
        for link in doc[i].get_links():
            target = link.get('nameddest', '')
            if target.startswith('B'):
                actual_pairs.append((label, target))
    assert Counter(actual_pairs) == Counter((row['source'], row['target']) for row in contracts), 'contract pair drift'

    navigation_audit = []
    for row in contracts:
        origin, target, words = row['source'], row['target'], row['text']
        boxes = [link for link in doc[expected[origin]].get_links() if link.get('nameddest') == target]
        assert boxes, row
        assert any(phrase_in(doc[expected[origin]].get_textbox(link['from']), words) for link in boxes), row
        assert visible_link(origin, words, target), row
        content = re.sub(r'\s+', ' ', doc[expected[target]].get_text())
        for needle in row['target_evidence']:
            assert needle in content, (target, 'semantic evidence missing', needle, row['source'])
        backup = next(item for item in backup_audit if item['label'] == target)
        number = int(origin[1:])
        return_text = (f'Back to Main {number}' if backup['primary_main'] == origin else f'Main {number}')
        assert visible_link(target, return_text, origin), (origin, target, 'visible return missing')
        navigation_audit.append(dict(
            source=origin, text=words, target=target, source_question=frames[expected[origin]][1],
            primary_return=backup['primary_main'], semantic_mismatch=False, visible_return=True))

    reached = set(range(19))
    pending = list(reached)
    while pending:
        for target in graph[pending.pop()] - reached:
            reached.add(target)
            pending.append(target)
    missing = sorted(set(range(len(doc))) - reached)
    assert not missing, ('unreachable pages', [frames[p][0] for p in missing])
    for origin in range(19):
        for target in graph[origin]:
            if target > expected['INDEX']:
                assert origin in graph[target], ('missing return', frames[origin][0], frames[target][0])

    render_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=110)
        path = render_dir / f'page-{i:02d}.png'
        pix.save(path)
        paths.append(path)
    qa = ROOT / 'output/qa'
    montage(paths[:19], qa / 'main-montage.png', 5)
    montage(paths[19:], qa / 'backup-montage.png', 4)
    originals = {}
    figroot = ROOT / 'CarbonSLO-GeoDistributed-LLM-Serving-2026'
    for folder in ('With-Caption', 'Without-Caption'):
        for image in sorted((figroot / folder).glob('*.png')):
            originals[image.relative_to(ROOT).as_posix()] = hashlib.sha256(image.read_bytes()).hexdigest()
    audit_lines = ['# Navigation audit', '',
                   'Main is pages 1–19. Discussion index is page 20. Backup is pages 21–30.', '',
                   '| Backup | PDF | Primary return | Other links |',
                   '|---|---:|---|---|']
    for row in backup_audit:
        others = ', '.join(row['cross_links']) or '—'
        audit_lines.append(f"| {row['label']} | {row['page']} | {row['primary_main']} | {others} |")
    audit_lines += ['', '## Main keyword links', '',
                    '| Main | Words | Backup | Evidence checked |',
                    '|---|---|---|---|']
    for row in navigation_audit:
        evidence = next(item['target_evidence'] for item in contracts
                        if item['source'] == row['source'] and item['target'] == row['target'] and item['text'] == row['text'])
        audit_lines.append(f"| {row['source']} | {row['text']} | {row['target']} | {', '.join(evidence)} |")
    (qa / 'navigation-audit.md').write_text('\n'.join(audit_lines) + '\n')
    report = dict(
        pages=len(doc), main_pages=19, index_pages=1, backup_pages=10,
        links=len(links), contracts=len(contracts),
        semantic_mismatch=False, unreachable=[],
        original_png_sha256=originals,
        build=build_report)
    (qa / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    doc.close()
    print(f'PASS: 19 main + 1 index + 10 backup, {len(contracts)} semantic links.')


def montage(paths, dest, columns):
    images = [Image.open(path).convert('RGB') for path in paths]
    width, height = images[0].size
    rows = math.ceil(len(images) / columns)
    canvas = Image.new('RGB', (columns * width, rows * height), 'white')
    for index, image in enumerate(images):
        canvas.paste(image, ((index % columns) * width, (index // columns) * height))
    canvas.save(dest)


if __name__ == '__main__':
    main()
