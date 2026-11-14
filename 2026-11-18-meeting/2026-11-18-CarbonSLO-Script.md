# 2026-11-18 Carbon–SLO 報告講稿

主動報告只走 Main。Backup 留給教授追問。

總時間 **15 分 50 秒**（950 秒）。時間是照著講的目標，不是每句都要念完；若前面超時，Q3 到 Q5 各收 10 秒，結論仍要留下「這不是作者已經做完的系統」。

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

TPOT 的印刷式是 decode step 加上一項分數。B 加 1 表示這筆 request 加入投影的 batch，KV 是當下的 occupancy。分子裡的 T pre 是還在 queue 的 prefill，攤到輸出長度上。論文把 1 減 duty 只放在這一項的分母。下一句又說這個因子對應已經在跑的 prefill。所以不要把 duty 和 queued prefill 說成同一個量，也不要把整個式子改寫成一個大分數。

- 怎麼指：先指上面的流程，再指 TTFT，再指 TPOT。符號細節點進 B05。
- 下一頁：先看這篇最主要的排程方法，Facility MILP，怎麼處理共享的 step energy。

## Main 07 — How Does Facility MILP Account for Shared Batch Energy?

- 預計：70 秒
- 論文：Section IV-C
- 上一頁：SLO 的估計講完了。這一頁直接講主要方法，不先從 Greedy 講起。

同一個 inference batch 裡的 request，會共用 engine 某一次 step 的一部分能量。那一份能量有固定的部分，也有跟著負載走的部分。如果每筆 request 都付一次完整成本，固定的那一份就被算了兩次。

左邊是示意，不是論文裡的一組瓦特數。加成法是 A 付固定成本加自己的邊際，B 再付一次固定成本。Facility 的記法是固定成本只收一次，再加上各自的邊際。這不是說這些 request 共用了全部的 attention，也不是 KV cache 的重用。

右邊是目標。x 是 request 指派到哪個 DC。y 表示這個 window 有沒有用到那個 DC。c 是邊際碳成本，f 是共享的那一份碳。容量限制乘上 y，所以沒用到的 DC 不會被分到 request。

請把限制念完。它沒有把資料中心斷電，也沒有把 RTT 拿掉。它不是先跑 Iterative ILP 再解一次 MILP。可行性是估計出來的，request 仍可能真的違反 SLO。作者的評估裡，它是整體 carbon–SLO 較好的選項，不是每一個 workload 的最優解。

- 怎麼指：先指左邊兩張卡的固定成本，再指右邊的 f_d y_d。不要把 y 等於 0 說成機房關機。
- 下一頁：另外三種政策各自補了什麼，又留下什麼。

## Main 08 — How Do the Other Scheduling Policies Differ?

- 預計：70 秒
- 論文：Section IV-A 到 IV-C
- 上一頁：Facility MILP 已經說明共享能量怎麼只收一次。這一頁用它當對照，看另外三種方法。

Greedy 一筆一筆決定。它先留下估計上 TTFT 和 TPOT 都過得了的 DC，再用 α 把歸一化後的延遲和 CI 加起來。歸一化是除以這個可行集合的最大值。α 等於 0 只看 CI，論文說這和 MOER 一樣。它不是在最小化全系統的 energy 乘上 CI。同一個 snapshot 上，沒有協調的 request 會擠到同一個站。

Standard ILP 把一個 window 一起指派，最小化各筆的估計碳成本。每一筆一個 DC，而且要落在預測的可行集合和剩餘容量裡。可是這一次求解裡，負載和成本是凍結的。

Iterative ILP 解完就把指派投影回 batch 和 queue，重算 TTFT 和 TPOT，再解。指派重複，或做滿 3 次，就停。它補的是負載估計，能量仍然是各筆相加，而且 solver 時間會增加。

這三個不是一層一定比上一層好。Facility MILP 也不是在這個迭代迴圈後面再加一次。它處理的是共享 batch 能量，前一頁已經講過。

- 怎麼指：三張卡由左到右。最後一句回到 Facility MILP 是另一個政策。
- 下一頁：這些估計和排程是建在什麼測量上，驗證到哪裡為止。

## Main 09 — Can We Trust the Geo-Distributed Simulator?

- 預計：70 秒
- 論文：Section V-B；限制在 Section VI。逐步擬合在 Section III-B，不跟這裡的百分比混在一起
- 上一頁：另外三種政策和 Facility MILP 的差別講完了。實驗數字之前，先分清楚哪一層是量到的。

分成三層。A，在 A100-40GB、vLLM 0.6.3、FP16 上量延遲和功率。B，每個模型、每種 tensor parallel，各配一組 prefill 和 decode 的延遲與能量。C，跨區模擬：routing、queue、continuous batching、RTT、多個 region 和 CI。這一層不是再做一次硬體實驗。

Within-node 的對照只做 Llama-3.1-8B。三個 data-parallel 的 vLLM engine，19 個 arrival rate，超過四萬筆 request。TTFT 整體平均誤差 9.1%，TPOT 平均誤差低於 5%，GPU energy 和量測差在 2.5% 以內。飽和附近的 TTFT 平均誤差升到 28.5%，而且是偏高估。這是端到端的 within-node 誤差。逐步的 1.7%、3.4%、5.6% 留在公式頁，不要加進 9.1%。

請把邊界念完。驗證對的是單節點 serving 的量測，不是 16 個實體資料中心已經部署。跨區的減碳結果是模擬。

- 怎麼指：三張卡片很快帶過，數字停在中間藍卡，28.5% 和單節點邊界停在紫卡。
- 下一頁：實驗比的是哪些模型、負載、SLO 和 baseline。

## Main 10 — How Is the System Evaluated?

