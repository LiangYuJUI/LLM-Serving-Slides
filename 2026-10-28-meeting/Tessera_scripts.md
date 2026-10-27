# Tessera 中文講稿

這是獨立簡報，對應 `2026-10-28-Tessera.tex`。投影片頁腳與下方講稿頁碼完全一致。

依據為本地 `Arxiv26_Tessera.pdf`，標題為 *Tessera: Unlocking Heterogeneous GPUs through Kernel-Granularity Disaggregation*，Hu 等人，arXiv:2604.10180v2，2026-07-09。以下「PDF 第幾頁」指這份論文的檔案頁碼。系統名稱只用 Tessera。可直接口述正文；公式若經過整理，會在該頁註明。

## 第 01 頁｜Title

今天介紹 Tessera。論文作者是 Tiancheng Hu、Jin Qin、Zheng Wang、Junhao Hu、Yuzheng Wang、Lei Chen、Yizhou Shan、Mingxing Zhang、Ting Cao、Chunwei Xia、Huimin Cui、Tao Xie 和 Chenxi Wang。這份本地 PDF 是 arXiv:2604.10180v2，2026 年 7 月 9 日，沒有標示已發表的會議。它主張：要利用異質 GPU，不該只把 prefill 和 decode，或 attention 和 FFN，整塊搬到不同 GPU，而應該以 GPU kernel 為單位來拆。

Kernel 就是框架一次啟動的那段 GPU 程式，比一層或一個 phase 更細，又比 thread block 更粗。Tessera 先離線從 PTX 抽出 kernel 之間的資料依賴，PTX 是 NVIDIA 的平行執行中間碼。再依目標是 throughput 還是 latency，解一個 MILP。執行時用多個 request 把通訊藏起來，並用一個輕量的 monitor 在兩種策略之間切換。

實驗涵蓋五種 GPU、四類模型，叢集最大到 16 張 GPU。最後會對照 ThunderServe、Hetis 和 Helix，但不把倍率排成名次。

來源：論文首頁與摘要，PDF 第 1 頁。

## 第 02 頁｜Presentation Roadmap

四段。第一段說明為什麼 phase 和 block 仍然會把 kernel 放錯 GPU。第二段是方法：PTX 依賴、兩種 MILP、pipeline，以及 monitor。第三段是實驗，先看單對 GPU 的離線 throughput 和線上 SLO，再看叢集、pipeline 和頻寬。第四段談成本、模型範圍，以及和另外三個系統的切分差異。

比較頁是我們的整理，不是 Tessera 的原表。

來源：簡報結構。

## 第 03 頁｜Hardware Heterogeneity Is Kernel-Dependent

Table I 是規格和相對租金，不是 serving 實測。價格以 L40s 為 1，主要來自 Google Cloud 的標準價格。B200 的 tensor 算力和記憶體頻寬、以及 RTX Pro 6000 的 tensor 算力，表上帶有波浪號，報告時要保留「大約」。

相對 A100，L40s 的 CUDA core FP32 是 4.7 倍、tensor core BF16 是 1.2 倍，但記憶體頻寬只有 A100 的 45%。論文還說 L40s 和 RTX Pro 6000 的每美元計算吞吐最高到 7.4 倍。這句話沒有寫明除數是哪一張 GPU，所以不要自己指定成「相對 B200」或「相對 A100」。

沒有一張 GPU 同時贏過算力、頻寬、容量和價格。這只說明混搭有動機。

來源：Section II-A、Table I，PDF 第 2–3 頁。

## 第 04 頁｜Why Phase- or Block-Level Disaggregation Is Too Coarse

Figure 1 是示意，不是 profile。正常執行時 K1 到 K6 在同一張 GPU 上，黑色箭頭是控制順序。拆開之後，GPU A 可能跑 K1、K3、K4，GPU B 跑 K2、K5、K6。紅色箭頭是原本在本地記憶體完成的資料依賴，現在變成跨 GPU 的傳輸。

如果這些紅邊沒被正確找出來，拆 kernel 會算錯，而不是變快。後面的 analyzer 就是在補這件事。

來源：Section I、Figure 1，PDF 第 2 頁。

## 第 05 頁｜Kernel as the Scheduling Granularity

再細會怎樣？一個 kernel 裡面的 thread block 大致同質，繼續切不會對上不同的硬體偏好。再粗呢？Prefill 對 decode，或 attention 對 FFN，都會把偏好不同 GPU 的 kernel 綁在一起。

