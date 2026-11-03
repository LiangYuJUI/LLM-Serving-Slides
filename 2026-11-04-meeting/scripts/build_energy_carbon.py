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
STEM = '2026-11-04-Energy-Carbon-Summary'
QA = ROOT / 'output/qa-energy-carbon'
URLS = [
    set(),
    {'https://doi.org/10.1145/3788087', 'https://arxiv.org/pdf/2505.23970v3',
     'https://greencache.persistentmemory.org'},
    {'https://arxiv.org/abs/2609.35569', 'https://arxiv.org/pdf/2609.35569'},
]


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


def check(pdf):
    doc = fitz.open(pdf)
    assert len(doc) == 3, 'Expected cover plus two summary pages'
    coordinates = []
    for index, page in enumerate(doc):
        assert abs(page.rect.width / page.rect.height - 16 / 9) < .001
        links = page.get_links()
        assert {link.get('uri') for link in links} == URLS[index]
        assert all(link['kind'] == fitz.LINK_URI for link in links)
        text = page.get_text()
        assert 'Discussion' not in text
        assert f'{index+1} / 3' in text
        spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b
                 for line in b['lines'] for s in line['spans'] if s['text'].strip()]
        for span in spans:
            assert page.rect.contains(fitz.Rect(span['bbox'])), span
        if index == 0:
            assert 'GreenCache and PRISM' in text
            continue
        labels = ['Motivation', 'Key Insight', 'Method', 'Experiments', 'Results', 'Conclusion']
        assert all(text.count(label) == 1 for label in labels)
        source_y = page.search_for('Source:')[0].y0
        footer_y = page.search_for('Power-, Energy-, and Carbon-Aware')[0].y0
        source_spans = [s for s in spans if source_y - 1 <= s['bbox'][1] < footer_y - 1]
        assert max(s['bbox'][3] for s in source_spans) < footer_y
        body_spans = [s for s in spans if 40 < s['bbox'][1] < source_y - 1]
        assert max(s['bbox'][3] for s in body_spans) < source_y
        coordinates.append({'source_y': source_y, 'footer_y': footer_y})
    assert abs(coordinates[0]['source_y'] - coordinates[1]['source_y']) < .5, coordinates
    assert coordinates[0]['footer_y'] == coordinates[1]['footer_y']
    return doc, coordinates


def main():
    protected = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in ROOT.rglob('*') if p.is_file()
                 and (('Helix' in str(p)) or ('output/qa/' in str(p))
                      or p.name in ('build.py', 'validate.py'))}
    QA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='energy-carbon-') as tmp:
        temp = Path(tmp)
        built = compile_twice(ROOT, STEM + '.tex', temp / 'local')
        doc, coordinates = check(built)
        archive = ROOT / 'output/overleaf/Energy-Carbon-Summary.zip'
        archive.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(ROOT / (STEM + '.tex'), 'main.tex')
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
    report = {'pages': 3, 'local_pdflatex_passes': 2, 'zip_pdflatex_passes': 2,
              'final_logs_clean': True, 'standalone_pixels_text_links_identical': True,
              'external_link_annotations': [sorted(urls) for urls in URLS],
              'internal_links': 0, 'text_bounds_and_source_footer_separation': 'pass',
              'alignment': coordinates, 'protected_files_unchanged': len(protected),
              'visual_review': 'See REVIEW.md; not inferred from automatic checks.'}
    (QA / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: 3 pages; local and extracted ZIP compiled twice; clean logs; identical text, pixels and links; Helix unchanged.')


if __name__ == '__main__':
    main()
