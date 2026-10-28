# Hetis 中文講稿

這是獨立簡報，對應 `2026-10-21-Hetis.tex`。投影片頁腳是 1/39 到 39/39，講稿標題用同一套頁碼，不和 ThunderServe 相加。第 01–02 頁是開場，第 03–36 頁是 Hetis 正文，第 37–38 頁是和 ThunderServe 的對照與後續問題，第 39 頁是 Q&A。

依據為本地 `SC25_Hetis.pdf`，標題為 _Hetis: Serving LLMs in Heterogeneous GPU Clusters with Fine-grained and Dynamic Parallelism_，首頁標示 arXiv:2509.08309v1，2025-09-10，SC ’25。以下「論文第幾頁」若出現，指 PDF 實際頁碼，不是投影片頁碼。每頁正文可直接口述；「來源」與「備註」供準備時查閱，不必念出。公式頁有為了說明而做的符號及單位整理，已與原文逐字公式區分。

## 第 01 頁｜Title

今天介紹 Hetis。論文作者是 Zizhao Mo、Jianxiong Liao、Huanle Xu、Zhi Zhou 和 Chengzhong Xu，發表在 SC 2025。它處理的是 heterogeneous GPU cluster 上的 LLM serving：同一層裡的 dense computation 和 decode attention，不一定適合放在同一組 GPU 上。

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

這一頁補 Table 1。測試是 OPT-2.7B，時間是走完所有 layer 的一次 iteration。Prefill 用 3 個 requests，decode 用 25 個，這是作者預先設定的 batch size，不是實驗結果。兩者是獨立的 GPU profiling 測試，不是把這 3 個 requests 做完 prefill 再傳給 decode：prefill 一次處理 3 個 requests 的 prompts，decode 則讓 25 個已有歷史 KV cache 的 requests 各跑一次 token generation iteration，也就是各生成一個 token。至於 decode 測試的 KV cache 怎麼初始化，論文沒有明確交代，這裡就不假設實作細節。

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

這裡先把兩種 worker 的分工講清楚，後面比較不容易混淆。Primary worker 存放模型權重，在 prefill 和 decode 都負責 QKV projection、output projection 和 MLP。Prefill 的 attention core 和 KV cache 建立也都由 Primary 執行，Attention worker 不參與。到了 decode，Primary 處理分配給自己的 heads，並儲存對應的 KV cache；Attention worker 則處理卸載給它的 heads，並儲存那部分的 KV cache。

這裡的 head 就是 multi-head attention 裡的注意力頭，是切分 attention 工作的單位，同一個 request 的不同 heads 可以交給不同 workers。Offload 就是把部分 heads 的 decode attention 計算和對應 KV cache 儲存交給 Attention worker，不是把整個 request 或整個 decode 階段都交出去。

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

這裡的 DP 是資料平行，讓不同模型服務副本分擔不同 requests；PP 是管線平行，把模型的不同 layers 分給不同 GPU，依序傳遞中間結果；TP 是張量平行，把同一層的運算拆給多張 GPU 合作。簡單記就是：DP 分 requests，PP 分層，TP 分同一層內的運算，三者也可以組合使用。

搜尋順序是 DP grouping、coarse PP search、GPU pruning，最後才是 fine-grained TP/PP search。第一步先考慮 serving instance 的切法，也就是 DP。它把各種型號的 GPU 平均分到不同 instances，並排除剩餘 cache 容量不夠的候選配置。接著，在每個 instance 裡，先把同一類 GPU 視為一個統一的 pipeline stage，先做初步的 layer assignment，讓最慢 stage 的計算成本盡量低。

然後，它會從較低階的 GPU 開始嘗試移除。少了這張卡，原本的 layers 還是要由剩餘 GPU 承擔，所以要重新評估 layer assignment，再比較移除前後的瓶頸計算成本 C_p；不能只把被移除 GPU 的成本從表裡刪掉。如果重新評估後的成本增加不超過百分之五，就通過 pruning 判斷。這張卡還是會參與服務，只是改成 Attention worker，釋放原本放模型權重的空間。

最後才更細地探索每個統一 stage 內的 TP、PP 組合，並把計算和通訊成本一起算進去。這個流程的重點，是先縮小搜尋空間，再做比較完整的成本評估；它是一個 heuristic，不是把所有配置都找完的全域最佳解。

來源：Section 4.1、Figure 4。

## 第 09 頁｜Primary Selection Objective and Pruning Rule

這頁用公式把剛才的搜尋補完整。上面的 sigma 代表模型參數怎麼放，以及 DP、PP、TP 怎麼設。目標是讓預估的總成本最小，包含 computation 和 communication；模型與 workload distribution 都會影響這個成本。

