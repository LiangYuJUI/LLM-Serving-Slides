# ThunderServe 與 Hetis：Marp 簡報

依目前兩份 `.tex` 的實際 frame 順序重新轉換：ThunderServe **44 頁**、Hetis **39 頁**。新增表格、公式與 pseudocode 均保留；以 HTML/CSS 重建配色與欄位，版面與 Beamer 略有不同。原始 LaTeX 和中文講稿未修改。

| 簡報 | Markdown | PDF | 離線 HTML |
| --- | --- | --- | --- |
| ThunderServe | `2026-10-21-ThunderServe.md` | `ThunderServe-marp.pdf` | `ThunderServe.html` |
| Hetis | `2026-10-21-Hetis.md` | `Hetis-marp.pdf` | `Hetis.html` |

## 閱讀與播放

PDF 可直接閱讀。用 Chrome 開啟 HTML 可播放，不需要安裝 LaTeX、Node.js 或 Marp，也不需要網路。圖片、數學公式和播放器已包含在 HTML，可單獨複製到其他電腦。

- 左右方向鍵：換頁。
- `P`：presenter view，顯示中文講稿；瀏覽器需允許開啟此視窗。
- `O`：投影片總覽。

HTML 包含講稿，分享 HTML 也會分享 notes。PDF 僅包含投影片。

## 修改 Markdown 或講稿後重新匯出

只有重新匯出時才需要 Node.js、Marp；匯出 PDF 還需要本機 Chrome、Edge 或 Firefox。**不需要 LaTeX compiler。**

在這個 `marp` 資料夾執行：

```sh
npm ci              # 首次安裝；工作區已有依賴可跳過
npm run build:all   # 兩份 HTML + 兩份 PDF
```

也可以用 `npm run build` 只產生 HTML，或 `npm run pdf` 只產生 PDF。

`build.mjs` 按投影片標題對應上層 `ThunderServe_scripts.md` 與 `Hetis_scripts.md`，避免插頁後講稿錯位。目前 83 頁皆找到對應講稿。若上層沒有講稿，會查找本資料夾的同名檔。

Markdown 的 `---` 分頁；`#` 是頁面標題；`$...$`／`$$...$$` 是行內／獨立公式；少量 `<div>` 負責雙欄與卡片。樣式內嵌在各檔案的 YAML。圖片位於 `assets/`：ThunderServe 使用原 PNG，Hetis 將原 vector PDF 圖轉成 SVG。

在 Marp for VS Code 預覽時，需允許 HTML 排版。

## LaTeX 更新後重新同步

`convert_tex.py` 是針對這兩份 Beamer 模板的轉換器，從上層 `.tex` 讀取內容，依實際 frame 順序產生 Markdown。它不修改 `.tex` 或講稿，遇到未支援的文字命令會報錯。

需要 Python、Pillow 和 PyMuPDF（可安裝在 virtual environment）。使用具備這些套件的 Python 執行：

```sh
python convert_tex.py
npm run build:all
```

**重新轉換會覆寫兩份 Markdown。** 若以 `.tex` 為主版本，先修改 `.tex` 再轉換；若直接改 Markdown，僅執行 `npm run build:all`。樣式來源為 `theme.css`，轉換時會內嵌到 Markdown。

`conversion-manifest.json` 記錄轉換來源的 SHA-256、頁數和標題，供核對版本；每次同步後仍應查看密集表格及公式頁的版面。
