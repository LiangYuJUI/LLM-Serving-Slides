# Helix 中文講稿

這是獨立簡報，對應 `2026-10-27-Helix.tex`。投影片頁腳與下方講稿頁碼完全一致。

依據為本地 `ASPLOS25_Helix.pdf`，標題為 *Helix: Serving Large Language Models over Heterogeneous GPUs and Network via Max-Flow*，Mei 等人，ASPLOS 2025。以下「PDF 第幾頁」指這份論文的檔案頁碼。可直接口述正文；「來源」與「備註」供準備時查閱。公式若經過整理，會在該頁註明，不把它說成逐字抄錄。

## 第 01 頁｜Title

今天介紹 Helix。它要解決的是：GPU 型號不同、而且機器可能跨地區時，LLM 要怎麼放、request 要怎麼走，才能提高 serving throughput。

作者把這個問題寫成一張有向圖上的 max-flow。Max-flow 就是網路流裡的最大流：在每條邊的容量限制下，從起點能送到終點的最大流量。這裡的流量單位是每秒可處理的 token 數。圖上的節點是 GPU，邊的容量同時反映算力與網路。Placement 用 mixed-integer linear programming，也就是混合整數線性規劃，簡稱 MILP，離線算一次。真正來 request 時，再用這張圖為每個 request 選一條 pipeline。

後面會先看為什麼平均切模型不夠，再看流量圖和 MILP，然後分開講 prototype 與 simulator 的實驗。最後用很短的篇幅，把 ThunderServe、Hetis、Tessera 放在不同切分粒度上對照，不把倍率排成名次。

來源：論文首頁與摘要，PDF 第 1 頁。

## 第 02 頁｜Presentation Roadmap

這份簡報分成四段。第一段是背景：同質 GPU 叢集為什麼愈來愈難湊齊，以及 tensor parallelism 和 pipeline parallelism 各自吃哪一種網路。

第二段是方法。先把一個已經決定好的模型放置，轉成最大流；再用 MILP 搜尋放置；上線之後用 interleaved weighted round-robin，簡稱 IWRR，把流量變成每個 request 的路徑。第三段是實驗，會分清楚 24 節點 prototype，以及 geo-distributed 和 42 節點的 simulator。第四段談限制，並和其他三個系統對照。

來源：簡報結構。比較頁是我們的整理，不是論文原表。

## 第 03 頁｜Why Heterogeneous and Geo-Distributed Serving?

先看硬體，不要把規格書上的算力當成實測 throughput。Table 3 列的是 NVIDIA 規格：H100、A100、L4、T4 的 FP16 算力、記憶體、頻寬和購買價格。這裡的 A100 是 40 GB 的 SXM 版本，不是 80 GB。

Table 1 是另一件事。它假設一半記憶體放參數、一半放 KV cache，然後估計同質系統至少要幾張 GPU。LLaMA-2 70B 在這個假設下要 12 張 L4、7 張 A100 或 4 張 H100。這是最低張數，不是 Helix 的實驗結果。

Table 4 說明配額和實際開得出來的機器可以差很多。作者在 us-east 的一個時間窗看到配額是 8 張 A100、8 張 L4、16 張 T4，但當時實際部署只有 16 張 T4。論文也說，八張 L4 的 FP16 算力可以和一張 H100 相當，而且記憶體更多、功耗更低。八乘 24 GB、八乘 72 W 是我們用 Table 3 做的乘法，論文正文只寫「更多記憶體、更低功耗」。

所以 Helix 的動機是 GPU 不好一次湊齊，不是主張任何混搭都比 H100 快。

來源：Section 1、Tables 1–4，PDF 第 1–2 頁。

## 第 04 頁｜Parallelism Across Nodes and GPUs

Tensor parallelism 把每一層的權重切開，每層要做兩次集合通訊。它很吃網路，Helix 只在同一台機器內部使用，不拿它跨高延遲的地區。Pipeline parallelism 把不同層交給不同 GPU，跨節點時主要傳 activation。如果每段切一樣多，慢的 GPU 會讓整條 pipeline 出現 bubble。

