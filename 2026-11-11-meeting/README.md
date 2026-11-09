# 2026-11-11 Research Meeting — GreenCache

**19 頁 Main + 29 頁 Discussion / Backup（含 1 頁索引），共 48 頁。** 主動報告約 15–20 分鐘。Main 在前，Backup 在後。

- [PDF](output/pdf/2026-11-11-GreenCache.pdf)
- [Beamer source](2026-11-11-GreenCache.tex)
- [Overleaf ZIP](output/overleaf/GreenCache.zip)
- [原論文](GreenCache-Research-Meeting-2026-11-11/GreenCache-Carbon-Aware-KV-Caching-SIGMETRICS2026.pdf)

這不是一篇一般的 KV-cache 加速論文。主線是：在 TTFT 與 TPOT 的 SLO attainment 約束下，同時考慮 operational carbon 與 SSD embodied carbon，動態決定 cache 容量。

## Main 頁碼與 Backup 對應

頁碼是實際 PDF 頁碼。

| Main / PDF | 主題 | 主要圖 | 直接連結 |
|---|---|---|---|
| M01 / 1 | GreenCache | — | 1, 20 |
| M02 / 2 | Why Do We Need GreenCache? | Fig. 7 | 1, 20, 21, 27, 28 |
| M03 / 3 | Why Is a Fixed Cache Size Suboptimal? | Fig. 8 | 1, 20, 22, 29 |
| M04 / 4 | What Does GreenCache Optimize? | 最佳化目標 + SLO | 1, 20, 27, 28 |
| M05 / 5 | How Does GreenCache Work? (1/2): Monitoring & Prediction | Fig. 10 | 1, 20, 30, 33 |
| M06 / 6 | How Does GreenCache Work? (2/2): Optimization & Execution | Fig. 10 | 1, 7, 20, 31, 32, 39, 41 |
| M07 / 7 | How Does the Solver Decide? (1/2): Variables & Inputs | 概念式摘要公式 | 1, 20, 28, 31, 33, 45 |
| M08 / 8 | How Does the Solver Decide? (2/2): Constraints | 同一公式 + Eq. (6) / §5.4.2 | 1, 20, 30, 31, 32, 45 |
| M09 / 9 | How Does LCS Rank KV Cache Entries? | Eq. (7) | 1, 20, 34, 46 |
| M10 / 10 | How Does LCS Work for Multi-Turn Conversations? | Eq. (8) + KV reuse diagram | 1, 20, 34 |
| M11 / 11 | How Does LCS Work for Document QA? | Eq. (9) + KV reuse diagram | 1, 20, 46, 47 |
| M12 / 12 | Why Use LCS Instead of FIFO or LRU? | FIFO / LRU / LCS comparison; 4 TB example | 1, 20, 47, 48 |
| M13 / 13 | Real Prototype or Simulator? | — | 1, 20, 35 |
| M14 / 14 | How Is GreenCache Evaluated? | — | 1, 20, 32, 47 |
| M15 / 15 | Q1: Does GreenCache Reduce Carbon? | Fig. 12 | 1, 20, 36 |
| M16 / 16 | Q2: Does GreenCache Still Meet SLOs? | Fig. 13 | 1, 20, 37 |
| M17 / 17 | Q3: Does Capacity Track Load and CI? | Fig. 14 | 1, 20, 38 |
| M18 / 18 | Q4: Does Adaptive Sizing Help? | Fig. 15 | 1, 20, 30 |
| M19 / 19 | Conclusion | — | 1, 20, 44 |

Slide 5、6 採相同 60% / 38% 左右欄：完整 Figure 10（含原 caption）尺寸與位置相同，右側分別介紹 monitoring / prediction 與 optimization / execution。兩頁底部均標示 hourly resizing、1 TB granularity，以及最佳化期間持續 serving。Slide 7、8 使用同一條概念式摘要 \(S^*=\arg\min_{S\in\mathcal S}\widehat C_{\mathrm{total}}(S)\)，並標明它不是 Equation (6)。變數與輸入連到 B10、B07、B12、B24；SLO 連到 B11；容量域與 §5.4.2 假設連到 B24 與 B09。PuLP/CBC 與完整 Equation (6) 在 B10；TTFT/TPOT 的 binary indicators 與門檻在 B11；1 TB 粒度、70B 16 TB、8B 8 TB、每小時決策與 profiling 假設在 B24。

