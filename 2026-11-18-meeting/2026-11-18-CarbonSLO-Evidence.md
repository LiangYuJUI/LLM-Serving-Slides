# Evidence notes — Carbon–SLO, 18 Nov 2026

來源是本機 PDF：`CarbonSLO-GeoDistributed-LLM-Serving-2026.pdf`，13 頁，arXiv:2610.14571v1，10 Oct 2026。作者公開的 simulator 是 <https://github.com/topcuburak/carbon-slo-at-geoscale>。這份簡報**沒有重跑**該程式。下面的數字都從 PDF 讀出。若之後程式與 PDF 不一致，先不要把程式說明改寫成論文結論。

單位沿用論文的 gCO₂/kWh，不是 GreenCache 的 gCO₂e。這篇的目標是 operational carbon（Scope 2），沒有把 embodied carbon 放進目標函數。

## 主張與範圍

| 主張 | 條件 | 出處 | 不要說成 |
|---|---|---|---|
| Inference 在模型生命週期的碳排可超過 training 的 25 倍 | 論文引用既有研究，不是他們自己量到的 | Sec. I, refs. [16], [17] | 這篇的實驗結果 |
| CI 跨地區、跨時間可差一個數量級以上 | 動機，不是某一張結果圖的座標 | Sec. I | 16 個 DC 的實測極差 |
| 電源中位數：nuclear/solar < 50，天然氣 490，煤 820 gCO₂/kWh | IPCC 引用 | Sec. II | 實驗裡每個 DC 的 CI |
| Operational carbon = energy × CI，DC 功率再乘 PUE | Scope 2 | Sec. II, Sec. III-A | embodied carbon，或 SSD 攤提 |
| SLO violation = 沒過 TTFT **或** 沒過 TPOT 的 request 比例 | 兩個 budget 是分開的 | Sec. V-A | 一個聯合機率，或只有 TTFT |
| 主要 budget：TTFT 3 s、TPOT 100 ms；Mixtral TPOT 200 ms | MLPerf 單機 TTFT 是 2 s，他們只放寬 TTFT | Table II, Sec. V-A | 所有實驗都是 2 s |
| Long / mixed prompt 的 TTFT budget 是 4.5 s | Fig. 7(b) | Sec. V-C | 主要實驗也用 4.5 s |
| Prefill MAPE ≤ 1.7%（Llama、Qwen，兩種 TP），Mixtral prefill 4.8%；decode ≤ 3.4%；step energy ≤ 5.6% | vLLM 0.6.3，FP16，A100，32–32K tokens | Sec. III-B, Fig. 1–2 | end-to-end serving error |
| Idle 約 72 W/A100；host 300 W，其中 CPU package 約 146 W | 他們的 testbed | Sec. III-B | 所有伺服器的 idle |
| Within-node：19 個 arrival rate、超過 40K requests | 3 個 Llama-3.1-8B engine，TP=1，A100-40GB，CNN-DailyMail，RR，2–50 req/s | Sec. V-B | 16 個真實 DC 已驗證 |
| TPOT 平均誤差 < 5%（15.5–54 ms） | 同上 | Sec. V-B | 每個 request 都 < 5% |
| TTFT 整體平均誤差 9.1% | 低於飽和 3.5%，overload 5.2%，飽和附近 28.5% 且偏高估 | Sec. V-B | 全程都是 9.1% |
| GPU energy 與量測相差在 2.5% 以內 | 所有 arrival rate | Sec. V-B | 含 host 的總碳都在 2.5% |
| 單 engine 對上三 engine，同 per-engine load，TPOT 只差 3.3% | 用來支持 engine 可獨立建模 | Sec. V-B | Mixtral 也做了同樣的對照 |
| 飽和容量 27.58 req/s；掃描覆蓋 7%–181% | 這三個 engine | Sec. V-B | geo 實驗的 1200 req/s |
| Mixtral TP=4 已經塞滿四張 GPU 的 node，所以沒有多 engine 的 end-to-end 對照 | Sec. VI 的限制 | Sec. VI | Mixtral 的 geo 結果已被硬體驗證 |
| Facility MILP：相對 RR **up to 60%**，average SLO violation **3%** | Abstract 與 Conclusion 的摘要。60% 是上界，3% 是平均 | Abstract; Sec. VIII | 每個 marker 都是 60% 且只違規 3% |
| 低負載（Fig. 4 沒畫）facility MILP 減碳 53.8–59.6% | 除 greedy α=0 與 Green-LLM 外，carbon-aware 的 SLO violation 在 1.3% 以內 | Sec. V-C | 這就是圖上的 moderate-load 點 |
| 最激進的 greedy，在相近減碳下，SLO violation **up to 55%** | Abstract 的 “most carbon-aggressive greedy setting” | Abstract; Fig. 4 高負載軸到 55 | 所有 α 的 greedy，或 moderate load |
| Moderate load，greedy α=0：dense 最高約 6.9%，Mixtral 44.8% | 等同 MOER | Sec. V-C | 55% 就是這個設定 |
| Moderate load，ILP / facility MILP / greedy α=0.5：dense 上最高約 54% 減碳，violation 在 1.9% 以內 | 三個模型裡的 dense | Sec. V-C | Mixtral 也在 1.9% 內 |
| Mixtral、moderate load：facility MILP 比上述政策再多最多 8.6 個百分點，violation 1.3% | 百分點，不是 8.6% 的相對比例 | Sec. V-C | 所有模型都多 8.6 點 |
| Greedy α=0.9：最多約 3% 減碳，violation 可忽略；高負載的 dense 甚至比 RR 更耗碳 | Fig. 4(b) 標了 −5% | Sec. V-C, Fig. 4(b) | α=0.9 也有 60% |
| 高負載減碳空間收到 32–38% | 綠 DC 飽和 | Sec. V-C | 高負載仍有 60% |
| Standard ILP 與 facility MILP：dense 最高 32.8%，Mixtral 35.0%，violation 最高 12.5% 與 2.4%，respectively | 語序最自然的讀法是對上 dense 與 Mixtral。論文沒有把 12.5 單獨指派給某一個 solver | Sec. V-C | 自行指定 12.5% 只屬於 ILP |
| Fig. 4(b) 標籤：facility MILP 高負載減碳 Llama 26%、Qwen 33%、Mixtral 35% | 標籤是相對 RR 的減碳，不是 TTFT | Fig. 4(b) | 和下面 29.2% 當成同一個數 |
| 高負載 TTFT：dense 上 greedy 的 p99 在 3 s 內，但 α=0 是靠 TPOT 違規 | p99 TTFT 與 SLO violation rate 是兩件事 | Sec. V-C, Fig. 4(b) | greedy 的 tail 一定爆掉 |
| Iterative ILP 的 p99 TTFT 到 7.5 s；Mixtral 上激進 greedy 與 Green-LLM 的 p99 到 8.8 s | 高負載 | Sec. V-C | 這就是 SLO violation 55% |
| Mixtral greedy α=0：median TTFT 3.3 s，平均 queue 2.9 s；ILP/MILP median 在 0.7 s 內、queue 約 0.2 s、p99 在 2.2 s 內 | TP=4，engine 數是 dense TP=1 的四分之一；mean OSL 211 對 Llama 的 71 | Sec. V-C | 三個模型的 tail 形狀一樣 |
| 真實 PUE 1.08–1.32。Facility MILP：Llama 29.2%→30.5%，Mixtral 36.6%→38.7% | 高負載。SLO 幾乎不變 | Sec. V-C, Fig. 5(a) | 這 29.2% 等於 Fig. 4(b) 的 26% |
| 日本例子：CI 449–502 gCO₂/kWh，PUE 1.32 | 用來說明髒電網同時 PUE 高，把 RR 的碳抬得更兇 | Sec. V-C | 每個區域都是這個 CI |
| CV 0.31→0.94。Llama/Mixtral：低負載 49/44→59/55；中 34/39→56/55；高 13/24→39/45。SLO 不變 | 35K 小時，2021–2024，選最低與最高 CV 以及 base hour | Sec. V-C, Fig. 5(b) | 26–60% 包住所有 CI hour |
| 高負載、CI spread 大時，facility MILP 仍可到 39–45% | 跨模型的上界 | Sec. V-C | 高負載永遠只剩 13% |
| Conclusion：facility MILP 相對 RR，跨 load 減碳 26% 到 60%，平均 SLO violation 3% | 26% 對得上 Fig. 4(b) Llama 高負載標籤；60% 對得上 abstract 的上界。這是解讀，不是論文寫出的換算 | Sec. VIII, Fig. 4(b), Abstract | Fig. 5(b) 的 13% 也在 26–60 裡 |
| Greedy < 1 ms。Std ILP、facility MILP、Green-LLM 的 p99 到 0.5 s。Iterative ILP 在 Llama 的 p99 是 6.5 s | 這是 scheduler 的 CPU 時間，不是 GPU token time | Sec. V-C, Fig. 6(a) | MILP 讓 TTFT 增加 0.5 s |
| Poll ≤ 2 s：facility MILP violation 最多 8.2%。5 s：升到 10.5–32% | Moderate load。Async 沒有穩定更好 | Sec. V-C, Fig. 6(b) | 1 s poll 是唯一可行值 |
| 8 個 scheduler：violation 10.3%→19.4%，減碳幾乎不變。更少但更大的 DC：violation 4.1%，減碳 23.2% | Llama，高負載，facility MILP。Engine 總數相同 | Sec. V-C, Fig. 6(c) | 排程器越多越省碳 |
| OSL bucket 正確率 51%（Llama）、37%（Mixtral）；鄰桶合計 99% 與 70%。亂猜約 17% | 兩層 MLP，128 units，約 27K 參數，< 0.1 ms | Sec. V-C | 預測很準，所以結果不變 |
| 預測 OSL 讓減碳最多移動 1.3（Llama）與 4.1（Mixtral）個百分點；violation 最多升 1.1 個百分點 | Iterative ILP 在 Llama 上會跟著它自己的 solver 延遲晃 | Sec. V-C, Fig. 7(a) | 所有政策都只動 1.1 點 |
| Long prompt 在 batch cap 16 省到 30%；mixed 在 cap 24 省到 28%；violation 近 5% | Mixtral。Mean ISL 10.7K / 2.9K。50 與 200 req/s。TTFT 放寬到 4.5 s | Sec. V-C, Fig. 7(b) | 圖上更右側、violation 更高的點也是 5% |
| OSL 100 大約比 OSL 10 多占 engine 十倍時間 | 解釋為什麼排程需要 OSL，是例子不是測量表 | Sec. IV | 他們的 workload 平均 OSL 是 100 |
| Idle：facility MILP 下 Llama TP=1 engine 在低/中/高負載閒置 73% / 56% / 33%，RR 最多 10%。Idle+host 佔剩餘碳的 28–81% | 觀察，用來動機一個還沒做的 engine activator | Sec. VI | MILP 已經把 DC 關掉 |
| TP=2 時 facility MILP 在高負載多排 22% 的碳，SLO violation 也更高 | 他們因此在這個比較裡偏好 data parallel | Sec. VI | TP 越高越省碳 |
| 16 DC = 4 region scheduler × 4 DC。每 DC 4 nodes × 8× A100-40GB | 模擬。一次 policy-rate 在一台 64-core server 上跑 200 s | Sec. V-A, Table II | 已經部署 16 個機房 |
| RTT 85–280 ms，AWS 一年 p50。預設 PUE 1.1 | Intra-DC 是 RR，所以減碳歸給 regional scheduler | Table II | RTT 可以忽略 |
| Load：RR 的平均 batch / capacity。低 <15%，中 15–40%，高 >40%。7B/8B 用 1200/2400/4000；Mixtral 用 800/1200/2000 | 模型之間的 req/s 不能直接比 | Sec. V-A | 4000 req/s 對 Mixtral 也是高負載 |
| MOER = greedy α=0。Green-LLM 只移植排程決策 | α 有 0、0.5、0.9 | Sec. IV-A, Sec. V-A | MOER 是另一套 batch ILP |
| Greedy α=0 在 moderate load 以外，高負載平均比 α=0.5 多 7.3 個百分點減碳、多 12.1 個百分點 violation | 差距從 Qwen 到 Llama 到 Mixtral 變大。RR 下 TPOT headroom 從 budget 的 71% 收到 51% | Sec. V-C | 這 71% 與 51% 是 SLO violation rate |

