# 2026-11-11 Research Meeting — GreenCache

**15 頁 Main + 25 頁 Discussion / Backup（含 1 頁索引），共 40 頁。** 主動報告約 15–20 分鐘。Main 在前，Backup 在後。

- [PDF](output/pdf/2026-11-11-GreenCache.pdf)
- [Beamer source](2026-11-11-GreenCache.tex)
- [Overleaf ZIP](output/overleaf/GreenCache.zip)
- [原論文](GreenCache-Research-Meeting-2026-11-11/GreenCache-Carbon-Aware-KV-Caching-SIGMETRICS2026.pdf)

這不是一篇一般的 KV-cache 加速論文。主線是：在 TTFT 與 TPOT 的 SLO attainment 約束下，同時考慮 operational carbon 與 SSD embodied carbon，動態決定 cache 容量。

## Main 頁碼與 Backup 對應

頁碼是實際 PDF 頁碼。

| Main / PDF | 主題 | 主要圖 | 直接連結 |
|---|---|---|---|
| M01 / 1 | GreenCache | — | 1, 16 |
| M02 / 2 | Why Do We Need GreenCache? | Fig. 7 | 1, 16, 17, 23, 24 |
| M03 / 3 | Why Is a Fixed Cache Size Suboptimal? | Fig. 8 | 1, 16, 18, 25 |
| M04 / 4 | What Does GreenCache Optimize? | 最佳化目標 + SLO | 1, 16, 23, 24 |
| M05 / 5 | How Does GreenCache Work? | Fig. 10 | 1, 16, 26, 27 |
| M06 / 6 | How Is Cache Capacity Selected? | Profiling / Forecast / ILP | 1, 16, 27, 28, 29 |
| M07 / 7 | What Does LCS Evict? | Eq. (7) | 1, 16, 30 |
| M08 / 8 | Real Prototype, Traces, or a Simulator? | — | 1, 16, 31 |
| M09 / 9 | What Are the Evaluation Settings? | — | 1, 16, 28 |
| M10 / 10 | Q1: Does GreenCache Reduce Carbon? | Fig. 12 | 1, 16, 32 |
| M11 / 11 | Q2: Does GreenCache Still Meet SLOs? | Fig. 13 | 1, 16, 33 |
| M12 / 12 | Q3: Does Capacity Track Load and CI? | Fig. 14 | 1, 16, 34 |
| M13 / 13 | Q4: Does Adaptive Sizing Help? | Fig. 15 | 1, 16, 26 |
| M14 / 14 | Q4: Does LCS Improve Token Reuse? | Table 3 | 1, 16, 30 |
| M15 / 15 | Conclusion and Limitations | — | 1, 16, 40 |

所有 Main 的頁腳都能打開第 16 頁索引。Fig. 1 的 KV reuse 基本機制移至第 17 頁 B00。

## Backup

| PDF | Label | 內容 | 返回 / 導覽 |
|---|---|---|---|
| 16 | INDEX | Discussion Index | 8, 15, 16, 17, 26, 27, 28, 31, 32, 34, 36, 40 |
| 17 | B00 | Why Cache Repeated Context? | 2, 16, 17, 19, 20 |
| 18 | B01 | Which Grids, and How Fast Does CI Move? | 3, 16, 17, 19 |
| 19 | B02 | Where Does Caching Change Latency? | 16, 17, 20 |
| 20 | B03 | How Long Is the Repeated Context? | 16, 17, 21 |
| 21 | B04 | What Does Request Rate Change? | 2, 16, 17, 22 |
| 22 | B05 | Does a Bigger Cache Always Raise the Hit Rate? | 3, 16, 17, 23 |
| 23 | B06 | Table 1: Embodied Carbon on This Server | 2, 4, 16, 17, 24 |
| 24 | B07 | Carbon Accounting, Equations (1)--(5) | 2, 4, 16, 17, 25 |
| 25 | B08 | Load and CI Push Capacity in Opposite Ways | 3, 16, 17, 26 |
| 26 | B09 | What Do the Profiles Actually Contain? | 5, 13, 16, 26, 27 |
| 27 | B10 | Equation (6): Capacity ILP | 5, 6, 16, 26, 28 |
| 28 | B11 | SLO Thresholds and Decision Granularity | 6, 9, 16, 26, 29 |
| 29 | B12 | Load Forecast and Carbon-Intensity Forecast | 6, 16, 26, 30 |
| 30 | B13 | LCS Scores for the Two Tasks | 7, 14, 16, 26, 31 |
| 31 | B14 | What Is Measured, Replayed, and Modeled? | 8, 16, 31, 32 |
| 32 | B15 | Figure 12b: Llama-3 8B Carbon | 10, 16, 31, 33 |
| 33 | B16 | Figure 13b: Llama-3 8B SLO Timelines | 11, 16, 31, 34 |
| 34 | B17 | Figure 14b: Document Timeline, α=0.4 | 12, 16, 31, 35 |
| 35 | B18 | Solver Time per Resize | 6, 16, 31, 36 |
| 36 | B19 | Do Forecast and Profile Errors Spend the Savings? | 6, 16, 36, 37 |
| 37 | B20 | How Often Should the Cache Resize? | 6, 16, 36, 38 |
| 38 | B21 | SSD Lifetime Changes the Embodied Weight | 15, 16, 36, 39 |
| 39 | B22 | SSD Embodied Carbon Is an Assumption | 15, 16, 36, 40 |
| 40 | B23 | Limits, and What We Would Not Claim | 15, 16, 36 |