Kernel 是使用者層級的啟動單位，不是另一種模型層抽象。它還有一個實用後果：Mamba 沒有 attention block，diffusion 沒有 prefill 和 decode。Phase 或 block 的方法會直接不適用，kernel 在他們評估的四類模型裡都存在。這個「都存在」要等實驗頁再看哪些是完整評估、哪些只是離線。

來源：Section I、Section II-C，PDF 第 1–3 頁。

## 第 06 頁｜Different Kernels Prefer Different GPUs

Figure 2 比較 A100 和 L40s。模型是 Llama3 8B、GPT-oss 20B、Mamba 7B、Qwen2.5-VL 7B 和 SD3.5。橫軸概念是 L40s 執行時間除以 A100。

按 kernel 顆數，平均有 67% 的 kernel 在 L40s 上更快。但顆數不是時間。若用這些 kernel 在 A100 上占的端到端時間來加權，平均是 36%，diffusion 最高到 53%。所以可以說有一塊工作適合較便宜或較新的卡，不能說大多數執行時間都在 L40s 上更快。

備註：這一節寫 Mamba 7B。後面評估的 SSM 是 Mamba-Codestral 7B。不要把兩個名字當成同一個實驗。

來源：Section II-B、Figure 2，PDF 第 3 頁。

## 第 07 頁｜Phase Labels Hide Kernel-Level Variation

Figure 3 是 GPT-oss 20B。虛線以上的 kernel 在 A100 更快，以下的在 L40s 更快。即使在同一個 phase 裡，45% 的 prefill kernel 和 57% 的 decode kernel 在 L40s 上更快。所以把整個 phase 搬到一張卡，一定會放錯一大批 kernel。

作者用兩個 kernel 解釋原因。cublasGemv 大約 1 FLOP/byte，受記憶體頻寬限制。A100 的 HBM 頻寬約是 L40s 的 2 倍，這個 kernel 在 A100 上快 1.9 倍。FlashAttention 計算較重，L40s 受益於更大的 L2、更高的頻率和 tensor core，最快到 2.1 倍。Block 內部也一樣：71% 的 attention kernel 和 33% 的 FFN kernel 在 L40s 上更快。

Phase 標籤不是硬體偏好。

來源：Section II-C、Figure 3，PDF 第 3 頁。比值是 L40s 時間除以 A100 時間。

## 第 08 頁｜Three Challenges for Kernel Disaggregation

三個問題。第一是正確性：一個 kernel 可能讀另一張 GPU 上一個 kernel 剛寫的 buffer。使用者自定或 JIT 編譯的 kernel 不會把這件事寫在 API 上。第二是 bubble：下游 GPU 在等遠端資料時會閒置，除非另一個 request 的 kernel 能補上。第三是策略：離線工作要 throughput，線上 serving 要單次請求的 latency，而且負載會變。

放錯的代價是通訊和負載不均超過計算上的好處。後面的順序就是：analyzer、兩種 MILP、pipeline、monitor。

來源：Section I，PDF 第 1–2 頁。這三點是論文自己的問題設定。

## 第 09 頁｜Tessera System Overview

Figure 4 有四塊。Analyzer 離線看記憶體範圍、RAW 邊和每張 GPU 上的 kernel 延遲。RAW 是 Read-After-Write，也就是先寫後讀，真正的資料依賴。Planner 為每張依賴圖產生 kernel 到 GPU 的策略。每張 GPU 一個 worker，只跑分給它的 kernel，以及被切開的邊上的傳輸。Monitor 把執行時的延遲送回去，用來選策略。

圖下方畫了 high-end GPU 之間的 NVLink，以及通往 general-purpose GPU 的 RDMA。這是設計圖。哪些實驗真的用 NVLink、哪些只用 RDMA，要等實作和評估那兩頁，不要從這張圖推論每一對 GPU 都有 NVLink。

來源：Section III、Figure 4，PDF 第 4 頁。

## 第 10 頁｜Offline Planning and Online Adaptation

離線部分是 analyzer 和 planner，通常在 warm-up 做完。每個 CUDA graph 有自己的依賴圖和 MILP 解。CUDA graph 是把一連串 kernel 啟動錄下來重播的機制。這一步不在每個 token 的路徑上。

