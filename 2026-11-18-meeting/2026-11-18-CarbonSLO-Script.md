# 2026-11-18 Carbon–SLO 報告講稿

主動報告只走 Main。Backup 留給教授追問。

總時間 **16 分**（960 秒）。時間是照著講的目標，不是每句都要念完；若前面超時，Q3 到 Q5 各收 10 秒，最後仍要留下「這些是我們提出的方向，不是作者已經驗證的結果」。

技術詞 TTFT、TPOT、SLO、PUE、RTT、MILP、ILP、CI、KV、continuous batching 保留英文。

## Main 01 — Carbon–SLO at Geo-Scale

- 預計：20 秒
- 論文：封面；arXiv:2610.14571，2026-10-10
- 上一頁：無。這是開場。

老師好。今天報告 Penn State 的 Topcu、Cim、Ozturk 和 Kandemir 這篇 preprint，題目是 Dissecting the Carbon–SLO Tension in Geo-Distributed LLM Serving。它問的是：把 request 送到比較綠的資料中心，能不能在 TTFT 和 TPOT 的 SLO 底下真的減碳。

- 怎麼指：停在標題和作者。
- 下一頁：先說明 carbon-aware routing 的機會，以及為什麼需要更完整的 serving 模型。

## Main 02 — Why Is Carbon-Aware LLM Routing Challenging?

- 預計：65 秒
- 論文：Section I 與 Table I；Section II；Section III-B、III-C
- 上一頁：從論文題目進入 carbon-aware routing 的機會與難題。

不同地區的 DC，用電的 CI 不一樣，也會隨時間變。所以把 request 送往 CI 較低的 DC，有機會減少 operational carbon；但總碳排還要看耗能和 PUE。

困難是，改變目的地，也會改變 serving 狀態。跨區多了 RTT；request 集中到同一站，可能增加排隊和 GPU 資源競爭。低 CI 本身不代表高延遲，是否符合 SLO 要看當下負載和網路條件。

LLM serving 又是動態的：Continuous Batching 讓 batch size 持續變動；KV Cache 或 batch 空間不足，就得等 admission，拉長 TTFT；Prefill 和 Decode 的延遲與功率特性也不同，還會影響 TPOT。這些因素必須一起考慮。

先前工作各有涵蓋，但沒有把這些影響完整整合。因此作者開發 geo-distributed LLM serving simulator，用真實 A100／vLLM 的量測校準，再模擬不同負載下的 routing。這不是已部署的 16 個實體 DC。

- 怎麼指：由上往下說明 Opportunity、四個 Challenge，再指 Paper's Response。Load-dependent Latency、Phase-dependent Power 和 Lowest-CI routing 三條連結留給追問，主動報告不開 B11、B12、B13。
- 下一頁：用 Table I 具體確認，各篇工作涵蓋了什麼、還缺少什麼。

## Main 03 — Table I: Scope of Prior Work and This Paper

- 預計：60 秒
- 論文：Section I，Table I
- 上一頁：前一頁提出 modeling 的必要性，這一頁用 Table I 檢查既有工作的涵蓋範圍。

先看這張 Table I。這篇的重點，是把跨資料中心 LLM serving 的問題考慮得更全面。表格左邊是各篇工作的排程粒度與延遲目標，中間四欄比較 batch-aware latency、power、queueing 和跨區 transfer，最後一欄是它們報告的延遲指標。

看最下面綠色這一列，這篇同時納入 batch 對延遲與功率的影響、engine 裡的排隊，以及跨區傳輸延遲，並用 TTFT、TPOT 對照 MLPerf 的 SLO。這些因素會一起影響 request 能不能送到低碳的資料中心，所以需要放在同一個模型裡評估。

這裡不要解讀成過去的工作全部都沒考慮：有幾篇已經納入 transfer，MOER 的 power 是部分建模，GCOS 的 batch-aware latency 則是不適用。這篇的差別在於把表中這些面向整合起來。

- 怎麼指：先指中間四個比較欄位，再沿著綠色的 This paper 那一列說明；不用逐篇念完。
- 下一頁：把優化目標寫清楚：送到哪個 DC、最小化 operational carbon、TTFT 和 TPOT 要在 budget 裡。