中間補的 C_p 等於各個 stage 計算成本的最大值，就是看哪個 pipeline stage 最慢。這是把論文文字定義寫成教學公式，不是論文另外編號的一條公式。這裡採 ideal scaling 的估算，也還沒算 communication。

下面保留論文的 GPU pruning 規則。分子是移除候選 GPU 後，按剩餘 GPU 重新評估 layer assignment 得到的 C_p；分母是移除前的 C_p。比值不超過 1.05，就通過這次移除判斷。Layer assignment 會改變每個 stage 承擔的工作，因此也會影響哪個 stage 最慢，以及能不能通過百分之五門檻。這是理解候選配置成本時必要的重新評估；原文沒有逐步交代每次移除後如何重算 layer mapping 的實作細節。

投影片的 Illustrative Example 全是假設數據，單位也是任意的，不是論文實驗結果。假設移除前，三個 stages 的成本是 100、90、20，最後一個是 P100，C_p 就是 100。移除 P100、把 layers 重新分配後，假設剩下兩個 stages 的成本變成 103 和 98，新的 C_p 就是 103；103 除以 100 等於 1.03，小於 1.05，所以可以移除。重點是重新分配後的最大成本，不是單看 P100 原本的 20。

這裡的 C_p 和上面的完整 C 要分清楚：pruning 只先看理想 scaling 下的計算成本，最後 fine-grained TP/PP search 才用包含 computation 和 communication 的完整成本評估候選配置。因此，百分之五不能解讀成實際端到端 latency 一定只增加百分之五。

來源：Section 4.1、Figure 4、Eq. (1) 與未編號的 GPU pruning 規則。C_p 的 max 寫法為教學補充；數值範例為假設，非論文實測。

## 第 10 頁｜Why Split Attention by Head?

接著看 attention 要沿哪個維度切。第一種是 batch-wise，把整個 request 丟給某張 GPU。實作比較直接，但粒度很粗，尤其 requests 的 context length 不同時，分到相同數量的 requests，不代表拿到相同工作量。

第二種是 sequence-wise，把同一個 request 的歷史 tokens 分到不同 GPU。這樣可以切得比較細，但不同 GPU 都需要收到 query，而且最後必須正確合併跨 sequence shards 的 softmax 統計與輸出，不能把各段的局部結果直接接起來。

Hetis 選的是 head-wise。各個 head 原本就分別計算 attention，只要把對應的 Q、K、V 放在一起，就能獨立算完，再依模型的 head 順序組合輸出。重點是，單一 head 的完整歷史 KV cache 留在同一張 GPU，不沿 token 維度拆散，所以這個 head 的 softmax 可以在本地完成，不需要跨 GPU 合併。簡單記就是：batch-wise 分整個 request，sequence-wise 分歷史 tokens，head-wise 分注意力頭。

下方實驗比較的是 communication overhead。在 Llama-70B、100 Gbps 的設定下，論文報告相對 sequence splitting，在百分之二十 offload 時有 2.68 倍通訊加速，四個 workers 時最高 3.55 倍。這些數字是通訊部分的改善，不能直接說整個 request 也快了 3.55 倍。

來源：Section 4.2、Figure 5。

## 第 11 頁｜Head-wise Attention as Printed

論文把 head-wise attention 寫成 Eq. (2)。一個 request 的輸出，是各 GPU 上那段 heads 的 result 依序 concat 起來。

每一段仍是 scaled dot-product：這組 heads 的 query 乘上對應 K 的轉置，除以根號 d，做 softmax，再乘 V。h 下標 i、上標 j、時間 t，是 request j 在 GPU i、時間 t 分到的 query heads。它被拿來當 Q、K、V 的下標，表示那一組 heads。

前面那頁的 attention core 是同一個 softmax，只是還沒寫成按 GPU 切開再接回去。因為每個 head 在一張 GPU 上就算完，所以不需要為了同一個 head 跨 GPU 合併 softmax。2.68 倍和 3.55 倍仍是通訊開銷的比較，不是這個式子本身的加速比。

實際執行時，Primary 先完成 QKV projection，把分配給 Attention worker 的 Q 和當前 token 的 K、V 傳過去。每張 GPU 把新的 K、V 加入本地 KV cache，再用完整歷史資料，獨立算完自己負責的 heads。遠端 results 回到 Primary 後，和 Primary 本地的結果按 head 順序 concat，再執行 output projection 和 MLP。所以這裡仍有 Q、K、V 和 results 的 GPU 間通訊，省下的是跨 GPU 的 softmax 合併，以及把不需要的 heads 資料重複傳送的開銷。

來源：Section 4.2、Eq. (2)。

## 第 12 頁｜Dynamic Attention Placement Across Requests