## 內部沒有對齊的兩組數字

1. **Fig. 4(b) 的印刷標籤**把高負載 facility MILP 寫成 Llama 26%、Qwen 33%、Mixtral 35%。
2. **PUE 段落**說 uniform PUE 1.1 的起點是 Llama 29.2%、Mixtral 36.6%，換成真實 PUE 後變成 30.5% 與 38.7%。

PDF 沒有說明 26 和 29.2 為什麼不同。簡報兩句都留著，不把其中一個改成另一個。可能是四捨五入、不同的 run，或標籤與正文取了不同的匯總。在作者說明之前，這是未解的差異，不是我們算出的第三個數字。

## Respectively

「saving up to 32.8% on dense models and 35.0% on Mixtral-8x7B, with SLO violation rates of up to 12.5% and 2.4%, respectively.」

前面的一對是 dense 與 Mixtral，所以簡報把 12.5% / 2.4% 讀成這兩個模型。它也可以被讀成 standard ILP 與 facility MILP。投影片不把 12.5% 單獨安到某一個 solver 上。

## 和 GreenCache 不要混

| | 這篇 | GreenCache |
|---|---|---|
| 決策 | request 送到哪個 DC | SSD cache 要開多大 |
| 碳 | operational，Scope 2 | operational + allocated SSD embodied |
| SLO | 任一 TTFT 或 TPOT 超過門檻即違規 | TTFT、TPOT 各自 90% attainment |
| 硬體敘事 | A100 上校準，geo 層是 simulator | L40 上的真實 serving，沒有獨立 GPU simulator |

## 我們的方向，不是作者結果

Heterogeneous GPU、HBM/HBF、attention / expert placement、cross-DC carbon-aware serving。作者自己的 future work 是 multi-turn KV locality，以及 DC 之間異質的模型與部署。Sec. VI 的 engine activator 也是他們提出、但沒有做出的系統。