線上時，worker 看到某個 graph 被啟動，就查出已經建好的策略，用另外的 stream 把 send 和 recv 與計算重疊。Monitor 每個時間窗看一次佇列壓力，決定用哪一份策略。

MILP 沒有 GPU 記憶體容量限制。初始化時每張 GPU 都複製完整權重，和 prefill/decode 拆分的做法類似。

來源：Section III、Section IV，PDF 第 4–7 頁。

## 第 11 頁｜Analyzer: Standard vs. Opaque Kernels

Kernel 分兩類。標準函式庫，例如 cublasSgemm，讀 A、B，寫 C，大小就在 API 參數裡，不必猜。Opaque kernel 是使用者寫的或 JIT 編譯的，啟動時看不到記憶體存取模式。

先前的 PhoenixOS 會從 GPU API 參數推測 buffer 位址。它能看到基底位址，但 PyTorch 的 caching allocator 不會在每次建立 tensor 時都呼叫 CUDA 分配，所以推測的大小常常太大。太大的 buffer 仍會被傳輸。Tessera 改在 PTX 上插樁，只記錄 kernel 真正碰到的位址。

來源：Section III-A，PDF 第 4 頁。PhoenixOS 是被引用的先前工作，不是 Tessera 的元件。

## 第 12 頁｜PTX Instrumentation and Address Ranges

做法可以記成四步。給 kernel 多一個插樁用的 buffer，用 `ld.param` 載入。在每個 `ld.global` 或 `st.global` 前後，用 `atom.global.min` 和 `atom.global.max` 讓並行的 thread 共同維持一個最小和最大位址。Kernel 結束後，把這個區間對齊到 buffer 的基底位址，指令種類本身就說明是讀還是寫。改過的 PTX 用 `ptxas` 編回機器碼。探針引擎基於 NEUTRINO。

如果 kernel 透過不在啟動參數裡的 global 變數間接存取，基底位址未知。這時 Tessera 不拆這個 kernel，讓它留在同一張 GPU。論文引用的研究說，PyTorch 和 vLLM 裡沒有這種 kernel，Rodinia 裡有一個。這是適用範圍的聲明，不是 Tessera 自己掃過所有框架的新測量。

Analyzer 記錄的是被碰到的位址範圍，不是把 kernel 的算術重寫出來。

來源：Section III-A、Section IV、Listing 1，PDF 第 4–5 與第 7 頁。

## 第 13 頁｜Extracting RAW Dependencies

因為執行順序保持不變，Tessera 只建 RAW 邊。WAR 和 WAW 不會因為拆到不同 GPU 而改變這套順序下的結果，所以不是它要排程的邊。

實作上有一個 registry，記住每個 buffer 最後的寫入者。後面的 kernel 若讀這個 buffer，就從寫入者連一條邊，邊上標實測的位元組數。非同步記憶體拷貝也是圖上的節點，來源、目的和大小來自 API。

一張 CUDA graph 對應一張依賴圖。輸入形狀改變時，是多張圖，不是一張圖裡的動態分支。還沒有 CUDA graph 的框架，可以用前處理工具錄下 trace，再用 stream capture 做成等價的 graph。那是前處理，不是線上排程器。

來源：Section III-A，PDF 第 4–5 頁。DDG 是論文對這張圖的稱呼。

## 第 14 頁｜Cross-Iteration Dependencies and KV State

預設的圖是同一次 iteration 裡面的依賴。KV cache 是這一輪寫、下一輪讀。Analyzer 會跑多個 iteration，把這種 buffer 標出來。

執行時每張 GPU 留一份複本，只非同步傳送增量，也就是 delta。論文用兩個 NCCL communicator，把這個背景複製和延遲關鍵的依賴傳輸分開，依賴傳輸的 traffic class 優先權較高。NCCL 是 NVIDIA 的集合通訊庫。

論文說 delta 複製少於總延遲的 0.1%。這句話引用的是先前的 prefill/decode 工作，不是 Tessera 新測的數字。報告時要說「論文引用先前工作」，不要說成 Tessera 的消融結果。

KV 狀態是背景同步的複本，不是每輪 critical path 上的那條 cut edge。

來源：Section III-A、Section IV，PDF 第 5 與第 7 頁。

## 第 15 頁｜Planner Inputs, Decisions, and Objectives

