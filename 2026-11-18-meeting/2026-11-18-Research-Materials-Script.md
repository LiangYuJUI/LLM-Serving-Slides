# Research Materials & Supporting Evidence — 講稿

2026 年 11 月 18 日研究會議。主講 Yu-Jui Liang，指導教授 Hsiang-Yun Cheng。
封面為 slide 1。全稿 17 頁，頁碼 1/17–17/17。敘事順序是 Previous Work、Embodied Carbon、HBM/HBF Performance and Energy，最後才是 Proposed Research。這是證據與提案，不是已完成的減碳實驗。

研究主題：Carbon- and Power-Aware Cross-Data-Center LLM Serving with Heterogeneous GPU and HBM/HBF Memory Co-Design。

## 1 — 封面

今天的順序是：先看前人研究留下的缺口，再看我們已找到的製造碳排資料，接著用 HBM/HBF 的效能與能耗說明瓶頸，最後才提出自己的架構和研究計畫。

## 2 — 證據地圖

主題是 Carbon- and Power-Aware Cross-DC LLM Serving。四張卡片對應四個章節：前人工作、HBM/HBF embodied carbon、記憶體效能與能耗，以及我們的提案。Backup 不放在這四章裡。

## 3 — Carbon–SLO：共享狀態、各自決策

Carbon–SLO 的 Global Provisioner 週期性收集各資料中心的碳強度、batch、queue、KV 和 RTT，再廣播同一份 snapshot。區域 scheduler 仍各自決定，所以可能同時把流量送進同一個低碳資料中心。

三個限制直接構成我們的動機。它只計 operational carbon，沒有 allocated embodied carbon。區域決策彼此獨立。模型校準在單一 GPU 型號 A100 上，還沒有 heterogeneous GPU。這頁是前人架構與缺口，不是我們的實驗結果。

## 4 — GreenCache：碳感知的 SSD cache

GreenCache 用預測的碳強度、請求率，以及功率和 SLO profile，每小時用 ILP 選 SSD 上的 KV cache 容量，目標是在 TTFT / TPOT 之下降低 total carbon。Cache 變大可以少做 prefill；cache 變小則降低分攤的 embodied carbon。

它已經同時考慮 operational 和 allocated embodied carbon，但範圍停在本地 SSD cache。沒有跨資料中心路由，沒有 heterogeneous GPU 或 HBM/HBF placement，也沒有分開的 prefill / decode 功率模型。SSD KV cache 不能直接當成 HBF expert storage。

## 5 — 可沿用的方法與還缺的輸入

Carbon–SLO 提供 SLO-aware geo scheduling、batching 和 queueing simulation，以及 GPU power、CI、PUE、WAN RTT。GreenCache 提供 KV reuse、adaptive cache sizing 和 total-carbon accounting，以及多輪 workload、cache profile 和碳模型。

還缺的是 heterogeneous GPU power、HBM/HBF 的存取能量、容量和傳輸成本，以及 MoE expert traces、KV reuse 和 HBM/HBF embodied-carbon estimates。下一章先看製造碳排資料，再看記憶體能耗；整合本身仍是提案。

## 6 — HBM/HBF 製造碳排證據

目前可追查的起點是 REEL LCI v1.0。同一個方法架構裡有 HBM3、HBM3E、HBM4 和 HBF，但完整 inventory 需要授權。HBF 是前瞻工程模型，沒有量產碳排驗證。這頁支持敏感度分析，不能說成已驗證的 HBF production measurement。About REEL / LCI 會開到第 16 頁。

## 7 — 每個 stack 的製造碳排

REEL v1.0 的 screening estimates：HBM3 8-Hi 16 GB 是 13.52 kg，12-Hi 24 GB 是 19.81 kg，HBM3E 12-Hi 36 GB 約 20.6 kg。HBF Gen 1 512 GiB 是 225.9 kg，約為 HBM3 8-Hi 的 16.7 倍。這不是等容量比較。數字是文章公布的模型估計，不是廠商實測。

## 8 — 每單位標示容量的製造碳排

把 stack 碳排除以標示容量後，四個指標約是 0.845、0.825、0.572 和 0.441。依這個名義正規化，HBF 比 HBM3 8-Hi 低約 47.8%。HBM 標 GB、HBF 標 GiB，所以只能稱 nominal capacity unit，不能說已驗證每 GiB 降低 47.8%，也不能由此推論服務能耗較低。

## 9 — HBF 碳排估計的假設與限制

模型假設是 16-Hi、512 GiB、232-layer NAND，以及 65 nm / 28 nm 製程代理，並用 175.6 mm² 封裝外框代理 die 面積。限制是沒有驗證過的量產碳排、面積與位元密度不一致，而且 interposer、substrate 和 package assembly 不在這個 stack 邊界內。可以做初步建模，不能當成已驗證的製造足跡。

## 10 — HBM 與 HBF 的存取參數

