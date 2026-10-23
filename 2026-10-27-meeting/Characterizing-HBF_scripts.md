# Characterizing High Bandwidth Flash for LLM Serving｜繁體中文講稿

主報告共 11 頁，目標約 14 至 15 分鐘。第 12 至 19 頁是 Backup，主要留給問答使用，不計入正式報告時間。以下頁碼對應 `2026-10-27-Characterizing-HBF.pdf`。

## 第 01 頁｜Characterizing High Bandwidth Flash for LLM Serving

這篇論文主要想回答的問題是，當我們在 GPU 附近加入非常大量的 HBF，也就是 High Bandwidth Flash 容量之後，到底在什麼條件下，它真的可以改善 LLM serving。這裡我覺得一開始要先強調，這篇論文的重點其實是「容量」，而不是說 HBF 本身比 HBM 更快。事實上後面會看到，HBF 在 latency、write bandwidth 以及 energy 上都有明顯代價。

所以作者真正研究的是，當系統多了一個很大的 device-side memory tier 之後，要怎麼配合 memory architecture、data placement 以及 scheduling，才能真的把這些額外容量轉換成 throughput 或 energy 上的收益。整篇論文主要使用 request-level simulator，比較不同的 HBM、HBF 配置，以及不同的 scheduling 和 placement policy，最後觀察整批 workload 的 completion time、energy consumption 和 HBF write amount。

這篇最重要的結論可以先放在這裡：HBF 並不是加上去就一定比較快。它的價值主要來自可以擴大 on-device working set，而這個容量要真的有用，memory architecture、資料配置和 scheduler 必須一起 co-design。接下來我會先從為什麼 agentic workload 特別需要這些容量開始講。

## 第 02 頁｜Why Does Agentic Serving Need More Device Memory?

為什麼這篇會特別討論 agentic serving？因為在一般 LLM serving 裡，HBM 本來就要同時容納 model weights 和目前正在執行 request 的 KV cache，但到了 agentic workload，還會多出一種很重要的資料，就是已經完成某一輪、現在暫時沒有運算，但之後仍然可能再次使用的 KV cache。

例如右邊這個簡單的流程，一個 agent session 先執行 Turn 1，產生一批 KV cache，接著 agent 可能去呼叫 tool 或等待外部環境。等工具執行完成之後，它再進入 Turn 2，而這時新的 request 通常會包含前一輪的 conversation context，所以 Turn 1 的 KV cache 其實還有很高的 reuse value。

問題是，在等待 tool 的這段時間裡，這些 KV 並不是 active request 的一部分。如果 HBM 很滿，系統很可能為了容納新的 request，把這些暫時 inactive、但之後還會使用的 KV cache evict 掉。下一輪回來時，就必須重新載入，甚至重新計算 prefix。

因此 HBF 的吸引力就在這裡。它可以提供比 HBM 大非常多的 package-local capacity，讓系統保留更多這類 reusable state。不過它並不是免費容量，因為 HBF 的讀取能耗更高、write bandwidth 比較低，而且 NAND 本身還有 endurance 問題。所以這篇接下來要研究的其實是，這些額外容量到底要怎麼用才划算。

## 第 03 頁｜Two Ways to Add HBF: Shared-Site vs. H³

作者考慮兩種把 HBF 放進 GPU memory system 的方式。第一種是左邊的 shared-site architecture。這種設計假設原本 package 上可以放八個 memory stacks，但 HBM 和 HBF 必須共用這八個位置。圖中的四個 HBM 加四個 HBF 只是其中一個例子。因此如果想增加更多 HBF，就代表必須犧牲原本的 HBM stack，也就是同時犧牲一部分 HBM capacity 和 bandwidth。

右邊的 H³ 就不一樣。它的概念是原本八個 HBM stacks 都保留，再額外增加八個 HBF stacks。HBF 放在 HBM 後面，利用 HBM 作為比較快速的 buffer，因此作者假設 HBF access latency 有一部分可以被隱藏。

所以這兩種架構不能只解讀成「一個是並行、一個是串行」。真正重要的差別是 resource budget。Shared-site 是拿原本的 HBM resource 去交換 HBF capacity，而 H³ 則是保留完整 HBM，再增加額外 HBF。當然，H³ 的代價就是需要更多 stacks、更複雜而且成本更高的 packaging。

