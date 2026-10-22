# Meeting Main 中文講稿

對應 `2026-10-27-Meeting-Main.tex` 與最終 38 頁 PDF。第 01–13 頁為正式報告，預算合計 **17.5 分鐘**；第 14–38 頁為 25 頁 Q&A backup，不計入報告時間。頁腳 `Main n/13` 與 `Backup PDF n` 均對應 PDF 實際頁碼。封面標題以 `Title` 作講稿索引。

時間包含看圖與轉場，是排練目標而非實測語速；若需壓到 15 分鐘，略過部分數字口述，保留問題、觀察與 caveat。所有 Helix／Tessera 事實只依本地原始 PDF。來源頁碼均指 PDF page index（從 1 起算），不是會議論文印刷頁碼。

## 第 01 頁｜Title

預計時間：0.3 分鐘。

今天我想用 Helix 和 Tessera 回答一個共同問題：面對不同能力的 GPU，系統應該以什麼單位安排工作？我會先說每篇的核心主張，再看作者如何用實驗建立這個主張，最後把它們放回我們的 heterogeneous serving project。

來源：兩篇本地 PDF 首頁；本頁標題為報告者整理。

## 第 02 頁｜Put the Two Papers on One Map

預計時間：0.8 分鐘。

先用這張表定位兩篇。Helix 面對的是不同 GPU 能力加上不同網路連線，決定 model layers 放在哪裡，以及 request 沿哪條 pipeline 執行。Tessera 則觀察，同一模型裡不同 kernel 偏好的 GPU 可能不同，所以決定每個 kernel 的執行位置。

兩篇都先做較昂貴的離線規劃，但 runtime 的決策不一樣：Helix 是替新 request 選路；Tessera 是執行既有 kernel policy，並依負載切換 policy。表裡 MILP 是混合整數線性規劃，DDG 是資料相依圖，後面只講它們在系統中負責什麼。

今天不把這兩篇排成誰比誰更細就更好。它們選擇的最佳化維度不同，我們真正要比較的是：每個切分單位看見了什麼瓶頸，又付出了什麼代價。

來源：Helix Sec. 4–5，PDF pp. 5–8；Tessera Sec. III，PDF pp. 4–7。比較表為自己的整理。

## 第 03 頁｜Helix: What Problem Is It Solving?

預計時間：1.4 分鐘。

Helix 一句話的重點，是一起規劃 layer placement 和 request routing。作者的起點是，雲端能取得的 GPU 不一定同型號，compute 和 memory capacity 都不同，還可能分散在不同 region。

這裡先區分兩個詞：heterogeneous 指硬體能力不同；geo-distributed 指地理位置不同，進一步帶來頻寬、延遲和拓樸差異。異質 GPU 可以在同一機房，兩者不是同義詞。

一個直覺是依 FLOPS 分配工作。FLOPS 是 Floating Point Operations Per Second，表示理論浮點運算吞吐能力；算力越強的 GPU，就分到較多模型工作。但 Figure 1 要指出，這只是 compute-proportional 的直覺。從左至右看，均勻分層會讓慢 GPU 限制整條 pipeline；即使改成算力平衡，若每個 activation 還是要跨越慢連線，瓶頸只是從 GPU 轉移到 network。

所以作者提出的問題不是如何把 layer 平均切好，而是如何讓整個系統真正送出最多 token。圖中的 network-aware 配置分散慢連線上的工作，說明 placement 和 routing 必須放在同一個資源模型裡考慮。

來源：Helix Sec. 1、4.2，Figure 1，PDF pp. 1–2、4–5。Figure 1 是動機示例，不是大型實驗測量。

## 第 04 頁｜Helix: How Does It Work?

預計時間：1.7 分鐘。

方法的輸入，是模型、GPU compute／memory profile，以及網路連線的 profile。第一階段在 serving 之前規劃：MILP 選擇每個節點存哪些連續 layers，並透過 flow formulation 評估這個 placement 的可行吞吐量。

為什麼可以用 max-flow？先把 placement 固定。每個 GPU 的處理能力和每條連線的傳輸能力都換成 tokens per second，變成 graph 上的 edge capacity。從 source 到 sink 能維持多少 flow，就近似代表這個配置能持續處理多少 token。這是一個資源容量模型，不會直接預測單筆 request 的 latency。

右側六步是概念上的資料流，不是說 MILP 完全不看 graph、等選完才考慮網路。MILP 本身就是利用 flow 約束搜尋 placement；固定配置後的 max-flow 則提供 runtime 可遵循的流量權重。

線上收到 request，scheduler 根據這些權重選一條完整 pipeline，後續 decode tokens 沿用相同 pipeline。因此不是每來一筆 request 都重算 MILP。這頁的 offline／online 指最佳化發生的時間；下一頁會用相同詞描述 workload，那是另一個分類。

