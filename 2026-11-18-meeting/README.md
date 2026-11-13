# 2026-11-18 Research Meeting — Carbon–SLO

**20 頁 Main + 1 頁 Discussion Index + 10 頁 Backup，共 31 頁。** 主動報告約 19 分鐘。Main 在前，Backup 在後。Main 可以獨立講完，不依賴 Backup。

- [PDF](output/pdf/2026-11-18-CarbonSLO.pdf)
- [Beamer source](2026-11-18-CarbonSLO.tex)
- [講稿](2026-11-18-CarbonSLO-Script.md)
- [證據註記](2026-11-18-CarbonSLO-Evidence.md)
- [Overleaf ZIP](output/overleaf/CarbonSLO.zip)
- [原論文](CarbonSLO-GeoDistributed-LLM-Serving-2026.pdf)

論文是 **Dissecting the Carbon–SLO Tension in Geo-Distributed LLM Serving**（Topcu, Cim, Ozturk, Kandemir; Penn State; arXiv:2610.14571v1, 10 Oct 2026）。

這不是把模型的 layer 或 MoE expert 搬到別的資料中心。決策是把 request 送到哪一個 datacenter。目標是 operational carbon，也就是 Scope 2 的用電排放，不是 GreenCache 那種 embodied carbon。

## Main 頁碼與 Backup 對應

「Main 01 / 20」是簡報頁腳上的獨立頁碼。PDF 頁碼是檔案裡的實際順序。每頁頁腳都可進入第 21 頁 Discussion Index；下表列內容中的直接連結。

| Main / PDF | 主題 | 主要圖 | 直接連結 |
|---|---|---|---|
| M01 / 1 | Cover | — | 21 |
| M02 / 2 | Why Is Carbon-Aware LLM Routing Challenging? | 動機與四項 serving 動態 | 23 |
| M03 / 3 | Table I: Scope of Prior Work and This Paper | Table I 完整比較 | 21（INDEX） |
| M04 / 4 | Why Not Always Choose the Greenest Datacenter? | 概念示意圖 | 23 |
| M05 / 5 | What Do Previous Approaches Miss? | 建模缺口對 routing 的影響 | 22 |
| M06 / 6 | What Is the Carbon–SLO Scheduling Problem? | 碳與 SLO | 23 |
| M07 / 7 | How Does the Geo-Distributed Simulator Work? | Fig. 3 | 26 |
| M08 / 8 | How Is LLM Serving Latency Modeled? | Fig. 1 | 24 |
| M09 / 9 | How Are Power and Energy Modeled? | Fig. 2 | 24 |
| M10 / 10 | Real GPUs or a Simulator? How Is It Validated? | — | 25 |
| M11 / 11 | Which Scheduling Policies Are Proposed? | 四層政策 | 27, 28 |
| M12 / 12 | How Do Greedy and Standard ILP Work? | Eq. (1)–(2) 摘要 | 27 |
| M13 / 13 | Why Iterative ILP and Facility MILP? | facility 目標 | 28 |
| M14 / 14 | How Is the System Evaluated? | Table II 摘要 | 29 |
| M15 / 15 | Q1: Carbon without excessive SLO violations? | Fig. 4(a) | 29 |
| M16 / 16 | Q2: Tail latency under high load | Fig. 4(b) | 23 |
| M17 / 17 | Q3: PUE and CI spread | Fig. 5 | 30 |
| M18 / 18 | Q4: Polling, overhead, topology | Fig. 6 | 30 |
| M19 / 19 | Q5: Unknown output length | Fig. 7 | 30 |
| M20 / 20 | Conclusion | — | 31 |

開場順序：M02 動機與建模需求 → M03 Table I 證據 → M04 routing 情境 → M05 缺漏對決策的影響。M02 不提前報告演算法細節或 60%／3% 結果。

## Backup

