# Research Materials 講稿

2026-11-18 會議後修訂，更新日期：2026-11-20（Asia/Taipei）。主簡報 1–13，補充 14–19，頁腳與 PDF 實際頁碼一致。本稿取代舊版 Attention/Expert、HBM/HBF 共同設計與排程架構的講法。英文投影片區分已發表證據、模型假設，以及尚未驗證的研究提案。

## 1 — Power- and Carbon-Aware LLM Serving on Heterogeneous GPUs

老師好，今天要報告的主題是異質 GPU 上的 power 與 carbon-aware LLM serving。實際的 serving 環境裡，GPU 的運算能力、記憶體容量、頻寬和功耗都不一樣，而不同 workload 對這些資源的需求也不同。所以我們想研究，怎麼依照 workload 特性在不同 GPU 之間做排程，並且在滿足延遲 SLO 的前提下，降低 serving energy 和 carbon。

## 2 — Contents

這份簡報分成四個部分。第一部分是 Carbon–SLO、GreenCache、Helix 和 ThunderServe 這幾篇相關研究，作為研究背景。第二部分整理不同 workload 的特性，以及已發表的 GPU 記憶體效能與能量證據。第三部分是從這些文獻歸納出的研究缺口和我們想探討的方向。最後介紹我們目前可以使用的實驗環境。每張卡片都可以直接點進去對應的頁面。

## 3 — Carbon–SLO: Shared State, Regional Decisions

Carbon–SLO 已經研究跨資料中心的請求路由，會考慮碳強度、queue、batch、KV 狀態與網路延遲。上層定期收集並廣播共同快照，各區域仍然獨立決策，所以同時選到同一個低碳站點時，可能出現壅塞。這篇主要計算 operational carbon，效能與功率模型校正在 A100 上。我們可以沿用它的路由與 SLO 思考方式，但需要重新建立不同工作負載、GPU 與記憶體配置的本地成本。異質 GPU 本身不是新貢獻。

## 4 — GreenCache: Carbon-Aware SSD Cache Sizing

GreenCache 的決策是 SSD KV cache 要配置多大。保留 cache 可以減少重複 prefill，卻也增加分攤到服務上的儲存設備 embodied carbon，因此它在碳強度、請求量與 SLO 限制下調整容量。這提醒我們，cache reuse 的好處要和保留、寫入及搬移資料的成本一起看。不過它不是跨資料中心排程，也沒有解決異質 GPU 與 HBM/HBF 的聯合配置。

## 5 — Helix: Heterogeneous GPU Placement

Helix 研究如何讓不同型號的 GPU 一起執行 LLM serving。圖左的 Coordinator 先透過 Profiler 收集 GPU 和網路資訊，再由 Planner 決定模型 layer 的位置；規劃使用 max-flow 與 MILP，但這張圖呈現的是系統架構，不是演算法內部。中間是異質 GPU workers，Scheduler 依照已部署的模型安排 request 路徑；右邊放大單一節點的 queue 和 layers。

作者有真實異質 cluster 實驗，跨區域設定則用 simulation。對我們的啟發是，GPU placement 和 scheduling 已有成熟方法，我們要進一步研究 workload 的能量需求與異質 GPU 的配置。

## 6 — ThunderServe: Workload-Aware Serving

ThunderServe 主要研究不同 Workload 下，如何有效分配異質 GPU 資源。

因為 Prefill 通常比較吃計算能力，而 Decode 比較受到記憶體頻寬限制，所以作者把兩個階段分開執行。

從這張圖可以看到，Coordinator 會把 Request 分配到不同的 Prefill Replicas，再透過 Routing 送到適合的 Decode Replicas。作者除了決定 Routing，也會一起考慮 GPU Grouping、Phase Assignment 和 Parallel Configuration。

比較有趣的是 Table 3，同樣使用 32 張異質 GPU，Coding 的配置是 8 個 Prefill 和 4 個 Decode Replicas，而 Conversation 則是 4 個 Prefill 和 8 個 Decode Replicas。

