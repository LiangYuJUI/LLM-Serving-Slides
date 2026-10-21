# ThunderServe 中文講稿

這是獨立簡報，對應 `2026-10-21-ThunderServe.tex`。投影片頁腳是 1/44 到 44/44，講稿標題用同一套頁碼，不和其他簡報相加。第 01–02 頁是開場，第 03–43 頁是正文，第 44 頁是 Q&A。

依據為本地 `MLSys25_Thunderserve.pdf`，首頁標示 arXiv:2502.09334v2，2025-11-06，含正文與 Appendix A–J。以下「論文第幾頁」指 PDF 實際頁碼，不是投影片頁碼。每頁正文可直接口述，引用與「備註」供準備時查閱，不必逐字念出。

## 第 01 頁｜Title

今天先介紹 ThunderServe。它研究的是：如果我們拿到的 GPU 不是整齊的一排 A100，而是不同型號、不同記憶體容量，連網路速度也不一樣，LLM serving 要怎麼部署，才能在有限預算下提供比較好的服務？

它的核心想法，是把 prefill 和 decode 的差異，跟不同 GPU 的硬體特性一起考慮。接下來我會先說明為什麼這樣做有機會，再介紹它怎麼找部署方案，以及實驗到底支持哪些結論。

## 第 02 頁｜Presentation Roadmap

今天這份簡報分成四段。先看 prefill、decode 和 heterogeneous GPUs 的背景，再看它怎麼把部署問題拆成上下兩層來解。

方法講完之後，我會接著說明服務已經跑起來時，要怎麼因應 workload 改變或 GPU 離線，以及它怎麼降低 KV cache 的傳輸成本。最後看實驗、幾個需要小心解讀的地方，還有可以延伸的研究問題。

## 第 03 頁｜Prefill and Decode Have Different Bottlenecks

先把兩個 inference phase 分清楚。Prefill 是把使用者輸入的整段 prompt 送進模型，計算各層的 key、value，建立 KV cache，並產生第一個 output token。因為 prompt tokens 都已知，同一層可以平行處理這些 tokens，讓矩陣運算比較容易把 GPU 的計算資源用起來；不同層之間仍要依序計算。

Decode 則要等上一個 token 生成後，才能把它作為下一步的輸入，所以同一個 request 的生成步驟需要依序進行。每一步仍會利用完整歷史的 KV cache，不是只看上一個 token，也不必重算整段歷史的 key、value。不過，每一步仍然需要讀模型權重和相關的 KV cache；當 batch 不大時，常常是記憶體頻寬比較先成為瓶頸。

這裡的 batch size 是一次一起處理的 request 數，可以想成 request 層級的平行程度；實際運算量還要看每個 request 的 token 數。Prefill 一次處理多個 prompt tokens，一般 decode 每個 request 每一步則只處理一個新 token。

看這張圖，左邊 prefill 起初隨 batch 增大，更能利用 GPU 的計算資源，所以 token throughput 上升；接近計算能力上限後，再增加 batch 就主要是增加執行時間，throughput 因此變平。右邊 decode 在這個測試範圍內，還能透過增加 batch，讓更多 requests 一起計算並分攤權重讀取成本，所以 throughput 持續提升。

這裡要記得，圖上的縱軸是 throughput，不是單一 request 的 latency。Batching 讓整體效率變好，不代表每個 request 都更快完成。另外，compute-bound 和 memory-bandwidth-bound 是這裡的典型特性，不是所有模型、所有 batch size 都一定如此。

來源：Section 2、Figure 2，論文第 3 頁。

## 第 04 頁｜Different GPUs Favor Different Inference Phases

既然兩個 phase 的瓶頸不同，那最適合它們的 GPU 也可能不同。

這張圖比較 A40 和 3090 Ti，測試條件是 input 512 tokens、output 16 tokens。左邊 prefill 的單次成本，A40 比較低；右邊 decode 的單次成本，則是 3090 Ti 比較低。這裡比較的是這個 workload 和論文租金設定下的 cost per request，不只是硬體跑一次需要幾毫秒。

作者用這個例子說明，A40 的計算能力在 prefill 比較有利，而 3090 Ti 較高的 memory bandwidth 對 decode 比較有利。所以，如果所有 GPU 都同時做 prefill 和 decode，就可能沒辦法充分利用每種 GPU 的強項。

但也不能因此訂死規則，說 A40 永遠只能 prefill、3090 Ti 永遠只能 decode。後面會看到，網路條件和工作負載改變後，最佳配置也會跟著變。

來源：Introduction、Figure 1，論文第 2 頁。


## 第 05 頁｜GPU Specifications in Table 1

前一頁的成本圖，背後是 Table 1 的硬體規格。A100、A6000、A5000、A40、3090Ti 的記憶體頻寬分別是 2 TB/s、768 GB/s、626.8 GB/s、696 GB/s、1008 GB/s。FP16 峰值是 312、38.7、27.8、149.7、71 TFLOPS。記憶體是 80、48、24、48、24 GB。單張租金是每小時 1.753、0.483、0.223、0.403、0.307 美元。

A40 的 149.7 TFLOPS 對應比較適合 prefill 的計算能力；3090Ti 的 1008 GB/s 對應比較適合 decode 的記憶體頻寬。八張 A100 乘上 1.753 美元，剛好是後面 in-house 預算的每小時 14.024 美元。

雲端那 32 張 GPU 的總租金，Section 5.1 寫的是每小時 13.542 美元。這個總價不是把這一欄的單價乘上張數再加起來，所以報告時把「單張規格」和「整包租金」分開說。

來源：Table 1、Section 5.1，論文第 1、8 頁。

## 第 06 頁｜Cloud Networking Is Highly Heterogeneous

接下來是網路。這兩張 heatmap 都是用 NCCL 實測 GPU 兩兩之間的 communication bandwidth。左邊是 32 張 cloud GPUs，右邊是同一台 in-house server 裡的 8 張 A100。

每一格代表一對 GPU，越接近黃色表示頻寬越高，越接近紫色則越低。對角線是同一張 GPU 與自己配對，不涉及跨 GPU 傳輸，因此圖中以零值呈現為紫色，不代表 GPU 本身沒有頻寬。

左邊可以看到連線能力非常不平均。有些 GPU 彼此很近，傳輸相對快；有些可能跨機器，甚至跨 data center，連線就慢很多。右邊的 A100 環境則有比較高速的互連。要注意，兩張圖的 color bar 尺度不一樣，不能只看顏色就說頻寬相同。

Prefill 和 decode 拆開之後，新增的一個重要成本，是把 prompt 的 KV cache 傳到 decode replica。這份 cache 會隨 prompt 長度和模型結構變大。如果選到很慢的路徑，前面靠 GPU 分工省下來的時間，可能又被傳輸吃掉。

所以 ThunderServe 不只問哪張 GPU 適合做什麼，也要問：這些 GPU 放在一起之後，資料實際要走哪一條路？

來源：Appendix C、Figure 13，論文第 14 頁。

## 第 07 頁｜Three Challenges for Phase Splitting in Clouds

作者把問題整理成三個挑戰。

第一個是 GPU 資源異質，而且數量有限。不是想要幾張同型號就一定拿得到，所以要先決定哪些 GPU 合作放一份模型，再決定這份模型負責哪個 phase。

第二個是網路異質。同一台 host 內，GPU 可能透過 PCIe 或 NVLink 連接；不同 hosts 之間則可能走 Ethernet 或 InfiniBand，頻寬差異很大。論文強調，雲端常見的是 PCIe 和 Ethernet，不能假設都有高速互連。因此，除了 prefill 到 decode 的 KV cache 傳輸，tensor parallelism 和 pipeline parallelism 的通訊成本也必須一起考慮。

第三個是環境會變。服務可能從短回答的 coding request，變成比較長回答的 conversation request；也可能有一部分 GPU 突然不能用。如果每次都重新分組、重新載入模型，調整本身就可能讓服務中斷很久。

所以整個系統要同時處理初始部署，以及上線之後的調整。接下來先看它的系統架構。

來源：Introduction 的 challenges 1–3，論文第 2 頁。

## 第 08 頁｜ThunderServe: System Overview

這張架構圖可以先抓三個元件：scheduler、workload profiler，以及 task coordinator。

Scheduler 負責產生 deployment plan。它會讀模型設定、有哪些 GPU、GPU 型號，以及 GPU 之間的 bandwidth matrix，也會讀 profiler 提供的 workload 資訊。

Profiler 觀察的是線上 request 的特徵，例如平均 prompt length 和平均 output length。因為這些特徵會改變 prefill 和 decode 各自需要多少資源，所以它不是只記錄 request 數量。

Coordinator 則負責真的把 request 派出去：先在哪個 prefill replica 做，再接到哪個 decode replica，最後把回應收回來。這些派送決定受到 deployment plan 指引。