| PDF | Label | 內容 | 返回 |
|---|---|---|---|
| 21 | INDEX | Discussion Index | M10, M13, M15, M16, M20, B01–B10 |
| 22 | B01 | Table I 逐列 | M05 |
| 23 | B02 | CI、PUE、Scope 2、TTFT、TPOT、SLO | M06；另有 M02, M04, M16 |
| 24 | B03 | Latency 與 energy 公式 | M08；另有 M09 |
| 25 | B04 | 19 組 arrival rate 的 within-node validation | M10 |
| 26 | B05 | Continuous batching、KV、queue | M07 |
| 27 | B06 | Greedy 與 Standard ILP | M12；另有 M11 |
| 28 | B07 | Iterative ILP 與 Facility MILP | M13；另有 M11 |
| 29 | B08 | Table II、baselines、load label | M14；另有 M15 |
| 30 | B09 | Fig. 5–7 的數值讀法 | M17；另有 M18, M19 |
| 31 | B10 | 限制、可重現性、我們的方向 | M20 |

## Figure → slide

| Figure | Main | 用法 |
|---|---|---|
| 1 Latency model | M08 | With-Caption，全寬 |
| 2 Power model | M09 | With-Caption |
| 3 Simulator | M07 | With-Caption |
| 4(a) Carbon–SLO | M15 | Without-Caption 的上半，含論文自己的 (a) caption |
| 4(b) TTFT tail | M16 | Without-Caption 的下半，含 (b) caption |
| 5 PUE / CI | M17 | 拆成 (a)(b)，兩張都保留座標軸與 legend |
| 6 Overhead / polling / topology | M18 | Without-Caption 全圖；右側是讀圖 |
| 7 OSL / prompt length | M19 | Without-Caption 全圖 |

`figures/crops/` 是原始 Without-Caption PNG 的像素裁切。沒有重繪曲線，也沒有改到 `With-Caption/` 與 `Without-Caption/` 裡的 14 張原圖。論文沒有 Figure 8。

## 編譯

需要 TeX Live（Beamer、pdfLaTeX）以及 PyMuPDF、Pillow。

```bash
python3 -m venv /tmp/carbonslo-qa
/tmp/carbonslo-qa/bin/pip install pymupdf pillow
/tmp/carbonslo-qa/bin/python scripts/build.py
/tmp/carbonslo-qa/bin/python scripts/validate.py
/tmp/carbonslo-qa/bin/python scripts/test_navigation.py
```

`build.py` 在本目錄編譯兩次，寫出 PDF 與 Overleaf ZIP，再把 ZIP 解到暫存目錄編譯兩次，並比對文字、像素與連結。驗證固定為 20 Main、1 Index、10 Backup，共 31 頁，並檢查語意連結、雙向返回、M02 動機內容與 M03 表格完整性。負向測試會刻意刪除／誤導連結及刪除證據，確認 QA 能攔截。ZIP 入口是 `main.tex`，compiler 選 **pdfLaTeX**。

## QA

- [Main montage](output/qa/main-montage.png)、[Backup montage](output/qa/backup-montage.png)
- [逐頁 PNG](output/qa/pages/)、[導覽稽核](output/qa/navigation-audit.md)、[validation.json](output/qa/validation.json)、[負向導覽測試](output/qa/navigation-tests.json)

## 已知限制

- End-to-end validation 是單節點、Llama-3.1-8B、三個 vLLM engine。不是 16 個實體資料中心。
- 「up to 60%」對的是 round-robin，而且是上界。作者說的 average SLO violation 3% 不是每個 load 都是 3%。
- 結論的 26–60% 是 base setting 跨 load 的摘要。Fig. 5(b) 在最低 CV、高負載的 Llama 是 13%，落在這個區間外面。
- Fig. 4(b) 印出的 facility MILP 減碳（Llama 26%、Mixtral 35%）和 PUE 段落的 29.2% / 36.6% 起點不完全相同。PDF 沒有解釋這個差。投影片兩組都保留，沒有平均成一個數字。
- 「respectively」那句把 12.5% 與 2.4% 接在 dense 與 Mixtral 後面。講稿依這個語序讀，不另外指定是哪一個 solver。
- 這份簡報沒有重跑作者的 simulator。若程式庫與 PDF 不一致，以本機 PDF 為準，並記在 Evidence。
- Facility MILP 的 \(y_d\) 是這個 window 要不要使用該 DC 的成本模型。它沒有關掉資料中心，也沒有消掉 RTT。
- 最後一頁「heterogeneous GPU、HBM/HBF、attention/expert placement」是我們之後可能做的方向，不是這篇論文的結果。