這張示意圖用三個 requests 說明動態配置。每個 request 都有六個 heads，但 context length 分別是六、九、三，所以每個 head 需要的 KV cache 大小不同。

Context 越長，每一步 attention 要讀取和計算的歷史 K、V 通常也越多，因此 head 數相同，不代表 cache 容量或 attention 工作量相同。

因此，Hetis 不要求所有 requests 都按照同一個固定比例切到 GPU 上。某個 request 可以多放一點在 Primary，另一個則多放一點到 Attention worker。配置時要看整張 GPU 已經承擔多少 heads、多少 cache，以及通訊成本。

這裡的 KV cache 會跟著對應的 head 走。某個 head 放在某張 GPU，這張 GPU 就需要它的完整歷史 K、V，才能算這一步 attention。算完之後，再把分散的 head outputs 收回來，接著執行後面的 output projection。

等 request 繼續產生 tokens，cache 會變大，配置也可能需要調整。必要時，Hetis 可以重新決定某個 request 在各 GPU 上的 head 分配比例，並搬移這些 heads 對應的 KV cache。Re-dispatching 只改需要搬的部分，原本位置還能沿用的 cache 就留下來。所謂 dynamic parallelism，改變的是運算與資料的放置位置，不是模型有幾個 heads，也不是把 attention 換成另一種近似演算法。

來源：Sections 4.2、5.3、Figure 6。

## 第 13 頁｜Head Integrity and Grouped-Query Attention

切 heads 還有一個限制：不能切到破壞模型本來的 Q、K、V 對應關係。這裡 H_Q 是 query heads 的數量，H_KV 是 KV heads 的數量，兩者的比值叫 r。

一般的 MHA，每個 query head 有自己的 K、V，所以 r 等於一。GQA 則是多個 query heads 共用同一組 KV head。Hetis 會把這一整組一起分配，所以每張 GPU 拿到的 query-head 數量，除以 r 之後必須是非負整數。

換句話說，MHA 可以按單一 query head 分配；GQA 則要把共用同一組 K、V 的 query heads 和對應 cache 一起放到同一張 GPU，保持完整的 GQA group。

用投影片上的例子來看，如果有八個 query heads、兩個 KV heads，那 r 就是四。一張 GPU 可以拿零個、四個或八個 query heads，實際上就是分配零組、一組或兩組；不能任意拿三個或五個。這是教學用的例子，不是這次實驗模型的設定。

例如把一組交給 Primary、另一組交給 Attention worker，兩邊各負責四個 query heads 和一組 KV；不能任意挑四個來自不同 groups 的 query heads 湊成一組。

另外，每個被分配出去的 head 都保有自己的完整 context，所以不需要像 sequence splitting 那樣跨 GPU 合併同一個 head 的 softmax。GQA 的好處是減少 KV cache，但對 Hetis 來說，它也讓最小配置單位變粗。後面看最佳化公式時，就要把這個整數限制一起記住。

來源：Sections 4.2、5.2.1、6。

## 第 14 頁｜Profiling Decode Attention Time

要決定 heads 放在哪裡，首先要知道每種配置大概會跑多久。Figure 7 用 OPT-30B 的 micro-benchmarks，觀察 decode attention 時間和幾個因素的關係；三個子圖的縱軸都是 Attention Computation Time，單位是毫秒，不是整個 request 的端到端延遲。

左圖 (a) 的橫軸是 request 數量，圖上從 400 到 700。這組測試固定跨 requests 加總的 query-head 數和 KV cache 大小，只改變 request 數量，結果時間變化不大。所以不能只用「這張 GPU 有幾個 requests」來估計它忙不忙；這也不代表實際服務中增加 requests 永遠沒有成本，因為總 heads 和 cache 通常也會跟著增加。

中圖 (b) 的橫軸是平均 context length，單位 k 代表千個 tokens，圖上是 0.9k 到 1.2k；觀察到 context 越長，attention 時間大致線性增加。每一步 decode 的 query 都要讀取歷史 K、V，context 變長就會增加相關的 KV cache 量、向量運算，以及從 GPU HBM 到 SRAM 的資料存取。論文用這張圖說明時間與 cache 量的關係，但沒有完整列出這個子圖的其他控制變數，因此這裡不自行補上固定 request 數或固定 head 數等設定。

右圖 (c) 的橫軸是總 query-head 數量，單位 k 代表千個 heads，圖上是 15k、30k、45k，不是模型單一 request 的 head 數。這組測試固定 KV cache 總量，增加 query heads，時間仍大致線性上升；論文將這個現象歸因於更多 heads 的 attention 計算競爭硬體資源。