來源：Helix Sec. 4.3–4.4、5.1，Figure 3，PDF pp. 5–8。Max-flow 是 throughput model，不是 latency model。

## 第 05 頁｜Q1: Does Helix Improve End-to-End Serving on Real Hardware?

預計時間：1.4 分鐘。

1. **Question**：前面的數學模型看起來合理，但真正做成 server 後，是否仍有 end-to-end 的收益？

2. **Setup**：作者使用含 4 A100、8 L4、12 T4 節點的單一異質 cluster，測 LLaMA 30B 和 70B。這裡有真實 prototype，不只有 simulator。

3. **What is controlled / compared**：在相同 cluster 和模型下，對比 Helix、separate pipelines，也就是 SP，以及實作在同一系統內的 Swarm 方法。圖也放入 simulator 結果驗證模擬器。

4. **Metric**：這裡的 offline/online 是 workload 定義，不是前面 planner 的 offline/online。Offline 持續供給 requests，讓系統接近滿載，觀察 decode tokens/s，越高越好。Online 按 Azure trace 的 arrival shape 送入，除吞吐量外，也看 prompt 和 decode latency，越低越好。上排是 throughput，下排是 online latency。

5. **Observation**：相對 Swarm，30B 的 offline／online throughput 是 2.14／2.07 倍；70B 是 1.94／2.00 倍，所以主頁用約兩倍概括。

6. **What this experiment proves**：Helix 的容量規劃確實能轉成真實硬體上的吞吐收益。

7. **Caveat**：不能推成 latency 全面更低。例如 70B 對 Swarm 的 decode latency 反而高 16%；對 SP 也有利用較慢 GPU 後平均 latency 較高的情況。

來源：Helix Sec. 6.1–6.3，Figure 6，PDF pp. 8–11。倍率順序為 offline、online。

## 第 06 頁｜Q2: Does Network-Aware Placement Matter under Slow Inter-Cluster Links?

預計時間：1.4 分鐘。

1. **Question**：如果跨 cluster 的 network 很慢，Helix 把 network 納入 placement 和 routing 是否真的有價值？

2. **Setup**：作者把同一組 GPUs 分成三個 cluster，在 simulator 中設定跨 cluster 約 100 Mb/s、平均約 50 ms latency。這頁是模擬結果，不是真實跨區 prototype。

3. **What is controlled / compared**：比較同一環境下的 Helix、SP、Swarm，測 30B 和 70B 的 offline／online workload。這是整個系統的比較，還沒有單獨隔離 placement 的效果。

4. **Metric**：左邊看 decode tokens/s，右邊看 online prompt／decode latency。吞吐量越高越好，延遲越低越好。

5. **Observation**：聚焦 30B 對 Swarm，兩種 workload 的吞吐收益約 2.3 到 2.4 倍。66% prompt 和 24% decode latency 降幅，專指這裡的 30B online 比較。它們不能搬回上一頁當 prototype 的成果。

6. **What this experiment proves**：當慢連線成為實際瓶頸，聯合考慮 placement 與 routing 的設計有明顯價值，支持一開始的 motivation。

7. **Caveat**：這不是單獨切換 network-awareness 的 ablation，而且依賴 simulator 的網路模型。接下來要固定其中一個元件，才能更清楚區分收益來源。

來源：Helix Sec. 6.2、6.4，Figure 7，PDF pp. 8、10–11。原文給 2.41×、2.33×；主稿不強行指派每個倍率的 workload 順序。

## 第 07 頁｜Q3: Where Do the Gains Come From: Placement or Scheduling?

預計時間：1.5 分鐘。

1. **Question**：Helix 的效果是 placement 比較好，還是 scheduler 比較好？作者用兩組控制變因實驗回答。

2. **Setup**：兩組都用 LLaMA 70B 的 offline serving，涵蓋 single cluster 和 geo-distributed setting，後者使用 simulator。

3. **What is controlled / compared**：左邊固定所有方法都使用 Helix scheduler，只換 Helix、Petals 或 Swarm placement。右邊反過來固定 Helix placement，換 Swarm、random 等 scheduler。這樣才能隔離各元件在固定搭配下的貢獻。

4. **Metric**：兩張圖的 bar 都是 decode throughput，單位 tokens/s，越高越好；旁邊的拓樸圖用來解釋資源未充分使用或網路壅塞的位置。

5. **Observation**：Placement 左邊，對 Petals／Swarm，單一 cluster 為 1.23／2.10 倍，geo 為 1.49／2.38 倍。Scheduling 右邊，對 Swarm／random，single 提升 30%／29%，geo 提升 22%／15%。不用記所有數字，重要的是固定另一元件後，差距仍存在。

