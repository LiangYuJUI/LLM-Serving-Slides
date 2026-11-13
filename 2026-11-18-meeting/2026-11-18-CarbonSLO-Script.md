# 2026-11-18 Carbon–SLO 報告講稿

主動報告只走 Main。Backup 留給教授追問。

總時間 **19 分 05 秒**（1145 秒）。時間是照著講的目標，不是每句都要念完；若前面超時，Q3 到 Q5 各收 10 秒，結論仍要留下「這不是作者已經做完的系統」。

技術詞 TTFT、TPOT、SLO、PUE、RTT、MILP、ILP、CI、KV、continuous batching 保留英文。

## Main 01 — Carbon–SLO at Geo-Scale

- 預計：20 秒
- 論文：封面；arXiv:2610.14571，2026-10-10
- 上一頁：無。這是開場。

老師好。今天報告 Penn State 的 Topcu、Cim、Ozturk 和 Kandemir 這篇 preprint，題目是 Dissecting the Carbon–SLO Tension in Geo-Distributed LLM Serving。它問的是：把 request 送到比較綠的資料中心，能不能在 TTFT 和 TPOT 的 SLO 底下真的減碳。

- 怎麼指：停在標題和作者。
- 下一頁：先介紹這篇做出的 simulator、scheduler 與實驗結果。

## Main 02 — What Does This Paper Do?

- 預計：65 秒
- 論文：Abstract；Section I 的三項 contribution
- 上一頁：從題目進到他們真正交付的東西。

這篇做三件事。第一，他們做了一個跨地區的 LLM serving simulator，延遲和功率是用 A100 上的 vLLM 量出來再擬合的。第二，他們比較四種愈來愈細的 carbon-aware、SLO-aware 排程，從單筆 request 的 greedy，到會看一整個 batch 的 facility MILP。第三，他們在三個模型、不同負載，以及會看碳和不會看碳的 baseline 上，畫出 carbon 和 SLO 的取捨。

中間這張卡片是摘要裡的總結，比較基準是 round-robin。Facility MILP 最多可以少掉 60% 的 operational carbon，作者給的平均 SLO violation 是 3%。這兩個數字不要黏在一起聽。60% 是上界，3% 是平均，不是每一個負載都只違規 3%。

Takeaway 是：決定 request 去哪個資料中心，會同時改到用電碳排和 token 延遲。CI 最低的站，不一定是還過得了 SLO 的站。

- 怎麼指：先指標題下的 simulator 副標題，再由左到右說明 Schedulers 和 Frontier，接著指中間的 60% 和 3%，最後停在 Takeaway。operational carbon 和 three models 可以點進 Backup。
- 下一頁：用 Table I 說明這篇涵蓋了哪些更完整的 serving 因素。

## Main 03 — Table I: Scope of Prior Work and This Paper

- 預計：60 秒
- 論文：Section I，Table I
- 上一頁：看完這篇的三項貢獻，再用 Table I 說明它與既有工作的差異。

先看這張 Table I。這篇的重點，是把跨資料中心 LLM serving 的問題考慮得更全面。表格左邊是各篇工作的排程粒度與延遲目標，中間四欄比較 batch-aware latency、power、queueing 和跨區 transfer，最後一欄是它們報告的延遲指標。

看最下面綠色這一列，這篇同時納入 batch 對延遲與功率的影響、engine 裡的排隊，以及跨區傳輸延遲，並用 TTFT、TPOT 對照 MLPerf 的 SLO。這些因素會一起影響 request 能不能送到低碳的資料中心，所以需要放在同一個模型裡評估。

這裡不要解讀成過去的工作全部都沒考慮：有幾篇已經納入 transfer，MOER 的 power 是部分建模，GCOS 的 batch-aware latency 則是不適用。這篇的差別在於把表中這些面向整合起來。

- 怎麼指：先指中間四個比較欄位，再沿著綠色的 This paper 那一列說明；不用逐篇念完。
- 下一頁：為什麼不能永遠選最綠的站。

