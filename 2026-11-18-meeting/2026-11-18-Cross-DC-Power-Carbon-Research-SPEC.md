# Cross-Data-Center Carbon- and Power-Aware LLM Serving — Research Evidence SPEC

> **文件用途：** 11/24（二）與杜教授討論前的研究資料整理規格，不是已完成的研究結果，也不是立即製作投影片的指令。  
> **建立日期：** 2026-11-17（Asia/Taipei）  
> **存放位置：** `2026-11-18-meeting/`；沿用 11/18 meeting 的現有 Carbon–SLO 與 HBM/HBF 資料。  
> **狀態：** Planning / Incremental evidence collection  
> **預計討論：** 2026-11-24（二）；正式會議議程、確切時段以邀請通知為準。  
> **資料檢視基準：** GitHub `main` @ `185874803c1f6828c68a0ec12211865cca90eb77`（2026-11-17 檢視時）。  
> **本 SPEC 的變更邊界：** 只新增本文件；不覆寫 11/18 Carbon–SLO、Research Materials、既有 PDF、講稿或 QA 成果。

## 0. Executive decision / 一句話主軸

**Proposed topic:** Cross-Data-Center Carbon- and Power-Aware LLM Serving with Heterogeneous GPU and HBM/HBF Memory Co-Design.

跨資料中心的 carbon-aware routing 是**系統層**研究主線；同一個 DC 內的 GPU power control、Attention/Expert（或 Attention/FFN）分工、HBM/HBF placement 是**硬體/serving 層**研究方向。以可重現的 energy + SLO + carbon model 連結兩層，逐步研究 **Operational Carbon + Allocated Embodied Carbon**。

重要定位：
1. **不是**聲稱「geo + heterogeneous GPU + power-aware scheduling」尚無人研究：FREESH 已覆蓋此組合；Carbon–SLO 已處理跨 DC、batch/queue/network、TTFT/TPOT 與 operational carbon。
2. **不是**聲稱「A/E（或 A/FFN）分工 + DVFS」尚無人研究：Janus、AFlex 等已有相近切入點。
3. **不是**聲稱 HBF 比 HBM 省電或省碳：HBF 存取成本、容量、batch、KV reuse、模型 placement、GPU waiting 和 SLO 可能使結論反轉。
4. **我們要驗證的問題**是：**記憶體配置改變 power–throughput / SLO-feasibility profile 之後，會不會改變跨 DC 的最佳路由以及整體排碳決策？** 這是研究假說，不是已證實的新穎性。

## 1. Scope / 成功條件

### In scope
- 調查既有研究在 geo-routing、heterogeneous GPU、DVFS、MoE disaggregation、HBM/HBF 與 carbon accounting 的覆蓋。
- 建立有原文來源與實驗條件的 **Power / Energy / Carbon Evidence Register**。
- 比較 HBM/HBF **operational energy** 與 **manufacturing embodied carbon**，不將不同模型的數字直接相加。
- 擬定兩層架構、baseline、統一指標、模擬/校準路線與可反駁的 RQ。
- 最終產出供杜教授討論的 8 頁左右「research direction / evidence」簡報；實際頁數依證據成熟度調整。

### Out of scope（此階段）
- 不實作或宣稱完成跨 DC / 多 GPU / HBF 模擬器整合；不宣稱已量測真實 HBF 晶片。
- 不把每個 Transformer layer 的 Attention 與 Expert 放到不同地理 DC，以 WAN 每層交換 activation 當作預設架構。
- 不將不同工作負載、GPU 數量、power boundary、SLO 與 baseline 的「節能百分比」當作可橫向比較的結果。
- 不因為假設的每容量 embodied carbon 較低就先行宣稱 HBF 系統總碳排更低。
- 在完整原文確認前，不把論文標題、數字、圖表編號視為已驗證可上台引用。

