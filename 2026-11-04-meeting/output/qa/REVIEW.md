# Helix methodology refinement — 2026-11-02

Baseline: `a259b15ddcf440fbf57023ec08bf3c8fdf87f8d5` (fetched origin/main before editing).
Only PDF pages 3, 4, 5, 6 and 34 change. All other 52 pages, including M07, are pixel-identical to the baseline PDF.

## Scientific content and scope

Checked the local original paper, especially Secs. 4.4–4.6, Figure 3, and Secs. 6.2, 6.8–6.9.

- M03 now has only Placement, Capacity and Flow. Placement and flow are joint MILP decisions; GPU profiling, network bandwidth and the chosen placement determine edge validity and capacities. The objective and capacity inequality remain unchanged and prominent. The latency / percentile caveat remains. Pipeline and IWRR details are removed from this page.
- M04 retains Figure 3 and uses Offline planning, Online scheduling, Pipeline execution and Decode reuse. It states that the coordinator checks estimated KV capacity, uses optimized flow weights in IWRR, selects one valid pipeline, and reuses that pipeline and local KV caches. MILP is not rerun per request or token.
- M05 retains node splitting, compute/network capacities, source/sink, conservation and both Figure 2 viewports. It adds F(Psi) = MaxFlow(G(Psi)) for a fixed placement, with a short transition to joint optimization on M06.
- M06 explicitly describes joint placement / flow search, not an outer placement-enumeration loop followed by independent max-flow solves. Existing objective, memory, connectivity, compute/network constraints and the global-optimality limitation remain.
- B17 / PDF 34 identifies Petals, Swarm and separate-pipeline heuristics as warm-start candidates. Gurobi searches for improved feasible solutions; initial plans need not be optimal. The paper does not supply a separate complete mathematical formulation for every heuristic initializer. Network pruning, warm starting and early stopping remain distinct, with the ten-minute no-improvement stop and four-hour budget unchanged.

No slides added, deleted or reordered. No experiment values, source images or existing displayed equations changed. All source strings, backup buttons and page numbers remain. No takeaway panels were reintroduced. Figure dimensions and existing column/table layouts are preserved; flexible space accommodates the text changes.

## Build, navigation and visual QA

- `scripts/build.py`: local pdfLaTeX twice and independently extracted Overleaf ZIP twice passed. No final-log warnings, undefined references, missing figures or overfull boxes.
- All 57 local and standalone ZIP pages have identical text, rendered pixel digests and hyperlink targets. The ZIP contains the exact current source, 12 caption-free figures and README.
- `scripts/validate.py` passed: 57 pages, 224 actual internal PDF annotations, all expected destinations and multiplicities, 12 image pixel hashes, 56 source-bearing pages, text bounds, footer clearance, critical claims and no large blue takeaway panels.
- Compared every page against the baseline: all 224 link target/page pairs and all visible source lines are unchanged. The only rendered differences are PDF 3, 4, 5, 6 and 34.
- Rendered all 57 pages and refreshed both montages. Visually inspected PDF 3–7 and 34 at 2x resolution. Equations, labels, figure content, sources and navigation are complete and legible, with no footer overlap or clipping.
- Existing cleanup checks passed: no LaTeX intermediate files anywhere under the meeting directory. Build intermediates were automatically removed by the existing temporary-directory workflow. Explicit review PNGs are outside the repository in `/tmp/helix-methodology-pages`.
- The pre-existing untracked root PDF remains untouched and excluded from this commit.

The following record documents the previous visual-cleanup revision.

---

# Helix visual cleanup validation — 2026-11-01

Baseline: `03622aea94186a9c1a36f4fa33624392b678c5cc`.
Result: 15 Main pages, 1 discussion index, 41 topic backup pages = 57 pages, in the same order.

## Changes and scientific claims

Removed all 44 rendered takeaway panels (15 Main, 29 Backup), their padding, and the obsolete takeaway macro. Main source/navigation uses a two-argument slidenote; backup sources and return buttons remain visible. Flexible space balances the body above compact bottom information rows, without reserving the former panel height.

