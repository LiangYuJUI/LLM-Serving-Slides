#!/usr/bin/env python3
"""Standalone Beamer build + automated QA. Requires pdflatex, PyMuPDF, Pillow.
Run from any directory: python3 path/to/build_research_materials.py.
Only this deck's PDF, research-materials PNGs, and validation.md are written.
"""
from pathlib import Path
import hashlib, re, shutil, subprocess, tempfile
import pymupdf as fitz
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
NAME = '2026-11-18-Research-Materials'
QA = ROOT/'output/qa'
PDF = ROOT/'output/pdf'/f'{NAME}.pdf'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def protected():
    return {str(p.relative_to(REPO)): digest(p) for p in REPO.rglob('*')
            if p.is_file() and '.git' not in p.parts
            and p != PDF and p != QA/'validation.md'
            and not (p.parent == QA/'pages' and p.name.startswith('research-materials-'))
            and p != QA/'research-materials-montage.png'}
def compile_pdf(cwd, out):
    out.mkdir(parents=True)
    for _ in range(2):
        run = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
            f'-output-directory={out}',NAME+'.tex'],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if run.returncode: raise RuntimeError(run.stdout[-8000:])
    log=(out/f'{NAME}.log').read_text()
    warnings=re.findall(r'^.*(?:Overfull|Underfull|undefined|Warning|Missing character|not found).*$',log,re.M)
    if warnings: raise RuntimeError('\n'.join(warnings))
    return out/f'{NAME}.pdf'
def validate(doc):
    total=len(doc)-1
    assert total == 5, 'Update content contract when intentionally extending this deck'
    assert 'Research Materials |' not in doc[0].get_text()
    assert 'November 18, 2026' in doc[0].get_text()
    uris=set()
    for i,p in enumerate(doc):
        t=p.get_text()
        if i: assert re.search(rf'Research Materials\s*\|\s*{i}\s*/\s*{total}',t), t
        assert abs(p.rect.width/p.rect.height-16/9)<.001
        links=[l for l in p.get_links() if l.get('uri')]
        assert links, f'No source URI on page {i+1}'
        uris.update(l['uri'] for l in links)
        for b in p.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line['spans']:
                    r=fitz.Rect(span['bbox'])
                    assert r.x0>=0 and r.y0>=0 and r.x1<=p.rect.width and r.y1<=p.rect.height, span
    assert 'https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf' in uris, uris
    for v in ['13.52','19.81','20.6','225.9','16 GB','24 GB','36 GB','512 GiB','16.7']:
        assert v in doc[2].get_text(),v
    for v in ['0.845','0.825','0.572','0.441','47.8','nominal capacity unit','Not a verified per-GiB']:
        assert v in doc[3].get_text(),v
    assert round(225.9/13.52,1)==16.7
    assert round(100*(1-(225.9/512)/(13.52/16)),1)==47.8
    assert 'Power-Aware HBM/HBF Co-Design' in doc[5].get_text()
    assert 'Published REEL LCI v1.0 screening estimates' in doc[2].get_text()
    assert 'Nominal normalization: divide' in doc[3].get_text()
    assert 'Conceptual proposed architecture' in doc[5].get_text()
    return sorted(uris)
def main():
    before=protected()
    (QA/'pages').mkdir(parents=True,exist_ok=True)
    PDF.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research-materials-') as td:
        temp=Path(td)
        local=compile_pdf(ROOT,temp/'local')
        isolated=temp/'isolated';isolated.mkdir()
        shutil.copy2(ROOT/f'{NAME}.tex',isolated)
        other=compile_pdf(isolated,temp/'standalone')
        a,b=fitz.open(local),fitz.open(other)
        uris=validate(a);validate(b)
        for x,y in zip(a,b):
            assert x.get_text()==y.get_text()
            assert x.get_pixmap().digest==y.get_pixmap().digest
            assert [(l.get('uri'),tuple(l['from'])) for l in x.get_links()]==[(l.get('uri'),tuple(l['from'])) for l in y.get_links()]
        montage=Image.new('RGB',(1600,1410),'#D8E4EB')
        for n,page in enumerate(a):
            dest=QA/'pages'/f'research-materials-{n+1:02d}.png'
            page.get_pixmap(matrix=fitz.Matrix(3,3)).save(dest)
            im=Image.open(dest).convert('RGB');im.thumbnail((800,450))
            x=(n%2)*800;y=(n//2)*470
            montage.paste(im,(x,y));ImageDraw.Draw(montage).text((x+12,y+452),'Cover' if n==0 else f'{n}/5',fill='#243748')
        montage.save(QA/'research-materials-montage.png')
        shutil.copy2(local,PDF)
    assert before==protected(),'Existing files changed'
    report=f'''# Research Materials validation\n\n- Build base HEAD: `{subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()}`\n- PASS: 2 local + 2 isolated pdfLaTeX passes, source-only standalone build.\n- PASS: no TeX warnings, undefined references/citations, missing characters or overfull/underfull boxes.\n- PASS: 6 pages, 16:9, unnumbered cover, content 1/5 through 5/5.\n- PASS: text stays within page bounds; every page has clickable external source links.\n- PASS: local/isolated text, rendered pixels and URI annotations match.\n- PASS: numeric labels, source capacity labels, 16.7x and 47.8% formulas.\n- PASS: all {len(before)} protected files retain SHA-256 hashes during build.\n- Rendered: six PNGs at 3x resolution plus 2-column montage.\n- PDF SHA-256: `{digest(PDF)}`\n- Visual review: pending human/agent inspection of the generated PNGs.\n\n## External URI targets verified in PDF\n\n'''+''.join(f'- {u}\n' for u in uris)
    (QA/'validation.md').write_text(report)
    print(report)
if __name__=='__main__':main()
