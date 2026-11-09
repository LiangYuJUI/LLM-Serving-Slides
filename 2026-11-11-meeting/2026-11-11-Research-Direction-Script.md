# Research Direction 講稿｜2026 年 11 月 11 日

目標約 6 分 35 秒，問答另計。六頁依序約 45、65、100、45、75、65 秒。依講述速度可落在 6–8 分鐘；遇到表格不逐格朗讀。這是獨立提案，接在 GreenCache 報告之後，但不沿用其頁碼。

## 獨立封面（不編號，約 5 秒）

接下來我要報告的是 Power-Aware HBM/HBF Co-Design for Disaggregated MoE Serving，這是我目前提出的研究方向。

## Slide 1｜Proposed Research Direction（約 45 秒）

剛才 GreenCache 的回顧，讓我更注意到記憶體與儲存配置會影響服務成本，但這份提案的主要目標先放在能源效率，而不是直接宣稱減碳。我想研究的是，針對 MoE 的不同工作，能不能共同設計 GPU 的 HBM、HBF 配置，以及 Attention、Expert 的分工方式。

這裡有三個面向：硬體上允許不同 GPU 使用不同記憶體配置；服務端決定資料放哪裡、哪些 worker 負責哪些運算；最後在相同延遲要求和資源限制下比較 J/token、Token/J 與 goodput。指標現在列出名稱與單位：每個輸出 token 的能耗是 J/token，能源效率是 tokens/J，TTFT 是毫秒，TPOT 是毫秒每 token，goodput 是符合 SLO 的每秒輸出 token 數。另外加入每個輸出 token 的營運排碳量，單位是 gCO₂e/token，以用電量乘上對應電網碳強度估算，不包含硬體製造的隱含碳排。這是規劃中的評估指標，不代表已得到減碳結果。目前這只是研究方向，還沒有完成多 GPU 的整合，也沒有證明任何節能收益。整體研究目標是透過硬體共同設計與跨資料中心的協同服務調度，在滿足延遲與 SLO 的前提下降低功耗和營運碳排放；實作上先建立單一資料中心的可信模型，再擴展到跨資料中心。

## Slide 2｜Why Heterogeneous HBM/HBF GPUs?（約 65 秒）

我的出發點是，這幾種資料的存取行為不一樣。Active KV 在 decode 會反覆讀取，也會隨新 token 增量更新，所以我把 HBM 當作自然的基準配置。Expert weights 大致是唯讀，但熱門和冷門 expert 的重用程度可能差很多。熱門權重可能值得留在 HBM，冷門權重則可能利用 HBF 的容量增加常駐數，減少其他層級的載入或遠端存取。

不過，容量增加不等於省電。權重即使只在部署時寫入，推論時仍可能反覆從 HBF 讀取。慢速讀取會讓 GPU 等待，等待期間也有功耗。另外，分離 worker 之後，中間 activation 要經過網路，不能把這個成本當成零。因此我真正要問的是，依角色配置記憶體，在哪些 workload 和網路條件下才有能源效益，而不是預設 HBF 一定比較好。

## Slide 3｜Proposed Attention/Expert Architecture（約 100 秒）

這張圖是目前想驗證的架構假說。左邊 Attention workers 負責 attention、相關的非 expert 運算，以及各層 active KV 的管理；候選配置是比較多 HBM。右邊 Expert workers 負責 MoE 的 expert FFN，讓較冷的權重常駐 HBF，熱門權重則使用 HBM 快取。右邊仍然需要 HBM 存放暫存資料和運算 buffer，並不是只有 HBF。

兩邊箭頭表示真正要傳的資料。Attention 到 Expert 是 hidden states，或者經過 routing 分派的 token activations；Expert 回傳的是 expert outputs 或合併後的 hidden states。不是每一層都把整份歷史 KV cache 和所有 expert weights 來回搬動。每層 KV 的所有權留在對應的 Attention 路徑，權重則盡可能常駐在 Expert 端。

但資料常駐不代表通訊消失。每一層仍有 activation dispatch、combine 和同步依賴，也可能遇到 HBF read stalls。不同請求或 microbatch 可以有重疊，但同一 token 的因果依賴不能任意跳過。這也是為什麼我要同時比較 monolithic、同質 A/E、正向與反向非對稱配置。A/E 分離已有 Janus 和 MegaScale-Infer 等前作；我們要測的是記憶體配置與完整成本模型會不會改變最佳解，而不是把分離本身說成新發明。

## Slide 4｜Simulation Frameworks（約 45 秒）

這一頁先整理三個模擬框架的角色。HBFSim 負責 HBM、HBF 的記憶體交易，以及 NAND、controller、FTL 的時序，也包含熱與壽命行為。

ServeLoop 是單裝置 serving 的前端，處理請求執行、資料放置，以及 KV 和權重的常駐管理。目前已經用它在 Oak 做初步實驗。

LLMServingSim 2.0 則提供多 GPU 和異質硬體的 serving 模型，包含 GPU profiles、網路，以及功率和能源估計。我把它列為後續系統層研究的候選框架。這三個工具各自對應記憶體、單裝置 serving，以及多 GPU 系統層的需求。

## Slide 5｜Research Questions and Next Steps（約 75 秒）

接下來我想回答三個問題。第一，正向的 HBM-rich Attention、HBF-rich Expert，在相同 SLO 下，能源效率是否真的贏過同質或不拆分的配置？第二，HBF 讀取等待、GPU 閒置耗能和通訊成本，什麼時候會抵銷容量的收益？第三，在可比較的容量、封裝、成本和功率限制下，哪個配置有最好的能源與 goodput 取捨？