### Done 的定義
- [ ] 每項關鍵數據均有完整來源（paper/version/section/table/figure）、量測或模擬身分、硬體/工作負載/模型/SLO、單位、比較基線。
- [ ] 在相關工作矩陣中標清楚「已有研究」、「原文尚未確認」、「我們的假說」。
- [ ] 能用同一 service window/workload 定義 `J/token`、`tokens/J`、SLO goodput、`gCO2e/token`、allocated embodied carbon。
- [ ] 每個 RQ 至少對應 1 個 baseline、1 組控制變因、1 個可觀察的 outcome。
- [ ] 8 頁主講資料只放可追溯證據；詳細數字、公式、未解決矛盾保留在 Evidence Register / Backup。

## 2. Existing repo assets / 直接沿用的內容

| Existing file | 已有證據 / 可用於新方向 | 用法與限制 |
| --- | --- | --- |
| [2026-11-18-CarbonSLO-Evidence.md](2026-11-18-CarbonSLO-Evidence.md) | Carbon–SLO scope、Table I、A100/vLLM phase power/energy、Facility MILP、SLO | 以原 PDF 為準；跨 DC 是**模擬**、不是實體 16 DC |
| [2026-11-18-CarbonSLO.tex](2026-11-18-CarbonSLO.tex) | M04–M10 目標/估計/排程/驗證，Backup B12 GPU Power Figure 2 | 主講頁只摘取最相關圖，不重述整篇 |
| [2026-11-18-Research-Materials-SPEC.md](2026-11-18-Research-Materials-SPEC.md) | REEL LCI v1.0、HBM/HBF stack footprint、LCA 假設與單位限制 | 沿用既有資料；公開估算不等於廠商實測 |
| [2026-11-18-Research-Materials.tex](2026-11-18-Research-Materials.tex) | 五頁 HBM/HBF embodied-carbon evidence | 可直接作新報告 embodied-carbon 頁的底稿 |
| [../2026-11-11-meeting/2026-11-11-Research-Direction.tex](../2026-11-11-meeting/2026-11-11-Research-Direction.tex) | A/E placement 提案、simulator integration、13 篇 Related Work Matrix | 標記為 proposed architecture，不當作完成結果 |
| [../2026-11-11-meeting/README.md](../2026-11-11-meeting/README.md) | GreenCache 內容、Carbon Accounting、真實功率量測 | Backup B07（carbon）、M13（prototype vs. replay vs. model） |
| [../2026-10-28-meeting/2026-10-28-HBF_Sucks.tex](../2026-10-28-meeting/2026-10-28-HBF_Sucks.tex) | HBF thermal throttling、write endurance、placement | device model / trace-based，不是實體 HBF lifetime 實測 |

**Existing materials ≠ new integration complete.** 本次只整理研究與證據，不修改上述文件。

## 3. Prior-work reading queue / 論文優先順序

### P0：必須先整理的五篇

| ID | Paper | 要回答的研究問題 | 優先提取 | 資料狀態 |
| --- | --- | --- | --- | --- |
| P0-A | **Dissecting the Carbon–SLO Tension in Geo-Distributed LLM Serving** | Geo routing 如何在 batching / queue / RTT 下平衡 CI、energy 與 SLO？ | Table I、Fig. 2、Facility MILP / fixed shared energy、load/PUE/CI、validation | 本 repo 已有 PDF/講稿/證據 |
| P0-B | **FREESH: Fair, Resource- and Energy-Efficient Scheduling for LLM Serving on Heterogeneous GPUs** | 既有研究如何 joint geo routing、heterogeneous GPU、DVFS 和 fairness？ | Power–throughput profiles、objective、algorithm、carbon/energy vs baseline、限制 | 需完整讀原文與定位差異 |
| P0-C | **Cache Your Prompt When It's Green — Carbon-Aware Caching for Large Language Model Serving (GreenCache)** | Embodied allocation 如何與運行能源一起最佳化？ | Carbon accounting Eq.、Table 1 / cache footprints、測量邊界、SLO | 11/11 已整理；需萃取共用證據 |
| P0-D | **Characterizing High Bandwidth Flash for LLM Serving** | HBM/HBF read/write energy 與 placement 如何影響模型總能耗？ | Table 1、Tables 4–7、GLM MoE、weight placement、SLO limitation | 原文數值可取得；需轉為證據表 |
| P0-E | **Energy-Efficient LLM Serving via Disaggregated Attention–FFN and Flexible Frequency Scaling (AFlex)** | A/FFN 分工與 DVFS 已達成什麼、尚缺什麼？ | A/F resource + frequency control、energy/token、SLO、measurement boundary | 需完整讀原文 |