Planner 的輸入是 GPU 集合、kernel 集合、RAW 邊、每個 kernel 在每張 GPU 上的延遲、每條邊的位元組數，以及 GPU 之間的頻寬和基礎延遲。決策變數 \(x_{k,g}\) 是二元的：kernel \(k\) 是否放在 GPU \(g\)。每個 kernel 恰好放一張 GPU。

兩個目標共用這張圖。離線、要 throughput 時，假設計算和通訊可以重疊，最小化最慢那張 GPU 的 stage 時間。線上、負載很低時，不假設重疊，把 kernel 時間和被切開的傳輸時間加總，拿來最小化。

Monitor 選的是哪一份已經解好的策略，不是在 request 路徑上重解。

來源：Section III-B、Table II，PDF 第 5 頁。符號是論文的；重疊與否是周圍正文的假設。

## 第 16 頁｜Offline Throughput-Oriented MILP

每個 kernel 對 GPU 的指派加總為 1。GPU \(g\) 的計算時間 \(T_g\) 是分到它的 kernel 延遲之和。Stage 時間 \(W_g\) 是計算時間和通訊時間的較大者。目標是最小化所有 GPU 的 \(W_g\) 的最大值。

穩定狀態下，系統 throughput 由最慢的 stage 決定，大約是每個 \(\max_g W_g\) 完成一個 request。這是離線目標。當同時在飛的 request 太少、蓋不住傳輸時，這個目標是錯的。

Gurobi 在離線解它。論文給的例子是 GPT-oss 20B、A100 加 L40s，大約 500 個 kernel，一張圖約 20 毫秒，把所有執行模式列完大約 5 秒。這 5 秒不在服務路徑上。

來源：Section III-B，PDF 第 5 頁。

## 第 17 頁｜Communication and Load-Balancing Constraints

一條跨 GPU 的邊，傳輸時間是基礎延遲加上位元組數除以頻寬。GPU \(g\) 的通訊時間 \(M_g\)，是所有切到它身上的這類邊的和。生產者在 \(u\)、消費者在 \(g\) 時，二次項 \(x_{i,u}x_{j,g}\) 用標準的布爾線性化改寫，這樣整個問題才仍是 MILP。

負載平衡沒有另外一條「變異數要小」的限制。最小化最慢 GPU 的 stage 時間，本身就會懲罰最忙的那張卡。

記憶體容量不在這個 MILP 裡。初始化時每張 GPU 拿到完整權重。離線、策略固定之後，用不到的權重 buffer 可以回收，用來放大 batch。論文沒有在結果表裡報告這個回收做了多少。

來源：Section III-B、Section IV，PDF 第 5 與第 7 頁。

## 第 18 頁｜Online Latency-Oriented Scheduling

負載低的時候，pipeline 蓋不住傳輸。這時目標改成所有 kernel 時間，加上所有被切開的傳輸時間，兩者相加再最小化。沒有 \(\max(T, M)\)，因為不假設重疊。

這個 MILP 仍然離線解。Worker 只查表。若通訊很貴，這個目標會把有依賴的 kernel 留在同一張 GPU。Figure 11 在 25 Gb/s 的線上輕負載裡，就是這個行為：latency 仍低於單獨的 A100，因為策略少傳了一些資料。

Latency 模式縮短的是單個 request 的 critical path。它不是把 throughput 公式換個名字。

來源：Section III-B，PDF 第 6 頁。投影片上的求和是為了說明而壓過的，項的內容與論文一致。

## 第 19 頁｜Pipelining Across Requests

沒有 pipeline 時，GPU 在等遠端 buffer 的期間是空的。後面的測量裡，這種做法大約只有零通訊理想值的一半 throughput。

每個正在處理的 request 用一條 CUDA stream。一條 stream 被依賴堵住時，硬體可以去跑其他 stream 上已經就緒的 kernel。若所有 stream 優先權相同，它們容易同時走進通訊，GPU 還是會閒。Tessera 讓較晚的 request 使用較低的 stream 優先權，硬體就會先給較早的 request，讓通訊錯開。

這裡的 optimal 是假設通訊開銷為零的參考線，不是另一個更準的 kernel。

來源：Section III-C；一半 throughput 和優先權的數字在 Section V-D、Figure 9，PDF 第 6 與第 9 頁。

## 第 20 頁｜GPU Worker Execution

Figure 5 對應 Figure 1 裡的 GPU B。上面是計算 stream，下面是通訊 stream，中間用 CUDA event 對齊。\(R_{ij}\) 是為了 kernel \(j\) 去接收 kernel \(i\) 的輸出，\(S_{ij}\) 是把 kernel \(i\) 的輸出送出去。

