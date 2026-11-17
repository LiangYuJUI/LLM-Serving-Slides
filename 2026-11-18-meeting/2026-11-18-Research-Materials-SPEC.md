# Research Materials specification and evidence register

Meeting: November 18, 2026. Author: Yu-Jui Liang. Advisor: Hsiang-Yun Cheng. National Taiwan University / Academia Sinica.

Repository: https://github.com/LiangYuJUI/LLM-Serving-Slides.git
Current expansion verified on **2026-11-17 (Asia/Taipei)** from clean `main` at `9d09be3`, equal to `origin/main` after fetch. Original REEL research accessed 2026-11-13; its preserved source register follows below.

## Scope and design

Extend the existing Research Materials source/PDF into exactly **16 pages**, numbered **1/16–16/16**, including the cover as slide 1 and the final Thank you slide. Five evidence categories cover GPU power, HBM/HBF energy, geo scheduling, operational/embodied accounting and disaggregation. This is evidence collection and proposed research, not a completed system evaluation.

Madrid, 16:9, Latin Modern, 0.48 cm margins and original title/footer geometry. Ink #243748, Muted #667B8B, Accent #347E74, AccentBlue #507DAD, SoftMint #E6F4EE, SoftLilac #F1EEF8, Paper #FBFCFE. Preserve `source`, `takeaway`, `card`, `researchquestion`, and `carbonchart`; add compact cards only where needed. New tables and diagrams are native LaTeX/TikZ. Existing carbon charts retain zero baselines and their data. The sole external visual is the original Carbon–SLO Fig. 2 With-Caption PNG, bundled in Overleaf.

## Page and navigation contract

| PDF page | Content | Label | Title / purpose |
|---|---|---|---|
| 1 | 1/16 | COVER | Research Materials & Supporting Evidence |
| 2 | 2/16 | EINDEX | Research Evidence Overview |
| 3 | 3/16 | GPU | LLM Serving Power Across Inference Phases and Workloads |
| 4 | 4/16 | MEMORY | How Much More Energy Does HBF Access Require? |
| 5 | 5/16 | PLACEMENT | Weight Placement and Modeled Serving Energy |
| 6 | 6/16 | GEO | Geo Scheduling Trade-offs in Carbon, Energy and Latency |
| 7 | 7/16 | RELATED | Related Work: Carbon–SLO and FREESH |
| 8 | 8/16 | ACCOUNT | Total Serving Carbon Accounting |
| 9 | 9/16 | REEL1 | HBM/HBF Embodied Carbon Evidence |
| 10 | 10/16 | REEL2 | Embodied Carbon per Memory Stack |
| 11 | 11/16 | REEL3 | Embodied Carbon per Nominal Capacity Unit |
| 12 | 12/16 | REEL4 | HBF Carbon Estimate: Assumptions and Limitations |
| 13 | 13/16 | DISAGG | Proposed Attention/Expert Placement and Energy Costs |
| 14 | 14/16 | NEXT | Research Direction and Next Steps |
| 15 | 15/16 | REELABOUT | REEL LCI: Database Background and Inventory Scope |
| 16 | 16/16 | THANKYOU | Thank you |

Five index cards link to `GPU`, `MEMORY`, `GEO`, `ACCOUNT`, `DISAGG`. All slides except the cover have a visible `Back to Evidence Index` link to `EINDEX`. Links use stable labels, not page-number mechanics. Automatic Beamer numbering includes the cover and closing slide. Four original REEL frame bodies are frozen by SHA-256, excluding only frame labels and global footer. Original pages 2–5 are now pages 9–12.

The [Power/Carbon evidence register](2026-11-18-Power-Carbon-Slide-Evidence.md) is the current 16-slide claim ledger, including exact sources, configurations, denominators, interpretation, limitations and proposal/prior-work status. The following original REEL register is retained for scientific provenance. Its historical slide numbers 1–4 map to current slides 9–12; original final slide 5 is now extended slide 14. The per-capacity chart is now PDF page 11 / slide 11.

## Source register and access results