初步外部原文連結：
- Carbon–SLO: https://arxiv.org/abs/2610.14571
- FREESH: https://arxiv.org/abs/2511.00807
- GreenCache: 以本 repo 收錄的 paper / 11/11 citation register 為準；不得誤用任意同名來源。
- Characterizing HBF: https://arxiv.org/abs/2609.39131
- AFlex: https://arxiv.org/abs/2608.01891

### P1：支援 placement / architecture / simulator

| Paper | 作用 | 新穎性界線 |
| --- | --- | --- |
| Helix | heterogeneous GPU + network-aware placement / routing；跨區模擬 | 不等於 carbon-/power-aware HBM/HBF |
| ThunderServe | Prefill/Decode split、heterogeneous GPU、network-sensitive placement | 不預設支援 geo carbon |
| Janus | Attention / Expert disaggregation 與 expert scheduling | 「A/E worker 分工」不是單獨的新發明 |
| How Far Can Disaggregation Go? | A/FFN separation、GPU/network trade-off | 不假定 A/FFN 與 A/E 是完全相同的計算切法 |
| LLMServingSim 2.0 | 多 GPU / heterogeneous / disaggregated serving 模擬底層候選 | 驗證可配置的 power 與 memory hook，勿假設已支援 HBF |
| HBFSim / ServeLoop | 單裝置 HBM/HBF timing / controller、serving abstraction 候選 | 與另一篇 HBF serving simulation 的同名簡稱要區分；整合尚未完成 |
| MemExplorer | NPU + HBM/HBF heterogeneous memory DSE / token-per-joule | 硬體 DSE 已有前人研究；聚焦我們的 DC + serving 耦合 |
| HBF Sucks? | KV-centric HBF trace、thermal/write/endurance 限制 | 不把理論 peak bandwidth 當持續實際頻寬 |
| H³ / Hot–Cold Tiering | HBM/HBF power/perf 與 hot/cold KV 分層 | 原始假設、量測/模型邊界需分清 |

P1 不是要求 11/24 全部逐篇報告，而是為 Related Work Matrix 與教授問答提供準備。

## 4. Evidence track A — Geo carbon + power modeling

### A1. Carbon–SLO（從既有 slide 開始）
待擷取欄位：DC topology / 4×4 locations、A100/vLLM 校準、prefill/decode power curve、idle GPU/host、continuous batching、PUE、WAN RTT、CI window、request-rate distributions、Facility MILP objective（是否共享 batch 的 fixed energy）、TTFT/TPOT 約束、performance/energy MAPE。

已在現有 Evidence Notes 提及的 **核對候選值**：A100 idle 約 72 W、host 300 W、A100 400 W TDP 為上限不是逐步固定功率；vs RR 約 26–60% operational-carbon reduction、平均 3% SLO violations。**引用前再核對該值對應哪張圖、何種 load 與相對 baseline。** 不將逐步預測 MAPE 混成 geo E2E 模擬校準誤差。

### A2. FREESH（優先新增）
提取 joint decision variables（DC routing / GPU configuration / DVFS / parallelism / fairness）、power–throughput curve、資料中心分布、trace、carbon/energy reduction、SLO/fairness trade-offs。

原文摘要報告在其實驗設定下約 **28.6% energy reduction、45.45% emission reduction**；標示為 **paper-reported, baseline-and-setting-dependent**，不能和 Carbon–SLO 的 60% 直接比較。

### A3. GreenCache（可重用）
提取 `C_total = C_operational + C_embodied,allocated` 的 accounting 概念、電力測量途徑（RAPL / pyNVML）與 DRAM/SSD 規格模型、lifetime amortization、SSD cache 增加可能降低 prefill 卻提升 embodied 的反向效應。GreenCache **不是** geo scheduler。