## Main 04 — What Is the Carbon–SLO Optimization Goal?

- 預計：55 秒
- 論文：Section II；Table II 的 budget
- 上一頁：Table I 指出既有工作只涵蓋這些 serving 特性的一部分。這一頁先寫下這篇要優化的目標。

決策是把每一筆 LLM request 指派到一個 datacenter。不是搬 layer，不是把 KV Cache 遷到別的站，也不是放 MoE expert。目標是 operational carbon，不包含 embodied carbon，也不拿模型品質去換碳。

中間的式子是在 routing 上最小化 operational carbon：每個 datacenter 的能量乘上那個站的 CI。能量已經乘過那個 DC 的 PUE，不要再乘一次。功率是模型裡的 IT 功率，包含 engine 和 host。

下面兩個不等式是估計的 TTFT 和 TPOT，各自要落在那筆 request 的 budget 裡。四種演算法的差別留到後面的方法頁。

- 怎麼指：先指 Decision，再指最小化的式子，然後左右兩個 budget。
- 下一頁：這個目標是在什麼 simulator 裡評估的。

## Main 05 — How Does the Geo-Distributed Simulator Work?

- 預計：75 秒
- 論文：Section III-C，Figure 3；Section III-A 的 polling 欄位
- 上一頁：優化目標定了，接著看 request 怎麼在 simulator 裡走。

Figure 3 是這一頁的主圖，caption 是論文原圖的。路徑照圖上的編號。1，load generator 用 Poisson 把 request 送到區域 scheduler。2 和 3，scheduler 可以留在本地，或轉給別區；轉出去就要付 RTT，再由對方的 scheduler 放上目標 DC。4 和 5，provisioner 週期性地跟每個 DC 要狀態，再把這份 snapshot 和 RTT 矩陣廣播給所有 scheduler。

DC 裡面，node 之間和 node 裡面都是 round-robin。所以論文把測到的減碳歸給區域排程，不是歸給 DC 內部的放置。Engine 跑的是 continuous batching：有空的 batch 位子、KV 也放得下，才把 request 從 queue 收進來。Queue 的長度不是一個常數。

Scheduler 看得到的，是每個 DC 平均過的 batch size、queue 深度、KV 佔用、prefill duty，再加上 CI。

- 怎麼指：左手指著圖上的 1 到 5，右手對應三小段。最後停在 continuous batching。
- 下一頁：這份 snapshot 怎麼變成 TTFT 和 TPOT 的估計。

## Main 06 — How Does the Scheduler Predict TTFT and TPOT?

- 預計：65 秒
- 論文：Section IV 開頭的 latency estimator；逐步模型在 Section III-B，不在這頁展開
- 上一頁：Figure 3 已經講過 provisioner。這一頁只問那些數字怎麼變成 TTFT 和 TPOT。

Scheduler 用的是 polling 得到的 DC 平均：batch size、queue、KV occupancy、prefill duty，再加上 RTT 矩陣。這不是每張 GPU 的即時讀數。估計上過了 SLO，也不等於最後真的過了。

TTFT 是三項相加。RTT 是跨區傳輸，留在本地就是 0。W_d 是在那個 DC 等一個 batch 位子。後面的 prefill 時間吃的是這筆 prompt，再加上已經排在 queue 裡的 token。碳的算法上一頁的優化目標已經寫過，這裡不再重複。

TPOT 是 decode step 加上 queued prefill，整個和再除以 1 減 duty。B 加 1 表示這筆 request 加入投影的 batch，KV 是當下的 occupancy。T pre 是還在 queue 的 prefill，攤到輸出長度上。分母對應已經在跑的 prefill，會把這兩項一起拉長。duty 和 queued prefill 不是同一個量。

- 怎麼指：先指上面的流程，再指 TTFT，再指 TPOT。符號細節點進 B05。
- 下一頁：Facility MILP 怎麼在預測過的 SLO 可行集合裡指派 request。

## Main 07 — How Does Facility MILP Route Requests Under SLO Constraints?