當 profiler 偵測到 workload shift，或 scheduler 發現 GPU heartbeat timeout，就會觸發 lightweight re-scheduling。Workload shift 就是工作負載特性變了，例如從長 prompt、短回答，變成短 prompt、長回答，讓 prefill 和 decode 的資源需求比例改變。Heartbeat timeout 則是 GPU worker 太久沒有回報心跳訊號，可能已經失聯；原因可能是硬體、程序或網路問題，不一定是 GPU 壞掉。

Lightweight re-scheduling 就是保留仍可用的 GPU groups 和既有 TP／PP 配置，只調整 replicas 的 prefill／decode 角色，以及 request routing，省下重新載入模型權重的成本。TP 是 tensor parallelism，把同一層的張量運算切給多張 GPU 合作；PP 是 pipeline parallelism，把不同層分成不同 stages，例如一組 GPU 算前半部，另一組算後半部，資料依序傳過去。

所以這裡的 scheduler 主要是在安排部署和 replica routing，和每一步決定哪些 requests 組成 token batch 的底層排程器，是不同層級的工作。

來源：Section 4、Appendix E、Figure 15，論文第 7、14–15 頁。

## 第 09 頁｜A Deployment Plan Has Four Components

在看演算法前，先定義什麼叫一份 deployment plan。它包含四個決定。

第一個是 group construction，也就是把哪些 GPU 放在同一組。這一組 GPU 共同承載一份完整的 model replica；不代表組內每張 GPU 都各自放一份完整模型。

第二個是 phase designation，決定這一組負責 prefill 還是 decode。兩種 replica 使用同一個模型的權重，只是被指定執行不同階段。

第三個是 parallel configuration，也就是這份 replica 內部要怎麼做 TP 和 PP。Group construction 決定「哪些 GPU 合作」，TP／PP 則決定「模型怎麼分給它們」。例如四張 GPU 用 TP=2、PP=2，就是把模型的層分成兩個 stages，每個 stage 再由兩張 GPU 分攤各層的張量運算，四張合起來承載一份完整模型。

第四個則是 orchestration，決定 request 先進哪個 prefill replica，再送到哪個 decode replica。

前兩個決定由 upper level 處理，後兩個由 lower level 處理。接下來的兩層搜尋，就是在這四個決策之間建立一個可以實際求解的流程。

來源：Section 3.1，論文第 4 頁。

## 第 10 頁｜Scheduling as Two-Level Hierarchical Optimization

如果把剛剛四個決定一次攤開來找，搜尋空間會非常大。所以 ThunderServe 把最佳化決策分成兩層；這裡的 level 不是模型的 layer。Upper level 先決定哪些 GPU 一組、各組負責哪個 phase，再交給 lower level 補齊細節並評估。

Lower level 先幫每組 GPU 選 parallel configuration，再決定各個 prefill 和 decode replica 之間的 routing。接著用模擬得到的 end-to-end SLO attainment，作為這個候選方案的分數，回傳給 upper level。

這個模擬器來自先前研究 DistServe，它有開源 serving system 和模擬器。ThunderServe 沿用並擴充其模擬器，加入 KV cache 傳輸成本，用 alpha-beta model 估算「啟動延遲，加上資料量除以頻寬」，再納入 SLO attainment 評估。因此不是從零重寫模擬器，而是讓既有模擬考慮雲端不同連線的成本，避免每個候選配置都要實際部署測試。

SLO 全名是 Service Level Objective，也就是服務水準目標；SLO attainment 是目標達成率。以 E2E 為例，deadline 設成十秒，若一百個 requests 有九十個在十秒內完成，達成率就是 90%。同一批 requests 可以用不同 deadlines 各算一個達成率，門檻越寬鬆，達成率通常越高；但搜尋時比較不同部署方案，要固定相同的 workload、request rate 和 deadline。

後面的實驗會分別看三種 SLO。TTFT（Time To First Token）是從 request 送出到收到第一個 output token 的時間，包含排隊與 prefill；TPOT（Time Per Output Token）是第一個 token 之後，平均每產生一個 output token 所需的時間；E2E latency（End-to-End Latency）則是從 request 送出到完整回答結束的總時間。簡單說，就是「等多久開始回答、回答時多快、多久全部答完」，再分別看是否符合各自的門檻。

Upper level 一開始只提出分組和 phase 角色，還不知道這個方案的分數；要等 lower level 選好 TP／PP、決定 routing 並估計 SLO attainment，才能拿回報的分數比較不同方案。簡單說，就是「upper 提案，lower 補齊細節並評分，upper 再根據回報搜尋更好的方案」。因為使用成本模型和 heuristic，也沒有窮舉所有可能配置，所以不保證找到全域最佳解。

