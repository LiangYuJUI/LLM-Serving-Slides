#!/usr/bin/env python3
"""Build and validate the independent summary; never writes Helix outputs.

Requires pdflatex and PyMuPDF. Run from any directory.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
STEM = '2026-11-04-Previous-Work-Research-Directions'
QA = ROOT / 'output/qa-previous-work'
INDEX = json.loads((ROOT / 'previous-work/index.json').read_text())


def compile_twice(directory, source, output):
    output.mkdir(parents=True)
    for _ in range(2):
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
             f'-output-directory={output}', source], cwd=directory,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout[-6000:])
    log = (output / (Path(source).stem + '.log')).read_text()
    issues = re.findall(r'^.*(?:Overfull|undefined|not found|Warning).*$', log, re.M)
    if issues:
        raise RuntimeError('\n'.join(issues))
    return output / (Path(source).stem + '.pdf')


def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower().replace('’', "'"))


def check(pdf):
    doc = fitz.open(pdf)
    mapping = INDEX['slides']
    assert len(doc) == len(mapping) == 22
    assert sum(x['type'] == 'paper' for x in mapping) == 13
    assert sum(x['type'] == 'category' for x in mapping) == 5
    coordinates = []
    forbidden = ['Source:', 'DOI:', 'Paper PDF', 'arXiv:', 'Key Insight', 'Experiments', 'Results', 'Conclusion',
                 'Carbon-Aware KV Cache Management for LLM Serving', 'Beyond Energy: Sustainability-Aware LLM Serving']
    for i, (page, info) in enumerate(zip(doc, mapping), 1):
        assert info['page'] == i
        assert abs(page.rect.width / page.rect.height - 16 / 9) < .001
        assert not page.get_links()
        text = page.get_text()
        assert normalize(info['title']) in normalize(text), (i, info['title'])
        assert not re.search(r'\b\d+\s*/\s*22\b', text)
        spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b
                 for line in b['lines'] for s in line['spans'] if s['text'].strip()]
        for span in spans:
            assert page.rect.contains(fitz.Rect(span['bbox'])), (i, span)
            assert span['bbox'][3] < page.rect.height - 8, (i, 'Bottom clearance', span)
        for j, first in enumerate(spans):
            for second in spans[j+1:]:
                overlap = fitz.Rect(first['bbox']) & fitz.Rect(second['bbox'])
                assert overlap.is_empty or overlap.width < .5 or overlap.height < .5, (i, first, second)
        if info['type'] == 'contents':
            assert i == 2
            counts = [sum(s.get('category') == c['id'] and s['type'] == 'paper'
                          for s in mapping) for c in INDEX['categories']]
            for category, count in zip(INDEX['categories'], counts):
                assert normalize(category['name'] + str(count)) in normalize(text)
            assert normalize('Total' + str(sum(counts))) in normalize(text)
        if info['type'] != 'paper':
            assert 'Motivation' not in text and 'Method' not in text
            continue
        assert all(label not in text for label in forbidden), i
        assert text.count('Motivation') == text.count('Method') == 1
        headings = [s for s in spans if s['text'] in ('Motivation', 'Method')]
        assert len(headings) == 2
        assert all('Bold' in s['font'] and s['color'] == 0x347E74 for s in headings)
        assert sum(s['text'].strip() == '•' for s in spans) == 6, i
        my, hy = [page.search_for(label)[0].y0 for label in ('Motivation', 'Method')]
        body = [s for s in spans if s['bbox'][1] > my]
        assert min(s['size'] for s in body) >= 9.9
        assert 35 < my < 65 and 120 < hy < 165
        coordinates.append({'page': i, 'motivation_y': my, 'method_y': hy})
        qualifiers = {'greencache': ['15.1%', '25.3%', 'Full Cache', '70B', 'France'],
                      'prism': ['50.2%', '12-region', 'WaterWise', 'operational-only'],
                      'characterizing': ['static power'], 'realgpu': ['experimental', 'uncalibrated'],
                      'hbmpower': ['36', 'HBM2', 'not HBF'], 'haven': ['retrieval', 'not LLM decode']}
        assert all(t in text for t in qualifiers.get(info['key'], [])), i
    assert max(x['motivation_y'] for x in coordinates) - min(x['motivation_y'] for x in coordinates) < .1
    assert max(x['method_y'] for x in coordinates) - min(x['method_y'] for x in coordinates) < .1
    return doc, coordinates


def main():
    # Hash every pre-existing file outside this deck, including uncommitted summary work.
    protected = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in ROOT.rglob('*') if p.is_file()
                 and 'previous-work' not in str(p).lower()
                 and 'previous_work' not in str(p).lower()}
    QA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='previous-work-') as tmp:
        temp = Path(tmp)
        built = compile_twice(ROOT, STEM + '.tex', temp / 'local')
        doc, coordinates = check(built)
        archive = ROOT / 'output/overleaf/Previous-Work-Research-Directions.zip'
        archive.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(ROOT / (STEM + '.tex'), 'main.tex')
            for module in sorted((ROOT / 'previous-work').glob('*.tex')):
                z.write(module, str(module.relative_to(ROOT)))
            z.writestr('README.txt', 'Main file: main.tex\nCompiler: pdfLaTeX\nCompile twice. No external assets required.\n')
        extracted = temp / 'overleaf'
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(extracted)
        standalone = compile_twice(extracted, 'main.tex', temp / 'standalone')
        other, _ = check(standalone)
        for i, (a, b) in enumerate(zip(doc, other), 1):
            assert a.get_text() == b.get_text()
            assert a.get_pixmap().digest == b.get_pixmap().digest
            assert a.get_links() == b.get_links()
            a.get_pixmap(matrix=fitz.Matrix(2.5, 2.5)).save(QA / f'page-{i}.png')
        destination = ROOT / 'output/pdf' / (STEM + '.pdf')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built, destination)
    assert all(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == h
               for p, h in protected.items()), 'A protected Helix artifact changed'
    from PIL import Image, ImageDraw
    for start in range(1, len(doc) + 1, 12):
        canvas = Image.new('RGB', (1600, 3 * 250), 'white')
        draw = ImageDraw.Draw(canvas)
        for page in range(start, min(start + 12, len(doc) + 1)):
            im = Image.open(QA / f'page-{page}.png')
            im.thumbnail((395, 225))
            x, y = ((page-start) % 4)*400, ((page-start)//4)*250
            canvas.paste(im, (x, y))
            draw.text((x+8, y+228), str(page), fill='black')
        canvas.save(QA / f'montage-{start:02d}.png')
    report = {'pages': len(doc), 'paper_pages': 13, 'category_covers': 5, 'local_pdflatex_passes': 2, 'zip_pdflatex_passes': 2,
              'final_logs_clean': True, 'standalone_pixels_text_links_identical': True,
              'external_link_annotations': 0, 'sections_per_summary': ['Motivation', 'Method'],
              'subtitles_sources_footers_absent': True, 'six_bullets_per_summary': True,
              'internal_links': 0, 'text_bounds_and_span_overlap': 'pass',
              'alignment': coordinates, 'protected_files_unchanged': len(protected),
              'visual_review': 'See REVIEW.md; not inferred from automatic checks.'}
    (QA / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: 22 pages, 13 papers, 5 category covers; local and extracted ZIP compiled twice; clean logs; identical text, pixels and links; existing decks unchanged.')


if __name__ == '__main__':
    main()
