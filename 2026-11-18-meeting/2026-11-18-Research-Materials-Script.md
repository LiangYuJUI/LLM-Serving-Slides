# Research Materials 講稿

2026-11-18 會議後修訂，更新日期：2026-11-20（Asia/Taipei）。主簡報 1–16，補充 17–22，頁腳與 PDF 實際頁碼一致。本稿取代舊版 Attention/Expert 架構的講法。英文投影片區分已發表證據、模型假設，以及尚未驗證的研究提案。

## 1 — Research Overview

老師，依照上次的建議，我把研究主軸改成工作負載導向的 GPU 與 HBM/HBF 記憶體配置，不再以 MoE 的 Attention/Expert 分離作為提案。核心問題是：不同工作負載適合什麼 GPU、記憶體配置與資料位置，能不能在滿足延遲 SLO 的前提下降低 serving energy？先把這個本地成本量準，再研究它如何影響跨資料中心的碳感知排程。今天呈現的是研究規劃與文獻證據，還沒有我們自己的節能結果。

## 2 — Research Evidence Overview

簡報分成四部分。先看 Carbon–SLO、GreenCache、Helix 和 ThunderServe 已經提供的方法，再比較工作負載需求與 HBM/HBF 的效能、能量證據。接著說明我們的本地配置與跨資料中心架構，最後交代中研院實驗環境、LLMServingSim 2.0 和三階段評估計畫。Embodied carbon 的資料保留在最後的補充頁，主線先以 operational energy 和 carbon 為主。

## 3 — Carbon–SLO: Shared State, Regional Decisions

Carbon–SLO 已經研究跨資料中心的請求路由，會考慮碳強度、queue、batch、KV 狀態與網路延遲。上層定期收集並廣播共同快照，各區域仍然獨立決策，所以同時選到同一個低碳站點時，可能出現壅塞。這篇主要計算 operational carbon，效能與功率模型校正在 A100 上。我們可以沿用它的路由與 SLO 思考方式，但需要重新建立不同工作負載、GPU 與記憶體配置的本地成本。異質 GPU 本身不是新貢獻。

## 4 — GreenCache: Carbon-Aware SSD Cache Sizing

GreenCache 的決策是 SSD KV cache 要配置多大。保留 cache 可以減少重複 prefill，卻也增加分攤到服務上的儲存設備 embodied carbon，因此它在碳強度、請求量與 SLO 限制下調整容量。這提醒我們，cache reuse 的好處要和保留、寫入及搬移資料的成本一起看。不過它不是跨資料中心排程，也沒有解決異質 GPU 與 HBM/HBF 的聯合配置。

## 5 — Helix: Heterogeneous GPU Placement

Helix 研究如何讓不同型號的 GPU 一起執行 LLM serving。圖左的 Coordinator 先透過 Profiler 收集 GPU 和網路資訊，再由 Planner 決定模型 layer 的位置；規劃使用 max-flow 與 MILP，但這張圖呈現的是系統架構，不是演算法內部。中間是異質 GPU workers，Scheduler 依照已部署的模型安排 request 路徑；右邊放大單一節點的 queue 和 layers。

作者有真實異質 cluster 實驗，跨區域設定則用 simulation。對我們的啟發是，GPU placement 和 scheduling 已有成熟方法，我們要進一步研究 workload 的能量需求與 HBM/HBF 配置。

## 6 — ThunderServe: Workload-Aware Serving

ThunderServe 利用 prefill 通常偏重計算、decode 通常較受記憶體頻寬影響的差異，聯合決定 GPU grouping、phase assignment、parallelism 和 routing。Table 3 的 LLaMA-30B 例子很直接：Coding 是八個 prefill、四個 decode replicas；Conversation 則是四個 prefill、八個 decode。這是 replica 數量，不是 GPU 張數，兩個部署都使用論文的三十二張 cloud GPU 資源。這頁只比較部署比例，沒有把不同硬體 baseline 的 throughput 混在一起。

## 7 — Different LLM Workload Characteristics

這頁是新方向的重要出發點。ThunderServe 的 Coding 工作負載相對長輸入、短輸出，因此 prefill 需求較高；Conversation 相對短輸入、長輸出，因此需要較多持續 decode 的資源。多輪或 agentic 工作負載還多了一個維度：前一輪的 prefix 和 KV 可能繼續使用，session state 需要保留多久、值得用多少容量，都會改變成本。上半部是文獻觀察，下半部是我們要驗證的配置意涵。三類可以重疊，也不能把所有 coding 或 conversation 都固定成同一種長度分布。

