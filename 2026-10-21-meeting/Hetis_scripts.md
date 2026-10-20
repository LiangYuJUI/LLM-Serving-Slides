# Hetis 中文講稿

這是獨立簡報，對應 `2026-10-21-Hetis.tex`。投影片頁腳是 1/39 到 39/39，講稿標題用同一套頁碼，不和 ThunderServe 相加。第 01–02 頁是開場，第 03–36 頁是 Hetis 正文，第 37–38 頁是和 ThunderServe 的對照與後續問題，第 39 頁是 Q&A。

依據為本地 `SC25_Hetis.pdf`，標題為 *Hetis: Serving LLMs in Heterogeneous GPU Clusters with Fine-grained and Dynamic Parallelism*，首頁標示 arXiv:2509.08309v1，2025-09-10，SC ’25。以下「論文第幾頁」若出現，指 PDF 實際頁碼，不是投影片頁碼。每頁正文可直接口述；「來源」與「備註」供準備時查閱，不必念出。公式頁有為了說明而做的符號及單位整理，已與原文逐字公式區分。

## 第 01 頁｜Title

今天介紹 Hetis。它處理的是 heterogeneous GPU cluster 上的 LLM serving：同一層裡的 dense computation 和 decode attention，不一定適合放在同一組 GPU 上。

接下來會先看記憶體和計算為什麼會失衡，再看 Primary worker、head allocation 和 KV cache 管理，然後看實驗。最後用很短的篇幅對照 ThunderServe，並留下可以繼續做的問題。

## 第 02 頁｜Presentation Roadmap

這份簡報分成四段。第一段是背景：KV cache 怎麼被粗切分浪費，以及 MLP 和 attention 對 GPU 的需求為什麼不同。

第二段是方法：怎麼選 Primary parallelism，怎麼按 head 分配 attention，以及線上怎麼管理 KV cache。第三段是實驗，看 latency、可用 cache、敏感度和 overhead。第四段整理主要發現，並把 ThunderServe 的 phase-level 切法和 Hetis 的 head-level 切法放在一起討論。

## 第 03 頁｜Coarse Splitting Wastes KV Cache Capacity

先從記憶體問題看起。Hetis 和 phase splitting 一樣在處理 heterogeneous GPU serving，不過切入點更細：如果一個 Transformer layer 裡，不同運算適合的 GPU 不一樣，那我們有沒有必要讓它們全部綁在同一組 GPU 上？

先看這張圖左邊的 phase splitting。Prefill 和 decode 各自有模型副本，decode 能容納多少 request，會受到 decode worker 剩餘 KV cache 空間限制。例如論文用 FP16 的 7B 模型說明，權重大約占 14 GB，放在 24 GB 的 RTX 3090 上，粗略只剩 10 GB 可以放 KV cache。這是簡化估算，實際還有其他 runtime 開銷。即使 prefill 那邊有空間，也不代表 decode 可以直接利用。

右邊是 parameter splitting，把模型權重切到不同 GPU。它可以依照運算速度調整工作量，但權重、運算和 KV cache 的位置通常仍然綁在一起。如果按照計算能力切分，有可能一張 GPU 的 cache 已經滿了，另一張卻還有空間。

所以這裡的問題不是叢集完全沒有記憶體，而是現有配置讓一部分記憶體用不上。Hetis 想把 dense computation 的配置，和 decode attention、KV cache 的配置拆開決定。

來源：Section 2.3、Figure 1。


## 第 04 頁｜Measured GPU Gaps and a Partition Example

這一頁補 Table 1。測試是 OPT-2.7B，時間是走完所有 layer 的一次 iteration。Prefill 用 3 個 requests，decode 用 25 個。

A100、3090、P100 的記憶體是 80、24、12 GB。Prefill 時間是 0.06、0.147、1.47 秒；decode 是 0.0097、0.0143、0.077 秒。

論文給的倍數是：prefill 階段 A100 比 3090 快 2.45 倍、比 P100 快 24.5 倍；decode 階段是 1.47 倍和 7.93 倍。容量是 3090 的 3.33 倍、P100 的 6.67 倍。

接著的例子是用 decode 算力切 FP16 OPT-2.7B：大約 40% 的參數和 KV cache 在 3090，60% 在 A100。這時 3090 最多剩 18.6 GB 給 KV cache，A100 還有 44.1 GB 空著。前一頁的 10 GB 是 FP16 7B 放在 3090 上的另一個例子，不要和這組 2.7B 混在一起。

來源：Section 2.2、Table 1、Section 2.3。倍數是論文對這些格子的比較。

## 第 05 頁｜MLP and Attention Scale Differently

為什麼可以拆開？這張圖比較 Llama-70B 在不同 GPU 上執行一層 decode 的時間，context length 是 1000。左邊看 MLP，右邊看 attention。可以看到，P100 和 A100 在 MLP 上的時間差距，比 attention 上的差距大很多。

MLP 需要做大量帶有模型權重的矩陣運算，較新的 GPU 通常有明顯優勢。Decode attention 則要讀取歷史 K、V；它對 KV cache 的存取需求很重要，不同 GPU 的相對表現也就不一定和 MLP 相同。這不是說 attention 沒有計算成本，而是兩類運算對硬體的需求不同。

因此，把慢 GPU 加進 dense computation，不一定划算：它提供的計算貢獻可能有限，卻增加切分、同步或傳輸成本。但這張 GPU 的記憶體仍然可以拿來放 KV cache，也能執行部分 attention。

Hetis 的出發點就是，挑選一部分 GPU 處理 dense work，再讓更大的 GPU pool 共同分擔 decode attention。這個判斷來自圖中的測試設定，不能直接說所有 attention 在任何 GPU 上都一樣快。

來源：Section 2.4、Figure 2。

## 第 06 頁｜Primary Workers and Attention Workers

