#!/usr/bin/env python3
"""Build twice, package only required inputs, and compile the extracted ZIP twice."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '2026-11-04-Helix.tex'


def compile_twice(directory, source, output):
    output.mkdir(parents=True, exist_ok=True)
    for run in (1, 2):
        result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                                 '-recorder', f'-output-directory={output}', source],
                                cwd=directory, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        (output / f'build-{run}.stdout').write_text(result.stdout)
        if result.returncode:
            raise RuntimeError(result.stdout[-5000:])
    log = (output / (Path(source).stem + '.log')).read_text()
    errors = re.findall(r'^.*(?:Overfull|undefined|not found|Warning).*$' , log, re.M)
    if errors:
        raise RuntimeError('\n'.join(errors))
    return output / (Path(source).stem + '.pdf')


def main():
    output = ROOT / 'output'
    # Keep build intermediates outside the versioned output directory.
    with tempfile.TemporaryDirectory(prefix='helix-build-') as tmp:
        temp = Path(tmp)
        pdf = compile_twice(ROOT, SOURCE.name, temp / 'local')
        (output / 'pdf').mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, output / 'pdf' / pdf.name)
        (output / 'overleaf').mkdir(parents=True, exist_ok=True)
        archive = output / 'overleaf' / 'Helix.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(SOURCE, 'main.tex')
            for image in sorted((ROOT / 'Helix' / 'Without-Caption').glob('*.png')):
                z.write(image, image.relative_to(ROOT))
            z.writestr('README.txt', 'Main file: main.tex\nCompiler: pdfLaTeX\nCompile twice for navigation.\nFigures: supplied Helix/Without-Caption PNGs, unchanged.\n')
        extracted = temp / 'overleaf'
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(extracted)
        standalone = compile_twice(extracted, 'main.tex', extracted / 'build')
        # Compare page content, navigation and rendered pixels, independent of PDF metadata.
        import pymupdf as fitz
        local, remote = fitz.open(pdf), fitz.open(standalone)
        assert len(local) == len(remote)
        for a, b in zip(local, remote):
            assert a.get_text() == b.get_text()
            assert a.get_pixmap().digest == b.get_pixmap().digest
            assert [(x.get('nameddest'), x.get('page')) for x in a.get_links()] == [
                (x.get('nameddest'), x.get('page')) for x in b.get_links()]
        pages = len(local)
        local.close()
        remote.close()
        print(f'PASS: local 2 passes; extracted ZIP 2 passes; {pages} identical rendered pages.')


if __name__ == '__main__':
    main()