TTFT 是第一個 token 出現前的時間，TPOT 是後續每個輸出 token 的時間。這些需求會影響 GPU 分配、記憶體頻寬、KV 保留與資料搬移，所以不能只依模型大小決定配置。

## 8 — Research Gaps and Required Models

前面的文獻分別提供了 geo routing、碳感知 cache、異質 GPU placement，以及 phase 和 workload-aware allocation。我們需要補的是可校正的工作負載功率與能量模型、HBM/HBF 的讀寫與延遲成本、權重和 KV 的資料位置，以及通訊與端到端 SLO 的影響。接著再問，這些本地成本會不會改變跨資料中心的選擇。這是具體要研究的整合問題，不是宣稱過去沒有任何人考慮過其中幾個因素；新穎性還要繼續比對相關系統。

## 9 — HBM and HBF Memory Access Energy

這頁保留 Characterizing HBF 的 Table 1。HBF 的容量較大，但在這個模型中，讀取能量是 6.8 pJ/bit，HBM 是 3.4；HBF 寫入能量與啟動延遲也更高，寫入頻寬則低很多。因此不能直接從容量推論節能。這些參數混合了硬體規格、先前研究與 SSD proxy，不是 HBF 生產晶片的實測數據。右下角可以跳到第 22 頁逐項看來源。

## 10 — Workload Completion Time Comparison

這是原論文的 GLM-5.2 模擬，涉及 MoE，我保留它作為已發表的記憶體證據，沒有把它改成 Dense LLM 結果。三種配置的完成時間分別是 11,354、4,543 和 4,538 秒。從 HBM-only 到 H³ 看起來約縮短六成，但 H³ 增加了 HBF 容量，8+0 和 8+8 並不是相同記憶體硬體的比較。這只能說明此模擬中額外容量的價值，不能當成我們配置演算法的收益，也沒有因此證明延遲 SLO 一定滿足。

## 11 — Modeled Serving Energy Comparison

相同三種配置的 modeled energy 是 9.11、7.19 和 9.54 MJ。最重要的受控比較是後兩者：同樣 H³ 8+8，只改權重位置，從 HBM 放到 HBF 後，完成時間幾乎不變，但 modeled energy 增加 32.7%。這個百分比不是相對 HBM-only 算的。論文模型排除了 static/background power，所以也不能把這個值說成整機耗電增加。它支持的重點是資料位置會影響能量，不能預設 HBF 一定省電。

## 12 — Proposed Workload-Aware GPU/Memory Placement

新的本地配置提案有三個部分。輸入是 workload 特徵、GPU 的效能與功率 profile、HBM/HBF 參數，以及延遲 SLO；決策則包括選哪種 GPU、配置多少資源、使用什麼記憶體組合，以及權重、active KV 和 reusable KV 放在哪裡。Prefill/decode phase placement 可以是候選決策，但只有在有利時才使用，也不是新提出的技術。

評估時一起看 latency、TTFT、TPOT、throughput、SLO goodput、能量和搬移成本。Goodput 指符合 SLO 的有效服務量。頻繁寫入、熱資料或低延遲資料，可能需要和冷的、以讀為主的資料不同的配置。這整頁都還是待驗證的提案。

## 13 — Proposed Serving and Scheduling Architecture

整體分成兩層。Global scheduler 決定 request 或 session 要送到哪個資料中心，輸入包含 CI、PUE、queue、workload、WAN RTT，以及本地預測的能量與 SLO 可行性。進入選定的資料中心後，local serving 再決定 GPU 資源、serving placement 和記憶體資料位置。

圖中的雙向箭頭表示路由往下、校正後的成本回傳上層，不是跨 WAN 執行每一層 Attention 或 Expert。Session 的 cache locality、搬移成本，以及狀態快照過期都需要在後續模型處理。主要先評估 operational energy/carbon，embodied carbon 等生命週期資料與分攤方式足夠可信之後再擴充。

## 14 — Experimental Environment and Simulator

實驗會以中研院資訊科技創新研究中心 RCITI 的 GPU cluster 作為真實量測環境。第一步是確認實際可用的 GPU 與存取條件，再跑代表性的 Dense LLM 工作負載，量測 latency、throughput、power 並積分得到 energy。現在沒有宣稱任何 GPU 型號、張數或功率結果，也沒有假設 cluster 有 HBF。

