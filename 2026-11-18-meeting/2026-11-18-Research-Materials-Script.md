# Research Materials & Supporting Evidence — 講稿

2026 年 11 月 18 日研究會議。主講 Yu-Jui Liang，指導教授 Hsiang-Yun Cheng。
更新：2026-11-17。建議主講約 12–14 分鐘；時間是排練目標，非實測。封面為 slide 1，所有 slide 編號與 PDF 頁碼一致，依序 1/16–16/16，最後一頁為 Thank you。詳細定位見 Power-Carbon-Slide-Evidence。

## 1 — 封面（20 秒）

這次把研究素材擴充成五個面向，回答跨資料中心、GPU 功率與 HBM/HBF 記憶體設計之間，有哪些可用證據。這是一份 evidence deck，裡面有真實 GPU 量測、模擬結果、製造碳排模型，以及我們的提案，不能混成已完成的節碳實驗。

## 2 — 證據地圖（30 秒；PDF 2）

五張橫向卡片可以直接跳到各節。先看 GPU 功率如何隨推論階段改變，再看 HBF 的存取與 placement 成本；接著看跨區排程與總碳排邊界，最後才討論 attention/expert 分工。每頁左下角都能回到這個索引。我們要把這些成本接起來，而不是從單一容量優勢推論整個系統一定省電。

## 3 — GPU 功率不是常數（60 秒；PDF 3）

左圖是 Carbon–SLO 原始 Figure 2。左半是 prefill，prompt 越長，功率逐漸接近飽和；右半是 decode，batch 變大時功率也變，但不是線性成長。圖中不同模型與 TP 的曲線不完全一致，所以不能直接拿 A100 的四百瓦 TDP 當所有步驟的功率。

每個 step 的能量是平均功率乘上時間。空閒也有成本，這個 testbed 約每張 A100 七十二瓦；host 三百瓦則是作者依 testbed 設定的節點基線。這些數字不能直接當所有 GPU 與伺服器的通用常數。原圖是每 GPU 功率，不是整台 TP engine 的總功率。

## 4 — HBF 存取能量的代價（60 秒；PDF 4）

這兩張表來自 Characterizing HBF 的 Table 1。讀取每 bit，HBM 是三點四 pJ，HBF 假設六點八；寫入則是三點四對一百。雖然假設的峰值讀頻寬相同，startup latency 差很多，寫頻寬也不同。這些是模型參數，HBF 的寫入還用了 SSD proxy，並不是量產 HBF 的實測結果。

本論文每 stack 容量用十進位 GB，HBM 二十四、HBF 三百七十五；不要把它和後面 REEL 的五百一十二 GiB stack 視為同一個硬體。下面公式提醒我們，還要知道讀寫流量才能換成焦耳，不能從 pJ/bit 直接跳到 J/token。

## 5 — 同硬體也會因 placement 改變能量（75 秒；PDF 5）

這頁選 GLM-5.2、十六張模擬 B200 compute GPU、同一個十萬 turn workload。最重要是兩個 H³ 列：每張 GPU 都是八個 HBM 加八個 HBF stack，只改 weights 放在哪一層。時間四千五百四十三秒對四千五百三十八秒，非常接近；模型能量卻由七點一九變九點五四 MJ，以七點一九為分母增加百分之三十二點七。

HBM-only 那一列只有八個 HBM stack，因此不能叫等硬體對照。Table 7 的分解則是在比較 H³、HBM weights 和 HBM-only，不是分解剛才兩個 H³ placement 的差：主要節省來自 weight read reuse，KV/index 讀取反而增加成本。

還有兩個限制。第一，模型沒有加 static/background power，所以不是整機電表能量。第二，HBM-only 到 H³/HBM 的平均 TPOT 從約二百十九升到二百七十九毫秒，完成整個 workload 較快不代表滿足互動式 SLO。

## 6 — 為什麼不能只選最低 CI（60 秒；PDF 6）

