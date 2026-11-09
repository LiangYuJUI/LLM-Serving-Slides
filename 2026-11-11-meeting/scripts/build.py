#!/usr/bin/env python3
"""Compile GreenCache twice, package the Overleaf ZIP, and compile that ZIP twice."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '2026-11-11-GreenCache.tex'
FIGDIR = ROOT / 'GreenCache-Research-Meeting-2026-11-11' / 'With-Caption'


def compile_twice(directory, source, output):
    output.mkdir(parents=True, exist_ok=True)
    for run in (1, 2):
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
             '-recorder', f'-output-directory={output}', source],
            cwd=directory, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / f'build-{run}.stdout').write_text(result.stdout)
        if result.returncode:
            raise RuntimeError(result.stdout[-8000:])
    log = (output / (Path(source).stem + '.log')).read_text(errors='replace')
    errors = re.findall(r'^.*(?:Overfull|undefined|not found|Warning).*$', log, re.M)
    if errors:
        raise RuntimeError('\n'.join(errors[:80]))
    return output / (Path(source).stem + '.pdf'), re.findall(r'^.*(?:Underfull|Overfull|undefined|Warning).*$', log, re.M)


def main():
    output = ROOT / 'output'
    with tempfile.TemporaryDirectory(prefix='greencache-build-') as tmp:
        temp = Path(tmp)
        pdf, local_warnings = compile_twice(ROOT, SOURCE.name, temp / 'local')
        (output / 'pdf').mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, output / 'pdf' / '2026-11-11-GreenCache.pdf')
        (output / 'overleaf').mkdir(parents=True, exist_ok=True)
        archive = output / 'overleaf' / 'GreenCache.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(SOURCE, 'main.tex')
            for image in sorted(FIGDIR.glob('*.png')):
                z.write(image, image.relative_to(ROOT).as_posix())
            z.writestr(
                'README.txt',
                'Main file: main.tex\nCompiler: pdfLaTeX\n'
                'Compile twice for navigation.\n'
                'Figures: 20 supplied With-Caption PNGs. Pixels are unchanged.\n')
        extracted = temp / 'overleaf'
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(extracted)
        standalone, zip_warnings = compile_twice(extracted, 'main.tex', extracted / 'build')
        import pymupdf as fitz
        local, remote = fitz.open(pdf), fitz.open(standalone)
        assert len(local) == len(remote)
        for index, (a, b) in enumerate(zip(local, remote), start=1):
            assert a.get_text() == b.get_text(), index
            assert a.get_pixmap().digest == b.get_pixmap().digest, index
            assert [(x.get('nameddest'), x.get('page')) for x in a.get_links()] == [
                (x.get('nameddest'), x.get('page')) for x in b.get_links()], index
        # Match click geometry and the visible text covered by each annotation too.
        def annotations(page):
            return [(x.get('nameddest'), x.get('page'), tuple(x['from']),
                     page.get_textbox(x['from'])) for x in page.get_links()]
        assert all(annotations(a) == annotations(b) for a, b in zip(local, remote))
        pages = len(local)
        qa = output / 'qa'
        qa.mkdir(parents=True, exist_ok=True)
        report = dict(pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                      zip_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                      source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      local_passes=2, standalone_zip_passes=2, pages=pages,
                      parity=dict(text=True, pixels=True, destinations=True, annotation_rectangles=True, annotation_text=True),
                      local_warnings=local_warnings, standalone_zip_warnings=zip_warnings)
        (qa / 'build-validation.json').write_text(json.dumps(report, indent=2) + '\n')
        local.close()
        remote.close()
        print(f'PASS: local 2 passes; extracted ZIP 2 passes; {pages} identical rendered pages.')


if __name__ == '__main__':
    main()