Characterizing HBF 的 Table 1：每 stack 容量 24 GB 對 375 GB，讀頻寬都假設 1,000 GB/s，寫頻寬 1,000 對 8 GB/s，讀取啟動 0.1 對 20 µs，寫入啟動 0.1 對 250 µs。讀取能量 3.4 對 6.8 pJ/bit，寫入 3.4 對 100。HBF 寫入與部分延遲使用 SSD proxy，P/E cycles 假設 100,000。容量優勢不能單獨代表省能。參數來源在第 17 頁。

## 11 — 工作完成時間

同一個 GLM-5.2、16 張模擬 GPU、TP16/EP16、100k-turn 設定。HBM-only 8+0 是 11,354 秒；H³ 8+8 不論 weights 放 HBM 或 HBF，都約 4,540 秒。完成時間大約少 60%，但 HBM-only 只有 8 個 stack，不是等硬體比較。這是模擬，表示多出來的容量在這個設定下可以縮短完成時間。

## 12 — 模擬服務能耗

同一組設定的模型能量是 HBM-only 9.11 MJ、H³ HBM weights 7.19 MJ、H³ HBF weights 9.54 MJ。要比較的是相同 8+8 硬體：HBF weights 比 HBM weights 高 32.7%。兩種 H³ 的完成時間幾乎一樣。這個 32.7% 排除 static/background power，不能解讀成整機耗電增加 32.7%，也不能把 HBM-only 和 H³ 當成相同容量。重點是：記憶體容量帶來的好處，不一定變成能耗下降。

## 13 — 提案：HBM/HBF-aware attention–expert placement

這是 Proposed / Not yet evaluated。同一資料中心內，HBM-rich attention worker 負責 attention 和 active KV；HBF-rich expert worker 負責 MoE expert，hot weights 在 HBM、cold weights 在 HBF。中間傳的是 activation / hidden state。Expert computation 在 GPU 上，HBF 只存資料。

可能的好處是讓容量和存取特性對上兩種工作負載。還要評估 HBF read energy、inter-GPU transfer、GPU waiting power 和 SLO。只有這些代價小於容量與放置的收益，這個分工才值得做。Janus、AFlex 和 MemExplorer 只放在來源；AFlex 是 attention/FFN，不是 MoE attention/expert。

## 14 — 研究計畫

上層 geo scheduler 用碳強度、PUE、queue / workload 和 WAN RTT，只做 request 或 session routing。選定資料中心之後，才做本地的 heterogeneous GPU、HBM/HBF placement 和 attention/expert workers。不是每一層 attention/expert 都走 WAN。

順序是：先建立 GPU 功率和 HBM/HBF 存取模型，再比較記憶體配置、hot/cold placement 和資料中心內的 A/E；最後才把本地成本放進跨資料中心路由，並分開評估 operational 與 allocated embodied carbon。指標是 serving energy、TTFT / TPOT、SLO goodput 和 total carbon。這是提案，上述論文沒有證明這個系統已經節能或減碳。

## 15 — Thank you

謝謝老師。想先確認本地 HBM/HBF placement 的能量與 SLO 代價，再決定如何接到跨資料中心的碳排排程。

## 16 — REEL LCI 補充

從第 6 頁的 About REEL / LCI 進來，講完返回第 6 頁。REEL 是 Repository of Electronics Environmental Line-items；LCI 是生命週期盤查，還不是碳足跡本身。Jonathan Balsvik 建立 v1.0，公開說明有 520 個資料集、18 個類別。完整 inventory 數量透過 Circa 授權。官網是 https://reellci.com/。

## 17 — HBM/HBF 參數來源

從第 10 頁的 Parameter Sources 進來，講完返回第 10 頁。讀寫能量、頻寬、啟動時間和耐久度分別來自 Micron、Lenovo、Ma and Patterson、Moon、MemExplorer、H³ 與 SSD proxy。6.8 pJ/bit 是沿用 MemExplorer 的 2 倍 HBM 假設，不是量到的 2 倍裝置功率。100 pJ/bit、8 GB/s、250 µs 和 100,000 P/E cycles 含 SSD 或假設，不是量產 HBF 實測。

## 可能的提問

### Q1. REEL 的數字可以當 HBF 量產碳排嗎？

不可以。它是可追查的前瞻模型。公開方法能檢查邊界和假設，但沒有量產驗證，完整 inventory 也還沒重算 GWP。

### Q2. 47.8% 是否代表 HBF 更省碳？

不代表。那是未轉換 GB/GiB 的名義容量指標，而且不含服務能耗、壽命和 SLO。容量變大不表示製造排放消失。

### Q3. 32.7% 是整機多耗的電嗎？

不是。分母是同一 H³ 8+8 配置、weights 放在 HBM 的 7.19 MJ。模型不含 static/background power。HBM-only 的 9.11 MJ 是另一種容量，不能和這個百分比混用。

### Q4. Attention/expert 分工是新貢獻嗎？

不是。Janus 已有 attention/expert 分離，AFlex 是 attention/FFN。我們要驗證的是 HBM/HBF 放置、傳輸和等待能量能不能覆蓋容量收益，以及之後如何接到跨資料中心路由。目前沒有自己的節能結果。
