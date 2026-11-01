# 2026-11-04 Research Meeting — Helix

新版採 **15 頁 Main + 42 頁 Discussion / Backup（含 1 頁索引），共 57 頁**。主動報告約 15–20 分鐘，整場含問答約 30–40 分鐘；這是整體規劃，不是逐頁計時。所有 Main 在前，Backup 在後，不交錯。

- [PDF](output/pdf/2026-11-04-Helix.pdf)
- [Beamer source](2026-11-04-Helix.tex)
- [Overleaf ZIP](output/overleaf/Helix.zip)
- [原論文](ASPLOS25_Helix.pdf)

不依賴逐字講稿。[Helix_scripts.md](Helix_scripts.md) 保留舊版 37 頁內容作歷史參考，**不對應新版頁碼**。

## Main 頁碼與 Backup 對應

頁碼為實際 PDF 頁碼，與頁腳一致。M13 / M14 分開呈現 placement / scheduling ablation，讓兩張完整圖各有一頁。

| Main / PDF | 主題 | 對應 Backup PDF 頁 |
|---|---|---|
| M01 / 1 | Helix | 16（索引） |
| M02 / 2 | Why Do We Need Helix? | 17, 18, 19, 20 |
| M03 / 3 | What Does Helix Optimize? | 21 |
| M04 / 4 | How Does One Request Run? | 22, 35 |
| M05 / 5 | How Does Max Flow Model Serving? | 23, 24, 25, 26, 27, 28 |
| M06 / 6 | How Does MILP Decide Placement? | 29, 30, 31, 32, 33, 34, 54, 55 |
| M07 / 7 | How Does Runtime Scheduling Work? | 36, 37, 38 |
| M08 / 8 | How Are Weights and KV Cache Managed? | 39, 40 |
| M09 / 9 | How Is Helix Evaluated? | 41, 42, 43, 44 |
| M10 / 10 | Does Helix Improve Single-Cluster Serving? | 45, 46 |
| M11 / 11 | Does Helix Work Across Regions? | 47, 48 |
| M12 / 12 | What Happens with More GPU Types? | 49 |
| M13 / 13 | Where Do the Gains Come From: Placement? | 50, 51 |
| M14 / 14 | Where Do the Gains Come From: Scheduling? | 52, 53 |
| M15 / 15 | Conclusion & Discussion | 16, 56, 57 |

## Backup 分組

| 區塊 | PDF 頁 | 內容 | 返回 Main |
|---|---|---|---|
| Discussion Index | 16 | A–E 入口 | M15 |
| A — Background and Motivation | 17–20 | GPU 規格、TP / PP / DP、Petals / Swarm、Fig. 1 | M02 |
| B — Max Flow and MILP | 21–34 | 設計分工、架構、graph、cost model、全部主要 MILP constraints、solver | M03–M06 |
| C — Runtime and Implementation | 35–41 | lifecycle、per-request pipeline、IWRR、KV masking、partial inference、vLLM / simulator | M04、M07–M09 |
| D — Experimental Evidence | 42–55 | 設定、workload、完整 Figures 6–12、數據表、ablation、solver quality | M06、M09–M14 |
| E — Limitations and Discussion | 56–57 | static placement、KV estimation、latency、simulation scope、研究方向 | M15 |

### 完整 Backup 頁碼

| PDF | Named destination | 主題 | Back to Main |
|---|---|---|---|
| 16 | `INDEX` | Discussion Index | M15 |
| 17 | `B01` | Why Heterogeneous and Geo-Distributed Serving? | M02 |
| 18 | `B02` | Parallelism Across Nodes and GPUs | M02 |
| 19 | `B03` | Uniform Model Placement Is Sub-Optimal | M02 |
| 20 | `B04` | Network-Unaware Routing Creates Congestion | M02 |
| 21 | `B05` | Helix Design Requirements | M03 |
| 22 | `B06` | Helix System Overview | M04 |
| 23 | `B07` | From Model Placement to a Flow Network | M05 |
| 24 | `B08` | Max-Flow Graph Abstraction | M05 |
| 25 | `B09` | Modeling Compute Capacity | M05 |
| 26 | `B10` | Modeling Network Capacity | M05 |
| 27 | `B11` | Why Max Flow Represents Serving Throughput | M05 |
| 28 | `B12` | Worked Three-Node Example | M05 |
| 29 | `B13` | MILP Variables and Objective | M06 |
| 30 | `B14` | Placement and Memory Constraints | M06 |
| 31 | `B15` | Flow and Compute Constraints | M06 |
| 32 | `B16` | Connectivity and Network Constraints | M06 |
| 33 | `LINEAR` | Full Connectivity Linearization | M06 |
| 34 | `B17` | Making the MILP Practical | M06 |
| 35 | `B18` | Runtime Components and Control Flow | M04 |
| 36 | `B19` | Per-Request Pipelines | M07 |
| 37 | `B20` | Converting Max-Flow Weights into Scheduling | M07 |
| 38 | `B21` | Pipeline Scheduling Example | M07 |
| 39 | `B22` | KV-Cache Masking and Backpressure | M08 |
| 40 | `PARTIAL` | Partial Inference and Request-Specific KV | M08 |
| 41 | `B23` | Implementation and Prototype | M09 |
| 42 | `B24` | Evaluation Methodology | M09 |
| 43 | `SETUP` | Hardware, Baselines, and Normalization | M09 |
| 44 | `B25` | Workload Characteristics | M09 |
| 45 | `FIG6` | Complete Figure 6: Single-Cluster Results | M10 |
| 46 | `B26` | Single-Cluster Results | M10 |
| 47 | `FIG7` | Complete Figure 7: Geo-Distributed Results | M11 |
| 48 | `B27` | Geo-Distributed Results | M11 |
| 49 | `B28` | High GPU-Heterogeneity Results | M12 |
| 50 | `FIG9` | Complete Figure 9: Model Placement Deep Dive | M13 |
| 51 | `B29` | Model Placement Deep Dive | M13 |
| 52 | `FIG10` | Complete Figure 10: Request Scheduling Deep Dive | M14 |
| 53 | `B30` | Request Scheduling Deep Dive | M14 |
| 54 | `B31` | MILP Optimization Ablation | M06 |
| 55 | `B32` | Solver Time and Solution Quality | M06 |
| 56 | `B33` | Limitations and Threats to Validity | M15 |
| 57 | `FUTURE` | Research Directions and Applicability | M15 |

