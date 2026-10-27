# 10 分鐘 Paper Review 中文講稿

對應 `2026-10-28-10min-Review.tex` 與獨立的 12 頁 PDF。第 01 頁是封面，第 02 頁是今天的時間軸，第 03–11 頁是 10 分鐘內容，合計 600 秒，第 12 頁是 Thank you。頁腳是這份 PDF 自己的 `n/12`，不是 Main deck 的頁碼。

ThunderServe 事實只依 `2026-10-21-meeting/MLSys25_Thunderserve.pdf`。Hetis 事實只依 `2026-10-21-meeting/SC25_Hetis.pdf`。

## 第 01 頁｜Title

預計時間：約 15 秒。不計入後面九頁的 10 分鐘。

這份是獨立的十分鐘 paper review，只談 ThunderServe 和 Hetis。ThunderServe 四分鐘，Hetis 四分鐘，最後兩分鐘比較它們切分 GPU 的粒度。頁碼是這份簡報自己的頁碼。

來源：報告者整理的範圍。ThunderServe 為 MLSys 2025；Hetis 為 SC 2025。

## 第 02 頁｜Presentation Roadmap

預計時間：約 30 秒。不計入後面九頁的 10 分鐘。

今天正式報告是三十分鐘，分成三段，每段十分鐘。第一段是 ThunderServe 和 Hetis，回顧上週的重點並做比較，就是這份簡報。第二段是 Helix，第三段是 Tessera，兩篇都是新論文的精簡報告。另外準備了十分鐘的兩篇 HBF，那是備用內容，不佔這三十分鐘。

來源：報告者整理的會議時間，不是論文結論。

## 第 03 頁｜Why Heterogeneous GPU Serving Needs Phase-Aware Scheduling

預計時間：50 秒。

論文觀察是，prefill 比較吃算力，decode 比較吃記憶體頻寬。以 A40 和 3090 Ti 為例，A40 的算力較強，在 prefill 比較有優勢；3090 Ti 的記憶體頻寬較高，在 decode 比較有優勢。Figure 1 的例子也顯示，以單筆 request 的成本來看，prefill 用 A40 比較便宜，decode 用 3090 Ti 比較便宜。所以兩個 phase 適合的 GPU 可能不同。

不過雲端能用的 GPU 種類和數量都有限，網路也不快，而且每對 GPU 之間的頻寬不一樣。Prefill 和 decode 分開之後，KV cache 還要從 prefill group 傳到 decode group，所以不能只看算力或頻寬來分 GPU。真正要一起決定的是：GPU 怎麼分、phase 放在哪，以及這段傳輸怎麼走。

論文出處：Sec. 1，Figure 1，Table 1。Figure 1 是單筆 request 的價格，不是整個 cluster 的 throughput。

## 第 04 頁｜Joint Optimization of GPU Placement, Parallelism, and Routing

預計時間：65 秒。

作者方法是把 GPU Placement 收成兩層，Figure 3 就是這個流程。上層用 Tabu Search，先把異質 GPU 組成 group，每一組負責一個 model replica，再指定這組做 prefill 還是 decode。下層接著決定每組的 TP 和 PP，以及 prefill replica 和 decode replica 之間 request 怎麼送。這個 routing 要看網路，因為 KV cache 得傳得過去。

兩層是一起評估同一個 deployment plan：下層算出這個分組和 phase 的表現，再交回上層繼續搜。不是先隨便分完組，才事後補平行設定。另外兩個機制這裡只點名，KV cache compression 用來縮小傳輸量，lightweight rescheduling 用來在負載或可用 GPU 改變時調整 phase 和 routing。這頁不講 Tabu Search 的 neighbor operators，也不寫線性規劃。

論文出處：Sec. 3.2–3.4，Figure 3。壓縮和 lightweight rescheduling 是作者的機制，效果留到後面的實驗頁，不在這張流程圖裡。

## 第 05 頁｜Does Phase-Aware Scheduling Improve Serving Efficiency?

預計時間：80 秒。

這頁的研究問題是，依照 workload 調整 phase placement，能不能提高 end-to-end throughput。

實驗設定要用 LLaMA-30B，workload 是 Azure 的 coding 和 conversation。論文觀察到 coding 的 prompt 較長、輸出較短，conversation 則相反。比較對象的機器並不相同。HexGen 和 ThunderServe 在同一組異質雲端 GPU 上比，一共 32 張，包含 A6000、A5000、A40 和 3090 Ti。DistServe 是價格接近的同質環境，8 張 A100，不能說成同一套硬體。