所有 Main 的頁腳都能打開第 20 頁索引。Fig. 1 的 KV reuse 基本機制在第 21 頁 B00。

## Backup

| PDF | Label | 內容 | 返回 / 導覽 |
|---|---|---|---|
| 20 | INDEX | Discussion Index | 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 20, 21, 30, 31, 32, 34, 35, 36, 38, 40, 44, 45, 46, 47, 48 |
| 21 | B00 | Why Cache Repeated Context? | 2, 20, 21, 23, 24 |
| 22 | B01 | Which Grids, and How Fast Does CI Move? | 3, 20, 21, 23 |
| 23 | B02 | Where Does Caching Change Latency? | 2, 20, 21, 24 |
| 24 | B03 | How Long Is the Repeated Context? | 2, 20, 21, 25 |
| 25 | B04 | What Does Request Rate Change? | 2, 20, 21, 26 |
| 26 | B05 | Does a Bigger Cache Always Raise the Hit Rate? | 3, 20, 21, 27 |
| 27 | B06 | Table 1: Embodied Carbon on This Server | 2, 4, 20, 21, 28 |
| 28 | B07 | Carbon Accounting, Equations (1)--(5) | 2, 4, 7, 20, 21, 29 |
| 29 | B08 | Load and CI Push Capacity in Opposite Ways | 3, 20, 21, 30 |
| 30 | B09 | What Do the Profiles Actually Contain? | 5, 8, 18, 20, 30, 31 |
| 31 | B10 | Full ILP and Variables | 6, 7, 8, 20, 30, 32, 39 |
| 32 | B11 | Exact SLO Constraints | 6, 8, 14, 20, 30, 33 |
| 33 | B12 | Load Forecast and Carbon-Intensity Forecast | 5, 7, 20, 30, 34 |
| 34 | B13 | Detailed Multi-turn LCS Example | 9, 10, 11, 12, 20, 30 |
| 35 | B14 | What Is Measured, Replayed, and Modeled? | 13, 14, 20, 35, 36 |
| 36 | B15 | Figure 12b: Llama-3 8B Carbon | 15, 20, 35, 37 |
| 37 | B16 | Figure 13b: Llama-3 8B SLO Timelines | 16, 20, 35, 38 |
| 38 | B17 | Figure 14b: Document Timeline, $\alpha=0.4$ | 17, 20, 35, 39 |
| 39 | B18 | Solver Time per Resize | 6, 20, 35, 40 |
| 40 | B19 | Do Forecast and Profile Errors Spend the Savings? | 6, 20, 40, 41 |
| 41 | B20 | How Often Should the Cache Resize? | 6, 20, 40, 42 |
| 42 | B21 | SSD Lifetime Changes the Embodied Weight | 19, 20, 40, 43 |
| 43 | B22 | SSD Embodied Carbon Is an Assumption | 19, 20, 40, 44 |
| 44 | B23 | Limits, and What We Would Not Claim | 19, 20, 40 |
| 45 | B24 | Discrete Capacity & Solver Assumptions | 7, 8, 20, 45 |
| 46 | B25 | Detailed Document QA LCS Example | 9, 10, 11, 12, 20, 45, 47 |
| 47 | B27 | How Is the TriviaQA Workload Generated? | 11, 12, 14, 20, 46, 48 |
| 48 | B26 | Full Replacement Policy Comparison — Table 3 | 9, 10, 11, 12, 20, 45, 47 |

## Figure → slide

| Figure | Main PDF | Backup PDF |
|---|---|---|
| 1 | — | 21 |
| 2 | — | 22 |
| 3 | — | 23 |
| 4 | — | 24 |
| 5 | — | 25 |
| 6 | — | 26 |
| 7 | 2 | — |
| 8 | 3 | — |
| 9 | — | 29 |
| 10 | 5, 6 | — |
| 11 | — | 30 |
| 12 | 15 | 36 |
| 13 | 16 | 37 |
| 14 | 17 | 38 |
| 15 | 18 | — |
| 16 | — | 39 |
| 17 | — | 40 |
| 18 | — | 41 |
| 19 | — | 42 |
| 20 | — | 43 |