既有系統對這個問題的做法，論文主要對比兩個。Petals 是志願者計算：新機器貪婪地接下目前算力最弱的 stage，沒有針對已知叢集做全域規劃。Swarm 原本是訓練系統，把模型均分，下一站只看即時 throughput。Helix 後來把 Swarm 的放置和路由重做成 baseline。

Helix 自己的分工是：節點之間用 pipeline，節點內部如果有多張 GPU 才用 tensor parallelism。它拒絕把模型切成等長的 stage。

來源：Section 2.2、Section 3，PDF 第 2–3 頁。

## 第 05 頁｜Uniform Model Placement Is Sub-Optimal

Figure 1 是一個兩地區的例子，不是後面 24 節點的實驗叢集。算力順序是 A100 大於 L4 大於 T4。地區之間的頻寬低，地區 2 內部的頻寬高。

(b) 先把模型均分，再按算力配機器。最後一段即使有 T4 和 L4，仍然被前面只有兩張 T4 的 stage 卡住。(c) 把每個 stage 的 FLOPs 配平，A100 單獨扛一段，其他 GPU 用 data parallel 扛剩下的層。每個 request 的中間狀態還是要從地區 1 送到地區 2。

這張圖要記住的是：每個 stage 的計算量平衡，不等於 serving throughput 最大。

來源：Section 3.1、Section 4.2、Figure 1a–c，PDF 第 4 頁。

## 第 06 頁｜Network-Unaware Routing Creates Congestion

同一張圖的 (c) 和 (d)。(c) 的問題不是算力不夠，而是 A100 的送出端塞車：每個 request 的 activation 都要走慢的跨區連線。

(d) 讓兩張 T4 和 A100 並行，分掉一部分工作，慢連線上的流量就下降。論文用這個例子說明，模型怎麼切、機器怎麼放、request 怎麼走，必須一起決定。只修其中一件，另外兩件仍會把 throughput 卡死。

這仍是示意圖。後面的倍率來自 Section 6，不要把這張圖的箭頭讀成實驗數據。

來源：Section 4.2、Figure 1c–d，PDF 第 4 頁。

## 第 07 頁｜Helix Design Requirements

從這個例子可以抽出三個設計要求。第一，一個叢集只做一次放置，每台機器拿到連續的一段 layer，而且要考慮它放得下幾層、以及它會用到的連線。第二，要有一個估計器，告訴我們這個放置每秒能送多少 token。第三，上線時不要只準備幾條互不相交的固定 pipeline，而要允許 request 共用節點。

KV cache 的容量沒有被寫成第三個 MILP 目標。它留到排程時，用遮罩把快滿的 GPU 暫時拿掉。這是論文把離線放置和線上排程拆開的方式，不是我們另加的機制。

來源：Section 3、Section 4.4、Section 5.2，PDF 第 3–8 頁。

## 第 08 頁｜Helix System Overview

Figure 3 的 coordinator 做兩件慢和快的事。慢的是 model placement，每個叢集算一次。快的是 scheduler：新 request 進來，指定一條 per-request pipeline，只把 request 送到第一個節點。

每個 compute node 只跑自己負責的層，再把結果送給下一站。最後一站把輸出 token 送回 coordinator，圖上標成 Worker Finished。下一個 token 沿用同一條 pipeline，不重新解 MILP。

所以路線的決定權在 coordinator。Compute node 不自己改道。

來源：Section 5、Figure 3，PDF 第 7 頁。

## 第 09 頁｜From Model Placement to a Flow Network

形式上，叢集有一個 coordinator，記成 \(h\)，以及一組 compute node。一台機器上若有多張 GPU，Helix 把它收成一個邏輯節點，算力和 VRAM 相加。

放置函數把每個節點映到模型的一段連續層。排程函數把每個 request 映到一串節點，這串節點必須按順序覆蓋每一層。

舊的分數常常只看最慢的 stage。Figure 1c 已經說明，stage 的 FLOPs 平衡時，廣域網路仍可能是瓶頸。那個分數看不到這件事。Helix 改成問：這個放置對應的圖，最大流是多少 token 每秒。

來源：Section 4.1–4.2，PDF 第 4–5 頁。最慢 stage 的式子是論文對先前 heuristic 的描述。

## 第 10 頁｜Max-Flow Graph Abstraction