這是概念圖，沒有捏造量測數字。A 的 CI 比較低，但 queue 和 WAN RTT 可能更大；B 的 CI 較高，卻可能有不同的 GPU、記憶體成本和較短等待。排程需要看這個 request 在各地實際會花多少能量，以及能不能同時符合 TTFT 和 TPOT。

公式中 IT 能量用焦耳，除以三百六十萬換 kWh，再乘 PUE 與 CI 得到克二氧化碳當量。這裡 IT energy 不含機房 overhead；如果用的是 Carbon–SLO 原文已含 PUE 的能量，就不能再乘一次。WAN 能量若納入，也要清楚另訂邊界。

## 7 — 相關工作已經做了哪些（65 秒；PDF 7）

Carbon–SLO 和 FREESH 都已做跨資料中心的碳感知選擇。FREESH 還有異質 GPU、TP 配置與 MIAD frequency control，因此不能把 geo 加 heterogeneous GPU 加 DVFS 宣稱成我們的獨創。

表中的 partial 需要仔細解釋：FREESH 的 runtime 有 vLLM 與 least-laxity-first queue，不是沒有 queue。差別在它的 pool optimization 使用 profile 的 latency 與 service rate，而 Carbon–SLO 顯式推估 step、batch 與排隊狀態。FREESH 也有 runtime 的 TTFT、TBT 和 E2E threshold，不能只看 Carbon–SLO 的比較表就刪掉這些機制。

目前比較有價值的候選問題是：memory-specific energy 和 performance profile 會怎樣改變 geo scheduling？這仍需要更完整的文獻確認。

## 8 — 總碳排要有一致邊界（60 秒；PDF 8）

左邊是服務期間的 operational carbon，右邊是分攤到服務的 embodied carbon。GreenCache 用時間除以生命週期來攤製造負擔；我們再用 allocation share 表達共享硬體。這是 accounting scenario，釋放容量不會讓過去的製造排放消失。

比較時要固定同 workload、同 service window 和 SLO，而且同一份成本只能算一次。假設 NVML board power 已含 HBM，就不能再把整份 HBM power 加上去；GPU 碳足跡若已含記憶體，也不能再加完整 stack 製造排放。REEL 的 stack 邊界不含完整 package，這些仍需補齊。降低 serving energy 不等於降低 total carbon。

## 9 — HBM/HBF 製造碳排證據（40 秒）

目前找到的是 REEL LCI v1.0。它的價值在於，同一個半導體生命週期建模架構裡，同時列有 HBM3、HBM3E、HBM4 和 HBF，可以追查製造與組裝假設。但公開文件不等於完整原始 inventory，詳細數量仍需取得資料集。尤其 HBF 明確是前瞻性工程模型，沒有量產資料驗證。因此這份資料可以作為初步敏感度分析的起點，不能稱作廠商實測的產品碳足跡，也不能把它當成經同儕審查的 HBF 論文。

## 10 — 每個 stack 的碳排（45 秒）

先看每做出一個 stack 的製造負擔。官方 v1.0 文章中，HBM3 八層是十三點五二公斤，十二層是十九點八一公斤；HBM3E 十二層大約二十點六公斤。HBF 十六層則是兩百二十五點九公斤二氧化碳當量，大約是 HBM3 八層的十六點七倍。圖的縱軸從零開始，所以差距很明顯。但這不是等容量比較：三個 HBM 配置標為十六、二十四和三十六 GB，HBF 則標為五百一十二 GiB。另外，這些是文章公布值，我們尚未用目前詳細 inventory 重新算出同樣結果。

## 11 — 每單位容量的比較（50 秒）