Fig. 7 保留完整原圖與 caption：第 2 頁聚焦 (a) 的負載比較。第 3 頁用 Fig. 8 說明不同電網與同一電網不同時段的 CI 趨勢及碳排取捨。Fig. 12、13、14 在 Main 放大相關子圖，Backup 放另一半；legend 與 caption 均來自原始 PNG viewport，沒有重繪座標軸。

## LCS methodology and navigation

**PDF 9–12 是連續的 Main LCS 段落：Eq. (7) → Eq. (8) → Eq. (9) → FIFO / LRU / LCS policy comparison。** 完整 Table 3 在 Backup B26（PDF 48），不在 Main。

| Topic | Label / PDF | Evidence |
|---|---|---|
| General LCS principle | M09 / 9 | §5.5, Eq. (7) |
| Multi-turn history KV reuse | M10 / 10 | ShareGPT, Eq. (8) |
| Shared document-prefix KV reuse | M11 / 11 | TriviaQA α=0.4 and α=0.7, Eq. (9) |
| Why LCS instead of FIFO or LRU | M12 / 12 | Mechanism comparison. Representative token-level hit rate: Llama-3 70B, TriviaQA α=0.7, 4 TB — FIFO 23%, LRU 26%, LCS 35% (+9 percentage points vs. LRU) |
| Detailed multi-turn scoring example | B13 / 34 | Three hypothetical entries, explicitly not paper data |
| Detailed document scoring example | B25 / 46 | Three hypothetical documents; hit count vs. reused tokens vs. size |
| TriviaQA / Zipf workload | B27 / 47 | §5.5, §6.1, §6.3.2; 50k warm-up; approximate 25% / 50% shares; fixed 4 TB LCS 14% / 35% |
| Full Table 3 | B26 / 48 | §6.3.2; Llama-3 70B; all 45 token-level hit rates. Not a direct CO₂ measurement |

M11 opens B27 through TriviaQA Workload / Zipf α. M12 links its underlined TriviaQA α=0.7 to B27 (PDF 47), while Full Table 3 opens B26 (PDF 48). M14, B25, B26, and the index also open B27. All backups use the standard Back to Main and Discussion Index buttons. B27 returns to M12 and links to M11, M14, B25, B26, and INDEX. [Main 9–12 screenshot](output/qa/lcs-main-09-12.png).

M10 and M11 share formula position, font size, and column layout. Their diagrams illustrate matching retained KV reuse, not unconditional hits. Age means time in storage. Scores are heuristics, not measured gCO₂e, and do not multiply by current CI. The paper reports no independent Eq. (7)/(8)/(9) ablation. Grow/shrink changes allocation under amortized carbon accounting; eviction does not transfer all SSD KV back to GPU HBM.

## Claim → source

