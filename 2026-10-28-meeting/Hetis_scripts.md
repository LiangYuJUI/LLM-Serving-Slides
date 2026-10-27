# Hetis 四分鐘摘要講稿

對應獨立簡報 `2026-10-28-10min-Review.pdf` 第 07–10 頁，也就是 `Hetis/Hetis-summary-frames.tex` 的四個 frames。頁碼是這份 12 頁 Review 自己的頁碼，不是 Main deck。時間 45 + 90 + 65 + 40 秒，合計 240 秒。第 11 頁的比較在 `2026-10-28-10min-Review_scripts.md`。

事實只依 `2026-10-21-meeting/SC25_Hetis.pdf`。下面把論文觀察、作者方法、實驗結果和報告者整理分開。沒有標成實驗結果的句子，不要念成論文已經證明的結論。

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
