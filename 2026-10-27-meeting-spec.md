# 2026-10-27 Meeting Slides Production Spec

## 0. 文件目的

本文件是 `2026-10-27-meeting/` 的實作規格。Helix 與 Tessera 各有一份完整 reference deck；**2026-10-27 meeting 真正要報告的是另一份精簡 combined deck**。

- 目標 meeting 日期：2026-10-27
- 規格建立時基準 commit：`0b7c2f5f9490c614e0ed351b72832801b4297101`
- 參考 meeting：`2026-10-21-meeting/`
- 第一輪先完成 LaTeX／Beamer 主線；**不要先製作 Marp 版本**。

### 兩種 deck，不要混用

| 角色 | 檔案 | 頁數 | 用途 |
|---|---|---|---|
| Meeting main deck | `2026-10-27-Meeting-Main.tex`、`Meeting-Main_scripts.md` | 約 13–14 張 main slides，另加 appendix | **15–20 分鐘正式報告**。故事是 Summary → Why → Method → Experiments as research questions → Conclusion。 |
| Full reference decks | `2026-10-27-Helix.tex`、`2026-10-27-Tessera.tex` 與對應 `_scripts.md` | 各 36–40 頁（目前各 38 頁） | Paper-reading reference 與 Q&A backup。保留，不要刪除或為了報告時間大幅改寫。 |

後面第 3、5、6 節的 36–40 頁結構只適用於 **full reference decks**。不要再把「每篇 36–40 頁」當成正式 meeting deck 的要求，也不要把 reference deck 當成下次報告版本。

---

## 1. Source of Truth 與輸入資料

### 1.1 論文事實來源

以下本地 PDF 是論文內容、公式、數據、實驗設定、版本與頁碼的唯一事實來源：

- `2026-10-27-meeting/ASPLOS25_Helix.pdf`
- `2026-10-27-meeting/Arxiv26_Tessera.pdf`

規則：

1. 所有數字、硬體型號、baseline、實驗條件、公式、演算法描述與結論都必須回到本地 PDF 查證。
2. 不可只依賴網頁摘要、記憶、舊版 arXiv abstract、figure 檔名或 README 推測內容。
3. 若網頁版與本地 PDF 不同，以本地 PDF 為準，且不可混用不同版本的結果數字。
4. 對論文未明確說明的內容，必須標示為「解釋」、「推論」、「限制」或「延伸問題」，不可寫成作者結論。

### 1.2 已整理 figure 素材

Helix：

- 目錄：`2026-10-27-meeting/Helix/`
- 現有 Figure 1–12，共 12 張 PNG。
- 使用目錄中**實際存在的檔名**。`Helix/README.txt` 的表格仍提到 `_with_caption.png`，但目前實際檔名沒有該 suffix；不要照 README 猜檔名。

Tessera：

- 目錄：`2026-10-27-meeting/Tessera/`
- 現有 Figure 1–11，共 11 張 PNG。
- `Tessera_Figures_600dpi.zip` 是素材封裝，不應直接被 LaTeX 引用。

任何圖片都不得拉伸變形、任意裁掉 legend／axis／caption／subfigure label，也不得重新繪製成可能改變資料含義的版本。

### 1.3 版型與講稿格式參考

只把以下檔案當作視覺與格式參考，不把它們當成 Helix／Tessera 的事實來源：

- `2026-10-21-meeting/2026-10-21-ThunderServe.tex`
- `2026-10-21-meeting/2026-10-21-Hetis.tex`
- `2026-10-21-meeting/ThunderServe_scripts.md`
- `2026-10-21-meeting/Hetis_scripts.md`

優先沿用：