## Main 04 — Why Not Always Choose the Greenest Datacenter?

- 預計：70 秒
- 論文：Section I 對 spatial scheduling 的動機；Section II 的 CI 變化
- 上一頁：摘要說最低 CI 不一定可行，這一頁解釋那個張力。

這張圖是概念示意圖，不是他們量到的曲線。Request 先到區域 scheduler。它可以留在本地，CI 比較高，但是排隊短；也可以送到 CI 最低的資料中心，可是那一跳要付 RTT，而且大家若都這樣送，queue 和 batch 會在綠的站長出來。

論文說 grid 的 carbon intensity 在地區之間、時間之間可以差一個數量級以上。所以把流量送去低 CI 的電網，確實有減碳空間。代價是排隊會拉長 TTFT，decode batch 變大會拉長 TPOT，跨區還要再加網路 RTT。

所以最低 CI 和「還符合 SLO 的指派」是兩個決定。後面的 simulator 就是要把 queue、batch 和 RTT 算進去，而不是只看一張 CI 地圖。

- 怎麼指：從左到右跟著箭頭。上面紫色是低 CI、會擠的站，下面綠色是 CI 較高但排隊較短的站。強調圖上的字是示意。
- 下一頁：既有的跨區排程少算了什麼。不要說每一篇都少同一件事。

## Main 05 — What Do Previous Approaches Miss?

- 預計：60 秒
- 論文：Section I 與 Table I
- 上一頁：動機有了，接著說明這個缺口為什麼還在。

Table I 放了六個 carbon-aware 的跨區排程，和這篇對照。缺口不是每一列都一樣。

左邊上面：SLIT、Green-LLM、FREESH、MARLIN 多半用 15 分鐘到 1 小時的粗計畫，而且把延遲當成跟當下 batch 無關。MOER 是一筆 request 決定一次，但它根本沒有 latency target。左邊下面：沒有一篇把 prefill 和 decode 的功率完整建模；MOER 在功率那一欄是 partial，其他是沒有。

右邊上面：沒有一篇建模「KV 或 batch 位子不夠時，engine 裡的排隊」。轉送延遲則是有人有、有人沒有，FREESH 和 MOER 沒有，另外幾篇有。右邊下面：他們的延遲目標多半是自己定的，例如平均 TTFT、5 秒的 end-to-end，或是 job 的等待時間。這篇用的是 TTFT 和 TPOT，並且對到 MLPerf 的 budget。

Takeaway：缺的是會跟著負載變的 TTFT 和 TPOT，以及一個有 benchmark 根據的 SLO，不是再多一個碳的訊號。

- 怎麼指：Table I 四個色塊依序。若被問某一列，開 B01，不要在這一頁把六篇都念完。
- 下一頁：把這篇自己的問題寫成一個決定、一個碳、兩個延遲。

## Main 06 — What Is the Carbon–SLO Scheduling Problem?

- 預計：55 秒
- 論文：Section II；Section III-A；Table II 的 budget
- 上一頁：缺口是 token SLO，這一頁定義他們到底在優化什麼。

決策只有一個：這筆 request 送到哪一個 datacenter。不是把 layer、KV cache 或 MoE expert 搬去另一個站。

上面的式子是總 operational carbon，每個 DC 的能量乘上那個 DC 的 CI。能量再乘上那個站的 PUE。一個 DC 共用一個 PUE、一個 CI，因為機房共用電網和冷卻。這是 Scope 2 的用電排放。這篇不優化 embodied carbon，也不拿輸出品質去換碳。

SLO 的定義要講清楚。一筆 request 只要 TTFT 或 TPOT 有一個超過門檻，就算 violation。主要實驗的門檻是 3 秒和 100 毫秒；Mixtral 的 TPOT 是 200 毫秒。MLPerf 單機的 TTFT 原本是 2 秒，他們只因為跨區轉送把 TTFT 放寬，TPOT 沒有放。

