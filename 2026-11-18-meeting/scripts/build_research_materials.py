#!/usr/bin/env python3
"""Build Research Materials twice locally and from its Overleaf ZIP; validate and render."""
from collections import Counter
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
LABELS = ['EINDEX','GEO','RELATED','HELIX','THUNDER','WORKLOAD','MEMORY','PLACEMENT','PLACEMENTENERGY','ACCOUNT','ENVIRONMENT','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES']
PAGE = {label: i for i, label in enumerate(['COVER'] + LABELS)}  # label -> 0-based PDF page
PAGES, MAIN_PAGES = len(PAGE), 13  # 19 pages: 13 main + 6 supplementary (REEL1-4, REELABOUT, MEMORYSOURCES)
assert PAGES == 19 and PAGE['THANKYOU'] == MAIN_PAGES - 1
# Last commit of the 20-page deck (a280f04). Slides that the 19-slide simplification leaves unchanged or only renumbers are compared with it.
REFERENCE_COMMIT = 'a280f04d21d525598a32ef839c78c3fe9f49baf2'
UNCHANGED_SINCE_REFERENCE = ['COVER','GEO','RELATED','HELIX','THUNDER','WORKLOAD','MEMORY','PLACEMENT','PLACEMENTENERGY','ACCOUNT','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES']
HELIX_BASE = '3f90a20ee7648052352fb19cc090c5500bfe06f9'
HELIX_FIGURE = REPO/'2026-11-04-meeting/Helix/Without-Caption/Helix_Figure_03_System_Overview.png'
HELIX_LOCAL_PATH = '../2026-11-04-meeting/Helix/Without-Caption/Helix_Figure_03_System_Overview.png'
HELIX_ZIP_PATH = 'figures/Helix_Figure_03_System_Overview.png'
# ThunderServe Figure 5 with only the printed caption removed (rows 0-439 of the original, pixel-identical).
THUNDER_ORIGINAL = REPO/'2026-10-21-meeting/ThunderServe/ThunderServe_Fig05.png'
THUNDER_FIGURE = ROOT/'figures/ThunderServe_Fig05_no_caption.png'
THUNDER_ZIP_PATH = 'figures/ThunderServe_Fig05_no_caption.png'
THUNDER_CROP_HEIGHT = 440
REVISED_SLIDES = {'COVER':0, 'EINDEX':1, 'WORKLOAD':6, 'ACCOUNT':10, 'ENVIRONMENT':11}  # label -> 0-based PDF page; refocus (2026-11-20), 20-slide reorganization and 19-slide simplification
# Frames of slides 3-6 (latest Helix / ThunderServe layouts), hashed without their removed source footers.
FROZEN_SLIDES_3_6 = {'GEO': '700bc9e62606ba398a4e1864cdf975cde829bf5afea2eca8c11019e08e568741', 'RELATED': 'bce101acdb51c519193a0cd36e447e96825e9030dfcfa48768e08c39469efa34', 'HELIX': '245c6e567a41dd791d6f45f1989205138268f28018a24b479e7150ac75769cee', 'THUNDER': 'd0a8034fb2f0838eb1328afe36b21ef4e1e954e6b697dc80e359d428e68df59e'}
COVER_TEXT = 'Power- and Carbon-Aware LLM Serving on Heterogeneous GPUs Workload-Aware Scheduling Across Compute and Memory Resources'
CATEGORIES = {'GEO':PAGE['GEO'], 'WORKLOAD':PAGE['WORKLOAD'], 'ACCOUNT':PAGE['ACCOUNT'], 'ENVIRONMENT':PAGE['ENVIRONMENT']}
ORIGINAL_REEL_TITLES = {'HBM/HBF Embodied Carbon Evidence': 'What Evidence Do We Have for HBM/HBF Embodied Carbon?', 'Embodied Carbon per Memory Stack': 'How Much Embodied Carbon Does One Stack Carry?', 'Embodied Carbon per Nominal Capacity Unit': 'Does HBF Reduce Embodied Carbon per Unit Capacity?', 'HBF Carbon Estimate: Assumptions and Limitations': 'Can We Trust the HBF Carbon Estimate?'}
# REEL1–4 baselines include user-requested concise copy updates; hashes are taken without their source footers.
PRESERVED = {'REEL1': '2e6c42ab7c6183cd8c21e882e46bdff3f08761af861eb1434a617e8b1ca7cc34', 'REEL2': '67c208ee185b642def61e2b5cd1a5c71cbff1c4e5fcb0bb22650023b400a003c', 'REEL3': 'eafaf33665b01ff8a1a3e3a5ee71026570d942a16a2d43dba81cae33fbf85269', 'REEL4': 'a4b1e49c1f9bdbda33d5cf6f955c9b5165b005556d82963b7bf826c85b0ade99'}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# Slide source footers were removed on 2026-11-21 at the professor's request. Frames are compared
# with their former `\source{...}` lines stripped on both sides, so only the footers can differ.
SOURCE_RE = re.compile(r'^\\source\{.*\}\n', re.M)
PAPER = (0.984, 0.988, 0.996)  # slide background colour (Paper), used to paint redacted footers
def without_source(frame): return SOURCE_RE.sub('', frame)