這裡先把兩種 worker 的分工講清楚，後面比較不容易混淆。Primary worker 存放模型權重，負責 QKV projection、output projection 和 MLP。Prefill 和 decode 都還是需要它；prefill attention 也由 Primary 執行。到了 decode，Primary 會保留一部分 attention，其他部分才交給 Attention worker。

Attention worker 主要負責分配給它的 decode attention core，以及對應的 KV cache。這裡的 core 就是公式裡，用 Q 和 K 算 attention scores、做 softmax，再對 V 加權的那一段。Q、K、V 已經由 Primary 的 projection 算好了，所以 Attention worker 不需要另外存整份模型權重。

「Parameter-free attention」要特別小心：它指的是這段 core 沒有額外的模型權重，不是整個 attention block 沒有參數。前面的 QKV projection 和後面的 output projection，仍然都有可訓練權重。

所以，Hetis 不是把 Primary 當成 prefill worker、Attention worker 當成完整的 decode worker。它是在 decode 的同一層裡，讓兩種 worker 合作；模型的 dense 計算仍然要經過 Primary。

來源：Sections 2.4、3.2、4；attention core 的用語為講解時釐清。

## 第 07 頁｜Hetis System Architecture

有了 worker 的分工，再來看整體架構。圖裡有四個主要元件，可以分成部署前的規劃，以及服務過程中的配置和搬移。

Parallelizer 決定哪些 GPU 當 Primary，並選擇 DP、PP、TP。DP 是多個 serving instance 分擔不同 requests；PP 是把不同層分給不同 stage；TP 則是在一層內切分張量運算。沒有被選進 Primary 的 GPU，可以成為共用的 Attention-worker pool。

Profiler 負責量測和建立成本模型，估計某張 GPU 接到一定數量的 heads、一定大小的 KV cache 時，要花多少計算時間，以及遠端執行會產生多少通訊時間。

服務開始之後，Dispatcher 根據這些估計，決定新 request 的 heads 放在哪裡。隨著 context 變長，原本的配置可能失衡，因此它也會選擇性地重新分配既有 requests。真正管理 head-level KV cache、搬移 cache shard 的工作，則交給 Hauler。

也就是說，Hetis 同時有比較慢、部署前做的 Primary 規劃，以及比較細、執行中會改變的 attention 配置。

來源：Section 3、Figure 3。

## 第 08 頁｜Hierarchical Search for Primary Parallelism

先看部署前怎麼挑 Primary。直接枚舉每張 GPU 的角色，以及所有 DP、PP、TP 組合，搜尋空間會很大，所以 Hetis 採用分層搜尋。

第一步先考慮 serving instance 的切法，也就是 DP。它把各種型號的 GPU 平均分到不同 instances，並排除剩餘 cache 容量不夠的候選配置。接著，在每個 instance 裡，先把同一類 GPU 視為一個統一的 pipeline stage，透過不同 stage 的層數配置來估計計算成本。

然後，它會從較低階的 GPU 開始嘗試移除：如果少了這張卡，dense computation 的估計時間只增加一點點，就有機會把它移出 Primary。這張卡還是會參與服務，只是改成 Attention worker，釋放原本放模型權重的空間。

最後才更細地探索每個統一 stage 內的 TP、PP 組合，並把計算和通訊成本一起算進去。這個流程的重點，是先縮小搜尋空間，再做比較完整的成本評估；它是一個 heuristic，不是把所有配置都找完的全域最佳解。

來源：Section 4.1、Figure 4。

## 第 09 頁｜Primary Selection Objective and Pruning Rule

這頁用公式把剛才的搜尋補完整。上面的 sigma 代表模型參數怎麼放，以及 DP、PP、TP 怎麼設。目標是讓預估的總成本最小，包含 computation 和 communication；模型與 workload distribution 都會影響這個成本。

下面是移除 GPU 的規則。分子是少掉候選 GPU 之後的估計計算成本，分母是原本的成本。如果比值不超過一加 Delta，就允許這個移除；論文使用的 Delta 是 0.05，也就是最多接受約百分之五的估計增加。

例如原本估計是 100 個時間單位，拿掉一張較慢的 GPU 後變成 103，就符合這個規則。這是幫助理解的例子，不是論文的實測數字。它願意付出這一點 dense computation 成本，換取該 GPU 成為 attention-only worker 後能提供的 cache 空間。

這裡的 C_p 和上面的完整 C 要分清楚。C_p 用理想 scaling 假設，估計最慢 stage 的計算時間；這一步還沒有算 communication。後面評估保留下來的配置時，才使用更完整的成本模型。因此，不能把這個百分之五解讀成實際端到端 latency 一定只增加百分之五。

來源：Section 4.1、Eq. (1) 與 GPU pruning 規則。

## 第 10 頁｜Why Split Attention by Head?

接著看 attention 要沿哪個維度切。第一種是 batch-wise，把整個 request 丟給某張 GPU。實作比較直接，但粒度很粗，尤其 requests 的 context length 不同時，分到相同數量的 requests，不代表拿到相同工作量。

第二種是 sequence-wise，把同一個 request 的歷史 tokens 分到不同 GPU。這樣可以切得比較細，但不同 GPU 都需要收到 query，而且最後必須正確合併跨 sequence shards 的 softmax 統計與輸出，不能把各段的局部結果直接接起來。

Hetis 選的是 head-wise。各個 head 原本就分別計算 attention，只要把對應的 Q、K、V 放在一起，就能獨立算完，再依模型的 head 順序組合輸出。這裡不需要跨 heads 做一次共同的 softmax。

下方實驗比較的是 communication overhead。在 Llama-70B、100 Gbps 的設定下，論文報告相對 sequence splitting，在百分之二十 offload 時有 2.68 倍通訊加速，四個 workers 時最高 3.55 倍。這些數字是通訊部分的改善，不能直接說整個 request 也快了 3.55 倍。

來源：Section 4.2、Figure 5。


## 第 11 頁｜Head-wise Attention as Printed

論文把 head-wise attention 寫成 Eq. (2)。一個 request 的輸出，是各 GPU 上那段 heads 的 result 依序 concat 起來。

