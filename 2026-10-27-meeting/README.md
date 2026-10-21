# 2026-10-27 Meeting

Helix 與 Tessera 的獨立 Beamer 簡報。事實來源是同目錄的兩份本地論文 PDF。視覺沿用 2026-10-21 meeting 的 Light Madrid 風格。

最後驗證日期：2026-10-21。兩份投影片編譯後都是 **38 頁**。講稿 `## 第 XX 頁` 的標題與 slide title 逐頁對齊。

## 簡報與講稿

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

本輪沒有 Marp、HTML 或合併版。