| Claim | Where it applies | Source |
|---|---|---|
| 15.1% average, up to 25.3% vs Full Cache | Llama-3 70B, FR, multi-turn only | Abstract; Sec. 6.2 timeline |
| 12.6% / 9.4% / 5.6% vs Full Cache | Llama-3 70B, average over FR, FI, ES, CISO; multi-turn, TriviaQA α=0.4, α=0.7 | Sec. 6.2 |
| 10.8% / 7.6% / 9.7% vs Full Cache | Llama-3 8B, same three workloads. Not comparable to 70B: 2×L40 BF16 and 8 TB max, versus 4×L40 INT8 and 16 TB max | Sec. 6.2 |
| 6.9–20.4% and 3.2–16.2% vs Full Cache | Day-long range, multi-turn and document α=0.4 | Sec. 6.2 |
| Up to 6.91% on a higher-CI grid such as CISO | Introduction's wording for Llama-3 70B. The deck states the Sec. 6.2 range 6.9–20.4% on PDF 38 and does not treat 6.91% as a second, independent result | Sec. 1 |
| 14.4–20.3% | Reported savings on the low-CI grids FR and FI | Sec. 6.2. Not placed on a Main slide, so it is not mixed with 15.1% |
| Prompt TTFT 1.7 s; KV load 0.03 s | ShareGPT, Llama-3 70B, 4×L40. Not an end-to-end speedup | Sec. 2.2 |
| SSD is 76.6% of embodied carbon | This Table 1 server at up to 16 TB, 480 kgCO₂e. Not a universal datacenter share | Sec. 2.3, Table 1 |
| 16 TB cache: +16.5% on FR, −7.5% on MISO | Versus no cache. Fig. 8 ratio below 1 means a reduction | Sec. 3.2, Fig. 8 |
| CISO day: 37 gCO₂e/kWh at 7 AM, 232 at 8 PM | Fig. 8b | Sec. 3.2 |
| ρ = 0.9, separate TTFT and TPOT sums | Not one joint probability | Eq. (6), Sec. 5.4 |
| Resize hourly, 1 TB steps, PuLP + CBC, 7.03 s average | Controller overhead, not the token path | Secs. 5.4, 6.1, 6.4 |
| Token hit rate; 4 TB, TriviaQA α=0.7: FIFO 0.23, LRU 0.26, LCS 0.35 | Reused input tokens / total input tokens. +9 percentage points is LCS minus LRU, not a relative percent. Full 45-value table is B26 | Table 3, Sec. 6.3.2 |
| LRU + adaptive capacity: up to 10.3%, and 6.6–9.9% | Versus Full Cache, ES average CI 124 gCO₂e/kWh | Sec. 6.3.1, Fig. 15 |
| Error trims 0.0064% / 0.20% / 0.79% of savings | CI, then plus load, then plus profiler, versus ground truth | Sec. 6.5 |
| 3-year SSD life: up to 11.9%; 90 kgCO₂e/TB: up to 25% | ES grid, fixed rates in Sec. 6.6 | Secs. 6.6.2–6.6.3 |

## Prototype, traces, and the carbon model

M13 **Real Prototype or Simulator?** 以三個卡片說明真實 GPU prototype、trace-driven evaluation，以及量測與碳模型的分工。CPU/GPU power 是量測，SSD/DRAM power 來自規格，embodied carbon 則以攤提模型估計。結論保留「沒有報告獨立 GPU-serving simulator」，Measurement Notes 連到 B14。

M14 **How Is GreenCache Evaluated?** 聚焦模型／workload、橫向排列的 No Cache／Full Cache／GreenCache，以及 carbon per prompt、TTFT／TPOT SLO attainment、allocated cache capacity。Full Cache 與 GreenCache 使用相同容量上限，TTFT／TPOT 各自要求 90%。TriviaQA 連到 B27，SLO Thresholds 連到 B11。

細節保留於既有 Backup，避免重複：

| 細節 | Backup |
|---|---|
| 512 GB DDR4、硬體與 embodied carbon | B06 |
| 碳會計與攤提 | B07、B23 |
| SLO thresholds 與各自的 attainment constraints | B11 |
| RAPL、pyNVML、1 ms、trace scaling；新增 8k context window 與截斷 | B14 |
| GPU 數量、INT8／BF16、8 TB／16 TB | B15、B24 |
| 每小時決策與容量粒度 | B24 |
| TriviaQA Zipf、Poisson arrivals、warm-up | B27 |
| Token-level hit rate replacement study | M12、B26 |

B14 保留返回 M13，並新增 Evaluation → M14。未增加頁面。

[Slide 13 前後對照](output/qa/main-13-before-after.png) · [Slide 14 前後對照](output/qa/main-14-before-after.png)

## 編譯

需要 TeX Live（Beamer、pdfLaTeX）以及 PyMuPDF、Pillow。

```bash
python3 -m venv /tmp/greencache-qa
/tmp/greencache-qa/bin/pip install pymupdf pillow
/tmp/greencache-qa/bin/python scripts/build.py
/tmp/greencache-qa/bin/python scripts/validate.py
/tmp/greencache-qa/bin/python scripts/test_navigation.py
```

