# Research category index

Edit the corresponding module to add a paper within an existing category. The master includes a contents page and inputs category modules; its structure need not change for an added paper. Update `index.json` (page order, title, source and key) and the intended count in the build QA when intentionally extending this 22-page edition. Keep three concise bullets per Motivation/Method and cite sources in comments and QA, never visible slide rows.

| Category | Module | Papers |
|---|---|---|
| 1: Power-, Energy-, and Carbon-Aware GPU Serving Optimization | [gpu-serving.tex](gpu-serving.tex) | greencache, prism |
| A: HBF System Characterization and KV-Centric Serving | [characterization.tex](characterization.tex) | sucks, characterizing, hotcold |
| B: HBM/HBF Architecture and Data-Path Co-Design | [architecture.tex](architecture.tex) | h3, flashaccel, hbflex, beyond |
| C: HBF Simulation and Power/Thermal Modeling | [simulation.tex](simulation.tex) | realgpu, event, hbmpower |
| D: HBF-Accelerated Retrieval and RAG Systems | [retrieval.tex](retrieval.tex) | haven |

`directions.tex` holds the final synthesis and proposed next steps. `index.json` is the machine-readable slide-to-paper map used by validation. The standalone ZIP includes all TeX modules, so no original decks are required to compile it.