這也是後面看實驗時很重要的一點。如果 H³ 比 shared-site 快，不能直接說是因為 H³ 的連線方式比較好，因為它本身就擁有更多 memory resources。

## 第 04 頁｜How Does the HBM–HBF–Host Hierarchy Work?

有了 HBM 和 HBF 之後，下一個問題就是資料怎麼放。這篇並不是把 HBF 當成一個「HBM 滿了之後什麼都往裡面丟」的 overflow storage，而是針對不同種類的資料設計不同 placement。

最熱的資料還是放在 HBM。像是 activations、目前 active request 使用的 KV，以及剛重新載入的 prefix，都是先進 HBM。如果 KV 逐漸變冷，再根據 request-level LRU policy 往 HBF、host DRAM，最後甚至 SSD 移動。

Model weights 的情況稍微不同。每一個實驗 configuration 裡的 weight placement 是固定的，不是在 runtime 不斷搬來搬去。如果是 MoE model，作者會根據 offline routing profile，把比較常被使用的 experts 固定放在 HBM，剩下比較少使用的 experts 放在 HBF。

另外這篇也考慮 sparse attention。這裡有一個 indexer 會先掃描整個 context 的 index，再選出例如 Top-2048 個 token positions，真正的 attention 只去讀這些位置的 KV。因此雖然 KV access 是 sparse 的，但是 index 本身其實會被非常頻繁地掃描，所以它比很多 KV 都更 hot。當 HBM 不夠時，系統會優先把適合 demote 的 KV 移出去，而不是先把 index 趕走。

所以這一頁真正要強調的是，HBF 的價值跟 object placement 有很大關係。不同資料有完全不同的 access pattern，不能把它們全部當成同一種 memory object。

## 第 05 頁｜Why Is Cache-Aware Scheduling Alone Not Enough?

接下來這一頁是我覺得這篇很重要的一個系統觀察。一般來說，如果某個 request 已經有很多 KV cache 留在 device memory 裡面，我們會覺得應該優先執行它，因為可以得到比較高的 cache hit。這就是左邊的 cache-aware scheduling。

但是問題是，只顧目前這一次的 cache hit，不代表未來的 cache hit 一定會被保留。當 scheduler 不斷把新的 request admit 進來時，active requests 會占用越來越多 locked KV。當 memory pressure 增加，就有可能把那些暫時沒有執行、但是下一個 turn 還會用到的 prefix evict 掉。結果現在這一輪看起來 cache hit 很高，可是下一輪回來時，反而失去了原本可以 reuse 的資料。

所以右邊加入了一個 buffered admission policy。它的想法很簡單：不要把 memory 塞到完全滿才停止 admit request，而是只有在目前 locked state 加上新 request 所需要的 state，還沒有超過某個 threshold 時，才允許新的 request 進來。這篇使用的是百分之九十，也就是保留大約百分之十的 headroom。

這裡的百分之十不是把 HBM 永久切一塊出來完全不用，而是一個 admission threshold。Request 被 admit 之後，它的 context 還是可能繼續變大。

這個方法的直覺是，我們刻意少一點 instantaneous concurrency，但換來比較少的 cache churn。只要能保留更多 reusable prefix，就可以減少重新載入、重做 prefill，以及重新寫入 HBF 的次數。所以這篇後面第一組實驗，就是要確認這種 scheduler 到底能不能同時改善效能和 endurance。

## 第 06 頁｜What Exactly Does the Simulator Model?

在看數字之前，要先知道這篇的 simulator 到底模擬到什麼程度。這不是一個 cycle-level GPU simulator，它比較接近 request-level serving simulator。

左邊是作者用來驗證 simulator 的結果。他們先把 HBF offload 關掉，只模擬 HBM-only serving，再拿 Llama 3.1 8B 在 H100 上的模擬 throughput 跟實際 profiled vLLM 做比較。Request 數量從三十二到四千零九十六，平均 input length 是四千零九十六 tokens，output 則測試一百二十八和五百一十二 tokens。

整體 throughput 的 MAPE，也就是 mean absolute percentage error，大約是百分之九點一四。因此作者認為 request-level performance model 在這個範圍內可以合理重現實際 serving behavior。

