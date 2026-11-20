# Research Materials 講稿

2026-11-18 會議後修訂，更新日期：2026-11-20（Asia/Taipei）。主簡報 1–16，補充 17–22，頁腳與 PDF 實際頁碼一致。本稿取代舊版 Attention/Expert 架構的講法。英文投影片區分已發表證據、模型假設，以及尚未驗證的研究提案。

## 1 — Power- and Carbon-Aware LLM Serving on Heterogeneous GPUs

老師好，今天要報告的主題是異質 GPU 上的 power 與 carbon-aware LLM serving。實際的 serving 環境裡，GPU 的運算能力、記憶體容量、頻寬和功耗都不一樣，而不同 workload 對這些資源的需求也不同。所以我們想研究，怎麼依照 workload 特性在不同 GPU 之間做排程，並且在滿足延遲 SLO 的前提下，降低 serving energy 和 carbon。

## 2 — Research Evidence Overview

這份簡報分成四個部分。第一部分是 Carbon–SLO、GreenCache、Helix 和 ThunderServe 這幾篇相關研究，作為研究背景。第二部分整理不同 workload 的特性，以及 GPU 和記憶體的特性與已發表的效能、能量證據。第三部分是我們提出的 power 與 carbon-aware GPU 排程方向，最後說明實驗環境與評估規劃。每張卡片都可以直接點進去對應的頁面。

## 3 — Carbon–SLO: Shared State, Regional Decisions

Carbon–SLO 已經研究跨資料中心的請求路由，會考慮碳強度、queue、batch、KV 狀態與網路延遲。上層定期收集並廣播共同快照，各區域仍然獨立決策，所以同時選到同一個低碳站點時，可能出現壅塞。這篇主要計算 operational carbon，效能與功率模型校正在 A100 上。我們可以沿用它的路由與 SLO 思考方式，但需要重新建立不同工作負載、GPU 與記憶體配置的本地成本。異質 GPU 本身不是新貢獻。

## 4 — GreenCache: Carbon-Aware SSD Cache Sizing

GreenCache 的決策是 SSD KV cache 要配置多大。保留 cache 可以減少重複 prefill，卻也增加分攤到服務上的儲存設備 embodied carbon，因此它在碳強度、請求量與 SLO 限制下調整容量。這提醒我們，cache reuse 的好處要和保留、寫入及搬移資料的成本一起看。不過它不是跨資料中心排程，也沒有解決異質 GPU 與 HBM/HBF 的聯合配置。

## 5 — Helix: Heterogeneous GPU Placement

Helix 研究如何讓不同型號的 GPU 一起執行 LLM serving。圖左的 Coordinator 先透過 Profiler 收集 GPU 和網路資訊，再由 Planner 決定模型 layer 的位置；規劃使用 max-flow 與 MILP，但這張圖呈現的是系統架構，不是演算法內部。中間是異質 GPU workers，Scheduler 依照已部署的模型安排 request 路徑；右邊放大單一節點的 queue 和 layers。

作者有真實異質 cluster 實驗，跨區域設定則用 simulation。對我們的啟發是，GPU placement 和 scheduling 已有成熟方法，我們要進一步研究 workload 的能量需求與 HBM/HBF 配置。

## 6 — ThunderServe: Workload-Aware Serving

ThunderServe 主要研究不同 Workload 下，如何有效分配異質 GPU 資源。

因為 Prefill 通常比較吃計算能力，而 Decode 比較受到記憶體頻寬限制，所以作者把兩個階段分開執行。

從這張圖可以看到，Coordinator 會把 Request 分配到不同的 Prefill Replicas，再透過 Routing 送到適合的 Decode Replicas。作者除了決定 Routing，也會一起考慮 GPU Grouping、Phase Assignment 和 Parallel Configuration。

比較有趣的是 Table 3，同樣使用 32 張異質 GPU，Coding 的配置是 8 個 Prefill 和 4 個 Decode Replicas，而 Conversation 則是 4 個 Prefill 和 8 個 Decode Replicas。

這說明不同 Workload 可能需要不同的資源配置。

## 7 — Different Workloads, Different Resource Requirements

這一頁想說明，不同 workload 對 GPU 資源的需求並不一樣。以 ThunderServe 評估的 workload 來看，Coding 的 prompt 比較長、輸出比較短，所以主要吃 prefill 的運算能力，也很在意 TTFT。Conversation 則相反，prompt 較短、輸出較長，比較需要 decode 的吞吐量和記憶體頻寬。Multi-turn 或 agentic 是一種互動模式，前後輪會重複使用 context，可能重用 prefix 和 KV，所以更看重記憶體容量，以及 KV 要保留多久。因此，不同 workload 需要不同的運算、記憶體和排程資源。

## 8 — Research Direction: Power- and Carbon-Aware Heterogeneous GPU Scheduling

前面的文獻已經提供 geo-aware routing、caching、異質 GPU placement，以及 phase-aware 的資源分配。我們計畫分成三個部分。第一，針對不同 workload，量測異質 GPU 的效能與功耗，建立 performance 和 power model。第二，在這個基礎上研究異質 GPU 的排程，包含 GPU 配置、request 排程，以及在適合的情況下決定模型或 phase 的放置。第三，加入 serving energy、各地區的碳強度、queue 與網路延遲，檢查 TTFT 和 TPOT SLO 是否可行；跨資料中心路由則作為本地排程校正之後的延伸。目標是在滿足延遲 SLO 的同時，降低 serving energy 和 operational carbon。

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