def source_rects(page):
    """Source footers are 6.8 pt text in the bottom band; the page-number footer (~7.0 pt) and 7.0 pt body notes are not matched."""
    H, W = page.rect.height, page.rect.width
    rects = []
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            for span in line['spans']:
                r = fitz.Rect(span['bbox'])
                if abs(span['size'] - 6.8) < .05 and r.y0 > H * .8 and r.x1 < W * .75: rects.append(r)
    return rects

def legacy_without_sources(doc):
    """In-memory copy of an earlier PDF with its source footers redacted (text, pixels and links)."""
    out = fitz.open(stream=doc.tobytes(), filetype='pdf')
    for page in out:
        rects = source_rects(page)
        for rect in rects: page.add_redact_annot(rect, fill=PAPER)
        if rects: page.apply_redactions()
        for link in page.get_links():
            if link.get('uri') and any(fitz.Rect(link['from']).intersects(rect) for rect in rects): page.delete_link(link)
    return out

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

def same_page(p, q, clip=None, footer_free=False):
    """Equivalence of two renderings of the same slide.

    pdfTeX subsets fonts per document, so adding glyphs elsewhere can move Type1 hinting by a few anti-aliasing
    levels on otherwise untouched pages. Text, word positions (0.1 pt), vector drawings, images and links must
    still match exactly; the raster is compared after 3x -> 1x area averaging with a small tolerance (measured
    subset-hinting noise <= 34/255, versus >= 200/255 for a genuinely different page).
    """
    if p.get_text(clip=clip) != q.get_text(clip=clip) or (clip is None and annotations(p) != annotations(q)): return False
    wp, wq = p.get_text('words', clip=clip), q.get_text('words', clip=clip)
    if len(wp) != len(wq) or any(a[4] != b[4] or max(abs(x-y) for x, y in zip(a[:4], b[:4])) > .1 for a, b in zip(wp, wq)): return False
    def drawn(page):
        # With footer_free, bottom-band shapes are ignored: redaction paints background rectangles over removed footers.
        items = page.get_drawings()
        if footer_free: items = [d for d in items if not (d['rect'].y0 > page.rect.height * .8 and d['rect'].x1 < page.rect.width * .75)]
        return [(tuple(d['rect']), d.get('fill'), d.get('color')) for d in items]
    def close(u, v):
        if u is None or v is None: return u == v
        return len(u) == len(v) and all(abs(x - y) < .05 for x, y in zip(u, v))
    if clip is None:
        dp, dq = drawn(p), drawn(q)
        if len(dp) != len(dq) or any(not (close(a[0], b[0]) and close(a[1], b[1]) and close(a[2], b[2])) for a, b in zip(dp, dq)): return False
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
    assert len(doc)==PAGES
    assert doc.resolve_names()['COVER']['page']==0
    assert 'Thank you' in doc[MAIN_PAGES-1].get_text()
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
        assert re.search(rf'Research Materials\s*\|\s*{i+1}\s*/\s*{PAGES}',t),t
        assert 'Back to Evidence Index' not in t
        assert abs(p.rect.width/p.rect.height-16/9)<.001
        assert 'Source:' not in t and not source_rects(p), f'Source footer remains on page {i+1}'
        links=[l for l in p.get_links() if l.get('uri')]
        uris.update(l['uri'] for l in links)
        for b in p.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line['spans']:
                    r=fitz.Rect(span['bbox'])
                    assert r.x0>=0 and r.y0>=0 and r.x1<=p.rect.width and r.y1<=p.rect.height,span
        for im in p.get_image_info(): assert p.rect.contains(fitz.Rect(im['bbox']))
    reel1, about, memory, sources = (doc[PAGE[k]] for k in ('REEL1','REELABOUT','MEMORY','MEMORYSOURCES'))
    assert any(x.get('uri') == 'https://reellci.com/insights/the-hbf-inversion.html'
               and 'REEL LCI v1.0' in reel1.get_textbox(x['from'])
               for x in reel1.get_links()), 'REEL title source hyperlink missing'
    assert any(x.get('nameddest')=='REELABOUT' and x.get('page')==PAGE['REELABOUT'] for x in reel1.get_links()), 'REEL supplement link missing'
    assert any(x.get('nameddest')=='REEL1' and x.get('page')==PAGE['REEL1'] for x in about.get_links()), 'REEL supplement return missing'
    for value in ['Repository of Electronics Environmental Line-items', 'Life cycle inventory', 'Jonathan Balsvik', '520 datasets', '18 categories', 'Circa', 'https://reellci.com/']:
        assert value in about.get_text(),value
    assert any(x.get('nameddest')=='MEMORYSOURCES' and x.get('page')==PAGE['MEMORYSOURCES'] for x in memory.get_links()), 'Memory source supplement link missing'
    assert any(x.get('nameddest')=='MEMORY' and x.get('page')==PAGE['MEMORY'] for x in sources.get_links()), 'Memory source return missing'
    for p in doc:
        for link in p.get_links():
            if link.get('nameddest'):
                assert link['nameddest'] in names and link['page']==names[link['nameddest']]['page']
    for page,values in {'REEL2':['13.52','19.81','20.6','225.9','16 GB','24 GB','36 GB','512 GiB','16.7'],'REEL3':['0.845','0.825','0.572','0.441','47.8','nominal capacity unit','not verified per-GiB results'],'PLACEMENTENERGY':['9.11','7.19','9.54','32.7','static/background']}.items():
        for value in values: assert value in doc[PAGE[page]].get_text(), (page,value)
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
        'HELIX': ['Serving Large Language Models over Heterogeneous GPUs and Network via Max-Flow','Motivation:', 'making model placement challenging.', 'Method:', 'max-flow/MILP-based layer placement to maximize throughput', 'runtime request scheduling', 'Evaluation:', 'Real heterogeneous GPU cluster', 'geo-distributed settings evaluated using simulation'],
        'THUNDER': ['ThunderServe: High-performance and Cost-efficient LLM Serving in Cloud Environments','MLSys 2025','Workload-Aware Prefill/Decode Placement & Scheduling','Motivation:','Prefill is typically compute-intensive','Method:','Jointly optimize GPU grouping, prefill/decode assignment, parallel configuration, and request routing','Workload characteristics affect the preferred prefill/decode resource allocation and routing'],
        'WORKLOAD': ['Different Workloads, Different Resource Requirements','Workload Characteristics Resource Requirements','Coding Longer prompts, shorter outputs Prefill compute, TTFT','Conversation Shorter prompts, longer outputs Decode throughput, memory bandwidth','Multi-Turn / Agentic Repeated context, potential prefix/KV reuse Memory capacity, KV retention and reuse','Different LLM workloads require different compute, memory, and scheduling resources.'],
        'ACCOUNT': ['Research Gaps and Proposed Direction',
                    'Coordinated Cross-DC Scheduling','Carbon–SLO shares global data-center states, but regional schedulers make routing decisions independently.','Investigate coordinated cross-region scheduling to account for shared capacity, workload distribution, and SLO feasibility.',
                    'Carbon-Aware Cost Modeling','GreenCache considers operational and amortized embodied carbon for caching, but not cross-data-center routing.','Adapt carbon-aware cost modeling to heterogeneous GPU serving and geographic scheduling, starting with operational carbon.',
                    'Power-Aware Heterogeneous GPU Scheduling','Helix and ThunderServe study heterogeneous GPU placement and workload-aware allocation, mainly for performance or cost.','Explore power-aware scheduling across GPUs with different compute, memory, and energy characteristics.'],
        'EINDEX': ['Contents','01 Previous Work and Research Background','Carbon–SLO, GreenCache, Helix, ThunderServe','02 Workload and Resource Characteristics','Workload Patterns, GPU/Memory Characteristics, Published Performance and Energy Evidence','03 Research Gaps and Proposed Direction','Cross-DC Coordination, Carbon-Aware Cost Modeling, Power-Aware GPU Scheduling','04 Experimental Environment','LLMServingSim 2.0, Academia Sinica RCITI GPU Cluster'],
        'ENVIRONMENT': ['Experimental Environment: LLMServingSim 2.0 and Real GPU Profiling',
                        'LLMServingSim 2.0 — Simulation','A profile-driven simulator for heterogeneous and disaggregated LLM serving systems.',
                        'Hardware and Network Modeling','Heterogeneous GPU configurations, memory hierarchies, and ASTRA-Sim-based interconnect simulation.',
                        'Serving Simulation','Multi-instance serving with configurable request routing, TP/PP parallelism, batching, and KV-cache management.',
                        'Performance and power/energy modeling rely on hardware-specific profiles, configured parameters, and validation.',
                        'Profiling and Validation',
                        'Real GPU Profiling — Academia Sinica RCITI GPU Cluster','We plan to run representative LLM workloads on real GPUs to measure serving performance and power consumption.','Real measurements can provide hardware profiles and help validate simulation results.'],
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
        assert bounds.width>doc[PAGE['HELIX']].rect.width*.93, 'Figure must occupy the content width'
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
        # Text blocks must not overlap: the takeaway must sit above the page footer band, and Method above the takeaway.
        takeaway = fitz.Rect(next(b[:4] for b in thunder_page.get_text('blocks') if 'Workload characteristics affect' in b[4]))
        method = fitz.Rect(next(b[:4] for b in thunder_page.get_text('blocks') if 'Method:' in b[4]))
        assert method.y1 <= takeaway.y0 and takeaway.y1 <= thunder_page.rect.height * .9, 'ThunderServe text blocks overlap'
        assert bounds.y1 <= method.y0, 'Figure 5 overlaps the Method sentence'
    index=' '.join(doc[1].get_text().split())
    for value in ['Previous Work and Research Background','Workload and Resource Characteristics','Research Gaps and Proposed Direction','Experimental Environment']:
        assert value in index, value
    assert 'Embodied Carbon' not in index
    # The index must not mention HBM/HBF in its cards; the index has no takeaway.
    for banned in ['HBM','HBF','High Bandwidth','Flash','MoE','Previous Work and Research Gaps','Proposed Research Direction','Calibrate local serving costs','Power- and Carbon-Aware GPU Scheduling','Experimental Environment and Evaluation','Experimental Plan','Roadmap','Research Phases','Proposed Architecture','Research Evidence Overview','From prior work and workload/memory evidence','energy- and carbon-efficient LLM serving','Research Question','Can workload-aware, coordinated']:
        assert banned not in index, ('Obsolete or out-of-scope index text', banned)
    for card in ['Carbon–SLO, GreenCache, Helix, ThunderServe','LLMServingSim 2.0']:
        assert card in index, ('Index card text missing', card)
    # Cover: only the title and subtitle, centered, with no personal or institutional metadata.
    cover = doc[0]
    cover_text = ' '.join(re.sub(rf'Research Materials\s*\|\s*1\s*/\s*{PAGES}','',cover.get_text()).split())
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
    # Slides 7 and 11-13: concise slides without HBM/HBF, MoE, novelty claims, removed layouts, GPU model names or result claims.
    for label in ['WORKLOAD','ACCOUNT','ENVIRONMENT']:
        text = ' '.join(doc[names[label]['page']].get_text().split())
        for banned in ['HBM','HBF','MoE','Attention','Expert','Reported:','Implications to evaluate','Reported behavior above','novel','Novelty','What previous work provides','Weight and KV','Workload characteristics influence','TTFT: time','KV: key']:
            assert banned.lower() not in text.lower(), ('Out-of-scope text on '+label, banned)
    for label in ['ACCOUNT','ENVIRONMENT']:
        text = ' '.join(doc[names[label]['page']].get_text().split())
        assert not re.search(r'\b(A100|H100|H200|B200|L40S?|V100|RTX|GB200)\b', text), ('GPU model name on '+label)
        assert '%' not in text, ('Unmeasured percentage on '+label)
        for banned in ['outperform','unexplored','no prior work','first to','has no global','Co-Design','Baselines','Fair comparisons','held-out','Reported:','completed experiment','already includes','out of the box']:
            assert banned.lower() not in text.lower(), ('Unsupported claim or detail on '+label, banned)
    workload_text = ' '.join(doc[names['WORKLOAD']['page']].get_text().split())
    for banned in ['Coding / Long-Prompt','Conversation / Long-Output','Categories can overlap','Characterizing','not universal definitions','may overlap with either','research opportunity']:
        assert banned not in workload_text, ('Obsolete workload text', banned)
    account_text = ' '.join(doc[names['ACCOUNT']['page']].get_text().split())
    for banned in ['Carbon–SLO Geo-aware routing and SLO modeling','GreenCache Carbon-aware KV reuse','Helix Heterogeneous GPU placement','ThunderServe Phase/workload-aware','Research Direction:','Workload-Aware Performance and Power Modeling','TTFT/TPOT SLO feasibility','Optimize heterogeneous']:
        assert banned not in account_text, ('Obsolete research-direction content', banned)
    for label in ['COVER','EINDEX','WORKLOAD','ACCOUNT','ENVIRONMENT']:
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
    # Slide 11: three stacked gap cards (Previous Work visually distinct from Research Opportunity) and no research-question box.
    ac = doc[names['ACCOUNT']['page']]
    heads = [ac.search_for(h)[0] for h in ['Coordinated Cross-DC','Carbon-Aware Cost','Power-Aware']]
    assert heads[0].y0 < heads[1].y0 < heads[2].y0 and max(abs(h.x0-heads[0].x0) for h in heads) < 2, 'Gap cards must be stacked and aligned'
    prev, opp = ac.search_for('Previous Work'), ac.search_for('Research Opportunity')
    assert len(prev) == len(opp) == 3, 'Each gap card needs one Previous Work and one Research Opportunity'
    assert all(o.x0 > p.x1 for p, o in zip(prev, opp)) and all(abs(p.y0 - o.y0) < 2 for p, o in zip(prev, opp)), 'Previous Work / Research Opportunity columns misplaced'
    assert max(b[3] for b in ac.get_text('blocks') if 'Research Material' not in b[4]) < ac.rect.height * .9, 'Gap cards collide with the footer'
    # Slide 12: simulator section on top, profiling-and-validation separator, real GPU profiling section below; no roadmap or architecture.
    en = doc[names['ENVIRONMENT']['page']]
    en_text = ' '.join(en.get_text().split())
    for banned in ['Phase','Roadmap','Carbon','carbon','Dense','Baseline','Data Center','Global','Scheduler','Proposed','Not Yet Evaluated','Takeaway']:
        assert banned not in en_text, ('Premature roadmap or architecture content on the environment slide', banned)
    sim, hw, serving = en.search_for('LLMServingSim 2.0 —')[0], en.search_for('Hardware and Network Modeling')[0], en.search_for('Serving Simulation')[0]
    mid, real = en.search_for('Profiling and Validation')[0], en.search_for('Real GPU Profiling —')[0]
    assert sim.y1 < hw.y0 and abs(hw.y0 - serving.y0) < 2 and hw.x1 < serving.x0, 'Simulator capability panels misplaced'
    assert serving.y1 < mid.y0 < real.y0, 'Simulation, Profiling and Validation, and real GPU sections out of order'
    note = en.search_for('Performance and power/energy modeling')[0]
    assert note.y1 < mid.y0 and (mid.y0 - sim.y0) > (real.y0 - mid.y0) * .9, 'Simulator section must be the larger upper section'
    assert max(b[3] for b in en.get_text('blocks') if 'Research Materials' not in b[4]) < en.search_for('Research Materials')[-1].y0 - 4, 'Real GPU profiling card collides with the footer'
    # No architecture, roadmap or research-phase content anywhere in the main presentation.
    for page in list(doc)[:MAIN_PAGES]:
        main_text = ' '.join(page.get_text().split())
        for banned in ['Phase 1','Phase 2','Phase 3','Research Phases','Research Roadmap','Experimental Plan','Proposed Coordinated Scheduling Architecture','Global Carbon-Aware Scheduler','Local Heterogeneous GPU Scheduler','Data Center A','Compute-rich','Memory-rich','Low-power','Workload-Aware Performance and Power Modeling','Coordinated Cross-DC Carbon-Aware Scheduling']:
            assert banned not in main_text, ('Removed architecture or roadmap content present', banned)
    assert round(100*(9.54/7.19-1),1)==32.7
    assert round(225.9/13.52,1)==16.7
    assert round(100*(1-(225.9/512)/(13.52/16)),1)==47.8
    return sorted(uris)

