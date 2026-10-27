# 2026-10-28 Meeting

Meeting 日期是 **2026-10-28（Wednesday）**。正式報告規劃 **30 分鐘**，另外保留約 **10 分鐘 HBF 備用**。目前 Main deck 只完成其中一部分。

| Section | Planned | Status |
|---|---|---|
| ThunderServe summary | 4 min | Done. Four frames in `ThunderServe/ThunderServe-summary-frames.tex` |
| Hetis summary | 4 min | Not implemented. No placeholder slides |
| ThunderServe vs. Hetis | 2 min | Not implemented. No placeholder slides |
| Helix + Tessera | 10 + 10 min planned | Existing main slides kept. Speaker notes still total about 17.2 min and were not recut |
| Additional HBF papers | Extra 10 min | Separate decks kept. Not counted in the 30 minutes |

`2026-10-28-Meeting-Main.tex` 目前是 **17 張 main slides**（封面 + ThunderServe 4 張 + 既有 Helix／Tessera）加上 appendix。已完成內容的口述預算是 **21.5 分鐘**。頁腳 `Main n/17` 才算正式報告；`Backup PDF n` 與獨立 HBF deck 都不計入。

`2026-10-28-Helix.tex` 與 `2026-10-28-Tessera.tex` 仍是完整 reference / Q&A backup，各 **38 頁**。

ThunderServe 事實來源是 `../2026-10-21-meeting/MLSys25_Thunderserve.pdf`。投影片用的 Figure 1、3、9 是該目錄 `ThunderServe/` 原圖的複本，見 `ThunderServe/SOURCE.txt`。Helix／Tessera／HBF 仍用本目錄的本地論文與圖檔。視覺沿用 2026-10-21 meeting 的 Light Madrid 風格。

ThunderServe summary 驗證日期：2026-10-27。Helix／Tessera 前一輪驗證日期仍是 2026-10-22。

## 正式報告

| 用途 | 簡報 | 講稿 | 頁數 |
|---|---|---|---|
| 目前完成的 main deck | `2026-10-28-Meeting-Main.tex` | `Meeting-Main_scripts.md` | 17 main + appendix，共 42 頁 |
| ThunderServe 四頁講稿 | 同上，`\input` | `ThunderServe_scripts.md` | Main PDF 第 02–05 頁 |

- PDF：`output/pdf/2026-10-28-Meeting-Main.pdf`
- 四頁預覽：`output/pdf/2026-10-28-ThunderServe-Summary.pdf`
- Overleaf：`output/overleaf/Meeting-Main.zip`（根目錄 `main.tex`，含 `ThunderServe/`）
- 頁腳 `Main n/17` 是正式報告；`Backup PDF n` 不計入報告時間。
- 講稿 `## 第 XX 頁` 對齊 PDF 實際頁碼。

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Meeting-Main.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Meeting-Main.tex
```

## 完整 reference decks

| 論文 | 簡報 | 講稿 | 頁數 |
|---|---|---|---|
| Helix (ASPLOS 2025) | `2026-10-28-Helix.tex` | `Helix_scripts.md` | 38 |
| Tessera (arXiv:2604.10180v2) | `2026-10-28-Tessera.tex` | `Tessera_scripts.md` | 38 |

## 來源

- `ASPLOS25_Helix.pdf`
- `Arxiv26_Tessera.pdf`
- `Helix/`：Figure 1–12 的 PNG，檔名沒有 `_with_caption`
- `Tessera/`：Figure 1–11 的 PNG。`Tessera_Figures_600dpi.zip` 只是素材封裝，簡報不引用它

## 編譯

在本目錄執行 pdfLaTeX 兩次：

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Helix.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Helix.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Tessera.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Tessera.tex
```

## 輸出

- `output/pdf/2026-10-28-Helix.pdf`
- `output/pdf/2026-10-28-Tessera.pdf`
- `output/overleaf/Helix.zip`
- `output/overleaf/Tessera.zip`

Overleaf zip 的根目錄是 `main.tex`，並只附上該簡報實際用到的 PNG。解壓後在該目錄執行兩次 `pdflatex main.tex` 即可。

本目錄沒有 Marp 或 HTML。正式 meeting 用上面的 Meeting-Main，不另做第二套版型。


## HBF：2026-10-28 短篇 paper summary

新增獨立 **9 頁** HBF 簡報（8 頁主報告 + 結論後的 1 頁來源整理），目標口述約 9 分鐘；不沿用 Helix/Tessera 的 38 頁結構。HBF figure refresh 驗證日期：2026-10-23。

