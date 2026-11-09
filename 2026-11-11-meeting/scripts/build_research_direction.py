#!/usr/bin/env python3
"""Build only Research Direction; validate extracted ZIP and preserve existing files.
Dependencies: pdfLaTeX, PyMuPDF, Pillow. Run with Python 3.
"""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile, zipfile
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
NAME = '2026-11-11-Research-Direction'
OUT = ROOT / 'output'
QA = OUT / 'qa'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def protected():
    return {str(p.relative_to(ROOT)): digest(p) for p in ROOT.rglob('*')
            if p.is_file() and 'research-direction' not in str(p).lower()
            and 'research_direction' not in str(p).lower() and p.name != 'README.md'}
def compile_pdf(cwd, source, output):
    output.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        r = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
                            f'-output-directory={output}',source],cwd=cwd,
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        if r.returncode: raise RuntimeError(r.stdout[-6000:])
    log = (output / (Path(source).stem + '.log')).read_text()
    warnings = re.findall(r'^.*(?:Overfull|Underfull|undefined|Warning|Missing character|not found).*$',log,re.M)
    if warnings: raise RuntimeError('\n'.join(warnings))
    return output / (Path(source).stem+'.pdf')
def validate(doc):
    assert len(doc)==7
    assert "Disaggregated MoE Serving" in doc[0].get_text()
    assert "Research Direction |" not in doc[0].get_text()
    for i,p in enumerate(doc):
        text=p.get_text()
        if i: assert re.search(rf'Research Direction\s*\|\s*{i}\s*/\s*6',text), text
        assert not re.search(r'Discussion Index|Back to Main|Backup',text,re.I)
        assert abs(p.rect.width/p.rect.height-16/9)<.001
        for block in p.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    r=fitz.Rect(span['bbox'])
                    assert r.x0>=-1 and r.y0>=-1 and r.x1<=p.rect.width+1 and r.y1<=p.rect.height+1, span
        assert not any(x['kind']==fitz.LINK_GOTO for x in p.get_links())
    assert 'Hypothesis to evaluate' in doc[3].get_text()
    assert 'November 18, 2026' in doc[5].get_text() and 'MemExplorer' in doc[5].get_text()
    assert 'Related Work Comparison Matrix' in doc[6].get_text()
    assert all(x in doc[6].get_text() for x in ['Helix','ThunderServe','Hetis','Tessera','GreenCache','Janus','Carbon','LLMServingSim','HBFSim','MemExplorer','Characterizing HBF','Potential Applications'])
def main():
    before=protected()
    for p in [OUT/'pdf',OUT/'overleaf',QA/'research-direction-pages']:p.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research-direction-') as td:
        tmp=Path(td)
        pdf=compile_pdf(ROOT,NAME+'.tex',tmp/'build')
        archive=OUT/'overleaf'/'Research-Direction.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(ROOT/(NAME+'.tex'),'main.tex')
            z.writestr('README.txt','Main document: main.tex\nCompiler: pdfLaTeX\nCompile twice. Unnumbered cover plus six content slides. No external assets.\n')
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(tmp/'extracted')
        other=compile_pdf(tmp/'extracted','main.tex',tmp/'zip-build')
        a,b=fitz.open(pdf),fitz.open(other)
        validate(a);validate(b)
        for x,y in zip(a,b):
            assert x.get_text()==y.get_text()
            assert x.get_pixmap().digest==y.get_pixmap().digest
            assert [(k.get('uri'),tuple(k['from'])) for k in x.get_links()]==[(k.get('uri'),tuple(k['from'])) for k in y.get_links()]
        images=[]
        for n,p in enumerate(a,1):
            pix=p.get_pixmap(matrix=fitz.Matrix(2.5,2.5))
            dest=QA/'research-direction-pages'/f'slide-{n}.png';pix.save(dest)
            im=Image.open(dest).convert('RGB');im.thumbnail((800,450))
            images.append(im)
        montage=Image.new('RGB',(1600,1880),'#D8E4EB')
        for n,im in enumerate(images):
            x=(n%2)*800;y=(n//2)*470
            montage.paste(im,(x,y));ImageDraw.Draw(montage).text((x+12,y+452),('Cover' if n == 0 else f'{n}/6'),fill='#243748')
        montage.save(QA/'research-direction-montage.png')
        shutil.copy2(pdf,OUT/'pdf'/(NAME+'.pdf'))
    assert before==protected(), 'Existing artifacts changed'
    report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'pages':7,'content_slides':6,'unnumbered_cover':True,'local_passes':2,'extracted_zip_passes':2,'warnings':[],
            'zip_parity':{'text':True,'pixels':True,'links':True},
            'page_numbering':'Unnumbered cover; content 1/6 through 6/6','existing_files_preserved':len(before),
            'pdf_sha256':digest(OUT/'pdf'/(NAME+'.pdf')),'zip_sha256':digest(archive)}
    (QA/'research-direction-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