| ID | Exact URL | Version / evidence used |
|---|---|---|
| A | https://reellci.com/insights/the-hbf-inversion.html | Updated 2026-09-10, explicitly REEL LCI v1.0 (released 2026-08-21). Published screening carbon values and comparison chart. |
| B | https://reellci.com/insights/hbm-footprint-inversion.html | Updated 2026-09-10, explicitly v1.0. HBM3E 12-Hi 36 GB: approximately 20.6 kg CO2e, IPCC 2021 GWP100. |
| C | https://reellci.com/d/hbf-gen1-16hi/ | Current page says release v1.0, UUID 95408b13-60a3-4a44-a48b-9e104a8ccd2b. Architecture, process proxies, data quality, scope, uncertainties. |
| D | https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf | Downloaded successfully with curl after web-tool retrieval failed. Section 4.4.4, PDF page 68 / printed page 66, rendered and inspected. |
| E | https://reellci.com/explorer/?category=memory_components | v1.0 catalogue; public documentation, not full inventory quantities. |
| F | https://reellci.com/d/hbm3-8hi/ | Current v1.0, HBM3 16GB, 8-Hi; component boundary. |
| G | https://reellci.com/d/hbm3-12hi/ | Current v1.0, HBM3 24GB, 12-Hi. |
| H | https://reellci.com/d/hbm3e-12hi/ | Current v1.0, HBM3E 36GB, 12-Hi. |

Methodology downloaded bytes SHA-256: `9ec048a91696086cb2087889dece3abf5fbe8af67c00261c24a0f1cb54f63042`. PDF p. 68 is a physical page index starting at 1; printed p. 66 is the page number displayed in the document. They are not interchangeable.

E lists HBM3 8/12-Hi, HBM3E 8/12-Hi, HBM4 8/12/16-Hi with mature/ramp variants, and HBF Gen 1 16-Hi. Availability here means a catalogue/documentation entry exists; no paid inventory was purchased or claimed as retrieved. No HBM4 carbon number is plotted.

## Exact data and derived values

All carbon inputs below are **REEL LCI model estimates reported in v1.0 insights**, not manufacturer-verified product footprints. Values are reproduced as published, not recomputed from the detailed life cycle inventory. This is neither an independently validated LCA nor a peer-reviewed HBF study.

| Configuration | Source capacity label | kg CO2e / stack | Carbon source | Our division by capacity numeral | Chart label |
|---|---|---:|---|---:|---:|
| HBM3 8-Hi | 16 GB (F and A prose); A chart says GiB | 13.52 | A chart | 13.52 / 16 = 0.845 | 0.845 |
| HBM3 12-Hi | 24 GB (G and B); A chart says GiB | 19.81 | A chart | 19.81 / 24 = 0.8254166667 | 0.825 |
| HBM3E 12-Hi | 36 GB (H and B) | approximately 20.6 | B | 20.6 / 36 = 0.5722222222 | approximately 0.572 |
| HBF Gen 1 16-Hi | 512 GiB (C and A) | 225.9 | A chart | 225.9 / 512 = 0.4412109375 | 0.441 |

No v0.1 results were used. B rounds HBM3 values to 13.5 and 19.8; A gives 13.52 and 19.81. This is consistent with rounding, so the chart retains A's precision without manufacturing extra digits for HBM3E.

The y-axis on current PDF page 11 (original content slide 3) is **kg CO2e / nominal capacity unit**. This is an arithmetic index based on the label numerals, not a physical-unit-harmonized carbon intensity. No assumption that GB equals GiB is made. The explicit units remain beside each bar.

Derived comparisons, always using unrounded inputs:

- Per-stack ratio: `225.9 / 13.52 = 16.7085798817`, displayed 16.7x.
- Nominal capacity numeral ratio: `512 / 16 = 32`. This is not a verified physical capacity ratio.
- Normalized ratio: `(225.9 / 512) / (13.52 / 16) = 0.5221431213`.
- Nominal reduction: `100 * (1 - (225.9 / 512) / (13.52 / 16)) = 47.78568787%`, displayed 47.8%.
- If HBM GB were confirmed decimal, convert to GiB with `GB * 10^9 / 2^30` before division. If it were confirmed a shorthand for binary capacity, the numeric capacities could be used directly. Neither interpretation has been established here, so no converted claim is on the slides.

## Model assumptions, boundaries and conflicts

C uses 232-layer NAND, 65 nm CMOS-peripheral and 28 nm base-logic proxies. A 10.975 x 16 mm device envelope yields 175.6 mm²; the central die-yield proxy is `exp(-0.005 * 175.6) ≈ 0.416`, with 0.670 described as a favorable bound. These are current public dataset assumptions, **not verified reconstruction parameters for A's 225.9**.