合起來看，Attention Time 主要與總 query-head 數和相關 KV cache 量有關，不能單靠 request count 估計。這就導出下一頁的線性模型：分別用 head 數和 cache 量描述成本，再加固定項。這是量測得到的近似，不是所有 batch、kernel、GPU 都必然遵守同一條直線；每種裝置仍然需要 profiling，才能得到自己的係數。

來源：Section 5.1、Figure 7。

## 第 15 頁｜Computation and Communication Cost Models

左邊的公式是 \(\tau_i(t)=a_i h_i(t)+b_i g_i(t)+c_i\)，結果 tau 是 GPU i 在時間 t 的預估 decode attention 計算時間。h 是這張 GPU 上跨 requests 加總的 query-head 數，不是模型本身固定的 head 數；g 是這些 heads 對應的 KV cache 總量。a、b 分別描述 head 數和 cache 量增加時的時間成本，c 是固定項，三者都由 profiling 擬合，各 GPU 可以不同。

中間的公式是 \(\rho_i(t)=\gamma_i d_i(t)+\beta_i\)，結果 rho 是 Primary 與 Attention worker i 之間的預估通訊時間。d 是這一步需要傳送的 Q、新產生的 K、V，以及回傳 attention output 的資料量；gamma 是每單位傳輸量的時間成本，beta 是固定通訊成本，兩者都由離線 profiling 決定。因此 gamma 不是直接拿網路標示的 Gbps 數值來代入。

右邊的 \(d*i(t)=(2+2/r)h_i(t)\) 是用向量數表示這份傳輸量，其中 \(r=H_Q/H*{KV}\)，代表每個 KV head 對應幾個 query heads。MHA 的 r 等於一；GQA 則讓多個 query heads 共用一組 K、V。第一個 2 是傳出去的 Q 和傳回來的 attention output，各有 h 個向量；第二個 2 是新 K 和新 V，但因為共用 KV，各只有 h 除以 r 個向量，所以這項要除以 r。

用一個教學示例來算：如果 h 等於 8、r 等於 4，就是 8 個 Q、8 個 output、2 個新 K 和 2 個新 V，合計 \(d=8+8+2+2=20\) 個向量，不是 20 Bytes。要換成實際 bytes，還要乘上 head dimension 和每個元素的位元組數；gamma 的單位也必須和 d 的單位一致。這裡計算的是每一步的新向量與結果，沒有把已經留在 worker 上的完整歷史 KV cache 每次重傳。

所以遠端 Attention worker 必須一起考慮 tau 的計算成本和 rho 的通訊成本，不能只看 attention kernel 快不快。Primary 留在本地計算的 attention，不需要額外付出這組 Primary 到 Attention worker 的往返成本；但這不代表 Primary 的 TP／PP 完全沒有 GPU 間通訊。

來源：Section 5.1、Eqs. (3)–(4)。備註：向量計數為使原式單位明確而採用的講解方式；h=8、r=4 為教學示例，非論文實驗數據。

## 第 16 頁｜Online Dispatch for Newly Arriving Requests

這四頁改以論文原式為主。Section 5.2.2 的做法是保留既有 requests 的配置，只替新到的 J(t) 分配 heads；不在每次 arrival 時把所有 requests 重排。

這頁直接呈現 Eq. (8)，也就是求解完成後的負載更新。x_i^j(t) 是 request j 分到第 k 個 pipeline stage 裡 GPU i 的 query-head 數；N_k 是這個 stage 的 Primary 和 Attention workers 總數。h_i 是這張 GPU 原本承擔的總 query heads，更新時加上新 requests 分到這裡的 x。

g_i 是原本的 cache 量；l_j 是 request j 當下的 context length。新增 cache 的式子是 x 乘 l 再加總，乘上 2/r；r 是 query heads 與 KV heads 的比值，2 是 K、V 各一份，除以 r 則反映 GQA 共用 KV。這裡保留原文記號，不把 g 或容量 M 擅自定義成 bytes 或某一種向量單位。

注意，原文把 J(t) 定義成集合，卻又拿 J(t) 當求和上限；投影片照原樣保留，口頭上理解為加總新到的 requests。Eq. (8) 的 t+1 是原文寫法，這個式子只呈現新分配帶來的增量，沒有完整列出既有 requests 的 cache 成長或完成離開時如何更新，不能把它當成全部 runtime 狀態轉移。

來源：Section 5.2.1–5.2.2、Eq. (8)。本頁已移除先前的 hat 變數及自行統一 KV-vector 容量的整理式，避免將其誤稱為原文等價式。

## 第 17 頁｜Printed Dispatch Constraints

這一頁保留論文印出的 Eqs. (5)–(7)，包含時間下標、求和範圍與適用對象。

Eq. (5) 對所有正在服務的 requests，也就是 S(t)，要求同一個 request 在 stage 內各 GPU 分到的 heads 加總為 0 或 H。H 是模型的 query-head 總數；0 是沒有分配，H 是完整分配。這個限制本身沒有交代 admission 或 rejection 的具體流程。