- 預計：70 秒
- 論文：Section IV-C
- 上一頁：TTFT 和 TPOT 的估計講完了。這一頁把那個估計放進 Facility MILP 的四個步驟。

第一步用最新的 provisioner snapshot 和跨區 RTT，估計每一筆 request 到每一個 datacenter 的 TTFT 和 TPOT。估計式上一頁已經寫過，這裡不再展開。

第二步只留下預測上兩個預算都過得了的指派。投影片把這個候選集合寫成 \(F_r\)。這是簡報用的記號，表示求解之前就固定的可行集合。

第三步解 Facility MILP。目標是各筆的邊際碳成本，加上每個 datacenter 的共享固定成本。每一筆 request 要在自己的 \(F_r\) 裡分到一個 datacenter。容量乘上 \(y\)，\(y\) 表示這個 window 有沒有用到該 datacenter。求解時不再重算 TTFT 或 TPOT。共享能量怎麼只收一次，留在補充頁。

第四步才執行。Simulator 記下實際的 TTFT、TPOT、operational carbon 和 SLO violation。預測上可行，不保證最後真的守得住。

- 怎麼指：由上到下四步。第三步停在目標和兩條限制。
- 下一頁：另外三種政策各自補了什麼，又留下什麼。

## Main 08 — How Do the Other Scheduling Policies Differ?

- 預計：70 秒
- 論文：Section IV-A 到 IV-C
- 上一頁：Facility MILP 先用預測的 SLO 限制可去的 datacenter，再一起選指派。這一頁用它當對照，看另外三種方法。

Greedy 一筆一筆決定。它先留下估計上 TTFT 和 TPOT 都過得了的 DC，再用 α 在 latency 和 carbon 之間取捨。同一個 snapshot 上，沒有協調的 request 會擠到同一個站。

Standard ILP 和 Facility MILP 幾乎一樣，都是一個 window 一起指派。差別是它沒有把每個 datacenter 的 shared fixed carbon cost 算進去。

Iterative ILP 解完就把指派投影回 batch 和 queue，重算 TTFT 和 TPOT，再解。指派重複，或做滿 3 次，就停。它補的是負載估計，能量仍然是各筆相加，而且 solver 時間會增加。

- 怎麼指：三張色塊由上到下。Greedy、Standard ILP、Iterative ILP。
- 下一頁：這些估計和排程是建在什麼測量上，驗證到哪裡為止。

## Main 09 — Can We Trust the Geo-Distributed Simulator?

- 預計：70 秒
- 論文：Section V-B；限制在 Section VI。逐步擬合在 Section III-B，不跟這裡的百分比混在一起
- 上一頁：另外三種政策和 Facility MILP 的差別講完了。實驗數字之前，先分清楚哪一層是量到的。

分成三層。A，在 A100-40GB、vLLM 0.6.3、FP16 上量延遲和功率。B，每個模型、每種 tensor parallel，各配一組 prefill 和 decode 的延遲與能量。C，跨區模擬：routing、queue、continuous batching、RTT、多個 region 和 CI。這一層不是再做一次硬體實驗。

Within-node 的對照只做 Llama-3.1-8B。三個 data-parallel 的 vLLM engine，19 個 arrival rate，超過四萬筆 request。TTFT 整體平均誤差 9.1%，TPOT 平均誤差低於 5%，GPU energy 和量測差在 2.5% 以內。飽和附近的 TTFT 平均誤差升到 28.5%，而且是偏高估。這是端到端的 within-node 誤差。逐步的 1.7%、3.4%、5.6% 留在公式頁，不要加進 9.1%。單節點和 16 個實體 DC 的邊界在補充頁。

- 怎麼指：A、B、C 由上到下。數字停在 Within-node validation，28.5% 停在最後一行。
- 下一頁：實驗比的是哪些模型、負載、SLO 和 baseline。

## Main 10 — How Is the System Evaluated?

- 預計：55 秒
- 論文：Section V-A，Table II
- 上一頁：驗證的邊界講完了。這一頁只說明實驗在比什麼，不再重講校準。