- 怎麼指：先指決策那一句，再指公式，然後左右兩張卡片。either 這個字要停一下。
- 下一頁：這個問題是在什麼 simulator 裡評估的。

## Main 07 — How Does the Geo-Distributed Simulator Work?

- 預計：75 秒
- 論文：Section III-C，Figure 3；Section III-A 的 polling 欄位
- 上一頁：問題定義完了，開始看他們用什麼系統來回答。

Figure 3 是這一頁的主圖，caption 是論文原圖的。路徑照圖上的編號。1，load generator 用 Poisson 把 request 送到區域 scheduler。2 和 3，scheduler 可以留在本地，或轉給別區；轉出去就要付 RTT，再由對方的 scheduler 放上目標 DC。4 和 5，provisioner 週期性地跟每個 DC 要狀態，再把這份 snapshot 和 RTT 矩陣廣播給所有 scheduler。

DC 裡面，node 之間和 node 裡面都是 round-robin。所以論文把測到的減碳歸給區域排程，不是歸給 DC 內部的放置。Engine 跑的是 continuous batching：有空的 batch 位子、KV 也放得下，才把 request 從 queue 收進來。Queue 的長度不是一個常數。

Scheduler 看得到的，是每個 DC 平均過的 batch size、queue 深度、KV 佔用、prefill duty，再加上 CI。

- 怎麼指：左手指著圖上的 1 到 5，右手對應三小段。最後一句停在 Takeaway 的四個狀態。
- 下一頁：TTFT 和 TPOT 為什麼不能做成常數。

## Main 08 — How Is LLM Serving Latency Modeled?

- 預計：55 秒
- 論文：Section III-B，Figure 1
- 上一頁：simulator 會問每個 DC 的延遲，這一頁是那個延遲從哪裡來。

Figure 1 有三塊。左邊 prefill：prompt 還短的時候幾乎是平的，過了 knee 之後大致跟 prefill token 數一起長。所以 TTFT 不能查一張固定表。中間 decode：batch 變大時先是次線性，飽和之後會陡起來，而且 KV context 越長越慢。右邊是 held-out 的誤差。這是 A100、vLLM 量測擬合的解析模型。Dense 的 prefill MAPE 在 1.7% 以內，Mixtral prefill 是 4.8%，decode 在 3.4% 以內。

係數沒有放在這頁，Backup 有完整的多項式。這裡只要記住：TTFT 和 TPOT 跟著當下的 batch、queue 和 context 走。排程若把延遲當常數，綠的站和忙的站會排錯。

- 怎麼指：由左至右 (a)(b)(c)。不必讀 legend 裡每一條線，點出「平、再上升」和「飽和後變陡」。
- 下一頁：同樣的兩階段，功率長得不一樣，所以能量也不能只用延遲代替。

## Main 09 — How Are Power and Energy Modeled?

- 預計：50 秒
- 論文：Section III-B，Figure 2
- 上一頁：延遲會隨負載變，碳排還要再乘功率。

Figure 2 的左邊是 prefill。Prompt 一長，功率很快頂到 A100 的 TDP，圖上那條線是 400 W。右邊是 decode，功率跟著 batch size 往上走，對負載敏感得多。能量是這一段的平均功率乘上這一段的時間。一段又快又高功率的 prefill，和一段比較長、功率沒那麼高的 decode，碳排不一樣。

另外兩個不能省略的底：模型載好但沒有 request 時，一張 A100 大約還有 72 W；每個 node 的 host 他們設成 300 W。閒置的 GPU 不是零碳。

Takeaway：carbon-aware 排程若忽略 phase 和 batch，會把資料中心的碳價排錯。

- 怎麼指：左圖指 TDP 和 idle，右圖指 decode 隨 batch 上升。72 W 和 300 W 在右邊第三點。
- 下一頁：這些模型跟真的 GPU 對過沒有。教授若只記一頁，請停在驗證邊界。