每一段仍是 scaled dot-product：這組 heads 的 query 乘上對應 K 的轉置，除以根號 d，做 softmax，再乘 V。h 下標 i、上標 j、時間 t，是 request j 在 GPU i、時間 t 分到的 query heads。它被拿來當 Q、K、V 的下標，表示那一組 heads。

前面那頁的 attention core 是同一個 softmax，只是還沒寫成按 GPU 切開再接回去。因為每個 head 在一張 GPU 上就算完，所以不需要為了同一個 head 跨 GPU 合併 softmax。2.68 倍和 3.55 倍仍是通訊開銷的比較，不是這個式子本身的加速比。

來源：Section 4.2、Eq. (2)。

## 第 12 頁｜Dynamic Attention Placement Across Requests

這張示意圖用三個 requests 說明動態配置。每個 request 都有六個 heads，但 context length 分別是六、九、三，所以每個 head 需要的 KV cache 大小不同。

因此，Hetis 不要求所有 requests 都按照同一個固定比例切到 GPU 上。某個 request 可以多放一點在 Primary，另一個則多放一點到 Attention worker。配置時要看整張 GPU 已經承擔多少 heads、多少 cache，以及通訊成本。

這裡的 KV cache 會跟著對應的 head 走。某個 head 放在某張 GPU，這張 GPU 就需要它的完整歷史 K、V，才能算這一步 attention。算完之後，再把分散的 head outputs 收回來，接著執行後面的 output projection。

等 request 繼續產生 tokens，cache 會變大，配置也可能需要調整。Re-dispatching 只改需要搬的部分，原本位置還能沿用的 cache 就留下來。所謂 dynamic parallelism，改變的是運算與資料的放置位置，不是模型有幾個 heads，也不是把 attention 換成另一種近似演算法。

來源：Sections 4.2、5.3、Figure 6。

## 第 13 頁｜Head Integrity and Grouped-Query Attention

切 heads 還有一個限制：不能切到破壞模型本來的 Q、K、V 對應關係。這裡 H_Q 是 query heads 的數量，H_KV 是 KV heads 的數量，兩者的比值叫 r。

一般的 MHA，每個 query head 有自己的 K、V，所以 r 等於一。GQA 則是多個 query heads 共用同一組 KV head。Hetis 會把這一整組一起分配，所以每張 GPU 拿到的 query-head 數量，除以 r 之後必須是非負整數。

用投影片上的例子來看，如果有八個 query heads、兩個 KV heads，那 r 就是四。一張 GPU 可以拿零個、四個或八個 query heads，實際上就是分配零組、一組或兩組；不能任意拿三個或五個。這是教學用的例子，不是這次實驗模型的設定。

另外，每個被分配出去的 head 都保有自己的完整 context，所以不需要像 sequence splitting 那樣跨 GPU 合併同一個 head 的 softmax。GQA 的好處是減少 KV cache，但對 Hetis 來說，它也讓最小配置單位變粗。後面看最佳化公式時，就要把這個整數限制一起記住。

來源：Sections 4.2、5.2.1、6。

## 第 14 頁｜Profiling Decode Attention Time

要決定 heads 放在哪裡，首先要知道每種配置大概會跑多久。Figure 7 用 OPT-30B 的 micro-benchmarks，觀察 attention 時間和幾個因素的關係。

第一個觀察是，固定總 head 數和 cache 大小，只改變 request 數量時，執行時間在這個測試裡變化不大。也就是說，不能只用「這張 GPU 有幾個 requests」來估計它忙不忙，因為每個 request 的 heads 和 context length 可能差很多。

第二個觀察是，cache 越大，attention 時間大致跟著增加；而在 cache 大小固定時，query-head 數增加，也會增加執行時間。所以 Hetis 用兩個主要變數建立簡單模型：總 query-head 數，以及相關的 KV cache 量。

這是一個根據量測得到的近似模型。它的好處是計算簡單，方便放進線上配置問題；但不是說所有 batch、所有 kernel、所有 GPU 都必然遵守完全相同的直線。每種裝置仍然需要 profiling，下一頁就是模型的形式。

來源：Section 5.1、Figure 7。

## 第 15 頁｜Computation and Communication Cost Models

左邊的 tau 是 attention 計算時間，用 a 乘上 head 數 h，加上 b 乘上 cache 量 g，再加固定項 c。這三個係數是 profiling 擬合出來的，各 GPU 可以不同。h 是這張 GPU 上跨 requests 加總的 query heads，不是模型本身固定的 head 數。

中間的 rho 是通訊時間，用傳輸量 d 的線性項，再加一個固定成本。Attention 放到遠端 worker 後，Primary 要送 query、新產生的 K、V，還要收回 attention output。因此不能只看遠端 GPU 的 attention kernel 快不快，也要加上這些資料往返。

為什麼 d 是二加二除以 r，再乘 h？Query 和回傳的 output 各有 h 個向量，合起來是二 h；K、V 各有 h 除以 r 個向量，合起來是二 h 除以 r。這裡是在數向量，不是直接得到 bytes。要換成實際傳輸量，還需要乘上 head dimension 和每個元素的位元組數。

所以 gamma 是對應這個單位的傳輸成本係數，不能直接把它當成網路的 Gbps 數值。Primary 留在本地計算的 attention，不需要額外付出這組 Primary 到 Attention worker 的往返成本；遠端 worker 則必須一起考慮 tau 和 rho。

來源：Section 5.1、Eqs. (3)–(4)。備註：向量計數為使原式單位明確而採用的講解方式；這裡也不是說 Primary 的 TP／PP 沒有任何通訊。

## 第 16 頁｜Online Dispatch for Newly Arriving Requests

有了成本模型，新 request 進來時就可以決定配置。這頁先把既有 requests 的位置固定，只替新到的這批 requests 分配 heads，避免每次 arrival 都把所有工作重排。