- `aspectratio=169`、`10pt`、pdfLaTeX。
- Light Madrid 風格與既有色票：`Ink`、`Muted`、`Accent`、`AccentBlue`、`SoftMint`、`SoftBlue`、`SoftLilac`、`Paper`、`Divider`。
- 現有 `\smalllabel`、`\hint`、`\takeaway`、`\figureplaceholder`、`\paperfigure`、`\figurefocus`、`\twofigurefocus` 等 reusable macros。
- 獨立 deck 的頁腳編號、簡潔 title slide、英文投影片與繁體中文講稿。

### 1.4 已知參考檔問題，不得複製

參考檔中有人工頁碼註解與實際內容不同步的跡象，例如：

- ThunderServe 的 preamble 註解與 Q&A／講稿總頁數不一致。
- Hetis 講稿宣告 39 頁，但 `.tex` 中 Q&A 的人工註解是 Slide 35。

因此新 deck 必須以**編譯後 PDF 實際頁數**為準，禁止靠手動總頁數註解維護。講稿頁數、標題、順序必須由最終 deck 逐頁核對。

---

## 2. 必須交付的檔案

所有主要成果放在 `2026-10-27-meeting/`：

### 2.1 Helix

- `2026-10-27-meeting/2026-10-27-Helix.tex`
- `2026-10-27-meeting/Helix_scripts.md`
- `2026-10-27-meeting/output/pdf/2026-10-27-Helix.pdf`
- `2026-10-27-meeting/output/overleaf/Helix.zip`

### 2.2 Tessera

- `2026-10-27-meeting/2026-10-27-Tessera.tex`
- `2026-10-27-meeting/Tessera_scripts.md`
- `2026-10-27-meeting/output/pdf/2026-10-27-Tessera.pdf`
- `2026-10-27-meeting/output/overleaf/Tessera.zip`

### 2.3 Meeting main deck

15–20 分鐘正式報告，不取代 2.1 與 2.2：

- `2026-10-27-meeting/2026-10-27-Meeting-Main.tex`
- `2026-10-27-meeting/Meeting-Main_scripts.md`
- `2026-10-27-meeting/output/pdf/2026-10-27-Meeting-Main.pdf`
- `2026-10-27-meeting/output/overleaf/Meeting-Main.zip`

Main story 約 13–14 張。Appendix 用 `\appendix` 接在最後一張正式 slide 之後，不計入 15–20 分鐘。講稿頁碼對齊編譯後 PDF，含 appendix。

### 2.4 建議附加檔

- `2026-10-27-meeting/README.md`
  - 列出兩份簡報、講稿、來源 PDF、figure 資料夾、輸出檔與編譯方式。
  - 記錄最終頁數與最後驗證日期。

不要另做 Marp 或 HTML。正式 15–20 分鐘報告是 2.3 的 Meeting-Main；2.1 與 2.2 維持完整 reference decks。不要再做第三套版型。

---

## 3. 全域簡報規格

### 3.1 Deck 結構

**Full reference decks：** 每篇論文各自是一份 standalone deck，建議 **36–40 頁**。頁數是內容密度指引，不是硬性湊頁；不得為達頁數而拆成空洞頁面，也不得因壓頁而把字縮到難以閱讀。這兩份不是 15–20 分鐘 meeting 的報告稿。

**Meeting main deck：** 約 **13–14 張**主要 slides，外加 appendix。每一張 main slide 只有一個研究問題或 takeaway。實驗頁標題寫成 research question。不要把 reference deck 縮印成 30–40 頁的正式報告。

每份 deck 至少包含：

1. Title
2. Presentation Roadmap
3. Background / Motivation
4. Problem Formulation / Key Challenges
5. Methodology / System Design
6. Algorithms / Formulation / Runtime
7. Experimental Setup
8. Main Results
9. Ablations / Sensitivity / Case Study
10. Comparison with related papers studied in this project
11. Limitations / Discussion
12. Conclusion
13. Q&A

### 3.2 視覺與排版

