# Slides 4–5 繁體中文講稿

重排後：本檔的 GreenCache 是 slide 4（原 slide 7），Previous Work 是 slide 5（原 slide 8）。Notion 頁面尚未改頁碼。

Notion：https://app.notion.com/p/41bc9399c91881598c97dee6fb8231b7

每頁正文預計約 50–70 秒；「研究啟發」與「原始論文來源」為提問補充，不計入正文講述時間。

## Slide 4 — GreenCache: Adaptive Caching and Limitations

這一頁看 GreenCache 如何管理 SSD 上可重用的 KV Cache。保留更多 Cache 能減少 Prefill 重算，但也增加儲存資源的分攤製造碳排，所以最佳容量會隨負載與電網碳強度改變。

左側是我們整理的簡化流程。系統先量測不同容量與請求率下的延遲、功率，再結合當前負載、CI 預測與 SARIMA 負載預測，由 ILP 選出滿足 SLO 達成率目標、總碳排最低的 Cache 容量。Cache Manager 負責調整 SSD 空間，LCS 則優先淘汰碳節省價值較低的項目。

它已經納入運行與分攤製造碳排。這裡的限制是研究範圍：沒有跨資料中心路由，沒有 HBM/HBF 與 MoE Expert Weights 放置最佳化，實驗也以同型 L40 為主；這不表示作者證明了這些延伸無效。

### 研究啟發

我們可以借用「重用收益、資源成本與 SLO 一起評估」的方法，但 SSD KV Cache 不能直接等同 HBF Expert Storage。GreenCache 的 CI 預測使用 EnsembleCI，CarbonCast 提供訓練與真實 CI 資料；SARIMA 用於請求率預測。LCS 是 Least Carbon Savings，依重用 token、命中次數、大小與存留時間評分。其製造碳排分攤假設未使用資源會供其他工作負載使用，縮減 Cache 並不消除已發生的製造排放。原文第 7 節討論 MoE 的可能影響，但未實作 Expert Weights Placement。

### 原始論文來源

[GreenCache — Cache Your Prompt When It’s Green（arXiv v3）](https://arxiv.org/abs/2505.23970v3)：Secs. 2.3、3.2.1（碳模型）；5.1–5.5（框架、Profiler、SARIMA、ILP、LCS）；6.1（LMCache/vLLM、L40、ShareGPT/TriviaQA、Azure/CarbonCast）；7（分攤假設與討論）。左側四組流程是我們對六個元件的簡化整理，不是 Figure 10 的完整重製。

## Slide 5 — Previous Work: Reusable Methods and Research Inputs

這一頁整理前人研究能提供的方法，以及我們還需要補上的輸入。Carbon–SLO 提供跨資料中心模擬與排程方法，把 Continuous Batching、Queue、RTT 和延遲功率模型接起來，在 TTFT、TPOT 限制下做路由。GreenCache 則提供 KV 重用、Cache Profiling、負載預測，以及分攤製造碳排的方法。

但這些還不足以完成我們的 HBM/HBF 研究。我們需要建立不同 GPU 的延遲功率模型、記憶體存取與傳輸成本，取得多輪 KV 重用和 MoE Expert 存取軌跡，再結合區域 CI、PUE、RTT 與硬體壽命假設。

因此，我們提出先研究本地記憶體放置，再接上 SLO-aware 跨區路由，最後評估總碳排。過程中要分清實測 GPU 資料、HBM/HBF 模擬假設和 REEL 前瞻碳排估算；這是待驗證的整合計畫，還不能宣稱已有減碳成果或確認新穎性。

### 研究啟發

上表是方法與素材清單，不是所有程式碼或資料皆已公開的保證；每個 artifact 都要確認版本、授權與可重現性。GPU profiles 需要依我們的硬體重新量測或校準。GreenCache 的 GPU/CPU 功率有量測，SSD/DRAM 則使用規格中的典型功率，不能把所有 energy data 都視為實測。HBM/HBF 模型需明列容量、頻寬、延遲與每 bit 能耗假設；REEL 製造碳排則要做壽命、分攤方式與模型不確定性的敏感度分析。最後在相同 Workload、服務時間與 SLO 目標下，分別檢驗本地放置、跨區路由與兩者整合的貢獻。

### 原始論文來源

[Carbon–SLO（arXiv v1）](https://arxiv.org/abs/2610.14571v1)：Secs. III-B、III-C（延遲／功率與模擬器）；IV-C（Facility MILP）；V-A、V-B（設定與驗證）。

[GreenCache（arXiv v3）](https://arxiv.org/abs/2505.23970v3)：Secs. 2.3、3.2.1（分攤碳模型）；5.2–5.5（量測與最佳化）；6.1（實驗素材）；7（假設）。

[Characterizing High Bandwidth Flash for LLM Serving（arXiv v2）](https://arxiv.org/abs/2609.39131v2)：Sec. 3、Table 1、Sec. 5.1（記憶體與能耗模型）。

[REEL HBF Gen 1 Dataset](https://reellci.com/d/hbf-gen1-16hi/)：前瞻製造碳排估算、系統邊界與資料限制。研究整合與評估順序是我們的提案。
