# 2026-10-27 Meeting

下次 meeting 真正要報告的是 **15–20 分鐘** combined deck，不是兩份 38 頁 reference deck。

`2026-10-27-Meeting-Main.tex` 是正式報告：約 **13 張 main slides**（預算口述約 17–18 分鐘）加上 appendix。故事線是 Summary → Why → Method → Experiments as questions → Conclusion。

`2026-10-27-Helix.tex` 與 `2026-10-27-Tessera.tex` 是完整 reference / Q&A backup，各 **38 頁**。不要把它們當成正式報告版本，也不要為了報告時間去刪改它們。

事實來源是同目錄的本地論文 PDF。視覺沿用 2026-10-21 meeting 的 Light Madrid 風格。

最後驗證日期：2026-10-22。

## 正式報告

| 用途 | 簡報 | 講稿 | 頁數 |
|---|---|---|---|
| 15–20 分鐘 meeting | `2026-10-27-Meeting-Main.tex` | `Meeting-Main_scripts.md` | 13 main + appendix |

- PDF：`output/pdf/2026-10-27-Meeting-Main.pdf`
- Overleaf：`output/overleaf/Meeting-Main.zip`（根目錄 `main.tex`）
- 頁腳 `Main n/13` 是正式報告；`Backup PDF n` 不計入報告時間。
- 講稿 `## 第 XX 頁` 對齊 PDF 實際頁碼。

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Meeting-Main.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Meeting-Main.tex
```

## 完整 reference decks

| 論文 | 簡報 | 講稿 | 頁數 |
|---|---|---|---|
| Helix (ASPLOS 2025) | `2026-10-27-Helix.tex` | `Helix_scripts.md` | 38 |
| Tessera (arXiv:2604.10180v2) | `2026-10-27-Tessera.tex` | `Tessera_scripts.md` | 38 |

## 來源

- `ASPLOS25_Helix.pdf`
- `Arxiv26_Tessera.pdf`
- `Helix/`：Figure 1–12 的 PNG，檔名沒有 `_with_caption`
- `Tessera/`：Figure 1–11 的 PNG。`Tessera_Figures_600dpi.zip` 只是素材封裝，簡報不引用它

## 編譯

在本目錄執行 pdfLaTeX 兩次：

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Helix.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Helix.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Tessera.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-Tessera.tex
```

## 輸出

- `output/pdf/2026-10-27-Helix.pdf`
- `output/pdf/2026-10-27-Tessera.pdf`
- `output/overleaf/Helix.zip`
- `output/overleaf/Tessera.zip`

Overleaf zip 的根目錄是 `main.tex`，並只附上該簡報實際用到的 PNG。解壓後在該目錄執行兩次 `pdflatex main.tex` 即可。

本目錄沒有 Marp 或 HTML。正式 meeting 用上面的 Meeting-Main，不另做第二套版型。


## HBF：2026-10-27 短篇 paper summary

新增獨立 **9 頁** HBF 簡報（8 頁主報告 + 結論後的 1 頁來源整理），目標口述約 9 分鐘；不沿用 Helix/Tessera 的 38 頁結構。驗證日期：2026-10-22。

- LaTeX：`2026-10-27-HBF.tex`
- 繁體中文講稿：`HBF_scripts.md`
- PDF：`output/pdf/2026-10-27-HBF.pdf`
- Overleaf：`output/overleaf/HBF.zip`（根目錄 `main.tex`）
- 原文：`Arxiv26_HBF_v4.pdf`，取自 https://arxiv.org/pdf/2608.11668v4
- 使用素材：`HBF/`，原文 Figure 4、Table 8、Figure 10(a)、Figure 12 的直接擷取圖
- 素材 mapping、來源與 review 說明：`HBF/README.md`

既有 `CharacterizingHBFforLLMServing/` 六張圖均已逐張檢視，但其內容與目標 paper v4 的 Figure 1–6 不同，故全部保留原檔但未納入簡報。

```bash
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-HBF.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-10-27-HBF.tex
pdfinfo 2026-10-27-HBF.pdf
```
