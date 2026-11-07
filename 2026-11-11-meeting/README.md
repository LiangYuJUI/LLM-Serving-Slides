# 2026-11-11 Research Meeting — GreenCache

**17 頁 Main + 27 頁 Discussion / Backup（含 1 頁索引），共 44 頁。** 主動報告約 15–20 分鐘。Main 在前，Backup 在後。

- [PDF](output/pdf/2026-11-11-GreenCache.pdf)
- [Beamer source](2026-11-11-GreenCache.tex)
- [Overleaf ZIP](output/overleaf/GreenCache.zip)
- [原論文](GreenCache-Research-Meeting-2026-11-11/GreenCache-Carbon-Aware-KV-Caching-SIGMETRICS2026.pdf)

這不是一篇一般的 KV-cache 加速論文。主線是：在 TTFT 與 TPOT 的 SLO attainment 約束下，同時考慮 operational carbon 與 SSD embodied carbon，動態決定 cache 容量。

## Main 頁碼與 Backup 對應

頁碼是實際 PDF 頁碼。

| Main / PDF | 主題 | 主要圖 | 直接連結 |
|---|---|---|---|
| M01 / 1 | GreenCache | — | 1, 18 |
| M02 / 2 | Why Do We Need GreenCache? | Fig. 7 | 1, 18, 19, 25, 26 |
| M03 / 3 | Why Is a Fixed Cache Size Suboptimal? | Fig. 8 | 1, 18, 20, 27 |
| M04 / 4 | What Does GreenCache Optimize? | 最佳化目標 + SLO | 1, 18, 25, 26 |
| M05 / 5 | How Does GreenCache Work? (1/2): Monitoring & Prediction | Fig. 10 | 1, 18, 28, 31 |
| M06 / 6 | How Does GreenCache Work? (2/2): Optimization & Execution | Fig. 10 | 1, 7, 18, 29, 30 |
| M07 / 7 | How Does the Solver Decide? (1/2): Variables & Inputs | 概念式摘要公式 | 1, 18, 26, 29, 31, 43 |
| M08 / 8 | How Does the Solver Decide? (2/2): Constraints | 同一公式 + Eq. (6) / §5.4.2 | 1, 18, 28, 29, 30, 43 |
| M09 / 9 | How Does LCS Rank KV Cache Entries? | Eq. (7) | 1, 16, 18, 32, 44 |
| M10 / 10 | Real Prototype, Traces, or a Simulator? | — | 1, 18, 33 |
| M11 / 11 | What Are the Evaluation Settings? | — | 1, 18, 30 |
| M12 / 12 | Q1: Does GreenCache Reduce Carbon? | Fig. 12 | 1, 18, 34 |
| M13 / 13 | Q2: Does GreenCache Still Meet SLOs? | Fig. 13 | 1, 18, 35 |
| M14 / 14 | Q3: Does Capacity Track Load and CI? | Fig. 14 | 1, 18, 36 |
| M15 / 15 | Q4: Does Adaptive Sizing Help? | Fig. 15 | 1, 18, 28 |
| M16 / 16 | Does LCS Outperform FIFO and LRU? | Table 3 | 1, 9, 18, 32, 44 |
| M17 / 17 | Conclusion and Limitations | — | 1, 18, 42 |

Slide 5、6 採相同 60% / 38% 左右欄：完整 Figure 10（含原 caption）尺寸與位置相同，右側分別介紹 monitoring / prediction 與 optimization / execution。兩頁底部均標示 hourly resizing、1 TB granularity，以及最佳化期間持續 serving。Slide 7、8 使用同一條概念式摘要 \(S^*=\arg\min_{S\in\mathcal S}\widehat C_{\mathrm{total}}(S)\)，並標明它不是 Equation (6)。變數與輸入連到 B10、B07、B12、B24；SLO 連到 B11；容量域與 §5.4.2 假設連到 B24 與 B09。PuLP/CBC 與完整 Equation (6) 在 B10；TTFT/TPOT 的 binary indicators 與門檻在 B11；1 TB 粒度、70B 16 TB、8B 8 TB、每小時決策與 profiling 假設在 B24。

所有 Main 的頁腳都能打開第 18 頁索引。Fig. 1 的 KV reuse 基本機制在第 19 頁 B00。

