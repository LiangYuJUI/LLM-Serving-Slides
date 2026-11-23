#!/usr/bin/env python3
"""Build the 20-page research deck and Overleaf package; validate page order, links and parity."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile, zipfile
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SOURCE = ROOT / '2026-11-18-Research-Materials.tex'
PDF = ROOT / 'output/pdf/2026-11-24-Meeting.pdf'
ZIP = ROOT / 'output/overleaf/Research-Materials.zip'
QA = ROOT / 'output/qa'
HELIX_FIGURE = REPO / '2026-11-04-meeting/Helix/Without-Caption/Helix_Figure_03_System_Overview.png'
HELIX_LOCAL = '../2026-11-04-meeting/Helix/Without-Caption/Helix_Figure_03_System_Overview.png'
HELIX_ZIP = 'figures/Helix_Figure_03_System_Overview.png'
THUNDER_FIGURE = ROOT / 'figures/ThunderServe_Fig05_no_caption.png'
LABELS = ['EINDEX','GEO','RELATED','HELIX','THUNDER','PRISM','WORKLOAD','MEMORY','PLACEMENT','PLACEMENTENERGY','ACCOUNT','ENVIRONMENT','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES','PW_CARBON_ARCH','PW_CARBON_MILP','PW_GREENCACHE','PW_HELIX_FLOW','PW_HELIX_MILP','PW_THUNDER']
PAGE = {label:i for i,label in enumerate(['COVER']+LABELS)}
PAGES, MAIN_PAGES = 26, 14
CATEGORIES = {'GEO':2,'WORKLOAD':7,'ACCOUNT':11,'ENVIRONMENT':12}
BACKUP_MAIN = {'PW_CARBON_ARCH':'GEO','PW_CARBON_MILP':'GEO','PW_GREENCACHE':'RELATED','PW_HELIX_FLOW':'HELIX','PW_HELIX_MILP':'HELIX','PW_THUNDER':'THUNDER'}
BACKUP_REQUIRED = {
 'PW_CARBON_ARCH':['Carbon–SLO: Geo-Distributed Simulator','Figure 3','Regional Scheduler','RTT','datacenter states','RTT matrix','continuous batching'],
 'PW_CARBON_MILP':['Carbon–SLO: Facility MILP Routing','Predict TTFT and TPOT','Filter SLO-feasible datacenters','Solve Facility MILP','Execute and evaluate','shared fixed/batch carbon cost','does not guarantee compliance','not a datacenter shutdown control'],
 'PW_GREENCACHE':['GreenCache: Optimization and Execution','Fig. 10','SLO Input','Constraint Solver','Cache Manager','LLM Server and Cache','ILP selects the lowest-carbon feasible SSD cache capacity','LCS then ranks entries for eviction','LMCache/vLLM'],
 'PW_HELIX_FLOW':['Helix: Max-Flow Model of Serving','Node splitting','Network capacity','Source, sink, conservation','MaxFlow','fixed placement','tokens/s'],
 'PW_HELIX_MILP':['Helix: MILP Placement and Flow','Layer placement and memory','Flow conservation','Compute constraints','Connectivity and network','Maximize aggregate serving throughput','does not optimize operational carbon or p99 latency'],
 'PW_THUNDER':['ThunderServe: Two-Level Scheduling','ThunderServe, MLSys 2025','UPPER LEVEL','GPU group construction','Phase designation','LOWER LEVEL','TP / PP configuration','Routing and KV transfer','Replica counts are not GPU counts']
}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def compile_pdf(cwd, name, out):
    out.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        run = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={out}',name+'.tex'],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if run.returncode: raise RuntimeError(run.stdout[-8000:])
    log=(out/(name+'.log')).read_text(errors='replace')
    warnings=re.findall(r'^.*(?:Overfull|Underfull|undefined|Warning|Missing character|not found).*$',log,re.M)
    if warnings: raise RuntimeError('\n'.join(warnings))
    return out/(name+'.pdf')

def normalized(p): return ' '.join(p.get_text().split())

def validate(doc):
    assert len(doc)==PAGES, len(doc)
    names=doc.resolve_names()
    assert names['COVER']['page']==0
    for label,page in PAGE.items(): assert names[label]['page']==page,(label,names[label])
    assert 'Thank you' in doc[13].get_text()
    assert [names[label]['page'] for label in ['PW_CARBON_ARCH','PW_CARBON_MILP','PW_GREENCACHE','PW_HELIX_FLOW','PW_HELIX_MILP','PW_THUNDER']]==list(range(20,26))
    for page,p in enumerate(doc):
        text=p.get_text()
        assert re.search(rf'Research Materials\s*\|\s*{page+1}\s*/\s*{PAGES}',text), (page+1,text[-100:])
        assert abs(p.rect.width/p.rect.height-16/9)<.001
        for link in p.get_links():
            if link.get('nameddest'):
                assert link['nameddest'] in names
                assert link['page']==names[link['nameddest']]['page']
            assert p.rect.contains(fitz.Rect(link['from']))
        for block in p.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    r=fitz.Rect(span['bbox'])
                    assert r.x0>=0 and r.y0>=0 and r.x1<=p.rect.width and r.y1<=p.rect.height,(page+1,span)
        for im in p.get_image_info(): assert p.rect.contains(fitz.Rect(im['bbox']))
    index=doc[1]
    for label,page in CATEGORIES.items():
        links=[l for l in index.get_links() if l.get('nameddest')==label]
        assert len(links)==1 and links[0]['page']==page and links[0]['from'].width>index.rect.width*.9,(label,links)
    # Each Main Previous Work link and each Backup return must follow stable Beamer labels.
    for backup,main in BACKUP_MAIN.items():
        src=doc[PAGE[main]]; dst=doc[PAGE[backup]]
        assert any(link.get('nameddest')==backup and link['page']==PAGE[backup] for link in src.get_links()),(main,backup,'missing main-to-backup')
        returns=[link for link in dst.get_links() if link.get('nameddest')==main and link['page']==PAGE[main]]
        assert len(returns)==1 and 'Back to Main Slide' in dst.get_textbox(returns[0]['from']),(backup,main,'missing return')
        for link in src.get_links():
            if link.get('nameddest')==backup:
                assert dst.rect.contains(fitz.Rect(link['from'])) and src.rect.contains(fitz.Rect(link['from']))
    for label,phrases in BACKUP_REQUIRED.items():
        text=normalized(doc[PAGE[label]])
        for phrase in phrases: assert phrase in text,(label,phrase)
    # Main to supplement and supplement return destinations must remain valid after the insertion.
    for main,supp in [('MEMORY','MEMORYSOURCES'),('REEL1','REELABOUT')]:
        p=doc[PAGE[main]]; q=doc[PAGE[supp]]
        assert any(l.get('nameddest')==supp and l['page']==PAGE[supp] for l in p.get_links()),(main,supp)
        assert any(l.get('nameddest')==main and l['page']==PAGE[main] for l in q.get_links()),(supp,main)
    reel=doc[PAGE['REEL1']]
    assert any(l.get('uri')=='https://reellci.com/insights/the-hbf-inversion.html' and 'REEL LCI v1.0' in reel.get_textbox(l['from']) for l in reel.get_links()), 'REEL source link missing'
    assert all(term in normalized(doc[PAGE['REELABOUT']]) for term in ['Repository of Electronics Environmental Line-items','Life cycle inventory','Jonathan Balsvik','520 datasets','18 categories'])
    assert 'https://reellci.com/' in normalized(doc[PAGE['REELABOUT']])
    requirements={
      'GEO':['Main Idea','Predict load-dependent serving latency and energy','Current Architecture','Global Provisioner','Regional Scheduler','Limitations','RTT: Round-Trip Time'],
      'RELATED':['Main Idea','Dynamically size SSD-backed KV caches','Inputs','Optimization','Trade-off','Limitations','GreenCache sizes'],
      'HELIX':['Main Idea','Use max-flow-based layer placement','Motivation:','Method:','Evaluation:'],
      'THUNDER':['Main Idea','Jointly optimize prefill/decode resource allocation','Motivation:','Method:','TP/PP are distinct decisions','Workload characteristics affect'],
      'PRISM':['From Single-Model to Multi-Model Deployment','Production clusters and agentic workflows increasingly serve many LLMs on limited GPUs.','Prism (OSDI 2026)','Memory ballooning: GPU memory as an elastic resource lent and reclaimed across models at runtime','Goal: SLO attainment & cost, environment: homogeneous H100s','Scepsy (arXiv 2026)','Workflow runtime is unpredictable, but each LLM’s share of it is stable','give each LLM GPUs in proportion to its share','Goal: latency at target throughput, environment: homogeneous RTX A6000s','Multi-model deployment on heterogeneous environments with carbon awareness remains less explored.','How should allocation change when carbon is the objective?'],
      'WORKLOAD':['Coding','Conversation','Multi-Turn / Agentic','Longer prompts, shorter outputs','Shorter prompts, longer outputs','Repeated context, potential prefix/KV reuse','Prefill compute, TTFT','Decode throughput, memory bandwidth','Memory capacity, KV retention and reuse','Different LLM workloads require different compute, memory, and scheduling resources.'],
      'ACCOUNT':['Coordinated Cross-DC Scheduling','Carbon–SLO shares global data-center states, but regional schedulers make routing decisions independently.','Investigate coordinated cross-region scheduling to account for shared capacity, workload distribution, and SLO feasibility.','Carbon-Aware Cost Modeling','GreenCache considers operational and amortized embodied carbon for caching, but not cross-data-center routing.','Adapt carbon-aware cost modeling to heterogeneous GPU serving and geographic scheduling, starting with operational carbon.','Power-Aware Heterogeneous GPU Scheduling','Prism and Scepsy address multi-model sharing','with multi-model serving as a potential extension'],
      'ENVIRONMENT':['LLMServingSim 2.0','A profile-driven simulator','Hardware and Network Modeling','Serving Simulation','Profiling and Validation','Real GPU Profiling','Academia Sinica CITI GPU Cluster','configured parameters'],
      'THANKYOU':['Thank you'],
    }
    for label,phrases in requirements.items():
        text=normalized(doc[PAGE[label]])
        for phrase in phrases: assert phrase in text,(label,phrase)
    prism_text=normalized(doc[PAGE['PRISM']])
    for extra in ['Main Idea','Method','Optimization Goal','Research Opportunity','Multi-LLM Resource Sharing']:
        assert extra not in prism_text,('Unrequested text on Slide 7',extra)
    # Preserve the underlying research evidence, values and original figure assets.
    for label,phrases in {'MEMORY':['24','375','1,000','250','3.4','6.8','100,000','P/E'], 'MEMORYSOURCES':['Micron','Lenovo','Ma & Patterson','Moon','MemExplorer','Son','SSD','100,000','device power ratio'], 'PLACEMENT':['11,354','4,543','4,538','60%','not an equal-hardware comparison','Published MoE-based simulation evidence'], 'PLACEMENTENERGY':['9.11','7.19','9.54','32.7','static/background','static/background power excluded','Published MoE-based simulation evidence'], 'REEL2':['13.52','19.81','20.6','225.9','16 GB','24 GB','36 GB','512 GiB','16.7'], 'REEL3':['0.845','0.825','0.572','0.441','47.8','nominal capacity unit','not verified per-GiB results'], 'REEL4':['Model Assumptions','Key Limitations','not validated HBF manufacturing footprints'] }.items():
        text=normalized(doc[PAGE[label]])
        for value in phrases: assert value in text,(label,value)
    assert len(doc[PAGE['HELIX']].get_image_info())==1
    assert len(doc[PAGE['THUNDER']].get_image_info())==1
    for label,count in {'PW_CARBON_ARCH':1,'PW_GREENCACHE':1,'PW_HELIX_FLOW':2,'PW_HELIX_MILP':0,'PW_THUNDER':1}.items():
        assert len(doc[PAGE[label]].get_image_info())==count,(label,count)
    assert 'Different LLM workloads require different compute, memory, and scheduling resources.' in normalized(doc[PAGE['WORKLOAD']])
    return sum(len(p.get_links()) for p in doc)

def main():
    # Ensure scientific and supplementary source frames outside this edit's scope are byte-identical to HEAD.
    baseline=subprocess.check_output(['git','show','HEAD:'+SOURCE.relative_to(REPO).as_posix()],cwd=REPO,text=True)
    current=SOURCE.read_text()
    def frames(source):
        return {label:body for body,label in re.findall(r'(\\begin\{frame\}\[[^]]*label=([^,\]]+)[^]]*\].*?\\end\{frame\})',source,re.S)}
    old,new=frames(baseline),frames(current)
    assert list(new)==['COVER']+LABELS, list(new)
    allowed={'EINDEX','GEO','RELATED','HELIX','THUNDER','PRISM','WORKLOAD','ACCOUNT'}
    for label in old.keys()-allowed:
        if label in new: assert old[label]==new[label],('Out-of-scope frame source changed',label)
    with tempfile.TemporaryDirectory(prefix='research-materials-') as td:
        tmp=Path(td)
        local=compile_pdf(ROOT,SOURCE.stem,tmp/'local')
        ZIP.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('main.tex',current.replace(HELIX_LOCAL,HELIX_ZIP))
            z.write(HELIX_FIGURE,HELIX_ZIP)
            z.write(THUNDER_FIGURE,'figures/ThunderServe_Fig05_no_caption.png')
            backup_assets={
                'figures/PreviousWork_CarbonSLO_Fig03.png': ROOT/'figures/PreviousWork_CarbonSLO_Fig03.png',
                'figures/PreviousWork_GreenCache_Fig10.png': ROOT/'figures/PreviousWork_GreenCache_Fig10.png',
                'figures/PreviousWork_Helix_Figure_02.png': ROOT/'figures/PreviousWork_Helix_Figure_02.png',
                'figures/PreviousWork_ThunderServe_Fig03.png': ROOT/'figures/PreviousWork_ThunderServe_Fig03.png',
            }
            for arc,path in backup_assets.items(): z.write(path,arc)
            z.writestr('README.txt','Main file: main.tex\nCompiler: pdfLaTeX\nCompile twice for numbering and navigation.\n26-page deck; all original figures required by the main and Previous Work backup slides are included.\n')
        isolated=tmp/'isolated'
        with zipfile.ZipFile(ZIP) as z:
            assert z.testzip() is None
            assert hashlib.sha256(z.read(HELIX_ZIP)).hexdigest()==sha(HELIX_FIGURE)
            assert hashlib.sha256(z.read('figures/ThunderServe_Fig05_no_caption.png')).hexdigest()==sha(THUNDER_FIGURE)
            for arc,path in backup_assets.items(): assert hashlib.sha256(z.read(arc)).hexdigest()==sha(path),(arc,'asset mismatch')
            z.extractall(isolated)
        zipped=compile_pdf(isolated,'main',tmp/'zipbuild')
        a,b=fitz.open(local),fitz.open(zipped)
        links=validate(a); validate(b)
        for i,(x,y) in enumerate(zip(a,b),1):
            assert x.get_text()==y.get_text(),('ZIP text mismatch',i)
            assert x.get_pixmap().digest==y.get_pixmap().digest,('ZIP render mismatch',i)
            assert [(l.get('nameddest'),l.get('page'),l.get('uri'),tuple(l['from'])) for l in x.get_links()]==[(l.get('nameddest'),l.get('page'),l.get('uri'),tuple(l['from'])) for l in y.get_links()],('ZIP links mismatch',i)
        PDF.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(local,PDF)
        QA.mkdir(parents=True,exist_ok=True)
        render_dir=QA/'pages'; render_dir.mkdir(exist_ok=True)
        for i,p in enumerate(a,1): p.get_pixmap(matrix=fitz.Matrix(3,3)).save(render_dir/f'research-materials-{i:02d}.png')
        # Keep the review montage synchronized with the rendered 26-page deck.
        montage=Image.new('RGB',(1600,((PAGES+1)//2)*470),'#D8E4EB')
        for n in range(PAGES):
            image=Image.open(render_dir/f'research-materials-{n+1:02d}.png').convert('RGB'); image.thumbnail((800,450))
            x=(n%2)*800; y=(n//2)*470; montage.paste(image,(x,y))
            ImageDraw.Draw(montage).text((x+12,y+452),f'{n+1}/{PAGES}',fill='#243748')
        montage.save(QA/'research-materials-montage.png')
        report={'pages':26,'main_pages':14,'supplementary_pages':6,'previous_work_backup_pages':6,'pdf_sha256':sha(PDF),'zip_sha256':sha(ZIP),'source_sha256':sha(SOURCE),'local_passes':2,'zip_passes':2,'warnings':[],'links':links,'contents_destinations':{k:v+1 for k,v in CATEGORIES.items()},'main_to_backup':{'GEO':[PAGE['PW_CARBON_ARCH']+1,PAGE['PW_CARBON_MILP']+1],'RELATED':[PAGE['PW_GREENCACHE']+1],'HELIX':[PAGE['PW_HELIX_FLOW']+1,PAGE['PW_HELIX_MILP']+1],'THUNDER':[PAGE['PW_THUNDER']+1]},'backup_to_main':{label:PAGE[target]+1 for label,target in BACKUP_MAIN.items()},'pdf_zip_parity':{'text':True,'pixels':True,'annotations':True},'unchanged_frames':sorted(old.keys()-allowed)}
        (QA/'research-materials-build.json').write_text(json.dumps(report,indent=2)+'\n')
        (QA/'validation.md').write_text('# Research Materials validation\n\n- PASS: 26 widescreen pages (14 main + 6 existing supplements + 6 Previous Work backups); Thank You at page 14.\n- PASS: local and extracted Overleaf ZIP compiled in two pdfLaTeX passes each with no warnings.\n- PASS: local PDF and ZIP PDF match in text, rendered pixels, and link annotations.\n- PASS: four Contents cards target pages 3, 8, 12, and 13; existing supplement links round-trip.\n- PASS: Previous Work links 3→21/22, 4→23, 5→24/25, 6→26; every Backup returns to its Main slide.\n- PASS: all 26 footers, page bounds, figures, destinations, retained evidence, and backup content validated.\n')
        a.close(); b.close()
    print(f'PASS: 26 pages; warning-free local/ZIP builds; {links} links validated; PDF and ZIP render identically.')

if __name__=='__main__': main()