如果問題改成「提供容量需要多少製造碳排」，排序就不同。我們把各自的碳排除以標示容量數字，得到零點八四五、零點八二五、約零點五七二，以及 HBF 的零點四四一。這樣算，HBF 比 HBM3 八層低約百分之四十七點八。原因是容量數字增加三十二倍，比 stack 碳排的增加幅度更大。但這裡有一個重要限制：官方 HBM 資料用 GB，HBF 用 GiB，文章圖片甚至和文字的標示不一致。因此這頁只能叫 nominal normalization，不能說已驗證每 GiB 降低百分之四十七點八。更不能由容量指標推論相同頻寬、延遲或 serving 效能。

## 12 — 可信度與限制（65 秒）

可信度要看假設是否透明，以及哪些假設還沒驗證。目前資料集用二百三十二層 NAND、六十五奈米周邊 CMOS 和二十八奈米 base logic 作代理製程，還包含 bonding、TSV 和測試。不過，它用封裝外框代理 die 面積，再估算良率；官方自己也指出面積和位元密度存在矛盾。因此主要的不確定性可能直接影響晶圓需求，不能只看資料品質分數就認為可信。

邊界也很重要：interposer、substrate 和整體 package assembly 不在這個 stack 資料集內，之後必須另外計入。方法報告在 PDF 第六十八頁、文件內第六十六頁，列有負百分之二十四、正百分之三十二的範圍。但我們還無法證明目前模型能重現文章的中心值，所以沒有把這個範圍畫成已驗證的碳排區間。這份資料適合做情境分析，還不足以做確定的硬體碳排宣稱。

## 13 — Attention/Expert 分工的機會與未知（65 秒；PDF 13）

圖上是 Our Proposed Design。attention worker 保留 active KV 在 HBM；expert worker 把 hot weights 放 HBM，cold weights 放 HBF，兩邊交換 activation 和 hidden state。這些傳輸是在資料中心內討論，不是假設每一層都穿越 WAN。

Janus 已有 attention/expert 分離與 expert scheduling；AFlex 做的是 attention/FFN 分工及 frequency scaling，不能把 A/FFN 和 MoE A/Expert 當完全相同。MemExplorer 則提供異質記憶體與 NPU 的設計空間方法，並不是我們架構的實測證據。

要驗證的成本包括 expert weights 讀取、GPU 等待、inter-GPU communication，以及 hot/cold placement 對 SLO 的影響。圖中的分工是可測試的假說，目前沒有我們自己的能量改善數字。

## 14 — 研究方向與下一步（65 秒；PDF 14）

我們把系統切成兩層。第一層根據 CI、PUE、資源、queue 和 WAN RTT，在 request 或 session 粒度選資料中心；第二層才在當地做異質 GPU、DVFS、attention/expert 和 HBM/HBF placement。這能把跨區 routing 和細粒度運算分工的通訊邊界分清楚。

RQ1 問 geo-aware power 和 carbon optimization；RQ2 問 memory placement；RQ3 問 total carbon 和 hardware co-design。下一步先校準能量與 component boundary，再做固定 workload 的 placement/routing ablation。最後一起看 J/token、功率、SLO goodput、TTFT/TPOT、operational 與 allocated embodied carbon，不能只挑一個有利指標。今天的證據支持我們提出問題，還沒有證明這個系統能減碳。

## 15 — REEL LCI 資料庫與盤查範圍（補充頁，約 60 秒；PDF 15）

這頁可以從 slide 9 的 About REEL / LCI 點進來，講完再返回。REEL 的全名是 Repository of Electronics Environmental Line-items，可以理解成電子產品環境盤查資料庫；LCI 則是 Life cycle inventory，生命週期盤查。

建立者 Jonathan Balsvik 是電子產業的 LCA 與產品碳足跡實務工作者。官網 v1.0 列出五百二十組資料集、十八個元件類別，涵蓋半導體、記憶體、封裝、PCB 與資料中心硬體。它利用公開論文、設備規格、專利及企業永續報告來建立工程製程模型。官網可以閱讀資料集說明，完整 inventory 數量則需經 Circa 授權取得。