LLMServingSim 2.0 的官方文件已描述異質／分離式 serving、batching、scheduling、KV 模型、profiled compute 和 ASTRA-Sim 通訊。右下方的 HBF access、能量整合與跨資料中心碳排程，是我們需要開發或驗證的部分，不能當成現成能力。真實資料校正支援的 GPU 行為，再用 held-out 情境驗證；假想 HBF 則要另外做參數敏感度分析。

## 15 — Research Roadmap and Evaluation Plan

計畫分成三階段。先確認 RCITI 資源，建立 Dense LLM workloads、量測 GPU 效能與能量，校正 simulator 並報告 held-out error。第二階段比較 workload-aware placement，包含 GPU 異質性、HBM-only 與 HBM/HBF、權重和 KV 位置，以及讀寫和搬移成本。第三階段才把校正後的成本帶入跨資料中心路由，評估 operational carbon 與 SLO。

Baseline 要包含 homogeneous 對 heterogeneous、workload-unaware 對 aware、HBM-only 對 hybrid，以及簡單 SLO-aware 對 carbon-aware routing。每組都交代 GPU 數量、容量、precision、同一份 trace 和 SLO；如果多了硬體容量，要把容量收益和策略收益分開。順序是先把本地模型量準，再談配置，最後談跨站減碳。

## 16 — Thank You

以上是依照老師建議調整後的方向。想請老師幫忙確認，先以 Dense LLM 的 workload-aware GPU／記憶體能量模型作為第一階段，是否適合。後面保留 embodied carbon 和記憶體參數來源，方便需要時補充討論。

## 17 — HBM/HBF Embodied Carbon Evidence（補充）

REEL LCI 提供可追溯的半導體製造模型與公開方法，可以當作初步比較或敏感度分析的起點。HBF 仍是 prospective model，並沒有經過我們獨立重建或生產資料驗證。完整 inventory 也不是公開頁面就能全部取得。右上角的 About REEL 可以到第 21 頁看資料庫背景。

## 18 — Embodied Carbon per Memory Stack（補充）

這裡保留 REEL 公布的每 stack screening estimates：HBM3 兩種配置是 13.52 和 19.81 kg CO₂e，HBM3E 約 20.6，HBF 是 225.9。HBF 對第一個 HBM3 stack 約高 16.7 倍，但容量標示分別是 512 GiB 和 16 GB，所以不是 capacity-matched 比較，更不是 serving carbon 的直接排名。

## 19 — Embodied Carbon per Nominal Capacity Unit（補充）

這頁把已公布的 footprint 除以標示的容量數字，得到 0.845、0.825、0.572 和 0.441。47.8% 是這個 nominal index 的計算結果。因為 HBM 標示 GB、HBF 標示 GiB，還沒建立一致的實際單位，所以不能說是經過驗證的每 GiB 減碳幅度，也不能用它推論整個服務會減碳。

## 20 — HBF Carbon Estimate: Assumptions and Limitations（補充）

模型使用 16-Hi、512 GiB、232-layer NAND，以及 65 nm 和 28 nm process proxies，並把 175.6 平方毫米的 package outline 當作 die-area proxy。來源本身揭露了 die-area 和 bit-density 的不一致，也沒有包含完整 interposer、substrate 和 package assembly。這些限制讓它適合初步探索，但不適合當成已驗證的製造 footprint。

## 21 — REEL LCI: Database Background and Inventory Scope（補充）

REEL 是 Repository of Electronics Environmental Line-items，LCI 指生命週期 inventory，也就是衝擊評估之前的製造投入與產出。這頁保留先前核對過的 v1.0 背景：520 datasets、18 categories，以及 Jonathan Balsvik 的方法與公開資料來源。完整 inventory 透過 Circa 授權取得；公開頁面可以看說明，但不能因此說我們已經取得或重建全部資料。返回按鈕回到第 17 頁。

## 22 — Sources of the HBM/HBF Memory Parameters（補充）

這張表把參數分成硬體 specification、prior-work-derived model 和 author assumption。HBF 的讀取能量依原論文沿用 MemExplorer 的兩倍 HBM 假設；寫入能量、頻寬與延遲有 SSD proxy 的成分，100,000 次 P/E 也是假設的 endurance。兩倍 pJ/bit 不等於兩倍整顆 device power。返回按鈕回到第 9 頁。