## Main 10 — Real GPUs or a Simulator? How Is It Validated?

- 預計：70 秒
- 論文：Section V-B；限制在 Section VI
- 上一頁：模型看起來合理，這一頁分清楚哪一層是量到的、哪一層是模擬的。

分成三層。A，真的硬體：A100-40GB、vLLM 0.6.3、FP16，延遲和功率是在這張 GPU 上 profile 的。B，解析擬合：每個模型、每種 tensor parallel，各配一組 prefill 和 decode 的延遲與能量。C，跨區模擬：很多 region、scheduler、queue、RTT 和碳。這一層不是再做一次硬體實驗。

他們有做 within-node 的端到端對照，而且只對 Llama-3.1-8B。三個 data-parallel 的 vLLM engine，19 個 arrival rate，超過四萬筆 request。TPOT 平均誤差低於 5%，TTFT 整體平均誤差 9.1%，GPU energy 和量測差在 2.5% 以內。TTFT 不是全程都是 9.1%：低於飽和 3.5%，overload 5.2%，飽和附近 28.5%，而且是偏高估。

下面紫色的限制請直接念。這是單節點的 inference serving。它不是 16 個實體資料中心已經部署完成的驗證。Mixtral 用 TP=4 時，一個 engine 就佔滿他們那台四張 GPU 的機器，所以 Mixtral 沒有同樣的多 engine 對照。

- 怎麼指：三張卡片很快帶過，數字停在中間藍卡，限制停在紫卡。不要把 2.5% 說成 16 個 DC 的碳排誤差。
- 下一頁：在這個 simulator 上，他們放了哪四種排程。

## Main 11 — Which Scheduling Policies Are Proposed?

- 預計：50 秒
- 論文：Section IV 開頭
- 上一頁：工具可信的範圍講完了，開始看政策本身。

四種政策共用同一個 TTFT、TPOT 估計。差在一次決定幾筆 request，以及 batch 的能量怎麼算。

Greedy 一筆一筆決定，只看當下 snapshot，能量不共享。Standard ILP 對一個 window 做一次聯合指派，但是這一次求解裡負載是凍結的，碳是各筆 request 加總。Iterative ILP 同一個 window 最多重解 3 次，每次把指派投影回 batch 和 queue。Facility MILP 多一個位元，記錄這個 window 有沒有用到該 DC，啟動成本只收一次。

Greedy 的 α 等於 0 就是只看碳，論文說這和 MOER 的決定一樣。他們報告 0、0.5 和 0.9。α 等於 1 會是只看延遲，實驗沒有把 1 放進表。

這四層不是把 ILP 越寫越大。每一層是在補上一層的一個洞：沒有協調、負載估計過期、然後 batch 的固定能量被算了兩次。

- 怎麼指：表格由上到下。α=0 那一行單獨停一下，因為後面圖裡的 MOER 就是它。
- 下一頁：前兩層的公式，只放教授需要看的那一層。

## Main 12 — How Do Greedy and Standard ILP Work?

- 預計：55 秒
- 論文：Section IV-A，Equation (1)；Section IV-B，Equation (2)
- 上一頁：表格有了，這一頁解釋前兩格為什麼不夠。

Greedy 先丟掉過不了 SLO 的 DC，再在剩下的裡面算分數：α 乘正規化延遲，加上 1 減 α 乘正規化 CI。延遲是 TTFT 加上輸出長度乘 TPOT。正規化是除以可行 DC 裡的最大值。分數最低的 DC 收下這筆 request。

它的弱點是同一個 polling 週期裡的 request 會擠向同一站，而各區 scheduler 還看同一份 snapshot，所以一起把那個站推過 SLO。