左邊兩個是 dense：Llama-3.1-8B 和 Qwen2.5-7B，TP 等於 1。右邊是 MoE：Mixtral-8x7B，8 個 expert 裡每次 top-2，TP 等於 4。因為 TP=4，Mixtral 每個 DC 的 engine 數只有 dense 的四分之一。低、中、高負載不能直接拿 req/s 互比：7B 和 8B 是 1200、2400、4000；Mixtral 是 800、1200、2000。

拓樸是 4 個區域 scheduler 乘 4 個 DC，一共 16 個模擬的 DC。SLO 是 TTFT 3 秒；dense 的 TPOT 是 100 毫秒，Mixtral 是 200 毫秒。

不會看碳的 baseline 是 round-robin 和 least-loaded。會看碳的是 Green-LLM，以及 MOER，也就是 α 等於 0 的 greedy。指標是含 idle 和 host 的 operational carbon、SLO violation rate，再加上 TTFT 的 p50、p90、p99。Violation rate 不是平均延遲，也不是 throughput。

- 怎麼指：表格的 Dense / MoE 兩欄，再由上到下指 Topology、Baselines、Metrics。
- 下一頁：全篇最重要的結果圖，Figure 4(a)。

## Main 11 — Q1: Can Carbon Be Reduced Without Excessive SLO Violations?

- 預計：85 秒
- 論文：Abstract；Section V-C，Figure 4(a)
- 上一頁：設定講完，這一頁回答減碳會不會把 SLO 打穿。

這是 Figure 4(a)。左邊是中負載，右邊是高負載。中負載時，只看 carbon 的 Greedy 和 Facility MILP 差不多。高負載時，Greedy 的 SLO violation 會拉得很高，Facility MILP 仍然比較好。

- 怎麼指：先指左邊兩組接近的點，再指右邊 Greedy 拉遠的點。
- 下一頁：violation rate 看不出尾巴。Figure 4(b) 把高負載的 TTFT 百分位拆開，而且圖上的百分比不是延遲。

## Main 12 — Facility MILP Balances TTFT and Carbon Saving on Every Model, No Clear Trade-off

- 預計：60 秒
- 論文：Section V-C，Figure 4(b)
- 上一頁：上一頁是違規比例，這一頁是高負載時 TTFT 的尾巴。

Figure 4(b) 只有高負載。橫條是 TTFT，從 p50 到 p99，中間刻度是 p50 和 p90。條旁邊印的百分比是相對 RR 的減碳，不是秒數。這件事要先講，不然 26%、35% 會被聽成延遲。

Dense 模型上，greedy 的 p99 TTFT 還在 3 秒預算裡。可是 α 等於 0 仍然違規，違的是 TPOT：decode batch 堆在最綠的 DC 上。所以 TTFT 的尾巴沒爆，不代表 SLO 過了。

Mixtral 不一樣。它的 engine 少、輸出比較長。α 等於 0 的 greedy 把中位數 TTFT 推到 3.3 秒。ILP 和 MILP 把中位數留在 0.7 秒以內，p99 留在 2.2 秒以內。激進的 greedy 和 Green-LLM，p99 可以到 8.8 秒。Iterative ILP 在 dense 上的 p99 會到 7.5 秒，那是反覆求解的開銷，不是 GPU 算得比較慢。

- 怎麼指：先指一條橫條上的百分號，說明那是碳。再指 Llama 上 greedy 的短條，和 Mixtral 上 greedy 拉到很右邊的長條。
- 下一頁：減碳空間從哪裡來。PUE 和 CI 的分散是兩件不同的事。

## Main 13 — Q3: How Do PUE and Carbon-Intensity Spread Affect Savings?

- 預計：55 秒
- 論文：Section V-C，Figure 5
- 上一頁：主結果是在預設 PUE 和一個 CI 小時上。這一頁看這兩個假設鬆開以後還在不在。

圖 (a) 比較統一的 PUE，和每個 datacenter 各自不同的 PUE。考慮真實 PUE 差異之後，Facility MILP 的 carbon savings 略為增加，SLO 幾乎沒有變化。

圖 (b) 改變不同地區 carbon intensity 的分散程度。CI 差距變大時，scheduler 有更大的空間，把 request 分到相對低碳的 datacenter。

