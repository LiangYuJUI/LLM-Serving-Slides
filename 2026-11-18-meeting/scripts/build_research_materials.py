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
LABELS = ['EINDEX','GEO','RELATED','HELIX','THUNDER','WORKLOAD','ACCOUNT','MEMORY','PLACEMENT','PLACEMENTENERGY','DISAGG','GEOARCH','ENVIRONMENT','NEXT','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES']
CATEGORIES = {'GEO':2, 'WORKLOAD':6, 'DISAGG':11, 'ENVIRONMENT':13}
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
    assert len(doc)==22
    assert doc.resolve_names()['COVER']['page']==0
    assert 'Thank you' in doc[15].get_text()
    names=doc.resolve_names()
    for i,label in enumerate(LABELS,1): assert names[label]['page']==i,(label,names[label])
    for target,page in CATEGORIES.items():
        links=[x for x in doc[1].get_links() if x.get('nameddest')==target and x['from'].width>doc[1].rect.width*.9]
        assert len(links)==1 and links[0]['page']==page,(target,links)
        assert target in names
        assert links[0]['from'].width>doc[1].rect.width*.9, 'Card must be clickable across its width'
    uris=set()
    for i,p in enumerate(doc):
        t=p.get_text()
        assert re.search(rf'Research Materials\s*\|\s*{i+1}\s*/\s*22',t),t
        assert 'Back to Evidence Index' not in t
        assert abs(p.rect.width/p.rect.height-16/9)<.001
        links=[l for l in p.get_links() if l.get('uri')]
        if i not in (0,15): assert links, f'No source URI on page {i+1}'
        uris.update(l['uri'] for l in links)
        for b in p.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line['spans']:
                    r=fitz.Rect(span['bbox'])
                    assert r.x0>=0 and r.y0>=0 and r.x1<=p.rect.width and r.y1<=p.rect.height,span
        for im in p.get_image_info(): assert p.rect.contains(fitz.Rect(im['bbox']))
    assert any(x.get('uri') == 'https://reellci.com/insights/the-hbf-inversion.html'
               and 'REEL LCI v1.0' in doc[16].get_textbox(x['from'])
               for x in doc[16].get_links()), 'REEL title source hyperlink missing'
    assert any(x.get('nameddest')=='REELABOUT' and x.get('page')==20 for x in doc[16].get_links()), 'REEL supplement link missing'
    assert any(x.get('nameddest')=='REEL1' and x.get('page')==16 for x in doc[20].get_links()), 'REEL supplement return missing'
    for value in ['Repository of Electronics Environmental Line-items', 'Life cycle inventory', 'Jonathan Balsvik', '520 datasets', '18 categories', 'Circa', 'https://reellci.com/']:
        assert value in doc[20].get_text(),value
    assert any(x.get('nameddest')=='MEMORYSOURCES' and x.get('page')==21 for x in doc[8].get_links()), 'Memory source supplement link missing'
    assert any(x.get('nameddest')=='MEMORY' and x.get('page')==8 for x in doc[21].get_links()), 'Memory source return missing'
    for p in doc:
        for link in p.get_links():
            if link.get('nameddest'):
                assert link['nameddest'] in names and link['page']==names[link['nameddest']]['page']
    for page,values in {17:['13.52','19.81','20.6','225.9','16 GB','24 GB','36 GB','512 GiB','16.7'],18:['0.845','0.825','0.572','0.441','47.8','nominal capacity unit','not verified per-GiB results'],10:['9.11','7.19','9.54','32.7','static/background'],14:['GPU Profiling and Simulator Calibration','Workload-Aware HBM/HBF Co-Design','Cross-DC Carbon-Aware Scheduling']}.items():
        for value in values: assert value in doc[page].get_text(), (page,value)
    required_by_label = {
        'MEMORY': ['24', '375', '1,000', '250', '3.4', '6.8', '100,000', 'P/E'],
        'PLACEMENT': ['11,354', '4,543', '4,538', '60%', 'not an equal-hardware comparison'],
        'GEO': ['Global Provisioner', 'Periodically polls DCs', 'broadcasts global snapshot',
                'Operational Carbon Only', 'No allocated embodied carbon.',
                'Independent Regional Decisions', 'same snapshot', 'Single GPU Type: A100', 'workload-aware GPU/memory costs', 'Our direction:'],
        'MEMORYSOURCES': ['Micron', 'Lenovo', 'Ma & Patterson', 'Moon', 'MemExplorer',
                          'Son', 'SSD', '100,000', 'device power ratio'],
    }
    for label, values in required_by_label.items():
        text = ' '.join(doc[names[label]['page']].get_text().split())
        for value in values:
            assert value in text, (label, value)
    new_required = {
        'HELIX': ['Serving Large Language Models over Heterogeneous GPUs and Network via Max-Flow','Max-flow graph + MILP','throughput objective','Real-system evidence','Simulation evidence'],
        'THUNDER': ['High-Performance and Cost-Efficient LLM Serving in Cloud Environments','LLaMA-30B','Table 3','Coding','Conversation','Replica counts, not physical GPU counts'],
        'WORKLOAD': ['Reported behavior above; proposed research implications below','Coding / Long-Prompt','Conversation / Long-Output','Multi-Turn / Agentic','Implications to evaluate','Categories can overlap'],
        'ACCOUNT': ['What previous work provides','What we still need to investigate','Novelty requires'],
        'DISAGG': ['Proposed','Not Yet Evaluated','Active / reusable KV placement','Optional serving-phase placement','SLO goodput'],
        'GEOARCH': ['Global Cross-DC Scheduler','DC A:','DC B:','request/session routing','operational energy/carbon'],
        'ENVIRONMENT': ['RCITI GPU Cluster','Dense LLM','LLMServingSim 2.0','Documented capabilities','Planned extensions','No HBF hardware is assumed'],
        'NEXT': ['held-out calibration error','Baselines:','Fair comparisons:','memory capacity','precision'],
        'PLACEMENT': ['Published MoE-based simulation evidence'],
        'PLACEMENTENERGY': ['Published MoE-based simulation evidence'],
    }
    for label, values in new_required.items():
        text = ' '.join(doc[names[label]['page']].get_text().split())
        for value in values: assert value in text, (label, value)
    thunder = ' '.join(doc[names['THUNDER']['page']].get_text().split())
    assert re.search(r'Coding 8 4 Conversation 4 8', thunder), thunder
    expected_citations = {
        'GEO': 'https://arxiv.org/abs/2610.14571v1',
        'RELATED': 'https://arxiv.org/abs/2505.23970v3',
        'MEMORY': 'https://arxiv.org/abs/2609.39131v2',
        'PLACEMENT': 'https://arxiv.org/abs/2609.39131v2',
        'PLACEMENTENERGY': 'https://arxiv.org/abs/2609.39131v2',
        'HELIX': 'https://doi.org/10.1145/3669940.3707215',
        'THUNDER': 'https://proceedings.mlsys.org/paper_files/paper/2025/file/c2a0e26dd9ee7d57e92bb1c24b39659a-Paper-Conference.pdf',
        'ENVIRONMENT': 'https://llmservingsim.ai/docs/getting-started/overview',
    }
    for label, uri in expected_citations.items():
        assert any(l.get('uri')==uri for l in doc[names[label]['page']].get_links()), (label,uri)
    index=' '.join(doc[1].get_text().split())
    for value in ['Previous Work and Research Gaps','Workload and HBM/HBF Evidence','Proposed Research Direction','Experimental Environment and Evaluation']:
        assert value in index, value
    assert 'Embodied Carbon' not in index
    assert round(100*(9.54/7.19-1),1)==32.7
    assert round(225.9/13.52,1)==16.7
    assert round(100*(1-(225.9/512)/(13.52/16)),1)==47.8
    return sorted(uris)