`build.py` 在本目錄編譯兩次，寫出 PDF 與 Overleaf ZIP，再把 ZIP 解到暫存目錄編譯兩次，並比對文字、像素與連結目標。ZIP 入口是 `main.tex`，compiler 選 **pdfLaTeX**。圖檔是 20 張未改像素的 With-Caption PNG，路徑與原始碼中的相對路徑一致。

這些 PNG 的 `pHYs` 是 3780 px/m。pdfTeX 因此用約 0.752813 pt/px，不是 1 px = 1 bp。Fig. 12、13、14 的裁切已依 With-Caption 圖片高度換算；主講頁分開顯示子圖與原圖 caption，備份頁保留底部 caption。

## QA

- 本地兩次與 ZIP 獨立兩次編譯通過，最終 log 沒有 Overfull、undefined reference 或 Warning。
- 48 頁、280 個內部連結、20 張來源圖的像素雜湊都通過。Main 19 頁，Discussion / Backup 29 頁。28 張 Backup 的可見 Back to Main 與 Discussion Index 按鈕均以 PDF annotations 驗證；M12 ↔ B27 與 M12 ↔ B26 通過。Table 3 的 45 個數值未變。
- [逐頁導覽稽核](output/qa/navigation-audit.md) 列出每張 Backup 的 PDF 頁碼、主要 Main 目的地與交叉連結。Validator 從 frame labels 推導目的頁，並鎖定 19 Main + 1 Index + 28 Backup = 48 頁結構。
- [Main montage](output/qa/main-montage.jpg)、[Backup montage](output/qa/backup-montage.jpg)、[逐頁 PNG](output/qa/pages/)、[機器紀錄](output/qa/validation.json)、[視覺紀錄](output/qa/REVIEW.md)。

## Main speaking points

1. GreenCache 決定的是 SSD cache 容量，目標是總碳排，不是單純提高 hit rate。
2. 重用 KV 省的是重複 prefill。Decode FLOPs 還在；1.7 s 與 0.03 s 不是同一個請求的端到端加速比。
3. 多加 SSD 會加 embodied carbon。這台機器上 16 TB SSD 佔 embodied carbon 的 76.6%，不能外推成所有伺服器。
4. Fig. 8 的 ratio 小於 1 才是碳排下降。低 CI 不一定關 cache；高負載仍可能為了 SLO 留下大 cache。
5. 流程是 profile、forecast、ILP、resize + LCS。服務路徑仍是 LMCache / vLLM。
6. TTFT 與 TPOT 是兩條各自 90% 的 attainment，不是一個聯合機率。
7. 沒有獨立 GPU simulator。硬體是真的，到達與 CI 是 trace，碳排是會計模型。
8. M15 以定性解讀取代文字中的實驗百分比：自適應容量比 Full Cache 省碳；prefix 重用有助抵銷快取成本，但不保證更大的減碳幅度。α=0.4 的 No Cache 較低，仍需由下一頁確認延遲 SLO。
9. M16：No Cache 常超過延遲 SLO；GreenCache 利用 Full Cache 的延遲餘裕，以略高但仍達標的延遲，換取較小容量與較低總碳排。此結論限於圖中實驗，不限縮為高 CI 地區的效果。
10. M15 是動態 CI 與 Azure request-rate trace 下的平均碳排；M17 展開 multi-turn 的日內時間序列。容量共同受負載、CI 與 SLO 約束影響，較高 CI 或負載不保證更大減碳幅度。LCS 的 hit rate 是 token 比例。4 TB、TriviaQA α=0.7：FIFO 23%、LRU 26%、LCS 35%，比 LRU 高 9 個百分點。完整 Table 3 在 B26，不直接等於減碳。
11. M19 由上到下是 Problem、Contribution、Evidence、Future work。Future work 是我們的計畫：跨地區資料中心，以及把 HBM–HBF 當成 cache 層。論文沒有評估這兩項。Trace、攤提與 dense Llama-3 的限制留在 B23。

## Unresolved

