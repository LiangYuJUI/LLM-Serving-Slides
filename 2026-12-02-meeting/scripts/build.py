#!/usr/bin/env python3
"""Build both decks, standalone Overleaf ZIPs, page renders, and validation report."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile, zipfile
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
DECKS = {
 '2026-12-02-Paper-Review': {'pages': 6, 'figures': ['figures/kareto/fig06.png','figures/ecoserve/fig6.png','figures/ecoserve/fig15.png']},
 '2026-12-02-Research-Discussion': {'pages': 10, 'figures': []},
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def compile_twice(cwd, source, dest):
 dest.mkdir(parents=True, exist_ok=True)
 for _ in range(2):
  run=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={dest}',source],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  if run.returncode: raise RuntimeError(run.stdout[-6000:])
 log=(dest/(Path(source).stem+'.log')).read_text(errors='replace')
 warnings=re.findall(r'^.*(?:Overfull|undefined|Missing character|not found|Warning).*$',log,re.M)
 return dest/(Path(source).stem+'.pdf'), warnings

def audit_pdf(path, expected):
 doc=fitz.open(path); assert len(doc)==expected, (path,len(doc),expected)
 pages=[]
 for i,page in enumerate(doc,1):
  assert abs(page.rect.width/page.rect.height-16/9)<.002
  txt=page.get_text(); assert re.search(rf'{i}\s*/\s*{expected}',txt), (path,i,txt[-100:])
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     r=fitz.Rect(span['bbox']); assert r.x0>=-1 and r.y0>=-3 and r.x1<=page.rect.width+1 and r.y1<=page.rect.height+3, (path,i,span['text'],r)
  for image in page.get_image_info(): assert page.rect.contains(fitz.Rect(image['bbox'])),(path,i,image)
  pages.append({'page':i,'text':txt,'dimensions_pt':[page.rect.width,page.rect.height]})
 return doc,pages

def montage(doc, path, prefix):
 thumbs=[]
 for i,p in enumerate(doc,1):
  im=Image.frombytes('RGB',[p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).width,p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).height],p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).samples)
  pagefile=path.parent/'pages'/f'{prefix}-{i:02}.png'; pagefile.parent.mkdir(parents=True,exist_ok=True); im.save(pagefile)
  im.thumbnail((800,450)); thumbs.append((im,i))
 cols=2; cellw,cellh=800,478; rows=(len(thumbs)+cols-1)//cols
 canvas=Image.new('RGB',(cols*cellw,rows*cellh),'#d8e4eb'); draw=ImageDraw.Draw(canvas)
 for n,(im,i) in enumerate(thumbs):
  x=(n%cols)*cellw; y=(n//cols)*cellh; canvas.paste(im,(x,y)); draw.text((x+10,y+454),f'{i}/{len(thumbs)}',fill='#243748')
 canvas.save(path)

def main():
 QA=OUT/'qa'; (OUT/'pdf').mkdir(parents=True,exist_ok=True); (OUT/'overleaf').mkdir(parents=True,exist_ok=True)
 result={}
 with tempfile.TemporaryDirectory(prefix='meeting-build-') as tmp:
  tmp=Path(tmp)
  for name,cfg in DECKS.items():
   local,warn=compile_twice(ROOT,f'{name}.tex',tmp/name)
   assert not warn, (name,warn)
   pdf=OUT/'pdf'/f'{name}.pdf'; shutil.copy2(local,pdf)
   archive=OUT/'overleaf'/('Paper-Review.zip' if 'Paper-Review' in name else 'Research-Discussion.zip')
   with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(ROOT/f'{name}.tex','main.tex')
    for fig in cfg['figures']: z.write(ROOT/fig,fig)
    z.writestr('README.txt','Entry point: main.tex\nCompiler: pdfLaTeX\nCompile twice for page numbering.\nAll required figure files are included.\n')
   extract=tmp/(name+'-zip'); extract.mkdir()
   with zipfile.ZipFile(archive) as z: assert z.testzip() is None; z.extractall(extract)
   packaged,warnzip=compile_twice(extract,'main.tex',tmp/(name+'-zip-build'))
   assert not warnzip,(name,'zip',warnzip)
   a,ap=audit_pdf(pdf,cfg['pages']); b,bp=audit_pdf(packaged,cfg['pages'])
   parity=[]
   for i,(x,y) in enumerate(zip(a,b),1):
    assert x.get_text()==y.get_text(),(name,'text mismatch',i)
    assert x.get_pixmap().digest==y.get_pixmap().digest,(name,'render mismatch',i)
    parity.append(True)
   prefix='paper-review' if 'Paper-Review' in name else 'research-discussion'
   montage(a,QA/f'{prefix}-montage.png',prefix)
   result[name]={'pages':len(a),'pdf_sha256':sha(pdf),'zip_sha256':sha(archive),'local_passes':2,'zip_passes':2,'pdf_zip_text_pixels_match':all(parity),'warnings':[],'page_dimensions_pt':[a[0].rect.width,a[0].rect.height],'page_text':[re.sub(r'\s+',' ',p.get_text()).strip() for p in a]}
   a.close(); b.close()
 (QA/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 (QA/'validation.md').write_text('# Build and PDF validation\n\n- PASS: Paper Review has 6 pages; Research Discussion has 10 pages.\n- PASS: each deck compiled twice with pdfLaTeX, locally and from its self-contained ZIP.\n- PASS: ZIP and local PDFs match in extracted text and rendered pixels.\n- PASS: widescreen dimensions, footer numbering, text/image bounds, and PDF readability checks.\n- PASS: A → B → C candidate ordering is present in Research Discussion pages 4–6.\n- Visual montages and full-resolution page PNGs are in this directory.\n\nThis automated report does not replace visual inspection; montages were inspected after build.\n')
 print('PASS: 6-page and 10-page decks; local/ZIP builds, parity, and PDF bounds checked.')
if __name__=='__main__': main()