- 怎麼指：先指左圖的空心和實心，再指右圖由左到右上升的線。百分比若被問到，再進 PUE and CI spread。
- 下一頁：排程器自己要花多少時間，以及狀態太舊時 SLO 會怎樣。

## Main 14 — Q4: How Important Are Polling, Overhead, and Topology?

- 預計：50 秒
- 論文：Section V-C，Figure 6
- 上一頁：碳的機會來自 CI 分散，這一頁看這個機會會不會被資訊延遲吃掉。

Figure 6 三塊一起看。右邊三句是讀圖，不是另一組實驗。

(a) 是 scheduler 在 CPU 上做決定的時間，不是 GPU 的 token 時間，也不是 TTFT。Greedy 不到 1 毫秒。Facility MILP 的 p99 到 0.5 秒。Iterative ILP 在 Llama 上的 p99 是 6.5 秒，因為一個 scheduler 上的求解在大約每秒 1000 筆時會飽和。

(b) 是狀態有多新鮮。Polling 在 2 秒以內，facility MILP 的 violation 最多 8.2%。拉到 5 秒，就升到 10.5% 到 32%。非同步 polling 沒有穩定地比同步好。

(c) 是拓樸，Llama、高負載。Scheduler 加倍、DC 不變，減碳差不多，violation 從 10.3% 到 19.4%，因為更多 scheduler 同時擠向同一批綠的 DC。DC 變少但每一個變大，violation 降到 4.1%，減碳也降到 23.2%，因為可以挑的綠站變少了。Engine 總數三種拓樸是一樣的。

- 怎麼指：先指 (a) 的橫軸是毫秒到秒，強調這不是 TTFT。再指 (b) 在 2 秒之後翹起來。(c) 只指星星往右上和往左下的兩步。
- 下一頁：真正上線時不知道輸出會多長。他們用一個小預測器試過。

## Main 15 — Q5: What If Output Length Is Unknown?

- 預計：45 秒
- 論文：Section IV 為什麼需要 OSL；Section V-C，Figure 7
- 上一頁：前面的主實驗用的是 oracle 輸出長度。這一頁問若沒有 oracle 會不會散掉。

排程需要 OSL，是因為 decode 的時間和能量都跟著輸出長度走。論文的例子是：輸出 100 個 token，大約比輸出 10 個 token 多佔用 engine 十倍。這是例子，不是說他們的平均輸出就是 100。

Figure 7(a) 空心是 oracle，實心是預測。預測是一個兩層 MLP 的中位數。它的 bucket 沒有很準，Llama 51%、Mixtral 37%，亂猜大約 17%；可是算上鄰近的 bucket，是 99% 和 70%。反映到結果上，減碳最多移動 1.3 和 4.1 個百分點，violation 最多上升 1.1 個百分點。例外是 Llama 上的 iterative ILP，它本身的求解時間就會讓結果晃。

(b) 是更長的 prompt。在 violation 大約 5% 的那個操作點，facility MILP 對長 prompt 還能省到 30%，對混合 prompt 省到 28%。圖的右上還有 violation 更高、減碳更多的點，那不是這句「大約 5%」的範圍。

- 怎麼指：(a) 看空心和實心幾乎疊在一起；(b) 看斜線區是 violation 小於 5% 的地方，不要把 cap 64 那個高 violation 點說成也只有 5%。
- 下一頁：不再重述貢獻。這一頁只講這篇沒做的，以及我們想接著做的。

## Main 16 — Limitations \& Future Work

- 預計：60 秒
- 論文：Section VI 的討論與限制
- 上一頁：實驗問題講完了。最後把論文的邊界和我們的方向分開。

左邊是這篇沒有處理的，右邊是我們提出的後續，不是 Topcu 等人已經驗證的結果。

碳帳只算 operational carbon。硬體的 embodied emissions 沒有放進去。不過他們的 operational energy model 很細，prefill、decode、idle GPU 和 host 都有。我們要沿用這一套，再補上 GPU、HBM、HBF 的 embodied carbon 和生命週期。