6. **What this experiment proves**：兩部分都有獨立貢獻。較好的 placement 建立較好的資源圖；scheduler 則把流量送到可承受的路徑。這也是 Helix 最後能成立的結論。

7. **Caveat**：不能把左右倍率相乘當總收益。Petals 在左邊只提供 placement，也不是完整 end-to-end server 的比較。

來源：Helix Sec. 6.6–6.7，Figures 9–10，PDF pp. 11–12。Geo 對 shortest queue 的額外比較是 +19%，未納入主頁範圍。

## 第 08 頁｜Tessera: Why Is Phase-Level Disaggregation Too Coarse?

預計時間：1.5 分鐘。

接下來 Tessera 問的是另一個問題：如果同一段模型工作裡面，不同 kernel 偏好的 GPU 就不一樣，把整個 phase 當單位會不會太粗？Kernel 是一次 GPU 上執行的運算工作，例如某個矩陣運算或 attention kernel；它不等於一整層。

作者先做 profiling。圖的縱軸是 L40s 執行時間除以 A100 執行時間，低於一表示 L40s 較快，高於一表示 A100 較快；橫軸是 FLOP/Byte，描述運算相對資料搬移的強度。左右分別按 prefill／decode、attention／FFN 標示 kernel。

以 GPT-oss 20B 為例，約 45% prefill kernels 和 57% decode kernels 在 L40s 比 A100 快。注意這是 kernel 數量占比，不是總執行時間占比，也不是直接代表能加速這麼多。即使在 attention 或 FFN 內，點也落在分界線兩側。

這個 evidence 推出的問題是：phase 或 block 的名稱，並不能唯一決定最佳 GPU。因此 Tessera 改以 kernel 為單位做規劃。不過，單顆 kernel 跑得比較快還不代表整個 request 比較快，因為切分後要搬資料。後面的方法和實驗都要回答這個代價。

來源：Tessera Sec. II-C，Figure 3，PDF pp. 3–4。該圖的模型為 GPT-oss 20B，硬體比較為 A100 與 L40s。

## 第 09 頁｜Tessera: How Does It Work?

預計時間：1.7 分鐘。

Tessera 的輸入是 kernel execution pattern、資料相依關係、各 GPU 的 kernel latency，還有 GPU 間的傳輸成本。這頁把系統濃縮成四個步驟。

首先 analyzer 找出 kernel 讀寫的 memory ranges，建立 RAW，也就是 Read After Write 的相依關係：如果 B 要讀 A 寫出的結果，B 必須等資料可用。接著 profiling 量每個 kernel 在不同 GPU 上的時間。Planner 把這些資訊組成 DDG，交給 MILP 決定 kernel-to-GPU mapping，並保留需要的傳輸。

它會預先算兩類 policy。Throughput-oriented policy 適合很多 requests 可以 overlap 的情境，目標是把 compute 和 communication 的 stage time 平衡，避免最慢 GPU 限制 throughput。Latency-oriented policy 適合低 load；沒有其他 requests 可以隱藏 transfer 時，就把單筆 request 的 compute 與跨 GPU transfer 成本一起壓低。我們用縮短 critical path 來解釋它的目的；論文實際公式是加總 kernel 和 cut-edge communication cost，不是一般 DAG 最長路徑求解器。

最後 runtime workers 只執行分到的 kernels 與傳輸，monitor 依 queueing pressure 選擇預先存好的 policy。因此昂貴的 analysis 和 MILP 在離線，線上不是重新解 MILP。真正的挑戰是，這種細分是否抵得過新增的通信和協調。

來源：Tessera Sec. III-A–D，Figure 4，PDF pp. 4–7。Throughput 與 latency policy 都由 offline planner 求解。

## 第 10 頁｜Q1: Does Kernel-Level Disaggregation Outperform Phase/Block-Level Methods?

預計時間：1.4 分鐘。

1. **Question**：前面看到 kernel preference 不一致，現在要驗證，更細的切分是否真的提高 end-to-end throughput？

2. **Setup**：五個 workloads、三組異質 GPU pair：A100＋L40s、H100＋RTX Pro 6000、B200＋H100，涵蓋 LLM、SSM、多模態和 diffusion。

3. **What is controlled / compared**：同一 workload、同一 GPU pair 下，比較 Tessera 與 prefill/decode disaggregation，也就是 PD，以及 attention/FFN disaggregation，也就是 AF；圖中也列 homogeneous 執行作參考。

4. **Metric**：每組橫軸是不同模型。LLM、SSM 和多模態用 output tokens/s；diffusion 用右軸 images/min。各自越高越好，兩種單位不能直接混加。