Figure 2 把三個節點畫成圖。每個 compute node 拆成入口和出口，中間那條邊代表這台機器每秒能處理多少 token。Coordinator 變成 source 和 sink，負責把 token 送進去、再把生成的 token 收回來。

邊上的數字是容量，單位是 token 每秒，不是 Mb/s，也不是 TFLOP/s。Source 到 sink 的最大流，就是這個放置的最大 serving throughput。

這張圖評估的是一個已經給定的放置。它還不是搜尋放置的演算法，搜尋在 MILP。

來源：Section 4.3、Figure 2，PDF 第 4 頁。

## 第 11 頁｜Modeling Compute Capacity

節點中間那條邊的容量，論文寫成這台機器的計算 throughput 和網路 throughput 的最小值。數值來自一次 profiling，不是 Table 3 的規格書 TFLOP/s。

後面 MILP 會用到 \(T_j\)：這台機器如果持有 \(j\) 層，每秒最多處理多少 token。\(T_j\) 也是 profile 出來的常數。Coordinator 只有 source 和 sink，沒有計算邊。

所以「算力」在 Helix 裡是 token 速率，而且已經把這台機器自己的網路上限算進去。

來源：Section 4.3；\(T_j\) 的定義在 Section 4.4 的 Constraint 3，PDF 第 5–6 頁。

## 第 12 頁｜Modeling Network Capacity

不是每對節點都有一條有效邊。有效連線只有三種：coordinator 連到持有第一層的節點；持有最後一層的節點連回 coordinator；或者節點 \(i\) 連到節點 \(j\)，而 \(j\) 持有 \(i\) 做完之後立刻需要的層。

前兩種傳的是 token。Figure 2 把 token 標成 4 byte。第三種傳的是 activation，Figure 2 標成 16 KB。容量等於 profile 到的平均頻寬，除以這個 payload 的位元組數，得到 token 每秒。

4 byte 和 16 KB 是這張圖的標註，不是所有模型的常數。Activation 比 token 大三個數量級，所以廣域網路上先被吃滿的通常是 activation。

來源：Section 4.3、Figure 2，PDF 第 4–5 頁。

## 第 13 頁｜Why Max Flow Represents Serving Throughput

一單位的流，就是一秒內可以通過某台機器或某條連線的一個 token。流量守恆要求進入節點入口的 token，必須從出口離開。Helix 用 preflow-push 演算法計算 source 到 sink 的最大流。這個值就是目前放置的最大 serving throughput。

它回答的是穩定的 token 速率。它不直接給出 prompt latency、decode latency，也不是 P99。

後面還有一個提前停止用的上界：所有節點計算 throughput 的總和，除以模型層數。那是上界，不是實測 throughput。

來源：Section 4.3 與 Section 4.5，PDF 第 5–7 頁。

## 第 14 頁｜Worked Three-Node Example

用 Figure 2 的數字把單位走一遍。A100 持有第 1 到第 2 層，T4-1 持有第 1 層，T4-2 持有第 3 層。節點邊上寫的是 1500、1000、1000 token 每秒。Token 尺寸的邊上寫著 1.25M、2.5M 和 625K。Activation 邊上寫著 458 和 687。

備註：把 40、80、20 Mb/s 除以 4 byte，會得到 1.25M、2.5M、625K；把 60 和 90 Mb/s 除以 16 KiB，會接近 458 和 687。這是我們對圖上數字的核對，論文正文沒有逐步寫出這兩個除法。投影片只把這些數字當作圖的標註。

重點是：決定最大流的是每秒幾百個 token 的 activation 邊，不是每秒幾百萬的 token 邊。這是三節點示意，不是實驗叢集。

來源：Figure 2，PDF 第 4 頁。

## 第 15 頁｜MILP Variables and Objective

MILP 要搜尋的是放置，目標是把 source 流出的流量加總最大化。變數可以記成五組。\(s_i\) 是節點 \(i\) 的第一層。\(b_{ij}\) 表示這個節點剛好放 \(j\) 層。\(f_{i,j}\) 是邊上的流量，單位仍是 token 每秒。\(d_{i,j}\) 表示這條邊是否有效。還有兩個輔助二元變數，用來把層的重疊條件寫成線性式。