## 導覽方式

Main 的 Details 按鈕進入相關技術頁。每張 Backup 的 **Back to Main** 返回對應主題，不返回封面。每頁頁腳都有 **Discussion index**，索引再跳到 A–E。

使用穩定的 Beamer `frame[label=...]` destinations。PDF 檢查逐一驗證實際 annotation 的目的頁，並核對所有來源按鈕及每頁回程連結，不只搜尋 LaTeX `hyperlink`。

## 圖片與版面

所有 12 張 Figure 均直接引用 `Helix/Without-Caption/`。`Helix/` 中原始 12 張 PNG 全數保留且未修改。沒有 fallback 到舊圖，也沒有重新加入 `\caption{...}` 或外部長 caption。

- 大幅放大 Main 的 Figures 1–4、6–10；縮小邊界，讓寬圖使用頁面寬度，讓圖、簡短解讀、來源與導覽共同使用頁面高度。
- M05（PDF 5）及 cost example（PDF 28）用 `graphicx` 的兩個 viewport 顯示 Figure 2 的實體拓撲及 flow graph，略去圖內長段說明。沒有重製或改寫 PNG；所有節點、capacity、layer table、payload labels 均保留。PDF 24 仍提供完整 Figure 2。
- 其他圖不裁切、不拆分、不拉伸；保留素材自帶的 subfigure labels 和 legends。若 caption-free 素材沒有底排標籤，圖旁文字明列 subplot 順序與意義。
- Backup 圖片與數值表分頁，避免把大圖壓回小圖。短內容採垂直平衡，較完整的公式與表格保持可讀。
- 原始圖內的 subfigure 說明是來源像素的一部分；未在圖下重複貼上外部 caption。

## 科學依據與解讀條件

主要依據為本地 `ASPLOS25_Helix.pdf`。各頁附 section / figure 來源。新 lifecycle 是原文流程的整理，partial inference 圖與 bandwidth 計算標明 illustrative，研究延伸標明 interpretation。

- Placement / edge capacity / optimized flow / request pipeline 分開描述。Max flow 的 objective 是 throughput，不是所有 latency metrics。
- 3.29× 限定為 42-node simulation、LLaMA-2 70B、online decode throughput、相對 SP。
- Fig. 6 包含 24-node prototype 與 simulator 對照；Fig. 7 / 8 為 simulation。
- Fig. 9 固定 Helix scheduler；Fig. 10 固定 Helix placement。Petals 僅為 placement baseline。
- Pruning、10 分鐘停滯停止與 4 小時預算，不等於所有部署都已證明 global optimum。
- Fig. 11 正文的「43% / 8% less time」與圖中 1600→1120 / 3100→2877 不完全一致。PDF 54 同時保留正文說法並明列：速度比 1.43× / 1.08×，時間實際節省約 30% / 7.2%，避免混淆分母。
- Appendix A 的 prototype artifact 使用 dummy weights；實驗支持系統效能，不能當成生成品質驗證。

## 編譯與 ZIP 驗證

需要 TeX Live（含 Beamer、TikZ、Latin Modern）及 `pdflatex`。請使用以下 build 腳本，避免直接編譯在專案目錄留下中間檔。

可重複執行的完整 build / QA（在本目錄）：

```bash
python3 -m venv /tmp/helix-qa-env
/tmp/helix-qa-env/bin/pip install pymupdf pillow
/tmp/helix-qa-env/bin/python scripts/build.py
/tmp/helix-qa-env/bin/python scripts/validate.py
```

