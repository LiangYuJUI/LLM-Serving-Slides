#!/usr/bin/env python3
"""Build Research Materials twice locally and from its Overleaf ZIP; validate and render."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile, zipfile
import pymupdf as fitz
from PIL import Image, ImageChops, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
NAME = '2026-11-18-Research-Materials'
QA = ROOT/'output/qa'
PDF = ROOT/'output/pdf'/f'{NAME}.pdf'
ZIP = ROOT/'output/overleaf/Research-Materials.zip'
LABELS = ['EINDEX','GEO','RELATED','HELIX','THUNDER','WORKLOAD','ACCOUNT','MEMORY','PLACEMENT','PLACEMENTENERGY','DISAGG','GEOARCH','ENVIRONMENT','NEXT','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES']
HELIX_BASE = '3f90a20ee7648052352fb19cc090c5500bfe06f9'
HELIX_FIGURE = REPO/'2026-11-04-meeting/Helix/Without-Caption/Helix_Figure_03_System_Overview.png'
HELIX_LOCAL_PATH = '../2026-11-04-meeting/Helix/Without-Caption/Helix_Figure_03_System_Overview.png'
HELIX_ZIP_PATH = 'figures/Helix_Figure_03_System_Overview.png'
# ThunderServe Figure 5 with only the printed caption removed (rows 0-439 of the original, pixel-identical).
THUNDER_ORIGINAL = REPO/'2026-10-21-meeting/ThunderServe/ThunderServe_Fig05.png'
THUNDER_FIGURE = ROOT/'figures/ThunderServe_Fig05_no_caption.png'
THUNDER_ZIP_PATH = 'figures/ThunderServe_Fig05_no_caption.png'
THUNDER_CROP_HEIGHT = 440
REVISED_SLIDES = {'COVER':0, 'EINDEX':1, 'WORKLOAD':6, 'ACCOUNT':7}  # label -> 0-based PDF page of the 2026-11-20 refocus
# Source frames of slides 3-6 as they stood before the refocus (latest Helix / ThunderServe layouts). Must stay byte-identical.
FROZEN_SLIDES_3_6 = {'GEO': 'a928fc065e6737f3787b94612151bf8bd4a44cb941c8d9951c07151f89ba8020', 'RELATED': '7b51b79f56d4ddba54bcb03ca7b980db9106f27e8472ceab3042bd3ce7457379', 'HELIX': 'b997d9a6bbb5a19a247c2e5d3f787d85f1ba04c31034b68070467b21e694a106', 'THUNDER': '69c2b725665f7b48ed16605644d372d7a1af1456ae0ec5e007770cef068d38d6'}
COVER_TEXT = 'Power- and Carbon-Aware LLM Serving on Heterogeneous GPUs Workload-Aware Scheduling Across Compute and Memory Resources'
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

def same_page(p, q, clip=None):
    """Equivalence of two renderings of the same slide.

    pdfTeX subsets fonts per document, so adding glyphs elsewhere can move Type1 hinting by a few anti-aliasing
    levels on otherwise untouched pages. Text, word positions (0.1 pt), vector drawings, images and links must
    still match exactly; the raster is compared after 3x -> 1x area averaging with a small tolerance (measured
    subset-hinting noise <= 34/255, versus >= 200/255 for a genuinely different page).
    """
    if p.get_text(clip=clip) != q.get_text(clip=clip) or (clip is None and annotations(p) != annotations(q)): return False
    wp, wq = p.get_text('words', clip=clip), q.get_text('words', clip=clip)
    if len(wp) != len(wq) or any(a[4] != b[4] or max(abs(x-y) for x, y in zip(a[:4], b[:4])) > .1 for a, b in zip(wp, wq)): return False
    if clip is None:
        if [(tuple(round(v, 2) for v in d['rect']), d.get('fill'), d.get('color')) for d in p.get_drawings()] != [(tuple(round(v, 2) for v in d['rect']), d.get('fill'), d.get('color')) for d in q.get_drawings()]: return False
        if [tuple(round(v, 2) for v in im['bbox']) for im in p.get_image_info()] != [tuple(round(v, 2) for v in im['bbox']) for im in q.get_image_info()]: return False
    m = fitz.Matrix(3, 3)
    pa, pb = p.get_pixmap(matrix=m, clip=clip), q.get_pixmap(matrix=m, clip=clip)
    if pa.digest == pb.digest: return True
    def gray(pm): return Image.frombytes('RGB', (pm.width, pm.height), pm.samples).convert('L')
    a, b = gray(pa), gray(pb)
    size = (a.width // 3, a.height // 3)
    return ImageChops.difference(a.resize(size, Image.BOX), b.resize(size, Image.BOX)).getextrema()[1] <= 48

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
        'GEO': ['Dissecting the Carbon–SLO Tension in Geo-Distributed LLM Serving', 'arXiv 2026 (Preprint)', 'Carbon- & SLO-Aware Geo-Distributed Request Scheduling', 'Global Provisioner', 'Periodically polls DCs', 'broadcasts global snapshot',
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
        'RELATED': ['Cache Your Prompt When It’s Green', 'Carbon-Aware Caching for Large Language Model Serving', 'SIGMETRICS 2026', 'Carbon-Aware Adaptive SSD KV Cache Sizing'],
        'HELIX': ['Serving Large Language Models over Heterogeneous GPUs and Network via Max-Flow','Motivation:', 'making model placement challenging.', 'Method:', 'max-flow/MILP-based layer placement to maximize throughput', 'runtime request scheduling', 'Evaluation:', 'Real heterogeneous GPU cluster', 'geo-distributed settings evaluated using simulation', 'Fig. 3 (System Overview)'],
        'THUNDER': ['ThunderServe: High-performance and Cost-efficient LLM Serving in Cloud Environments','MLSys 2025','Workload-Aware Prefill/Decode Placement & Scheduling','Motivation:','Prefill is typically compute-intensive','Method:','Jointly optimize GPU grouping, prefill/decode assignment, parallel configuration, and request routing','Workload characteristics affect the preferred prefill/decode resource allocation and routing','Figure 5','Sec. 3.3','Sec. 5.3'],
        'WORKLOAD': ['Different Workloads, Different Resource Requirements','Workload Characteristics Resource Requirements','Coding Longer prompts, shorter outputs Prefill compute, TTFT','Conversation Shorter prompts, longer outputs Decode throughput, memory bandwidth','Multi-Turn / Agentic Repeated context, potential prefix/KV reuse Memory capacity, KV retention and reuse','Different LLM workloads require different compute, memory, and scheduling resources.','ThunderServe, Sec. 3.4, Fig. 6, Table 3','GreenCache, Secs. 2–3'],
        'ACCOUNT': ['Research Direction: Power- and Carbon-Aware Heterogeneous GPU Scheduling','Prior work provides geo-aware routing, caching, heterogeneous GPU placement, and phase-aware resource allocation.',
                    '1 Workload-Aware Performance and Power Modeling','Profile heterogeneous GPUs across different workload characteristics.','Compute capability','Memory capacity and bandwidth','Serving latency and throughput','GPU power and energy',
                    '2 Heterogeneous GPU Scheduling','different GPU capabilities and power characteristics','GPU allocation','Workload-aware request scheduling','Model/phase placement where appropriate','Resource utilization and communication costs',
                    '3 Carbon-Aware Scheduling','Cross-data-center routing may be evaluated as an extension of calibrated local scheduling.','Serving energy estimation','Regional carbon intensity','Queueing and network latency','TTFT/TPOT SLO feasibility',
                    'Optimize heterogeneous GPU serving energy and operational carbon while satisfying latency SLOs.','Carbon–SLO','GreenCache','Helix','ThunderServe'],
        'EINDEX': ['Research Evidence Overview','01 Previous Work and Research Background','Carbon–SLO, GreenCache, Helix, ThunderServe','02 Workload and Resource Characteristics','Workload Patterns, GPU/Memory Characteristics, Published Performance and Energy Evidence','03 Power- and Carbon-Aware GPU Scheduling','Heterogeneous GPU Allocation, Workload-Aware Scheduling, Cross-DC Routing','04 Experimental Environment and Evaluation','Academia Sinica GPU Cluster, LLMServingSim 2.0, Research Roadmap','Workload-aware heterogeneous GPU scheduling for energy- and carbon-efficient LLM serving.'],
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
    helix_images=doc[names['HELIX']['page']].get_image_info()
    assert len(helix_images)==1, 'Helix must use one original system overview figure'
    with Image.open(HELIX_FIGURE) as original:
        im=helix_images[0]; bounds=fitz.Rect(im['bbox'])
        assert (im['width'],im['height'])==original.size, 'Original image resolution must be preserved'
        assert abs(bounds.width/bounds.height-original.width/original.height)<.001, 'Figure distorted'
        assert bounds.width>doc[4].rect.width*.93, 'Figure must occupy the content width'
    # ThunderServe slide: Table 3 is intentionally removed from the slide (explained orally, kept in script/evidence).
    # Negative checks ensure its values and out-of-scope HBM/HBF content do not reappear on this Related Work slide.
    thunder_page = doc[names['THUNDER']['page']]
    thunder = ' '.join(thunder_page.get_text().split())
    for value in ['LLaMA-30B', 'Coding', 'Conversation', 'Replica counts', 'Joint scheduling decisions', 'Coding 8', 'HBM', 'HBF', 'Our direction', 'proposal']:
        assert value not in thunder, ('Removed Table 3 or out-of-scope content present', value)
    thunder_images = thunder_page.get_image_info()
    assert len(thunder_images) == 1, 'ThunderServe slide must contain exactly one Figure 5 image'
    with Image.open(THUNDER_FIGURE) as crop, Image.open(THUNDER_ORIGINAL) as original:
        assert crop.size == (original.width, THUNDER_CROP_HEIGHT), 'Figure 5 crop size changed'
        assert ImageChops.difference(crop.convert('RGB'), original.convert('RGB').crop((0, 0, original.width, THUNDER_CROP_HEIGHT))).getbbox() is None, 'Figure 5 crop must be pixel-identical to the original top region'
        im = thunder_images[0]; bounds = fitz.Rect(im['bbox'])
        assert (im['width'], im['height']) == crop.size, 'Figure 5 resolution must be preserved'
        assert abs(bounds.width / bounds.height - crop.width / crop.height) < .001, 'Figure 5 distorted'
        assert bounds.width > thunder_page.rect.width * .5, 'Figure 5 must be large'
        assert thunder_page.rect.contains(bounds), 'Figure 5 must sit inside the slide'
        # Text blocks must not overlap: the takeaway has to finish above the source footer, and Method above the takeaway.
        takeaway = fitz.Rect(next(b[:4] for b in thunder_page.get_text('blocks') if 'Workload characteristics affect' in b[4]))
        source = fitz.Rect(next(b[:4] for b in thunder_page.get_text('blocks') if b[4].startswith('Source:')))
        method = fitz.Rect(next(b[:4] for b in thunder_page.get_text('blocks') if 'Method:' in b[4]))
        assert method.y1 <= takeaway.y0 and takeaway.y1 <= source.y0, 'ThunderServe text blocks overlap'
        assert bounds.y1 <= method.y0, 'Figure 5 overlaps the Method sentence'
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
    for value in ['Previous Work and Research Background','Workload and Resource Characteristics','Power- and Carbon-Aware GPU Scheduling','Experimental Environment and Evaluation']:
        assert value in index, value
    assert 'Embodied Carbon' not in index
    # The index must not mention HBM/HBF in its cards or takeaway (the only trace allowed is the spelled-out title of the cited paper in the source line).
    index_body = index.split('Source:')[0]
    for banned in ['HBM','HBF','High Bandwidth','Flash','MoE','Previous Work and Research Gaps','Proposed Research Direction','Calibrate local serving costs']:
        assert banned not in index_body, ('Obsolete or out-of-scope index text', banned)
    for source in ['Carbon–SLO','GreenCache','Helix','ThunderServe','LLMServingSim 2.0']:
        assert source in index.split('Source:')[1], ('Index citation missing', source)
    # Cover: only the title and subtitle, centered, with no personal or institutional metadata.
    cover = doc[0]
    cover_text = ' '.join(re.sub(r'Research Materials\s*\|\s*1\s*/\s*22','',cover.get_text()).split())
    assert cover_text == COVER_TEXT, ('Cover must contain only the title and subtitle', cover_text)
    for banned in ['Yu-Jui','Liang','Advisor','Hsiang-Yun','Cheng','National Taiwan','Academia Sinica','Research Overview','HBM','HBF','2026']:
        assert banned not in cover.get_text(), ('Cover contains removed metadata', banned)
    boxes = [fitz.Rect(sp['bbox']) for b in cover.get_text('dict')['blocks'] for ln in b.get('lines',[]) for sp in ln['spans']
             if sp['text'].strip() and fitz.Rect(sp['bbox']).y1 < cover.rect.height-24]
    union = fitz.Rect(boxes[0])
    for box in boxes[1:]: union |= box
    assert abs((union.x0+union.x1)/2-cover.rect.width/2) < 6, 'Cover text is not horizontally centered'
    assert abs((union.y0+union.y1)/2-cover.rect.height/2) < cover.rect.height*.08, 'Cover text is not vertically balanced'
    assert union.width > cover.rect.width*.6 and union.height > cover.rect.height*.3, 'Cover typography is too small or sparse'
    sizes = [sp['size'] for b in cover.get_text('dict')['blocks'] for ln in b.get('lines',[]) for sp in ln['spans'] if sp['text'].strip() and sp['bbox'][3] < cover.rect.height-24]
    assert max(sizes) >= 20, 'Cover title must be large'
    # Slides 7 and 8: concise workload/direction slides without HBM/HBF, MoE, novelty claims, or removed layouts.
    for label in ['WORKLOAD','ACCOUNT']:
        text = ' '.join(doc[names[label]['page']].get_text().split())
        for banned in ['HBM','HBF','MoE','Attention','Expert','Reported:','Implications to evaluate','Reported behavior above','novel','Novelty','What previous work provides','Weight and KV','research opportunity','Workload characteristics influence','TTFT: time','KV: key']:
            assert banned.lower() not in text.lower(), ('Out-of-scope text on '+label, banned)
    workload_text = ' '.join(doc[names['WORKLOAD']['page']].get_text().split())
    for banned in ['Coding / Long-Prompt','Conversation / Long-Output','Categories can overlap','Characterizing','not universal definitions','may overlap with either']:
        assert banned not in workload_text, ('Obsolete workload text', banned)
    account_text = ' '.join(doc[names['ACCOUNT']['page']].get_text().split())
    for banned in ['Carbon–SLO Geo-aware routing and SLO modeling','GreenCache Carbon-aware KV reuse','Helix Heterogeneous GPU placement','ThunderServe Phase/workload-aware']:
        assert banned not in account_text, ('Four-paper comparison card must be removed', banned)
    for label in ['COVER','EINDEX','WORKLOAD','ACCOUNT']:
        page = doc[names[label]['page']]
        blocks = [fitz.Rect(b[:4]) for b in page.get_text('blocks') if b[4].strip()]
        for n,x in enumerate(blocks):
            for y in blocks[n+1:]:
                inter = x & y
                assert inter.is_empty or inter.width*inter.height < 1, ('Overlapping text blocks on '+label, x, y)
    # Slide 7 table: three workloads stacked in order, each row spanning three aligned columns.
    wl = doc[names['WORKLOAD']['page']]
    row_y = {name: wl.search_for(name)[0].y0 for name in ['Coding','Conversation','Multi-Turn / Agentic']}
    assert row_y['Coding'] < row_y['Conversation'] < row_y['Multi-Turn / Agentic'], 'Workload rows out of order'
    for header, row_text in [('Characteristics','Longer prompts'),('Resource Requirements','Prefill compute')]:
        assert abs(wl.search_for(header)[-1].x0 - wl.search_for(row_text)[0].x0) < 2, ('Table column misaligned', header)
    # Slide 8: three stacked cards in order, takeaway between the cards and the source footer.
    ac = doc[names['ACCOUNT']['page']]
    heads = [ac.search_for(h)[-1] for h in ['Workload-Aware Performance and Power Modeling','Heterogeneous GPU Scheduling','Carbon-Aware Scheduling']]
    assert heads[0].y0 < heads[1].y0 < heads[2].y0 and max(abs(h.x0-heads[0].x0) for h in heads) < 2, 'Research cards must be stacked and aligned'
    last_item = ac.search_for('TTFT/TPOT SLO feasibility')[0]; take = ac.search_for('Optimize heterogeneous GPU serving energy')[0]
    src = fitz.Rect(next(b[:4] for b in ac.get_text('blocks') if b[4].startswith('Source:')))
    assert last_item.y1 < take.y0 and take.y1 < src.y0, 'Slide 8 takeaway collides with cards or source'
    assert round(100*(9.54/7.19-1),1)==32.7
    assert round(225.9/13.52,1)==16.7
    assert round(100*(1-(225.9/512)/(13.52/16)),1)==47.8
    return sorted(uris)

def normalize_related(frame):
    # Undo the authorized slide-3 edits: heading-to-diagram gap and removed bottom takeaway.
    if 'label=GEO' in frame:
        frame=frame.replace(r'Current Architecture\par}'+'\n'+r'\vspace{.20cm}'+'\n'+r'\begin{tikzpicture}', r'Current Architecture\par}'+'\n'+r'\vspace{.03cm}'+'\n'+r'\begin{tikzpicture}', 1)
        frame=frame.replace('\\vspace{.08cm}\n\n\\source{\\href{\\carbonurl}{Carbon--SLO, Secs. III-A',
            '\\vspace{.08cm}\n\\takeaway{Our direction: Calibrate workload-aware GPU/memory energy and SLO costs for regional routing.}\n\n\\source{\\href{\\carbonurl}{Carbon--SLO, Secs. III-A', 1)
    # Undo the authorized slide-4 layout spacing (matches Helix's subtitle-to-body gap).
    if 'label=RELATED' in frame:
        frame=frame.replace(r'\vspace{.16cm}'+'\n'+r'\begin{columns}[T,onlytextwidth]', r'\vspace{.08cm}'+'\n'+r'\begin{columns}[T,onlytextwidth]', 1)
    # Restore only the explicitly removed SLO sentence for evidence comparison.
    if 'label=RELATED' in frame and 'Cache resizing must still satisfy' not in frame:
        frame=frame.replace(r'\end{columns}'+'\n'+r'\vspace{.06cm}', r'\end{columns}'+'\n'+r'\vspace{.06cm}'+'\n'+r'{\footnotesize Cache resizing must still satisfy TTFT / TPOT SLO targets.\par}', 1)
    # Normalize explicitly authorized GreenCache heading edits only.
    if 'label=RELATED' in frame and r'\color{Accent}Core Idea' not in frame:
        frame=frame.replace(r'\begin{columns}[T,onlytextwidth]', r'{\small\bfseries\color{Accent}Core Idea\par}'+'\n'+r'\vspace{.06cm}'+'\n'+r'\begin{columns}[T,onlytextwidth]', 1)
    return frame.replace('Dissecting the Carbon--SLO Tension in Geo-Distributed LLM Serving', 'Carbon--SLO: Shared State, Regional Decisions').replace(r'arXiv 2026 (Preprint)\quad |\quad Carbon- \& SLO-Aware Geo-Distributed Request Scheduling', 'Hierarchical control with independent regional scheduling').replace("Cache Your Prompt When It's Green --- Carbon-Aware Caching for Large Language Model Serving", 'GreenCache: Carbon-Aware SSD Cache Sizing').replace(r'SIGMETRICS 2026\quad |\quad Carbon-Aware Adaptive SSD KV Cache Sizing', 'Adaptive KV caching under carbon and SLO constraints')

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
        assert normalize_related(current[label])==baseline[label], ('Preserved frame changed',label)
    scope_note = r'\\Published MoE-based simulation evidence; our proposed workload evaluation is not restricted to MoE.'
    for label in ['PLACEMENT','PLACEMENTENERGY']:
        assert current[label].replace(scope_note,'')==baseline[label], ('Published HBF evidence changed',label)
    for label in ['DISAGG','GEOARCH','ENVIRONMENT','NEXT']:
        assert r'\proposed' in current[label], label
        for obsolete in ['Attention Worker','Expert Worker','expert-weight','A/E disaggregation']:
            assert obsolete not in current[label], (label,obsolete)
    helix_baseline=subprocess.check_output(['git','show',HELIX_BASE+':2026-11-18-meeting/'+NAME+'.tex'],cwd=REPO,text=True)
    baseline_frames=frames(helix_baseline)
    # THUNDER is the authorized Figure 5 redesign; its contract is checked explicitly in validate().
    for label in current.keys()-{'HELIX','THUNDER'}-set(REVISED_SLIDES):
        assert normalize_related(current[label])==baseline_frames[label], ('Preserved frame changed',label)
    # Slides 3-6 must stay byte-identical to their pre-refocus source (latest Helix / ThunderServe layouts).
    for label,expected in FROZEN_SLIDES_3_6.items():
        assert hashlib.sha256(current[label].encode()).hexdigest()==expected, ('Slides 3-6 changed by the refocus',label)
    assert r'\begin{tabularx}' not in current['THUNDER'] and 'figures/ThunderServe_Fig05_no_caption.png' in current['THUNDER'], 'THUNDER must use the Figure 5 crop'
    assert HELIX_LOCAL_PATH in current['HELIX'] and r'\begin{tikzpicture}' not in current['HELIX']
    (QA/'pages').mkdir(parents=True,exist_ok=True);ZIP.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research-materials-') as td:
        temp=Path(td);local=compile_pdf(ROOT,temp/'local',NAME)
        with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('main.tex',source.replace(HELIX_LOCAL_PATH,HELIX_ZIP_PATH))
            z.write(HELIX_FIGURE,HELIX_ZIP_PATH)
            z.write(THUNDER_FIGURE,THUNDER_ZIP_PATH)
            z.writestr('README.txt','Main file: main.tex\nCompiler: pdfLaTeX\nCompile twice for numbering and navigation.\nSelf-contained Beamer source, original Helix Figure 3, and ThunderServe Figure 5 (printed caption removed); 22 pages.\n')
        isolated=temp/'isolated'
        with zipfile.ZipFile(ZIP) as z:
            assert z.testzip() is None
            assert hashlib.sha256(z.read(HELIX_ZIP_PATH)).hexdigest()==digest(HELIX_FIGURE)
            assert hashlib.sha256(z.read(THUNDER_ZIP_PATH)).hexdigest()==digest(THUNDER_FIGURE)
            z.extractall(isolated)
        other=compile_pdf(isolated,temp/'standalone','main')
        a,b=fitz.open(local),fitz.open(other)
        uris=validate(a);validate(b)
        for x,y in zip(a,b):
            assert x.get_text()==y.get_text()
            assert x.get_pixmap().digest==y.get_pixmap().digest
            assert annotations(x)==annotations(y)
        previous=fitz.open(stream=subprocess.check_output(['git','show',HELIX_BASE+':2026-11-18-meeting/output/pdf/'+NAME+'.pdf'],cwd=REPO),filetype='pdf')
        for i in range(22):
            # Pages 3-6 (GEO, RELATED, HELIX, THUNDER) are earlier authorized redesigns, frozen by hash above;
            # pages 1, 2, 7 and 8 are the 2026-11-20 refocus. Everything else must equal the older baseline.
            if i in (2,3,4,5) or i in REVISED_SLIDES.values(): continue
            assert a[i].get_text()==previous[i].get_text(), ('Non-Helix text changed',i+1)
            assert same_page(a[i],previous[i]), ('Non-Helix rendering changed',i+1)
            assert annotations(a[i])==annotations(previous[i]), ('Non-Helix links changed',i+1)
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
    for label, old_page in {'MEMORY':9,'REEL1':5,'REEL2':6,'REEL3':7,'REEL4':8,'THANKYOU':14}.items():
        new_page=new_doc.resolve_names()[label]['page']
        clip=fitz.Rect(0,0,new_doc[new_page].rect.width,new_doc[new_page].rect.height-16)
        assert same_page(old_doc[old_page], new_doc[new_page], clip), label
        assert {l.get('uri') for l in old_doc[old_page].get_links() if l.get('uri')} == {l.get('uri') for l in new_doc[new_page].get_links() if l.get('uri')}, label
        preserved_pages.append(dict(label=label,original_page=old_page+1,current_page=new_page+1,pixels_equal_above_footer=True,external_citations_equal=True))
    (QA/'research-materials-preservation.json').write_text(json.dumps(dict(base_commit=base_commit,pdf_sha256=digest(PDF),preserved_pages=preserved_pages,comparison='3x pixels excluding bottom 16 PDF points; source-frame checks additionally preserve all scientific content',hbf_table6='Source unchanged except explicit MoE scope note; all values and charts frozen'),indent=2)+'\n')
    (QA/'research-materials-frame-baseline.json').write_text(json.dumps(dict(commit=base_commit,scope='Frozen source frames checked against starting commit; current source includes only authorized revision',unchanged_labels=['MEMORY','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES'],scope_note_only_labels=['PLACEMENT','PLACEMENTENERGY'],current_order=['COVER']+LABELS,sha256={label:hashlib.sha256(frame.encode()).hexdigest() for label,frame in current.items()}),indent=2)+'\n')
    (QA/'research-materials-geo-validation.json').write_text(json.dumps(dict(baseline_commit=base_commit,pdf_sha256=digest(PDF),current_page=3,label='GEO',preserved_scientific_claims=['Shared global snapshot and independent regional scheduling','Operational carbon only','A100-calibrated models'],authorized_change='Research direction now emphasizes calibrated workload-aware GPU/memory costs for routing; no total-carbon result claimed',primary_source='https://arxiv.org/abs/2610.14571v1'),indent=2)+'\n')
    (QA/'research-materials-helix-validation.json').write_text(json.dumps(dict(baseline_commit=HELIX_BASE,pdf_sha256=digest(PDF),changed_page=5,label='HELIX',figure=str(HELIX_FIGURE.relative_to(REPO)),figure_sha256=digest(HELIX_FIGURE),zip_asset_bytes_identical=True,other_19_pages_excluding_geo_green_cache_title_updates=dict(text_equal=True,pixels_equal_at_3x=True,annotations_equal=True),local_zip_parity=True),indent=2)+'\n')
    (QA/'validation.md').write_text("# Research Materials validation\n\n"
        "- PASS: 22 widescreen pages; Thank You at 16, supplements at 17–22.\n"
        "- PASS: two local and two extracted ZIP pdfLaTeX passes; no warnings.\n"
        "- PASS: local/ZIP text, pixels and annotations match.\n"
        "- PASS: four index cards (Previous Work and Research Background; Workload and Resource Characteristics; Power- and Carbon-Aware GPU Scheduling; Experimental Environment and Evaluation) target pages 3, 7, 12 and 14; no HBM/HBF wording in the card text or takeaway; embodied carbon is supplementary.\n"
        "- PASS: backup round trips, bounds, evidence values and unchanged evidence frames.\n"
        "- PASS: all text/image bounds fit; preserved evidence and new proposal contracts pass.\n"
        "- PASS: Helix Figure 3 retains original resolution and aspect ratio; ZIP asset bytes match.\n"
        "- PASS: 14 pages outside Carbon-SLO/GreenCache/Helix/ThunderServe and the refocused pages 1, 2, 7, 8 match commit 3f90a20 in text, 3x pixels and annotations.\n"
        "- PASS: Slide 1 contains only the new title and subtitle (no presenter, advisor, institution or label), centered; Slide 7 is a three-row workload table without HBM/HBF; Slide 8 is three stacked research cards without HBM/HBF, MoE, Attention/Expert, or novelty claims; slides 3-6 source frames are byte-identical to the pre-refocus versions.\n"
        "- PASS: ThunderServe slide (page 6) uses ThunderServe Figure 5 with only the printed caption removed (pixel-identical to the original top 440 rows); Table 3 values and HBM/HBF content are absent from the slide; Figure 5 is included in the Overleaf ZIP.\n"
        "- Note: the page-6 frame is an authorized redesign, so it is excluded from the frozen-baseline and page-pixel comparisons and checked by the explicit ThunderServe contract instead.\n")
    print('PASS: 22 pages; warning-free local/ZIP builds; navigation and preserved-content checks.')
if __name__=='__main__':main()