層的終點是 \(e_i = s_i + \sum_j j\, b_{ij}\)，節點持有的是半開區間 \([s_i, e_i)\)。\(k\) 是這張 GPU 最多放得下幾層。Table 5 把變數個數寫成對節點數或邊數是線性的。投影片的符號是為了口頭說明而壓過的，不是逐行抄表。

來源：Section 4.4、Tables 5–6，PDF 第 5–6 頁。

## 第 16 頁｜Placement and Memory Constraints

第一組限制是：每個節點只能選一個層數，所以 \(b_{ij}\) 對 \(j\) 求和等於 1；起點和終點都必須落在模型的 \(L\) 層裡面。

記憶體怎麼進來？論文不是在 Table 6 裡放一個 KV 位元組變數。它用 \(k\) 限制這張 GPU 最多能放幾層。KV 留到執行時再遮罩。

另外有一個選項叫 partial inference。如果 \(s_j < e_i < e_j\)，從 \(i\) 來的 request 在 \(j\) 上只跑 \([e_i, e_j)\) 這些層。求解器可以打開或關掉這個選項。關掉時，邊只有在 \(e_i = s_j\) 時才有效，也就是層段必須首尾相接，不能重疊。

來源：Section 4.4，Constraint 1，PDF 第 6 頁。

## 第 17 頁｜Flow and Compute Constraints

第二組是流量守恆：流進節點 \(i\) 的和，等於流出的和。

第三組是計算上限。流過這個節點的流量，不能超過 \(\sum_j b_{ij} T_j\)。因為 \(b_{ij}\) 只有一個是 1，這其實就是選中那個層數對應的 profile 速率 \(T_j\)。

網路還會再卡一次，那是下一頁的傳輸限制。這一頁只說：節點不能被分配超過它在該層數下測到的 token 速率。

來源：Section 4.4，Constraints 2–3，PDF 第 6 頁。求和時略過節點自己，依論文敘述。

## 第 18 頁｜Connectivity and Network Constraints

第四組決定邊能不能用。Coordinator 連進節點 \(i\)，只有在 \(i\) 持有第一層時成立，線性寫法是 \(s_i \le L(1-d_{\mathrm{source},i})\)。連回 sink 則要求終點層數夠深。

兩個 compute node 之間，條件是 \(s_j \le e_i < e_j\)。論文用兩個輔助二元變數把這個不等式線性化，再讓 \(d_{ij}\) 不超過兩者的平均。投影片沒有把每一條輔助不等式都展開。

第五組是傳輸上限：流量不超過 \(d_{ij}\) 乘上這條連線 profile 到的 token 速率 \(S_{ij}\)。無效邊的流量必須是 0。

來源：Section 4.4，Constraints 4–5，PDF 第 6–7 頁。

## 第 19 頁｜Making the MILP Practical

變數個數對節點數是線性的，但 40 個節點以上仍可能要跑很久。論文用三個辦法。第一，把慢的連線剪掉，讓平均度數約為 12。第二，用 Petals、Swarm 和 separate pipelines 的解當起始值。第三，若已經接近「總計算速率除以層數」這個上界，就提早停。

把整數放寬成線性規劃再四捨五入，論文認為不可行，因為層的整數一改，邊可能整批失效，最大流會跳。實作上 Gurobi 若 10 分鐘沒有更好的解就停，每個叢集最多搜 4 小時，機器是 14 核 CPU。

論文提到若要擴到數百或數千節點，可以先用 heuristic 切成小叢集再各自跑 Helix。這是建議，不是已評估的結果。

來源：Section 4.5–4.6、Section 6.2，PDF 第 7 與第 9 頁。

## 第 20 頁｜Runtime Components and Control Flow

執行順序可以收成五步。叢集建立時，profile 節點和連線，解一次 MILP，每個節點載入自己的層。Request 到達時，coordinator 造出一條 pipeline，送給第一個節點。

節點把「上一個 batch 執行期間到達」的 request 合成下一個 batch，不再額外等待。這是 best-effort dynamic batching。最後一節點把 token 送回 coordinator。同一個 request 的後續 token 沿用這條 pipeline。

