# 10 分鐘 Paper Review 中文講稿

對應 `2026-10-28-10min-Review.tex`。正式報告仍是 12 頁：第 01 頁封面，第 02 頁時間軸，第 03–11 頁是 10 分鐘內容，合計 600 秒，第 12 頁 Thank you。這 12 頁的頁腳維持 `n/12`。第 13 頁起是 Q&A backup，不計入口述時間；關鍵字可點進 10/21 的詳細頁，再從頁尾回到這份報告。

ThunderServe 事實只依 `2026-10-21-meeting/MLSys25_Thunderserve.pdf`。Hetis 事實只依 `2026-10-21-meeting/SC25_Hetis.pdf`。

## 第 01 頁｜Title

預計時間：約 15 秒。不計入後面九頁的 10 分鐘。

這份是獨立的十分鐘 paper review，只談 ThunderServe 和 Hetis。ThunderServe 四分鐘，Hetis 四分鐘，最後兩分鐘比較它們切分 GPU 的粒度。頁碼是這份簡報自己的頁碼。

來源：報告者整理的範圍。ThunderServe 為 MLSys 2025；Hetis 為 SC 2025。

## 第 02 頁｜Presentation Roadmap

預計時間：約 30 秒。不計入後面九頁的 10 分鐘。

今天正式報告是三十分鐘，分成三段，每段十分鐘。第一段是 ThunderServe 和 Hetis，回顧上週的重點並做比較，就是這份簡報。第二段是 Helix，第三段是 Tessera，兩篇都是新論文的精簡報告。另外準備了十分鐘的兩篇 HBF，那是備用內容，不佔這三十分鐘。

來源：報告者整理的會議時間，不是論文結論。

## 第 03 頁｜ThunderServe: Why Heterogeneous GPU Serving Needs Phase-Aware Scheduling

預計時間：50 秒。

論文觀察是，prefill 比較吃算力，decode 比較吃記憶體頻寬。以 A40 和 3090 Ti 為例，A40 的算力較強，在 prefill 比較有優勢；3090 Ti 的記憶體頻寬較高，在 decode 比較有優勢。Figure 1 的例子也顯示，以單筆 request 的成本來看，prefill 用 A40 比較便宜，decode 用 3090 Ti 比較便宜。所以兩個 phase 適合的 GPU 可能不同。

不過雲端能用的 GPU 種類和數量都有限，網路也不快，而且每對 GPU 之間的頻寬不一樣。Prefill 和 decode 分開之後，KV cache 還要從 prefill group 傳到 decode group，所以不能只看算力或頻寬來分 GPU。真正要一起決定的是：GPU 怎麼分、phase 放在哪，以及這段傳輸怎麼走。

論文出處：Sec. 1，Figure 1，Table 1。Figure 1 是單筆 request 的價格，不是整個 cluster 的 throughput。

## 第 04 頁｜Joint Optimization of GPU Placement, Parallelism, and Routing

預計時間：65 秒。

作者方法是把 GPU Placement 收成兩層，Figure 3 就是這個流程。上層用 Tabu Search，先把 heterogeneous GPU 組成 group，再指定這組做 prefill 還是 decode。下層接著決定每組的 TP 和 PP，以及 prefill group 和 decode group 之間 request 怎麼送。這個 routing 要看網路，因為 KV cache 得傳得過去。

兩層是一起評估同一個 deployment plan：下層算出這個分組和 phase 的表現，再交回上層繼續搜。不是先隨便分完組，才事後補平行設定。另外兩個機制這裡只點名，KV cache compression 用來縮小傳輸量，lightweight rescheduling 用來在負載或可用 GPU 改變時調整 phase 和 routing。這頁不講 Tabu Search 的 neighbor operators，也不寫線性規劃。

論文出處：Sec. 3.2–3.4，Figure 3。壓縮和 lightweight rescheduling 是作者的機制，效果留到後面的實驗頁，不在這張流程圖裡。

## 第 05 頁｜Does Phase-Aware Scheduling Improve Serving Efficiency?

預計時間：80 秒。

接著看實驗：依照 workload 調整 prefill 和 decode 的部署，能不能提高整體吞吐量？作者使用 LLaMA-30B，測試 Azure 的 coding 和 conversation 兩種 workload。Coding 的 prompt 較長、輸出較短，conversation 則相反，因此兩者對 prefill 和 decode 的資源需求也不同。

ThunderServe 和 HexGen 使用同一組 32 張異質雲端 GPU，包含 A6000、A5000、A40 和 3090 Ti。另一個比較對象 DistServe，則使用價格接近的 8 張 A100；圖中的 vLLM 也部署在 in-house 環境。因此，這裡同時包含相同異質硬體上的方法比較，以及相近成本下不同硬體配置的比較。