第一行是更新負載。原本已經有 h 個 heads，再加上新分配的 x；cache 則是原本的 g，加上新 requests 帶來的量。每個 query head 對應多少 KV，要考慮 GQA 的 r；每個 head 又有 ell 個 context tokens，再把 K、V 都算進去，所以出現二除以 r。

下面的 z 可以想成所有參與 GPU 的完成時間上限。要求每張 GPU 的預估時間 f 都不能超過 z，再讓 z 盡量小，就等於想辦法縮短最慢的那一張。對遠端 Attention worker，f 會包含計算和通訊；對 Primary 上的本地 attention，則沒有這份額外的遠端傳輸。

其他限制有三個：不能超過各 GPU 的 cache 容量；每個新 request 的 heads 要完整分配；GQA 必須以整組為單位。這頁以 KV-vector 數量統一 g 和 M 的單位，是依原文前後定義整理的版本，不是原 Eq. (7) 的逐字轉貼。

來源：Sections 5.2.1–5.2.2、Eqs. (6)–(8)。備註：若以 bytes 實作，要再納入 head dimension、datatype 與本地 layers；這裡對已接納的新 request 要求完整分配，沒有補寫論文未交代的 admission policy。ell 是目前長度，還需處理之後的 cache 成長。


## 第 17 頁｜Printed Dispatch Constraints

這一頁改看論文印出來的式子，和前面整理過的 LP 分開。

Eq. (5) 的對象是所有正在服務的 request，集合是 S(t)。每張 GPU 分到的 heads 加總，要落在 0 或 H。H 是模型的 query-head 總數。0 表示這個 request 沒被分配，H 表示全部分完。

Eq. (6) 是容量：每張 GPU 上，query-head 數乘 context length 再加總，不能超過 r 乘 M_i 再除以 2。對象同樣是 S(t)。

Eq. (7) 只處理新到的 J(t)。目標是讓最慢 GPU 的 f_i 最小。(7b) 把既有 g_i 直接加上 x 乘 l，右端仍是 r M 除以 2。(7c) 要求新 request 的 heads 加總等於 H，沒有再寫 0。所以 Eq. (5) 和 (7c) 的寫法不完全一樣。

前面整理版用 z，並把 cache 統一成 KV-vector。這裡留著原文，是為了看到單位沒有完全對齊。

來源：Section 5.2、Eqs. (5)–(7)。H 就是前面寫成 H_Q 的 query-head 總數。

## 第 18 頁｜Closed Forms of Attention Time

f_i 在原文沒有獨立編號，寫在 Eq. (7) 後面。

Primary 沒有這段遠端傳輸。更新後的 head 數是原本的 h 加上新分配的 x，cache 是原本的 g 加上 (2/r) 乘上新 request 的 context 乘 heads。f 就是 a 乘 head 數、b 乘 cache、再加 c。

Attention worker 還要加通訊。head 數的係數變成 a 加上 (2 加 2/r) 乘 gamma；cache 項和 Primary 一樣；最後再加 c 和 beta。gamma 乘上的是這張 worker 更新後的全部 heads，所以每個 decode step 都會傳已經放在遠端的 heads，不只是剛到的 request。

這和前面 d 等於 (2 加 2/r) 乘 h 是同一套向量計數，只是這裡把計算和傳輸加在同一個 f 裡。投影片省掉時間下標 t；原文寫的是 h_i(t)、g_i(t) 和 x_i^j(t)。

來源：Section 5.2.2。

## 第 19 頁｜Dispatch Formulation: What the Paper Specifies

這一頁補充重現方法時要注意的地方。論文把配置描述為 linear programming，並說實作用 CVXPY 和 MOSEK。若先允許 x 是連續數值，剛才的 affine cost model 加上 z，確實可以寫成 LP。

但實際的 heads 不能分成小數，GQA 還要求整組分配。把 x 除以 r 必須是整數的限制保留下來，問題就有離散變數，不能直接當成一般連續 LP。這份論文沒有清楚交代，是求解時保留整數限制，還是先 relaxation 再 rounding；所以這裡不能替作者補出一個不存在於文中的演算法，也不能保證一般 LP 解會自然滿足 head integrity。

另一點是 cache 單位。原文 Eq. (7b) 把既有 g 和 query-head-token 數放在一起，但 Eq. (8) 以及剛才的 f_i 更新 g 時有二除以 r 的換算。再前面那頁整理過的 dispatch LP，把新舊 cache 都統一成 KV-vector 單位，讓 K、V 和 GQA sharing 的換算一致。

這些問題不影響我們理解它想做什麼：平衡時間、避免 cache 超量。但如果要自己實作，整數配置、記憶體單位，以及留多少空間給後續 decode，都是需要明確補足的細節。

來源：Sections 5.2、6。備註：公式一致性與 LP／整數問題的區分是講者對提供版本的分析，不代表作者公開實作一定沒有處理。

## 第 20 頁｜Re-dispatching to Balance Computation

只在 request 進來時分配一次，還是不夠。因為 decode 會持續增加 context，有些 request 很快結束，有些會生成很久，原本平衡的 GPU 可能逐漸出現 straggler。

投影片上的 f-star 是：在現有 requests S(t) 上，最小化最慢 GPU 的 f_i。唯一印出來的限制，是所有 GPU、所有 request 的 x 乘 l 加總，不超過所有 GPU 的 r M 除以 2 再加總。Head integrity 沒有在這個式子裡重寫。如果目前 attention 時間和 f-star 的偏差超過 Theta，就觸發 re-dispatching；預設門檻是百分之五十。原文沒有把這個偏差的正規化分母寫得很完整，所以這裡不自行補成某個精確百分比公式。

觸發後，先找 attention 最慢的 GPU，再找其中對時間貢獻最大的 request，針對這個 request 重新求配置。它不是直接把叢集所有 requests 全部搬一次，而是先處理最明顯的瓶頸。

重新分配之後，如果某些 heads 還在原本的位置，對應 cache 就直接沿用；只有改變位置的 shards 才需要搬移。這樣能降低調整成本，不過仍然會占用網路和裝置資源。因此門檻不能只追求越低越好，後面會看到它和搬移頻率之間的取捨。