**A track deliverables**
- [ ] `Geo-Power-Paper-Matrix.md`：Carbon–SLO vs FREESH vs GreenCache + AFlex 的 scope 與可追溯差異。
- [ ] `Geo-Power-Evidence.csv` 或統一 evidence table：CI、PUE、power、energy、SLO、workload、baseline。
- [ ] 1 張「geo 選擇不只是最低 CI」實驗證據圖與 1 張功率曲線；保留 figure number / caption / copyright attribution。

## 5. Evidence track B — HBM/HBF operational energy

### B1. Characterizing HBF Table 1：同一論文的 *per-stack simulation assumptions*

| Parameter | HBM | HBF | Unit |
| --- | ---: | ---: | --- |
| Capacity | 24 | 375 | GB（paper 指明 decimal） |
| Read energy | 3.4 | 6.8 | pJ/bit |
| Write energy | 3.4 | 100 | pJ/bit |
| Read bandwidth | 1,000 | 1,000 | GB/s（assumed peak） |
| Write bandwidth | 1,000 | 8 | GB/s |
| Read startup | 0.1 | 20 | μs |
| Write startup | 0.1 | 250 | μs |

**重要：** 這些值是 *assumed modeling parameters*，**不是實體 HBF 量測**。在該模型中，HBF read/bit = 2× HBM，write/bit ≈ 29.4× HBM；不代表整個 serving system 比 HBM 多耗 2×/29.4× 能源。特別檢查 HBF write energy 來自何種 SSD proxy、是否僅 KV、controller/thermal/host 是否納入。

### B2. 同篇 Table 6：固定 H3 硬體，換 weight placement

GLM-5.2 / 16 GPUs / TP16 / 1× 100k-turn trace / 10% buffer（simulated）：

| Architecture | Weights | Completion time (s) | Modeled energy (MJ) | Mean TPOT (ms) |
| --- | --- | ---: | ---: | ---: |
| 8+0 HBM-only | HBM | 11,354 | 9.11 | 218.72 |
| H3 8 HBM + 8 HBF | HBM | 4,543 | 7.19 | 279.15 |
| H3 8 HBM + 8 HBF | HBF | 4,538 | 9.54 | 278.01 |

**觀察（不外推）：** 在同一 H3 TP16 配置，weights in HBF 比 weights in HBM 多 (9.54−7.19)/7.19 ≈ **32.7% modeled energy**，completion time 卻接近。HBM-only 的 mean TPOT 反而較低；不能只憑 throughput/completion time 斷言 online SLO 改善。這是高吞吐量 agentic trace 的模擬，不是跨 DC 單請求服務實測。

接著查 **Table 7** 的 reduced weight reads、increased KV/index reads、avoided prefill 與 net energy savings；將 energy benefits/penalties 拆開，不只複製整體結果。

### B3. 補充 Power 研究
- H³：power efficiency / configuration trade-off；留意比較的功率邊界、硬體預算。
- MemExplorer：HBM/HBF 能源模型、token/J 與 NPU DSE；不得當成實測 GPU。
- HBF Sucks?：write-heavy KV、thermal throttling、write endurance、controller 限制。
- Hot–Cold Tiering：hot KV in HBM、cold session state in HBF；比較的是 hot/cold placement，而不是所有 KV 都放 HBF。
- AFlex：A/FFN frequency sensitivity、measured GPU energy/token，可提供 GPU worker power-control baseline。

**B track deliverables**
- [ ] `HBM-HBF-Power-Evidence.md`：每個 memory parameter 的 original table / parameter origin / assumption quality。
- [ ] 至少 2 組 **same-model + same-workload + controlled hardware** 的 power/energy placement 對照；標明是 simulated 還是 measured。
- [ ] memory read/write energy calculator 公式與單位一致性：
  - `E_mem_dynamic[J] = (N_read_bits * e_read_pJ_bit + N_write_bits * e_write_pJ_bit) * 10^-12`
  - 必須另處理 idle/standby、controller、background、GPU stalled/waiting、network；避免與 GPU board power profile 重複計價。
