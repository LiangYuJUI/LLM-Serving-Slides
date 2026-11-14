# 2026-11-18 Research Meeting — Carbon–SLO

**16 頁 Main + 1 頁 Discussion Index + 13 頁 Backup，共 30 頁。** 主動報告約 15 分 50 秒。Main 在前，Backup 在後。Main 可以獨立講完，不依賴 Backup。

- [PDF](output/pdf/2026-11-18-CarbonSLO.pdf)
- [Beamer source](2026-11-18-CarbonSLO.tex)
- [講稿](2026-11-18-CarbonSLO-Script.md)
- [證據註記](2026-11-18-CarbonSLO-Evidence.md)
- [Overleaf ZIP](output/overleaf/CarbonSLO.zip)
- [原論文](CarbonSLO-GeoDistributed-LLM-Serving-2026.pdf)

論文是 **Dissecting the Carbon–SLO Tension in Geo-Distributed LLM Serving**（Topcu, Cim, Ozturk, Kandemir; Penn State; arXiv:2610.14571v1, 10 Oct 2026）。

這不是把模型的 layer 或 MoE expert 搬到別的資料中心。決策是把 request 送到哪一個 datacenter。目標是 operational carbon，也就是 Scope 2 的用電排放，不是 GreenCache 那種 embodied carbon。

## Main 頁碼與 Backup 對應

「Main 01 / 16」是簡報頁腳上的獨立頁碼。PDF 頁碼是檔案裡的實際順序。每頁頁腳都可進入第 17 頁 Discussion Index；下表列內容中的直接連結。

| Main / PDF | 主題 | 主要圖 | 直接連結 |
|---|---|---|---|
| M01 / 1 | Cover | — | 17 |
| M02 / 2 | Why Is Carbon-Aware LLM Routing Challenging? | 動機與四項 serving 動態 | 19, 28, 29, 30 |
| M03 / 3 | Table I: Scope of Prior Work and This Paper | Table I 完整比較 | 18 |
| M04 / 4 | What Is the Carbon–SLO Optimization Goal? | 碳目標與 TTFT／TPOT | 17（INDEX） |
| M05 / 5 | How Does the Geo-Distributed Simulator Work? | Fig. 3 | 22 |
| M06 / 6 | How Does the Scheduler Predict TTFT and TPOT? | TTFT 與 TPOT 估計 | 22 |
| M07 / 7 | How Does Facility MILP Route Requests Under SLO Constraints? | 四步指派流程 | 24 |
| M08 / 8 | How Do the Other Scheduling Policies Differ? | Greedy、ILP、迭代 | 23, 24 |
| M09 / 9 | Can We Trust the Geo-Distributed Simulator? | within-node validation | 20, 21 |
| M10 / 10 | How Is the System Evaluated? | Table II 摘要 | 25 |
| M11 / 11 | Q1: Carbon without excessive SLO violations? | Fig. 4(a) | 25 |
| M12 / 12 | Facility MILP balances TTFT and carbon saving on every model | Fig. 4(b) | 19 |
| M13 / 13 | Q3: PUE and CI spread | Fig. 5 | 26 |
| M14 / 14 | Q4: Polling, overhead, topology | Fig. 6 | 26 |
| M15 / 15 | Q5: Unknown output length | Fig. 7 | 26 |
| M16 / 16 | Limitations \& Future Work | 論文限制與我們的方向 | 27 |

開場順序：M02 動機 → M03 Table I 缺口 → M04 優化目標 → M05 simulator 架構 → M06 TTFT／TPOT 估計 → M07 Facility MILP → M08 其餘三種政策 → M09 驗證 → M10 實驗設定。M02 不提前報告演算法細節或 60%／3% 結果。

## Backup

| PDF | Label | 內容 | 返回 |
|---|---|---|---|
| 17 | INDEX | Discussion Index | M07, M09, M11, M12, M16, B01–B13 |
| 18 | B01 | Table I 逐列 | M03 |
| 19 | B02 | CI、PUE、Scope 2、TTFT、TPOT、SLO | M12；另有 M02 |
| 20 | B03 | Latency 與 energy 公式 | M02；另有 B11, B12, M09 |
| 21 | B04 | 19 組 arrival rate 的 within-node validation | M09 |
| 22 | B05 | Continuous batching、KV、queue、TTFT／TPOT | M05；另有 M06 |
| 23 | B06 | Greedy 與 Standard ILP | M08 |
| 24 | B07 | Iterative ILP 與 Facility MILP | M07；另有 M08 |
| 25 | B08 | Table II、baselines、load label | M10 |
| 26 | B09 | Fig. 5–7 的數值讀法 | M13；另有 M14, M15 |
| 27 | B10 | 限制、可重現性、我們的方向 | M16 |
| 28 | B11 | Figure 1：逐步延遲為何隨負載變 | M02；另有 B03 |
| 29 | B12 | Figure 2：功率與能量為何要分 phase 與負載 | M02；另有 B03 |
| 30 | B13 | 最低 CI 站不一定 SLO-feasible 的示意 | M02；另有 B02 |

## Figure → slide

| Figure | 頁面 | 用法 |
|---|---|---|
| 1 Latency model | B11 | With-Caption 原圖；Main 只留連結 |
| 2 Power model | B12 | With-Caption 原圖；Main 只留連結 |
| 3 Simulator | M05 | With-Caption |
| 4(a) Carbon–SLO | M11 | Without-Caption 的上半，含論文自己的 (a) caption |
| 4(b) TTFT tail | M12 | Without-Caption 的下半，含 (b) caption |
| 5 PUE / CI | M13 | 拆成 (a)(b)，兩張都保留座標軸與 legend |
| 6 Overhead / polling / topology | M14 | Without-Caption 全圖；右側是讀圖 |
| 7 OSL / prompt length | M15 | Without-Caption 全圖 |

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

`build.py` 在本目錄編譯兩次，寫出 PDF 與 Overleaf ZIP，再把 ZIP 解到暫存目錄編譯兩次，並比對文字、像素與連結。驗證固定為 16 Main、1 Index、13 Backup，共 30 頁，並檢查語意連結、雙向返回、M02 動機內容與 M03 表格完整性。負向測試會刻意刪除／誤導連結及刪除證據，確認 QA 能攔截。ZIP 入口是 `main.tex`，compiler 選 **pdfLaTeX**。

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