Eq. (6) 對 stage 裡的每張 GPU，把 S(t) 中的 query-head 數乘 context length 後加總，限制在 r 乘 M*i(t) 除以 2 以下。這裡 \(r=H_Q/H*{KV}\) 是 GQA 的共享比例；用教學示例來說，r 等於 4，代表每四個 query heads 共用一組 Key、Value，所以這四個 heads 只需要儲存一個 KV head 的歷史資料。把原式兩邊乘上 \(2/r\) 來理解，左邊除以 r 是考慮 KV 共用，乘以 2 是因為 Key 和 Value 都要儲存，目的就是讓每張 GPU 上所有 requests 的 KV cache 總量不超過可用容量 M_i(t)。論文稱 M_i(t) 為 available cache capacity，但沒有在這裡完整交代實體單位，以及 available 與既有 cache 占用之間的換算。

Eq. (7a) 讓各 GPU 中最大的 f_i 最小，x 向量收集這張 GPU 對新 requests 的 head 分配。Eq. (7b) 原樣把既有 g_i 加上新 requests 的 x 乘 l，右端是 r M_i 除以 2；Eq. (7c) 則對每個新 request 強制總和為 H，和 Eq. (5) 允許 0 的寫法不同。J(t) 作為集合與求和上限的混用也保留，沒有悄悄改成集合大小。

要留意，(7b) 的新增項沒有 2/r，但 Eq. (8) 更新 g 時有這個係數，因此不能直接宣稱兩種容量寫法等價。這頁先忠實保留原式，下一頁看成本公式，最後再集中說明單位與整數限制的歧義。

來源：Section 5.2、Eqs. (5)–(7)。H 就是前面寫成 H_Q 的 query-head 總數；原文的 group-integrality 限制寫在正文，未列入 Eq. (7) 的限制式。

## 第 18 頁｜Closed Forms of Attention Time

這兩個 \(f_i(\vec{x}\_i(t))\) 是預測 GPU i 在加入新 requests 的 head allocation 後，執行一次 decode attention 所需的時間；遠端 worker 的預估還包含傳輸成本。Min-Max optimization 就是比較各 GPU 的這個時間，讓最慢的一張盡量快。這兩式是 Section 5.2.2 在 Eq. (7) 後直接給出的公式，沒有獨立編號，不是我們自行推導的新公式。

先看變數：\(h*i(t)\) 是 GPU 原本負責的 query heads 總數，\(g_i(t)\) 是原本儲存的 KV cache 量。\(x_i^j(t)\) 是新 request j 分配給 GPU i 的 query-head 數，\(\vec{x}\_i(t)\) 則收集這張 GPU 對所有新 requests 的分配。\(J(t)\) 是當前新到達的 requests，\(\ell_j(t)\) 是 request j 的 context length，也就是投影片原式的 l_j(t)。\(r=H_Q/H*{KV}\) 是 GQA ratio，例如 r 等於 4，就代表四個 query heads 共用一組 K、V。

係數方面，\(a_i,b_i,c_i\) 是 GPU profiling 得到的 attention computation cost 係數：a 對應 head 數的成本，b 對應 cache 量的成本，c 是固定項。\(\gamma_i\) 是每單位傳輸量的時間成本，\(\beta_i\) 是通訊模型的固定延遲；這些係數要和模型使用的資料量單位一致。

兩式共同的第一個括號 \(h_i+\sum_j x_i^j\)，就是既有 heads 加上新分配的 heads。第二個括號 \(g_i+\frac{2}{r}\sum_j\ell_jx_i^j\)，則是既有 KV cache 加上新 requests 需要的 cache；context length 乘 head 數描述新增負載，2 代表 K、V 都要保存，除以 r 則反映 GQA 共用 KV。這個 cache 增量和 Eq. (8) 相同，這裡只是解釋原式，沒有另替 g 指定實體單位。

Primary 的 f_i 只計算本地 decode attention 成本，也就是 a 乘更新後的 heads、b 乘更新後的 cache，再加 c。Attention worker 除了同樣的計算，還需要接收 Q、新 K/V，並把 attention output 傳回 Primary，所以 head 數的係數多了 \((2+2/r)\gamma_i\)，最後再加 beta。第一個 2 是 Q 傳送與 output 回傳；第二個 2 是 K、V 的傳送，因為 GQA 共用 KV，所以這一項要除以 r。

通訊成本乘的是既有與新分配的全部遠端 heads，不只新到的 requests。既有遠端 heads 每個 decode step 也要接收新的向量並回傳結果，但不代表每一步都重傳完整歷史 KV cache；Primary 的式子沒有這組遠端往返成本，也不代表其他 TP／PP 操作完全沒有通訊。