- [ ] `Known HBF uncertainties`：read/write latency、write amplification、thermal cap、power cap、lifetime、package power、production hardware unavailability。
- [ ] 不把 `pJ/bit`、`W`、`J/token`、`MJ/workload` 或 `kgCO2e/stack` 當成可直接相加的量。

## 6. Evidence track C — Embodied Carbon / REEL LCI

沿用既有 `2026-11-18-Research-Materials-SPEC.md`，不複製整份 LCA 描述。供彙整頁使用的**模型估算**：

| Component | Published capacity label | REEL v1.0 kgCO2e/stack | Caveat |
| --- | --- | ---: | --- |
| HBM3 8-Hi | 16 GB | 13.52 | REEL model output |
| HBM3 12-Hi | 24 GB | 19.81 | REEL model output |
| HBM3E 12-Hi | 36 GB | ≈20.6 | rounded published result |
| HBF Gen 1 16-Hi | 512 GiB | 225.9 | prospective HBF model, not production measurement |

- **Per-stack** HBF 的製造碳排高於表中 HBM stacks，**不同容量**不可視為 equal-capacity test。
- 既有頁面的 nominal normalization（HBM 與 HBF GB/GiB 標示不一致）是 **unharmonized arithmetic index**；約 47.8% lower 的數字不得寫成經驗證的「per-GiB saving」。
- HBF dataset 有製程、die area/yield、package boundary 與 inventory gaps；設備與 interposer/assembly 的完整碳排要避免漏算/重複算。
- REEL manufacturing carbon 和 serving electricity operational carbon 是不同生命週期範圍；需指定硬體 lifetime、allocation period、使用率與系統邊界才能合成 total。
- 不把 `225.9 kgCO2e` 加在**已包括 HBF 的完整 GPU/封裝 footprint** 上再次計算。

**C track deliverables**
- [ ] `Embodied-Carbon-Allocation.md`：stack → package → board/server → DC 的邊界與分攤假設。
- [ ] 情境敏感度（base / conservative / optimistic）；不得將未經驗證的 ± uncertainty band 當正式信賴區間。
- [ ] 以 **同 workload、同 SLO、同期間** 比較 operational+allocated embodied；不只比每 GB footprint。

Reference: https://reellci.com/insights/the-hbf-inversion.html；https://reellci.com/d/hbf-gen1-16hi/；https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf

## 7. Research architecture hypothesis / 兩層架構

```text
Incoming requests / sessions
       |
       v
Global / Regional Carbon-Aware Scheduler
Inputs: CI(region,t), PUE, GPU/memory inventory, load, queue, WAN RTT, SLO
Decision: request / session -> DC or replica; not per-layer WAN placement
       |
       +--------------------------+
       |                          |
       v                          v
  DC A local scheduler       DC B local scheduler
  hetero GPU + DVFS          hetero GPU + DVFS
  HBM-rich Attention         Attention / Prefill workers
  HBF-rich Experts           HBM/HBF KV & weight placement
  same-site A/E traffic      same-site disaggregation
       |                          |
       +---------- metrics -------+
      power/energy, TTFT/TPOT, SLO goodput, operational + allocated carbon
```

**關鍵取捨：** 跨 DC 以 request/session 級 routing 為基礎；A/E worker 放同一 DC（仍需計網路或 NVLink / PCIe transfer）。若討論跨 DC model split，必須先以每層 activation traffic、RTT、bandwidth 與 SLO 做 feasibility gate，而不是預設可行。

## 8. Research Questions / baseline and experiments

### RQ1 — Geo-aware energy and carbon
**Question:** 在控制相同服務工作負載下，加入 phase-/load-aware power model、geo CI 和 heterogeneous GPU scheduling，能否降低 operational carbon 且維持 TTFT/TPOT SLO？