我會把 monolithic All-HBM、monolithic hybrid、同質 A/E、正向、反向，以及依 workload 搜尋的配置一起比較。除了 J/token，也要看 P95 TTFT、TPOT、符合 SLO 的 goodput，以及等待和網路的成本，避免只看平均速度。公平性會分別交代固定了哪些資源，不會把相同 stack 數當成所有成本都相同。

下週十一月十八日，我會另外報告 MemExplorer。它已經研究異質 compute、HBM/HBF 記憶體與能源效能取捨，也包含 Attention/FFN 分工。因此要先看清楚它做了什麼、模型省略了什麼，才能決定我們真正能增加的貢獻。下週是另一份獨立報告，今天先不展開精讀。

## Slide 6｜Related Work Comparison Matrix（約 65 秒）

最後這張是依教授要求，將已整理的論文放在相同比較軸上。完整矩陣仍在 Notion，這裡挑十三項代表工作。我想強調三個群組：Helix、ThunderServe、Hetis、Tessera 涵蓋不同粒度的配置與運算分工；Janus 和 How Far 已經直接研究 Attention、Expert 或 FFN 的分離；記憶體相關的 MemExplorer、Characterizing HBF 與 Potential Applications，則已涵蓋異質記憶體、多 GPU 或 expert 常駐，這些都不是空白領域。

跨資料中心這欄，我只把有地理分散或 WAN 路由的研究標成有。多 GPU、多節點和不同地區碳強度 trace 都不自動算跨資料中心，所以 GreenCache 這裡標成沒有。Not shown 代表目前來源沒有建立該範圍的證據，不是斷言技術上做不到。NV 是仍需確認獨立模擬器形式。星號則表示評估指標，不一定是最佳化目標。這張表讓我們確定研究差異必須落在可驗證的聯合成本與配置比較，不能只靠組合既有名詞宣稱新穎性。

## 教授可能提問（不計入主講時間）

### 1. 已經有人做 A/E separation 了嗎？

有。Janus 明確分開 attention 與 expert GPU pools，MegaScale-Infer 也研究 Attention/FFN 分離。How Far 評估分離的設計空間。我們不能把分離本身當成新貢獻，必須比較加入 HBF 時序、能源和角色配置後，是否得到不同且有價值的結論。

### 2. 異質 HBM/HBF co-design 已經被研究了嗎？

有，MemExplorer 是直接相關前作。Characterizing HBF 已做多 GPU 與 expert weights placement，Potential Applications 也有 expert 常駐與複製。我們的差異仍待逐項確認，不能先宣稱「第一個」。

### 3. HBF 讀取較慢，為什麼還可能省電？

只是可能，不是結論。更多常駐容量可能減少載入、遠端 dispatch 或所需裝置數，但讀取耗能和較長等待可能完全抵銷收益。要積分整段執行的功耗，包含閒置、記憶體及網路，並固定工作量和 SLO；目前沒有正向節能證據。

### 4. Inter-GPU communication 怎麼建模？

從實際 activation shape、token 數、precision、top-k routing 和分片方式算 bytes，分別記錄 dispatch、combine 與 collective。使用拓樸、頻寬、啟動延遲與壅塞模型，放入 A/E dependency graph，再檢查 microbatch overlap 和同步。不能用固定零成本，也不能把單 token 的相依性任意重疊。

### 5. HBFSim 和 LLMServingSim 如何整合？

預計由系統層管理請求、A/E DAG 和網路事件，記憶體子模型回傳指定 transaction 的完成事件與相應能源。先定義 transaction 與 kernel 的責任邊界，從同質 All-HBM 驗證，再加入 hot cache、HBF residency 和非對稱配置；目前還沒完成這個介面。

### 6. 如何避免 memory timing double counting？

先追蹤 profile 的 time_us 包含哪些 stall，以及 power 是 compute-only 還是 board-level。若可取得可靠拆分，就以一致的 compute 和 memory 依賴重新建模；若只能校準差額，必須驗證差額方法和重疊假設，不能直接減去或加上整段 memory makespan。HBM 回歸、零 HBF 流量和能源分帳都要成立。

### 7. Phase 1 包含跨資料中心嗎？

不包含。先做單一資料中心內的多 GPU 能源與延遲比較。Geo-carbon 是可能的第二階段，才增加 request/session routing、WAN、碳強度和 KV 重算成本，不預設每一層 A/E 都跨 WAN。

### 8. MemExplorer 到底已經涵蓋什麼？

已核對的 v2 原文 Table I 和 Section V-E 包含異質記憶體、compute/memory co-design、P/D 與 A/FFN 分工。Figure 8 的特定 decode 情境甚至偏好讓 Attention 使用 HBF 或 LPDDR，提醒我們正向配置不是定律。完整限制、通訊與 HBF 行為的處理還要在下週精讀確認；不能直接把它說成只做單裝置容量分析。

## 來源與閱讀界線

主要依據為 [Notion 研究紀錄](https://app.notion.com/p/412c9399c91881fa90a4c56a96ce42d6)，版本時間 2026-11-09 04:38:25 UTC。實驗數字為其中 §§4.2–4.3 的記載，不是此次重跑。另核對 [Janus 摘要](https://arxiv.org/abs/2512.13525) 與 [MemExplorer v2](https://arxiv.org/html/2604.16007v2) 的 Table I、§V-E / Fig. 8。其餘矩陣分類以 §5.3 為準，並保留未確認標記。