Table 3 顯示，排程找出的部署會隨 workload 改變。Coding 配置了 8 個 prefill replicas 和 4 個 decode replicas；conversation 則是 4 個 prefill 和 8 個 decode。也就是說，prompt 較長時，多分配資源給 prefill；輸出較長時，則增加 decode 的 replicas。

Figure 9 以 ThunderServe 的吞吐量作為正規化基準。相對 HexGen，ThunderServe 在 coding 和 conversation 分別達到 1.5 倍和 1.3 倍吞吐量；相對 DistServe，則分別是 1.5 倍和 2.1 倍。這些結果支持了它的設計方向：根據 workload 的需求調整 phase placement，能更有效地利用異質 GPU，提高 end-to-end throughput。

論文出處：Sec. 5.1–5.3，Figure 9，Table 3。

## 第 06 頁｜Phase-Aware Deployment Improves Cost Efficiency

預計時間：45 秒。

ThunderServe 的核心，是把 GPU grouping、prefill 和 decode 的角色分配、TP/PP，以及 request routing 放進同一個 deployment plan，一起考慮計算與通訊成本。論文摘要將整體實驗結果總結為平均 1.7 倍、最高 2.1 倍的吞吐量提升。

這篇的重點是，異質 GPU 的效益需要透過 phase 分工、硬體分配和通訊規劃一起發揮。接下來的 Hetis 則把工作切得更細，進一步看不同 module 和 attention heads 如何分配到 GPU 上。

論文出處：摘要與 Sec. 6 的 1.7 倍／2.1 倍。

## 第 07 頁｜Hetis: Why Static Parallelism Wastes GPU Resources

預計時間：45 秒。

接下來看 Hetis。它觀察到，同一張 GPU 在不同 module 上的表現差距並不一樣，因此，用同一套 model parallelism 分配所有工作，可能無法充分利用異質 GPU。

Figure 2 比較 Llama-70B 單層 decode 的 MLP 和 Attention 執行時間，sequence length 設為 1000。在 MLP 上，P100 和 A100 的執行時間差距很大，論文報告最高約 40.4 倍；但在 Attention 上，差距就小得多。這表示，對 dense computation 幫助有限的 GPU，仍可能適合分擔 attention 工作。

固定切分也會造成 KV cache 空間使用不平均。Figure 1 的例子中，3090 的 cache 已經用完，A100 卻還有空間。因此 Hetis 希望依照 module 的特性分配工作，再動態調整 attention 的切分，同時改善計算和記憶體的利用率。

論文出處：Sec. 2.2–2.4，Figure 1–2。

## 第 08 頁｜Hetis: Selective Primary Workers and Dynamic Head-wise Attention

預計時間：90 秒。

Hetis 把 GPU 分成 Primary 和 Attention worker 兩種角色。Parallelizer 根據 dense computation 和通訊成本，搜尋適合擔任 Primary 的 GPU。Primary 透過 TP、PP，必要時搭配 DP，承載模型參數，負責 prefill、decode 的 dense modules，以及留在本地的 attention heads。

對 dense 計算幫助較小的 GPU，則可以擔任 Attention worker，負責部分 decode attention 和對應的 KV cache，不需要再存一份完整模型權重。搜尋時，預設以 Δ = 0.05 為門檻：如果移除某張 GPU 後，dense cost 增加不超過 5%，就可以考慮把它移出 Primary 集合。因此，角色分配取決於整體執行成本。

Decode 時，Primary 先計算 QKV projection，再把分配給遠端 heads 的當前 token Q、K、V 傳給 Attention worker。Worker 搭配本地保存的歷史 KV cache 計算 attention，將結果傳回 Primary，接著完成 output projection 和 MLP。這個過程會在不同 layers 重複，歷史 KV cache 則留在 worker 上，避免每一步都重新傳送。其餘 heads 由 Primary 本地計算；對 GQA，分配時也會維持 query heads 與對應 KV head 的群組關係。

Figure 3 呈現了這套分工背後的四個組件。Profiler 提供計算和通訊成本預測，Parallelizer 決定 worker 角色與 TP/PP 配置，Dispatcher 在線上分配 attention heads，Hauler 則負責 head 等級的 KV cache 管理與搬移，讓 head 分配能隨執行狀況調整。

論文出處：Sec. 3–5，Figure 3。Δ = 0.05 在 Sec. 4.1；GQA 群組關係在 Sec. 5.1。

## 第 09 頁｜Hetis: Does Head-wise Parallelism Improve Serving Performance?

預計時間：65 秒。