實驗結果分兩層看。Table 3 是排程找出的部署：coding 用 8 個 prefill replicas 和 4 個 decode replicas，conversation 用 4 個 prefill 和 8 個 decode。這表示 replica 比例會跟著 input、output 的長短調整。Figure 9 再把 throughput 用 ThunderServe 正規化。相對 HexGen，coding 是 1.5 倍、conversation 是 1.3 倍；相對 DistServe，coding 是 1.5 倍、conversation 是 2.1 倍。圖上的 vLLM 也是 in-house，不要跟 HexGen 那組混在一起。

它證明的是，在異質資源限制下，workload-aware 的 phase placement 可以提升整體 throughput。沒有證明兩種 baseline 是在同一批 GPU 上被比較。

論文出處：Sec. 5.1–5.3，Figure 9，Table 3。正文寫的就是 HexGen 的 1.5／1.3 倍，以及 DistServe 的 1.5／2.1 倍。

## 第 06 頁｜Phase-Aware Deployment Improves Cost Efficiency

預計時間：45 秒。

三點收束。第一是作者方法：GPU grouping、phase designation、TP/PP 和 request routing 放在同一個 deployment plan。第二是論文整體的實驗結果，平均 1.7 倍、最高 2.1 倍的 throughput。這句在摘要，不要把它說成 Figure 9 的某一根 bar。第三是 Table 4 的時間。Full rescheduling 總共 157 秒，裡面是重新搜尋再加上重新載入模型；lightweight rescheduling 是 13 秒，而且 reload 是 0。兩者的差距包含有沒有付出模型載入，不只是搜尋本身變快。

報告者整理是，異質 GPU serving 的效益來自同時考慮 inference phase、硬體分配和通訊。ThunderServe 停在 phase 這個粒度；更細的 workload partitioning 是另一個方向，今天先接到這裡。

論文出處：摘要與 Sec. 6 的 1.7 倍／2.1 倍；Sec. 5.4 與 Table 4 的 157 秒和 13 秒。Table 4 的細項是 full 54(±5) 秒加 reload 103(±10) 秒，lightweight 13(±2) 秒加 reload 0 秒。

## 第 07 頁｜Hetis: Why Static Parallelism Wastes GPU Resources

預計時間：45 秒。

Hetis 問的是，異質 GPU 能不能用同一套 model parallelism 跑所有 module。論文觀察主要看 Figure 2。那是 Llama-70B 單層 decode 的 MLP 和 Attention 執行時間，每筆 sequence length 是 1000，不是整個模型的 end-to-end latency，也不是記憶體頻寬的比較。MLP 上低階 GPU 落後很多，正文說 P100 在 decode MLP 平均最多落後 A100 約 40.4 倍；Attention 的差距小得多。所以低階 GPU 很容易拖住 dense computation。固定切分還會讓 KV cache 空間不平均。Figure 1 的例子是，3090 的 cache 用完時，A100 還有不少空間空著。因此作者要的是看 module、切得更細、而且可以動態調整的 parallelism。這頁只建立問題，不是說 Primary 一定是頻寬最高的 GPU。

論文出處：Sec. 2.2–2.4，Figure 1–2。

## 第 08 頁｜Hetis: Selective Primary Workers and Dynamic Head-wise Attention

預計時間：90 秒。

作者把 GPU 分成兩種角色，選擇標準是模型執行成本，不是 FLOPS 或頻寬排名。Primary 由 Parallelizer 依 dense computation 的成本和通訊成本搜出來。它們用 TP、PP，必要時再用 DP，一起放完整模型的參數，負責 prefill、decode 的 dense modules，以及沒有被 offload 的 attention heads。Attention worker 通常是對 dense 計算幫助不大的 GPU，主要做一部分 decode attention 和對應的 KV cache，不必再存一份完整權重。預設的排除門檻是，拿掉這張 GPU 之後，dense cost 增加不超過 Δ = 0.05。

Decode 時，Primary 先算 QKV projection。如果某些 heads 分給遠端 worker，Primary 只送這些 heads 當前 token 的 Q、K、V。Attention worker 用自己留下的歷史 KV cache 算 attention，把 output 送回 Primary，Primary 再做 output projection 和 MLP。這段通訊會在不同 layer 重複，但平常的 decode 不用每一步重傳整段歷史 KV cache。沒被 offload 的 heads 留在 Primary 本地算。GQA 還要維持 query head 和它對應的 KV head 群組。

Figure 3 把系統收成四個組件。Parallelizer 決定 worker 和 TP/PP，Profiler 預測計算與通訊成本，Dispatcher 在線上分配 heads，Hauler 做 head 等級的 KV cache 管理和搬移。Figure 4 和 Figure 6 這次不放上主投影片，留著回答搜尋流程和 head 切分的細節。

論文出處：Sec. 3–5，Figure 3。Δ = 0.05 在 Sec. 4.1。GQA 的群組比例在 Sec. 5.1。