右邊則是整個模擬流程。輸入 request trace 之後，scheduler 決定哪些 request 執行以及 cache 如何變化，再根據 fitted kernel latency model 計算 GPU operation，並且模擬 HBM、HBF、host DRAM、SSD 和 PCIe 或 NVLink 上的 data transfer，最後得到 completion time、energy 以及 flash writes。

需要特別注意的是，kernel latency model 有用 H100 和 B200 的實際 profiling 校準，但是 HBF 本身還沒有量產硬體可以實測，所以 HBF 的 latency、bandwidth 和 energy 還是來自 assumed specification 或 extrapolation。因此這篇應該理解成 architecture and system characterization，而不是 production HBF hardware benchmark。

## 第 07 頁｜Experimental Setup: What Workload Stresses HBF?

這一頁主要是解釋 workload，因為後面會一直看到 1× trace 和 5× trace。

原始的 LMCache workload 有兩萬四千八百八十個 turns，來自七百六十七個 sessions。這裡 session 指的是一整段 agent conversation，而 turn 才是其中一次 LLM request。所以一個 session 可能是 Turn 1 執行完，等待 tool，接著 Turn 2，再等待，然後 Turn 3。

後面的 100k experiment 使用三千零八十個 sessions。比較特別的是 5× workload 並不是單純把 request 數量乘五，然後產生五倍互相獨立的短 conversation。作者是把同一個 session 的五份 workload 接在一起，讓 context 持續累積。

因此 1× 和 5× 都是三千零八十個 sessions，但是總 turns 從十萬增加到五十萬，而且平均 input length 從大約兩萬兩千五百五十八 tokens 增加到八萬九千一百二十五 tokens。

所以 5× 的意義不只是系統比較忙，而是每一個 conversation 本身變得更長，per-session KV state 也大幅增加。這正是 HBF 大容量可能最有價值的場景。

後面的實驗分成三部分。Qwen3-32B 主要用來研究 scheduling 和 endurance，Llama 3.1 405B 看 dense model，而 GLM-5.2 則用來研究 MoE model 的 placement 和 parallelism。

## 第 08 頁｜Q1: Can Scheduling Make HBF KV Writes Sustainable?

第一個實驗要回答的是，scheduler 能不能真的降低 HBF write pressure，而且不是單純拿 performance 去換 endurance。

這裡硬體固定使用 H³，也就是八個 HBM 加八個 HBF，model 是 Qwen3-32B，所以表格裡三列主要差別只有 scheduling policy。第一個是 FCFS，第二個是 cache-aware，第三個則是在 cache-aware 上再加入剛剛講的百分之十 admission buffer。

從 cache-aware 加 buffer 之後可以看到，HBF KV writes 從二十一點八一 TB 降到六點六九 TB，減少百分之六十九點三三。這個下降其實非常大。

更重要的是，performance 並沒有因此變差。Completion time 從一萬零九百三十點七八秒降到一萬零四百一十九點一七秒，大約又改善百分之四點六八。同時 device hit rate 上升到百分之九十六點四六。

這跟前面講的機制是一致的。因為 scheduler 不會一直把 memory 塞滿，減少了 reusable prefix 被反覆 eviction，所以後面不需要一直 reload 或重新產生同樣的 KV，也就同時減少了 execution time 和 flash writes。

最右邊還有一個 lifetime estimation。FCFS 算出來只有一點二一年，而 buffered policy 可以到十四點八二年。不過這裡一定要強調，這不是硬體實際跑十四年的測試結果。它是假設 NAND 可以承受十萬次 P/E cycles、wear 完全平均，而且 write amplification 等於一之後算出來的 model estimate。

所以真正有意義的結論不是「HBF 可以用十四年」，而是 serving policy 本身就可能讓 flash write pressure 相差一個數量級。

## 第 09 頁｜Q2: Does More HBF Capacity Help Dense LLM Serving?

第二個問題是，對 dense LLM 來說，多出來的 HBF capacity 到底有沒有用，以及收益主要從哪裡來。

這裡使用 Llama 3.1 405B、八張 GPU、TP8，workload 是 1× 的十萬 turns，scheduler 使用百分之十 buffer。表格第一列是 HBM-only，第二列是 H³，但是 model weights 還是留在 HBM，第三列則是把 weights 放到 HBF。