有進來的 cut edge 時，worker 先發出接收，再啟動 kernel。Kernel 做完若有出去的 cut edge，再發傳送。這些 send 和 recv 是 GPU 端的 kernel，走 NCCL 的 GPUDirect Async，也就是 IBGDA，CPU 不在這條關鍵路徑上。

一個 worker 只跑分給它的 kernel 和被切開的訊息，不跑整份模型。

來源：Section III-C、Figure 5，PDF 第 6 頁。

## 第 21 頁｜Overlapping Communication and Computation

Tessera 攔截 CUDA graph 的建立，按策略把節點分到各 GPU，再把 send 和 recv 嵌進每張子圖。Stream 之間的 event 變成子圖裡的普通依賴邊，重播時不再額外同步。

每個 worker 有一張表，從原本的 graph handle 對到策略和子圖。啟動時查表，不重建圖。

它也可以和 tensor parallelism 疊加。既有的集合通訊仍留在原本那組同質 GPU 上，Tessera 只重排配對 GPU 之間的計算 kernel。8 張 B200 加 8 張 H100 的實驗就是這樣：每一對 B200 和 H100 是一個 TP rank。這不是把所有 collective 都改寫了。

來源：Section III-C、Section IV、Section V-C，PDF 第 6–7 與第 9 頁。

## 第 22 頁｜Online Monitor Signals

Monitor 記三類東西：每個 request 的延遲、通訊時間，以及 kernel group 的延遲。Kernel group 不是單顆 kernel，而是兩次連續通訊之間的那一串 kernel。線上不對每顆 kernel 計時，這樣開銷較小。

\(\bar L_{\mathrm{req}}\) 是平均的端到端請求延遲。\(\bar L_{\mathrm{exec}}\) 把計算和通訊加起來，但不含排隊。壓力指標是兩者的比。比值低，表示幾乎沒有排隊，適合 latency 策略。比值高，表示排隊主導端到端時間，改用 throughput 策略來提高處理能力。

這個訊號是論文定義的比值，不是我們另起的 GPU 計數器。

來源：Section III-D，PDF 第 6–7 頁。

## 第 23 頁｜Policy Switching and Sensitivity Parameters

兩個旋鈕。時間窗 \(W\) 決定多久看一次比值。閾值 \(\beta\) 決定比值多高就換成 throughput 策略。論文選的預設是 300 毫秒和 1.5。

每次切換要在一個 iteration 邊界把所有 worker 對齊，論文報告的停頓大約 30 毫秒。這是該次測量的停頓，不是形式上的上界。

調參用的是 GPT-oss 20B、360 秒的 Azure Conversation trace。太頻繁和太遲鈍的代價在 Figure 10，下一頁的敏感度只先記住：兩個方向都會讓延遲變差。

來源：Section III-D、Section V-D，PDF 第 6–7 與第 10 頁。

## 第 24 頁｜Implementation Stack

GPU worker 大約 3,000 行 C++ 和 CUDA，analyzer 大約 2,000 行 Python，接上 vLLM 和 PyTorch。評估用的是 vLLM v0.18.0。

Gurobi 的時間就是前面那組：兩張 GPU、約 500 個 kernel，一張圖約 20 毫秒，列舉模式約 5 秒。這些行數是論文自己的規模描述，不要拿去和 Helix 的 1,500 加 1,700 行比「誰更複雜」。

間接、且不在啟動參數裡的 global 存取，會退回不拆分。論文認為這在 PyTorch 和 vLLM 裡少見。

來源：Section IV、Section III-B，PDF 第 5 與第 7 頁。

## 第 25 頁｜Communication Backends and Interconnects

評估的通訊後端是 NCCL，cut edge 用 GPU 發起的 IBGDA。

本地三對是 A100 加 L40s、H100 加 RTX Pro 6000、B200 加 H100。每張 GPU 配一張 200 Gb/s 的 RDMA 網卡。論文沒有說這三對之間用 NVLink。A100 和 L40s 這種不同架構，也不應自行假設有 NVLink。

叢集實驗才寫 NVLink：在同質的 high-end 組內。跨節點則是 RDMA，2 張 A100 加 1 張 L40s 用 200 Gb/s，8 加 8 用 400 Gb/s。Figure 4 的連線是設計圖，不是這份接線表。