- Baselines: Carbon–SLO reported policies（RR / Greedy / Standard ILP / Facility MILP）；FREESH 的適用控制方法。
- Variables: CI spread、arrival rate、region/DC routing、RTT、PUE、GPU profiles、DVFS；同一地區/工作負載條件下 ablation。
- Outputs: energy (kWh)、operational kgCO2e、SLO goodput、TTFT/TPOT distributions、SLO violation、admission/drop rates。
- Caveat: Carbon–SLO 與 FREESH 的實驗架構不同，需建**共同平台/基線**才能做定量宣稱。

### RQ2 — HBM/HBF placement and worker power
**Question:** 哪些 HBM/HBF 配置、KV/weight placement 和 A/E 分工能在較高 HBF access cost 下，降低服務能源且滿足 SLO？

- Baselines: all-HBM placement、hybrid HBM/HBF (hot/cold weights or KV)；必要時比較 monolithic vs A/E（固定硬體資源）。
- Variables: HBM/HBF stack counts、read/write pJ/bit、bandwidth/latency、arrival/load、batch、reuse、expert popularity、GPU waiting power、activation/network costs。
- Outputs: J/output-token、tokens/J、goodput under SLO、power (W) by phase、memory traffic、completion time、TPOT distribution、write endurance。
- Controls: **equal GPU count / equal memory capacity / equal package sites / equal cost / equal power budget** 是不同試驗，不可全部混成「fair comparison」。

### RQ3 — Total carbon accounting
**Question:** 在相同 output-quality / workload / SLO 下，memory-aware hardware co-design 的 operational benefit 能否抵銷 allocated embodied carbon？

- Total: `C_total = C_operational + C_embodied,allocated`，使用相同服務期間與碳排單位。
- Approximate operational expression: `C_op = sum_d E_IT(d, kWh) * PUE(d) * CI(d, kgCO2e/kWh)`。如果 network 或 facility 已內含，**不可重複乘 PUE/重複計價**。
- Control: model、quantization、prompt/output lengths、arrival trace、SLO、service duration、hardware inventory、baseline placements。
- Report: gCO2e/valid output token 及 total kgCO2e、goodput、utilization、amortization/lifetime sensitivity；對 dropped requests 的公平性/品質做顯式報告。

## 9. Simulation & calibration plan / 不預設整合已完成

1. **Baseline fidelity first:** 複核 Carbon–SLO 總結、程式、A100 phase energy calibration 與共用 batch fixed-energy 模型，先再現至少 1 個已公開實驗情境。
2. **Local serving:** 檢查 LLMServingSim 2.0 的 hetero GPU / TP, PP, EP / runtime power model 接口，與 profile/trace 的來源；現階段只做 interface mapping。
3. **Memory:** 分別確認 HBFSim/ServeLoop 的 memory transactions、HBM/HBF latency、controller/FTL、是否已有 energy model；若沒有則建立假設與必要校準資料。
4. **Causal integration:** 由 workload/serving simulator 產生 memory accesses，回傳 dependencies/completion times；處理可 overlap 部分，不能直接將 `T_compute + T_memory + T_network` 當真實 end-to-end。
5. **Energy boundary:** 記錄 GPU board power 是否包含 memory；若以 component power 分解，才另外計 HBM/HBF dynamic + background。Idle/waiting energy 納入。
6. **Geo integration last:** 當 local power–performance profile 可信後，讓 geo scheduler 依每 DC profile + CI/PUE/WAN RTT 選擇 routing / capacity。
7. **Honest status:** 所有 simulator links 都以 `candidate integration` 稱呼；若無法復現，改做 sensitivity analysis，不宣稱實體節能驗證。

## 10. Data schema / 後續統一填表

建議產出 `2026-11-18-meeting/evidence/Power-Carbon-Evidence.csv`（本 SPEC 建立時**尚未產生**）；每一列是**一個數值或一個有共同條件的比較**，至少有：