放置是叢集的常數。每個 token 只是在這張圖上走已選好的路。

來源：Section 5、Figure 3，PDF 第 7–8 頁。

## 第 21 頁｜Per-Request Pipelines

一條合法 pipeline 是一串「節點加上它要跑的層」，合起來每層恰好跑一次，而且順序正確。先前系統常用固定 pipeline，每條 pipeline 的機器互不相交。

Helix 允許 pipeline 相交。候選路徑就是放置圖上所有從 source 到 sink 的路。路徑一旦定了，後面的 token 不換路。

和 HexGen 這類固定 pipeline 的差別，論文放在 related work：Helix 認為路徑可以相交，而且 MILP 在其模型下可以給出最優放置。這個「最優」是公式意義上的，和下一頁的提早停止要分開看。

來源：Section 5.1，PDF 第 8 頁；HexGen 的對照在 Section 7，PDF 第 13 頁。

## 第 22 頁｜Converting Max-Flow Weights into Scheduling

IWRR 是 interleaved weighted round-robin。每個頂點有一個排程器。鄰居的權重，等於最大流解裡那條出邊上的流量。選中的頻率和權重成正比，但交錯選取，避免短時間把一條重邊灌爆。

實際走路是：coordinator 的排程器選第一站，該節點的排程器選第二站，直到路徑完整。在走之前，KV 超過高水位的節點會先從候選裡拿掉。

MILP 決定的是速率。IWRR 是上線時實現這些速率的規則。

來源：Section 5.1，PDF 第 8 頁。IWRR 本身引用 Tabatabaee 等人。

## 第 23 頁｜Pipeline Scheduling Example

Figure 4 的頂點是 compute node。邊只保留 MILP 認為有效的連線。邊上的數字是最大流解裡的流量，不是連線容量。容量在 Figure 2，流量在這張圖，兩套數字不要混。

圖右側給了兩條例子：request 1 走 \(1 \rightarrow 5 \rightarrow 9\)，request 2 走 \(2 \rightarrow 6 \rightarrow 8\)。它們可以共用叢集，不是兩條凍結的 replica。

來源：Section 5.1、Figure 4，PDF 第 8 頁。

## 第 24 頁｜KV-Cache Masking and Backpressure

每張 GPU 能放的 KV cache 有限。超過之後若把 request 換到主記憶體，論文說 throughput 會明顯下降。但輸出長度要到生成結束才知道，所以排程器無法知道精確的 KV 占用。

Helix 用平均輸出長度估計每個節點的 KV 使用量。超過 high water mark 的節點，會從 IWRR 的候選中遮掉，直到上面有 request 結束。論文沒有給出這個水位的數值，也沒有給出估計式的位元組公式。

這是同一條 IWRR 上的遮罩，不是再解一次 MILP。

來源：Section 5.2，PDF 第 8 頁。

## 第 25 頁｜Implementation and Prototype

Prototype 大約 1,500 行 Python 和 1,700 行 C++，模型執行用 vLLM 0.4.0.post1。作者加了 unified page pool 來支援 partial inference。節點之間用 ZeroMQ，MILP 用 Gurobi。

Simulator 大約 14,000 行 Python，用來試更多 GPU 和網路組合。Geo-distributed 和 42 節點的結果來自 simulator。

他們在 single cluster 上把 simulator 和 prototype 對過：decode throughput 的平均誤差低於 5%，prompt latency 低於 5%，decode latency 低於 4%。這個誤差只涵蓋該次 single-cluster 對照，不能直接當成跨區網路的誤差棒。

實驗節點是單 GPU。多 GPU 節點可以用節點內的 tensor parallelism，但 prototype 實驗沒有這樣配。

來源：Section 6.1、Section 6.3，PDF 第 9 頁。Section 6.2 寫實驗用 FP16。

備註：Artifact 附錄寫 prototype 可以用 dummy weights、只需要模型結構。Section 6.2 則寫推論使用 FP16。兩處是否指同一批報告中的權重，論文沒有對齊，報告時不要自行裁定。

## 第 26 頁｜Evaluation Methodology