5. **Observation**：論文跨測試配置報告，對 PD 平均 1.5 倍、最高 2.3 倍；對 AF 平均 1.35 倍、最高 1.7 倍。

6. **What this experiment proves**：Kernel preference 的動機可以轉成完整系統的 throughput 收益，而不只是 microbenchmark 上某個 kernel 較快。

7. **Caveat**：這是 saturated offline workload。紅色 X 表示 baseline 不適用，不是 throughput 為零；不同 baseline 適用的模型範圍不同。原文未把最大倍率明確對到單一 bar，我們也不自行指定。

來源：Tessera Sec. V-A–B，Figure 6，PDF pp. 7–8。五個模型：Llama-3 8B、GPT-oss 20B、Qwen2.5-VL 7B、Mamba-Codestral 7B、Stable Diffusion 3.5。

## 第 11 頁｜Q2: Can Tessera Sustain More Requests under the Same Latency SLO?

預計時間：1.4 分鐘。

1. **Question**：如果 request 隨時間到達，而且要求相同 latency SLO，Tessera 能否承受更多流量？

2. **Setup**：這裡只測 GPT-oss 20B，三組 GPU pair，request 按 Poisson process 到達，SLO 設為 50 ms/token。

3. **What is controlled / compared**：在同一 GPU pair 上逐步提高 arrival rate，對比 Tessera、PD、AF 以及 homogeneous 參考線。

4. **Metric**：橫軸是 requests/s，縱軸是 end-to-end request latency 除以 output token 數，也就是 normalized latency。它不是單一 decode token 的間隔，也不是直接量測 P99。曲線越低越好，跨過 SLO 前能到達的 request rate 越高越好。

5. **Observation**：低負載時，相對 PD／AF，normalized latency 約低到原本的 1/1.3、1/1.2。固定同一條 50 ms/token SLO，Tessera 最多承受最佳 baseline 約 1.3 倍的 arrival rate。

6. **What this experiment proves**：收益不只存在於滿載 throughput；低 load 的 latency policy 和負載上升時的 policy 選擇，也能支援 online serving。

7. **Caveat**：這是整個系統的線上結果，不能只靠這張圖把收益全部歸因於 monitor。也不能把這個單一 LLM 的 online 結果外推到所有模型家族。

來源：Tessera Sec. V-B，Figure 7，PDF p. 9。1.3× SLO request-rate 比較對象為 best baseline。

## 第 12 頁｜Q3: Does Communication Overhead Cancel the Benefit of Kernel Splitting?

預計時間：1.2 分鐘。

1. **Question**：Kernel splitting 增加跨 GPU 傳輸，這個 overhead 會不會把前面的收益吃掉？

2. **Setup**：GPT-oss 20B 的 offline workload，檢查 runtime pipeline 的效果。

3. **What is controlled / compared**：同一系統切換 no pipeline、pipeline、pipeline 加 priority 三種執行配置，另以零 communication overhead 作參考。

4. **Metric**：左邊看 throughput，單位 tokens/s，越高越好；右邊是 bottleneck GPU 的 compute／communication 時間分解。

5. **Observation**：吞吐量從 1443 提升到 2123，再到 2641；零通信參考是 2734，所以最後約達 96.6%。Priority 指後到的 requests 使用較低 CUDA stream priority，讓 requests 的傳輸時段錯開，不是單純把所有 transfer 都設成高優先權。

6. **What this experiment proves**：Kernel placement 本身還不夠，需要 runtime overlap 才能接近它的潛力。這是 Tessera 論證最後要補上的機制證據。

7. **Caveat**：零通信只是參考條件，不能說成本已經消失。Figure 9 與這段正文沒有明確命名 GPU pair，因此不由相似數字反推硬體。

來源：Tessera Sec. III-C、V-D，Figure 9，PDF pp. 6、9–10。96.6% = 2641/2734，屬直接計算。

## 第 13 頁｜What Do Helix and Tessera Teach Us about Heterogeneous Serving?

預計時間：1.8 分鐘。

最後回到我們的 project。ThunderServe 選擇 GPU groups 與 prefill／decode roles；Helix 決定 layers 的位置與 request pipeline；Hetis 分配 attention heads 以及相關 KV state；Tessera 把決策單位放到 GPU kernels。這不是一條可以直接排名的粗到細路線，因為它們切分的維度不同。

Helix 的研究論證是：compute balance 看不到慢網路，因此需要聯合 placement 和 routing；prototype 和慢連線模擬提供 end-to-end 證據，再用 ablation 證明兩個元件各自有作用。它的結論偏向吞吐量，沒有保證所有 latency 都更低。