- 預計：55 秒
- 論文：Section V-A，Table II
- 上一頁：驗證的邊界講完了。這一頁只說明實驗在比什麼，不再重講校準。

左邊兩個是 dense：Llama-3.1-8B 和 Qwen2.5-7B，TP 等於 1。右邊是 MoE：Mixtral-8x7B，8 個 expert 裡每次 top-2，TP 等於 4。因為 TP=4，Mixtral 每個 DC 的 engine 數只有 dense 的四分之一。低、中、高負載不能直接拿 req/s 互比：7B 和 8B 是 1200、2400、4000；Mixtral 是 800、1200、2000。

拓樸是 4 個區域 scheduler 乘 4 個 DC，一共 16 個模擬的 DC。SLO 是 TTFT 3 秒；dense 的 TPOT 是 100 毫秒，Mixtral 是 200 毫秒。

不會看碳的 baseline 是 round-robin 和 least-loaded。會看碳的是 Green-LLM，以及 MOER，也就是 α 等於 0 的 greedy。指標是含 idle 和 host 的 operational carbon、SLO violation rate，再加上 TTFT 的 p50、p90、p99。Violation rate 不是平均延遲，也不是 throughput。

- 怎麼指：表格的 Dense / MoE 兩欄，再指 baseline 和指標，最後停在 Takeaway。
- 下一頁：全篇最重要的結果圖，Figure 4(a)。

## Main 11 — Q1: Can Carbon Be Reduced Without Excessive SLO Violations?

- 預計：85 秒
- 論文：Abstract；Section V-C，Figure 4(a)
- 上一頁：設定講完，這一頁回答減碳會不會把 SLO 打穿。

這是 Figure 4(a)。橫軸是沒過 TTFT 或沒過 TPOT 的 request 比例，縱軸是相對 round-robin 的減碳。左邊是中負載，右邊是高負載。星星是 facility MILP，倒三角是只看碳的 greedy，也就是 MOER。

看形狀就好。Facility MILP 多半留在左邊、減碳仍高的位置。只看碳的 greedy 可以有差不多的減碳，但是橫軸會被拉得很遠，尤其是 Mixtral。

數字請分開講。摘要的 up to 60%，和平均 3% 的 SLO violation，是作者相對 RR 的總結，不是圖上每一個點的座標。低負載這張圖沒畫：那裡 facility MILP 是 53.8% 到 59.6%，對得上「最多約 60%」。最激進的 greedy 可以到 55% 的 violation；那不是 α 等於 0.9。α 等於 0.9 幾乎不減碳。中負載、α 等於 0 的時候，dense 大約到 6.9%，Mixtral 到 44.8%，這兩個也不是 55%。

高負載時綠的 DC 會飽和，減碳空間收到大約 32% 到 38%。所以 60% 不要從右邊這張高負載圖上讀出來。

- 怎麼指：先指兩軸和星星，再指高負載最右邊的點，最後念「How to read the claim」。
- 下一頁：violation rate 看不出尾巴。Figure 4(b) 把高負載的 TTFT 百分位拆開，而且圖上的百分比不是延遲。

## Main 12 — Q2: What Happens to Tail Latency Under High Load?

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

左邊是高負載的 PUE。空心是大家都用 1.1，實心是各 DC 用公開的 PUE，大約 1.08 到 1.32。Facility MILP 在 Llama 上從 29.2% 移到 30.5%，Mixtral 從 36.6% 移到 38.7%。SLO 幾乎不動。PUE 主要是在重算每一度電的碳，不是在改 request 會不會排隊。

這裡有一個不要混的數字。Figure 4(b) 把 Llama 高負載的 facility MILP 標成 26%，這段正文的起點卻是 29.2%。論文沒有解釋這兩個數為什麼不同，所以我兩組都留著，不把它們平均。

右邊是 CI 的分散，係數是各 DC 的標準差除以平均。從最低的 CV 0.31 到最高的 0.94，減碳上升，SLO 不變。負載越高，曲線越低。可是 spread 很大的時候，高負載仍然可以到 39% 到 45%。反過來說，Llama 在高負載、最低 CV 只有 13%，這已經在結論那句 26% 到 60% 的外面。

- 怎麼指：左圖看實心點略為上移，右圖看三條線由左下到右上，High 那條最低。13% 用口頭講，不必在圖上找一個沒標數字的點。
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
- 下一頁：四層結論。最後一層要把「我們想做的」和「他們做完的」分開。

## Main 16 — Conclusion

- 預計：50 秒
- 論文：Section VI 與 Section VIII
- 上一頁：五個實驗問題都回答過了，收成四句。

第一，問題是：把 request 送去 CI 較低的資料中心，TTFT 和 TPOT 會跟著排隊、batch 和 RTT 一起變。

第二，他們做了一個在單節點上校準過的跨區 simulator，以及四種排程。Facility MILP 的差別是共享 batch 的能量只算一次，不是把每筆 request 的碳加總。

第三，相對 round-robin，作者報告最多少 60% 的 operational carbon，平均 SLO violation 是 3%。減碳跟著 CI 的分散變大，跟著負載變小，而 SLO 看狀態更新得夠不夠勤。26% 到 60% 是結論對 base setting、跨負載的摘要；剛才 Figure 5 已經看到，換一個 CI 小時可以落到這個區間外面。

第四，這篇做完的是 simulator 和排程實驗。還沒做的是多輪對話的 KV locality，以及異質硬體。我們之後若做 heterogeneous GPU、HBM/HBF、attention 和 expert 的放置，以及跨 DC 的 carbon-aware serving，那是我們的方向，不是這篇論文的結果。

- 怎麼指：四張卡片由上到下。第四張的「not an author result」要留在最後一句。
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