| Column | Meaning |
| --- | --- |
| `claim_id` / `category` | 唯一識別；geo / GPU / memory / embodied / system |
| `paper_title` / `source_url` / `version` | 論文版本與可回溯原文 |
| `section` / `table_figure` / `page` | 精確證據位置 |
| `status` | `verified-primary` / `reported-needs-check` / `modeled` / `assumed` / `derived` / `hypothesis` |
| `quantity` / `value` / `unit` | 對比前保持原始單位 |
| `baseline` / `comparison` | 基準與測試組 |
| `hardware` / `memory_config` | GPU、stack、HBF/HBM placement、precision |
| `model` / `workload` / `load` | LLM、trace、arrival、input/output、batch |
| `slo` / `metric_denominator` | TTFT/TPOT 門檻、request/output token/workload |
| `power_energy_boundary` | board/GPU/DRAM/HBF/host/network/PUE 是否包含 |
| `notes` / `limitations` / `checked_on` | 假設、單位警告、是否與原文一致 |

規則：paper-reported model result ≠ real hardware measurement；source estimate ≠ our verified calculation；new simulation result ≠ author claim；不引用只有表格而無設定的節能百分比。

## 11. Proposed 11/24 meeting deck / 約 8 頁，12–15 分鐘

| Slide | Title | Figure/table to prepare | Evidence gate |
| --- | --- | --- | --- |
| 1 | Research Goal and Scope | One-slide thesis / 2-level scope | 明確說 proposed |
| 2 | What Has Prior Work Already Solved? | Carbon–SLO / FREESH / GreenCache / Janus / AFlex matrix | 不能宣稱無前人研究 |
| 3 | Why Does Geo-Aware Power Modeling Matter? | Carbon–SLO Figure 2 / CI + batching + SLO + FREESH | 圖與數字附 baseline |
| 4 | HBM vs. HBF: Operational Energy | Characterizing HBF Tables 1/6/7 | assumption vs modeled result |
| 5 | HBM vs. HBF: Embodied Carbon | REEL v1.0 existing slides | GB/GiB 與 package boundary |
| 6 | Proposed Two-Level Serving Architecture | Geo request routing + local GPU/memory/A/E | same-DC A/E; WAN constraint |
| 7 | Simulation Framework and Evaluation Plan | Carbon–SLO / LLMServingSim 2.0 / HBFSim | interface mapping ≠ completed integration |
| 8 | Research Questions and Discussion | RQ1/2/3, novelty / calibration / experiment sequence | evidence gaps openly noted |

教授偏好的敘事：**Summary → Motivation（用圖/數據）→ Method idea → Planned evaluation → Limitations / next decision**。簡報保持精簡，完整數值與未解決矛盾保留在 evidence document；不要搶先加入大量 backup 或重新講過去所有論文。

## 12. Step-by-step task backlog / 我們接下來一項一項做

| Priority | ID | Task | Output / exit criterion | Status |
| --- | --- | --- | --- | --- |
| P0 | T01 | 將 Carbon–SLO geo/power/energy baseline 整理為 claim ledger | 原文 Table I、Fig. 2、power/energy/CI/SLO 的來源與限制 | PARTIAL：Fig. 2、geo/PUE/SLO ledger 完成；Table I 全比較未擴充 |
| P0 | T02 | 精讀 FREESH | 決策變數、energy model、geo/hetero/DVFS 的重疊與缺口 | DONE（2026-11-17）：原文/附錄與 scope matrix、限制見 Power-Carbon-Slide-Evidence |
| P0 | T03 | 萃取 GreenCache carbon accounting | operational+embodied boundary 與 amortization 假設 | DONE（2026-11-17）：Eqs. (1)–(5)、amortization/count-once 見 evidence register |
| P0 | T04 | 建立 HBM/HBF power quantification | Table 1、6、7 精確來源、單位、same-config ablation | DONE（2026-11-17）：Table 1/6/7 與 same-H³ placement pair 已核對；第二組 controlled study 仍待辦 |
| P0 | T05 | 萃取 REEL HBM/HBF embodied-carbon boundary | stack/package、GB vs GiB、可信度與生命週期分攤 | PARTIAL：保留並核對 stack/package、GB/GiB 與限制；生命周期敏感度未完成 |
| P1 | T06 | 讀 AFlex + Janus + MemExplorer | A/E–DVFS 與 memory DSE 的已有貢獻與 gap | PARTIAL：Janus/AFlex 定性 scope 已核對；MemExplorer 僅 author record，完整定量 review 未完成 |
| P1 | T07 | 建共同 related-work matrix | Geo / GPU / A/E / HBM-HBF / Power / Embodied / SLO / Simulator | PARTIAL：Carbon–SLO/FREESH 兩篇 matrix 完成；其他論文仍待擴充 |
| P1 | T08 | 檢查 simulator APIs 與 energy boundary | integration feasibility map、calibration plan | TODO |
| P1 | T09 | 定義 RQ1–3 的 baseline / metrics / ablation | 研究設計表，足以給教授評估 | TODO |
| P2 | T10 | 製作 11/24 簡報與講稿 | 每頁 claim-to-source；符合目前簡報排版規範 | TODO |

