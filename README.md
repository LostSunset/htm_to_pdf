# htm-to-pdf

[![CI](https://github.com/LostSunset/htm_to_pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/LostSunset/htm_to_pdf/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/LostSunset/htm_to_pdf)](https://github.com/LostSunset/htm_to_pdf/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LostSunset/htm_to_pdf)](https://github.com/LostSunset/htm_to_pdf/network)
[![GitHub issues](https://img.shields.io/github/issues/LostSunset/htm_to_pdf)](https://github.com/LostSunset/htm_to_pdf/issues)

> HTML 轉 PDF 工具 — 使用 Playwright 將本地 HTML 檔案轉換為 PDF，**完整支援 Google 簡報背景渲染**。

## 特色

- **Google 簡報完整背景** — 自動偵測 Google Slides HTML，透過 embed 模式載入完整背景、Logo 和設計元素
- **一般 HTML 支援** — 使用 Chromium PDF 引擎，支援 A4 格式、橫向輸出、列印背景色
- **零配置** — 自動偵測 HTML 類型，選擇最佳轉換策略
- **中文支援** — 完整支援正體中文檔名和內容

## 安裝

```bash
# 使用 uv（推薦）
uv venv .venv
uv pip install playwright Pillow
uv run playwright install chromium
```

## 使用方式

### Step 1：取得 Google 簡報的 HTML

當 Google 簡報被設為「僅供檢視」無法下載時，可以透過修改網址來取得完整 HTML：

1. 開啟簡報，網址通常為：
   ```
   https://docs.google.com/presentation/d/XXXXXXX/preview?slide=iYYYYYY
   ```

2. 將網址改為 `htmlpresent`：
   ```
   https://docs.google.com/presentation/d/XXXXXXX/htmlpresent
   ```

3. 在瀏覽器按 `Ctrl+S`（另存新檔），選擇「**網頁，完整**」儲存為 `.html` 檔案

### Step 2：轉換為 PDF

```bash
# 基本用法 — 輸出同名 PDF
python htm_to_pdf.py "檔案.html"

# 指定輸出路徑
python htm_to_pdf.py "檔案.html" -o output.pdf

# 橫向輸出（一般 HTML）
python htm_to_pdf.py "檔案.html" -l
```

## 運作原理

```
輸入 HTML
    │
    ├─ 偵測到 .slide-content？
    │   ├─ 是 → 提取 Google Presentation ID
    │   │       ├─ 成功 → Google embed 模式逐頁截圖 → PDF
    │   │       └─ 失敗 → 本地模式逐頁截圖 → PDF
    │   └─ 否 → Chromium PDF 引擎直接輸出
    │
    └─ 輸出 PDF
```

### Google 簡報模式

從瀏覽器「另存新檔」的 Google Slides HTML，其背景圖片存放在 Google 伺服器需要認證。本工具透過 Google Slides 的公開 `/embed` 端點載入完整簡報，逐頁截圖後組合成 PDF，保留所有背景、Logo 和設計元素。

## 系統需求

- Python 3.11+
- Playwright + Chromium
- Pillow

## 授權

[MIT License](LICENSE)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=LostSunset/htm_to_pdf&type=Date)](https://star-history.com/#LostSunset/htm_to_pdf&Date)