右邊的 Standard ILP 是把一個 window 裡的 request 一起分配。每筆 request 恰好去一個 DC，每個 DC 收到的筆數不能超過剩下的 batch 位子。單筆的碳是 PUE 乘能量乘 CI。關鍵是：這一解裡面，剩多少位子、延遲估出來是多少，都用解之前的狀態，不會隨著這一窗的指派更新。所以每一筆單獨看都可行的 DC，合在一起仍可能爆掉。

Window 是 100 毫秒，或滿 300 筆就先解。完整的式子和 totally unimodular 那一句在 Backup。

- 怎麼指：左卡的分數，右卡的三個條件。Takeaway 的「frozen」對應右卡最後一句。
- 下一頁：後兩層改的就是這個凍結，以及能量被重複計算。

## Main 13 — Why Iterative ILP and Facility MILP?

- 預計：65 秒
- 論文：Section IV-B 與 IV-C
- 上一頁：Standard ILP 的負載是凍結的，這一頁是他們怎麼補。

Iterative ILP 解完一次，就把這個 window 的指派寫回每個 DC 的 batch 和 queue，重算 TTFT 和 TPOT，再解。指派不再變，或做滿 3 次，就停。它補的是負載耦合。碳的算法還是各筆相加。

Facility MILP 改的是能量。如果這個 window 有任何一筆 request 用到某個 DC，就付一次啟動碳 \(f_d\)，request 自己只付邊際能量。式子裡的 \(y_d\) 就是「這個 window 用不用這個 DC」。兩筆 request 若共用一個原本閒置的 engine，固定的那一份 step energy 只收一次，不會收兩次。

請把 Takeaway 念完。它改的是共享 batch 的能量帳。它沒有把資料中心關機，也沒有把 RTT 拿掉。RTT 仍然在 TTFT 的估計裡。

- 怎麼指：左右兩張卡，然後中間的式子只指 \(f_d y_d\) 和 \(H_d y_d\)。不要說 \(y_d=0\) 代表機房斷電。
- 下一頁：這些政策是在什麼設定上比的。先把「16 個 DC 是模擬」講清楚。

## Main 14 — How Is the System Evaluated?

- 預計：50 秒
- 論文：Section V-A，Table II
- 上一頁：方法講完，實驗設定要先把 dense 和 MoE 分開。

左邊兩個是 dense：Llama-3.1-8B 和 Qwen2.5-7B，TP 等於 1。右邊是 MoE：Mixtral-8x7B，8 個 expert 裡每次 top-2，TP 等於 4。因為 TP=4，Mixtral 每個 DC 的 engine 數只有 dense 的四分之一。到達率也不能直接比：7B 和 8B 的低、中、高是 1200、2400、4000 req/s；Mixtral 是 800、1200、2000。

拓樸是 4 個區域 scheduler 乘 4 個 DC，一共 16 個 DC。RTT 是 85 到 280 毫秒，預設 PUE 1.1。CI 用 Electricity Maps 的一個小時，一次實驗裡保持不變。

不會看碳的 baseline 是 round-robin 和 least-loaded。會看碳的是 Green-LLM，以及 MOER，也就是 α 等於 0 的 greedy。指標是含 idle 和 host 的 operational carbon、SLO violation，再加上 TTFT 的 p50、p90、p99，因為 violation rate 看不出尾巴有多嚴重。

Takeaway 要留下：這 16 個 DC 是一台伺服器上的模擬角色，不是 16 個已經架好的機房。

- 怎麼指：表格的 Dense / MoE 兩欄，再指 Takeaway。
- 下一頁：全篇最重要的結果圖，Figure 4(a)。

## Main 15 — Q1: Can Carbon Be Reduced Without Excessive SLO Violations?

- 預計：85 秒
- 論文：Abstract；Section V-C，Figure 4(a)
- 上一頁：設定講完，這一頁回答減碳會不會把 SLO 打穿。

這是 Figure 4(a)。橫軸是沒過 TTFT 或沒過 TPOT 的 request 比例，縱軸是相對 round-robin 的減碳。左邊是中負載，右邊是高負載。星星是 facility MILP，倒三角是只看碳的 greedy，也就是 MOER。