來源：Section 5.3.1。

## 第 21 頁｜Re-dispatching to Relieve KV Cache Exhaustion

另一種觸發原因是記憶體：某張 GPU 的 KV cache 空間快用完了，但其他 GPU 還有剩。這時如果用全系統的 LIFO 或 LRU 挑 victim，可能剛好挑到一個根本沒有在這張 GPU 放 cache 的 request，那就無法解除真正的瓶頸。

Hetis 先把候選範圍縮到，確實有占用這張 GPU cache 的 requests，再在這個範圍內使用 LIFO 的想法，挑較晚進來的 request。論文用一個不等式判斷叢集還有沒有空間：所有 GPU 的 g_i 加總，要小於所有 GPU 的 r M_i 除以 2 再加總。成立的話，就嘗試把 victim 的部分 head groups 重新分配出去，而不是整份丟掉。

這和直接丟掉整個 request 的 cache，或把整份 cache swap 出去不一樣。它想保留還能沿用的部分，只搬為了騰出空間而必須搬的 shards。過程中也要顧到計算負載，不能解決記憶體問題後，又把某張卡變成非常慢的 straggler。

還有一個實作上要記得的限制：全叢集加起來有空間，不代表一定找得到合法配置。GQA 必須整組搬，單張 GPU 也需要裝得下對應的 cache。因此容量、配置粒度，以及計算平衡都要一起檢查。

來源：Section 5.3.2。備註：最後一段為離散配置限制的延伸說明。

## 第 22 頁｜Head-Level KV Management and Migration

前面說的是配置策略，這頁看 runtime 怎麼支援。原本 vLLM 用固定 token 數的 blocks 管理 KV cache；Hetis 進一步沿 head 維度拆分，讓 cache 可以跟著 head placement 移動。

這也代表索引不能只知道 request 和 token 在哪個位置，還要知道是哪一個 head。實作使用自訂 CUDA kernel 處理 cache 的存取，並利用多個 CPU cores 加速 block indexing。真正的 attention 計算則沿用 PagedAttention，讓各 worker 計算本地負責的 heads。

通訊部分使用 NCCL 的 point-to-point groups，在 Primary 和 Attention workers 之間傳遞對應資料。當既有 request 需要重新分配時，Hauler 再搬移相關的 head-level KV shards。

為了減少搬 cache 對正在執行的 inference 通訊造成干擾，論文把 migration 放到低優先權的 CUDA streams。但低優先權不是免費，也不是完全不會影響 latency；搬移仍然要讀寫資料、占用頻寬。這頁想強調的是，要支援細粒度配置，cache layout、索引、kernel 和通訊機制都需要一起配合，只有排程公式還不夠。

來源：Section 6。

## 第 23 頁｜Hetis Experimental Setup

接下來看實驗。主要叢集有十二張 GPU，分布在四台 hosts：一台有四張 A100-80GB，兩台各有兩張 RTX 3090，另一台有四張 P100。3090 的記憶體是 24 GB，P100 是 12 GB；不同型號的計算能力和容量差異都很明顯。

Host 之間使用 100 Gbps 的 LAN，host 內使用 PCIe。這個網路設定很重要，因為 Hetis 在 decode 過程中會反覆傳遞 attention 的輸入和輸出，不能把它當成只在 request 開始時傳一次資料。

模型方面，Llama-13B 和 OPT-30B 使用 MHA，Llama-70B 使用 GQA，所以可以觀察不同 KV sharing 結構下的效果。Workloads 有三類：ShareGPT，簡稱 SG，是聊天；HumanEval，簡稱 HE，是程式碼補全；LongBench，簡稱 LB，這裡用在長文章摘要。

比較對象是 Splitwise 和 HexGen，後面會說部署方式。要先記住，這是指定本地叢集中的效能比較，不是雲端租用成本的比較，也不是把 ThunderServe 的實驗環境原封不動搬過來。

來源：Section 7.1、Table 1。

## 第 24 頁｜Baselines and Evaluation Metrics

先用 Llama-70B 說明部署。Hetis 選 A100 和 3090 當 Primary，P100 當 Attention worker。HexGen 採用非對稱的 parameter splitting，依 GPU 類型配置 pipeline stages，stage 裡再做 tensor parallelism。Splitwise 則是作者在這個叢集上的實作：prefill 使用四張 A100 做 TP，decode 使用兩個 PP stages，分別在 3090 和 P100 上做 TP 等於二。

後面圖表有兩種不同的 normalization，不能混在一起。Figures 8 到 10 的縱軸是 normalized end-to-end latency，單位是秒除以 token；它仍然是有單位的時間指標，不是把某個 baseline 設成一的倍數圖，也不能直接叫它 TPOT。原文沒有把聚合與正規化的完整算式寫清楚。

橫軸是外部送進來的 request rate，也就是每秒幾個 requests。當負載繼續增加，latency 明顯上升，表示系統開始接近或超過可穩定服務的範圍。這裡沒有先指定一條固定 SLO，再計算 goodput，所以不能直接套用 ThunderServe 的 SLO attainment 解讀。

Figures 12、13 則是 P95 的比較，並以 Hetis 正規化成一；那時候柱子的高度才是相對 Hetis 的 latency ratio。

來源：Section 7.2、Figures 8–13。備註：不從上述 TP／PP 描述自行推定 Splitwise 每一張實體 GPU 的 instance replication 配置。

## 第 25 頁｜Llama-13B: Latency Under Increasing Load

先看 Llama-13B，三個小圖依序是 SG、HE、LB。讀這張圖時，先選定一個 workload，再在同一個 request rate 下比較三條曲線。縱軸越低，代表該負載下的 normalized E2E latency 越小。

這裡最值得看的，是曲線什麼時候開始快速往上升。Hetis 在三個 workloads 裡都把明顯上升的位置往右推，代表在這些測試條件下，可以承受比較高的外部請求量，才出現嚴重的 latency 增加。