來源：Sections 3.1、3.3、Figure 3，論文第 4、6 頁。DistServe 官方開源專案：[LLMServe/DistServe](https://github.com/LLMServe/DistServe)；模擬器位於 `simdistserve/`，使用 SimPy 做離散事件模擬。

## 第 11 頁｜Initialization and Feasibility in Tabu Search

Upper level 使用 tabu search，也就是禁忌搜尋。它從一個初始方案出發，每次小幅修改方案，交給 lower level 評分，再選沒有被 tabu list 排除的鄰居中分數最高的。Tabu list 就像短期記憶，避免搜尋一直在相同方案之間來回；即使下一步暫時比較差，也可能先走過去，嘗試跳出局部最佳解，同時保留搜尋過程中找到的最好方案。

這頁先說明如何建立搜尋起點，以及後續候選方案的基本可行性檢查。

作者用 hierarchical clustering，根據 GPU 之間的 bandwidth matrix 來建立初始 group。直覺上，就是盡量先把連線比較好的 GPU 放在一起，避免一開始就讓同一份模型跨過特別慢的連線。各 group 的 prefill 或 decode 角色，則先隨機指定。

之後在產生新候選方案時，會先做便宜的 early check。例如，某一組 GPU 的總記憶體連一份模型權重都放不下，就沒有必要再花時間跑完整的 lower-level 評估。

不過，總記憶體放得下權重，只是必要條件。真正執行時還有各 GPU 的分配、KV cache 和其他空間需求，所以不能把這個 early check 當成完整的 memory feasibility 保證。

作者用 Job Shop Scheduling Problem 的類比來說明這個問題為什麼難解。我們這裡要掌握的是，它選擇用 heuristic 搜尋控制成本，而不是嘗試列舉所有部署。

來源：Section 3.2、Algorithm 1、Appendix A，論文第 5、13 頁。

## 第 12 頁｜Four Neighbor Operations in Tabu Search

Tabu search 每次怎麼產生附近的候選解？這篇提供四種操作。

第一種是 flip，只改某個 group 的角色：prefill 改成 decode，或反過來。

第二種是 split，把一個 group 拆成兩組。第三種是 merge，把兩組併成一組。Split 和 merge 都可能改變 replica 的數量，也會影響每份模型能拿到多少資源。論文會對新產生的 group 隨機指定 phase。

第四種是 move，把某一種型號的一些 GPU，從一組移到另一組。它保留了調整資源比例的彈性，不需要每次都整組拆掉重來。

圖上主要畫的是 split、merge 和 move，phase 的改變為了簡化被省略了。這四種操作加起來，讓搜尋可以同時探索 GPU grouping 和 phase allocation，而不是只調 prefill、decode 的數量比例。

來源：Section 3.2、Figure 4，論文第 5 頁。


## 第 13 頁｜Neighbor Updates in Notation

上一頁的四種操作裡，flip 只改 phase，不改 GPU 數量。另外三種可以用符號寫下來。g 下標 i、t 是 group i 裡、型號 t 的 GPU 張數。

Split 用隨機比例 r 把 group s 拆開：第一組拿到 floor of g 乘 r，第二組拿到剩下的張數。每種型號都照同一個 r 切。Merge 就是兩個 group 的同型號張數相加。Move 是從 group i 搬 m_t 張型號 t 到 group j，一邊減、一邊加。

Split 和 merge 產生的新 group，phase 會重新隨機指定。如果某個 group 的總記憶體連一份模型權重都放不下，這個鄰居會在評分前被丟掉。

來源：Section 3.2，論文第 5 頁。這些式子在原文沒有編號。

## 第 14 頁｜Tabu Search: Evaluation and Update

這頁直接列出論文 Algorithm 1 的 pseudocode，保留原文的 14 個行號。第 1 行的參數是搜尋 100 步，每步產生 10 個鄰居，tabu list 最多記住 5 個解。第 2–3 行先初始化目前方案 x、空的 tabu list T，以及目前找到的最佳方案 x_best。

第 5–7 行是每一步的搜尋：先產生候選鄰居，再排除 tabu list 裡最近走過的方案。剩下的候選方案，用 lower-level 回傳的 SLO attainment，也就是 f，來評分，選出其中分數最高的 x′。

這裡一個重要細節是，它選的是目前可走的鄰居中最好的，不要求這個鄰居一定比現在的解更好。因此搜尋可以暫時接受比較差的分數，才有機會離開 local optimum。另一方面，系統另外保存一路看過最好的解，最後回傳的是這個 best-so-far，而不是最後停下來的位置。

對照程式，第 8 行只有在分數更高時才更新 x_best；第 9–10 行把新方案加入 tabu list，超過五個就只保留最新五個；第 11 行則不論是否進步，都把目前方案移到 x′。最後第 13 行回傳 x_best。Tabu list 用來避免繞圈，但不代表 100 步結束後就能保證全域最佳。

來源：Algorithm 1、Section 3.2，論文第 5 頁。

## 第 15 頁｜Deducing Parallel Configurations for Each Group

現在進入 lower level。當 GPU grouping 和 phase 已經給定，第一步是決定每個 group 內部怎麼做 model parallelism。

TP，也就是 tensor parallelism，是把同一層裡的 tensor 和運算切到多張 GPU 上。因為層內需要協作和通訊，所以很依賴快速互連。ThunderServe 不允許 TP 跨 node，Appendix B 也限制 TP 使用同一種型號的 GPU。

PP，也就是 pipeline parallelism，則是把模型的 layers 分成幾個 stage，讓不同 GPU 負責不同層，stage 之間傳 activation。因為不同 GPU 的計算能力和記憶體容量不同，所以它支援不平均的 layer partition，不要求每個 stage 都有一樣多的 layers。

另外，作者用 dynamic programming，也就是 DP，選擇 pipeline 的通訊路徑，考慮 stage 之間的 bandwidth。舉個示意例子：三張 GPU 各負責一個 stage，如果 A–B、B–C 的連線快，A–C 很慢，排成 A → B → C 就能避開慢連線。模型的 layers 仍照原本順序執行，只是換成不同 GPU 負責各段 layers。DP 會記住「已經用了哪些 stage、目前停在哪個 stage」的最佳部分路徑，再逐步延伸；bitmask 就是用 0／1 記錄已使用的 stage。論文有描述這個流程，但沒有列出完整的 DP 遞推式。

對每個候選配置，作者再使用 HexGen 的 cost model 估計記憶體和執行成本。

HexGen 是研究 heterogeneous GPU 推論部署的 previous work。它的 cost model 可以想成部署前的估算工具：給定 TP／PP 配置和 batch size，預測需要多少 GPU 記憶體、執行要多久，幫助判斷「放不放得下、跑起來多快」。這裡的 cost 指記憶體需求和執行時間。Cost model 先估計各配置的成本，simulator 再利用預測的 latency 等資訊，估計整體 request 的 SLO attainment。

Prefill 最後選的是預測 latency 最低的候選配置；decode 則選預測 throughput 最高的配置。原因是 decode 比較能透過 batching 提升效率。這裡的最佳，應該理解成在它保留下來的候選集合與成本模型之下最佳。

來源：Section 3.3、Appendix B、Algorithm 2，論文第 6、13–14 頁。

備註：Appendix B 將 decode throughput 的估計描述為可承載的最大 total batched token size 除以 decode latency；這是搜尋使用的估計，不應直接當成所有服務情境的實測 throughput 定義。


## 第 16 頁｜Algorithm 2: Parallel Configuration Search (1/2)

上一頁講的是規則，這裡開始對照完整的 Algorithm 2。原文共 29 行，分成兩頁呈現；這頁是第 1–17 行，下一頁接第 18–29 行，註解、end for 和 end if 都有保留。

第 1–4 行先讀入 GPU 分組、cluster 和模型資訊，建立結果清單，再逐一處理每個 group。每個 group 都有自己的 plan_list，用來記錄候選配置和分數。

第 5–7 行開始搜尋 TP／PP。TP 從 1 試到 T_i；T_i 是這個 group 裡，數量最少的 GPU 型號有幾張。作者限制 TP 使用同型號 GPU，再以 T_i 作為共同上限來縮小搜尋空間，這是 heuristic，不是 TP 的必然限制。PP 從 1 試到該 group 的 GPU 數除以 T_i；若只考慮 GPU 數量，上限應隨當前 TP 計算，因此原文的固定上限較保守，但沒有進一步解釋原因。

第 8–11 行針對每組 TP／PP，先用 DP 找 pipeline 路徑，再依 GPU 記憶體和算力調整 layer partition。

第 12–16 行依 phase 計算分數 C：prefill 用預測 latency，decode 用預測 throughput。第 17 行把分數和 plan 一起放進 plan_list。此時還在搜尋候選方案，尚未選出這個 group 的最終配置。

來源：Appendix B、Algorithm 2 第 1–17 行，論文第 13 頁；成本估計說明見第 14 頁。

## 第 17 頁｜Algorithm 2: Parallel Configuration Search (2/2)

這頁接續原文第 18 行。第 18、19 行的 end for 分別結束 PP 和 TP 迴圈，代表這個 group 的候選配置已經全部評估完，才進入後面的選擇。

第 20–26 行從 plan_list 選出一個配置：prefill 選 latency 最小的 plan，decode 選 throughput 最大的 plan。原文第 22、25 行寫 min(C) 和 max(C)，意思是取出對應分數的 plan，不是只回傳一個數字。

第 27 行把選出的 plan 加入總結果清單。第 28 行結束最外層的 group 迴圈；所有 group 都處理完後，第 29 行才回傳整份 parallel configurations。

Appendix B 把 decode throughput 估計成這組 GPU 能承載的最大 total batched token 數，除以 decode latency。完整的 29 行保留了控制流程，但 DP 和 Pipeline_Partition 的內部實作仍沒有在這段 pseudocode 裡展開。

來源：Appendix B、Algorithm 2 第 18–29 行，論文第 13 頁；throughput 估計說明見第 14 頁。

## 第 18 頁｜Orchestrating Prefill and Decode Replicas

每個 replica 的 parallel configuration 選好之後，下一個問題是：request 應該經過哪一組 Prefill → Decode 路徑？這裡的 replica 是一份部署好的模型副本，可以由多張 GPU 共同執行，不一定等於一台 instance。

看這張圖，左邊 coordinator 可以把 request 分給不同的 Prefill replicas；Prefill 做完後，又可以把 KV cache 送往不同的 Decode replicas。因此有很多可能的 pairing。我們先回答「每一組 pairing 好不好」，之後才決定實際流量怎麼分配。

這裡用來評估好壞的指標是 SLO attainment。它不是單純的 latency，而是「有多少比例的 requests 可以在預先設定的 latency deadline 內完成」。更精確地說，要看目前評估的是哪一種時間要求：TTFT，也就是 Time To First Token，關心多快拿到第一個 token；TPOT，也就是 Time Per Output Token，關心後續每個 output token 的生成時間；E2E，也就是 End-to-End latency，關心整個 request 完成的時間。達成率是符合所選 SLO 時間要求的 request 比例，不是把三種 latency 混成一個數字。

ThunderServe 沿用 previous work DistServe 的 inference task simulator，並額外考慮 KV cache communication cost，預測每一組 Prefill i → Decode j 的 SLO attainment。這些結果整理成 performance／SLO attainment score matrix D。D_ij 表示在給定 workload 與 SLO deadline 的條件下，若 request 使用 Prefill replica i，再送到 Decode replica j，模擬器預測可以滿足該 SLO 的 request 比例。

例如 D_12 = 0.92，就是在目前 workload 與 deadline 設定下，採用 Prefill 1 → Decode 2 這條路徑的 requests，預測約有 92% 可以符合正在評估的 SLO。這裡的 SLO 可以是 TTFT、TPOT 或 E2E 的時間要求。簡單說，D 是「每條 Prefill → Decode 路徑的預測服務品質評分表」，不是 latency matrix，也不是實際 routing 的流量比例。

Deadline 不是固定的 1 秒或 2 秒。論文 evaluation 以 A100 的 execution latency 為基準，用不同的 SLO Scale，也就是基準時間的不同倍數，設定 latency deadline，再觀察達成率。反過來，作者也會問：若要求 90% 或 99% 的 requests 滿足 SLO，最小需要多寬鬆的 latency deadline？所以 deadline 是時間門檻，90% 或 99% 則是希望達到的 request 比例。

D 的分數會受到計算能力、workload、執行 latency，以及 KV cache communication cost 影響。下一頁先拆開其中一個重要因素：Prefill 做完後，把 KV cache 搬到 Decode 究竟要多久？

來源：Section 3.3、Figure 5，論文第 6 頁；SLO 定義、SLO Scale 與 90%／99% 目標見 Section 5.1 的 Evaluation metrics。

備註：Figure 5 的箭頭數值與正文對 conditional Y_ij 的定義有歧義。從同一 Prefill 出發的箭頭值分別加總為 0.6 與 0.4，看起來比較像「全體 requests 中走每條完整路徑的比例」，而不是條件於該 Prefill 的比例。口述應以正文對 X、Y 的定義為主，不直接把圖上的箭頭值當成已正規化的 Y。

## 第 19 頁｜Modeling KV Cache Communication Cost

上一頁先評估每組 pairing 好不好，這頁看其中一個重要因素：Prefill 做完後，把 KV cache 搬到 Decode 要多久。論文使用 alpha-beta model，基本概念很簡單：傳輸時間等於啟動一次通訊的固定成本，加上資料量除以頻寬，也就是 T_comm = alpha_ij + payload / beta_ij。

在這篇的符號裡，alpha 是 network latency，beta 是 bandwidth。這裡要跟著作者的定義看，因為有些文獻會把 beta 定義成每個 byte 的傳輸時間，寫法就會不同。

原文的 payload 寫成 2 × b × s × h × N_bytes。分子裡的 b 是 batch size，s 是 sequence length，h 是 Transformer block 的 hidden size，N bytes 是每個 KV element 在傳輸時占幾個 bytes。前面的 2 代表 key 和 value 兩份資料。如果 bandwidth 用 bytes per second，那 payload 也要用 bytes；不能把 Gbps 的數字直接當成 GB/s 代進去。

不過，原文這個式子沒有明確寫出 layer 數。如果要計算整個模型的 KV cache，還需要考慮 L 個 layers，以及每一層真正的 KV-head width。這一頁下方的完整資料量公式，是根據 tensor 維度補充的說明，不是說原文已經把這些項目都寫出來了。

對一般 multi-head attention，總 KV-head width 通常等於 hidden size；如果是 grouped-query attention，也就是 GQA，就不能直接用完整 hidden size 代替 KV 的寬度。此外，TP、PP 分片會影響每條 link 實際要傳多少資料。因此實作時要估的是實際傳輸的 shards，再加上必要的量化 metadata，而不是只照抄一個總量公式。

最後把它接回 D：KV cache communication time 並不是最終 routing objective 本身，而是影響 Prefill i → Decode j 這條路徑的整體 latency，進一步影響 request 是否超過所選 SLO 的 deadline，也就影響 D_ij 的預測達成率。可以記成「KV 傳輸成本 → latency → 是否超過 SLO deadline → D_ij」。對不同 SLO 指標的影響，仍要依其計時範圍判斷，不能說傳輸時間會等量加到 TTFT、TPOT 與 E2E 上。

來源：Section 3.3、Equation 1，論文第 6 頁。全模型資料量與分片注意事項為補充解釋。

## 第 20 頁｜Replica Routing Objective and Formulation Caveats

前兩頁回答了「每組 pairing 的預測表現如何」，也說明 KV 傳輸成本怎麼影響評分。現在才要回答「實際流量應該怎麼分配」。D 是評分表；X 和 Y 才是 routing proportion。

先看第一階段的向量 X。X_i 是所有 incoming requests 中，有多少比例先送到 Prefill replica i。例如 X_1 = 0.6、X_2 = 0.4，意思是用 100 個 requests 來看，60 個先到 Prefill 1，40 個先到 Prefill 2。因此 sum_i X_i = 1，也就是所有流量都要分配出去。

第二階段的矩陣 Y 是 conditional routing proportion。Y_ij 的意思是：「已經送到 Prefill i 的 requests 裡，有多少比例接著送到 Decode j。」例如剛剛有 60 個 requests 到 Prefill 1，其中 18 個接著送到 Decode 2，那 Y_12 = 18 / 60 = 0.3。注意，這個 30% 的分母是到 Prefill 1 的 60 個 requests，不是全部 100 個。

因此，依照條件比例的語意，每個 Prefill i 對應的一整列 Y 應該滿足 sum_j Y_ij = 1。不過原文印出的 constraint 在這裡缺少等號與右側，這是數學表達不完整的地方。我們可以解釋條件比例應有的意思，但不能說論文已經完整寫出了這條約束。

為了把流量看得更直觀，我們額外引入 Z_ij = X_i Y_ij。Z 是輔助理解用的 joint traffic fraction，不是 ThunderServe 論文原文獨立定義的變數。它表示「所有 incoming requests 中，真正走 Prefill i → Decode j 這條完整路徑的比例」。延續剛剛的例子，Z_12 = 0.6 × 0.3 = 0.18，也就是全體 requests 中有 18% 走 Prefill 1 → Decode 2。

原文想最大化的 objective 是 sum_i sum_j X_i Y_ij D_ij。如果用我們引入的 Z 表示，就是 sum_i sum_j Z_ij D_ij。口頭上可以讀成「每條路徑的流量比例，乘上該路徑的預測 SLO attainment，最後全部加總」。例如 Z_12 = 0.18、D_12 = 0.92，這條路徑對加權分數的貢獻就是 0.18 × 0.92 = 0.1656，也就是 16.56 個百分點；這只是其中一條路徑的貢獻，還要加上其他路徑。直觀目的就是把更多 requests 分配給預測 SLO attainment 比較好的路徑。

但這裡有一個不能省略的 formulation caveat：如果把 D 當成固定分數，而只要求 Z 非負、總和為 1，沒有其他與負載相關的限制，那把全部流量放到 D 最大的那條路徑就能取得最大值；若有多條同分最高的路徑，也可以在它們之間分配。這個式子本身沒有解釋集中流量後，replica capacity、queueing 或其他負載效應會如何改變可行性或分數。原文沒有完整展開這些關係，我們不能自行補出限制，再宣稱是作者的方法。

此外，作者把問題稱為 two-stage transportation problem，並宣稱可以用 linear programming 求解；但目前印出的 objective 裡，X_i 與 Y_ij 都是變數，兩者相乘在形式上是 bilinear。引入 Z 可以讓目標寫成對 Z 的線性形式，卻不代表已經補齊完整 solver。投影片保留的原文約束包括 X 的總和為 1、X 與 Y 非負，以及缺少等號與右側的 Y row-sum 項；這些資訊不足以完整重現實際 routing solver。

所以報告時應說：「論文用 transportation formulation 描述 Prefill–Decode routing，並宣稱以 LP 求解；但 paper 中印出的數學式沒有完整展開所有必要 constraints，因此不能只根據這個式子推斷完整 solver implementation。」這是對論文呈現方式的限制提醒，不代表我們已經知道實作使用了哪些額外約束。

最後記住四個符號：D 是每條路徑的預測 SLO 表現；X 是第一階段選 Prefill 的比例；Y 是在某個 Prefill 之後選 Decode 的條件比例；我們引入的 Z_ij = X_i Y_ij，則是全體 requests 中走某條完整路徑的比例。這裡是逐條路徑相乘，不是一般的矩陣乘法 Z = XY。

來源：Section 3.3，論文第 6 頁。Z、數值例子與數學形式的限制為報告者的輔助解釋及分析。

## 第 21 頁｜Network-Aware Deployment Plans

這個例子把前面的方法串起來：同樣是 4 張 A40 加上 4 張 3090 Ti，網路條件不同，最佳 deployment plan 也可能不同。作者在兩個 GPU instances 上執行 LLaMA-30B，一台有 4×A40，另一台有 4×3090 Ti，持續送入長度為 1024 的 input sequences，測試 inter-instance bandwidth 為 40 Gbps 和 5 Gbps 時的表現。這裡研究的是跨 GPU instance 的網路條件差異，不是明確比較「40 Gbps 是同機器、5 Gbps 是跨資料中心」。

先釐清 replica。它是一份可以獨立承接 request、執行所負責推論工作的模型服務實例，不是單張 GPU。一個 replica 可以由多張 GPU 組成，內部透過 TP、PP 共同執行模型。例如 4×A40 可以組成一個 model replica，4×3090 Ti 也可以組成另一個。在一般 non-disaggregated serving 中，每個 replica 同時負責 Prefill 和 Decode；在 ThunderServe 中，則可以指定為只負責 Prefill 的 replica，或只負責 Decode 的 replica，由兩者接力完成 request。

這裡的 non-disaggregating baseline，是作者在 Appendix H 建立的對照配置，不是 vLLM、DistServe 或 HexGen 等另一個系統名稱。Baseline 用 4×A40 組成一個完整 model replica，再用 4×3090 Ti 組成另一個；兩個 replica 各自都做 Prefill 加 Decode，不進行 phase disaggregation。可以把它想成兩組各自完整跑模型的服務實例。

相對地，在 40 Gbps 下，ThunderServe 讓 4×A40 組成 1 個 Prefill replica，4×3090 Ti 組成 1 個 Decode replica。原因是這個例子中，A40 較高的 peak FLOPS 有利於 compute-heavy 的 Prefill，而 3090 Ti 較高的 memory access bandwidth 有利於 memory-bound 的 Decode。在這個 workload 和配置下，40 Gbps 的跨 instance 網路讓 KV cache 傳輸成本仍可接受，因此可以利用兩種 GPU 各自的優勢。

這裡的資料流是：request 先到 Prefill replica，產生 KV cache，再把 KV cache 傳給 Decode replica，讓 Decode 接著生成 tokens。如果兩個 replica 位於不同 instances，KV cache 就可能經過 inter-instance network。圖表中的 KV Comm 不是泛指所有 communication，主要指這個 Prefill 到 Decode 搬移 KV cache 所需的 communication time。

在 40 Gbps 的配置下，ThunderServe 系統 throughput 是 3292 tokens/s，而不做 Prefill／Decode 分離的 baseline 是 1610 tokens/s。3292 除以 1610 約等於 2.04，也就是整體 throughput 約為 baseline 的兩倍。這個數字是整個 serving system、所有 requests 加總後每秒處理的 token 數，不是單一 request 每秒生成 3292 個 tokens。

接著把 inter-instance bandwidth 降到 5 Gbps。如果仍然讓 A40 做全部 Prefill、3090 Ti 做全部 Decode，每個 request 的 KV cache 都要經過這條慢連線，大量 KV cache transfer 就會成為瓶頸。因此 ThunderServe 改成 Prefill replica 使用 2×A40 加 2×3090 Ti，Decode replica 也使用 2×A40 加 2×3090 Ti，並透過 PP 把不同 instances 上的 stages 接起來。

這個改動的重點，是重新安排什麼資料需要經過慢網路。透過對應 layers 的 placement，昂貴的 KV cache transfer 可以盡量留在同一個 instance 內，利用 intra-instance 的高頻寬連線；跨 instance 的低頻寬連線則用來傳 pipeline stages 之間的 activations。它沒有消除跨機器通訊，仍然存在 pipeline communication，而是改變了跨慢 link 傳輸的資料種類與資料量。

在這個 5 Gbps 部署下，系統 throughput 是 2196 tokens/s，約為 baseline 的 1.4 倍。這些數字要和 optimization 的結果分開看：deployment／scheduling optimization 根據 GPU profile、parallel configuration、network bandwidth、KV communication cost 與 workload 等資訊選擇 deployment plan；3292、2196 與 1610 tokens/s，則是論文對相應配置進行 serving execution／benchmark evaluation 後報告的系統表現，不是 solver 直接算出的 throughput。

Table 5 還有一個容易誤讀的地方：40 Gbps 配置的單次 KV Comm 約為 133 ms，5 Gbps 配置卻只有約 41 ms。這不代表 5 Gbps 傳 KV cache 比 40 Gbps 快，因為兩種情況的 deployment plan、KV 傳輸路徑，以及實際跨各條 link 的資料量都不同。低頻寬配置透過改變 placement，讓更多 KV communication 留在 intra-instance 的高頻寬連線上，因此 KV Comm 反而較低。

另外，也不能用 1 / (Prefill time + KV Comm + Decode time) 直接推導 system throughput。這些單次 request 的時間，和整個系統透過多個 replicas、pipeline、batching 與 concurrent requests 達成的總吞吐量，是不同層次的量測；系統 throughput 不是單一 request latency 的簡單倒數。

所以這個例子要傳達的是：不能只看 GPU compute 或 memory bandwidth，就固定指定某種 GPU 永遠做哪個 phase。同樣是 4×A40 加 4×3090 Ti，網路快時可以讓 A40 專門 Prefill、3090 Ti 專門 Decode；網路慢時，就要重新安排 replicas 與 PP placement，避免大量 KV cache 經過慢 link。Deployment plan 必須一起考慮 GPU capability、parallel configuration、KV communication cost、network bandwidth 與 workload。

ThunderServe 最重要的不是固定 GPU-to-phase mapping，而是 network-aware heterogeneous deployment。

來源：Appendix H、Figures 16–17、Table 5，論文第 16–17 頁。Replica 定義與 throughput 解讀為輔助說明。

## 第 22 頁｜Request-Time Breakdown in Table 5

上一頁給了 throughput，這一頁把 Table 5 的單次時間補上。Baseline 的 prefill、KV、decode 是 884、0、1689 ms，throughput 1610 tokens/s。40 Gbps 的 ThunderServe 是 698、133、1126 ms，3292 tokens/s。5 Gbps 是 964、41、1846 ms，2196 tokens/s。

5 Gbps 那一列的 KV 時間只有 41 ms，比 40 Gbps 的 133 ms 更短。原因是部署改了：KV 留在 instance 裡面傳，不是慢的連線突然變快。

這三個時間是單次 request 的區段，不能把 prefill 加 decode 再取倒數，當成整個多 replica 系統的 throughput。

來源：Appendix H、Table 5，論文第 16–17 頁。

## 第 23 頁｜Throughput Depends on Prefill-to-Decode Ratio

接下來看 workload 變動。這個實驗先固定比較單純的硬體環境：都是 A5000，兩張 GPU 承載一個 replica，模型是 LLaMA-13B。

三個子圖分別對應 8、12、16 張 GPU，也就是 4、6、8 個 replicas。橫軸是 prefill replica 數量和 decode replica 數量的比例，縱軸是 token throughput。

在這份資料裡，coding 的 prompt 相對長，output 相對短，所以分配更多 prefill replicas 通常比較有幫助。Conversation 的回答比較長，每個 request 會占用 decode 較久，因此通常需要更多 decode replicas。

這張圖的重點不是找出一個永遠有效的比例，而是說，即使 group construction 和 parallel configuration 不變，只調整 phase 比例，整體 throughput 就會有明顯差異。而且 cluster size 改變後，適合的比例也會變。

這正是 lightweight re-scheduling 的動機：很多時候，先改角色與 routing，就能處理主要的瓶頸轉移。

來源：Section 3.4、Figure 6，論文第 7 頁。

## 第 24 頁｜SLO Attainment Also Depends on Phase Ratio

上一頁看 throughput，這一頁改看 SLO attainment。設定是 16 張 A5000，兩張一個 replica，所以總共 8 個 replicas。

這裡先釐清 coding 和 conversation。它們是 LLM 的兩類應用任務，在這個實驗中，更精確地說，是兩種 request workload，也就是工作負載。Coding 指程式相關的使用情境，例如程式碼補全；conversation 則是對話、問答等情境。作者採用 Azure 資料集中的這兩類 workload，這裡關心的是 requests 的輸入、輸出長度與服務需求，不是在比較模型寫程式或聊天的回答品質。

在論文採用的 workload 中，coding 的輸入較長、輸出較短。Prefill 要處理整段輸入，所以較長的 prompt 會增加 Prefill 的工作量；輸出較短，則需要較少的 Decode 生成步數。因此作者在這組實驗裡發現，5 個 Prefill 搭配 3 個 Decode 的配置較合適。

Conversation 則是輸入相對較短、輸出較長。因為 Decode 要逐步生成後續 tokens，較長的回覆會增加 Decode 的工作量，因此這組實驗較適合 3 個 Prefill 搭配 5 個 Decode。這裡的 5:3 和 3:5 都是 Prefill replica 數量比上 Decode replica 數量；同樣的 8 個 replicas，會因為 workload 不同而採用不同的 phase ratio。

可以看到，不同的 phase ratio 會讓 SLO 曲線往左或往右移。橫軸 SLO scale 越大，代表 deadline 越寬鬆；縱軸越高，代表越多 requests 能符合這個 deadline。所以在同一個 deadline 下，較高的曲線比較好；如果固定想達成的比例，就看哪個配置需要的 deadline 比較短。

要注意，「coding 輸入較長、輸出較短」是這篇採用的 workload 特徵，不是所有程式任務都一定如此；conversation 也不一定永遠需要更多 Decode。這裡的 5:3 和 3:5 是這個模型、硬體及 workload 下作者報告的配置，不能直接當成其他部署的固定比例。當 deadline 放得很鬆，很多配置都能達到接近 100%，也就不會一直有明顯差距。

因此這一頁的重點是：要根據實際 workload 的輸入與輸出需求分配 Prefill／Decode 資源，才能提高在指定 deadline 下的 SLO attainment，不能只看任務名稱就固定 phase ratio。

來源：Appendix D、Figure 14，論文第 14 頁；workload 來源見 Section 5.1 的 Model and workloads。任務情境例子為輔助解釋。

## 第 25 頁｜Lightweight Re-scheduling in Real Time

真正上線之後，如果 workload 變了，要不要把剛剛整個搜尋全部重跑？作者的答案是，先做一個範圍比較受限的調整。

Lightweight re-scheduling 保留仍然可用的 GPU groups，也保留原來的 parallel configurations。Tabu search 的四種操作，只留下 flip，也就是改 prefill 或 decode 的角色；split、merge 和 move 都先不做。Lower level 也跳過 parallel configuration deduction，只重新解 routing。

這樣能省掉載入模型權重的成本，因為 prefill 和 decode 用的是同一份模型。當模型已經放在這組 GPU 上，並且原本的 TP、PP 配置也保留，就可以改變它服務的 phase，而不需要搬動整份模型參數。

代價是搜尋空間變小。某個配置原本適合 prefill，改做 decode 之後不一定是 decode 的最佳配置。作者選擇的是用這個限制，換取比較短的調整時間，而不是聲稱任何 workload shift 都能不用重部署就達到全域最佳。

來源：Section 3.4，論文第 6–7 頁。

備註：不重新載入權重，不等於角色切換完全沒有工作，也不等於故障前正在處理的 request、KV cache 都能無損保留。本文沒有完整交代所有 in-flight request 的故障恢復語意。

## 第 26 頁｜Runtime Support for Phase Splitting

前面是怎麼找方案，這一頁補充它在 runtime 怎麼把方案執行起來。

首先，NCCL communication group 的建立也有成本。所以作者會預先建立可能需要的 communication groups，避免每次調整時才開始建立。

第二，KV cache 傳輸使用 asynchronous communication，讓通訊有機會和運算重疊。這不代表傳輸時間消失，只是盡量不要讓 GPU 因為等待傳輸而完全停下來。

第三，prefill 做完的 KV cache，不是無限量地直接塞到 decode 那邊。系統把 KV cache queue 放在 prefill replicas 的 GPU memory，decode replica 在完成一輪 decoding 後，再從 queue 取出對應的 KV cache。

所以 prefill GPU 的記憶體也扮演暫存 buffer 的角色。這些實作細節很重要，因為 phase splitting 真正跑起來，不只有「切成兩個階段」這件事，還要處理通訊建立、資料等待，以及兩邊處理速度不一樣的情況。

來源：Section 4、Appendix E，論文第 7、15 頁。

備註：論文另外整合 FlashAttention 和 PagedAttention。這些是採用的推論技術；本篇主要貢獻仍是異質環境下的 deployment、routing 與 re-scheduling。

## 第 27 頁｜Quantize KV Cache for Communication Only

除了選比較好的 KV transfer 路徑，另一個辦法是讓傳輸的資料變小。

ThunderServe 借用低精度 KV quantization 的想法，在 prefill 端把原本 16-bit 的 KV values 量化並打包成 4-bit，送到 decode 端後再 unpack、dequantize，回到 16-bit 表示來做後續計算。

所以它的設計重點是 communication compression。不能把這件事說成模型權重變成 4-bit，也不能直接說 decode 持續用 4-bit KV cache 執行。兩邊在計算時，使用的都是 16-bit 表示。

看 Figure 18，較深的部分是 KV communication time，較淡的部分是 end-to-end processing time，不是兩段要再相加的堆疊。測試是 LLaMA-7B、兩張 A5000、40 Gbps。正文報告 KV communication 占 E2E 成本的比例，從 16–30% 降到 4–9%。

但有一點一定要說清楚：dequantize 只是恢復成 16-bit 的數值格式，不會把量化時捨棄的資訊完整找回來。所以它仍是 lossy compression，模型品質需要用實驗檢查。

來源：Section 4、Appendix I、Figure 18，論文第 8、17 頁。

## 第 28 頁｜KV Compression: Speed and Model Quality

先看速度。這張表是另一組 LLaMA-30B 的測試，使用 Appendix H 的硬體配置，不能跟上一頁兩張 A5000 的 LLaMA-7B 實驗混在一起。

把 KV transfer 從 16-bit 改成 4-bit 後，通信時間由 584 ms 降到 133 ms；prefill 是 684 ms 對 698 ms，decode 是 1108 ms 對 1126 ms，幾乎沒變。整體 throughput 從 2450 增加到 3292 tokens per second，大約是 1.34 倍。這裡可以看到，即使 element 的 bitwidth 變成四分之一，系統 throughput 也不會自動變四倍，因為其他運算和排隊成本仍然存在。

品質方面，Table 2 測了 CoQA、TruthfulQA 和 GSM8K。最大的絕對分數下降，是 LLaMA-13B 的 GSM8K，從 22.34 到 21.29，差 1.05 個百分點。如果除以原來的 22.34，則大約是 4.7% 的相對下降。

這個區分很重要。正文寫 accuracy drop below 2%，但不能把它理解成所有測試的相對下降都小於 2%。我們用表格的原始數值來說比較準確。

Table 2、6、7 的每一格在後面兩頁。這裡先記 PPL 的相對變動小於 1%，ROUGE 大約落在 0.911 到 0.975。這些結果支持測試範圍內的影響不大，但不代表完全無損，或其他模型和任務也一定一樣。

來源：Table 2、Appendix I、Tables 6–8，論文第 7、16–17 頁。1.34 倍與 4.7% 為依表格數值計算。

備註：PPL 是 perplexity，通常越低代表模型對測試序列的預測越好。這裡 ROUGE 的 reference 是 16-bit 模型輸出，衡量的是輸出相似度，不是直接衡量回答的事實正確性。Table 2 的 LLaMA-7B GSM8K 從 13.23 到 12.54，相對下降約 5.2%；「最大的 1.05」指絕對百分點下降。


## 第 29 頁｜Task Scores under 4-bit KV Transfer

Table 2 的格子在這一頁。CoQA，7B 從 63.95 到 64.58，13B 從 66.35 到 66.54，4-bit 反而略高。TruthfulQA，7B 從 30.64 到 30.13，13B 從 29.68 到 29.34。GSM8K，7B 從 13.23 到 12.54，13B 從 22.34 到 21.29。

絕對分數掉最多的是 13B 的 GSM8K，1.05 分，相對大約 4.7%。7B 的 GSM8K 相對大約 5.2%。正文說 drop below 2%，比較接近這些絕對百分點，不是每一個相對下降都小於 2%。

來源：Table 2，論文第 7 頁。相對變化由表格計算。

## 第 30 頁｜PPL and ROUGE under 4-bit KV Transfer

Table 6 是 perplexity，16-bit 在前、4-bit 在後，越低越好。WikiText2：7B 是 3.53 / 3.55，30B 是 2.73 / 2.75。PTB：7.46 / 7.42，以及 6.49 / 6.55。CBT：7.66 / 7.70，以及 6.31 / 6.30。變動都在大約 1% 以內，而且 PTB 的 7B、CBT 的 30B 還略降。

Table 7 用 16-bit 輸出當 reference，看 4-bit 輸出的 ROUGE-1、2、L。WikiText2，7B 是 0.962 / 0.941 / 0.955，30B 是 0.942 / 0.928 / 0.941。PTB，7B 是 0.975 / 0.950 / 0.971，30B 是 0.928 / 0.911 / 0.928。CBT，7B 是 0.925 / 0.912 / 0.925，30B 是 0.946 / 0.931 / 0.937。

最低的 0.911 是 PTB、30B 的 ROUGE-2；最高的 0.975 是 PTB、7B 的 ROUGE-1。這個 ROUGE 量的是和 16-bit 輸出有多像，不是回答是否符合事實。

來源：Appendix I、Tables 6–7，論文第 16 頁。

## 第 31 頁｜Experimental Setup and Baselines

接著進入主要的 end-to-end evaluation。模型是 LLaMA-30B，workload 分成 coding 和 conversation，使用 Azure Conversation dataset 裡的 request 特徵，再按照指定的 request rate，用 Poisson process 產生到達時間。也就是說，它有真實資料的 workload 特徵，但到達時間是合成的，不是完整重播線上的所有時間變化。

硬體有兩個環境。Cloud 這邊是 Vast.ai 上租的 32 張 GPU，包含 A6000、A5000、A40 和 3090 Ti，論文報告的總租金是每小時 13.542 美元。另一邊是 8 張 A100-80GB 的 in-house server，作者用相同 GPU 的租金估算成每小時 14.024 美元。

HexGen 和 ThunderServe 使用相同的異質 cloud 環境。vLLM 和 DistServe 則跑在 A100 server 上。因此，跟 HexGen 比較，較能看同一批異質硬體上不同系統的效果；跟 vLLM、DistServe 比較，回答的是接近預算下，整套系統加上硬體選擇的成本效益。

這些價格是論文的實驗設定，不是現在的即時報價，也不是完整包含所有維運項目的 total cost of ownership。

來源：Section 5.1、Table 1，論文第 1、8 頁。

## 第 32 頁｜Reading SLO Attainment and Latency Deadlines

在看曲線之前，先把指標講清楚。

TTFT 是 time to first token，從 request 到達，到第一個 output token 出現的時間，會受到排隊和 prefill 影響。TPOT 是 time per output token，這篇指 decode 期間後續 output tokens 的平均生成時間，不是保證每一個 token 都具有相同延遲。E2E latency 則是整個 request 從到達到完成的時間，包含排隊、推論以及跨 phase 傳輸的影響。

SLO attainment 是符合指定 deadline 的 request 比例。論文分別評估 TTFT、TPOT 和 E2E，所以看到 99% attainment 時，要先確認是對哪個指標的 deadline 而言。

橫軸 SLO scale 則是把 deadline 表成 A100 execution-latency reference 的倍數。往右代表要求變寬鬆，所以通常越容易達標。比較兩個系統時，要固定 request rate 和目標 attainment，再看哪個系統需要比較小的 deadline。

例如兩條曲線都要達到 90%，baseline 需要 20 秒，ThunderServe 需要 10 秒，那 deadline ratio 就是兩倍。這不等於平均 latency 降低兩倍，也不代表每一個 request 都快兩倍。後面提到的 latency deadline improvement，都是用這個角度理解。

來源：Sections 2、5.1，論文第 3、8 頁。20 秒與 10 秒為講解用假設例子，不是論文量測值。

## 第 33 頁｜Cloud SLO Attainment: ThunderServe vs. HexGen

這張圖先比較同一個 cloud GPU 環境裡的 ThunderServe 和 HexGen。

上排是 coding，下排是 conversation。每一欄對應不同的 request arrival rate，所以比較時要先看子圖上方的數字，不要把不同 load 的曲線直接拿來互相比。圖中也同時畫了 TTFT、TPOT 和 E2E；我們這裡先抓 E2E 的整體趨勢。

在相同的 request rate 和目標 attainment 下，ThunderServe 通常需要比較短的 deadline。正文報告，coding 的 E2E deadline ratio 最高 1.8 倍、平均 1.4 倍；conversation 最高 1.4 倍、平均 1.3 倍。分子是 HexGen 所需的 deadline，分母是 ThunderServe 所需的 deadline。

作者的解釋是，phase splitting 降低 prefill 和 decode 互相干擾的情況，再配合不同 workload 的資源分配，所以兩個 phase 的服務品質都能改善。當 request rate 增加、排隊壓力上來時，要達到同樣的 attainment，通常也需要更寬鬆的 deadline。

來源：Section 5.2、Figure 7，論文第 8–9 頁。

備註：原圖 legend 把 TTFT 寫成 TTPT；正文的指標定義是 TTFT，報告時沿用正文用語。

## 第 34 頁｜Cost Efficiency: Cloud vs. In-House

這一頁換成接近租金預算的比較。ThunderServe 使用 32 張 cloud GPUs，DistServe 和 vLLM 則使用 8 張 A100。

正文報告，在這個比較範圍裡，E2E latency deadline 的 ratio 最高是 2.5 倍，平均是 1.8 倍。還是跟上一頁一樣，要在相同 request rate 和相同目標 attainment 下讀這個 ratio。

作者認為一個重要原因是，在這組預算與部署下，cloud 可以放到 12 個 phase replicas，而 in-house 的 DistServe 配置是 4 個。雖然單張舊 GPU 不如 A100 快，但更多 replicas 可以提供更多整體並行服務的能力，再靠排程把不同 GPU 放到適合的位置。

這裡的 12 個 replicas，包含 prefill 與 decode replicas，不是 12 組各自獨立的 prefill-decode 配對。此外，這是 system-plus-hardware 的結果，不能把差距全部歸因於某一個排程演算法，也不能據此推論任何雲端方案都一定比 A100 便宜或更快。

來源：Sections 5.2–5.3、Figure 8、Table 3，論文第 9–10 頁。

備註：摘要寫 latency deadline 平均改善 1.5 倍，Section 5.2 的 cloud-vs-in-house 比較寫平均 1.8 倍。它們是不同摘要範圍的敘述，不能把平均值混用；本頁引用的是 Section 5.2 的這組比較。

## 第 35 頁｜End-to-End System Throughput

這張圖看 throughput。ThunderServe 被 normalize 成 1，所以其他系統的柱子越低，代表相對於 ThunderServe 的 throughput 越低。柱子上標的倍數，則是 ThunderServe 除以那個 baseline 的 throughput。

這裡先提醒，四個系統不是全部使用相同硬體。ThunderServe 和 HexGen 使用同一組異質 cloud 環境，共 32 張 GPU：8 張 A6000、8 張 A5000、8 張 A40 和 8 張 3090 Ti。DistServe 和 vLLM 則使用一台配備 8 張 A100-80GB 的 in-house server。

作者對齊的是接近的 GPU 租用價格預算，不是相同 GPU 數量或相同總算力。Cloud 配置在論文中的租金合計為每小時 13.542 美元；in-house 的 8 張 A100，則以「租用同樣 GPU 要多少錢」估算為每小時 14.024 美元，作為預算對照。這不是先把硬體換算成 FLOPS，再根據算力推估報價。

也要區分價格與效能數據：租用價格用來建立預算比較基準；圖上的 throughput 則是實際執行實驗得到的系統表現，不是根據報價或理論算力推算出來的。因此，和 HexGen 的比較是在相同硬體環境下看不同系統的整體效果；和 DistServe、vLLM 的比較，則是在接近租用預算下看「系統加上硬體部署」的整體效益。後者的 GPU 型號、數量與網路條件都不同，不能把差距全部歸因於 ThunderServe 的演算法。

跟相同 cloud 環境的 HexGen 比，coding 是 1.5 倍，conversation 是 1.3 倍。跟 in-house 的 DistServe 比，則分別是 1.5 倍和 2.1 倍。

Figure 9 另外標了跟 vLLM 比的結果，coding 是 1.7 倍，conversation 是 2.3 倍。這裡有一個論文內部的不一致：摘要說最高 throughput 改善 2.1 倍，但圖上 vLLM 的 conversation 比較寫 2.3 倍。

所以我這裡不把它們壓成一個「全篇最高幾倍」的說法，而是保留每個 baseline 的具體結果。能確定的趨勢是，在這兩個 workload 與設定下，ThunderServe 的整體 throughput 都比圖中 baselines 高。

來源：硬體配置與價格基準見 Section 5.1；throughput 結果見 Section 5.2、Figure 9，論文第 9 頁；與摘要的差異見論文第 1 頁。

備註：上述 in-house 價格是等效 GPU 租用價格的估算，不是完整的自建機房總成本分析，不能直接當成已計入採購、電力與維運的成本。

備註：Figure 9 是 normalized system throughput，不能把縱軸的 1.0 解釋成每秒 1 個 request。正文沒有在這張圖清楚交代一個固定 attainment 門檻，因此不另行把它命名為「99% SLO goodput」。

## 第 36 頁｜Deployment Plans Found on the 32-GPU Cluster

前面一直說部署會因為 workload 改變，這一頁用作者實際找到的方案來看。

同樣是 32 張 GPU，coding 的部署有 8 個 prefill replicas 和 4 個 decode replicas；conversation 則是 4 個 prefill 和 8 個 decode。總數都是 12，但 phase 分配不一樣。

再看 A40 的例子。Coding 時，8 張 A40 切成四個 prefill replicas，每個 replica 用兩張 GPU，配置是 TP=2、PP=1。Conversation 時，6 張 A40 支援三個 prefill replicas，剩下 2 張 A40 則形成一個 decode replica，配置改成 TP=1、PP=2。

另一個例子是 mixed replica：2 張 A5000 加 2 張 3090 Ti，採用 TP=2、PP=2。可以理解成兩個 pipeline stages，各 stage 裡的兩張同型號 GPU 做 TP，stage 之間再透過 PP 接起來。

這頁也提醒我們，這是針對不同 workload 找出的完整 deployment plans，包含 parallel configuration 的改變。不能把這兩份 plan 的所有差異，都說成前面那個只做 phase flip 的 lightweight re-scheduling 能直接做到。

來源：Table 3、Appendix F，論文第 9、15 頁。


## 第 37 頁｜Full Deployment Plans from Table 3

上一頁只舉了 A40 和一組 mixed replica。Table 3 的完整列在這裡。

Coding 的 prefill 有四列：8 張 A40，TP=2、PP=1，4 個 replicas；4 張 A5000，TP=4、PP=1，1 個；4 張 A6000，TP=2、PP=1，2 個；2 張 A5000 加 2 張 3090Ti，TP=2、PP=2，1 個。Decode 有三列：4 張 3090Ti，TP=2、PP=2，1 個；4 張 A6000，TP=1、PP=2，2 個；另一組 2 張 A5000 加 2 張 3090Ti，TP=2、PP=2，1 個。合計 8 個 prefill、4 個 decode。

Conversation 的 prefill 是 6 張 A40，TP=2、PP=1，3 個，加上一組 mixed，TP=2、PP=2，1 個。Decode 是 4 張 3090Ti 一個、2 張 A40 一個、4 張 A5000 一個、8 張 A6000 四個，再加另一組 mixed 一個。合計 4 個 prefill、8 個 decode。兩種 workload 都是 12 個 replicas。

來源：Table 3、Appendix F，論文第 9、15 頁。

## 第 38 頁｜Tabu Search: Scheduling Convergence

搜尋 deployment plan 本身需要多久？這張圖測試 16、24 和 32 張 GPU 的情況。

橫軸是 search time，縱軸是搜尋過程裡估計的 SLO 表現。三種規模大約分別在 21、36 和 54 秒收斂。因為是離散地找到比較好的候選方案，所以曲線會呈現階梯狀，而不是每秒都連續變好。

這個搜尋是在初次部署模型之前執行的，不是每進來一個 request 都跑一次。若服務會持續跑好幾小時，幾十秒的初始規劃成本相對容易接受。

不過這裡的數字是 scheduling time，不包含把所有模型權重載入 GPU 的時間。而且圖中縱軸是 estimated SLO，也不是每一步都真的部署上去量測。它支持的是在這幾個實驗規模內，搜尋成本還算可控，不能直接外推成上千張 GPU 也會一樣快。

來源：Section 5.4、Figure 10，論文第 10 頁。

## 第 39 頁｜Lightweight Re-scheduling after GPU Failures

這個實驗模擬一台有 4 張 A6000 的 instance 離線，總共移除了兩個 decode replicas。

圖上比較四種情況：GPU 離線之前、離線後做完整 re-scheduling、離線後做 lightweight re-scheduling，以及離線後完全不調整。可以看到，在測試的 workload 裡，lightweight 的 SLO 曲線接近 full re-scheduling，也比完全不調整好。不過，這不代表它能把少掉 GPU 的影響全部消除，離線前後的資源量畢竟不同。

Appendix G 也給了具體例子。Coding 原本是 8 個 prefill、4 個 decode，少掉兩個 decode 後變成 8:2；系統再把一個使用 4 張 A5000 的 prefill replica 改成 decode，因此變成 7:3。Conversation 則從 4:8，經過故障變成 4:6，再翻轉一個使用 2 張 A40 的 prefill replica，變成 3:7。

再看調整成本。Table 4 把 full re-scheduling 拆成搜尋 54（正負 5）秒，加上重新載入權重 103（正負 10）秒，合計 157（正負 13）秒。Lightweight 的搜尋是 13（正負 2）秒，reload 是零，所以整段也是 13 秒。用 157 除以 13，大約是 12 倍的差距。

所以「zero overhead」不能拿來描述整個調整流程。準確的說法是，不需要重新載入模型權重，但重新搜尋 phase 和 routing 仍要時間；這張表也不是完整的故障偵測到所有 request 恢復的時間保證。

來源：Section 5.4、Figure 11、Table 4、Appendix G，論文第 10、16 頁。7:3、3:7 與約 12 倍依文中數量計算。

## 第 40 頁｜Ablation: KV Cache Compression and Orchestration

這張 ablation 想回答，通訊壓縮和 routing 各有多重要。

先看完整的 ThunderServe，也就是同時有 KV compression 和 prefill-decode orchestration 的版本。拿掉 KV compression 後，兩種 workload 的 SLO 表現都變差，正文描述單次 request 的 overhead 約變成 1.3 倍。

接著，作者在已經沒有 compression 的情況下，再把原本的 orchestration 換成 random dispatching，表現又進一步下降。這跟前面的動機一致：在高度異質的網路上，隨機把 KV cache 送到某個 decode replica，可能選到非常慢的通訊路徑。

不過這個 ablation 是累積移除。它沒有提供「保留 compression、只拿掉 orchestration」的第四種組合，所以不能把兩個元件的獨立貢獻完整拆開，也不能把兩個倍數直接相乘。

正文雖然提到另外 4 倍的 performance degradation，但沒有在這段清楚定義對應的量測量和比較門檻。這裡以圖上可以確認的 SLO 曲線惡化來說明，不把它直接講成 throughput 下降四倍。

來源：Section 5.4、Figure 12，論文第 10 頁。

## 第 41 頁｜Simulator and Alpha-Beta Model Accuracy

因為整套搜尋很依賴 estimated performance，所以作者也檢查模擬和實測到底接不接近。

左邊是 LLaMA-30B 在不同 SLO scales 下的 attainment。實測和估計分別是 0 對 0、26 對 24、78 對 80，以及 100 對 100。也就是圖上這四個點，最多差 2 個百分點。

右邊是不同 batched token sizes 下的 KV communication latency。實測和估計分別是 30 對 30、34 對 34、41 對 42，以及 60 對 58 毫秒。在這幾個點裡，最多差 2 ms。

這說明它的 simulator 和 alpha-beta model，在作者測試的範圍內有一定可信度。不過這是有限的 micro-benchmarks，不能把「最多 2 ms」當成對所有模型、所有網路壅塞情況都成立的誤差上界。尤其線上流量變動很大時，是否還能維持這種準確度，需要另外驗證。

來源：Appendix J、Figure 19，論文第 17 頁。最大差值依圖中四個配對數值計算。

## 第 42 頁｜Discussion: Scope and Open Questions

這一頁是我根據論文做的整理和討論，不是作者額外跑過的實驗結果。

首先，ThunderServe 把一個很大的部署搜尋問題變得可以實際求解，這是它的優點。不過 tabu search 和受限制的 TP、PP 枚舉，都不保證找到全域最佳；而且搜尋分數也受到 cost model 準確度影響。

第二個取捨是 adaptation。保留 grouping 和 parallel configuration，確實大幅減少 reloading 成本；但如果 workload 變化很大，或網路結構明顯改變，單純翻轉 phase 可能已經不夠。

第三個是結果適用範圍。主要 end-to-end 實驗是 LLaMA-30B、兩類 workload，以及一套 32-GPU cloud setup。比較新或不同架構的模型、不同 context length、不同網路狀況，仍需要再驗證。Routing 的容量限制與負載如何影響 pairwise score，論文也沒有完全寫清楚，這會影響重現。

我覺得可以延伸的一個問題是：服務什麼時候應該繼續做 lightweight adjustment，什麼時候值得付出搬權重、重新分組的成本？例如預測這個 workload shift 會持續多久，再比較「沿用較差配置的累積損失」和「重部署的一次性成本」。這是從本文取捨延伸的研究方向，不是 ThunderServe 已經解決的功能。

來源：報告者分析，依據 Sections 3–5。

## 第 43 頁｜ThunderServe: Contributions and Evaluation Findings

最後整理 ThunderServe 的貢獻。

它把 phase splitting 放進異質 cloud 的部署問題裡考慮：哪些 GPU 放在一起、每份 replica 負責哪個 phase、裡面怎麼做 TP 和 PP，以及 request 要怎麼走，都由同一個兩層最佳化流程串起來。

服務上線之後，它用比較受限的 lightweight re-scheduling，調整 phase 和 routing，避免每次都重新載入模型。同時也用 KV cache communication compression，降低 prefill 和 decode 之間的資料傳輸成本。

實驗方面，跟 DistServe 比，coding 和 conversation 的 throughput 分別是 1.5 倍和 2.1 倍；在接近租金預算的 cloud-vs-in-house 比較裡，E2E deadline ratio 最高到 2.5 倍。這些結果要放在各自的 workload、baseline 和 SLO 條件下理解。

我認為這篇最值得帶走的觀點，是在異質環境裡，GPU 的計算能力、記憶體頻寬和網路不能分開決策。Prefill-decode disaggregation 提供了更多分工空間，但要把通訊、部署和線上調整一起處理，才能把這個空間轉成實際效益。

來源：Sections 5.2、6、Figure 9，論文第 9–10 頁。

## 第 44 頁｜Q&A

以上是 ThunderServe。投影片上留的三個討論方向是 phase splitting、scheduling，以及 KV transfer。

可以接著問：在我們自己的硬體和網路條件下，什麼時候值得把 prefill 和 decode 拆開；搜尋找出的部署，有哪些限制沒有寫進印出的 routing 式子；以及 4-bit KV transfer 省下的時間，和模型品質的損失要怎麼一起看。

---

## 報告前快速核對

- 「一個 replica」是一組 GPU 共同承載一份模型，且被指定為一個 phase；不是每張 GPU 都各自有一份完整模型，也不是一組完整 P/D pair。
- 「deadline 改善幾倍」是固定 request rate 與目標 attainment 後的 deadline ratio，不能換成平均 latency 改善。
- 「4-bit KV transfer」不等於 4-bit weights 或持續使用 4-bit KV 做運算；dequantization 也不代表無損。
- 「1.05 percentage points」和「相對下降 4.7%」是不同算法；Table 2 的 below 2% 敘述不可直接解釋成相對下降。
- 「無須 reload」只代表權重 reloading 是零；lightweight re-scheduling 仍約需 13 秒。
- Figure 9 的 vLLM conversation 標 2.3 倍，但摘要寫最高 2.1 倍；口述用具體 baseline 的結果，保留這個不一致。
- Figure 5 的箭頭比例、routing 式子的缺漏，以及 Eq. (1) 未列 layer 數，都是本地 PDF 的表述限制；不把補充解釋冒充作者已寫出的完整實作。