`build.py` 編譯兩次、更新 PDF 與 ZIP，再將 ZIP 解壓到獨立暫存目錄編譯兩次，逐頁比較文字、rendered pixels 與連結目標。`validate.py` 檢查所有 named destinations、內部連結目的頁、文字邊界、圖像像素雜湊，再 render 全部頁面及 montage。自動檢查不能取代人工視覺檢查。

Overleaf：建立專案並上傳 `output/overleaf/Helix.zip`，入口為 `main.tex`，compiler 選 **pdfLaTeX**。ZIP 包含 source 與 12 張 Without-Caption 圖，無需依賴 repo 其他目錄，也不需要歷史講稿或原論文才能編譯。

## 本次驗證

- 本地 pdfLaTeX 兩次及 ZIP 獨立編譯兩次成功；最終 log 無 warnings、undefined references 或 overfull boxes。
- 57 頁輸出一致，15 頁 Main 已逐頁視覺檢查，所有 Backup 已 render 並檢查 montage，密集公式與數據頁另行放大檢查。
- **224 個實際 PDF 內部連結**全部解析，Main / Backup / Index 目的頁皆正確。
- **12 / 12 圖片**以 PDF embedded pixels 對照來源 PNG 的雜湊確認，不只核對檔名。
- 未發現內容裁切、公式或 navigation 與 footline 重疊。Figure 2 的 viewport 是明確記錄的例外，完整來源仍可查看。
- [視覺檢查與圖片放大對照](output/qa/REVIEW.md)、[機器檢查紀錄](output/qa/validation.json)、[Main montage](output/qa/main-montage.jpg)、[Backup montage](output/qa/backup-montage.jpg)。編譯 log / recorder 僅存在於自動清除的暫存目錄；單頁 render 預設也在暫存目錄，只有明確指定 `--render-dir` 才保留。

## Takeaway 清理與乾淨編譯（2026-11-01）

- 移除所有大型 Takeaway 背景與舊 `\takeaway` macro。`\slidenote` 現在只有來源和導覽兩個參數；Backup 保留 `\src`、`\back`。
- M03 的 latency objective 限制、M05 的 steady-flow 意義、M06 的 global-optimum 限制、M10 與 M12 的 throughput / latency trade-off 改為正文。M11 的 30B、online、simulation、vs. Swarm 條件完整保留。M07 / M08 的 interleaving 和 KV admission 整合進原有條目。
- Backup 的獨有補充（變數規模、KV admission、pruned trace、simulated 30B online 比較、3.29× 四捨五入及 solver 證據限制等）改為普通正文。重複摘要移除。
- 圖片放大：PDF 7 / 10 / 12 / 22。PDF 2 / 4 / 5 / 11 / 13 / 14 的圖已受頁寬限制，保留尺寸並重新平衡垂直位置。所有圖像像素、公式與實驗數值保持不變。
- `build.py` 不再複製 `.log` / `.fls` 到 QA。成功與失敗均由 `TemporaryDirectory` 清理中間檔；失敗仍輸出必要錯誤摘要。
- 新增局部 `.gitignore`，只涵蓋 LaTeX 中間檔。既有 9 個根目錄中間檔已確認並刪除，沒有已追蹤中間檔需要取消追蹤。
- `validate.py` 新增實際 PDF 藍色大區塊、56 頁來源、5 個關鍵主張頁、導覽連結次數及中間檔殘留檢查。Discussion Index 本來就無論文來源。
- 重新 build 後，中間檔仍為零。開始任務時已存在的未追蹤根目錄 PDF 保留原樣，不納入本次 commit。

## 方法論文字釐清（2026-11-02）

本次僅修改 PDF 3、4、5、6、34，其餘 52 頁與前版逐頁 rendered pixels 相同。

- M03：Placement / Capacity / Flow 三項，明確說明 placement 與 flow 共同最佳化，保留 throughput objective、capacity constraint 及 latency 限制。
- M04：Figure 3 搭配 offline planning、online scheduling、pipeline execution、decode reuse；IWRR 使用 optimized flow weights，同一 request 沿用 pipeline 與 KV，不逐 request / token 重跑 MILP。
- M05 / M06：區分固定 placement 的 `MaxFlow(G(Psi))` throughput model 與 joint MILP，維持原順序及限制式。
- PDF 34：Petals / Swarm / SP heuristics 提供 warm-start candidates，Gurobi 繼續搜尋，不保證初始方案最優。Pruning、warm start、early stopping 分開說明。

PDF 與 ZIP 獨立編譯驗證通過，仍為 57 頁、224 個內部連結及 12 張來源圖片；第 3–7、34 頁已視覺檢查，來源、頁碼與雙向導覽保留，無 LaTeX 中間檔殘留。詳見 [最新 QA 紀錄](output/qa/REVIEW.md)。