這和前面的設計是連得起來的：低負載時資源可能還有餘裕；負載高起來之後，dense computation 的配置、attention 是否平衡，以及還有多少可用 KV cache，就會變得更重要。不過，這張圖本身是整個系統的結果，不能只靠它就精確分出每個元件貢獻多少。

另外，三個小圖的座標尺度不同，不要拿左圖和右圖相同的高度，當成同樣的 latency 或同樣的 request rate。這張圖支持的是負載承受能力的提升，不是每個 request、任何負載下都固定快同一個倍數。

來源：Section 7.2、Figure 8。備註：原論文此圖 LongBench 的橫軸單位文字有裁切；完整單位為 req/s，其他面板及正文可確認。

## 第 26 頁｜OPT-30B: Latency Under Increasing Load

這頁換成 OPT-30B，一樣是 MHA，但模型比前一頁大。讀圖方式不變：在每個 dataset 裡，固定橫軸的 offered load，比較 latency，以及曲線開始快速上升的位置。

這裡同樣看到 Hetis 可以把快速上升的位置推到較高的 request rate。模型權重變大之後，哪些 GPU 存權重、權重占掉多少空間，就會影響整個叢集還能提供多少 KV cache。只按照 dense computation 的速度切分，不一定能把每張 GPU 剩餘的記憶體利用好。

Hetis 讓 Attention worker 不需要存整份模型權重，又允許每個 request 的 heads 有不同配置，因此能使用固定分割下可能閒置的 cache。這是解釋結果的設計機制；它不是說有多少空間就一定能無成本地拿來用，仍然有 attention 計算與通訊成本。

這頁提供的證據是，優勢不只出現在 Llama-13B，也出現在這個較大的 MHA 模型。至於不同 dataset 之間的絕對 latency 差異，牽涉輸入、輸出長度等因素，不適合只用柱高或線高直接比較。

來源：Section 7.2、Figure 9。備註：原圖 LongBench 的橫軸標籤尾端不完整，單位同樣為 req/s。

## 第 27 頁｜Llama-70B: GQA End-to-End Results

接著換成 Llama-70B。和前兩頁不同，這個模型使用 GQA，多個 query heads 共用 KV heads，所以平均每個 query head 對應的 KV cache 比 MHA 少，但配置時也必須以完整的 groups 為單位。

在這個設定裡，Hetis 仍然維持較好的負載表現。A100 和 3090 負責 dense work，P100 提供額外的 decode attention 和 KV cache 容量。這表示，即使 GQA 已經降低了 KV cache 的需求，把不同模組分開配置，以及動態分享 attention，仍然可能有幫助。

論文對這組端到端實驗的總結是，相對 Splitwise，throughput 最高改善 2.25 倍；相對 HexGen，最高改善 1.33 倍。這是 Figures 8 到 10 相關實驗的最大結果，不是這一頁每個小圖都剛好有 2.25 倍，也不是每種 request 都會快這個倍數。

所以我們可以說，Hetis 在這些異質硬體、模型和 workloads 下，提高了系統可以承擔的服務負載。接下來要拆開看，這個優勢和可用 cache、單個 request 的尾端延遲，以及模組執行時間有什麼關係。

來源：Section 7.2、Figure 10；2.25×／1.33× 為該節對端到端實驗的摘要。

## 第 28 頁｜Maximum Usable KV Cache Space

這張圖直接看 usable KV cache。論文報告，Hetis 的最大可用 KV cache 容量，相對 baselines 最高可以增加到 1.87 倍。

這不是硬體突然多出記憶體，而是同樣的 GPU 記憶體裡，有多少能實際用來容納服務中的 request state。第一個來源是 Attention workers 不需要存整份模型權重，因此能留更多空間給 KV cache。第二個來源是動態配置，可以減少某張 GPU 已滿、另一張還有空間，卻因為固定分割而用不到的情況。

因此這個指標比單純把所有 GPU 的剩餘 bytes 加起來更有系統意義：配置、worker 角色和負載分布，都會影響記憶體能不能真正派上用場。

不過，1.87 倍的可用 cache 不等於 1.87 倍 throughput。能放更多 concurrent requests 之後，系統可能又遇到計算、記憶體頻寬或網路的限制。這張圖確認的是容量利用上的改善；效能改善要和前面的端到端結果一起看，不能把兩者當成同一個指標。

來源：Section 7.2、Figure 11。

## 第 29 頁｜P95 TTFT and TPOT on Llama-70B

前面看系統承受高負載的能力，這頁則在所有方法都還沒飽和的 request rate 下，比較尾端延遲。SG 是每秒 1.5 個 requests，HE 是六個，LB 是 0.8 個。

TTFT 是 request 送進來之後，到第一個 output token 出現的時間；TPOT 描述 decode 階段每個 output token 的時間。P95 是第九十五百分位，也就是關注比較慢的那一端，不是平均值。

這張圖以 Hetis 設為一，所以 baseline 的柱子如果是 1.47，意思是 baseline latency 是 Hetis 的 1.47 倍，不是延遲減少百分之一百四十七。論文報告，P95 TTFT 相對 HexGen 最高有 1.22 倍改善，相對 Splitwise 最高 1.47 倍；P95 TPOT 相對 baselines 最高改善 1.39 倍。

TTFT 的改善可以從 Primary 的選擇和 dense computation 配置來理解；TPOT 則還受益於把較慢 GPU 從不合適的 dense work 中移出，以及讓 attention 更平衡。這些結果說明，優勢不只是高負載時比較晚飽和，在選定的未飽和設定下，尾端延遲也有改善。

來源：Section 7.3、Figure 12。

## 第 30 頁｜MLP and Attention Contributions to Decode Latency

這頁再把 decode 的模組拆開看，左邊是 MLP，右邊是 attention，使用和上一頁相同的 request rates。論文報告，MLP 的 P95 latency 最高改善 1.29 倍，attention 最高改善 1.49 倍。