三個叢集不要混。Single cluster 是 prototype：4 張 A100、8 張 L4、12 張 T4，同一個 Google Cloud 地區，網路設成 10 Gb/s。作者認為這個速率足以讓瓶頸落在 GPU 而不是網路。

Geo-distributed 是 simulator。三個子叢集分別是 4 張 A100、2 張 L4 加 8 張 T4、6 張 L4 加 4 張 T4。叢集之間平均約 100 Mb/s、延遲約 50 ms。100 Mb/s 是依 Table 7 的跨區 iperf3 結果來設定的；Table 7 的配對大約從 54 到 204 Mb/s，不是每一對都剛好 100。

第三個是 42 節點、7 種節點類型的高異質叢集，同樣是 simulator，包含 V100 和多 GPU 節點。

模型是 LLaMA-1 30B 和 LLaMA-2 70B，FP16。Baseline 是重做的 Swarm，以及在 Helix 系統裡實作的 separate pipelines，簡稱 SP，也就是每種機器各服務一份模型。Petals 只在放置實驗裡比較，因為它沒有集中式 request scheduling，所以沒有端到端對打。

離線指標是平均 decode throughput，單位是每秒生成的 token。線上另外報平均 prompt latency 和平均 decode latency，不是 P99。線上到達率是 Azure 的形狀，縮放到該叢集峰值的 75%。離線則讓到達率高到可以把叢集餵滿。

來源：Section 6.2、Table 7，PDF 第 9 頁。

## 第 27 頁｜Workload Characteristics

Trace 是 Azure Conversation。輸入長於 2048 或輸出長於 1024 的 request 被拿掉。剩下 16,657 筆，平均輸入 763 token，平均輸出 232 token。論文說這比他們引用的先前工作更長，也更難。

線上實驗熱身 30 秒、測 30 分鐘。離線熱身 1 分鐘、測 10 分鐘。Figure 5 畫的是長度分布和到達率，是縮放到 75% 之前的 trace 形狀。

後面的延遲倍率都是這份剪過的長對話，不要外推到短 prompt。

來源：Section 6.2、Figure 5，PDF 第 8–9 頁。

## 第 28 頁｜Single-Cluster Results

這一頁是 prototype，Figure 6。上面四張是 decode throughput，下面四張是線上的 prompt 和 decode latency。箱子是 25 到 75 百分位，鬚是 5 到 95，紅線是中位數。圖裡同時有實系統和 simulator，用來檢查 simulator。

LLaMA 30B 時，每種 GPU 都夠自己組成一條 pipeline。Helix 的最好放置是三種 GPU 各一份 replica。相對 SP，離線和線上 throughput 高 4% 和 14%；prompt latency 低 2%，decode latency 高 10%。相對 Swarm，throughput 是 2.14 倍和 2.07 倍；prompt 低 32%，decode latency 低 12%。

LLaMA 70B 時，單一 GPU 類型無法在留下 KV 空間的前提下自己放下整份模型，SP 因此變差。相對 SP，throughput 是 1.86 倍和 1.69 倍，但 Helix 的平均 latency 更高，因為 SP 把大多數 request 放在 A100 上，L4 和 T4 沒被用滿。相對 Swarm，throughput 是 1.94 倍和 2.00 倍；prompt 低 15%，decode latency 高 16%。

Throughput 的提升是實機上的。它不是每一個 latency 欄位都變好。

來源：Section 6.3、Figure 6，PDF 第 9 頁。成對的百分比順序是先離線、再線上。

## 第 29 頁｜Geo-Distributed Results

這一頁全部是 simulator。GPU 集合和 single cluster 相同，但叢集之間大約 100 Mb/s，所以所有方法的 throughput 都下降、latency 都上升。圖上 H 是 Helix，S 是 Swarm。

LLaMA 30B 相對 SP：離線和線上 throughput 高 7% 和 10%；prompt 低 14%，decode latency 高 2%。相對 Swarm，論文寫 2.41 倍和 2.33 倍，句子是 “both online and offline”，沒有像其他句子那樣用 respectively 標明哪一個是線上。Prompt 和 decode latency 分別降低 66% 和 24%。摘要裡的 “up to 66% and 24%” 就是這組線上、對 Swarm 的模擬結果。