- 16:9、10pt、Light Madrid，維持 10/21 meeting 的識別風格。
- Title slide 保持簡潔：論文標題、副標、Yu-Jui Liang、Advisor: Hsiang-Yun Cheng、National Taiwan University、27 Oct 2026。
- 每頁以一個主要問題或結論為核心；標題最好直接表達該頁 takeaway。
- 一張主要論文圖通常搭配 2–4 個重點與一個 takeaway；不要把圖當背景裝飾。
- 優先保留圖的完整比例。寬圖採上圖下文，窄圖採左文右圖；必要時一頁放兩張，但兩張都必須可讀。
- 表格與公式只能放報告需要的內容；若原表過大，重排時必須保留欄位意義、單位與比較基準。
- 不得出現：缺圖 placeholder、超出畫面的物件、看不清楚的 legend、密集小字、無來源的數字、只有圖片而沒有解讀的頁面。
- Slide 主文使用英文；專有名詞保留論文用語。
- 每頁底部可用 `\hint{Source: ...}` 標出 section／figure／table／equation，保持簡短。

### 3.3 內容密度

- 一般正文至少維持 `\footnotesize` 可讀性；若需要縮到 `\scriptsize` 才能塞入，優先刪減或拆頁。
- 每頁一般不超過 5 個主 bullet。
- 演算法若過長，可分成連續兩頁，但必須解釋輸入、輸出、核心步驟與該演算法在整體系統的位置。
- 公式頁需先定義符號與單位，再說明每一項的物理／系統意義，不只抄公式。

---

## 4. 繁體中文逐頁講稿規格

每份講稿必須和最終 PDF 一對一對齊。

### 4.1 固定格式

檔案開頭：

```markdown
# Helix 中文講稿

這是獨立簡報，對應 `2026-10-27-Helix.tex`。投影片頁腳與下方講稿頁碼完全一致。
```

Tessera 依相同格式替換名稱與檔名。

每頁標題：

```markdown
## 第 01 頁｜Title
```

頁碼必須補零，標題必須與 slide title 完全一致。

### 4.2 每頁內容

- 以可直接口述的繁體中文完整句子撰寫，不是簡報 bullet 的直譯。
- 一般每頁 2–5 段；依內容複雜度調整。
- 先說這頁要回答什麼，再帶讀圖／公式／演算法，最後給 takeaway 或銜接下一頁。
- 第一次出現的專有名詞要解釋，例如 max-flow、MILP、PTX、RAW dependency、IWRR、goodput、kernel disaggregation。
- 圖表頁必須說明 x/y 軸、單位、baseline、越高／越低代表什麼，以及作者真正能支持的結論。
- 結果頁不得只念倍率；必須說明測試場景與比較對象。
- 把「論文主張」、「為了教學的解釋」與「自己的推論」清楚分開。
- 不要把 speaker note 寫成論文逐段翻譯；目標是研究 meeting 可講、可被追問。

每頁末尾加來源，例如：

```markdown
來源：Section 4.2、Figure 3，PDF 第 7 頁。
```

若為跨論文比較或自己的整理：

```markdown
備註：本頁為跨論文整理；各欄位依原論文對應章節，並非單一論文原表。
```

### 4.3 對齊驗收

- PDF 實際頁數 = 講稿 `## 第 XX 頁` 標題數。
- 每個 PDF slide title = 對應講稿頁標題。
- 不可有跳號、重號、過時頁數說明或已刪頁的講稿。

---

## 5. Helix 建議故事線與頁面規劃

目標約 38 頁，可在 36–40 頁內調整。Figure 編號依原論文，不可自行改號。