def main():
    before=protected()
    source=(ROOT/f'{NAME}.tex').read_text()
    frame_titles=re.findall(r'\\begin\{frame\}\[[^]]+\]\{([^}]+)\}',source)
    assert len(frame_titles)==20 and all('?' not in title for title in frame_titles), 'Unexpected question-style slide title remains'
    for label,expected in PRESERVED.items():
        frame=re.search(r'\\begin\{frame\}\[t,label='+label+r'\](.*?)\\end\{frame\}',source,re.S).group(1)
        # Normalize authorized title edits and source/supplement navigation only.
        for current, original in ORIGINAL_REEL_TITLES.items():
            if frame.startswith('{'+current+'}'):
                frame='{'+original+'}'+frame[len(current)+2:]
        frame=frame.replace(r'\hfill\hyperlink{REELABOUT}{\scriptsize About REEL / LCI}', '')
        frame=frame.replace(r'\href{\srcA}{REEL LCI v1.0}', 'REEL LCI v1.0')
        assert hashlib.sha256(frame.encode()).hexdigest()==expected,('Preserved frame changed',label)
    # Freeze unchanged evidence against the actual starting HEAD. Only the two
    # explicit MoE scope notes may be added to the published simulation frames.
    baseline_source=subprocess.check_output(['git','show',
        '51548444d0d896c8302ad94a9c81cae3f2ed571d:2026-11-18-meeting/'+NAME+'.tex'],
        cwd=REPO,text=True)
    def frames(text):
        return {label:frame for frame,label in re.findall(
            r'(\\begin\{frame\}\[[^]]*label=([^,\]]+)[^]]*\].*?\\end\{frame\})',text,re.S)}
    baseline,current=frames(baseline_source),frames(source)
    assert list(current)==['COVER']+LABELS, 'Frame order / labels differ'
    for label in ['RELATED','MEMORY','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES']:
        assert current[label]==baseline[label], ('Preserved frame changed',label)
    scope_note = r'\\Published MoE-based simulation evidence; our proposed workload evaluation is not restricted to MoE.'
    for label in ['PLACEMENT','PLACEMENTENERGY']:
        assert current[label].replace(scope_note,'')==baseline[label], ('Published HBF evidence changed',label)
    for label in ['DISAGG','GEOARCH','ENVIRONMENT','NEXT']:
        assert r'\proposed' in current[label], label
        for obsolete in ['Attention Worker','Expert Worker','expert-weight','A/E disaggregation']:
            assert obsolete not in current[label], (label,obsolete)
    (QA/'pages').mkdir(parents=True,exist_ok=True);ZIP.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research-materials-') as td:
        temp=Path(td);local=compile_pdf(ROOT,temp/'local',NAME)
        with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(ROOT/f'{NAME}.tex','main.tex')
            z.writestr('README.txt','Main file: main.tex\nCompiler: pdfLaTeX\nCompile twice for numbering and navigation.\nSelf-contained Beamer source; 22 pages.\n')
        isolated=temp/'isolated'
        with zipfile.ZipFile(ZIP) as z: assert z.testzip() is None;z.extractall(isolated)
        other=compile_pdf(isolated,temp/'standalone','main')
        a,b=fitz.open(local),fitz.open(other)
        uris=validate(a);validate(b)
        for x,y in zip(a,b):
            assert x.get_text()==y.get_text()
            assert x.get_pixmap().digest==y.get_pixmap().digest
            assert annotations(x)==annotations(y)
        for stale in (QA/'pages').glob('research-materials-*.png'):
            if int(stale.stem.rsplit('-',1)[1]) > len(a): stale.unlink()
        montage=Image.new('RGB',(1600,((len(a)+1)//2)*470),'#D8E4EB')
        for n,page in enumerate(a):
            dest=QA/'pages'/f'research-materials-{n+1:02d}.png'
            page.get_pixmap(matrix=fitz.Matrix(3,3)).save(dest)
            im=Image.open(dest).convert('RGB');im.thumbnail((800,450))
            x=(n%2)*800;y=(n//2)*470
            montage.paste(im,(x,y));ImageDraw.Draw(montage).text((x+12,y+452),f'{n+1}/22',fill='#243748')
        montage.save(QA/'research-materials-montage.png');shutil.copy2(local,PDF)
    assert before==protected(),'Protected files changed during build'
    report=dict(pages=22,local_passes=2,zip_passes=2,warnings=[],source_sha256=digest(ROOT/f'{NAME}.tex'),pdf_sha256=digest(PDF),zip_sha256=digest(ZIP),preserved_frame_hashes=PRESERVED,category_destinations={k:v+1 for k,v in CATEGORIES.items()},supplement_round_trips={'REEL1_REELABOUT':[17,21], 'MEMORY_MEMORYSOURCES':[9,22]},parity={'text':True,'pixels':True,'annotations':True},protected_files=len(before),uris=uris)
    (QA/'research-materials-build.json').write_text(json.dumps(report,indent=2)+'\n')
    # Audit preserved rendered evidence against the user's actual starting PDF.
    base_commit='51548444d0d896c8302ad94a9c81cae3f2ed571d'
    base_pdf=subprocess.check_output(['git','show',base_commit+':2026-11-18-meeting/output/pdf/'+NAME+'.pdf'],cwd=REPO)
    old_doc=fitz.open(stream=base_pdf,filetype='pdf')
    new_doc=fitz.open(PDF)
    preserved_pages=[]
    for label, old_page in {'RELATED':3,'MEMORY':9,'REEL1':5,'REEL2':6,'REEL3':7,'REEL4':8,'THANKYOU':14}.items():
        new_page=new_doc.resolve_names()[label]['page']
        clip=fitz.Rect(0,0,new_doc[new_page].rect.width,new_doc[new_page].rect.height-16)
        assert old_doc[old_page].get_pixmap(matrix=fitz.Matrix(3,3),clip=clip).digest == new_doc[new_page].get_pixmap(matrix=fitz.Matrix(3,3),clip=clip).digest, label
        assert {l.get('uri') for l in old_doc[old_page].get_links() if l.get('uri')} == {l.get('uri') for l in new_doc[new_page].get_links() if l.get('uri')}, label
        preserved_pages.append(dict(label=label,original_page=old_page+1,current_page=new_page+1,pixels_equal_above_footer=True,external_citations_equal=True))
    (QA/'research-materials-preservation.json').write_text(json.dumps(dict(base_commit=base_commit,pdf_sha256=digest(PDF),preserved_pages=preserved_pages,comparison='3x pixels excluding bottom 16 PDF points; source-frame checks additionally preserve all scientific content',hbf_table6='Source unchanged except explicit MoE scope note; all values and charts frozen'),indent=2)+'\n')
    (QA/'research-materials-frame-baseline.json').write_text(json.dumps(dict(commit=base_commit,scope='Frozen source frames checked against starting commit; current source includes only authorized revision',unchanged_labels=['RELATED','MEMORY','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES'],scope_note_only_labels=['PLACEMENT','PLACEMENTENERGY'],current_order=['COVER']+LABELS,sha256={label:hashlib.sha256(frame.encode()).hexdigest() for label,frame in current.items()}),indent=2)+'\n')
    (QA/'research-materials-geo-validation.json').write_text(json.dumps(dict(baseline_commit=base_commit,pdf_sha256=digest(PDF),current_page=3,label='GEO',preserved_scientific_claims=['Shared global snapshot and independent regional scheduling','Operational carbon only','A100-calibrated models'],authorized_change='Research direction now emphasizes calibrated workload-aware GPU/memory costs for routing; no total-carbon result claimed',primary_source='https://arxiv.org/abs/2610.14571v1'),indent=2)+'\n')
    (QA/'validation.md').write_text("# Research Materials validation\n\n"
        "- PASS: 22 widescreen pages; Thank You at 16, supplements at 17–22.\n"
        "- PASS: two local and two extracted ZIP pdfLaTeX passes; no warnings.\n"
        "- PASS: local/ZIP text, pixels and annotations match.\n"
        "- PASS: four index cards target pages 3, 7, 12 and 14; embodied carbon is supplementary.\n"
        "- PASS: backup round trips, bounds, evidence values and unchanged evidence frames.\n"
        "- PASS: all text/image bounds fit; preserved evidence and new proposal contracts pass.\n")
    print('PASS: 22 pages; warning-free local/ZIP builds; navigation and preserved-content checks.')
if __name__=='__main__':main()
