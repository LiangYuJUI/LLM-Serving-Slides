# ThunderServe 四分鐘摘要講稿

對應 `2026-10-28-Meeting-Main.pdf` 第 02–05 頁，也就是 `ThunderServe/ThunderServe-summary-frames.tex` 的四個 frames。頁碼是整份 Main PDF 的頁碼。時間 50 + 65 + 80 + 45 秒，合計 240 秒。指圖包含在時間內。

事實只依 `2026-10-21-meeting/MLSys25_Thunderserve.pdf`（arXiv:2502.09334v2）。下面用「論文觀察」「作者方法」「實驗結果」「報告者整理」分開，沒有標成實驗結果的句子不要念成論文已經證明的結論。

## 第 02 頁｜Why Heterogeneous GPU Serving Needs Phase-Aware Scheduling

預計時間：50 秒。

論文觀察是，prefill 比較吃算力，decode 比較吃記憶體頻寬。Table 1 裡，A40 的 FP16 是 149.7 TFLOPS，3090 Ti 是 71 TFLOPS；頻寬反過來，3090 Ti 有 1008 GB/s，A40 是 696 GB/s。所以兩個 phase 合適的 GPU 可能不同。Figure 1 用一筆 request 的價格來看，input 512、output 16：prefill 在 A40 比較便宜，decode 在 3090 Ti 比較便宜。

作者要處理的困難是，雲端 GPU 的種類和數量都有限，網路頻寬也不高，而且每對 GPU 不一樣。Phase 拆開之後，還得把 KV cache 從 prefill replica 傳到 decode replica。報告者整理是：只看 FLOPS 或 bandwidth 來分 GPU 並不夠，因為中間多了這段傳輸。這頁先停在研究問題，怎麼一起決定 GPU 怎麼分、phase 放在哪、通訊怎麼走，先不講演算法。

論文出處：Sec. 1，Figure 1，Table 1。Figure 1 是單筆 request 的價格，不是整個 cluster 的 throughput。

## 第 03 頁｜Joint Optimization of GPU Placement, Parallelism, and Routing

預計時間：65 秒。

作者方法是把部署收成兩層，Figure 3 就是這個流程。上層用 Tabu Search，先把異質 GPU 組成 group，每一組負責一個 model replica，再指定這組做 prefill 還是 decode。下層接著決定每組的 TP 和 PP，以及 prefill replica 和 decode replica 之間 request 怎麼送。這個 routing 要看網路，因為 KV cache 得傳得過去。

兩層是一起評估同一個 deployment plan：下層算出這個分組和 phase 的表現，再交回上層繼續搜。不是先隨便分完組，才事後補平行設定。另外兩個機制這裡只點名，KV cache compression 用來縮小傳輸量，lightweight rescheduling 用來在負載或可用 GPU 改變時調整 phase 和 routing。這頁不講 Tabu Search 的 neighbor operators，也不寫線性規劃。

論文出處：Sec. 3.2–3.4，Figure 3。壓縮和 lightweight rescheduling 是作者的機制，效果留到後面的實驗頁，不在這張流程圖裡。

## 第 04 頁｜Does Phase-Aware Scheduling Improve Serving Efficiency?

預計時間：80 秒。

這頁的研究問題是，依照 workload 調整 phase placement，能不能提高 end-to-end throughput。

實驗設定要用 LLaMA-30B，workload 是 Azure 的 coding 和 conversation。論文觀察到 coding 的 prompt 較長、輸出較短，conversation 則相反。比較對象的機器並不相同。HexGen 和 ThunderServe 在同一組異質雲端 GPU 上比，一共 32 張，包含 A6000、A5000、A40 和 3090 Ti。DistServe 是價格接近的同質環境，8 張 A100，不能說成同一套硬體。

實驗結果分兩層看。Table 3 是排程找出的部署：coding 用 8 個 prefill replicas 和 4 個 decode replicas，conversation 用 4 個 prefill 和 8 個 decode。這表示 replica 比例會跟著 input、output 的長短調整。Figure 9 再把 throughput 用 ThunderServe 正規化。相對 HexGen，coding 是 1.5 倍、conversation 是 1.3 倍；相對 DistServe，coding 是 1.5 倍、conversation 是 2.1 倍。圖上的 vLLM 也是 in-house，不要跟 HexGen 那組混在一起。

它證明的是，在異質資源限制下，workload-aware 的 phase placement 可以提升整體 throughput。沒有證明兩種 baseline 是在同一批 GPU 上被比較。

論文出處：Sec. 5.1–5.3，Figure 9，Table 3。正文寫的就是 HexGen 的 1.5／1.3 倍，以及 DistServe 的 1.5／2.1 倍。

## 第 05 頁｜Phase-Aware Deployment Improves Cost Efficiency

預計時間：45 秒。

三點收束。第一是作者方法：GPU grouping、phase designation、TP/PP 和 request routing 放在同一個 deployment plan。第二是論文整體的實驗結果，平均 1.7 倍、最高 2.1 倍的 throughput。這句在摘要，不要把它說成 Figure 9 的某一根 bar。第三是 Table 4 的時間。Full rescheduling 總共 157 秒，裡面是重新搜尋再加上重新載入模型；lightweight rescheduling 是 13 秒，而且 reload 是 0。兩者的差距包含有沒有付出模型載入，不只是搜尋本身變快。

報告者整理是，異質 GPU serving 的效益來自同時考慮 inference phase、硬體分配和通訊。ThunderServe 停在 phase 這個粒度；更細的 workload partitioning 是另一個方向，今天先接到這裡。

論文出處：摘要與 Sec. 6 的 1.7 倍／2.1 倍；Sec. 5.4 與 Table 4 的 157 秒和 13 秒。Table 4 的細項是 full 54(±5) 秒加 reload 103(±10) 秒，lightweight 13(±2) 秒加 reload 0 秒。