這說明不同 Workload 可能需要不同的資源配置。

## 7 — Different Workloads, Different Resource Requirements

這一頁想說明，不同 workload 對 GPU 資源的需求並不一樣。以 ThunderServe 評估的 workload 來看，Coding 的 prompt 比較長、輸出比較短，所以主要吃 prefill 的運算能力，也很在意 TTFT。Conversation 則相反，prompt 較短、輸出較長，比較需要 decode 的吞吐量和記憶體頻寬。Multi-turn 或 agentic 是一種互動模式，前後輪會重複使用 context，可能重用 prefix 和 KV，所以更看重記憶體容量，以及 KV 要保留多久。因此，不同 workload 需要不同的運算、記憶體和排程資源。

接下來先看已發表的記憶體證據，了解 GPU 記憶體特性如何影響服務效能與能量。

## 8 — HBM and HBF Memory Access Energy

這頁保留 Characterizing HBF 的 Table 1。HBF 的容量較大，但在這個模型中，讀取能量是 6.8 pJ/bit，HBM 是 3.4；HBF 寫入能量與啟動延遲也更高，寫入頻寬則低很多。因此不能直接從容量推論節能。這些參數混合了硬體規格、先前研究與 SSD proxy，不是 HBF 生產晶片的實測數據。右下角可以跳到第 19 頁逐項看來源。

## 9 — Workload Completion Time Comparison

這是原論文的 GLM-5.2 模擬，涉及 MoE，我保留它作為已發表的記憶體證據，沒有把它改成 Dense LLM 結果。三種配置的完成時間分別是 11,354、4,543 和 4,538 秒。從 HBM-only 到 H³ 看起來約縮短六成，但 H³ 增加了 HBF 容量，8+0 和 8+8 並不是相同記憶體硬體的比較。這只能說明此模擬中額外容量的價值，不能當成我們配置演算法的收益，也沒有因此證明延遲 SLO 一定滿足。

## 10 — Modeled Serving Energy Comparison

相同三種配置的 modeled energy 是 9.11、7.19 和 9.54 MJ。最重要的受控比較是後兩者：同樣 H³ 8+8，只改權重位置，從 HBM 放到 HBF 後，完成時間幾乎不變，但 modeled energy 增加 32.7%。這個百分比不是相對 HBM-only 算的。論文模型排除了 static/background power，所以也不能把這個值說成整機耗電增加。它支持的重點是資料位置會影響能量，不能預設 HBF 一定省電。

這些記憶體結果促使我們把異質 GPU 的記憶體特性納入服務效能與能量的建模。

## 11 — Research Gaps and Proposed Direction

這頁整理前面文獻留下的缺口，以及我們想探討的方向。先強調，這些都是研究假設，不是已經驗證的改進。

第一，Carbon–SLO 已經有全域的資料中心狀態，包括 Global Provisioner 和共同快照，但各區域的 scheduler 仍然獨立決定路由。所以我們想研究跨區域協調排程，看它在共享容量、workload 分配和 SLO 可行性上能不能帶來幫助。這裡不假設協調一定比獨立決策好，必須實際比較。

第二，GreenCache 有碳會計，除了 operational carbon，也把儲存設備分攤的 embodied carbon 放進快取決策，但它沒有跨資料中心的請求路由。我們想把這種 carbon-aware 的成本模型改用到異質 GPU serving 與地理排程。起步先以 operational carbon 為主要目標，等有可靠的 lifecycle 資料，再把 embodied carbon 當作後續或敏感度分析。

第三，Helix 和 ThunderServe 已經研究異質 GPU 的 placement 與 workload-aware 資源分配，主要是為了效能或成本。我們想把 power 也放進來，在運算、記憶體和能量特性不同的 GPU 之間排程。要補充的是，異質 GPU 上的碳或能量最佳化並不是沒有人做過，像 GreenLLM 這類工作就有探討，所以我們的差異與新穎性還要再和相關研究仔細比較。