C explicitly discloses a die-capacity/area inconsistency, a package outline substituted for measured die geometry, and packaging/material gaps. Package-level interposer, redistribution, organic substrate and assembly are excluded from the stack; they require additional accounting without double counting. Operational electricity is outside this manufacturing boundary. Semiconductor-fab electricity is part of manufacturing, not serving operational energy.

D describes a prospective dataset and an approximate −24%/+32% band, alongside about 243 kWh per component. That energy number is not a carbon value, and no grid factor is inferred to turn it into one. The range's exact application to the article's GWP result cannot be independently established from the public quantities. The optional low/base/high chart is therefore omitted. For transparency, mechanically applying it to 225.9 would give `225.9 * 0.76 = 171.684` and `225.9 * 1.32 = 298.188` kg CO2e. These would be illustrative scenarios, not measured bounds or a confidence interval, and are not used as chart data.

Both A and C display v1.0, but public detailed pages disclose assumptions not reconciled with the article's carbon characterization. The deck distinguishes **published article estimates** from **current dataset assumptions**. Reproducibility of the article from today's inventory remains an open verification item; it is not valid to silently claim they are a single frozen model snapshot.

The source's TRL/sample timing is an authored model status, not an independent assessment of the actual HBF market as of this meeting. The deck does not claim a current commercial-shipment status.

## Claim-to-source mapping

| Slide / claim | Source / location | Evidence type and limitation |
|---|---|---|
| Cover / topic and identity | User's requested identity; A/D | Meeting metadata, not external scientific claim |
| 1 / common framework and available memory families | D Sec. 4.4; E catalogue | Public methodology and listed dataset coverage |
| 1 / HBF lacks production data | C, Sampling procedure; D Sec. 4.4.4 | Source-declared prospective model |
| 1 / preliminary sensitivity use | A screening-level framing plus our judgment | Intended use, not validation guarantee |
| 2 / stack values and capacity labels | A chart; B listed results; E/F/G/H names | Published model outputs, units retained |
| 2 / 16.7x | Formula above | Our calculation |
| 3 / four normalized bars and 47.8% | A/B inputs plus explicit formula above | Our nominal index, not verified per-GiB comparison |
| 3 / capacity cannot establish serving performance | Methodological limitation of capacity-only index | Does not claim measured bandwidth/latency equivalence |
| 4 / current process, geometry, yield assumptions | C Overview | Model proxies, not vendor manufacturing recipe |
| 4 / die-area/bit-density conflict; package gaps | C Limitations and unquantified flows | Model's own disclosure |
| 4 / omitted package burdens | C Production covered; F boundary | Include in system accounting separately |
| 4 / uncertainty band and caution | D PDF p. 68 / printed p. 66; C | Published band; not validated around A's GWP center |
| 5 / proposed attention/expert worker roles | Existing `2026-11-11-Research-Direction.tex` | Research hypothesis; no completed evaluation asserted |
| 5 / total-carbon equation and metrics | Our proposed accounting and existing research direction | Proposed evaluation, not REEL measured system result |

## System accounting interpretation

The final equation defines total carbon over the same declared service workload/window. Allocated embodied carbon requires documented lifetime and hardware-use allocation, counts of GPU/memory/other components, and package boundaries. Operational carbon requires energy and matching electricity carbon intensity. For fair comparisons fix model, precision, request trace and SLO thresholds; report hardware resources explicitly. Do not add stack footprints on top of a GPU footprint that already includes its memory. Do not equate power with energy or claim a lower nominal index proves total savings. Simulator integration, energy calibration and system results are outside this task.

## Build and validation workflow

Run `python3 2026-11-18-meeting/scripts/build_research_materials.py` from any directory using Python with PyMuPDF and Pillow plus pdfLaTeX/Beamer/TikZ/Latin Modern. An isolated environment can be created with `python3 -m venv /tmp/research-materials-qa` then `/tmp/research-materials-qa/bin/pip install pymupdf pillow`.

The existing workflow now compiles twice locally, packages `output/overleaf/Research-Materials.zip` with `main.tex` and original Fig. 2, extracts that ZIP and compiles twice. (No Research Materials ZIP existed in the inspected baseline; CarbonSLO.zip is untouched.) It checks 16 pages, numbering, text/image bounds, named links/visible return links, source URI annotations, numeric evidence, four preserved frame hashes, local/ZIP text/pixel/annotation parity and protected file hashes. It rejects all layout/reference warnings. It renders `research-materials-01.png` through `-16.png` at 3× and a montage.