| 頁次 | 建議標題／內容 | 主要素材 |
|---:|---|---|
| 1 | Title | — |
| 2 | Presentation Roadmap | — |
| 3 | Why Heterogeneous and Geo-Distributed Serving? | Introduction |
| 4 | Parallelism Across Nodes and GPUs | Background |
| 5 | Uniform Model Placement Is Sub-Optimal | Figure 1 |
| 6 | Network-Unaware Request Routing Creates Congestion | Figure 1 |
| 7 | Helix Design Requirements | Introduction |
| 8 | Helix System Overview | Figure 3 |
| 9 | From Model Placement to a Flow Network | Section 4 |
| 10 | Max-Flow Graph Abstraction | Figure 2 |
| 11 | Modeling Compute Capacity | Formulation |
| 12 | Modeling Network Capacity | Formulation |
| 13 | Why Max Flow Represents Serving Throughput | Formulation |
| 14 | Worked Three-Node Example | Figure 2 |
| 15 | MILP Variables and Objective | Section 4.4 |
| 16 | Placement and Memory Constraints | Section 4.4 |
| 17 | Flow and Compute Constraints | Section 4.4 |
| 18 | Connectivity and Network Constraints | Section 4.4 |
| 19 | Making the MILP Practical | Pruning / heuristic / solver discussion |
| 20 | Runtime Components and Control Flow | Figure 3 |
| 21 | Per-Request Pipelines | Runtime section |
| 22 | Converting Max-Flow Weights into Scheduling | IWRR / scheduling section |
| 23 | Pipeline Scheduling Example | Figure 4 |
| 24 | KV-Cache Masking and Backpressure | Runtime section |
| 25 | Implementation and Prototype | Implementation section |
| 26 | Evaluation Methodology | Models, clusters, baselines, metrics |
| 27 | Workload Characteristics | Figure 5 |
| 28 | Single-Cluster Results | Figure 6 |
| 29 | Geo-Distributed Results | Figure 7 |
| 30 | High GPU-Heterogeneity Results | Figure 8 |
| 31 | Model Placement Deep Dive | Figure 9 |
| 32 | Request Scheduling Deep Dive | Figure 10 |
| 33 | MILP Optimization Ablation | Figure 11 |
| 34 | Solver Time and Solution Quality | Figure 12 |
| 35 | Helix vs. ThunderServe and Hetis | Cross-paper comparison |
| 36 | Limitations and Threats to Validity | Discussion |
| 37 | Conclusion | Three takeaways |
| 38 | Questions & Discussion | — |

### Helix 特別注意

- 用本地 ASPLOS PDF 的最終內容與數字；不可把舊版摘要中的數字混入。
- 清楚區分：offline model placement、max-flow abstraction、online per-request scheduling。
- 說明 edge capacity 的單位及其如何由 compute／network cost 轉換，不可只畫 graph。
- MILP 頁要說明決策變數、objective 與 constraint 類別；不必把所有符號塞在同一頁。
- 評估頁每個倍率都要附 baseline、模型、cluster／workload 條件與 metric。
- Figure 6–12 不必每個 subpanel 都逐字念，但必須指出主要趨勢與例外。

---

## 6. Tessera 建議故事線與頁面規劃

目標約 38 頁，可在 36–40 頁內調整。