**開始順序建議：T01 → T02 → T04 → T03 → T05 → T06/T07 → T08/T09 → T10。** T04 排在中間，是因為用確定的 HBM/HBF 能源數字決定接下來更值得聚焦 KV 還是 Expert placement。

每完成一項時，更新本表、增列 evidence CSV/MD、寫「觀察 / 推論 / 假說 / 未知」四欄。避免每次重新整理全部論文，維持 stable claim IDs。

## 13. Questions for Professor Du / 等待研究討論決定

1. Primary objective 應優先 operational carbon、total carbon、energy/token，還是多目標（carbon+SLO+cost）？
2. 比較上是否先限定**跨 DC request routing**，再擴展 DC 內 GPU/HBM/HBF placement？
3. 哪些資料必須 real GPU measurement 校準？哪些可以接受 HBF 未量產的 sensitivity/simulator study？
4. 我們應優先研究 MoE expert residency、agentic KV hot/cold，還是 GPU idle/DVFS 和 memory traffic 的交互作用？
5. 是否可取得地區 CI/PUE、GPU功率 profile、真實 workload trace？可用度將決定 simulator 的可信度。

## 14. Source index and citation discipline

**Repo sources:**
- [11/18 Carbon–SLO Evidence](2026-11-18-CarbonSLO-Evidence.md)
- [11/18 Research Materials SPEC](2026-11-18-Research-Materials-SPEC.md)
- [11/11 Research Direction SPEC](../2026-11-11-meeting/2026-11-11-Research-Direction-SPEC.md)

**External primary sources / starting points:**
- Carbon–SLO: https://arxiv.org/abs/2610.14571
- FREESH: https://arxiv.org/abs/2511.00807
- Characterizing HBF: https://arxiv.org/abs/2609.39131
- AFlex: https://arxiv.org/abs/2608.01891
- Hot–Cold Tiering: https://arxiv.org/abs/2609.25782
- MemExplorer: https://www.microsoft.com/en-us/research/publication/memexplorer-navigating-the-heterogeneous-memory-design-space-for-agentic-inference-npus/
- REEL HBF v1.0: https://reellci.com/insights/the-hbf-inversion.html
- HBF dataset assumptions: https://reellci.com/d/hbf-gen1-16hi/

**Verification rules:** 報告上任何百分比、表格數字，都需回到原文完整情境；圖表應保留原標題/caption 和軸單位。Web 摘要/第三方轉載只能作 locator，最後以原文 PDF / publisher / official repository 為準。若不同版本資料衝突，標明版本和未解決項，禁止硬湊一致。

---
**2026-11-17 更新：** 14 頁 Research Materials 與 `2026-11-18-Power-Carbon-Slide-Evidence.md` 已整理 Fig. 2、FREESH scope、HBF Table 1/6/7 及 accounting。下一步補完整 MemExplorer/Janus/AFlex 定量 review、第二組 controlled placement study、allocation scenario，再推進 T08/T09。這不是 T10 的 11/24 簡報或 simulator 完成紀錄。