看形狀就好。Facility MILP 多半留在左邊、減碳仍高的位置。只看碳的 greedy 可以有差不多的減碳，但是橫軸會被拉得很遠，尤其是 Mixtral。

數字請分開講。摘要的 up to 60%，和平均 3% 的 SLO violation，是作者相對 RR 的總結，不是圖上每一個點的座標。低負載這張圖沒畫：那裡 facility MILP 是 53.8% 到 59.6%，對得上「最多約 60%」。最激進的 greedy 可以到 55% 的 violation；那不是 α 等於 0.9。α 等於 0.9 幾乎不減碳。中負載、α 等於 0 的時候，dense 大約到 6.9%，Mixtral 到 44.8%，這兩個也不是 55%。

高負載時綠的 DC 會飽和，減碳空間收到大約 32% 到 38%。所以 60% 不要從右邊這張高負載圖上讀出來。

- 怎麼指：先指兩軸和星星，再指高負載最右邊的點，最後念「How to read the claim」。
- 下一頁：violation rate 看不出尾巴。Figure 4(b) 把高負載的 TTFT 百分位拆開，而且圖上的百分比不是延遲。

## Main 16 — Q2: What Happens to Tail Latency Under High Load?

- 預計：60 秒
- 論文：Section V-C，Figure 4(b)
- 上一頁：上一頁是違規比例，這一頁是高負載時 TTFT 的尾巴。

Figure 4(b) 只有高負載。橫條是 TTFT，從 p50 到 p99，中間刻度是 p50 和 p90。條旁邊印的百分比是相對 RR 的減碳，不是秒數。這件事要先講，不然 26%、35% 會被聽成延遲。

Dense 模型上，greedy 的 p99 TTFT 還在 3 秒預算裡。可是 α 等於 0 仍然違規，違的是 TPOT：decode batch 堆在最綠的 DC 上。所以 TTFT 的尾巴沒爆，不代表 SLO 過了。

Mixtral 不一樣。它的 engine 少、輸出比較長。α 等於 0 的 greedy 把中位數 TTFT 推到 3.3 秒。ILP 和 MILP 把中位數留在 0.7 秒以內，p99 留在 2.2 秒以內。激進的 greedy 和 Green-LLM，p99 可以到 8.8 秒。Iterative ILP 在 dense 上的 p99 會到 7.5 秒，那是反覆求解的開銷，不是 GPU 算得比較慢。

- 怎麼指：先指一條橫條上的百分號，說明那是碳。再指 Llama 上 greedy 的短條，和 Mixtral 上 greedy 拉到很右邊的長條。
- 下一頁：減碳空間從哪裡來。PUE 和 CI 的分散是兩件不同的事。

## Main 17 — Q3: How Do PUE and Carbon-Intensity Spread Affect Savings?

- 預計：55 秒
- 論文：Section V-C，Figure 5
- 上一頁：主結果是在預設 PUE 和一個 CI 小時上。這一頁看這兩個假設鬆開以後還在不在。

左邊是高負載的 PUE。空心是大家都用 1.1，實心是各 DC 用公開的 PUE，大約 1.08 到 1.32。Facility MILP 在 Llama 上從 29.2% 移到 30.5%，Mixtral 從 36.6% 移到 38.7%。SLO 幾乎不動。PUE 主要是在重算每一度電的碳，不是在改 request 會不會排隊。

這裡有一個不要混的數字。Figure 4(b) 把 Llama 高負載的 facility MILP 標成 26%，這段正文的起點卻是 29.2%。論文沒有解釋這兩個數為什麼不同，所以我兩組都留著，不把它們平均。