| 頁次 | 建議標題／內容 | 主要素材 |
|---:|---|---|
| 1 | Title | — |
| 2 | Presentation Roadmap | — |
| 3 | Hardware Heterogeneity Is Kernel-Dependent | Introduction / hardware table |
| 4 | Why Phase- or Block-Level Disaggregation Is Too Coarse | Figure 1 |
| 5 | Kernel as the Scheduling Granularity | Motivation |
| 6 | Different Kernels Prefer Different GPUs | Figure 2 |
| 7 | Phase Labels Hide Kernel-Level Variation | Figure 3 |
| 8 | Three Challenges for Kernel Disaggregation | Introduction |
| 9 | Tessera System Overview | Figure 4 |
| 10 | Offline Planning and Online Adaptation | Figure 4 |
| 11 | Analyzer: Standard vs. Opaque Kernels | Analysis section |
| 12 | PTX Instrumentation and Address Ranges | Analysis section |
| 13 | Extracting RAW Dependencies | Dependency analysis |
| 14 | Cross-Iteration Dependencies and KV State | Dependency / transfer section |
| 15 | Planner Inputs, Decisions and Objectives | Planning section |
| 16 | Offline Throughput-Oriented MILP | Formulation |
| 17 | Communication and Load-Balancing Constraints | Formulation |
| 18 | Online Latency-Oriented Scheduling | Online policy |
| 19 | Pipelining Across Requests | Execution section |
| 20 | GPU Worker Execution | Figure 5 |
| 21 | Overlapping Communication and Computation | Runtime section |
| 22 | Online Monitor Signals | Runtime section |
| 23 | Policy Switching and Sensitivity Parameters | Runtime section |
| 24 | Implementation Stack | Implementation section |
| 25 | Communication Backends and Interconnects | NCCL / RDMA / NVLink as stated in paper |
| 26 | Evaluation Methodology | Models, hardware, baselines, metrics |
| 27 | Offline Throughput | Figure 6 |
| 28 | Online Latency and Goodput | Figure 7 |
| 29 | Scaling with Cluster Size | Figure 8 |
| 30 | Pipeline Effectiveness | Figure 9 |
| 31 | Online Monitor Sensitivity | Figure 10 |
| 32 | Network Bandwidth and MILP Analysis | Figure 11 |
| 33 | Cost Efficiency of Heterogeneous Pairing | Evaluation |
| 34 | Generality Across Model Families | LLM / SSM / MLLM / diffusion, only if evaluated |
| 35 | Tessera vs. ThunderServe, Hetis and Helix | Cross-paper comparison |
| 36 | Limitations and Threats to Validity | Discussion |
| 37 | Conclusion | Three takeaways |
| 38 | Questions & Discussion | — |

### Tessera 特別注意

- 全文名稱統一使用本地 PDF 首頁的 **Tessera**；若原文某處或程式名稱出現舊名，只在必要時解釋，不可混用成兩個系統。
- 必須把 kernel granularity 和 phase／module／layer granularity 的差異說清楚。
- PTX dependency analysis 頁要區分靜態可辨識資訊、runtime instrumentation 與最終 dependency graph。
- RAW dependency、跨 iteration state、KV cache／state transfer 不可用模糊箭頭代替說明。
- MILP 頁要說明 throughput objective、placement／load／communication constraints，以及 solver 是 offline planner 的一部分。
- Online monitor 頁要定義論文實際使用的訊號、視窗與切換條件；不確定就回到 PDF，不可自行命名。
- 關於 NCCL、RDMA、NVLink、PCIe、Ethernet，只能寫論文明確使用或測試的配置，不得從一般常識推定實驗硬體。
- 「支援多種模型」只列論文真正實作或評估者，並區分 proof-of-concept 與完整評估。

---

## 7. 跨論文比較頁規格

Helix 與 Tessera 的結尾各放一頁 project-level comparison；可依該篇視角調整欄位順序，但至少比較：

| 欄位 | 說明 |
|---|---|
| System | ThunderServe / Hetis / Helix / Tessera |
| Optimization granularity | phase、head/module、model layer/pipeline、kernel 等 |
| Primary decision | 分組、placement、routing、head allocation、kernel schedule 等 |
| Optimization time scale | offline、periodic re-plan、per-request、runtime monitor |
| Communication state | KV cache、activation、kernel tensors／state 等 |
| Adaptation mechanism | workload shift、failure、online feedback、policy switching |
| Target environment | heterogeneous GPUs、geo-distributed network、single/multi-node 等 |
| Model scope | 僅 LLM 或更廣模型類型 |
| Main limitation | 依各論文 discussion 與可合理支持的分析 |

規則：

- 比較表是自己的統整，不可偽裝成原論文表格。
- 每一格都必須可追溯到論文；不確定則寫 `Not specified`，不要猜。
- 避免單純排「層級高低」；要說明不同切分維度解決的是不同瓶頸。
- 不可用單一實驗倍率跨論文直接排名，除非硬體、模型、workload、baseline 與 metric 完全相同。

---

## 8. 事實與引用規則