最後用一個教學示例：假設 GPU 原有四個 heads，新 request 再分配四個，r 等於 4，更新後就是八個 heads。如果這個新 request 的 context length 是 L，代入原式的 cache 增量就是 \((2/4)\times L\times4=2L\)，所以 cache 項變成原本的 g 加 2L。用向量計數來理解，就是一個 KV head 的 L 個 K 向量加 L 個 V 向量，不是 2L bytes；這只是教學用的單位解讀，並未消除原文的容量單位歧義。以上配置是假設數據，不是論文實驗結果。

來源：Section 5.2.2、Eq. (7) 後未編號的兩個 f_i 公式。投影片保留原文時間下標及 J(t) 求和上限；原文將 J(t) 定義為集合又用作求和上限，這裡口頭理解為加總新 requests，未自行修改原式或 cache 單位。

## 第 19 頁｜Dispatch Formulation: What the Paper Specifies

這頁把原文與講者分析分開。唯一保留的 Derived 公式是把 minimax 目標改寫成輔助變數 z：要求每張 GPU 的 f_i 都不超過 z，再把 z 最小化。這只是目標的等價改寫，原本的配置與容量限制仍要另外保留；它不會自動修正 Eq. (7b) 的單位問題。

Section 5.2.1 的正文要求 x_i^j(t) 除以 r 屬於自然數集合 N，也就是按完整 head groups 分配。原文沒有明確定義 N 是否包含 0，但 Eq. (5) 又允許總分配為 0，因此投影片保留 N 並註明這個記號歧義，不直接換成我們自行選定的整數集合。

Section 5.2.2 稱問題可以改寫成 LP。如果放寬 x 為連續變數，affine 成本配合 z 確實可以形成 LP relaxation；保留整組分配的整數要求，則是離散問題，不能直接等同一般連續 LP。原文這一節沒有交代如何處理 integrality，因此我們不假設作者用了 rounding、特定整數求解方法，或一般 LP 解會自然符合 GQA 分組。

容量也有需要釐清的地方：Eq. (7b) 把既有 g 與 query-head-token 計數相加，但 Eq. (8) 及兩個 f_i 的新增 cache 項都有 2/r。原文沒有給出足以消除這個差異的完整單位與正規化定義；把 g、M 統一成 KV-vector 是額外的建模選擇，不能宣稱它就是原文等價式。這次因此移除先前的 reconciled capacity／LP，保留原式和歧義說明。

來源：Section 5.2。z 的 epigraph 改寫與公式一致性分析屬於講者補充；不據此推測作者實作，也不自行補出論文沒有的演算法。

## 第 20 頁｜Re-dispatching to Balance Computation

只在 request 進來時分配一次，還是不夠。因為 decode 會持續增加 context，有些 request 很快結束，有些會生成很久，原本平衡的 GPU 可能逐漸出現 straggler。

投影片上的 f-star 是：在現有 requests S(t) 上，最小化最慢 GPU 的 f_i。唯一印出來的限制，是所有 GPU、所有 request 的 x 乘 l 加總，不超過所有 GPU 的 r M 除以 2 再加總。Head integrity 沒有在這個式子裡重寫。如果目前 attention 時間和 f-star 的偏差超過 Theta，就觸發 re-dispatching；預設門檻是百分之五十。原文沒有把這個偏差的正規化分母寫得很完整，所以這裡不自行補成某個精確百分比公式。

觸發後，先找 attention 最慢的 GPU，再找其中對時間貢獻最大的 request，針對這個 request 重新求配置。它不是直接把叢集所有 requests 全部搬一次，而是先處理最明顯的瓶頸。

重新分配之後，如果某些 heads 還在原本的位置，對應 cache 就直接沿用；只有改變位置的 shards 才需要搬移。這樣能降低調整成本，不過仍然會占用網路和裝置資源。因此門檻不能只追求越低越好，後面會看到它和搬移頻率之間的取捨。

來源：Section 5.3.1。

## 第 21 頁｜Re-dispatching to Relieve KV Cache Exhaustion

另一種觸發原因是記憶體：某張 GPU 的 KV cache 空間快用完了，但其他 GPU 還有剩。這時如果用全系統的 LIFO 或 LRU 挑 victim，可能剛好挑到一個根本沒有在這張 GPU 放 cache 的 request，那就無法解除真正的瓶頸。

LIFO 是 Last In, First Out，也就是「後進先出」，優先挑較晚進來的 request；LRU 是 Least Recently Used，也就是「最近最少使用」，優先挑距離上次使用最久的項目。簡單說，LIFO 看進來的先後，LRU 看最後一次使用的時間；這裡的 victim 就是被選來暫停服務或騰出 cache 空間的 request。論文這一節具體說明的是調整 LIFO 的做法，並不是說 Hetis 同時採用兩種策略。