LLaMA 70B 對慢網路更敏感，因為 activation 更大、模型更深。Helix 的 pipeline 比 Swarm 淺 28%，也比它自己在快網路上的放置淺 19%。相對 SP，離線和線上是 1.61 倍和 1.79 倍。SP 的平均 latency 較低，因為 12 張 T4 受 VRAM 限制而沒被用滿。相對 Swarm 是 1.92 倍和 1.97 倍；prompt 低 21%，decode latency 低 7%。Swarm 離線的平均 prompt latency 是 71 秒，為 Helix 的 7.5 倍。

來源：Section 6.4、Figure 7，PDF 第 10 頁。

## 第 30 頁｜High GPU-Heterogeneity Results

這一頁仍是 simulator，只有 LLaMA 70B，42 個節點、7 種型號。V100、T4 和兩張 T4 的節點無法自己形成 pipeline。SP 的數字不含這些機器。SP+ 嘗試把它們編成混合 pipeline。

相對 Swarm、SP、SP+，離線 throughput 是 1.37、2.91、2.24 倍；線上是 1.48、3.29、2.54 倍。Prompt latency 分別降低 17%、1% 和 7%。Helix 的平均 decode latency 略高，因為 baseline 把多數 request 留在快的、VRAM 大的 GPU 上。

摘要的 3.3 倍，對應的是線上相對 SP 的 3.29 倍，四捨五入後寫進摘要。不要把它說成 prototype 上的 3.3 倍。

來源：Section 6.5、Figure 8，PDF 第 10 頁。

## 第 31 頁｜Model Placement Deep Dive

這一頁把排程器固定成 Helix 的，只換放置方法，所以看到的是放置本身的差距。工作負載是離線 LLaMA 70B。

相對 Petals 和 Swarm，single cluster 是 1.23 倍和 2.10 倍；geo-distributed 是 1.49 倍和 2.38 倍。

Single cluster 的案例：Swarm 在 pipeline 尾端用四張 T4、每張 4 層，造成瓶頸，A100 和 L4 的算力閒著。Petals 有八張 T4 和一張 L4 利用不足。Helix 的放置讓幾乎所有節點都忙。圖上節點裡的整數是層數，不是 throughput。

Petals 仍不是端到端伺服器，只是放置方法。

來源：Section 6.6、Figure 9，PDF 第 11 頁。

## 第 32 頁｜Request Scheduling Deep Dive

這一頁把放置固定成 Helix 找到的，只換排程。還是離線 LLaMA 70B。

相對 Swarm 和隨機排程，single cluster 的 throughput 高 30% 和 29%；geo-distributed 高 22% 和 15%。Geo-distributed 還比了 shortest queue，Helix 高 19%。

案例在跨區叢集。有三條慢連線上，prompt 階段的 request 平均要等 5 到 16 秒。其中一個壅塞，來自三跳之外的節點怎麼排。所以只看下一站佇列，看不到上游已經造成的切口。

來源：Section 6.7、Figure 10，PDF 第 12 頁。

## 第 33 頁｜MILP Optimization Ablation

消融是離線 LLaMA 70B。24 節點指 geo 設定，42 節點指高異質設定。

平均度數 12 的剪枝，在兩個設定上分別刪掉 50% 和 72% 的連線。Table 8：24 節點從 1376 個變數、1848 條限制，降到 876 和 1122；42 節點從 4004 和 5502，降到 2144 和 2772。問題規模大約少 36% 和 46%。

在同樣的時間預算下，用剪枝找到的放置，decode throughput 高 16% 和 2%。論文把這解釋成搜尋變容易，不是證明被刪的連線永遠沒用。從 heuristic 起始時，最好的放置相同，牆鐘時間少 43% 和 8%。論文也說，加速幅度會隨 MILP 實例改變。

來源：Section 6.8、Figure 11、Table 8，PDF 第 12 頁。

## 第 34 頁｜Solver Time and Solution Quality

Figure 12 的實例比 24 和 42 節點小：LLaMA 30B，4 張 L4 加 6 張 T4。最好的可行放置在 5 分鐘內到達最優 throughput。要證明它是最優，求解器還要再花一個多小時把搜尋樹走完。紅虛線是這個叢集的最優 throughput。