它讓缺少晶圓廠專有數據的研究者，仍能建立可追查來源的製造碳排模型。但 LCI 是投入與產出資料，還不是碳足跡答案；仍要串接背景資料、套用影響評估方法，並檢查邊界與資料品質。頁面下方可以直接開啟官網。

## 16 — Thank you（10 秒；PDF 16）

謝謝老師，接下來想請教這三個研究問題的優先順序，以及哪些能量與碳排假設應該先驗證。

## Potential Professor Questions

### Q1. REEL LCI 的數據可信嗎？

可作為可追溯的模型起點，但應分層看待。公開的方法與 dataset 說明可以檢查來源、邊界及假設；HBF 沒有直接生產資料，且官方揭露幾何與材料缺口。DQI 是模型的資料品質評分，不是獨立驗證或誤差保證。目前我們確認的是官方公開數值與方法，尚未取得完整 inventory 並重現 GWP 計算。使用時要標記版本、做參數敏感度分析，並尋找獨立資料交叉驗證。[來源 C、D；完整連結見 SPEC]

### Q2. HBF 為什麼一個 stack 的碳排這麼高？

它包含多層 NAND、配對的 CMOS peripheral wafer、base logic，以及 bonding 與 TSV 等製程。晶圓需求會受 die 面積和良率影響，不能只把差距歸因於封裝。尤其目前以封裝外框代理 die 面積，而面積與 bit density 的矛盾尚未解決，可能改變估計，因此不能說兩百二十五點九就是量產產品必然的碳排。[來源 A、C、D]

### Q3. HBF 每單位容量碳排較低，是否代表更省碳？

不代表。這裡只是 nominal 容量比較，而且單位仍有歧義。總碳排要指定服務工作量、使用時間、硬體配置與相同 SLO，再合併製造分攤和用電碳排。若增加 GPU、延長執行時間，或出現 HBF stall，結果可能反轉。也不能把實際製造排放因為分攤給更多 token 就說成消失。這些是我們要驗證的系統問題。[研究評估原則，非 REEL 實驗結論]

### Q4. HBM 和 HBF 的容量單位是否完全一致？

尚未確認。HBM dataset 名稱和比較文章寫 GB，HBF 寫 GiB，HBF 文章的圖片卻把 HBM 標成 GiB。不能默認相等。本次只除以 16、24、36、512 這些數字，因此軸上寫 nominal capacity unit。若未來證實 HBM 的 GB 是十進位，必須乘以 10^9 / 2^30 轉為 GiB 再除；若證實只是二進位容量的慣用標法，才可直接以 GiB 比較。兩個假設應分開報告。[來源 A、B、E 與 HBM dataset 頁面]

### Q5. 是否已經可以用於 LLM Serving Simulator？

可以先當可切換的情境係數，作離線碳排後處理的候選輸入；不代表已完成整合或校準。要先決定 stack 數量、元件邊界、使用壽命與分攤方式，避免和整張 GPU 的製造碳排重複計算。還需要 serving 的時間、能量、電網碳強度及 SLO 結果；這份資料本身不能提供 HBF 功率或效能模型。這次交付只有證據簡報，沒有新增 simulator 實作。[研究假設與後續工作]

### Q6. 32.7% 是整機能量增幅嗎？

不是。分母是 H³/HBM weights 的 7.19 MJ，分子差為 9.54−7.19 MJ，來自相同 100k-turn 模擬。模型排除 static power，因此是該模型邊界內的相對差，不能直接當 wall-plug 增幅。Table 7 的 saving breakdown 又是另一個對照：H³/HBM 對 HBM-only。

### Q7. FREESH 是否已經把我們的方向做完？

Geo、異質 GPU 與 DVFS 確實有重疊。已檢視的 objective 和 controls 沒有 HBM/HBF placement 與 manufacturing carbon，但仍須擴大文獻審查與建立共同基線，不能只憑兩篇比較宣稱 novelty。