Tessera 的論證是：phase 和 block 裡仍有不同硬體偏好的 kernel，因此 kernel granularity 有機會提高效率；offline throughput 和 online SLO 的實驗證明整體收益，最後用 pipeline ablation 說明通信開銷必須由 runtime 機制處理。

我的整理是，粒度變細可能看見更多硬體機會，但也增加 dependency tracking、communication、optimization complexity 和 runtime coordination。所以接下來的研究問題不是無限制地往更細切，而是：在什麼硬體與負載條件下，新增收益還能大於通信及協調成本？這可作為之後討論 GPU、HBM、HBF 或 architecture co-design 的問題，但今天兩篇並沒有證明任何 HBF 結論。正式報告到這裡結束，後面只用於追問。

來源：Helix Sec. 4–6、Tessera Sec. III、V；ThunderServe／Hetis 的定位依 2026-10-21 完整 reference decks。比較與最後問題是報告者統整，並非四篇在共同環境下的 performance ranking。


---

以下為 Appendix / Q&A。按追問選頁，不連續口述，不計入 17.5 分鐘。

## 第 14 頁｜Max-Flow Graph Abstraction

用途：Q&A backup；沿用 Helix reference deck 第 10 頁素材，講稿為本次重寫。

如果追問 graph 如何建立，先把 placement 視為已知。每個 compute node 拆成 in／out 兩點，中間 edge 表示節點容量；coordinator 對應 source 和 sink。合法 layer 接續才建立跨節點 edge。圖上的數值都是 tokens/s，整張圖是在核算同一配置的資源容量，不是畫 request 的實際時間軸。

來源：Helix Sec. 4.3，Figure 2，PDF pp. 4–5。

## 第 15 頁｜Modeling Compute Capacity

用途：Q&A backup；沿用 Helix reference deck 第 11 頁素材，講稿為本次重寫。

Compute capacity 來自 profiling，不直接採用 datasheet FLOPS。節點的內部 edge 取 compute 與節點 network throughput 的較小值，避免節點本身的進出頻寬被忽略。MILP 中的 T_j 表示這個節點存 j 個 layers 時可維持的 token rate；它是已量測的常數，layer count 改變就選到不同的 rate。

來源：Helix Sec. 4.3–4.4，PDF pp. 5–6。

## 第 16 頁｜Modeling Network Capacity

用途：Q&A backup；沿用 Helix reference deck 第 12 頁素材，講稿為本次重寫。

Network capacity 把 bandwidth 除以每個 token 對應的 payload bytes，單位才會變成 tokens/s。Coordinator 到第一層、最後一層回 coordinator 傳的是 token；中間 layers 傳的是 activation，通常大得多。Figure 2 標示 4 bytes 與 16 KB，只是該例子的值。這也說明即使 nominal bandwidth 一樣，傳 activation 的 edge 能承受的 token rate 仍低得多。

來源：Helix Sec. 4.3、Figure 2，PDF pp. 4–5。

## 第 17 頁｜Why Max Flow Represents Serving Throughput

用途：Q&A backup；沿用 Helix reference deck 第 13 頁素材，講稿為本次重寫。

Max-flow 能代表吞吐量，是因為每一單位 flow 都要依序消耗 compute 和 network capacity，並滿足中間節點的 flow conservation。它回答 steady-state 每秒能通過多少 token；沒有處理 arrival burst、queueing 分布或每個 token 的完成時間。因此用它最佳化 throughput 是合理建模，但不能直接推出 latency 最佳。Early-stop 的 compute bound 也只提供容量上界。

來源：Helix Sec. 4.3、4.5，PDF pp. 5、7。

## 第 18 頁｜MILP Variables and Objective

用途：Q&A backup；沿用 Helix reference deck 第 15 頁素材，講稿為本次重寫。

這頁把決策與目標分開看。s_i 決定起始 layer，b_ij 選擇 layer 數量，f 是 token flow，d 表示 link 是否可以使用。Placement 的結果決定 graph 的可行路徑，flow 的總量就是 objective。這不是在固定 placement 上只做 routing；placement 本身也在 MILP 的搜尋空間裡。此處符號為方便口述整理。

來源：Helix Sec. 4.4，Tables 5–6，PDF pp. 5–6。

## 第 19 頁｜Placement and Memory Constraints

用途：Q&A backup；沿用 Helix reference deck 第 16 頁素材，講稿為本次重寫。

Placement constraint 先保證 layer range 在模型範圍內，並且只選一個可容納的 layer count。Memory 的限制透過最多可放幾層 k 表示，沒有另外一個精細 KV-byte 決策變數。Partial inference 允許下一個節點雖然存了一段重疊 layer，卻只執行尚未完成的後段；如果禁用，就要求邊界剛好相接。KV 的即時餘裕交給 scheduler 處理。