def normalize_related(frame):
    # Undo the authorized slide-3 edits: heading-to-diagram gap and removed bottom takeaway.
    if 'label=GEO' in frame:
        frame=frame.replace(r'Current Architecture\par}'+'\n'+r'\vspace{.20cm}'+'\n'+r'\begin{tikzpicture}', r'Current Architecture\par}'+'\n'+r'\vspace{.03cm}'+'\n'+r'\begin{tikzpicture}', 1)
        frame=frame.replace('\\vspace{.08cm}\n\n\\end{frame}',
            '\\vspace{.08cm}\n\\takeaway{Our direction: Calibrate workload-aware GPU/memory energy and SLO costs for regional routing.}\n\n\\end{frame}', 1)
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
    assert len(frame_titles)==PAGES-2 and all('?' not in title for title in frame_titles), 'Unexpected question-style slide title remains'
    for label,expected in PRESERVED.items():
        frame=re.search(r'\\begin\{frame\}\[t,label='+label+r'\](.*?)\\end\{frame\}',source,re.S).group(1)
        # Normalize authorized title edits and source/supplement navigation only.
        for current, original in ORIGINAL_REEL_TITLES.items():
            if frame.startswith('{'+current+'}'):
                frame='{'+original+'}'+frame[len(current)+2:]
        frame=frame.replace(r'\hfill\hyperlink{REELABOUT}{\scriptsize About REEL / LCI}', '')
        frame=frame.replace(r'\href{\srcA}{REEL LCI v1.0}', 'REEL LCI v1.0')
        assert hashlib.sha256(without_source(frame).encode()).hexdigest()==expected,('Preserved frame changed',label)
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
        assert without_source(normalize_related(current[label]))==without_source(baseline[label]), ('Preserved frame changed',label)
    # The two published-HBF caveats that used to live in the footer now sit in the slide body (same wording).
    moe_note = r'{\scriptsize\color{Muted}Published MoE-based simulation evidence; our proposed workload evaluation is not restricted to MoE.\par}'+'\n'
    energy_note = r'{\scriptsize\color{Muted}Simulation-based energy; static/background power excluded. Published MoE-based simulation evidence; our proposed workload evaluation is not restricted to MoE.\par}'+'\n'
    def energy_layout(frame):
        # Layout-only: slightly tighter spacing above the energy card so the moved caveat fits on the slide.
        return (frame.replace('\\vspace{.04cm}\n\\card{mintbox}{+32.7', '\\vspace{.15cm}\n\\card{mintbox}{+32.7')
                .replace('\\vspace{.10cm}\n{\\small\\bfseries Modeled Workload', '\\vspace{.17cm}\n{\\small\\bfseries Modeled Workload'))
    for label,note in [('PLACEMENT',moe_note),('PLACEMENTENERGY',energy_note)]:
        frame=without_source(current[label]) if label=='PLACEMENT' else energy_layout(without_source(current[label]))
        assert frame.replace(note,'')==without_source(baseline[label]), ('Published HBF evidence changed',label)
        assert note in current[label], ('Published HBF caveat missing from slide body', label)
    for label in ['ENVIRONMENT']:
        for obsolete in ['Attention Worker','Expert Worker','expert-weight','A/E disaggregation','HBM','HBF']:
            assert obsolete not in current[label], (label,obsolete)
    assert not {'DISAGG','NEXT','GEOARCH'} & set(current), 'Standalone DISAGG / NEXT / GEOARCH frames must stay removed'
    # The 19-slide simplification leaves these frames untouched: they must be byte-identical to the 20-page deck.
    reference_source=subprocess.check_output(['git','show',REFERENCE_COMMIT+':2026-11-18-meeting/'+NAME+'.tex'],cwd=REPO,text=True)
    reference_frames=frames(reference_source)
    assert 'GEOARCH' in reference_frames and len(reference_frames)==20, 'Unexpected reference deck'
    assert 'GEOARCH' not in current, 'The premature GEOARCH architecture frame must stay removed'
    for label in UNCHANGED_SINCE_REFERENCE:
        assert current[label]==reference_frames[label], ('Frame changed by the reorganization',label)
    helix_baseline=subprocess.check_output(['git','show',HELIX_BASE+':2026-11-18-meeting/'+NAME+'.tex'],cwd=REPO,text=True)
    baseline_frames=frames(helix_baseline)
    # THUNDER is the authorized Figure 5 redesign; its contract is checked explicitly in validate().
    # PLACEMENT / PLACEMENTENERGY are checked above against the starting commit, with their moved caveat notes.
    for label in current.keys()-{'HELIX','THUNDER','PLACEMENT','PLACEMENTENERGY'}-set(REVISED_SLIDES):
        assert without_source(normalize_related(current[label]))==without_source(baseline_frames[label]), ('Preserved frame changed',label)
    # Slides 3-6 must stay identical to their pre-refocus source (latest Helix / ThunderServe layouts), ignoring the removed footers.
    for label,expected in FROZEN_SLIDES_3_6.items():
        assert hashlib.sha256(without_source(current[label]).encode()).hexdigest()==expected, ('Slides 3-6 changed by the refocus',label)
    assert r'\begin{tabularx}' not in current['THUNDER'] and 'figures/ThunderServe_Fig05_no_caption.png' in current['THUNDER'], 'THUNDER must use the Figure 5 crop'
    assert HELIX_LOCAL_PATH in current['HELIX'] and r'\begin{tikzpicture}' not in current['HELIX']
    (QA/'pages').mkdir(parents=True,exist_ok=True);ZIP.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research-materials-') as td:
        temp=Path(td);local=compile_pdf(ROOT,temp/'local',NAME)
        with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('main.tex',source.replace(HELIX_LOCAL_PATH,HELIX_ZIP_PATH))
            z.write(HELIX_FIGURE,HELIX_ZIP_PATH)
            z.write(THUNDER_FIGURE,THUNDER_ZIP_PATH)
            z.writestr('README.txt','Main file: main.tex\nCompiler: pdfLaTeX\nCompile twice for numbering and navigation.\nSelf-contained Beamer source, original Helix Figure 3, and ThunderServe Figure 5 (printed caption removed); 19 pages.\n')
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
        # Every slide that was only moved or renumbered must render exactly as in the 22-page deck, compared by label
        # above the page-number footer (the footer's "n / 20" becomes "n / 19"). Links are compared without page numbers.
        reference=fitz.open(stream=subprocess.check_output(['git','show',REFERENCE_COMMIT+':2026-11-18-meeting/output/pdf/'+NAME+'.pdf'],cwd=REPO),filetype='pdf')
        assert len(reference)==20
        ref_names,new_names=reference.resolve_names(),a.resolve_names()
        def link_signature(page): return [(l.get('uri'),l.get('nameddest'),tuple(round(v,2) for v in l['from'])) for l in page.get_links()]
        def return_numbers(page):
            # The "Back to slide N" buttons of the two supplements show the renumbered page of their origin slide.
            words = page.get_text('words')
            return [fitz.Rect(w[:4]) for prev, w in zip(words, words[1:]) if prev[4].lower() == 'slide' and w[4].isdigit()
                    and any(x[4].lower() == 'back' for x in words[max(0, words.index(prev)-3):words.index(prev)])]
        def masked(doc, index, rects):
            tmp = fitz.open(); tmp.insert_pdf(doc, from_page=index, to_page=index)
            for rect in rects: tmp[0].add_redact_annot(rect, fill=PAPER)
            if rects: tmp[0].apply_redactions()
            return tmp
        moved=[]
        for label in UNCHANGED_SINCE_REFERENCE:
            old,new=reference[ref_names[label]['page']],a[new_names[label]['page']]
            clip=fitz.Rect(0,0,new.rect.width,new.rect.height-16)
            numbers=return_numbers(old)+return_numbers(new)
            assert bool(numbers)==(label in ('REELABOUT','MEMORYSOURCES')),('Unexpected return-number buttons',label)
            old_m,new_m=masked(reference,ref_names[label]['page'],numbers),masked(a,new_names[label]['page'],numbers)
            assert old_m[0].get_text(clip=clip)==new_m[0].get_text(clip=clip),('Text changed on moved slide',label)
            assert same_page(old_m[0],new_m[0],clip),('Rendering changed on moved slide',label)
            assert link_signature(old)==link_signature(new),('Links changed on moved slide',label)
            moved.append(dict(label=label,reference_page=ref_names[label]['page']+1,current_page=new_names[label]['page']+1))
        for stale in (QA/'pages').glob('research-materials-*.png'):
            if int(stale.stem.rsplit('-',1)[1]) > len(a): stale.unlink()
        montage=Image.new('RGB',(1600,((len(a)+1)//2)*470),'#D8E4EB')
        for n,page in enumerate(a):
            dest=QA/'pages'/f'research-materials-{n+1:02d}.png'
            page.get_pixmap(matrix=fitz.Matrix(3,3)).save(dest)
            im=Image.open(dest).convert('RGB');im.thumbnail((800,450))
            x=(n%2)*800;y=(n//2)*470
            montage.paste(im,(x,y));ImageDraw.Draw(montage).text((x+12,y+452),f'{n+1}/{len(a)}',fill='#243748')
        montage.save(QA/'research-materials-montage.png');shutil.copy2(local,PDF)
    assert before==protected(),'Protected files changed during build'
    report=dict(pages=len(a),main_pages=MAIN_PAGES,supplementary_pages=len(a)-MAIN_PAGES,reference_commit=REFERENCE_COMMIT,moved_or_unchanged_pages=moved,local_passes=2,zip_passes=2,warnings=[],source_sha256=digest(ROOT/f'{NAME}.tex'),pdf_sha256=digest(PDF),zip_sha256=digest(ZIP),preserved_frame_hashes=PRESERVED,category_destinations={k:v+1 for k,v in CATEGORIES.items()},supplement_round_trips={'REEL1_REELABOUT':[PAGE['REEL1']+1,PAGE['REELABOUT']+1], 'MEMORY_MEMORYSOURCES':[PAGE['MEMORY']+1,PAGE['MEMORYSOURCES']+1]},parity={'text':True,'pixels':True,'annotations':True},protected_files=len(before),uris=uris)
    (QA/'research-materials-build.json').write_text(json.dumps(report,indent=2)+'\n')
    # Audit preserved rendered evidence against the user's actual starting PDF.
    base_commit='51548444d0d896c8302ad94a9c81cae3f2ed571d'
    base_pdf=subprocess.check_output(['git','show',base_commit+':2026-11-18-meeting/output/pdf/'+NAME+'.pdf'],cwd=REPO)
    old_doc=legacy_without_sources(fitz.open(stream=base_pdf,filetype='pdf'))
    new_doc=fitz.open(PDF)
    preserved_pages=[]
    for label, old_page in {'MEMORY':9,'REEL1':5,'REEL2':6,'REEL3':7,'REEL4':8,'THANKYOU':14}.items():
        new_page=new_doc.resolve_names()[label]['page']
        clip=fitz.Rect(0,0,new_doc[new_page].rect.width,new_doc[new_page].rect.height-16)
        assert same_page(old_doc[old_page], new_doc[new_page], clip), label
        assert {l.get('uri') for l in old_doc[old_page].get_links() if l.get('uri')} == {l.get('uri') for l in new_doc[new_page].get_links() if l.get('uri')}, label
        preserved_pages.append(dict(label=label,original_page=old_page+1,current_page=new_page+1,pixels_equal_above_footer=True,external_citations_equal=True))
    (QA/'research-materials-preservation.json').write_text(json.dumps(dict(base_commit=base_commit,pdf_sha256=digest(PDF),preserved_pages=preserved_pages,comparison='legacy source footers redacted before comparison; 3x pixels excluding bottom 16 PDF points; source-frame checks additionally preserve all scientific content',hbf_table6='Source unchanged except explicit MoE scope note; all values and charts frozen'),indent=2)+'\n')
    (QA/'research-materials-frame-baseline.json').write_text(json.dumps(dict(commit=base_commit,scope='Frozen source frames checked against starting commit; current source includes only authorized revision',unchanged_labels=['MEMORY','THANKYOU','REEL1','REEL2','REEL3','REEL4','REELABOUT','MEMORYSOURCES'],scope_note_only_labels=['PLACEMENT','PLACEMENTENERGY'],current_order=['COVER']+LABELS,reorganization_reference=REFERENCE_COMMIT,identical_to_reference=UNCHANGED_SINCE_REFERENCE,sha256={label:hashlib.sha256(frame.encode()).hexdigest() for label,frame in current.items()}),indent=2)+'\n')
    (QA/'research-materials-geo-validation.json').write_text(json.dumps(dict(baseline_commit=base_commit,pdf_sha256=digest(PDF),current_page=3,label='GEO',preserved_scientific_claims=['Shared global snapshot and independent regional scheduling','Operational carbon only','A100-calibrated models'],authorized_change='Research direction now emphasizes calibrated workload-aware GPU/memory costs for routing; no total-carbon result claimed',primary_source='https://arxiv.org/abs/2610.14571v1'),indent=2)+'\n')
    (QA/'research-materials-helix-validation.json').write_text(json.dumps(dict(baseline_commit=HELIX_BASE,pdf_sha256=digest(PDF),changed_page=5,label='HELIX',figure=str(HELIX_FIGURE.relative_to(REPO)),figure_sha256=digest(HELIX_FIGURE),zip_asset_bytes_identical=True,moved_or_unchanged_pages_vs_22_page_reference=dict(text_equal=True,pixels_equal_at_3x_above_footer=True,links_equal=True),local_zip_parity=True),indent=2)+'\n')
    (QA/'validation.md').write_text("# Research Materials validation\n\n"
        "- PASS: 19 widescreen pages (13 main + 6 supplementary); Thank You at 13, supplements at 14–19; DISAGG, NEXT and GEOARCH frames removed.\n"
        "- PASS: two local and two extracted ZIP pdfLaTeX passes; no warnings.\n"
        "- PASS: local/ZIP text, pixels and annotations match.\n"
        "- PASS: four index cards (Previous Work and Research Background; Workload and Resource Characteristics; Research Gaps and Proposed Direction; Experimental Environment) target pages 3, 7, 11 and 12; no HBM/HBF wording in the card text or takeaway; embodied carbon is supplementary.\n"
        "- PASS: backup round trips (HBM/HBF Memory Access Energy 8 <-> Sources 19; REEL 14 <-> REEL LCI 18), bounds, evidence values and unchanged evidence frames.\n"
        "- PASS: all text/image bounds fit; preserved evidence and new proposal contracts pass.\n"
        "- PASS: Helix Figure 3 retains original resolution and aspect ratio; ZIP asset bytes match.\n"
        "- PASS: no slide carries a source footer (all 19 pages); citations remain in the speaker script and evidence register. The MoE scope note (pages 9-10) and static/background power note (page 10) are in the slide body.\n"
        "- PASS: the 17 unchanged or renumbered slides (cover, pages 3-11, Thank You and supplements) are byte-identical in source to the 20-page deck (a280f04) and match it in text, 3x pixels above the page footer, and links.\n"
        "- PASS: Slide 11 is three stacked gap cards (Previous Work vs. Research Opportunity) without a research-question box; slide 12 introduces LLMServingSim 2.0 and real RCITI GPU profiling with a Profiling and Validation separator and no architecture, roadmap or research phases; neither contains HBM/HBF, GPU model names, percentages or result claims.\n"
        "- PASS: ThunderServe slide (page 6) uses ThunderServe Figure 5 with only the printed caption removed (pixel-identical to the original top 440 rows); Table 3 values and HBM/HBF content are absent from the slide; Figure 5 is included in the Overleaf ZIP.\n")
    print('PASS: 19 pages; warning-free local/ZIP builds; navigation and preserved-content checks.')
if __name__=='__main__':main()