MLP 對應到 Primary parallelism 的選擇：哪些 GPU 真正適合一起執行 dense work、怎麼配置 TP 和 PP。Attention 則對應 head placement：同時考慮各 GPU 的計算能力、cache 負載，以及遠端通訊成本。

這裡有個 metric 定義需要注意。論文把模組時間定義為「最慢 pipeline stage 的時間，乘上 PP stage 數量」，再比較 P95。它不是逐一把所有 stages 在某次 request 上的實際時間相加，也不是整個 request 的端到端 latency。

所以這頁的 1.49 倍，應該明確說是這個實驗中的 attention module 改善，不能直接拿來當所有 workloads 的 E2E 加速。它提供的價值，是讓我們看到 dense work 和 attention 分別都有改善，支持不同模組使用不同 GPU 配置的設計方向。

來源：Section 7.3、Figure 13。

## 第 31 頁｜Dynamic Head and Cache Allocation

這張圖觀察執行過程中的配置變化。為了容易分析，這裡不是前面完整的十二張 GPU，而是用一張 A100 當 Primary、兩張 3090 當 Attention workers，服務 Llama-13B。

ShareGPT 的 arrival rate 依時間從每秒五個 requests，變成零，再變成 2.5，最後回到零。上面的 head 分配和下面的 cache 使用量，會跟著 arrival、持續 decode，以及 requests 完成而改變。Arrival rate 變成零，只代表沒有新 request 進來，前面尚未完成的 requests 仍然會繼續執行。

可以看到 A100 通常處理比較多 heads，但不同 GPU 都能有高的 cache 利用率。Head 數和 cache bytes 不是完全相同的量，因為不同 request 的 context length 不一樣。

低負載時，3090 的參與會比較晚開始，原因是遠端 attention 要付出傳輸成本。如果 A100 本地還能有效處理，立刻把 heads 分出去不一定比較快。這張圖呈現的是，Hetis 會根據當下負載，在本地執行與遠端利用計算、容量之間做調整，而不是每一步都強迫所有 GPU 平均分工。

來源：Section 7.3、Figure 14。

## 第 32 頁｜Re-dispatching Benefits and Cache Operation Costs

左邊比較 re-dispatching 和 LIFO，在 ShareGPT、每秒五個 requests 的設定下，重新分配能改善 output latency。P95 的改善約是 1.14 倍，表示針對真正缺空間的 GPU 搬移部分 heads，確實可以減少只靠 preemption 帶來的影響。

這裡有一個原文數字不一致的地方：正文寫 mean 改善 1.06 倍，但圖中的 mean 柱子是 1 和 1.16，對應 1.16 倍。兩者無法同時成立，所以投影片把差異保留下來，不擅自選一個當成確定值。P95 的柱子約是 1.5 和 1.7，兩者相除接近 1.14，和文字大致一致。

右邊看 head-wise cache management 的成本。相對 vLLM，storage operations 的 overhead 增加百分之十三，但 fetching time 減少百分之二十六。作者把前者歸因於更多存放操作，後者則和多核心加速 block indexing 有關。

百分之十三不是 KV cache bytes 增加百分之十三。原文明確說，這個比較中的 KV memory consumption 相同。因此這頁要傳達的是，細粒度配置需要付出管理成本，但 re-dispatching 和索引加速也能帶來效益；不能把每一項 overhead 都解讀成額外的記憶體容量。

來源：Section 7.4、Figure 15。備註：mean 的 1.06×／1.16× 差異存在於提供的 PDF 版本。

## 第 33 頁｜Sensitivity to Threshold and Profiling Error

這頁看兩種敏感度。左邊改變 re-dispatching 門檻 Theta。門檻太低，稍微不平衡就搬 cache，容易花太多時間在 migration；門檻太高，又會讓 straggler 維持太久。預設的 0.5，是作者在這些測試中取得折衷的選擇，不代表所有硬體和 workloads 都應該固定用 0.5。

右邊則故意讓成本模型不準，擾動前面用到的 a、b、c、gamma、beta 等係數，最大到正負百分之二十，再觀察 per-token latency。

在報告的測試裡，latency 最多增加百分之六點九。這表示這個配置方法對這些程度的模型係數誤差，有一定容忍度，不需要每次預測都精準到完全沒有誤差，才能維持效果。

但這個測試的範圍是「profiling 係數偏掉多少」。它沒有直接驗證 GPU 突然離線、網路故障、嚴重壅塞，或 workload 結構完全改變的情況。因此我們可以說，在這組擾動實驗下敏感度不高，但不能把它延伸成一般性的 fault tolerance 保證。

來源：Section 7.4、Figure 16。

## 第 34 頁｜Planning and Profiling Overhead

最後看方法本身的時間成本。Primary placement search 在實體叢集裡需要四秒；更大的例子使用五種 GPU、每種三十二張，共一百六十張，搜尋花十五秒。不過這個大規模結果是 simulation，不能說作者真的在一百六十張 GPU 上完成了整套 serving 實驗。

這個搜尋在初次部署之前做一次，和每個新 request 進來時的 online dispatch 是不同成本。四秒或十五秒，都不是線上 solver 的 per-request latency。

Profiling 使用八種 head 數、八種 cache 量的組合。原文說每個 configuration 執行一次 attention，通常不超過一百毫秒；這是每一組的量測時間，不是全部六十四組加起來只有一百毫秒，也沒有包含所有可能的初始化開銷。

預測準確度方面，計算模型最高 93.8%，傳輸模型是 92.4% 到 96.1%。作者沒有給出完整的 accuracy 定義，所以不宜直接轉換成嚴格的誤差上界。這頁最重要的是分清楚：部署前搜尋、每組 profiling，以及線上配置求解，是三種不同成本；論文沒有完整提供線上 solver 的尾端延遲分布。

來源：Section 7.4。

## 第 35 頁｜Hetis: Scope and Open Questions