這支持「可以提早停」在這個小實例上是合理的。它沒有證明 42 節點那次 4 小時預算內的解也是最優。

來源：Section 6.9、Figure 12，PDF 第 13 頁。

## 第 35 頁｜Helix vs. ThunderServe, Hetis, and Tessera

這一頁是我們的整理，不是任何一篇論文的原表，也不用倍率排名。

ThunderServe 切的是 prefill 和 decode 兩個 phase，決定 GPU 怎麼分組、哪一組做哪個 phase、以及 request 怎麼路由。Hetis 切的是 dense 模組和 attention head，Primary worker 先定下來，線上再按 head 分配，必要時搬 KV。Helix 切的是 layer 區間和跨節點路徑，放置做一次，每個 request 選一條路。Tessera 切到 CUDA kernel，離線做 MILP，再用時間窗切換策略。

它們移動的狀態也不同：phase 邊界的 KV、head 級的 QKV 和 KV shard、token 與 activation、以及 kernel 邊界上的 tensor。環境分別是異質雲、本地異質叢集、含跨區的異質叢集，以及 NVIDIA 的異質配對。模型範圍上，前三個報告的是 LLM；Tessera 的離線實驗還有 SSM、多模態和 diffusion。

Helix 自己的主要限制是放置不做在線重算，而且跨區與 42 節點結果是模擬。

備註：本頁為跨論文整理。ThunderServe 與 Hetis 的格子依那兩篇論文自己的系統描述，不依 Helix 的 related work。Tessera 的格子依本地 Tessera PDF。

## 第 36 頁｜Limitations and Threats to Validity

放置每個叢集算一次。論文描述的 runtime 不會因為工作負載改變而重解 MILP。

跨區和 42 節點是 simulator。低於 5% 的誤差只來自 single-cluster 的對照。KV 遮罩用平均輸出長度，高水位沒有給數字。剪枝和 10 分鐘沒有進步就停止，表示上線的放置不一定是已證明的最優。結論裡 “guaranteed optimal solution” 指的是 MILP 公式若解完可以保證最優，不是每一次限時執行都已證明最優。

有些設定下 decode latency 會變差，因為 Helix 真的使用了 SP 放著不用的慢 GPU。證據範圍是 FP16 的 LLaMA-1 30B 與 LLaMA-2 70B，以及一份剪過的 Azure trace。

報告任何倍率時，要同時說叢集、是不是 simulator、以及指標是 throughput 還是哪一種 latency。

來源：Section 4.5、Section 6、Section 8。最後一點是結論用語和 Section 6.2、6.9 之間的對照，屬於報告時的限制，不是作者自己列出的條目。

## 第 37 頁｜Conclusion

三件事。第一，一個放置可以被評成一張流量圖，邊的容量是 token 每秒，最大流是 throughput，不是 latency。第二，MILP 和 IWRR 是兩個時間尺度：層的放置做一次，每個 request 選路，後續 token 沿用。第三，增益大的地方，是單一 GPU 類型放不下模型，或廣域網路成為瓶頸的時候。

在論文報告的設定裡，相對 SP 的 decode throughput 最高到線上 3.29 倍，摘要寫成 3.3 倍。相對 Swarm 最大的延遲降幅，66% 的 prompt 和 24% 的 decode，是模擬的跨區 LLaMA 30B 線上實驗。

Helix 同時決定層的放置和 request 的路徑。它沒有主張對每個 baseline 的每個 latency 都更好。

來源：Section 8；倍率回查 Section 6.4 與 Section 6.5，PDF 第 10 與第 14 頁。

## 第 38 頁｜Questions & Discussion

可以留下來的問題有三個。Max-flow 的單位到底是 token 速率還是延遲，這決定我們能不能拿它估 TTFT。Per-request pipeline 和固定 pipeline 差在路徑可以相交，但放置本身並不隨每個 token 重算。最後，哪些數字來自 24 節點 prototype，哪些來自 simulator，不能在問答裡混用。

若要接到這個系列的其他系統，Helix 是層與路徑，ThunderServe 是 phase，Hetis 是 head，Tessera 是 kernel。它們沒有在同一套硬體上比過。

備註：問答頁沒有新的實驗數字。