論文明確把範圍放在 NVIDIA。它沒有評估 AMD、NPU、只靠 PCIe 的主機，或 Ethernet。這些「沒有測」不要補成「不能用」，也不要補成「已經支援」。

來源：Section IV、Section V-A，PDF 第 7–8 頁。

## 第 26 頁｜Evaluation Methodology

離線模型有四類。LLM 是 Llama-3 8B 和 GPT-oss 20B，SSM 是 Mamba-Codestral 7B，兩者用 Splitwise 對話資料，中位數輸入 1020、輸出 129。MLLM 是 Qwen2.5-VL 7B，COCO 圖片縮到 512 乘 512。Diffusion 是 Stable Diffusion 3.5，PartiPrompts，1024 乘 1024，28 步去噪。

Baseline 有同質的左卡和右卡、PD 和 AF。PD 依 DistServe，把 prefill 和 decode 分到不同 GPU，diffusion 沒有這個分離，所以不適用。AF 依 MegaScale-Infer，把 attention 和 FFN 分開，SSM 和 diffusion 不適用。圖上的紅叉是不適用，不是 throughput 為 0。

引擎是 vLLM v0.18.0，打開 continuous batching，關掉 DVFS。每個實驗重複多次，變異低於 1%，論文沒有寫精確的重複次數。Throughput 對 LLM、SSM、MLLM 是每秒輸出 token。Diffusion 在 Figure 6 的右軸是每分鐘圖片，正文也稱為每分鐘 request。線上實驗只有 GPT-oss 20B，Poisson 到達，monitor 另用一段 Azure trace。

線上的 normalized latency 是端到端延遲除以輸出 token 數。

來源：Section V-A，PDF 第 7–8 頁。

## 第 27 頁｜Offline Throughput

Figure 6 是五個工作負載、三對 GPU 的最大可持續 throughput。左軸是 token 每秒，SD 用右軸的圖片每分鐘。

相對 PD，平均 1.5 倍，最高 2.3 倍。相對 AF，平均 1.35 倍，最高 1.7 倍。論文沒有把這兩個最高值指到某一根具名的柱子，所以不要指著某一格說「就是這根 2.3 倍」。摘要的 throughput 2.3 倍，就是相對既有 disaggregation 的這個上界。

作者把增益歸因於：phase 或 block 會綁在一起的 kernel，被分開對到不同 GPU。

來源：Section V-B、Figure 6，PDF 第 8 頁。

## 第 28 頁｜Online Latency under a Token SLO

這一頁只有 GPT-oss 20B，Poisson 到達，三對 GPU。縱軸是每個輸出 token 的端到端延遲。紅線是 SLO，50 毫秒每個 token。

論文沒有把這個指標叫做 goodput。Goodput 是 DistServe 那類工作常用的詞，指在 SLO 內完成的有效吞吐。Tessera 這裡報告的是 normalized latency，以及在 50 毫秒這條線之下能撐住的 request rate。

低負載時，Tessera 的 normalized latency 比 PD 低 1.3 倍、比 AF 低 1.2 倍。在 SLO 下，它能撐的 request rate 最高是最好 baseline 的 1.3 倍。摘要說的「同樣 SLO 下多服務 1.3 倍 request」就是這句。

低負載的延遲，和高負載下還不破 SLO 的容量，是兩個操作點。

來源：Section V-B、Figure 7，PDF 第 8 頁。

## 第 29 頁｜Scaling with Cluster Size

兩個離線叢集。GPT-oss 20B 在 2 張 A100 加 1 張 L40s 上，PD、AF、Tessera 是 2987、3144、4253 token 每秒。Qwen-3 235B 在 8 張 B200 加 8 張 H100 上，是 4367、4912、6799。

在不對稱的三張卡上，Tessera 直接解一個三 GPU 的 MILP。PD 用 L40s 做 prefill，每張 A100 各自做 decode。AF 把 attention 放在兩張 A100 上、TP 等於 2，FFN 放在 L40s。八加八則是每一對 B200 和 H100 一個 TP rank，集合通訊留在 high-end 組的 NVLink 上。

論文把這兩個設定概括成相對 PD 1.5 倍、相對 AF 1.4 倍。用柱子算，第一組相對 PD 約 1.42 倍，第二組約 1.56 倍，平均接近 1.5。報告時可以說概括值，也可以說柱上的絕對值，但不要把 1.5 倍說成每一組都剛好 1.5。