整理完方法和結果，這裡看幾個還需要追問的地方。第一個是配置粒度。GQA 必須整組分配，GPU 數變多、或各 GPU 剩餘容量很零碎時，理想的連續比例不一定能轉成合法的整數配置。前面提到的整數求解細節，會直接影響能否重現。

第二個是網路。Hetis 在 decode 的各層會反覆傳 Q、K、V 和 outputs，必要時再搬歷史 KV cache。這和只做一次 phase handoff 的通訊型態不同。在較慢或更容易壅塞的網路上，遠端 attention 到底還划不划算，需要重新量測。

第三個是證據範圍。主要 serving 結果來自十二張 GPU 的本地叢集；一百六十張 GPU 的結果，只是模擬搜尋時間。E2E normalization、cache 單位和線上 solver latency，也有需要補充的細節。

我想延伸的問題是：如果未來記憶體容量增加得比頻寬更快，配置策略還適不適合主要以「放得下多少 cache」來看資源？能放下更多 requests，不代表能在每一步 decode 及時把它們的 K、V 讀完。這就把問題帶到 capacity、bandwidth 和 latency 必須一起建模。

來源：依 Sections 4–7 整理；限制分析與最後的研究問題為講者延伸。

## 第 36 頁｜Hetis: Main Contributions and Findings

Hetis 的核心貢獻可以整理成三個部分。第一，Primary parallelism 專門處理帶權重的 dense work，挑選適合的 GPU，再配置 DP、PP、TP。Primary 會參與 prefill 和 decode，不是只處理其中一個 phase。

第二，decode attention 用 head groups 作為分配單位，讓不同 requests 能有不同的 GPU 配置。決策同時考慮 attention 計算時間、遠端傳輸成本，以及各 GPU 的 KV cache 容量。

第三，request 的 context 會持續成長，所以配置不能只在一開始決定一次。Hetis 透過選擇性的 re-dispatching 和 head-level KV migration，處理計算失衡與局部記憶體耗盡，並盡量保留不需要搬動的 cache。

實驗中，throughput 相對 Splitwise 最高提升 2.25 倍，相對 HexGen 最高 1.33 倍；可用 KV cache 容量最高增加到 1.87 倍。這些都是指定實驗的最大結果。真正值得帶走的設計觀念是：同一層裡的不同模組，可以用不同 GPU 組合；而 attention 的配置，也應該隨 request 狀態在線上調整。

來源：Sections 3–7、9。

## 第 37 頁｜ThunderServe vs. Hetis: Design Choices

現在把兩篇放在一起看。ThunderServe 的主要切分單位是 phase，分別安排 prefill 和 decode 的模型 replicas，再決定 request routing。Hetis 則進一步切到模組與 heads，讓 Primary 負責 dense work，其他 GPU 共享 decode attention。

搜尋方式也不同。ThunderServe 用上層 tabu search 搭配下層選擇，安排 GPU groups、phase roles 和 parallelism；Hetis 先選 Primary 的 parallelism，再於線上配置每個 request 的 heads。Runtime 的調整，前者著重 phase roles 和 routing，後者著重 head placement 與 re-dispatching。

通訊型態是很重要的差異。ThunderServe 的典型 request 流程，在 prefill 完成後把 KV cache 交給 decode replica。Hetis 除了偶爾搬歷史 KV cache，還需要在 decode 的各層反覆交換當步的 Q、新 K/V 和 attention outputs。所以即使兩者都說 network-aware，實際要建模的資料流並不一樣。

最後，不能用 Hetis 的 2.25 倍，直接和 ThunderServe 的 2.1 倍比較誰比較強。兩篇的硬體、baselines、workloads 和 metrics 都不相同，也沒有直接的 head-to-head 實驗。這裡比較的是設計選擇，以及它們分別適合解決哪種資源配置問題。

來源：ThunderServe Sections 3–5；Hetis Sections 4–7。備註：此頁為跨論文整理，不是任一論文提供的直接實驗比較。

## 第 38 頁｜Implications for GPU + HBM / HBF Co-design

最後連回我們關心的 GPU 和記憶體設計。這裡把 HBM，以及可能採用 HBF 的較大容量層，當成後續研究情境。兩篇論文都沒有直接評估 HBF，因此下面是研究假設，不是已經被它們驗證的結果。

第一個問題是 memory-aware placement。ThunderServe 提醒我們區分 prefill、decode，Hetis 又提醒我們區分 dense work 和 attention。如果不同 GPU、不同記憶體層的容量與頻寬不一樣，就應該把這些差異放進 phase 或 head 的配置模型，而不是只看 GPU 算力。

第二個問題是 tiered KV cache。比較大、比較慢的層，可能讓更多 requests 的 KV cache 放得下，但 decode attention 需要反覆讀取歷史 K、V。不能只因為資料比較舊，就假設它每一步都不會被讀到。若要讓部分 cache 留在慢層，就需要計算存取、搬移與可能的預取成本，並檢查 TPOT 是否還能接受。

第三個問題是 simulation。如果要放進 LLMServingSim，至少要區分權重讀取、attention 的 KV 讀取、當步輸入輸出傳輸，以及歷史 cache migration；也要納入頻寬競爭和可重疊的部分。之後再用實測校正，才能回答「增加容量值不值得」和「什麼情況應該把 heads 搬走」這類問題。

備註：本頁是講者提出的研究方向。未假定特定 HBF 產品規格，也未宣稱兩篇系統已實作 HBM／HBF 分層。

## 第 39 頁｜Q&A

以上是 Hetis。第 37–38 頁把 ThunderServe 放進來，是為了對照 phase 和 head 兩種切法，不是兩篇的聯合實驗。投影片上留的討論方向是 GPU heterogeneity、KV cache，以及 HBM／HBF。

可以接著問：對我們預計研究的硬體而言，瓶頸比較接近 phase placement，還是 attention 與 KV cache 的細粒度配置；以及容量、頻寬和每一步讀取成本，哪些要先用實測建成模型。