- Section 6.1 寫 Llama-3 8B document TTFT SLO 為 2.5 s。Fig. 13 該面板的虛線畫在 4.0 s。PDF 32（B11）與 37（B16） 同時保留兩種說法，沒有代作者選一個。
- Section 6.2 先給出 70B 的 12.6% / 9.4% / 5.6%，後面又說高 skewness 的節省更高。數字句與這句方向不一致。README 的來源對照保留帶 respectively 的三個百分比；M15 不再列出這些百分比，也不宣稱較高 skewness 必然減碳更多。
- Fig. 2 的 PNG 頂端有幾個被切掉的標題像素。PDF 22（B01）去掉上方約 16 px。座標軸、CI 數字與 legend 仍在。

Slide 9–11 已還原為先前確認的色塊排版：M09 四個變數色塊；M10／M11 各有兩個上下變數色塊與底部結論色塊。Size／Age 重複說明與 proxy／ablation 句維持刪除；TriviaQA 分布解說集中在新增 B27。

Slide 9–11 的公式字體各縮小一級，保留已確認的變數色塊與結論。Slide 12 和 B26 維持策略比較與完整 Table 3 的分工。

M18 的結論：即使不使用 LCS，GreenCache 的自適應容量決策仍能相對 Full Cache 降低碳排；在本實驗中，低負載時效果較明顯，因為滿足 SLO 所需的 cache 較小。這說明容量調整本身有貢獻，但不代表 LCS 沒有額外價值。原圖、設定與來源保留，百分比仍在來源對照表。

## Final Main–Backup navigation alignment

Baseline：`dfd9923a09d2b68ffb83df3f48745a8b200f6fa0`。開始前已 `git fetch origin`，HEAD 與最新 origin/main 相同，working tree 乾淨。本次沒有新增頁面或改寫研究內容。

- M09 → B13 / B25：標示為 Eq. (7) 的 task-specific extensions；M10 → B13 是 Eq. (8) worked example，M11 → B25 是 Eq. (9) worked example。M11 → B27 的 TriviaQA workload / Zipf 入口保留。
- M06 增加 Solver Time → B18、Resize Interval → B20，全部放在既有 source/navigation 區，未縮小正文或公式。
- M18 → B09 改為 `Capacity Profiling (Background)`；B09 來源列說明 Figure 11 是 profiling background，Figure 15 ablation 在 M18。M12 改為 `LCS (GreenCache)`；M19 → B23 改為 `Limits / Our Future Work`。
- 28 張 Backup 均保留 `Back to Main N` 與 Discussion Index。既有 Main 快捷連結改成編號與主題，例如 `Main 18 (Ablation)`；Index 使用 `Go to Conclusion (M19)`。
- 46 個可點擊 Backup 入口、36 組不同 Main → Backup 對應，全部有可見的來源 Main 返回連結。無未解決語意不一致。B02–B05、B19、B21、B22 沒有 Main 直接入口，可經 Index 與 Backup 串接到達；它們並非只能由 Index 單一路徑開啟。
- Index 表格的 Open A–D 原有點擊範圍略有重疊，局部 `mbox` 修正 annotation 範圍，視覺排版不變。所有 280 個內部連結均有效且點擊矩形互不重疊。
- [Navigation contracts](scripts/navigation-contracts.json) 記錄每個入口的可見文字、目標、知識補充與直接／背景關聯；validator 比對編譯後 PDF annotation、文字、目標頁與可見返回按鈕。新增或改名入口時須同步人工覆核此檔。
- [Build validation](output/qa/build-validation.json) 記錄本地／獨立 ZIP 的文字、像素、連結目標、矩形及按鈕文字 parity，並以 SHA-256 綁定當次 source/PDF/ZIP；validator 拒絕過期 build。[Baseline preservation](output/qa/baseline-preservation.json) 記錄 20 張原圖像素雜湊、數學式不變及逐頁像素差異。

Validator regression tests：移除 M10 範例入口、把 M11 的 Eq. (9) 入口錯接到仍有效的 B27、移除 B09 → M18 返回連結，三種錯誤均被攔下。
