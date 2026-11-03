# Final conclusion and duplicate cleanup — 2026-11-04

Updated Main 16 with the requested contribution, evidence, throughput/latency trade-off, static-planning limitations, and research questions about adaptation, latency SLOs, and power constraints. The final build and validation passed for 58 pages and 283 internal links; inspected the rendered conclusion for fit and spacing.

Removed the untracked meeting-root PDF after verifying it was byte-identical to output/pdf/2026-11-04-Helix.pdf. The canonical PDF is now only in output/pdf; build.py already writes there. Earlier synchronization references below are historical.

---

# Navigation and consistency fixes — 2026-11-04

Preserved 16 Main slides, Conclusion on PDF 16, Discussion Index on PDF 17, and all 58 page numbers. Corrected PDF 12 to specify larger gains over SP for the larger model. Renamed the MILP Variables buttons to match their destination.

Added related-topic links, explicit numbered return options for shared detail pages, and direct Main links to full figures / graph details. All appendix pages are reachable by clicking from Main; every direct Main-to-detail link has a matching return option. Validation now checks both properties in addition to destination and annotation multiplicity checks.

Reformatted PDF 49 and 50 results as tables, shortened PDF 35, enlarged the graph view on PDF 25, and reorganized PDF 45 / 55 chart-and-text layouts. PDF 51 / 53 deliberately crop and enlarge the graph panels; full figures remain on Main 14 / 15. Original Figure 6 / 7 on Main 11 / 12 remain intact, including their embedded captions.

Local and extracted Overleaf ZIP builds each passed two pdfLaTeX runs; all 58 pages have identical text, rendered pixels, and link destinations between builds. Validation passed 283 internal links and all 14 source image hashes, with no text overflow or footer intrusion. Reviewed the final Main / Backup montages and enlarged revised layouts, including corrected PDF 49 paragraph spacing. Root PDF synchronized with output/pdf. Earlier historical records follow.

---

# Slide 12 original Figure 7 — 2026-11-02

Replaced only Main M11 / PDF 12's figure with the user-specified original Helix/Helix_Figure_07_Geo_Distributed_Cluster_Results.png. Full image, subfigure labels and embedded caption are retained without cropping or pixel changes. Reduced one vertical gap to fit the taller image; explanatory text, experimental claims and navigation remain unchanged. Backup FIG7 retains its existing caption-free image.

Updated standalone ZIP packaging and exact pixel-hash validation for original Figure 7, permitted only on M11 with full-image bounds checked. Local and extracted ZIP compiled twice each, with 58 identical rendered pages. Validation passed: 228 internal links, 14 approved image hashes (12 caption-free and originals 6/7), zero LaTeX intermediates. Inspected rendered PDF 12 for complete image and footer clearance. Earlier records follow.

---

# Slide 11 full Figure 6 and serving modes — 2026-11-02

Main M10 / PDF 11 now uses the user-specified original Helix/Helix_Figure_06_Single_Cluster_Results.png, with no cropping or pixel edits. The full lower-row (e–h) labels and embedded caption are visible. Image height cap is 4.85 cm to fit the replacement Offline/Online descriptions. Removed the previous external chart explanation and 70B ratio sentence from this Main page; ratios and latency trade-off remain in B26.

Offline text describes continuously supplying requests to saturate the cluster. Online text describes Azure Conversation arrival patterns scaled to 75% of peak throughput on average, without constant saturation. Source now includes Sec. 6.2 alongside Sec. 6.3 / Fig. 6.

Build packages the additional original PNG into the standalone ZIP. Validation retains all 12 caption-free image checks and adds an exact pixel-hash check for original Figure 6, restricted to M10, with full-image page bounds checked. The previous blanket original-image prohibition is replaced by this explicit single-image exception. The old Main ratio check now checks B26; Main checks the new serving-mode text.

Local and extracted-ZIP builds passed twice each: 58 identical rendered pages. Validation passed: 228 actual PDF links, 13 source images (12 caption-free plus original Figure 6), zero intermediate files. Rendered and visually checked PDF 11: all subfigure labels and caption fit, with no footer overlap. Previous records follow.

---

# Dedicated baseline comparison — 2026-11-02

Added PDF 10 (BASELINES), What Does Helix Compare Against?, after evaluation setup. Removed the Baselines point from PDF 9. The table compares Helix, Swarm, SP and Petals by core approach and comparison scope. Swarm/SP are end-to-end serving baselines; Petals is placement-only. The accompanying note fixes the Helix scheduler while varying Helix/Swarm/Petals placement to isolate placement gains. Sources: Secs. 2.2, 6.2, 6.6, Fig. 9.

