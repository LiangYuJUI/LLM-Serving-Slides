# HBF 中文講稿

對應 `2026-10-28-HBF_Sucks.tex`，共 9 頁（8 頁主報告 + 1 頁來源整理）。目標約 9 分鐘；每頁時間含指圖與停頓，實際仍需口頭試講。正文可直接口述，來源與準備筆記不念。

來源：使用者需求中的 quantitative facts，以及補取的 [arXiv:2608.11668v4](https://arxiv.org/abs/2608.11668v4)，本地保存為 `Arxiv26_HBF_v4.pdf`。原有 `CharacterizingHBFforLLMServing/` 六圖與這版 paper 不一致，沒有混用；本 deck 使用 `CharacterizationOfHBFforKVCentricLLMServing/` 的 Figure 1、3、4、10、11、12，Table 8 以 native LaTeX 重建。以下頁碼指論文 PDF 檔案頁碼。

## 第 01 頁｜HBF Sucks?

這篇論文的核心結論是：更快的 flash，反而可能讓整個 LLM serving 系統變慢。今天介紹的是 Zhuoran Li 等人的 HBF Sucks，研究問題很直接：保留既有的 KV offloading runtime，只把 SSD 換成 HBF，能不能改善端到端效能？

作者做的是 full-stack characterization，從 serving latency 一路看到流量、溫度和壽命。接下來會用三個條件解釋這個看似矛盾的結果，最後回到 HBF 適合放什麼資料。

時間：35 秒。來源：首頁、摘要。

## 第 02 頁｜Why Replace SSD with HBF?

這頁要說明，為什麼把 SSD 換成 HBF 會是一個很自然的想法。LLM 的 KV cache 會隨著工作量成長，超過 GPU memory 能容納的範圍，所以 serving system 會把有機會再次使用的 KV 搬到容量更大的 backing tier，之後需要時再讀回來。

SSD 可以提供容量，但資料還原有 storage latency。HBF 則把 flash 放到 package-local 的位置，承諾更低的 latency 和更高的 bandwidth。因此，直覺會認為，只要 flash 更快，request 就應該更快。

但使用者等的是完整 request，不是單次 flash access。這篇 paper 要檢驗的就是右邊這個問題：裝置層的加速，到底能不能轉成端到端 serving 的加速？後面的實驗都圍繞這個問題。

時間：55 秒。來源：摘要、Introduction。

## 第 03 頁｜What Did the Paper Actually Evaluate?

這頁要說明，作者保留 SSD-style runtime，但換進來的 HBF-1 和 HBF-2，連近端記憶體配置也不同。上方保留 Mooncake-style 的 admission、retention、lookup，以及 KV save 和 restore，和容量匹配的 SSD 比較。評估用擴充的 TokenSim，重播四份兩小時 traces，涵蓋五個模型和 H100、B200 profiles，再加入 thermal 與 endurance model。

這兩種架構的 roadmap 來自 KAIST 的 Joungho Kim，在 2026 年 2 月的《HBF Technology, Workload Analysis and Roadmap》簡報中提出，是本文的 reference 11。不過要分清楚：架構方向與世代年份來自這份 roadmap；這篇 paper 實際使用的 stack 數、容量、頻寬和 service settings，則是論文作者依 roadmap 建立的模擬配置，不能全部當成廠商公布的產品規格。

下方 Figure 1 是兩者的 roadmap 架構，右側列出主要差別。HBF-1 把 interposer 上的 memory stack 位置都給 HBF，所以近端記憶體改用板上的 GDDR7。HBF-2 則把位置一半給 HBM、一半給 HBF，保留 interposer 上的 HBM3e。在同一 GPU profile 下，兩者近端容量相同，但記憶體技術和頻寬不同；HBF-1 的 flash 容量與頻寬則是 HBF-2 的兩倍。

所以這不是免費加上更快的 storage，而是用近端資源換取 flash。作者比較的是完整配置的代價，不只是 flash access 速度。這些是 roadmap 配置的模擬，不是量產 HBF 硬體實測。

時間：約 90 秒。來源：Section 2.2、Table 2、Table 3(c)、Section 6.1，以及 reference [11]：Joungho Kim, *HBF Technology, Workload Analysis and Roadmap*, TeraByte Interconnection and Package Laboratory, KAIST, 2026-02-10。此處來源歸屬依本文引用，未另行取得該 roadmap 原始簡報。表中 2× 比例限於本文同一 GPU profile 的 modeled configurations，不是所有 HBF 產品的固定規格；roadmap 不等於保證量產日期。

## 第 04 頁｜Three Conditions for HBF to Help

這頁把整篇研究整理成三個必須同時成立的條件。第一個是 critical path：從 secondary tier 讀資料，必須真的是 request 在等待的瓶頸，否則把這段再加速，總時間也不會少多少。

第二個是 reuse：每一份資料寫進 flash 都有成本，後續必須有足夠的有效讀取來回收這個成本。第三個是 sustainability：高頻寬要能持續維持，不能忽略短期的溫度限制和長期的寫入磨耗。

論文一共是六個 findings，每個條件對應兩個，不是只有三個 findings。接下來我各用一頁講最主要的證據，重點是為什麼原來的 transient KV offloading 同時踩到這三個問題。

時間：50 秒。來源：Sections 5–8。

## 第 05 頁｜Faster HBF Barely Improves E2E Latency

這頁要證明，flash-media latency 並不是整個 serving system 的主要瓶頸。上方是原文 Figure 4，呈現 HBF 與 SSD 的 matched-pair latency、media sensitivity，以及 queue behavior。比較 baseline 是容量匹配的 SSD：HBF-1 對 SSD24，HBF-2 對 SSD12。雖然 connector service 變快，但跨實驗的平均端到端 latency 仍是 SSD 的二到五點五倍。

最關鍵的是右下方整理的 sensitivity 結果。作者把 HBF 原始媒體 latency 加速三點七五倍，對照各自較慢的 media setting，平均 E2E 卻只改善百分之零點七五和零點八八，分別對應 HBF-1 和 HBF-2。依 paper 的模型反推，真正暴露在 critical path 上的 secondary-tier I/O 大約只有百分之一。這些 summary 數字來自正文，並不是要把上方圖所有柱子的統計口徑當成同一個平均值。

為什麼整體反而更慢？因為換進 HBF 的 package tradeoff 減少了 near-tier 的容量或頻寬，使能同時接納的 requests 減少，排隊變多。加速一個原本只占很小部分的 flash access，無法補回 admission 和 queueing 的損失。這就是 C1 失敗的原因。

時間：85 秒。來源：Figure 4、Section 6.1，PDF 第 7 頁。Figure 4 的 median matched-pair ratio 與正文的 mean E2E 範圍不同；不要互相替代。

## 第 06 頁｜All Production Traces Send More Writes Than Reads to HBF

這頁要證明，既有 hierarchy 送給 HBF 的其實是寫多讀少的 cold stream。上方是以 LaTeX 重建的原文 Table 8，比較每份完整 trace replay 的 flash-tier byte traffic。這裡的 baseline 是寫入與讀取位元組相等，也就是 ratio 等於一，不是另一台 SSD 的吞吐量。

表格第一列四個 write/read ratio，traceA 是二點一四，traceB 是四點九，coder 是一點一四，thinking 是二點二，全部都超過一。最重要的不是哪個 trace 最大，而是四份流量都沒有讓有效讀取抵銷寫入量。每個 block 寫入 HBF 都要付出 flash write 的代價，卻有許多 block 之後根本沒有讀回來。

原因是 hierarchy 本身把高重用的 hot KV 留在 HBM 或 GDDR，被淘汰到 HBF 的通常就是低重用的冷資料。因此，整體有 prefix reuse，也不代表那些 reuse 會變成 HBF read。這讓 C2 失敗：HBF 得到的正是對 flash 不利的 write-heavy、low-reuse traffic。

時間：65 秒。來源：Table 8、Section 7.1，PDF 第 9 頁。

## 第 07 頁｜Write-Heavy KV Traffic Makes Peak HBF Bandwidth Unsustainable

這頁要證明，寫入多不只浪費工作，也讓 HBF 的峰值頻寬難以持續。左邊完整 Figure 10 的上方 panel (a)，橫軸是單一 stack 的持續頻寬，縱軸是模型估計的最高溫度。這裡的比較門檻是紅色的八十度 thermal limit，不是 SSD 的溫度。

在這個 16-Hi TLC HBF model 中，約二百零二點二七 GB/s 就到達溫度上限。因此，介面標示的 peak bandwidth，不能直接當成這個 workload 能持續使用的頻寬。Figure 10 的中間 panel (b) 是完整 replay，下方 panel (c) 放大 throttling 時段，顯示頻寬受限且溫度維持在八十度附近。Thermal 講的是短期 throttling；右邊 Figure 11 的 endurance 則是長期寫入磨耗。

四份 trace 的寫入量換算為每天四十八到一百四十 TB。在 unchanged KV pooling 和論文的 endurance budget 假設下，HBF 的預估壽命約為容量匹配 SSD pool 的零點五六倍。這是模型壽命，不是硬體真的跑到損壞。結論是同一股 write-heavy traffic 造成兩次成本：當下限制持續頻寬，長期消耗 flash lifetime，所以 C3 也不成立。

時間：65 秒。來源：Figure 10(a–c)、Figure 11、Section 8，PDF 第 10–11 頁。

## 第 08 頁｜The Device Is Fine; the Drop-In Deployment Is Not

最後的結論是，這篇 paper 否定的是把 HBF 直接當成更快 SSD 的部署方式。左邊 Figure 12 是由 findings 整理出的概念性 placement map：橫軸是暴露出來的 secondary-tier stall，縱軸是 useful reads per write。它不是實測校準的數值邊界，而是提醒我們同時看 critical path 和 reuse。

右邊把選擇說得更直接。Private KV、transient decode KV 和低重用物件是差的目標；model weights、shared prefixes，以及 read-mostly 的 reusable objects 則更有機會合適。但也不能只靠物件名稱決定，仍要滿足前面的三個條件。

所以未來 runtime 需要 critical-path-aware、reuse-aware，還要控制 write budget 並考慮 thermal state。這些是研究提出的設計要求，不是作者已經完成的新 runtime。這篇最值得帶走的是：評估 HBF，要看整個系統把什麼流量送給它，以及為了得到它付出了哪些近端資源。

時間：60 秒。來源：Figure 12、Sections 9–10，PDF 第 12 頁。

## 第 09 頁｜Sources Behind the HBF Evaluation

這頁要釐清，本文的 HBF 結果是不同層級來源組合出的模型，不是實體 HBF 硬體 benchmark。左邊用開源 TokenSim 模擬 serving，並重播 Qwen-Bailian 的 production-derived traces；四份 traces 是 workload，不是四個模型。

中間區分三種依據：OCP v0.7.0 是 Sandisk 和 SK hynix 貢獻的業界 open specification，定義介面與管理規則；KAIST TERA Lab 的學術 roadmap 提供 HBF-1、HBF-2 架構方向，不是商品規格或量產保證；HAVEN 提供 NAND device modeling 的依據。

右邊用 3D-ICE 算溫度，八十度門檻由本文選定。SSD endurance baseline 參考 KIOXIA 的額定規格；HBF 壽命則由作者的 TLC budget 和 trace 寫入量推估，沒有真的把硬體寫壞。所以這是 full-stack modeled characterization。

時間：約 60 秒。來源：本地 HBF paper Sections 2、4，Refs. [1]、[9]、[11]、[13]、[23]、[24]、[26]。

### 第 09 頁完整來源（準備用，不口述）

- **[26] TokenSim**：Feiyang Wu et al., *TokenSim: Enabling Hardware and Software Exploration for Large Language Model Inference Systems*, 2025, arXiv:2503.08415。提供 request arrival、prefill/decode、continuous batching、admission、paged KV allocation、save/restore、tier transfers、queueing 與 E2E latency 的基礎。本文擴充 prefix lookup、SSD/HBF tiers、read/write counters、HBF profiles、connector waits 與 SLO metrics。[GitHub repository](https://github.com/pku-lemonade/TokenSim)；[HBF branch](https://github.com/pku-lemonade/TokenSim/tree/hbf)，2026-10-22 經 GitHub connector 確認可取得。它是學術開源 serving simulator，不是 HBF 官方 simulator。
- **[1] OCP technical specification**：Chinnakrishnan Ballapuram、Dongsop Lee, *High Bandwidth Flash (HBF) High-Level Base Die Specification*, **v0.7.0, August 3, 2026**。Open Compute Project；contributors 為 **Sandisk Corporation + SK hynix**。規範 host/device contract、interface、page-write/layout、reliability 和 lifecycle 管理。[官方 Storage contributions](https://www.opencompute.org/contributions/?project=Storage)。沿用本文引用版本，不以後續版本替換。不是學術論文或單一產品 datasheet。
- **[11] KAIST academic roadmap**：Joungho Kim, *HBF Technology, Workload Analysis and Roadmap*, TeraByte Interconnection and Package Laboratory（TERA Lab）, KAIST, **February 10, 2026**（名稱與日期依本文 bibliography）。[TERA Lab 官方下載入口](https://tera.kaist.ac.kr/)列有 HBF Workload and Roadmap。提供 GDDR–HBF／HBM–HBF organization 方向與世代；具體模擬 stack 數與 capacity/bandwidth profiles 由本文設定。**2028／2030 是 roadmap generations，不是保證量產日期。**
- **[9] HAVEN**：Po-Kai Hsu、Weihong Xu、Qunyou Liu、Tajana Rosing、Shimeng Yu, *HAVEN: High-Bandwidth Flash Augmented Vector Engine for Large-Scale Approximate Nearest-Neighbor Search Acceleration*, 2026。[arXiv:2603.01175](https://arxiv.org/abs/2603.01175)。本文 Section 2 明確指出其 modeled NAND arrays 提供 latency、energy、bandwidth 與 package power 依據；屬學術架構／模型研究，非 industry specification。
- **[23] 3D-ICE**：3D Interlayer Cooling Emulator，EPFL 相關開源 3D IC thermal tool。本文引用 Arvind Sridhar、Alessandro Vincenzi、Martino Ruggiero、Thomas Brunschwiler、David Atienza, *3D-ICE: Fast Compact Transient Thermal Modeling for 3D ICs with Inter-tier Liquid Cooling*, ICCAD 2010, pp. 463–470。[官方 GitHub](https://github.com/esl-epfl/3d-ice)。本文用它求解 16-Hi TLC HBF stack 的熱行為；**80°C 是本文選定的 safe junction temperature，throttling policy 也是本文模型的一部分**，不是 3D-ICE 的固定 HBF 規格。
- **[24] Production traces**：Jiahao Wang et al., *KVCache Cache in the Wild: Characterizing and Optimizing KVCache Cache at a Large Cloud Provider*, USENIX ATC 2025, pp. 465–480；作者來自 Shanghai Jiao Tong University 與 Alibaba Group。[USENIX 官方論文頁](https://www.usenix.org/conference/atc25/presentation/wang-jiahao)。HBF paper 的四份匿名化 Qwen-Bailian production-derived traces 是 traceA、traceB、coder、thinking，各完整重播兩小時；保留 request order/content、prompt/output lengths、sessions 和 KV reuse，負載掃描會縮放 arrival timestamps。
- **[13] SSD vendor data**：KIOXIA America, Inc., *KIOXIA SSDs for Supermicro Servers: Data Sheet*, **Version 1.0, 2024**。[官方 PDF](https://americas.kioxia.com/content/dam/kioxia/en-us/business/ssd/oem/supermicro/asset/KIOXIA_Supermicro_SSD_Data_Sheet_Global.pdf)。CM7-V 容量／頻寬／rated endurance 用於 SSD baseline 與 capacity-matched endurance comparison。壽命由 trace traffic 與 write budget 線性耗盡估算，不是 SSD 寫壞實測。HBF 的 favorable TLC endurance budget 與 unit write amplification 是本文 Section 4.4 的建模假設，不能歸給 KIOXIA。

---

### Preparation notes（不口述、不增加投影片）

六個 findings 的完整對應：

| 條件 | Finding | 內容 |
|---|---|---|
| C1 | F1 | HBF trades GPU near-tier capacity/bandwidth for flash. |
| C1 | F2 | Base-die attention compute cannot overcome limited HBF KV coverage. |
| C2 | F3 | SSD-style hierarchy sends HBF a write-heavy cold stream. |
| C2 | F4 | SSD-style write batching helps little on HBF. |
| C3 | F5 | Write-heavy traffic overheats HBF and causes throttling. |
| C3 | F6 | HBF wears out sooner under unchanged KV pooling. |

F2 和 F4 保留為準備知識，不增加 main slide 或延伸成我們的 proposal。架構替換比較同時包含 near-tier 與 backing-tier 改變；只有 media-latency sweep 用來隔離媒體延遲敏感度。不要把所有變差都歸因於 HBF NAND 本身。