## Backup

| PDF | Label | 內容 | 返回 / 導覽 |
|---|---|---|---|
| 18 | INDEX | Discussion Index | 5, 6, 7, 8, 9, 10, 16, 17, 18, 19, 28, 29, 30, 32, 33, 34, 36, 38, 42, 43, 44 |
| 19 | B00 | Why Cache Repeated Context? | 2, 18, 19, 21, 22 |
| 20 | B01 | Which Grids, and How Fast Does CI Move? | 3, 18, 19, 21 |
| 21 | B02 | Where Does Caching Change Latency? | 18, 19, 22 |
| 22 | B03 | How Long Is the Repeated Context? | 18, 19, 23 |
| 23 | B04 | What Does Request Rate Change? | 2, 18, 19, 24 |
| 24 | B05 | Does a Bigger Cache Always Raise the Hit Rate? | 3, 18, 19, 25 |
| 25 | B06 | Table 1: Embodied Carbon on This Server | 2, 4, 18, 19, 26 |
| 26 | B07 | Carbon Accounting, Equations (1)--(5) | 2, 4, 7, 18, 19, 27 |
| 27 | B08 | Load and CI Push Capacity in Opposite Ways | 3, 18, 19, 28 |
| 28 | B09 | What Do the Profiles Actually Contain? | 5, 8, 15, 18, 28, 29 |
| 29 | B10 | Full ILP and Variables | 6, 7, 8, 18, 28, 30, 37 |
| 30 | B11 | Exact SLO Constraints | 6, 8, 11, 18, 28, 31 |
| 31 | B12 | Load Forecast and Carbon-Intensity Forecast | 5, 7, 18, 28, 32 |
| 32 | B13 | How Does LCS Work for Multi-Turn Conversations? | 9, 16, 18, 28, 44 |
| 33 | B14 | What Is Measured, Replayed, and Modeled? | 10, 18, 33, 34 |
| 34 | B15 | Figure 12b: Llama-3 8B Carbon | 12, 18, 33, 35 |
| 35 | B16 | Figure 13b: Llama-3 8B SLO Timelines | 13, 18, 33, 36 |
| 36 | B17 | Figure 14b: Document Timeline, α=0.4 | 14, 18, 33, 37 |
| 37 | B18 | Solver Time per Resize | 6, 18, 33, 38 |
| 38 | B19 | Do Forecast and Profile Errors Spend the Savings? | 6, 18, 38, 39 |
| 39 | B20 | How Often Should the Cache Resize? | 6, 18, 38, 40 |
| 40 | B21 | SSD Lifetime Changes the Embodied Weight | 17, 18, 38, 41 |
| 41 | B22 | SSD Embodied Carbon Is an Assumption | 17, 18, 38, 42 |
| 42 | B23 | Limits, and What We Would Not Claim | 17, 18, 38 |
| 43 | B24 | Discrete Capacity and Solver Assumptions | 7, 8, 18, 43 |
| 44 | B25 | How Does LCS Work for Document QA? | 9, 16, 18, 32, 43 |

## Figure → slide

| Figure | Main PDF | Backup PDF |
|---|---|---|
| 1 | — | 19 |
| 2 | — | 20 |
| 3 | — | 21 |
| 4 | — | 22 |
| 5 | — | 23 |
| 6 | — | 24 |
| 7 | 2 | — |
| 8 | 3 | — |
| 9 | — | 27 |
| 10 | 5, 6 | — |
| 11 | — | 28 |
| 12 | 12 | 34 |
| 13 | 13 | 35 |
| 14 | 14 | 36 |
| 15 | 15 | — |
| 16 | — | 37 |
| 17 | — | 38 |
| 18 | — | 39 |
| 19 | — | 40 |
| 20 | — | 41 |

Fig. 7 保留完整原圖與 caption：第 2 頁聚焦 (a) 的負載比較。第 3 頁用 Fig. 8 說明不同電網與同一電網不同時段的 CI 趨勢及碳排取捨。Fig. 12、13、14 在 Main 放大相關子圖，Backup 放另一半；legend 與 caption 均來自原始 PNG viewport，沒有重繪座標軸。

## LCS methodology and navigation