Current architecture: 16 Main slides, discussion index on PDF 17, 41 technical backup slides on PDF 18–58. Original topic labels remain stable. New buttons open SETUP (PDF 44) and B29 (PDF 52); SETUP returns to BASELINES. Other backup return topics are preserved.

Validation now checks 58 pages and 16 Main slides, derives section-footer targets from the source, resolves scientific-claim checks by stable frame label, and verifies the new baseline scope. Existing strict image, source, annotation multiplicity, footer-clearance and cleanup checks remain enabled. Both montages reflect the new Main/Backup boundary.

Local and extracted-ZIP pdfLaTeX each passed twice with identical text, rendered pixels and link targets on all 58 pages. Validation passed: 228 actual internal links, 12 figure hashes, 57 source-bearing pages, no LaTeX intermediates. All pages rendered; visually checked PDF 9–11, including the final table spacing. No clipping or footer overlap. README navigation tables updated. Earlier entries below use historical page numbers and counts.

---

# Slide 9 workload clarification — 2026-11-02

Added the Azure Conversation filtering thresholds and retained dataset statistics to Main PDF 9, matching the existing workload backup: discard input >2048 or output >1024 tokens; retain 16,657 requests with mean input 763 and output 232 tokens. Source remains Secs. 6.1–6.2.

Local and extracted ZIP compiled twice each. Validation passed: 57 pages, 224 internal links, 12 source image hashes, no LaTeX intermediates. Visually inspected page 9: added text fits without clipping or footer overlap. PDF, ZIP and montage updated. Previous records follow.

---

# Slide 8 KV-aware selection — 2026-11-02

Replaced the generic busy-worker admission sentence with a separate KV-aware selection point: mask workers above the estimated KV high-water mark, then apply flow-weighted IWRR to remaining candidates. Preserved the partial-inference diagram and KV ownership explanation. Added Sec. 5.1 to the source reference alongside Sec. 5.2.

Local and extracted ZIP compiled twice each. Validation passed: 57 pages, 224 links, 12 figure hashes, no LaTeX intermediates. Rendered and visually inspected page 8; all text, diagram and footer navigation fit without overlap. Previous records follow.

---

# Main MILP slide simplified — 2026-11-02

PDF 6 now keeps only the aggregate source-flow objective formula. A plain-English sentence states the goal of finding the placement with the highest aggregate serving throughput through joint placement/flow optimization. Five numbered descriptions correspond to the paper's Constraints 1–5: placement/memory, conservation, compute capacity, connectivity and network capacity. Removed variable definitions and the layer-range equation from this Main slide; all technical Backup equations remain unchanged. The finite-solver/global-optimality caveat, sources and navigation are retained.

Local and independent ZIP builds passed twice each. Validation passed: 57 pages, 224 internal links, 12 source-image hashes, zero intermediate files. Only PDF 6 differs in rendered pixels from the immediately preceding version; all link targets are unchanged. Visually inspected page 6 with no clipping or footer overlap. Prior records follow.

---

# Slide 3 latency clarification — 2026-11-02

Expanded the throughput-objective caveat on PDF 3 with concise English descriptions of TTFT, TPOT and P95 / P99 latency, using abbreviations without expanded names. P95 / P99 are described as thresholds exceeded by the slowest 5% / 1% of requests.

Local and extracted-ZIP compilation passed twice each. Validation passed: 57 pages, 224 internal links, 12 image hashes and zero LaTeX intermediates. Inspected rendered page 3: text, objective, source and navigation fit without clipping or footer overlap. PDF, ZIP and QA montage are updated. Previous revision records follow.

---

# Slide 3 / 4 second swap — 2026-11-02

The user requested another swap of the current pages 3 and 4.
Current order: PDF 3 = What Does Helix Optimize? (M03),
PDF 4 = How Does One Request Run? (M04).
Frame content and stable topic labels are preserved. PDF and Overleaf ZIP rebuilt,
with all 57 pages and 224 internal links validated; no LaTeX intermediates remain.
Earlier swap records below are historical, not the current page mapping.

---

# Slide 3 / 4 swap — 2026-11-02

PDF 3 is now "How Does One Request Run?" (stable label M04).
PDF 4 is now "What Does Helix Optimize?" (stable label M03).
Only the two frame blocks were reordered; their content and topic labels are unchanged.
Backup returns therefore follow their original topics at the new page positions.

Rebuilt local PDF and extracted ZIP twice each. Validation passed: 57 pages,
224 actual internal links, 12 figure pixel hashes, no intermediate files.
Rendered all pages and inspected pages 3–4; no clipping or footer overlap.
The objective/latency claim check now resolves M03's actual page rather than hardcoding page 3.
Updated PDF, ZIP, montages, validation JSON and README page mapping.

Previous revision records follow.

---

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