Qwen-3 235B 不在 Figure 6 的單對套件裡。

來源：Section V-C、Figure 8，PDF 第 9 頁。單位是 token 每秒。

## 第 30 頁｜Pipeline Effectiveness

Figure 9 是 GPT-oss 20B 的離線 pipeline 消融。圖說沒有寫 GPU 配對。沒有 pipeline 是 1443 token 每秒，大約是 2734 這條零通訊參考線的一半。加上 pipeline 是 2123，為無 pipeline 的 1.47 倍。再加優先權是 2641，達到參考線的 96.6%。瓶頸 GPU 上，通訊閒置從接近一半降到 4% 以下。

備註：2641 和 Figure 11 在 200 Gb/s、A100 加 L40s 的那一點相同。這是我們對兩張圖的對讀，不是 Figure 9 圖說寫明的硬體。

優先權的作用是讓傳輸不要同時發生。成本模型假設穩態下通訊可以完全重疊；這張圖顯示剩餘閒置低於 4%，不是零。

來源：Section V-D、Figure 9，PDF 第 9 頁。

## 第 31 頁｜Online Monitor Sensitivity

Figure 10 仍是 GPT-oss 20B、360 秒的真實 trace。左圖固定 \(\beta = 1.5\) 掃時間窗，右圖固定 300 毫秒掃閾值。

\(W = 30\) 毫秒或 \(\beta = 1.1\) 會切太勤，延遲最高到 1.32 倍。\(W = 1.5\) 秒或 \(\beta = 3.0\) 反應太慢，延遲最高到 1.55 倍。每次切換約 30 毫秒的停頓會累積。作者選 300 毫秒和 1.5，是這次掃描裡的折衷，不是普遍常數。

太頻繁和太少切換，在這條 trace 上都會讓延遲變差。

來源：Section V-D、Figure 10，PDF 第 10 頁。

## 第 32 頁｜Network Bandwidth and MILP Analysis

Figure 11 左圖是 GPT-oss 20B、A100 加 L40s，頻寬從 200 降到 25 Gb/s。Throughput 依序是 2641、2610、2550、2490 token 每秒，25 Gb/s 的下降不到 6%。Normalized latency 是 1.00、1.03、1.08、1.15，仍低於同質 A100 的 1.18。離線時 pipeline 把變慢的傳輸藏在其他 request 後面。線上輕負載時，latency 策略會少做跨 GPU 傳輸。

右圖是求解時間。正文給的兩張 GPU 數字是：200 個 kernel 0.07 秒，1000 個 kernel 0.43 秒。DeepSeek-V3 671B 的一次 forward、大約 1500 個 kernel，可以在 1 秒內解完。這是求解器壓力測試，不是端到端服務結果。時間隨 GPU 種類數上升；重複的層可以共用放置，把問題縮小。

來源：Section V-D、Figure 11，PDF 第 10 頁。

## 第 33 頁｜Cost Efficiency of Heterogeneous Pairing

Table III 的 Perf/\$ 是五個工作負載的平均 throughput，除以租金，再對左側那張同質 GPU 正規化。拆分方法要付兩張卡的錢。

A100 加 L40s 上，Tessera 是 1.21，PD 是 0.87，AF 是 1.02，右側同質 L40s 是 1.18。H100 加 RTX Pro 6000 上，Tessera 是 1.64，右側同質卡自己是 2.01。B200 加 H100 上，Tessera 是 1.01，只略高於單獨的 B200，但仍高於 PD 的 0.70 和 AF 的 0.74。

相對 PD，成本效率平均 1.5 倍、最高 1.6 倍。相對 AF，平均 1.4 倍、最高 1.5 倍。摘要的 1.6 倍指的是這個成本效率上界。

H100 加 RTX Pro 6000 這組，論文說 Tessera 的成本效率是單張 H100 的 1.64 倍，throughput 是單張 H100 的 2.3 倍，因此超過兩張 H100，而且更便宜。2.9 加 1.2 對上 2 乘 2.9，是我們用 Table I 的相對價格做的加法，用來說明「更便宜」指的是這組相對租金，不是新的報價。

來源：Section V-B、Table III，PDF 第 9 頁。這裡的 2.3 倍寫在成本效率段落，不要和相對 PD 的 throughput 上界混成同一次比較，除非論文自己把它們連在一起。論文這段是在說相對 H100。