- M03: throughput objective does not directly optimize request latency or percentiles.
- M05: steady max flow estimates throughput for a fixed placement.
- M06: pruning and timed solving do not always prove global optimality.
- M10: 70B vs. SP remains 1.86x offline / 1.69x online throughput with higher average latency.
- M11: simulated 30B online prompt/decode latency reductions of 66% / 24%, vs. Swarm. Simulation is now repeated in the comparison label.
- M12: 3.29x online decode throughput vs. SP, 42-node simulation, LLaMA-2 70B FP16, with slightly higher decode latency.
- M07 / M08: interleaving and KV admission are integrated into the existing body points.
- Backup B01, B05–B07, B09–B10, B12–B14, B22, B25, B27–B28, B31–B32 retain the substantive former panel text as ordinary body paragraphs. Other removed summaries repeat their page's evidence or explanation.

No experiment values or formulas were changed. All academic source strings, frame labels, image assets, and navigation targets are retained. The original Fig. 2 viewports on PDF 5 / 28 remain unchanged, and PDF 24 still supplies the full figure.

## Build and automated checks

- Local pdfLaTeX twice, extracted Overleaf ZIP pdfLaTeX twice, repeated after cleanup. Final logs contain no warnings, undefined references, missing assets, or overfull boxes.
- Local / standalone ZIP: identical text, rendered pixel digests, and hyperlink targets on all 57 pages.
- 224 actual PDF internal link annotations checked against resolved destinations. Exact multiplicities checked for every authored button, footer index, backup return and Beamer section-footer link.
- 12 / 12 supplied caption-free PNGs matched by decoded RGB pixel hashes. Original and caption-free source assets remain unchanged.
- Sources visible on all 56 source-bearing pages; the discussion index has no source in either version.
- PDF text bounds and footer clearance pass. Critical scientific claims checked on PDF 3, 6, 10, 11, 12.
- No takeaway macro remains. Actual PDF drawings contain no broad SoftBlue body panel; title bars and the small illustrative layer-range diagram remain.

## Visual review

Rendered all 57 pages at 2x resolution. Inspected both complete montages, all 15 Main pages at readable resolution, and enlarged PDF 28–33 / 54–55 for formula and solver-evidence details. No text, equations, axes, legends, or navigation are clipped or overlap the footline. Short text-only backup slides retain balanced white space rather than filler.

Figures are enlarged on PDF 7 (3.6 to 4.05 cm height cap), 10 (4.45 to 4.75 cm), 12 (4.4 to 4.85 cm), and 22 (3.0 to 3.4 cm). The key wide figures on PDF 2 / 4 / 5 / 11 / 13 / 14 already use the available width; their original aspect ratios and contents remain intact, with improved vertical balance. The Main and Backup montages reflect this cleanup, not the earlier redesign.

## Cleanup and repeatability

Removed nine confirmed job intermediates from the meeting root: `.aux`, `.log`, `.out`, `.nav`, `.snm`, `.toc`, `.fls`, `.fdb_latexmk`, `.synctex.gz`. None were tracked. No research source, figure, final deliverable, or pre-existing untracked PDF was deleted.

Build logs and recorder files now live only inside `TemporaryDirectory`, which cleans on success or exception. Failed compilation reports a bounded stdout tail. Validation renders default to an automatically cleaned temporary directory; `--render-dir` explicitly opts into retaining pages. A scoped `.gitignore` covers the additional LaTeX intermediate suffixes listed in the task.

After a fresh repeated build and validation, no LaTeX intermediates remain anywhere under the meeting directory. `output/pdf` contains only the final PDF, `output/overleaf` only the final ZIP, and `output/qa` only the ignore file, this review, validation JSON, and the two montage images. The pre-existing untracked root PDF is intentionally left untouched and excluded from the commit.

Manual review is separate from `validation.json`; automated checks alone are not visual proof.