Hetis 先把候選範圍縮到，確實有占用這張 GPU cache 的 requests，再在這個範圍內使用 LIFO 的想法，挑較晚進來的 request。論文用一個不等式判斷叢集還有沒有空間：所有 GPU 的 g_i 加總，要小於所有 GPU 的 r M_i 除以 2 再加總。成立的話，就嘗試把 victim 的部分 head groups 重新分配出去，而不是整份丟掉。

這和直接丟掉整個 request 的 cache，或把整份 cache swap 出去不一樣。它想保留還能沿用的部分，只搬為了騰出空間而必須搬的 shards。過程中也要顧到計算負載，不能解決記憶體問題後，又把某張卡變成非常慢的 straggler。

還有一個實作上要記得的限制：全叢集加起來有空間，不代表一定找得到合法配置。GQA 必須整組搬，單張 GPU 也需要裝得下對應的 cache。因此容量、配置粒度，以及計算平衡都要一起檢查。

來源：Section 5.3.2。備註：最後一段為離散配置限制的延伸說明。

## 第 22 頁｜Head-Level KV Management and Migration

前面介紹的是 Dispatcher 如何決定 Heads 的配置，這頁則說明 Hetis 如何在 Runtime 中真正執行這些配置。

Hetis 是基於 vLLM 修改而成。原本 vLLM 透過固定大小的 Blocks 管理 KV Cache，Hetis 進一步沿 Head 維度拆分，讓系統可以只搬移指定 Heads 的歷史 KV Cache，而不是整個 Request 的 Cache。如果使用 GQA，仍然需要維持完整的 Query/KV Group 關係。

為了找到正確的 Cache，Hetis 使用自訂 CUDA Kernels，根據 Sequence ID、Token Position 和 Head ID 進行資料存取。另外，由於 Head-level 管理增加了索引工作，作者使用 CPU 多核心平行化加速 Block Indexing。真正執行 Attention 時，則沿用 vLLM 的 PagedAttention Kernel。

接著是 GPU 間通訊。論文使用 NCCL，也就是 NVIDIA Collective Communications Library。它是一套 GPU 間通訊函式庫，支援 Point-to-Point 傳輸。例如 Primary Worker 可以把部分 Heads 的 Query 和新產生的 K、V 傳給 Attention Worker，等遠端 GPU 算完後，再透過 NCCL 收回 Attention Results。

如果發生 Re-dispatching，Hetis 的 Hauler 就負責搬移位置改變的 Head-level KV Cache。原本沒有改變位置的 KV Cache 可以直接保留，因此不必重新搬移整個 Request 的歷史資料。

最後，作者使用 Low-priority CUDA Streams 執行 KV Cache Migration，盡量避免資料搬移與正常 Inference 的通訊競爭。但低優先權不代表完全沒有成本，Migration 仍會消耗 GPU 與網路資源。

這頁的重點是，Hetis 不只設計了 Head Allocation 演算法，也修改了底層的 KV Cache Layout、索引與通訊機制，讓動態 Head-wise Parallelism 真正能夠執行。

來源：Hetis Section 6 — System Implementation。

## 第 23 頁｜Hetis Experimental Setup

接下來看實驗。主要叢集有十二張 GPU，分布在四台 hosts：一台有四張 A100-80GB，兩台各有兩張 RTX 3090，另一台有四張 P100。3090 的記憶體是 24 GB，P100 是 12 GB；不同型號的計算能力和容量差異都很明顯。

Host 之間使用 100 Gbps 的 LAN，host 內使用 PCIe。這個網路設定很重要，因為 Hetis 在 decode 過程中會反覆傳遞 attention 的輸入和輸出，不能把它當成只在 request 開始時傳一次資料。

模型方面，Llama-13B 和 OPT-30B 使用 MHA，Llama-70B 使用 GQA，所以可以觀察不同 KV sharing 結構下的效果。MHA 是 Multi-Head Attention，每個 Query Head 都有自己對應的 Key、Value；GQA 是 Grouped-Query Attention，讓多個 Query Heads 共用一組 Key、Value，因此可以減少 KV Cache 的儲存量。Workloads 有三類：ShareGPT，簡稱 SG，是聊天；HumanEval，簡稱 HE，是程式碼補全；LongBench，簡稱 LB，這裡用在長文章摘要。

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

因此這個指標比單純把所有 GPU 的剩餘 bytes 加起來更有系統意義：配置、worker 角色和負載分布，都會影響記憶體能不能真正派上用場。簡單說，這裡增加的是能實際拿來放 KV cache 的有效容量，不是當下的 VRAM 占用率，也不是每秒讀寫的頻寬利用率。

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