1. 每個 quantitative claim 都必須記錄：數值、單位、metric、baseline、模型、硬體／cluster、workload 或 sequence setting。
2. 不可把 peak hardware spec 當成實測 performance。
3. 不可把 throughput improvement 寫成 latency improvement，或把 average 寫成 P99。
4. 不可把 simulator／cost model 結果寫成真實硬體實測，反之亦然。
5. 不可把作者的假設寫成系統已實作功能。
6. Figure caption、section text 與正文數字若看似矛盾，回到上下文確認；在講稿註明必要 caveat。
7. 原論文 Figure／Table／Equation 編號保持一致。
8. Slide 上的簡化 notation 必須在講稿註明「為說明而整理」，不可宣稱逐字抄自論文。
9. 引用其他論文時，優先使用該 paper 自己的描述；不要只轉述 Helix／Tessera related work 對競品的評價。

---

## 9. 實作流程

### Phase A — Audit and source map

1. 執行 `git status`，確認不覆蓋未提交工作。
2. 列出 `2026-10-27-meeting/` 的實際檔案。
3. 讀取兩份本地 PDF，建立每篇的 source map：
   - section / subsection
   - PDF page
   - figure / table / equation / algorithm
   - 可放入哪一頁 slide
   - 需要在講稿補充的 caveat
4. 核對 figure 實際檔名與尺寸；不要只看 README。

### Phase B — Deck outline

1. 先建立每篇逐頁 outline。
2. 每頁明定：問題、主要 claim、素材、來源、takeaway。
3. 在寫 LaTeX 前檢查是否完整涵蓋背景、方法、實驗、限制與比較。

### Phase C — LaTeX implementation

1. 從 10/21 的 standalone Beamer deck 複製乾淨 preamble 與 macros。
2. 更新 title、subtitle、date、paper-specific label 與 image paths。
3. 不要複製舊 paper 的 source hints、頁碼或內容。
4. 使用 actual figure paths，例如 `Helix/Helix_Figure_...png`。
5. 每完成 5–8 頁即編譯一次，避免最後集中除錯。

### Phase D — Speaker scripts

1. 以已穩定的 slide 順序產生講稿。
2. 每頁加入來源與必要 caveat。
3. 逐頁核對標題與頁碼。
4. 若 deck 後續增刪頁，立即同步講稿，不留到最後才修。

### Phase E — Build and visual QA