Deliverables: existing `.tex`, existing PDF path, Traditional Chinese Script, this SPEC, Power-Carbon evidence register, README and scoped Cross-DC backlog updates. QA: `output/qa/validation.md`, `research-materials-build.json`, `research-materials-url-checks.json`, `research-materials-preservation.json`, page PNGs and montage. URL availability is recorded separately from valid clickable PDF annotations. Visual review must inspect every generated page.

## Scientific acceptance

- HBF Table 1 and Tables 6–7 verified in original v2; distinguish assumed pJ/bit, simulated MJ and real measured GPU W.
- Page 5 labels static/background exclusion, hardware difference and no SLO guarantee; Table 7 breakdown uses the correct GLM 1× column.
- FREESH column includes its runtime LLF queue and DVFS, while distinguishing profiled pool planning from explicit batch-state projection.
- No generic “geo + heterogeneity + DVFS is novel” claim. Janus/AFlex operator partitions differ, and MemExplorer quantitative verification remains open.
- Operational energy and embodied component boundaries count each term once. PUE is applied once. Same workload/window/SLO required.
- Four REEL slides retain all values, nominal GB/GiB warning, manufacturing uncertainty, package exclusions and prospective-model status.
- Carbon–SLO, GreenCache and Research Direction PDFs and all unrelated tracked files retain their baseline hashes.

Current final automated/visual findings are recorded in `output/qa/validation.md`; scientific unknowns are listed in the evidence register. Historical six-page QA is superseded by the 16-page build.

## Numbering update

Per user request, slide number equals physical PDF page, including the cover. PDF pages 2–14 retain their content and internal destinations. Page 16 is a simple Thank you / Questions & Discussion closing slide, with an index return link and no scientific claim or source requirement.

Slide 9 source-link update: the `REEL LCI v1.0` card title links directly to the original HBF article, https://reellci.com/insights/the-hbf-inversion.html. Scientific text and rendered appearance remain unchanged. The preserved-frame check normalizes only this authorized hyperlink wrapper and separately verifies the title annotation target.

REEL supplement: slide 9’s `About REEL / LCI` links to named destination `REELABOUT` (slide 15), which returns to `REEL1` (slide 9). The original external article link remains. Supplement statements and the 520/18 v1.0 counts were verified against https://reellci.com/ on 2026-11-17. It describes a database rather than asserting government or academic institutional status.

## Descriptive title update

All 14 content/supplement frame titles use descriptive headings rather than questions. Cover and Thank you are unchanged. REEL scientific content remains frozen; preservation checks normalize the four explicitly authorized title replacements before comparing original frame hashes.


### Slide 9 concise copy update

Slide 9 uses the user-provided research question, three points in each evidence card and concise takeaway. The original article, source citations and supplement navigation remain. REEL1 now has a refreshed frozen hash for this authorized copy; REEL2–4 retain their original baselines.


### Slide 10 concise comparison update

Slide 10 uses the requested screening-estimate subtitle, manufacturing-carbon chart, 16.7× comparison, capacity-difference card and concise takeaway. Axis ticks are 0/60/120/180/240; bar values and capacity labels (16 GB, 24 GB, 36 GB, 512 GiB) remain. Source links and model-estimate qualification remain in the footer. REEL2 frozen hash reflects this authorized update.


### Slide 11 concise nominal-normalization update

Slide 11 uses the user-provided subtitle, GB/GiB qualification and concise 47.8% comparison card. Axis ticks are 0/0.25/0.5/0.75/1. Bar values, capacity labels, units and source links remain. REEL3 frozen hash reflects this authorized update.


### Slide 12 concise assumptions and limitations

Slide 12 uses the user-provided three model assumptions, three limitations, takeaway and two linked sources. REEL4 frozen hash reflects this authorized update. Speaker scripts are not updated for this or future deck revisions, per user preference.


### Slide 4 concise access-energy comparison

Slide 4 uses the user-specified question title (an explicit exception to the earlier descriptive-title preference), publication label, read/write table, units and modeled-data qualification, takeaway and linked Table 1 citation. Ratios are 6.8/3.4 = 2 and 100/3.4 rounded to 29.4. No speaker-script update.