| Topic | Label / PDF | Evidence |
|---|---|---|
| General LCS score and capacity/replacement boundary | M09 / 9 | §5.5, Eq. (7) |
| FIFO / LRU / LCS token-level hit rates | M16 / 16 | §6.3.2, Table 3 (all 45 values retained) |
| Multi-turn history KV reuse | B13 / 32 | ShareGPT, Eq. (8) |
| Shared document-prefix KV reuse | B25 / 44 | TriviaQA α=0.4 and α=0.7, Eq. (9) |

Each of these four pages links directly to the other three; the Discussion Index links to all four. B13 and B25 use matching formula/variables + diagram columns. The diagrams are conceptual KV reuse illustrations, not additional paper figures. Age means time in storage. Scores are proxies, not measured gCO₂e, and do not multiply by current CI. The paper reports no independent Eq. (7)/(8)/(9) ablation. Grow/shrink changes allocation under amortized carbon accounting; eviction does not transfer all SSD KV back to GPU HBM.

## Claim → source

| Claim | Where it applies | Source |
|---|---|---|
| 15.1% average, up to 25.3% vs Full Cache | Llama-3 70B, FR, multi-turn only | Abstract; Sec. 6.2 timeline |
| 12.6% / 9.4% / 5.6% vs Full Cache | Llama-3 70B, average over FR, FI, ES, CISO; multi-turn, TriviaQA α=0.4, α=0.7 | Sec. 6.2 |
| 10.8% / 7.6% / 9.7% vs Full Cache | Llama-3 8B, same three workloads. Not comparable to 70B: 2×L40 BF16 and 8 TB max, versus 4×L40 INT8 and 16 TB max | Sec. 6.2 |
| 6.9–20.4% and 3.2–16.2% vs Full Cache | Day-long range, multi-turn and document α=0.4 | Sec. 6.2 |
| Up to 6.91% on a higher-CI grid such as CISO | Introduction's wording for Llama-3 70B. The deck states the Sec. 6.2 range 6.9–20.4% on PDF 36 and does not treat 6.91% as a second, independent result | Sec. 1 |
| 14.4–20.3% | Reported savings on the low-CI grids FR and FI | Sec. 6.2. Not placed on a Main slide, so it is not mixed with 15.1% |
| Prompt TTFT 1.7 s; KV load 0.03 s | ShareGPT, Llama-3 70B, 4×L40. Not an end-to-end speedup | Sec. 2.2 |
| SSD is 76.6% of embodied carbon | This Table 1 server at up to 16 TB, 480 kgCO₂e. Not a universal datacenter share | Sec. 2.3, Table 1 |
| 16 TB cache: +16.5% on FR, −7.5% on MISO | Versus no cache. Fig. 8 ratio below 1 means a reduction | Sec. 3.2, Fig. 8 |
| CISO day: 37 gCO₂e/kWh at 7 AM, 232 at 8 PM | Fig. 8b | Sec. 3.2 |
| ρ = 0.9, separate TTFT and TPOT sums | Not one joint probability | Eq. (6), Sec. 5.4 |
| Resize hourly, 1 TB steps, PuLP + CBC, 7.03 s average | Controller overhead, not the token path | Secs. 5.4, 6.1, 6.4 |
| Token hit rate; 4 TB, TriviaQA α=0.7: LRU 0.26, LCS 0.35 | Reused input tokens / total input tokens | Table 3, Sec. 6.3.2 |
| LRU + adaptive capacity: up to 10.3%, and 6.6–9.9% | Versus Full Cache, ES average CI 124 gCO₂e/kWh | Sec. 6.3.1, Fig. 15 |
| Error trims 0.0064% / 0.20% / 0.79% of savings | CI, then plus load, then plus profiler, versus ground truth | Sec. 6.5 |
| 3-year SSD life: up to 11.9%; 90 kgCO₂e/TB: up to 25% | ES grid, fixed rates in Sec. 6.6 | Secs. 6.6.2–6.6.3 |

## Prototype, traces, and the carbon model

PDF 10 是這題的回答。