接著看這樣的分工，能不能提高服務容量。作者使用四台主機，共有 4 張 A100-80GB、4 張 3090 和 4 張 P100，主機間以 100 Gbps 連接。實驗涵蓋 Llama-13B、OPT-30B 和 Llama-70B，使用 ShareGPT、HumanEval 和 LongBench，比較對象是 Splitwise 和 Hexgen。

Figure 10 顯示 Llama-70B 在不同 request rate 下的 normalized end-to-end latency，縱軸單位是 s/token。隨著 request rate 增加，可以觀察各方法的延遲如何上升，以及系統能承受多少請求。在論文測試的設定中，Hetis 的吞吐量相對 Splitwise 最高達到 2.25 倍，相對 Hexgen 最高達到 1.33 倍。在這組 Llama-70B 部署裡，搜尋選出 A100 和 3090 作為 Primary，P100 則擔任 Attention worker。

Figure 11 進一步顯示，Hetis 的最大可用 KV cache 相對測試過的 baselines，最高達到約 1.87 倍。作者也在 module 層級的分析中，報告 decode attention 最高 1.49 倍的加速。這些結果顯示，細分 attention 工作除了改善計算分配，也能利用原本閒置的 KV cache 空間，讓系統承接更多請求。

論文出處：Sec. 7.1–7.3，Figure 8–13。吞吐量最高改善見 Sec. 7.2；KV cache 容量見 Figure 11；decode attention 加速見 Sec. 7.3。

## 第 10 頁｜Hetis: Main Contributions and Takeaways

預計時間：40 秒。

Hetis 的核心，是根據不同 module 的執行成本分配 GPU 角色，讓 Primary 負責 dense computation，再把部分 decode attention heads 分配給其他 workers。搭配線上的 head dispatch 和 head 等級的 KV cache migration，系統就能動態調整計算與記憶體負載。

作者把 Hetis 實作成 vLLM 的擴充，加入 head-level KV cache 管理、cache 讀寫的 CUDA kernels，以及 NCCL peer-to-peer 通訊，並沿用 PagedAttention。主要的 end-to-end serving 結果來自真實 GPU cluster；另外再透過大規模模擬，評估 Parallelizer 的搜尋成本。

因此，這篇展示的是：除了依 prefill 和 decode 分工，還可以進一步依 module 和 attention head 的需求，發揮不同 GPU 的能力。

論文出處：Sec. 6、7.1–7.2、7.4、9。投影片中的連結指向底層框架 [vLLM](https://github.com/vllm-project/vllm)。

## 第 11 頁｜ThunderServe vs. Hetis: Different Granularities of GPU Specialization

預計時間：120 秒。

把這兩篇放在一起看，它們都希望讓不同 GPU 承擔適合自己的工作，但切分的單位不同。ThunderServe 從 prefill 和 decode 的需求差異出發，在部署層一起決定 GPU grouping、phase designation、TP/PP 和 request routing。它的重點是，整個 cluster 應該分配多少資源給各個 phase，以及 requests 如何在這些資源之間流動。

Hetis 則進一步觀察同一個 phase 裡的 module 差異。Dense computation 和 decode attention 對 GPU 的需求不同，因此它讓 Primary workers 承載模型參數並處理 dense modules，再把部分 attention heads 交給 Attention workers。這些 workers 保存自己負責的 KV cache，專門處理被分配到的 attention 工作。

切分方式也決定了通訊的內容。ThunderServe 在 prefill 和 decode replicas 之間搬移 KV cache，讓 decode 接續處理 prompt。Hetis 則在 decode 的每一層，為 offload 的 heads 傳送當前 token 的 Q、K、V，再收回 attention output；歷史 KV cache 平常留在 worker 上，當 head 分配改變時，再進行對應的 cache migration。

兩者調整資源的方式也不同。ThunderServe 的 lightweight rescheduling 調整 phase 和 routing；Hetis 的 online head dispatching 則調整 heads 的分配。前者處理 phase 層級的資源需求，後者處理 module 和 head 層級的計算與記憶體負載。

由於兩篇實驗使用的硬體、workload 和 baselines 不同，各自報告的最高吞吐量改善倍數，無法直接作為彼此的效能排名。更值得比較的是它們的設計選擇：ThunderServe 最佳化 phase-level deployment，Hetis 則透過 module-aware 的執行與 head-level attention placement，利用更細的工作分工來改善異質 GPU 的使用效率。

論文出處：跨論文比較依據 ThunderServe Sec. 3、Table 3，以及 Hetis Sec. 3–5、7。比較表與上方概念流程為本報告整理。

## 第 12 頁｜Thank you

預計時間：約 10 秒。不計入 10 分鐘。

以上是 ThunderServe 和 Hetis 的回顧。從 phase 到 module 和 attention head，兩篇展示了利用異質 GPU 的不同分工方式。謝謝大家。
