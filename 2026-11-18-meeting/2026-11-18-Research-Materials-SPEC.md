# Research Materials specification and evidence register

Meeting: November 18, 2026. Author: Yu-Jui Liang. Advisor: Hsiang-Yun Cheng. National Taiwan University / Academia Sinica.

Repository: https://github.com/LiangYuJUI/LLM-Serving-Slides.git
Initial branch: `main`, clean working tree. Inspected local HEAD: `5de69e65dadb7028ca55d10accff91f3183b9c69`. This records the local checkout, not a claim that the remote has no newer commits. Access date for all sources: **2026-11-13 (Asia/Taipei)**.

## Scope and design

Standalone pdfLaTeX Beamer deck: unnumbered cover plus five content slides, six PDF pages. Scope is HBM/HBF embodied-carbon evidence only. The final slide connects to the existing proposed research direction, without adding future-topic sections or claiming completed simulation work. Speaker script targets 4–5 minutes, excluding Q&A.

Madrid, 16:9, Latin Modern, 0.48 cm text margins and inherited title/footer geometry follow the November 11 Research Direction source and GreenCache design. Palette: Ink #243748, Muted #667B8B, Accent #347E74, AccentBlue #507DAD, SoftMint #E6F4EE, SoftLilac #F1EEF8, Paper #FBFCFE. Reference PDF content page 1 rendered and visually inspected. New charts and architecture are native TikZ. Both quantitative charts start at zero, without log scaling or broken axes. No external assets are required by the TeX source.

Shared components: `source`, `takeaway`, `card`, `researchquestion`, `carbonchart`, color definitions and TikZ styles. `inserttotalframenumber` updates the footer automatically as content frames are appended; the cover uses `noframenumbering`. Update the build script's five-content-slide acceptance assertion when intentionally expanding scope. No Main/Backup division or Discussion Index.

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

The y-axis on slide 3 is **kg CO2e / nominal capacity unit**. This is an arithmetic index based on the label numerals, not a physical-unit-harmonized carbon intensity. No assumption that GB equals GiB is made. The explicit units remain beside each bar.

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

Run `python3 2026-11-18-meeting/scripts/build_research_materials.py` from the repository root (or use an absolute script path from elsewhere). Dependencies: Python 3, PyMuPDF, Pillow, pdfLaTeX with Beamer/TikZ/Latin Modern. In this session dependencies were isolated in `/tmp/reel-research/venv`; no existing build script or environment was modified.

The script compiles twice locally and twice using only a copied TeX file in a clean temporary directory. It checks pixel/text/link parity, six-page count, 16:9 ratio, automatic numbering, clickable source URIs, text bounds, numeric labels and formulas, and absence of TeX warnings. It renders all pages at 3x resolution and a montage. Output PNGs are named `output/qa/pages/research-materials-01.png` through `-06.png`, deliberately avoiding existing Carbon–SLO `page-*.png` files. No existing QA report is replaced.

Final automated and visual results are recorded in `output/qa/validation.md`. Visual review is required in addition to compilation. Original repository-file SHA-256 values were captured before authoring and are checked before completion. Only new Research Materials outputs are staged in the local commit; no remote push is authorized or performed.

## Completed QA results (2026-11-13)

PASS: four total pdfLaTeX passes (two local, two source-only isolated), zero warnings/overfull boxes, six 16:9 pages, unnumbered cover and 1/5–5/5 content numbering. Required numeric labels, formulas, full research title and source links pass automated checks. Local and isolated renders/text/links agree. Six page PNGs and montage generated and visually inspected, including re-inspection of all changed pages after correcting Beamer's initial-paragraph handling. No observed overlap or clipping. PDF SHA-256: `4c8a98cb3af3966102ce7777e9cc6b694732475731ca3cb660e7334b9114fa15`. All 11,058 original files match the pre-authoring SHA-256 snapshot. The standalone build and visual QA are complete; source-unit harmonization and independent inventory-to-GWP reproduction remain explicitly unresolved scientific limitations, not omitted build work.