左邊比較 re-dispatching 和 LIFO，在 ShareGPT、每秒五個 requests 的設定下，重新分配能改善 output latency。P95 是第九十五百分位，表示約百分之九十五的 requests 延遲不超過這個值，用來觀察較慢那群 requests 的表現。P95 的改善約是 1.14 倍，表示針對真正缺空間的 GPU 搬移部分 heads，確實可以減少只靠 preemption 帶來的影響。

這裡有一個原文數字不一致的地方：正文寫 mean 改善 1.06 倍，但圖中的 mean 柱子是 1 和 1.16，對應 1.16 倍。兩者無法同時成立，所以投影片把差異保留下來，不擅自選一個當成確定值。P95 的柱子約是 1.5 和 1.7，兩者相除接近 1.14，和文字大致一致。

右邊看 head-wise cache management 的成本。Store 是把新算出的 K、V 寫入 cache；Fetch 是找到並取用歷史 K、V，供當前 query 計算 attention，兩者都不同於跨 GPU 搬移 cache 的 migration。相對 vLLM，storage operations 的 overhead 增加百分之十三，但 fetching time 減少百分之二十六。作者把前者歸因於更多存放操作，後者則和多核心加速 block indexing 有關。

百分之十三不是 KV cache bytes 增加百分之十三。原文明確說，這個比較中的 KV memory consumption 相同。因此這頁要傳達的是，細粒度配置需要付出管理成本，但 re-dispatching 和索引加速也能帶來效益；不能把每一項 overhead 都解讀成額外的記憶體容量。

來源：Section 7.4、Figure 15。備註：mean 的 1.06×／1.16× 差異存在於提供的 PDF 版本。

## 第 33 頁｜Sensitivity to Threshold and Profiling Error

這頁看兩種敏感度。左邊改變 re-dispatching 門檻 Theta。門檻太低，稍微不平衡就搬 cache，容易花太多時間在 migration；門檻太高，又會讓 straggler 維持太久。預設的 0.5，是作者在這些測試中取得折衷的選擇，不代表所有硬體和 workloads 都應該固定用 0.5。

右邊的 profiling error，指的是量測後擬合出的成本模型係數不準，不是 GPU 算錯或模型回答錯誤。作者刻意擾動前面用到的 a、b、c、gamma、beta 等係數，最大到正負百分之二十，再觀察 per-token latency；改變的是 Dispatcher 對計算與通訊成本的估計，不是直接把硬體變慢。例如原本係數是 10，改成 12 就是增加百分之二十，這只是教學示例；單一係數偏差百分之二十，也不代表整體預測時間或實際延遲一定增加百分之二十。

在報告的測試裡，latency 最多增加百分之六點九。這表示這個配置方法對這些程度的模型係數誤差，有一定容忍度，不需要每次預測都精準到完全沒有誤差，才能維持效果。

但這個測試的範圍是「profiling 係數偏掉多少」。它沒有直接驗證 GPU 突然離線、網路故障、嚴重壅塞，或 workload 結構完全改變的情況。因此我們可以說，在這組擾動實驗下敏感度不高，但不能把它延伸成一般性的 fault tolerance 保證。

來源：Section 7.4、Figure 16。

## 第 34 頁｜Planning and Profiling Overhead

最後看方法本身的時間成本。Primary placement search 在實體叢集裡需要四秒；更大的例子使用五種 GPU、每種三十二張，共一百六十張，搜尋花十五秒。不過這個大規模結果是 simulation，不能說作者真的在一百六十張 GPU 上完成了整套 serving 實驗。

這個搜尋在初次部署之前做一次，和每個新 request 進來時的 online dispatch 是不同成本。四秒或十五秒，都不是線上 solver 的 per-request latency。

Profiling 使用八種 head 數、八種 cache 量的組合。原文說每個 configuration 執行一次 attention，通常不超過一百毫秒；這是每一組的量測時間，不是全部六十四組加起來只有一百毫秒，也沒有包含所有可能的初始化開銷。

預測準確度方面，計算模型最高 93.8%，傳輸模型是 92.4% 到 96.1%。這裡的計算模型，是根據 head 數和 KV cache 量估計 GPU 算 attention 要多久；傳輸模型則根據資料量估計 Q、新 K/V 和 attention output 在 GPU 間傳送要多久，兩者都是時間預測，不是語言模型回答的正確率。作者沒有給出完整的 accuracy 定義，所以不宜直接轉換成嚴格的誤差上界。這頁最重要的是分清楚：部署前搜尋、每組 profiling，以及線上配置求解，是三種不同成本；論文沒有完整提供線上 solver 的尾端延遲分布。

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

tp pp dp