右邊是 CI 的分散，係數是各 DC 的標準差除以平均。從最低的 CV 0.31 到最高的 0.94，減碳上升，SLO 不變。負載越高，曲線越低。可是 spread 很大的時候，高負載仍然可以到 39% 到 45%。反過來說，Llama 在高負載、最低 CV 只有 13%，這已經在結論那句 26% 到 60% 的外面。

- 怎麼指：左圖看實心點略為上移，右圖看三條線由左下到右上，High 那條最低。13% 用口頭講，不必在圖上找一個沒標數字的點。
- 下一頁：排程器自己要花多少時間，以及狀態太舊時 SLO 會怎樣。

## Main 18 — Q4: How Important Are Polling, Overhead, and Topology?

- 預計：50 秒
- 論文：Section V-C，Figure 6
- 上一頁：碳的機會來自 CI 分散，這一頁看這個機會會不會被資訊延遲吃掉。

Figure 6 三塊一起看。右邊三句是讀圖，不是另一組實驗。

(a) 是 scheduler 在 CPU 上做決定的時間，不是 GPU 的 token 時間，也不是 TTFT。Greedy 不到 1 毫秒。Facility MILP 的 p99 到 0.5 秒。Iterative ILP 在 Llama 上的 p99 是 6.5 秒，因為一個 scheduler 上的求解在大約每秒 1000 筆時會飽和。

(b) 是狀態有多新鮮。Polling 在 2 秒以內，facility MILP 的 violation 最多 8.2%。拉到 5 秒，就升到 10.5% 到 32%。非同步 polling 沒有穩定地比同步好。

(c) 是拓樸，Llama、高負載。Scheduler 加倍、DC 不變，減碳差不多，violation 從 10.3% 到 19.4%，因為更多 scheduler 同時擠向同一批綠的 DC。DC 變少但每一個變大，violation 降到 4.1%，減碳也降到 23.2%，因為可以挑的綠站變少了。Engine 總數三種拓樸是一樣的。

- 怎麼指：先指 (a) 的橫軸是毫秒到秒，強調這不是 TTFT。再指 (b) 在 2 秒之後翹起來。(c) 只指星星往右上和往左下的兩步。
- 下一頁：真正上線時不知道輸出會多長。他們用一個小預測器試過。

## Main 19 — Q5: What If Output Length Is Unknown?

- 預計：45 秒
- 論文：Section IV 為什麼需要 OSL；Section V-C，Figure 7
- 上一頁：前面的主實驗用的是 oracle 輸出長度。這一頁問若沒有 oracle 會不會散掉。

排程需要 OSL，是因為 decode 的時間和能量都跟著輸出長度走。論文的例子是：輸出 100 個 token，大約比輸出 10 個 token 多佔用 engine 十倍。這是例子，不是說他們的平均輸出就是 100。

Figure 7(a) 空心是 oracle，實心是預測。預測是一個兩層 MLP 的中位數。它的 bucket 沒有很準，Llama 51%、Mixtral 37%，亂猜大約 17%；可是算上鄰近的 bucket，是 99% 和 70%。反映到結果上，減碳最多移動 1.3 和 4.1 個百分點，violation 最多上升 1.1 個百分點。例外是 Llama 上的 iterative ILP，它本身的求解時間就會讓結果晃。

(b) 是更長的 prompt。在 violation 大約 5% 的那個操作點，facility MILP 對長 prompt 還能省到 30%，對混合 prompt 省到 28%。圖的右上還有 violation 更高、減碳更多的點，那不是這句「大約 5%」的範圍。

- 怎麼指：(a) 看空心和實心幾乎疊在一起；(b) 看斜線區是 violation 小於 5% 的地方，不要把 cap 64 那個高 violation 點說成也只有 5%。
- 下一頁：四層結論。最後一層要把「我們想做的」和「他們做完的」分開。

## Main 20 — Conclusion

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

- 不要說六篇都忽略 queue。Queue 那一欄，先前工作全是沒有；transfer 則是 SLIT、Green-LLM、GCOS、MARLIN 有，FREESH 和 MOER 沒有。
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