先看前兩列。加入 HBF 之後，completion time 從三萬九千六百六十六秒下降到兩萬一千四百三十九秒，大約減少百分之四十五點九五。Energy 也從五十三點六零 MJ 降到四十點七零 MJ，大約減少百分之二十四。

所以從整批 workload 的角度看，extra capacity 是非常有幫助的。

但是最後一欄 TPOT 很重要。HBM-only 是九十點八五毫秒，H³ 反而增加到四百三十八點六一毫秒。也就是說，整批 workload 可以更快完成，不代表每一個 user 等下一個 token 的 latency 更低。

這篇的 optimization target 比較偏 high-throughput serving，而不是 latency-sensitive serving。

接著比較第二列和第三列，可以看到把 dense model weights 從 HBM 移到 HBF 幾乎沒有進一步改善 completion time，兩萬一千四百三十九跟兩萬一千四百二十三幾乎一樣，但是 energy 反而增加大約百分之三點三三。

原因也很直觀。Dense model 的 weights 幾乎每一個 token 都要讀，所以是非常 hot 的資料，不適合放到 energy cost 更高的 HBF。HBF 真正有價值的是拿來放比較冷、但是我們又希望可以繼續保留的 KV state。

因此這組實驗的結論是，dense model 的收益主要來自 extra KV capacity，而不是把 hot model weights 搬到 HBF。

## 第 10 頁｜Q3: How Do Placement and Parallelism Change MoE Results?

第三個實驗看的是 MoE model，這時候情況更複雜，因為除了 HBM 和 HBF placement 以外，還有 TP、EP 和不同 replica configuration。

這裡使用的是 GLM-5.2。所謂 TP16、EP16 加上 DPA，可以想成一個十六張 GPU 的 replica。另一種 2×TP8，則是兩個獨立的八張 GPU replica。DPA 讓不同 GPU 負責不同 request 的 attention 和 KV，但是進到 MoE layer 之後，token activation 還是會根據 expert routing 被送到對應的 expert GPU。

左邊圖是 1× workload，右邊是 5× workload。橫軸是 completion time，縱軸是 modeled energy，所以越靠左下越好。不過左右兩張圖的 scale 不一樣，所以不要直接用點跟點之間的視覺距離比較。

先看 HBM-only 跟 H³，而且都讓 weights 留在 HBM。1× workload 的 completion time 從一萬一千三百五十四秒降到四千五百四十三秒，減少大約百分之五十九點九九。

到了 5× long-context workload，差距更大。HBM-only 需要十九萬八千四百一十一秒，而 H³ 只需要兩萬八千二百七十九秒，大約快七倍，同時 energy 從九十一點九九 MJ 降到三十七點六二 MJ，減少百分之五十九點一。

這代表當 context 變得非常長、KV working set 大幅增加時，額外 HBF capacity 的價值會變得更明顯。

不過最快的 configuration 並不是最省 energy 的。5× workload 裡，最快的是兩個 TP8 replica，而且 weights 全放 HBF，完成時間是兩萬四千三百八十五秒。但是它的 energy 是五十二點零六 MJ，比剛才 HBM weights 的三十七點六二 MJ 高很多。

Shared-site 也有類似 trade-off。1× workload 時 6 HBM 加 2 HBF 表現最好，但到了 5×，4+4 的 completion time 比 6+2 快百分之十四點二五；相反地，6+2 的 energy 又比 4+4 少百分之四點零一。

所以這裡真正想證明的是，當 context 變長，最佳 HBM/HBF ratio 會改變，而且最快、最低 energy、最低 latency 不一定是同一個 configuration。Placement 和 parallelism 必須根據 optimization objective 一起決定。

## 第 11 頁｜Where Do the Gains Come From, and What Did the Paper Prove?

最後這頁把前面的結果整理成真正的原因。因為如果只看到 energy 下降，很容易誤會成 HBF 本身比較省電，但其實完全不是。

這篇假設 HBM read energy 是每 bit 三點四 pJ，而 HBF 是六點八 pJ。也就是說，直接從 HBF 讀資料其實更耗能。

整體 energy 之所以還是會下降，是因為 extra capacity 改變了整個 serving execution pattern。

第一條路徑是 batch size。當 device memory 容量增加之後，系統可以同時保留更多 request，形成更大的 batch。這樣同一批 model weights 可以服務更多工作，因此 weight read 被更有效率地 amortize。

