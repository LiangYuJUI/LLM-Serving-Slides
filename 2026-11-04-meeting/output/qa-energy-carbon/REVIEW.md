# Energy / Carbon Summary — verification (2026-11-04)

## Scope and template

Read latest `origin/main` at `659728d317a4cd52f247ffc204b4ede1233e695c`; local HEAD matched. Reviewed the Helix TeX, README, all 58 PDF pages as rendered contact sheets, and a full-size text slide. Copied the 16:9, 10pt Madrid preamble, Latin Modern fonts, palette, margins, title bar and footer dimensions. Retained inline teal bold `\point` labels; equal-height rows align the two slides. Removed index navigation. Includes one cover and two summary slides. No figures, backup, proposal, or hardware co-design claims.

## Source verification

Primary PDFs downloaded and read (not just prompt or abstract):

- [GreenCache, arXiv:2505.23970v3](https://arxiv.org/pdf/2505.23970v3), linked from the author's publication list. DOI [10.1145/3788087](https://doi.org/10.1145/3788087) identifies the POMACS full paper associated with SIGMETRICS 2026.
- [PRISM, arXiv:2609.35569v1](https://arxiv.org/pdf/2609.35569).

| Claim | Primary evidence | Wording in deck |
|---|---|---|
| SSD prefix/KV caching; operational vs. embodied carbon | GreenCache §§2–3, Table 1; §3.2.1 | Electricity emissions vs. SSD manufacturing. Capacity allocation attributes amortized embodied carbon; it does not physically undo manufacturing emissions. |
| Dynamic capacity and LCS | GreenCache §§5.4–5.5 | ILP capacity allocation and Least Carbon Savings replacement. |
| Hardware and workloads | GreenCache §6.1 | Llama-3 70B INT8, 4 L40s, LMCache, up to 16 TB SSD, ShareGPT and TriviaQA. The paper also evaluates 8B; this summary focuses on the requested 70B setup. |
| 15.1% average; 25.3% peak | GreenCache §6.2, PDF p.17, Fig.14(a) | FR grid, Llama-3 70B, comparison with Full Cache; 25.3% is a multi-turn peak (12 AM), not an overall average. |
| Over 90% latency SLO attainment | GreenCache §§6.1–6.2, Fig.13 | Reported SLO attainment. Paper evaluates P90 TTFT and TPOT separately. For 70B: multi-turn thresholds 2.5 s / 0.2 s; document TTFT threshold 15 s. The slide does not invent a joint latency-success statistic. |
| Operational configuration invariance | PRISM §2, Proposition 1, Eq.(4) | Fixed workload, region and time; operational-only; all dimensions preserve IT-energy configuration ranking. |
| Lifecycle exception | PRISM Proposition 3, Eq.(6) | Embodied impacts can change the ranking. |
| Minimax relative regret | PRISM §3, Eq.(9) | Largest relative penalty from each dimension's own optimum. |
| 50.2% and baseline | PRISM §5.3, Fig.7; Appendix A.6.4–A.6.5, Table 12 | Median reduction in worst-case regret, 12 regions, 20 capacity seeds, offline WaterWise adaptation. |

Scientific refinements to the prompt: added GreenCache's Full Cache baseline and INT8 precision; specified the offline adaptation of WaterWise. PRISM Table 12 labels 50.2% as **median reduction** over 20 seeds. The separately reported median regrets are 157.8% (WaterWise) and 75.1% (PRISM); calculating the reduction of those two medians gives about 52.4%, not 50.2%. The slide preserves the paper's 50.2% statistic and calls it a median reduction. No supplied headline number was replaced.

## Build and visual QA

Run from the repository root with Python containing PyMuPDF:

```sh
python 2026-11-04-meeting/scripts/build_energy_carbon.py
```

Tested using `/tmp/helix-qa-env/bin/python` and TeX Live 2026.

- Local source: pdfLaTeX twice; final log has no warnings, undefined references, or overfull boxes.
- Exactly 3 pages, 16:9, page labels 1/3, 2/3 and 3/3.
- ZIP contains only `main.tex` and `README.txt`; extracted into a separate temporary directory and compiled twice. All three pages have identical text, rendered pixels and link annotations to the local build.
- Five external link annotations; zero internal navigation links. All text bounds fit within the page. Summary source rows differ vertically by less than 0.5 pt; footer positions match exactly.
- Visually inspected all three final 2.5x renders (`page-1.png`, `page-2.png`, `page-3.png`): readable body text, aligned labels, no title/body/source/footer overlap or clipping; matches the Helix visual style.
- PDF and arXiv URLs return HTTP 200. GreenCache project returns HTTP 200 and redirects via HTML to its GitHub repository.
- ACM DOI access returns HTTP 403 in this environment. DOI identity was independently confirmed through Crossref (HTTP 200, exact paper title). The slide also supplies the successfully fetched arXiv PDF link. See `link-checks.json`; full ACM page availability is not claimed.
- All pre-existing files under `2026-11-04-meeting/` matched their pre-task SHA-256 hashes, including Helix source, PDF, ZIP, figures, scripts and QA outputs.
- Build intermediates stay in temporary directories. IDE-generated duplicate PDF/intermediates for the new basename were removed after validation.

## New files / Git scope

- `2026-11-04-Energy-Carbon-Summary.tex`
- `scripts/build_energy_carbon.py`
- `output/pdf/2026-11-04-Energy-Carbon-Summary.pdf`
- `output/overleaf/Energy-Carbon-Summary.zip`
- `output/qa-energy-carbon/REVIEW.md`
- `output/qa-energy-carbon/validation.json`
- `output/qa-energy-carbon/link-checks.json`
- `output/qa-energy-carbon/page-1.png`
- `output/qa-energy-carbon/page-2.png`
- `output/qa-energy-carbon/page-3.png`

No existing tracked file changed. No commit or push performed.

## Cover and full-title revision

Added the requested cover. Both paper slides now display their complete paper titles in two lines at 11 pt, within the original light-blue title-bar style. Body text stays at 10 pt; row height is 0.90 cm to accommodate the taller title bar. Summary content and source links are unchanged. Rebuilt local PDF and standalone ZIP twice each, verified three pages and clean logs, and reviewed the rendered layout. Helix artifacts remain unchanged.