在 `2026-10-27-meeting/` 下執行：

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Helix.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Helix.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Tessera.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Tessera.tex
```

或使用等價的 `latexmk -pdf`，但最終必須能由 pdfLaTeX 乾淨重建。

檢查：

```bash
pdfinfo 2026-10-27-Helix.pdf
pdfinfo 2026-10-27-Tessera.pdf
grep -E "Undefined control sequence|LaTeX Error|Overfull|Underfull|not found|multiply defined" *.log
```

建議渲染所有頁面做 montage，至少逐頁檢查：

- title／roadmap
- figure-heavy slides
- equation／algorithm slides
- evaluation result slides
- comparison／conclusion／Q&A

若使用 `pdftoppm`：

```bash
mkdir -p .render/helix .render/tessera
pdftoppm -png -r 120 2026-10-27-Helix.pdf .render/helix/slide
pdftoppm -png -r 120 2026-10-27-Tessera.pdf .render/tessera/slide
```

必須修正所有 missing figures、不可接受的 overfull boxes、文字截斷、錯誤 crop、圖太小與明顯失衡的空白。

### Phase F — Factual QA

對每頁逐項確認：

- 數字是否與本地 PDF 相同。
- baseline、metric、unit、model、hardware、workload 是否齊全。
- slide claim 是否超過 evidence。
- 講稿來源頁碼是否正確。
- cross-paper comparison 是否公平且未混用不同 setting。

### Phase G — Packaging

1. 複製最終 PDF 到：
   - `output/pdf/2026-10-27-Helix.pdf`
   - `output/pdf/2026-10-27-Tessera.pdf`
2. 建立 Overleaf zip：
   - zip 根目錄放 `main.tex`
   - 只包含實際使用的 figure assets
   - 不依賴 repo 外部檔案
   - 在乾淨暫存目錄解壓後，以 pdfLaTeX 成功編譯兩次
3. 不要把 `.aux`、`.log`、`.nav`、`.out`、`.snm`、`.toc`、`.fls`、`.fdb_latexmk`、rendered PNG 暫存檔提交進 repo。
4. 若這些檔案在工作流程中大量產生，可更新根目錄 `.gitignore`，但不要忽略交付 PDF／zip。

---

## 10. Definition of Done

只有以下全部成立才算完成：

- [ ] Helix 與 Tessera 各有一份獨立 reference `.tex`，且沒有被 meeting main deck 覆蓋。
- [ ] `2026-10-27-Meeting-Main.tex` 是 15–20 分鐘報告：約 13–14 張 main slides，appendix 另計。
- [ ] Meeting main 的講稿頁碼與 PDF 一致，實驗頁先回答「這個實驗要證明什麼」。
- [ ] 兩份 deck 都能在乾淨環境以 pdfLaTeX 編譯兩次。
- [ ] 沒有 missing figure、Undefined control sequence 或 fatal LaTeX error。
- [ ] 所有頁面已做視覺檢查，沒有文字截斷與圖表變形。
- [ ] 每份 deck 有完整背景、方法、實驗、限制、比較、結論與 Q&A。
- [ ] 每份 deck 的 quantitative claims 都可追溯到本地 PDF。
- [ ] Helix 沒有混用舊版摘要結果。
- [ ] Tessera 系統名稱與本文版本一致。
- [ ] 兩份繁體中文講稿可直接口述，且逐頁有來源。
- [ ] PDF 頁數、講稿頁數、頁碼與 title 逐頁完全一致。
- [ ] `output/pdf/` 有兩份最終 PDF。
- [ ] `output/overleaf/` 有兩份經乾淨解壓編譯驗證的 zip。
- [ ] Repo 中沒有 LaTeX 暫存檔或 render 暫存圖。
- [ ] 最後回報所有新增／修改檔案、PDF 頁數、編譯 warning 與仍需人工判斷的項目。

---

## 11. Cursor 啟動 Prompt

```text
你現在位於 LLM-Serving-Slides repo 根目錄。先完整閱讀 `2026-10-27-meeting-spec.md`，再執行 `git status` 並檢查目前 HEAD，確認工作建立在 commit `0b7c2f5f9490c614e0ed351b72832801b4297101` 或其後續版本。不要只產生大綱，直接完成 spec 中所有必要交付物。

以 `2026-10-21-meeting/2026-10-21-Hetis.tex`、`2026-10-21-meeting/2026-10-21-ThunderServe.tex` 與兩份 `_scripts.md` 作為版型和講稿格式參考；以 `2026-10-27-meeting/ASPLOS25_Helix.pdf`、`2026-10-27-meeting/Arxiv26_Tessera.pdf` 作為事實來源；使用 `2026-10-27-meeting/Helix/`、`2026-10-27-meeting/Tessera/` 中現有圖片的實際檔名。

依 spec 先完成 source map，再建立兩份獨立 Beamer deck、兩份繁體中文逐頁講稿、編譯 PDF 與 Overleaf zip。每完成一份 deck，就立即編譯兩次，檢查 missing figures、Undefined control sequence、Overfull box、頁碼／講稿對齊，並渲染所有頁面做視覺抽查。不得臆造數字，不得混用不同論文版本的結果；任何不確定敘述都回到本地 PDF 查證。第一輪不要製作 Marp。

完成後先不要 push。請回報：新增／修改檔案清單、兩份 PDF 的實際頁數、編譯 warnings、視覺 QA 結果、所有仍需人工決定的問題。
```