跨區 routing 和 RTT 已經有了。限制是每個 regional scheduler 只用自己 poll 到的 snapshot，看不到別的 scheduler 同時送出的指派，所以會一起湧向低 CI 的 datacenter。我們想做的是跨 scheduler 協調指派，或先保留容量。

硬體剖面是 A100。模型和 tensor parallel 有變，但沒有混用不同 GPU。我們要把 simulator 擴成混合的性能、功耗、記憶體容量，以及更大的異質叢集。

KV capacity 和 admission 已經有模型，不是忽略 KV Cache。沒有做的是 HBM/HBF 的儲存層，以及 attention 和 expert 的放置。我們的假設是 HBM 較多的 worker 放 attention 和 KV，HBF 較多的 worker 放 MoE expert weight，並把傳輸成本和能量算進去。這仍是研究假設。HBF 的延遲、頻寬、壽命和 embodied carbon 要另外建模和驗證。

- 怎麼指：由上到下四列。左邊是一整塊論文限制，右邊四塊是我們的方向。最後停在 Memory and placement。
- 下一頁：若沒有問題，停在這裡。問題再從頁腳進 Discussion Index。

## Backup 問答

教授若追問，用條列回答，不要把 Backup 整頁念完。

### B01 Table I

- 不要說六篇都忽略所有因素。Queue 那一欄，先前工作全是沒有；transfer 則是 SLIT、Green-LLM、GCOS、MARLIN 有，FREESH 和 MOER 沒有。
- 「負載無關的延遲」那句，Section I 點名的是粗時間尺度的 SLIT、Green-LLM、FREESH、MARLIN。MOER 和 GCOS 不是同一句話。
- GCOS 的延遲是 GPU job 的等待，不是 TTFT/TPOT。

### B02 碳與 SLO

- CI 是發電占比加權。論文引用的中位數：nuclear 和 solar 低於 50，天然氣 490，煤 820 gCO₂/kWh。這不是 16 個 DC 的表。
- \(P_{\mathrm{tot}}=P_{\mathrm{IT}}\times\mathrm{PUE}\)，跨 DC 再乘各站的 CI。
- Violation 是「TTFT 或 TPOT 任一超過」。主要門檻 3000 ms / 100 ms；Mixtral TPOT 200 ms；長 prompt 的 TTFT 才是 4500 ms。
- 沒有 embodied carbon，也沒有用品質換碳。

### B03 公式

- Prefill 時間：token 項是分段線性，加上固定成本、每筆 request 的成本，和 attention 的平方項。
- Decode 時間對 batch 是二次的，係數再隨平均 KV 長度線性變。
- 能量是另一組係數，不是功率模型直接乘一個常數時間。
- Decode 的 MAPE 比較難壓，是因為 step 只有幾十毫秒，溫度和頻率的暫態會出來。

### B04 驗證邊界

- 回放的是記錄下來的 engine、到達時間、輸入長度和真實輸出長度。容量基準是 27.58 req/s，掃描從這個容量的 7% 到 181%。
- 單 engine 和三 engine 在相同 per-engine load 下，TPOT 差 3.3%。
- 其他 GPU 會改變絕對延遲和絕對碳。作者預期排隊的現象還在，但沒有在別的 GPU 上展示。

### B05 Engine

- 每一步先送走完成的 request，再在 batch 上限和 KV 放得下時收新的。類似 vLLM 的 max_num_seqs 和 max_num_batched_tokens。
- Llama-3.1-8B 的例子是每個 token 128 KiB KV。Batch 上限：TP=1 是 40，TP=2 是 80，Mixtral 是 400。
- TTFT 估計含 RTT、等待和 prefill。TPOT 估計含「這筆 request 加入 batch」以及已經在跑的 prefill 佔用。

### B06 Greedy 與 ILP

- α=0 是 MOER。報告的是 0、0.5、0.9。
- 約束矩陣 totally unimodular，所以 LP relaxation 就是整數解。HiGHS，幾十毫秒。
- 解不開或放不進容量時，退回還有餘裕的最低 CI、且 SLO 可行的 DC；再不行就 RR。
- 主實驗用 oracle OSL。預測 OSL 只在 Figure 7。

### B07 MILP