第二條路徑是 KV reuse。更多 KV 可以留在 device memory，就比較不容易失去 reusable prefixes，因此可以減少重新載入以及重新執行 prefill。

右邊表格把這些 contribution 拆開。對 Llama 的 1× workload，最後 net energy saving 是百分之二十四點零六；對 GLM 的 5× workload，則是百分之五十九點一。不同 workload 的節能來源不完全相同，但都不是因為 HBF 單次 access 比 HBM 省電。

所以整篇論文可以整理成三個結論。第一，HBF 最主要的價值是 capacity，可以擴大 on-device working set。第二，這些 capacity 能不能真的轉成效能或 energy benefit，非常依賴 placement 和 scheduling，尤其 scheduler 必須避免反覆 cache churn 和無效 HBF writes。第三，HBF 不能被當成一層被動的 overflow memory，而是需要跟 serving system 以及 GPU memory architecture 一起 co-design。

另外這些結果都是 simulator 在明確 hardware assumptions 下得到的結果，並不是 production HBF hardware measurement。主報告到這裡結束，後面幾頁我保留比較細的 hardware assumptions、equations、parallelism example 和完整 table，如果有問題再往後看。

## 第 12 頁｜HBM vs. HBF Assumptions

這張主要是問答時如果需要確認硬體參數，可以回來看。作者假設 HBM 和 HBF 每個 stack 的 read bandwidth 都是每秒一千 GB，但是其他特性差非常多。HBM 每個 stack 只有二十四 GB，而 HBF 是三百七十五 GB，所以 HBF 的核心優勢是容量。

相對地，HBF write bandwidth 只有每秒八 GB，遠低於 HBM 的一千 GB。Read startup latency 也從零點一微秒增加到二十微秒，write startup 則到兩百五十微秒。Energy 方面 HBF read 是每 bit 六點八 pJ，write 更高到一百 pJ。

所以如果教授問為什麼不能直接把所有東西都放 HBF，這張表就是答案。它很大，但是 write 很慢，而且讀寫 energy 都更高。這些數字是這篇 simulation 使用的假設，不代表已經量到量產 HBF device。

## 第 13 頁｜Shared-Site vs. H³ Service-Time Model

這張是兩種 architecture 在 simulator 裡怎麼估 service time。

Shared-site 假設 HBM 和 HBF 可以走各自的路徑，所以 service time 取兩邊所需時間的最大值。公式裡的 \(m\) 是 HBM stack 數量，因此剩下的 \(8-m\) 就是 HBF stack。

H³ 則比較保守，假設 HBM 和 HBF 的部分是 serialized，因此兩段 service time 直接相加。

不過這裡一定要避免一個誤解。不能看到 H³ 最後 performance 比較好，就說 serialized model 比 parallel model 快。H³ 的關鍵是它有完整八個 HBM stacks，再額外增加八個 HBF stacks；shared-site 則是八個位置在兩種 memory 之間分配。所以兩者的 resource budget 本身就不同。

## 第 14 頁｜Energy Model

如果教授問 energy 是怎麼算的，可以看這張。

作者把 energy 分成三個部分。第一部分是 arithmetic operations，例如不同 GPU operations 的 operation count 乘上每次 operation 的 energy。第二部分是 memory access，把每一層 memory 的 read bytes 和 write bytes 乘八轉成 bits，再乘上對應的 per-bit energy。第三部分則是 communication energy。

這個模型有一個很重要的限制，就是它沒有把 static power 和 background power 完整算進來。所以論文裡看到的 MJ 並不能直接解讀成整台 server 從牆上插座量到的總耗電。

也因此 completion time 降低，不代表整台系統所有 power component 都會同比例下降。這裡比較適合看不同 architecture 或 policy 造成的 relative energy difference。

## 第 15 頁｜Sparse Attention and Index-First Placement

這張補充前面提到的 sparse attention。

系統先讓 indexer 掃描整個 context 的 index，從裡面選出例如 Top-2048 個 token positions。真正 attention 計算時，不需要把整段 KV 都讀進來，只讀這兩千零四十八個位置。

所以這裡的 Top-k 跟 MoE 的 expert Top-k 是兩件完全不同的事情。Sparse attention 的 Top-k 是在 token positions 裡選哪些 KV 要讀；MoE routing 的 Top-k 則是在 experts 裡選 token 要送到哪幾個 expert。