## 第 09 頁｜Hetis: Does Head-wise Parallelism Improve Serving Performance?

預計時間：65 秒。

這頁只回答兩個問題：這樣的配置能不能提高 end-to-end throughput，以及可用的 KV cache 空間有沒有變大。

實驗是四台主機，4 張 A100-80GB、4 張 3090、4 張 P100，主機之間 100 Gbps。模型是 Llama-13B、OPT-30B 和 Llama-70B。Baseline 是 Splitwise 和 Hexgen。Workload 是 ShareGPT、HumanEval 和 LongBench。Figure 10 是 Llama-70B 的 normalized end-to-end latency 對 request rate，縱軸是延遲，單位 s/token，不要把它念成 throughput。論文是看系統能撐到多高的 request rate，再把這個讀成 throughput。實驗結果的最高值是相對 Splitwise 2.25 倍、相對 Hexgen 1.33 倍。這是不同設定下的最高改善，不是所有 workload 的平均。在這個 Llama-70B 實驗裡，搜尋把 A100 和 3090 留成 Primary，P100 做 Attention worker。那是該次搜尋的結果，不是一般規則。

Figure 11 是最大可用 KV cache。相對測試過的 baselines，最高約 1.87 倍。另外，1.49 倍是 Section 7.3 裡 decode attention module 的 latency，不是整段 end-to-end latency 都改善 1.49 倍。報告者的整理是，較細的 attention 放置同時減少計算不平衡和 KV cache 沒用完的情況，所以服務容量提高。

論文出處：Sec. 7.1–7.3，Figure 8–13。2.25 倍和 1.33 倍在 Sec. 7.2；1.87 倍對應 Figure 11；1.49 倍在 Sec. 7.3。

## 第 10 頁｜Hetis: Main Contributions and Takeaways

預計時間：40 秒。

三個貢獻可以收在一起。第一是依 module 的成本指派 worker。第二是 decode attention 按 head 動態平行，沒被分出去的 head 留在 Primary。第三是線上的 head dispatch，以及 head 等級的 KV cache migration。實作上，作者把 Hetis 做成 vLLM 的擴充，不是只靠 GPU simulator。裡面有 head-level 的 KV cache、用來讀寫 cache 的 CUDA kernels、NCCL 的 peer-to-peer，並重用 PagedAttention。投影片上的 GitHub 是 vLLM 專案本身，不是 Hetis 的官方 repository。主要的 end-to-end serving 結果來自真實 GPU cluster。Section 7.4 另外用大規模模擬看 Parallelizer 的搜尋成本，不要把它說成主要的服務實驗。

論文出處：Sec. 6 的實作，Sec. 7.1–7.2 的 cluster 結果，Sec. 7.4 的搜尋模擬，Sec. 9 的結論。vLLM 連結是 https://github.com/vllm-project/vllm。

## 第 11 頁｜ThunderServe vs. Hetis: Different Granularities of GPU Specialization

預計時間：120 秒。

這兩篇都在異質 GPU 上做專門化，但切的單位不一樣，所以不是粗細的排名。ThunderServe 是部署層的資源分配。它先把 GPU 分成 prefill group 和 decode group，中間傳 KV cache，再決定 TP/PP 和 request routing。Hetis 是 module 和 head 的工作分配。Primary workers 一起放模型權重；Attention workers 不必再存一份完整模型，decode 時只處理被分出去的 heads。

通訊也不一樣。ThunderServe 要在 prefill 和 decode replica 之間搬 KV cache。Hetis 在 decode 的每一層，只為被 offload 的 heads 送當前 token 的 Q、K、V 和 attention output，歷史 KV cache 留在 worker 上。兩邊都會看計算、記憶體和通訊成本，但 lightweight rescheduling 是在改 phase 和 routing，online head dispatching 是在改 heads 怎麼分，不是同一個機制。

實驗上的最高 throughput 倍數不能直接拿來比誰比較好，因為硬體、workload 和 baseline 都不同。報告者的整理是，ThunderServe 最佳化 phase-level deployment，Hetis 最佳化 module-aware 的執行和 head-level attention placement。這句話收束這份十分鐘回顧。Helix 和 Tessera 在另一份主簡報，不在這份 PDF 裡。

論文出處：比較表是報告者整理，不是兩篇的共同實驗。ThunderServe 依據 Sec. 3 與 Table 3–4；Hetis 依據 Sec. 3–5 與 Sec. 7。上方流程是 Conceptual comparison，不是論文原圖。

## 第 12 頁｜Thank you

預計時間：約 10 秒。不計入 10 分鐘。

以上是 ThunderServe 和 Hetis 的十分鐘回顧。兩篇處理的粒度不同，這裡先停下來。

來源：報告者整理的收束，不是論文結論。