合起來，研究問題是：workload-aware、協調式的異質 GPU 排程，能不能在滿足延遲 SLO 的前提下，降低 serving energy 和 operational carbon。這是研究假設，不是已經證明的結果。

## 12 — Experimental Environment: LLMServingSim 2.0 and Real GPU Profiling

最後介紹一下我們目前可以使用的實驗環境。

上面是 LLMServingSim 2.0，這是一個用來模擬 LLM Serving 的 Simulator。它支援 Heterogeneous GPU、不同 Memory Hierarchy，以及 Multi-Instance Serving、Batching、Scheduling 和 Request Routing 等功能，因此我們可以利用它來探索不同 GPU 配置下的 Serving Performance。

另外，我們也會使用中研院 RCITI 的真實 GPU Cluster 進行實驗，實際量測不同 LLM Workload 在 GPU 上的 Latency、Throughput 和 Power Consumption。

這樣就不會完全依賴 Simulator，而是可以透過真實 GPU 的量測結果建立 Profile，並驗證模擬的準確性。

## 13 — Thank You

以上是依照老師建議調整後的方向。想請老師幫忙確認，先以 Dense LLM 的 workload-aware GPU／記憶體能量模型作為第一階段，是否適合。後面保留 embodied carbon 和記憶體參數來源，方便需要時補充討論。

## 14 — HBM/HBF Embodied Carbon Evidence（補充）

REEL LCI 提供可追溯的半導體製造模型與公開方法，可以當作初步比較或敏感度分析的起點。HBF 仍是 prospective model，並沒有經過我們獨立重建或生產資料驗證。完整 inventory 也不是公開頁面就能全部取得。右上角的 About REEL 可以到第 18 頁看資料庫背景。

## 15 — Embodied Carbon per Memory Stack（補充）

這裡保留 REEL 公布的每 stack screening estimates：HBM3 兩種配置是 13.52 和 19.81 kg CO₂e，HBM3E 約 20.6，HBF 是 225.9。HBF 對第一個 HBM3 stack 約高 16.7 倍，但容量標示分別是 512 GiB 和 16 GB，所以不是 capacity-matched 比較，更不是 serving carbon 的直接排名。

## 16 — Embodied Carbon per Nominal Capacity Unit（補充）

這頁把已公布的 footprint 除以標示的容量數字，得到 0.845、0.825、0.572 和 0.441。47.8% 是這個 nominal index 的計算結果。因為 HBM 標示 GB、HBF 標示 GiB，還沒建立一致的實際單位，所以不能說是經過驗證的每 GiB 減碳幅度，也不能用它推論整個服務會減碳。

## 17 — HBF Carbon Estimate: Assumptions and Limitations（補充）

模型使用 16-Hi、512 GiB、232-layer NAND，以及 65 nm 和 28 nm process proxies，並把 175.6 平方毫米的 package outline 當作 die-area proxy。來源本身揭露了 die-area 和 bit-density 的不一致，也沒有包含完整 interposer、substrate 和 package assembly。這些限制讓它適合初步探索，但不適合當成已驗證的製造 footprint。

## 18 — REEL LCI: Database Background and Inventory Scope（補充）

REEL 是 Repository of Electronics Environmental Line-items，LCI 指生命週期 inventory，也就是衝擊評估之前的製造投入與產出。這頁保留先前核對過的 v1.0 背景：520 datasets、18 categories，以及 Jonathan Balsvik 的方法與公開資料來源。完整 inventory 透過 Circa 授權取得；公開頁面可以看說明，但不能因此說我們已經取得或重建全部資料。返回按鈕回到第 14 頁。

## 19 — Sources of the HBM/HBF Memory Parameters（補充）

這張表把參數分成硬體 specification、prior-work-derived model 和 author assumption。HBF 的讀取能量依原論文沿用 MemExplorer 的兩倍 HBM 假設；寫入能量、頻寬與延遲有 SSD proxy 的成分，100,000 次 P/E 也是假設的 endurance。兩倍 pJ/bit 不等於兩倍整顆 device power。返回按鈕回到第 8 頁。