來源：Helix Sec. 4.4、5.1，PDF pp. 6–8。

## 第 20 頁｜Flow and Compute Constraints

用途：Q&A backup；沿用 Helix reference deck 第 17 頁素材，講稿為本次重寫。

第一條式子是流量守恆，進入節點多少 token flow，就必須送出去多少。第二條把 incoming flow 限在該 layer count 的 profile 之內。b_ij 只會選中一個 throughput 常數，因此它把 placement 和可承受 flow 綁在一起。這些仍不是完整網路條件，還要配合下一頁的 link validity 與傳輸容量。

來源：Helix Sec. 4.4，Constraints 2–3，PDF p. 6。

## 第 21 頁｜Connectivity and Network Constraints

用途：Q&A backup；沿用 Helix reference deck 第 18 頁素材，講稿為本次重寫。

Connectivity constraint 先檢查語意是否合法：只有持有第一層的節點可以接 source，持有最後一層的才可以接 sink；中間 hop 必須接得上尚未完成的 layers。接著 f_ij 不能超過 d_ij 乘上 S_ij。如果 d 是零，該 edge 完全不能有流量。這裡的二元 auxiliary variables 只是把條件轉成線性形式，不是額外的 runtime decision。

來源：Helix Sec. 4.4，Constraints 4–5，PDF p. 6。

## 第 22 頁｜Converting Max-Flow Weights into Scheduling

用途：Q&A backup；沿用 Helix reference deck 第 22 頁素材，講稿為本次重寫。

IWRR 是 Interleaved Weighted Round-Robin。對每個頂點，鄰居的權重來自 max-flow 解中的 outgoing flow。Scheduler 從 source 開始，沿各頂點的選擇建立一條完整 pipeline；交錯選擇避免一次把高權重路徑集中塞滿。事先也會遮罩 KV cache 超過 high-water mark 的節點。這是把規劃好的 rate 轉成 request 派送的方法。

來源：Helix Sec. 5.1，PDF pp. 7–8。

## 第 23 頁｜Pipeline Scheduling Example

用途：Q&A backup；沿用 Helix reference deck 第 23 頁素材，講稿為本次重寫。

Figure 4 的兩個示例 pipeline 是 1→5→9 和 2→6→8。Edge 上的數字是 max-flow solution 的 flow，不是 physical link bandwidth，也不是 request 數量。這些路徑共用同一個 cluster，並不要求先切成互斥的固定 replica。選好後同一 request 的後續 tokens 重用它，這樣 KV state 可以留在相同路徑。

來源：Helix Sec. 5.1，Figure 4，PDF pp. 7–8。

## 第 24 頁｜High GPU-Heterogeneity Results

用途：Q&A backup；沿用 Helix reference deck 第 30 頁素材，講稿為本次重寫。

Question：GPU 類型更多時能否延續效果？Setup 是 42 nodes、7 種節點類型的 simulator，模型為 LLaMA 70B。比較 Swarm、SP、SP+；SP+ 額外用 mixed pipeline 納入無法獨立成 pipeline 的 GPU。Metric 是 decode tokens/s 與 online latency。Helix offline 對三者分別 1.37／2.91／2.24 倍，online 為 1.48／3.29／2.54 倍。這支持它能運用更多異質資源；但 3.29 倍是對 SP 的 online 模擬吞吐量，不是真實硬體結果，而且 decode latency 仍略高。

來源：Helix Sec. 6.5，Figure 8，PDF pp. 10–11。

## 第 25 頁｜MILP Optimization Ablation

用途：Q&A backup；沿用 Helix reference deck 第 33 頁素材，講稿為本次重寫。

Question：Pruning 和 warm start 是否讓有限求解時間更有效？Setup 是 offline LLaMA 70B，24-node geo 與 42-node 高異質環境。分別開關 pruning、改變初始化，觀察問題大小、decode throughput 與 solver time。Pruning 移除 50%／72% links，變數與約束規模約降 36%／46%，求得吞吐量提高 16%／2%；warm start 找到相同 placement，耗時少 43%／8%。它支持工程求解策略的價值，但不能證明被刪掉的 link 在全域最佳解裡一定沒用。

來源：Helix Sec. 6.8，Figure 11、Table 8，PDF p. 12。

## 第 26 頁｜Solver Time and Solution Quality

用途：Q&A backup；沿用 Helix reference deck 第 34 頁素材，講稿為本次重寫。

Question：找到好解與證明最佳，需要同樣久嗎？Setup 是較小的 4 L4＋6 T4 cluster、LLaMA 30B。圖比較 feasible solution 和 solver bound 隨時間的變化，縱軸是 throughput，橫軸是求解秒數。不到五分鐘已找到最佳 placement，但收緊 bound、證明 optimality 要超過一小時。這支持 early stop 的實務動機；不能把這個小例子的最佳性證明套到 42-node 配置。

