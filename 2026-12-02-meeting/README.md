# 2026-12-02 LLM Serving Research Meeting

Two independent English Beamer decks for the research meeting. Both use the repository's Madrid-based 16:9 visual system. The research discussion presents candidate directions and a validation plan; it is not a results report.

## Presentations

### Paper Review — 6 slides

1. Kareto: motivation and HBM–DRAM–SSD trade-offs
2. Kareto: simulator, search, and validation
3. Kareto: results and energy research question
4. EcoServe: operational and embodied carbon
5. EcoServe: Reduce, Reuse, Rightsize, Recycle
6. EcoServe: reported results and research opportunity

- [PDF](output/pdf/2026-12-02-Paper-Review.pdf)
- [LaTeX source](2026-12-02-Paper-Review.tex)
- [Overleaf ZIP](output/overleaf/Paper-Review.zip)
- [Evidence Register](2026-12-02-Paper-Review-Evidence.md)

### Research Topic Discussion — 10 slides

1. Revised scope
2. Power, energy, and carbon metrics
3. Prior work and research questions
4. Topic A — Multi-tier KV energy optimization (Rank 1)
5. Topic B — Heterogeneous GPU rack scheduling (Rank 2)
6. Topic C — Agentic KV management (Rank 3)
7. Research-gap validation plan
8. LLMServingSim 2.0 capabilities and audit boundary
9. Proposed power and carbon extensions
10. Proposed next steps and discussion

- [PDF](output/pdf/2026-12-02-Research-Discussion.pdf)
- [LaTeX source](2026-12-02-Research-Discussion.tex)
- [Overleaf ZIP](output/overleaf/Research-Discussion.zip)
- [Research specification](2026-12-02-Research-Discussion-SPEC.md)
- [Evidence Register](2026-12-02-Research-Discussion-Evidence.md)

## Figures

- `figures/kareto/fig06.png`: original Kareto Fig. 6 reuse-ratio heatmaps for high- and low-density workloads; PDF p. 6.
- `figures/ecoserve/fig6.png`: original EcoServe Fig. 6 component carbon comparison (A100 configuration), including units; PDF p. 4.
- `figures/ecoserve/fig15.png`: original EcoServe Fig. 15 results with panels, axes, legends, and baselines; PDF p. 10.

Figures are extracted from the cited papers and retain source captions/legends in the image crop. Conceptual diagrams in the Research Discussion are not experimental data.

## Build and QA

Install the QA helpers once, then run from the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install pymupdf pillow
.venv/bin/python 2026-12-02-meeting/scripts/build.py
.venv/bin/python 2026-12-02-meeting/scripts/validate.py
```

The build compiles each local source twice with pdfLaTeX, writes the two final PDFs, packages each deck with `main.tex` as entry point and required figures, compiles each extracted ZIP twice, compares extracted text and rendered pixels, renders every page to PNG, and writes separate montages plus `output/qa/validation.json`.

## QA results

- [Validation report](output/qa/validation.md)
- [Paper Review montage](output/qa/paper-review-montage.png)
- [Research Discussion montage](output/qa/research-discussion-montage.png)

## Known limits and open checks

- Kareto reports simulation fidelity on selected GPU-only, GPU+DRAM, and GPU+disk setups; its maximum TTFT deviation is 19.2%.
- EcoServe's carbon shares and 47% maximum depend on the studied hardware, workload mix, baselines, and iso-throughput setting.
- LLMServingSim 2.0 power fields are documented, but a storage idle-power setting alone does not establish SSD KV migration timing or I/O contention. Pin and audit the repository version before extending it.
- Hardware measurements, trace access, SSD behavior, and carbon-model calibration remain to be established for the proposed experiments.