因為 indexer 每次都要看到完整 context，而真正 KV 只讀一個 subset，所以 index 反而是比較 hot 的資料。當 HBM 有 memory pressure 時，作者因此優先把 eligible KV demote 到 HBF，而不是先把 index 移出去。

## 第 16 頁｜TP / EP / DPA: A Four-GPU Example

這張是我為了方便說明 TP、EP 和 DPA 做的四張 GPU 示意，不是論文真正 evaluated configuration。

假設 DPA 讓 GPU0 負責 Request A 的 attention 和 KV，GPU1 負責 Request B，以此類推。所以在 attention 階段，每個 request 的 KV 會有一個主要的 home rank。

但是進入 MoE layer 後，情況就不一樣。假設 Request A 在 GPU0 做完 attention，router 選到 Expert 1 和 Expert 5。如果 Expert 1 在 GPU0，那這部分可以本地計算；如果 Expert 5 在 GPU2，就要把 Request A 的 token activation 傳到 GPU2，算完 expert 之後再把 output 拿回來 combine。

所以 DPA 說的是 request 和 KV 在 attention 階段的 ownership，EP 說的是 expert weights 放在哪張 GPU，而 TP 又是在切同一個大型 tensor operation。三個 parallelism 是不同維度，不應該混在一起。

## 第 17 頁｜Does the Paper Dynamically Swap Experts?

如果教授問這篇有沒有做動態 expert migration，答案是沒有。

這篇每一種 experiment configuration 的 model weight placement 都是固定的。如果使用 split placement，作者先根據 offline routing profile 找出比較常用的 experts，優先固定放在 HBM，剩下 experts 放在 HBF。

Runtime 當然還是會動態做 MoE routing，也就是每個 token 選不同 expert。但如果選到一個 HBF-resident expert，系統只是計算從 HBF 讀取這個 expert weight 的成本，不代表把整個 expert migration 到 HBM。

所以 per-layer expert migration、dynamic expert cache、expert prefetch prediction 這些其實都是我們之後可以考慮的研究方向，但不是這篇 paper 已經做的 contribution。

## 第 18 頁｜Full GLM Table 6

這張是前面 MoE result 的完整 Table 6，主要是教授如果想問某一個 configuration 的 exact number 時再回來看。

左半邊是 1× trace，右半邊是 5× trace，每一邊都有 completion time、modeled energy 和 TPOT。這裡比較的時候要一次固定一個變因，例如固定 5× workload，再比較 HBM-only 和 H³，或者固定 H³ 再比較 TP16 和兩個 TP8 replicas。

前面主報告提到，5× workload 下最快的是 H³、兩個 TP8 replica，而且 weights 放 HBF，completion time 是兩萬四千三百八十五秒。不過 energy 最低的不是這個 configuration，而是 H³、TP16，而且 weights 留在 HBM，energy 是三十七點六二 MJ。

Shared-site 也呈現相同現象：不同 HBM/HBF ratio 在 time 和 energy 上的 ranking 不一樣。所以完整表格最主要就是用來支持前面那個結論，也就是 fastest configuration 跟 lowest-energy configuration 不一定相同。

## 第 19 頁｜Scope and Limitations

最後這張整理這篇的適用範圍。

首先，它主要研究的是 high-throughput serving，也就是希望一整批 workload 可以盡快完成，並不是針對有嚴格 latency SLO 的 online serving。所以前面才會看到 completion time 大幅改善，但是 TPOT 可能變差。

它只考慮 autoregressive decoding，也沒有 speculative decoding。Kernel performance model 有用 H100 和 B200 profiling 校準，但是 HBF device behavior 和某些很大的 batch configuration 還是需要 extrapolation。

另外這篇沒有真正的 production HBF controller，也沒有完整 package power model。Endurance 部分使用簡化的 wear assumption，也不是所有 activation 或 staging write 都被完整建模。

所以這篇最適合拿來回答的是：在不同 memory architecture、placement 和 scheduler 下，HBF capacity 的系統性 trade-off 大概會怎麼變。它不適合被解讀成某個量產 HBF GPU 一定可以得到論文中的 exact speedup、energy saving 或 lifetime。