來源：Helix Sec. 6.9，Figure 12，PDF p. 13。

## 第 27 頁｜PTX Instrumentation and Address Ranges

用途：Q&A backup；沿用 Tessera reference deck 第 12 頁素材，講稿為本次重寫。

如果問 opaque kernel 怎麼知道讀寫範圍，Tessera 在離線分析時修改 PTX。PTX 是 NVIDIA GPU 的中介指令表示；它在 global load／store 附近加入 atomic min／max，收集各 instruction 觸及的地址區間，再對齊 buffer base address。Standard library kernels 則可從 API 參數取得 buffer 資訊。這是在辨識資料範圍，不是在重建完整運算語意；若 kernel 存取未出現在參數中的 global、無法找出 base address，就拒絕拆分該 kernel。

來源：Tessera Sec. III-A、IV，Listing 1，PDF pp. 4–5、7。

## 第 28 頁｜Extracting RAW Dependencies

用途：Q&A backup；沿用 Tessera reference deck 第 13 頁素材，講稿為本次重寫。

RAW edge 來自 buffer 最後一次寫入者與後續 reader。Analyzer 按原 execution order 掃描，維護 registry，reader 讀到別的 kernel 寫出的 buffer 時就建立 edge，並附上需要搬移的 byte 數。Async copy 也當成 graph node。論文保留原本執行順序，因此只針對真資料相依建立這些跨 GPU 傳輸關係；不代表任意重排後也能忽略 WAR／WAW。不同 captured CUDA Graph 各自建立 DDG，並非每個 request 現場重新分析。

來源：Tessera Sec. III-A，PDF pp. 4–5。

## 第 29 頁｜Cross-Iteration Dependencies and KV State

用途：Q&A backup；沿用 Tessera reference deck 第 14 頁素材，講稿為本次重寫。

一般 DDG 先描述 iteration 內部，KV cache 卻可能這輪寫、下一輪讀。Analyzer 透過多輪 profiling 標出這類 buffer；runtime 在各 GPU 保留 replica，非同步傳 delta。兩個 NCCL communicators 區分背景 state update 和 latency-critical dependency traffic，後者優先。這個 priority 與主報告 Figure 9 的 request stream priority 是不同機制。投影片的低於 0.1% 引用前人工作，不能當成 Tessera 自己的新測量。

來源：Tessera Sec. III-A、IV，PDF pp. 5、7；0.1% 引用原文 [9]、[10]。

## 第 30 頁｜Offline Throughput-Oriented MILP

用途：Q&A backup；沿用 Tessera reference deck 第 16 頁素材，講稿為本次重寫。

每個 kernel 只放到一個 GPU。T_g 累加該 GPU 上的 kernel time，M_g 是跨 GPU incoming transfer time。大量 requests 可 overlap 時，stage cost 取兩者較大值，再最小化最慢 stage。這是 throughput-oriented policy 的核心假設。原文在 GPT-oss 20B、A100＋L40s、約 500 kernels 的例子，報告單 graph 約 20 ms、所有 patterns 約 5 秒；它與後面 solver scaling sweep 的數字是不同實例，不應混成通用保證。

來源：Tessera Sec. III-B，Table II，PDF pp. 5–6。

## 第 31 頁｜Communication and Load-Balancing Constraints

用途：Q&A backup；沿用 Tessera reference deck 第 17 頁素材，講稿為本次重寫。

跨 GPU edge 的成本是 base latency 加 bytes/bandwidth；只有 producer 和 consumer 分到不同 GPU 時才計入。二元乘積用標準 linearization 處理。Load balancing 來自最小化最慢 stage，不是另一條 variance constraint。值得追問的限制是，這個 MILP 沒有逐 GPU memory capacity constraint，初始化先在每個 GPU 複製完整 weights；offline policy 固定後可以回收不用的 buffers，但不能據此宣稱已量到相應容量收益。

來源：Tessera Sec. III-B、IV，PDF pp. 5、7。

## 第 32 頁｜Online Latency-Oriented Scheduling

用途：Q&A backup；沿用 Tessera reference deck 第 18 頁素材，講稿為本次重寫。

Low load 沒有其他 requests 幫忙隱藏 transfer，所以 objective 改成 kernel time 和 cut-edge communication cost 的加總。這是論文的低負載近似，目的在降低單筆 request 的完成時間，而不是使用 throughput objective 的 overlap credit。求解依然發生在 offline；runtime 查表執行。Network 很慢時，這個 objective 可能傾向把 dependent kernels 放回同一 GPU，減少 cut。

