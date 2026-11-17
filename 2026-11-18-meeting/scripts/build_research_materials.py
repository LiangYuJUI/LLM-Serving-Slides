#!/usr/bin/env python3
"""Build Research Materials twice locally and from its Overleaf ZIP; validate and render."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile, zipfile
import pymupdf as fitz
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
NAME = '2026-11-18-Research-Materials'
QA = ROOT/'output/qa'
PDF = ROOT/'output/pdf'/f'{NAME}.pdf'
ZIP = ROOT/'output/overleaf/Research-Materials.zip'
FIGURE = Path('CarbonSLO-GeoDistributed-LLM-Serving-2026/With-Caption/CarbonSLO_Fig02.png')
LABELS = ['EINDEX','GPU','MEMORY','PLACEMENT','PLACEMENTENERGY','GEO','RELATED','ACCOUNT','REEL1','REEL2','REEL3','REEL4','DISAGG','NEXT','REELABOUT','MEMORYSOURCES','THANKYOU']
CATEGORIES = {'GPU':2, 'MEMORY':3, 'GEO':6, 'ACCOUNT':8, 'DISAGG':13}
ORIGINAL_REEL_TITLES = {'HBM/HBF Embodied Carbon Evidence': 'What Evidence Do We Have for HBM/HBF Embodied Carbon?', 'Embodied Carbon per Memory Stack': 'How Much Embodied Carbon Does One Stack Carry?', 'Embodied Carbon per Nominal Capacity Unit': 'Does HBF Reduce Embodied Carbon per Unit Capacity?', 'HBF Carbon Estimate: Assumptions and Limitations': 'Can We Trust the HBF Carbon Estimate?'}
# REEL1–4 baselines include user-requested concise copy updates.
PRESERVED = {'REEL1': 'a48e62133c24df47d87ca15285fc999607b32e1ee2b5933999f2570035c1bbd3', 'REEL2': '893e24ef3c3b3dc2d50e559402ce0ff48e0243a0fd4d36627d20ad8a3cb59965', 'REEL3': '1fc3a6cce4ab8ec2c99130ad8e3d17ce2eb1ecf5367dff6c2dfa5643e739eb09', 'REEL4': 'e8bc4a53e7f5c755c1b4bb33ab1f4b03ea8be635ef1d5701c01944af2a7139fe'}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def protected():
    return {str(p.relative_to(REPO)): digest(p) for p in REPO.rglob('*')
            if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts
            and p not in (PDF, ZIP, QA/'validation.md', QA/'research-materials-build.json', QA/'research-materials-montage.png')
            and not (p.parent == QA/'pages' and p.name.startswith('research-materials-'))}

def compile_pdf(cwd, out, name):
    out.mkdir(parents=True)
    for _ in range(2):
        run = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
            f'-output-directory={out}',name+'.tex'],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if run.returncode: raise RuntimeError(run.stdout[-8000:])
    log=(out/f'{name}.log').read_text()
    warnings=re.findall(r'^.*(?:Overfull|Underfull|undefined|Warning|Missing character|not found).*$',log,re.M)
    if warnings: raise RuntimeError('\n'.join(warnings))
    return out/f'{name}.pdf'

def annotations(p):
    return [(x.get('uri'),x.get('nameddest'),x.get('page'),tuple(x['from'])) for x in p.get_links()]

def validate(doc):
    assert len(doc)==18
    assert doc.resolve_names()['COVER']['page']==0
    assert 'Thank you' in doc[-1].get_text()
    names=doc.resolve_names()
    for i,label in enumerate(LABELS,1): assert names[label]['page']==i,(label,names[label])
    for target,page in CATEGORIES.items():
        links=[x for x in doc[1].get_links() if x.get('nameddest')==target]
        assert len(links)==1 and links[0]['page']==page,(target,links)
        assert target in names
        assert links[0]['from'].width>doc[1].rect.width*.9, 'Card must be clickable across its width'
    uris=set()
    for i,p in enumerate(doc):
        t=p.get_text()
        assert re.search(rf'Research Materials\s*\|\s*{i+1}\s*/\s*18',t),t
        if i:
            back=[x for x in p.get_links() if x.get('nameddest')=='EINDEX']
            assert len(back)==1 and back[0]['page']==1
            assert 'Back to Evidence Index' in p.get_textbox(back[0]['from'])
        assert abs(p.rect.width/p.rect.height-16/9)<.001
        links=[l for l in p.get_links() if l.get('uri')]
        if i < 17: assert links, f'No source URI on page {i+1}'
        uris.update(l['uri'] for l in links)
        for b in p.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line['spans']:
                    r=fitz.Rect(span['bbox'])
                    assert r.x0>=0 and r.y0>=0 and r.x1<=p.rect.width and r.y1<=p.rect.height,span
        for im in p.get_image_info(): assert p.rect.contains(fitz.Rect(im['bbox']))
    assert any(x.get('uri') == 'https://reellci.com/insights/the-hbf-inversion.html'
               and 'REEL LCI v1.0' in doc[9].get_textbox(x['from'])
               for x in doc[9].get_links()), 'REEL title source hyperlink missing'
    assert any(x.get('nameddest')=='REELABOUT' and x.get('page')==15 for x in doc[9].get_links()), 'REEL supplement link missing'
    assert any(x.get('nameddest')=='REEL1' and x.get('page')==9 for x in doc[15].get_links()), 'REEL supplement return missing'
    for value in ['Repository of Electronics Environmental Line-items', 'Life cycle inventory', 'Jonathan Balsvik', '520 datasets', '18 categories', 'Circa', 'https://reellci.com/']:
        assert value in doc[15].get_text(),value
    assert any(x.get('nameddest')=='MEMORYSOURCES' and x.get('page')==16 for x in doc[3].get_links()), 'Memory source supplement link missing'
    assert any(x.get('nameddest')=='MEMORY' and x.get('page')==3 for x in doc[16].get_links()), 'Memory source return missing'
    for p in doc:
        for link in p.get_links():
            if link.get('nameddest'):
                assert link['nameddest'] in names and link['page']==names[link['nameddest']]['page']
    assert doc[2].get_images(), 'Original power figure missing'
    for page,values in {10:['13.52','19.81','20.6','225.9','16 GB','24 GB','36 GB','512 GiB','16.7'],11:['0.845','0.825','0.572','0.441','47.8','nominal capacity unit','not verified per-GiB results'],5:['9.11','7.19','9.54','32.7','static/background'],14:['RQ1','RQ2','RQ3','Request/session']}.items():
        for value in values: assert value in doc[page].get_text(), (page,value)
    required_by_label = {
        'MEMORY': ['24', '375', '1,000', '250', '3.4', '6.8', '100,000', 'P/E'],
        'PLACEMENT': ['11,354', '4,543', '4,538', '60%', 'not an equal-hardware comparison'],
        'GEO': ['Global Provisioner', 'Periodically polls DCs', 'broadcasts global snapshot',
                'Operational Carbon Only', 'No allocated embodied carbon.',
                'Independent Regional Decisions', 'same snapshot', '10.3%', '19.4%',
                'Facility MILP', 'Llama-3.1-8B', 'Same total inference engines', 'evaluated topology',
                'Figure 6(c)', 'high load', 'not a universal outcome', 'Our direction:', 'not yet validated',
                'GPU provisioning', 'hardware configuration', 'lifetime allocation'],
        'MEMORYSOURCES': ['Micron', 'Lenovo', 'Ma & Patterson', 'Moon', 'MemExplorer',
                          'Son', 'SSD', '100,000', 'device power ratio'],
    }
    for label, values in required_by_label.items():
        text = ' '.join(doc[names[label]['page']].get_text().split())
        for value in values:
            assert value in text, (label, value)
    assert round(100*(9.54/7.19-1),1)==32.7
    assert round(225.9/13.52,1)==16.7
    assert round(100*(1-(225.9/512)/(13.52/16)),1)==47.8
    return sorted(uris)

def main():
    before=protected()
    source=(ROOT/f'{NAME}.tex').read_text()
    frame_titles=re.findall(r'\\begin\{frame\}\[[^]]+\]\{([^}]+)\}',source)
    assert len(frame_titles)==16 and all('?' not in title or title == 'Where Do the HBM/HBF Memory Parameters Come From?' for title in frame_titles), 'Unexpected question-style slide title remains'
    for label,expected in PRESERVED.items():
        frame=re.search(r'\\begin\{frame\}\[t,label='+label+r'\](.*?)\\end\{frame\}',source,re.S).group(1)
        # Normalize authorized title edits and source/supplement navigation only.
        for current, original in ORIGINAL_REEL_TITLES.items():
            if frame.startswith('{'+current+'}'):
                frame='{'+original+'}'+frame[len(current)+2:]
        frame=frame.replace(r'\hfill\hyperlink{REELABOUT}{\scriptsize About REEL / LCI}', '')
        frame=frame.replace(r'\href{\srcA}{REEL LCI v1.0}', 'REEL LCI v1.0')
        assert hashlib.sha256(frame.encode()).hexdigest()==expected,('Preserved frame changed',label)
    baseline=json.loads((QA/'research-materials-frame-baseline.json').read_text())
    frames={label:frame for frame,label in re.findall(r'(\\begin\{frame\}\[[^]]*label=([^,\]]+)[^]]*\].*?\\end\{frame\})',source,re.S)}
    assert set(frames)-{'GEO'}==set(baseline['sha256'])
    for label,expected in baseline['sha256'].items():
        assert hashlib.sha256(frames[label].encode()).hexdigest()==expected, ('Unrelated frame changed',label)
    (QA/'pages').mkdir(parents=True,exist_ok=True);ZIP.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research-materials-') as td:
        temp=Path(td);local=compile_pdf(ROOT,temp/'local',NAME)
        with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(ROOT/f'{NAME}.tex','main.tex');z.write(ROOT/FIGURE,FIGURE.as_posix())
            z.writestr('README.txt','Main file: main.tex\nCompiler: pdfLaTeX\nCompile twice for numbering and navigation.\nOriginal Carbon--SLO Fig. 2 included unchanged.\n')
        isolated=temp/'isolated'
        with zipfile.ZipFile(ZIP) as z: assert z.testzip() is None;z.extractall(isolated)
        other=compile_pdf(isolated,temp/'standalone','main')
        a,b=fitz.open(local),fitz.open(other)
        uris=validate(a);validate(b)
        for x,y in zip(a,b):
            assert x.get_text()==y.get_text()
            assert x.get_pixmap().digest==y.get_pixmap().digest
            assert annotations(x)==annotations(y)
        montage=Image.new('RGB',(1600,4230),'#D8E4EB')
        for n,page in enumerate(a):
            dest=QA/'pages'/f'research-materials-{n+1:02d}.png'
            page.get_pixmap(matrix=fitz.Matrix(3,3)).save(dest)
            im=Image.open(dest).convert('RGB');im.thumbnail((800,450))
            x=(n%2)*800;y=(n//2)*470
            montage.paste(im,(x,y));ImageDraw.Draw(montage).text((x+12,y+452),f'{n+1}/18',fill='#243748')
        montage.save(QA/'research-materials-montage.png');shutil.copy2(local,PDF)
    assert before==protected(),'Protected files changed during build'
    report=dict(pages=18,local_passes=2,zip_passes=2,warnings=[],source_sha256=digest(ROOT/f'{NAME}.tex'),pdf_sha256=digest(PDF),zip_sha256=digest(ZIP),preserved_frame_hashes=PRESERVED,category_destinations={k:v+1 for k,v in CATEGORIES.items()},return_links=17,parity={'text':True,'pixels':True,'annotations':True},protected_files=len(before),uris=uris)
    (QA/'research-materials-build.json').write_text(json.dumps(report,indent=2)+'\n')
    (QA/'validation.md').write_text('''# Research Materials validation\n\n- PASS: 18 widescreen PDF pages; slide numbers match PDF pages, 1/18–18/18; final Thank you page.\n- PASS: two local and two extracted Overleaf ZIP pdfLaTeX passes; no layout/reference warnings.\n- PASS: local/ZIP text, pixels, source URI and named-destination annotations match.\n- PASS: five full-card index links land on PDF pages 3, 4, 7, 9, 14; 17 visible return links land on page 2.\n- PASS: text/image bounds, source hyperlinks on every evidence page, required numeric claims and calculations.\n- PASS: REEL1–4 concise frame bodies match frozen SHA-256 values exactly; authorized titles, frame labels, footer and slide 9 source/supplement hyperlinks normalized; previously authorized REEL copy and caveat removal included in baselines.\n- PASS: protected repository files unchanged during build.\n- Rendered all 18 pages at 3x resolution and a two-column montage.\n- Visual review: pending inspection of current generated PNGs.\n- Detailed checksums: `research-materials-build.json`.\n- External URL availability: see `research-materials-url-checks.json`; HTTP availability is separate from PDF annotation validity.\n\n## Source hyperlink targets\n\n'''+''.join(f'- {u}\n' for u in uris))
    print('PASS: 18 pages; warning-free local/ZIP builds; navigation and preserved-content checks.')
if __name__=='__main__':main()