- Iteration 更新的是 batch、queue、可行集合和能量。停在指派重複或 3 次。
- \(y_d\) 只多了 DC 個二元變數。論文說 0.25 秒限制內解得完。
- 它不關機房、不刪 RTT。Section VI 的 engine activator 只是觀察到很多 engine 閒著，沒有做出那個系統。

### B08 設定

- 四區：EU-North、US-East、Asia、South America。EU-North 的例子是 Netherlands、Belgium、Lithuania、Latvia。
- 一次實驗在一台 64-core server 上跑 200 秒。前 15 秒當暖機，九成以上時間在穩態。
- 負載標籤是 RR 之下的平均 batch 除以 batch 容量，不是用 req/s 直接跨模型比較。
- PDF 沒有說這 16 個 DC 被實體架設。

### B09 圖 5 到圖 7 的數字

- 日本那個例子是 CI 449–502，同時 PUE 1.32，所以 RR 被抬得比 carbon-aware 排程更兇。
- 26% 對 29.2%：Fig. 4(b) 的標籤和 PUE 段落的起點，PDF 沒有對帳。
- CV 的高負載低點，Llama 是 13%，在結論 26–60% 之外。
- OSL 預測準度不高，但鄰桶覆蓋高，所以 frontier 移動有限。Iterative ILP 在 Llama 上是例外。
- 30% 和 28% 是 violation 近 5% 的操作點，不是 Figure 7(b) 最右端。

### B10 限制與我們的方向

- 單輪、獨立 request。長 prompt 只壓到 KV 容量。多輪的 prefix 會把下一輪綁在持有 KV 的那個 DC，論文列為 future work。
- Facility MILP 下，Llama TP=1 的 engine 在低、中、高負載閒置 73%、56%、33%，RR 最多 10%。Idle 加 host 佔剩餘碳的 28% 到 81%。
- TP=2 讓 facility MILP 在高負載多 22% 的碳，SLO 也更差。那個比較裡他們偏好 data parallel。
- 我們的 HBM/HBF、heterogeneous GPU、attention/expert placement 不是他們的結果。
- 程式在 github.com/topcuburak/carbon-slo-at-geoscale。這次報告沒有重跑。

### B11 Figure 1：逐步延遲

- 這張是論文 Figure 1 原圖，不是重畫的曲線。主動報告不講這頁；被問到「延遲為什麼不能當常數」再開。
- Prefill 在短 prompt 幾乎是平的，之後才跟著總 prefill token 上升。所以 TTFT 沒有一個固定值。
- Decode 的 step latency 看 Batch Size 和 KV Cache。飽和之後會陡升。
- Held-out 的 per-step MAPE：dense Prefill 在 1.7% 以內，Mixtral Prefill 是 4.8%，Decode 在 3.4% 以內。這是逐步模型的誤差，不是整個跨區 simulator 的 end-to-end TTFT／TPOT。
- 多項式在 B03。這裡不要把逐步 MAPE 說成 16 個資料中心已經被硬體驗證。

### B12 Figure 2：逐步功率與能量

- 這張是論文 Figure 2 原圖。曲線是 per-GPU Power，不是整台 engine 的總功率。
- Prefill 的 Power 會靠近 A100 的 400 W TDP。TDP 是裝置上限，不是每個 step 都量到的固定功耗。
- Decode 的 Power 跟著 Batch Size 變，大批次大約到 TDP 的 95%。
- Energy 是平均 Power 乘上 step 時間。Power 和 Energy 不是同一個量。Idle 大約每張 A100 72 W，host 300 W，都要留在 operational energy 裡。
- Held-out step-energy MAPE 在 5.6% 以內。這仍是逐步能量的檢查，不能拿來宣稱整個 geo-distributed simulator 已被驗證。

### B13 最低 CI 站不一定可行

- 這是壅塞的概念示意，不是量測 trace，也不是低 CI 必然造成高延遲。主動報告不開這頁。
- 較低的 CI 是減碳機會。Queue、batch 變大，加上遠端 RTT，可能把 TTFT 和 TPOT 拉過 SLO。
- 所以 CI 最低的站，不一定是還符合 SLO 的 routing 決定。