來源：Tessera Sec. III-B，PDF pp. 5–6；頻寬敏感度見 Fig. 11、PDF p. 10。

## 第 33 頁｜GPU Worker Execution

用途：Q&A backup；沿用 Tessera reference deck 第 20 頁素材，講稿為本次重寫。

Worker 根據 policy 只執行自己負責的 kernels。在 consumer 前安排 receive，在 producer 後安排 send；compute 和 communication 使用不同 streams，以 CUDA events 保證次序。R_ij 表示接收 i 的輸出給 j，S_ij 表示發送這份資料。NCCL 的 IBGDA 支援 GPU-side send／recv，減少 CPU 控制路徑成本。這些 subgraphs 已預先準備，runtime replay 不重新求解。

來源：Tessera Sec. III-C、IV，Figure 5，PDF pp. 6–7。

## 第 34 頁｜Online Monitor Signals

用途：Q&A backup；沿用 Tessera reference deck 第 22 頁素材，講稿為本次重寫。

Monitor 不是在線上重新量每顆 kernel。它量 request latency、communication time，以及兩次 communication 之間 kernel group 的時間。平均 request latency 包含 queueing，pure execution latency 不包含；兩者比值就作為 queueing pressure 訊號。比值低時偏向 latency policy，比值高時改用 throughput policy。這個解釋要和下一頁的 window、threshold 放在一起看。

來源：Tessera Sec. III-D，PDF pp. 6–7。

## 第 35 頁｜Policy Switching and Sensitivity Parameters

用途：Q&A backup；沿用 Tessera reference deck 第 23 頁素材，講稿為本次重寫。

每個 window 邊界計算壓力比值，超過 beta 就選 throughput policy，否則選 latency policy。作者在 GPT-oss 20B 的 360 秒 Azure trace 做 sensitivity sweep，選 W=300 ms、beta=1.5。切換時 workers 在 iteration boundary 同步，報告約 30 ms stall。這些是該測試的設計與量測，不是免費切換，也不是所有 workload 的最佳參數。

來源：Tessera Sec. III-D、V-D，Figure 10，PDF pp. 7、10。

## 第 36 頁｜Network Bandwidth and MILP Analysis

用途：Q&A backup；沿用 Tessera reference deck 第 32 頁素材，講稿為本次重寫。

這頁有兩個追問。第一，降低 bandwidth 是否崩潰？GPT-oss 20B、A100＋L40s，在 200／100／50／25 Gb/s 下 throughput 為 2641／2610／2550／2490 tokens/s，normalized latency 為 1.00／1.03／1.08／1.15。它支持 policy 能以 overlap 或減少 cuts 適應，但不是零通信成本。第二，solver 規模如何？兩 GPU 的 200／1000-kernel graph，正文報告 0.07／0.43 秒；約 1500 kernels 的 DeepSeek-V3 graph 在一秒內。後者只是 solver stress test，沒有證明 DeepSeek 的 end-to-end serving。

來源：Tessera Sec. V-D，Figure 11，PDF p. 10。

## 第 37 頁｜Cost Efficiency of Heterogeneous Pairing

用途：Q&A backup；沿用 Tessera reference deck 第 33 頁素材，講稿為本次重寫。

Question：效能提高是否值得多付一張 GPU 的成本？Table III 用五個 workloads 的平均 throughput 除 rental cost，再以每組左邊單 GPU 正規化；pair 的價格包含兩張。Tessera 對 PD 的 cost efficiency 平均 1.5 倍、最高 1.6 倍，對 AF 平均 1.4 倍、最高 1.5 倍。H100＋RTX Pro 6000 對 H100 單卡為 1.64 倍 Perf/$，另有 2.3 倍 throughput。這個 2.3 倍不是 Figure 6 對 PD 的 maximum。價格只用論文 Table I 的相對 rental，不能當今天市場報價。

來源：Tessera Sec. V-B，Table III，PDF p. 9；價格見 Table I，PDF p. 3。

## 第 38 頁｜Generality Across Model Families

用途：Q&A backup；沿用 Tessera reference deck 第 34 頁素材，講稿為本次重寫。

如果問 generality，要先分清 evidence 的層次。五個單 pair workloads 涵蓋四類模型，是 offline throughput；online SLO 只有 GPT-oss 20B。Cluster-scale 有 GPT-oss 和 Qwen-3 235B；DeepSeek-V3 則只是 solver graph stress test。這些證據支持一定範圍的可組合性，不能把四類 offline 結果改說成四類都驗證了 online latency。PD／AF 不適用某些家族，也不能當作這些 baseline 的零分測量。

來源：Tessera Sec. V-A–D，Figures 6–8、11，PDF pp. 7–10。