## 第 34 頁｜Generality Across Model Families

「四種模型」指的是離線、三對 GPU 上的 Llama-3 8B、GPT-oss 20B、Qwen2.5-VL 7B、Mamba-Codestral 7B 和 Stable Diffusion 3.5。AF 需要 attention，所以 Mamba 和 diffusion 不適用。PD 需要 prefill 和 decode，所以 diffusion 不適用。

線上 SLO 只有 GPT-oss 20B。叢集離線另外有 Qwen-3 235B。DeepSeek-V3 671B 只用來測求解時間。

動機段的 Mamba 7B 和評估段的 Mamba-Codestral 7B 不要合併。四類家族的證據是離線 kernel 拆分。它還不是每一類的線上延遲結果。

來源：Section II-B、Section V-A 到 V-D，PDF 第 3 與第 7–10 頁。

## 第 35 頁｜Tessera vs. ThunderServe, Hetis, and Helix

這一頁是我們的整理。ThunderServe 以 phase 為單位，決定分組和 prefill 或 decode 的角色。Hetis 把 dense 計算和 attention head 分開，線上可以重分配 head 並搬移 KV。Helix 以層的區間和跨節點路徑為單位，放置做一次，每個 request 選路。Tessera 以 kernel 為單位，離線解 MILP，再用 \(\bar L_{\mathrm{req}} / \bar L_{\mathrm{exec}}\) 在時間窗上切換。

移動的狀態分別是 phase 邊界的 KV、head 級的 QKV 與 KV、token 和 activation，以及被切開的 kernel 輸出；KV 在 Tessera 裡是背景 delta。環境上也不同：異質雲、本地異質叢集、含跨區模擬的異質叢集，以及論文寫明的 NVIDIA 配對與 NVLink、RDMA。

不要用 2.3 倍、3.3 倍這類數字跨論文排名。硬體、模型、workload 和指標都不相同。

備註：本頁為跨論文整理。各欄依該系統自己的論文，不是 Tessera related work 對他人的評價。

## 第 36 頁｜Limitations and Threats to Validity

MILP 沒有每張 GPU 的記憶體限制，完整複製權重是保守做法。回收未使用 buffer 只在策略固定的離線情況被描述，結果表沒有報告。

線上延遲、SLO 和 monitor 掃描都是 GPT-oss 20B。Diffusion 和 Mamba 是離線配對結果。Delta 複製少於 0.1% 來自先前 PD 工作的引用。通訊閒置低於 4% 才是 Tessera 自己的 Figure 9。

間接 PTX 存取會退回單卡。研究範圍是 NVIDIA。Figure 9 的圖說沒有寫 GPU 配對。每次策略切換大約停 30 毫秒。

和 Helix、Hetis、ThunderServe 沒有同一套硬體上的對打。這個空白是我們的觀察，不是 Tessera 的結論句。

來源：Section IV、Section V、Section VII。

## 第 37 頁｜Conclusion

三件事。第一，phase 和 block 仍會混合偏好不同 GPU 的 kernel，Tessera 改以 kernel 放置。第二，正確性來自 PTX 的位址範圍和 RAW 圖；throughput MILP 假設計算和通訊可以重疊，latency MILP 不假設。第三，在報告的配對上，相對 PD 的 throughput 最高 2.3 倍，成本效率最高 1.6 倍；H100 加 RTX Pro 6000 這一組可以在更低的相對租金下，超過兩張 H100 的 throughput。

離線實驗也覆蓋 PD 或 AF 不適用的模型。Monitor 的 1.3 倍是 GPT-oss 20B、50 毫秒每個 token 的 SLO，不是另一篇論文定義下的 goodput。

來源：Section VII；倍率回查 Section V-B，PDF 第 8–9 與第 11 頁。

## 第 38 頁｜Questions & Discussion

可以追問的有三點。依賴圖是靜態的 RAW，還是會在每個 token 重分析？兩個 MILP 一個假設通訊能被蓋住，一個不假設，monitor 只是在兩者之間選。最後，哪些模型真的被服務過，哪些只出現在求解時間或動機 profile 裡。

若接到這個系列的其他系統：Tessera 是 kernel，Helix 是層和路徑，Hetis 是 head，ThunderServe 是 phase。它們解決的瓶頸不同，沒有共同的實驗排名。

備註：問答頁沒有新的實驗數字。