- **實際系統：** GreenCache 建在 LMCache 上，LMCache 使用 vLLM 與 continuous batching。沒有論文句子說作者開發或改造了一個獨立的 GPU serving simulator。
- **工作負載：** ShareGPT 與 TriviaQA 提供內容與重用；到達過程是 Poisson，速率來自 Azure LLM trace，並縮放到這台機器的可持續吞吐量。CI 來自 CarbonCast，經既有的 EnsembleCI 預測。
- **碳會計：** CPU 用 RAPL、GPU 用 pyNVML（1 ms）。SSD 與 DRAM 功率來自規格，不是元件級實測。Embodied carbon 是 ACT 一類的攤提模型。雲端 resize 是分配與釋放容量，不是每次增減硬碟時量到的製造碳排。

## 編譯

需要 TeX Live（Beamer、pdfLaTeX）以及 PyMuPDF、Pillow。

```bash
python3 -m venv /tmp/greencache-qa
/tmp/greencache-qa/bin/pip install pymupdf pillow
/tmp/greencache-qa/bin/python scripts/build.py
/tmp/greencache-qa/bin/python scripts/validate.py
```

`build.py` 在本目錄編譯兩次，寫出 PDF 與 Overleaf ZIP，再把 ZIP 解到暫存目錄編譯兩次，並比對文字、像素與連結目標。ZIP 入口是 `main.tex`，compiler 選 **pdfLaTeX**。圖檔是 20 張未改像素的 With-Caption PNG，路徑與原始碼中的相對路徑一致。

這些 PNG 的 `pHYs` 是 3780 px/m。pdfTeX 因此用約 0.752813 pt/px，不是 1 px = 1 bp。Fig. 12、13、14 的裁切已依 With-Caption 圖片高度換算；主講頁分開顯示子圖與原圖 caption，備份頁保留底部 caption。

## QA

- 本地兩次與 ZIP 獨立兩次編譯通過，最終 log 沒有 Overfull、undefined reference 或 Warning。
- 44 頁、245 個內部連結、20 張來源圖的像素雜湊都通過。Main 17 頁。Main 可以點到全部 Backup，Backup 能回到對應 Main。
- [Main montage](output/qa/main-montage.jpg)、[Backup montage](output/qa/backup-montage.jpg)、[逐頁 PNG](output/qa/pages/)、[機器紀錄](output/qa/validation.json)、[視覺紀錄](output/qa/REVIEW.md)。

## Main speaking points

1. GreenCache 決定的是 SSD cache 容量，目標是總碳排，不是單純提高 hit rate。
2. 重用 KV 省的是重複 prefill。Decode FLOPs 還在；1.7 s 與 0.03 s 不是同一個請求的端到端加速比。
3. 多加 SSD 會加 embodied carbon。這台機器上 16 TB SSD 佔 embodied carbon 的 76.6%，不能外推成所有伺服器。
4. Fig. 8 的 ratio 小於 1 才是碳排下降。低 CI 不一定關 cache；高負載仍可能為了 SLO 留下大 cache。
5. 流程是 profile、forecast、ILP、resize + LCS。服務路徑仍是 LMCache / vLLM。
6. TTFT 與 TPOT 是兩條各自 90% 的 attainment，不是一個聯合機率。
7. 沒有獨立 GPU simulator。硬體是真的，到達與 CI 是 trace，碳排是會計模型。
8. 70B 相對 Full Cache 的三個 workload 平均是 12.6%、9.4%、5.6%。15.1% / 25.3% 只屬於 FR、multi-turn。
9. 碳排下降時 P90 仍在作者的門檻下。No Cache 常常過不了 SLO。
10. 容量會隨負載與 CI 變。LCS 的 hit rate 是 token 比例；4 TB、α=0.7 時 LRU 0.26、LCS 0.35。
11. 限制是 trace 長度、攤提假設、工作負載與 SLO。HBF 是我們的延伸問題，不是這篇的實驗結果。

## Unresolved

- Section 6.1 寫 Llama-3 8B document TTFT SLO 為 2.5 s。Fig. 13 該面板的虛線畫在 4.0 s。PDF 30 與 35 同時保留兩種說法，沒有代作者選一個。
- Section 6.2 先給出 70B 的 12.6% / 9.4% / 5.6%，後面又說高 skewness 的節省更高。數字句與這句方向不一致。簡報採用帶 respectively 的三個百分比，不用後面那句。
- Fig. 2 的 PNG 頂端有幾個被切掉的標題像素。PDF 20 去掉上方約 16 px。座標軸、CI 數字與 legend 仍在。