## Figure → slide

| Figure | Main PDF | Backup PDF |
|---|---|---|
| 1 | — | 17 |
| 2 | — | 18 |
| 3 | — | 19 |
| 4 | — | 20 |
| 5 | — | 21 |
| 6 | — | 22 |
| 7 | 2 | — |
| 8 | 3 | — |
| 9 | — | 25 |
| 10 | 5 | — |
| 11 | — | 26 |
| 12 | 10 | 32 |
| 13 | 11 | 33 |
| 14 | 12 | 34 |
| 15 | 13 | — |
| 16 | — | 35 |
| 17 | — | 36 |
| 18 | — | 37 |
| 19 | — | 38 |
| 20 | — | 39 |

Fig. 7 保留完整原圖與 caption：第 2 頁聚焦 (a) 的負載比較。第 3 頁用 Fig. 8 說明不同電網與同一電網不同時段的 CI 趨勢及碳排取捨。Fig. 12、13、14 在 Main 放大相關子圖，Backup 放另一半；legend 與 caption 均來自原始 PNG viewport，沒有重繪座標軸。

## Claim → source

| Claim | Where it applies | Source |
|---|---|---|
| 15.1% average, up to 25.3% vs Full Cache | Llama-3 70B, FR, multi-turn only | Abstract; Sec. 6.2 timeline |
| 12.6% / 9.4% / 5.6% vs Full Cache | Llama-3 70B, average over FR, FI, ES, CISO; multi-turn, TriviaQA α=0.4, α=0.7 | Sec. 6.2 |
| 10.8% / 7.6% / 9.7% vs Full Cache | Llama-3 8B, same three workloads. Not comparable to 70B: 2×L40 BF16 and 8 TB max, versus 4×L40 INT8 and 16 TB max | Sec. 6.2 |
| 6.9–20.4% and 3.2–16.2% vs Full Cache | Day-long range, multi-turn and document α=0.4 | Sec. 6.2 |
| Up to 6.91% on a higher-CI grid such as CISO | Introduction's wording for Llama-3 70B. The deck states the Sec. 6.2 range 6.9–20.4% on PDF 34 and does not treat 6.91% as a second, independent result | Sec. 1 |
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

PDF 8 是這題的回答。

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
- 40 頁、193 個內部連結、20 張來源圖的像素雜湊都通過。Main 可以點到全部 Backup。
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

- Section 6.1 寫 Llama-3 8B document TTFT SLO 為 2.5 s。Fig. 13 該面板的虛線畫在 4.0 s。PDF 28 與 33 同時保留兩種說法，沒有代作者選一個。
- Section 6.2 先給出 70B 的 12.6% / 9.4% / 5.6%，後面又說高 skewness 的節省更高。數字句與這句方向不一致。簡報採用帶 respectively 的三個百分比，不用後面那句。
- Fig. 2 的 PNG 頂端有幾個被切掉的標題像素。PDF 18 去掉上方約 16 px。座標軸、CI 數字與 legend 仍在。