- LaTeX：`2026-10-28-HBF.tex`
- 繁體中文講稿：`HBF_scripts.md`
- PDF：`output/pdf/2026-10-28-HBF.pdf`
- Overleaf：`output/overleaf/HBF.zip`（根目錄 `main.tex`）
- 原文：`Arxiv26_HBF_v4.pdf`，取自 https://arxiv.org/pdf/2608.11668v4
- 使用素材：`CharacterizationOfHBFforKVCentricLLMServing/`，原文 Figure 3（動機）、1（架構）、4（C1）、10 + 11（C3）、12（結論）的完整擷取圖
- Table 8（C2）使用 native LaTeX table，保留 write/read ratio、reads/write、prefix hit rate 三列
- Figure 2、5–9 保留作未來 Q&A 素材；短版 deck 不引用。Overleaf zip 僅包含實際使用的六張圖與 `main.tex`。

既有 `CharacterizingHBFforLLMServing/` 六張圖均已逐張檢視，但其內容與目標 paper v4 的 Figure 1–6 不同，故全部保留原檔但未納入簡報。

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-HBF.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-HBF.tex
pdfinfo 2026-10-28-HBF.pdf
```

## Characterizing High Bandwidth Flash for LLM Serving

獨立的 focused paper presentation，**13 張 main slides + 8 張 appendix，共 21 頁**。主線講稿約 **16–18 分鐘**，附錄供 Q&A，不計入正式報告時間。

- Main TeX：`2026-10-28-Characterizing-HBF.tex`
- 繁體中文講稿：`Characterizing-HBF_scripts.md`（第 01–21 頁對齊 PDF）
- PDF：`output/pdf/2026-10-28-Characterizing-HBF.pdf`
- Overleaf package：`output/overleaf/Characterizing-HBF.zip`（根目錄 `main.tex`，僅附 TeX 實際引用的五張裁切圖）
- Source：Zack Yu et al., *Characterizing High Bandwidth Flash for LLM Serving*, arXiv:2609.39131v2, 5 Oct 2026。repo 沒有本篇原始 PDF；本次以使用者提供的 paper facts、數字與既有 Fig. 1–6 為依據，未宣稱核讀不存在的原文，也未補猜未提供的章節編號。
- 圖片來源：`CharacterizingHBFforLLMServing/`；與另一篇 *HBF Sucks?*（arXiv:2608.11668v4）及其素材完全分開。
- 投影片實際引用：`CharacterizingHBFforLLMServing/slides/Fig01.png` 至 `Fig05.png`。`slides/Fig06.png` 與原始 `CharacterizingHBFforLLMServing_Fig06.png` 仍留在 repo，供 reference 或未來 Q&A；主報告改以 Table 6 的六個 Figure 6 數據點呈現，TeX 不再引用 Fig06。原始六張圖映射正確，保留原檔；衍生圖只裁去下方圖說，保留座標、面板標籤及圖例，不拉伸。
- 原圖解析度依序：1026×784、1018×876、1022×1564、1022×801、1022×805、2122×1142。裁切圖高度依序為 550、560、1300、540、540、965 px，寬度不變；裁切框左上角均為 (0,0)。
- 標題頁算 Main 1/13；結論為 Main 13/13；`\appendix` 之後顯示 Backup PDF 14–21。
- Q3 拆成三頁：第 10 頁是每一層 DPA attention 再到 TP/EP MoE 的流程；第 11 頁是 Figure 6 六個點的數字表；第 12 頁是 improvement trade-off。第 13 頁收能量機制與結論。TP 只寫成 simulator 的 tensor-parallel computation / communication abstraction，不宣稱論文未給出的 per-expert tensor-to-rank mapping。
- 數據限制：能耗不含靜態／背景功率；壽命為假設下估計；Table 7 的淨值保留提供的原數字，分項四捨五入後可能與淨值差 0.01 百分點。

在本目錄編譯並更新 PDF：

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Characterizing-HBF.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-28-Characterizing-HBF.tex
cp 2026-10-28-Characterizing-HBF.pdf output/pdf/
pdfinfo output/pdf/2026-10-28-Characterizing-HBF.pdf
```

驗證日期：2026-10-24。21 頁皆渲染為 PNG 並完成視覺檢查；講稿標題與 PDF 頁碼核對。Overleaf zip 在乾淨暫存目錄解壓後，pdfLaTeX 兩次編譯為 21 頁。
