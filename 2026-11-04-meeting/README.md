# 2026-11-04 Meeting — Helix

本目錄只整理 Helix 的報告資料。日期已更新為 2026-11-04；前次會議原檔保留作歷史紀錄，本目錄可獨立使用。

## 簡報與講稿

| 用途 | LaTeX | PDF | 講稿 |
|---|---|---|---|
| Helix 報告 | [2026-11-04-Helix.tex](2026-11-04-Helix.tex) | [37 頁 PDF](output/pdf/2026-11-04-Helix.pdf) | [Helix_scripts.md](Helix_scripts.md) |

本目錄保留單一 37 頁 Helix 簡報。此版本移除原來的跨論文比較頁，並清理 roadmap 與結尾的跨論文文字。Helix 實驗本身使用的 baselines 保留，才能正確解讀實驗。

講稿頁碼對齊 PDF。這次以搬整、抽頁為主，沒有擴寫新的研究內容，也尚未重新設定下週口述時間。

## 原文與素材

- [ASPLOS25_Helix.pdf](ASPLOS25_Helix.pdf)：原論文。
- [Helix/](Helix/)：原有 Figure 1–12 PNG 與來源說明。
- `output/overleaf/Helix.zip`：完整版 Overleaf 套件。

## 舊版頁碼對照

| 新版 | 原始來源 |
|---|---|
| 完整版 1–34 | 10/28 Helix 完整版 1–34 |
| 完整版 35–37 | 10/28 Helix 完整版 36–38 |

## 編譯

在本目錄執行：

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=output/pdf 2026-11-04-Helix.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=output/pdf 2026-11-04-Helix.tex
```

Overleaf 套件 `output/overleaf/Helix.zip` 的入口是 `main.tex`，可直接上傳。
