"""HTML 轉 PDF 工具 — 使用 Playwright 將本地 HTML 檔案轉換為 PDF

支援兩種模式：
1. 一般 HTML：直接使用 Chromium PDF 引擎輸出
2. Google 簡報 HTML：透過 Google embed 模式逐頁截圖後組合成 PDF
   （自動載入完整背景、圖片等遠端資源）
"""

import argparse
import io
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote

from PIL import Image
from playwright.sync_api import sync_playwright


def _extract_presentation_id(html_path: Path) -> str | None:
    """從本地 Google 簡報 HTML 中提取 presentation ID"""
    with open(html_path, "r", encoding="utf-8") as f:
        head = f.read(10000)
    match = re.search(r"/presentation/(?:u/\d+/)?d/([^/\s\"']+)/", head)
    if match:
        return unquote(match.group(1))
    return None


def _is_slide_html(page) -> bool:
    """偵測是否為 Google 簡報匯出的 HTML"""
    return page.evaluate("document.querySelectorAll('.slide-content').length") > 0


def _get_slide_count_from_html(page) -> int:
    return page.evaluate("document.querySelectorAll('.slide-content').length")


def _convert_google_slides(p, presentation_id: str, slide_count: int, pdf_path: Path) -> None:
    """透過 Google embed 模式逐頁截圖，組合成 PDF"""
    embed_url = (
        f"https://docs.google.com/presentation/d/{presentation_id}/embed?start=false&loop=false"
    )
    print("使用 Google embed 模式載入完整背景...")

    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto(embed_url, wait_until="networkidle", timeout=30000)

    # 按 Home 確保在第一頁
    page.keyboard.press("Home")
    time.sleep(0.5)

    images: list[Image.Image] = []
    for i in range(slide_count):
        if i > 0:
            page.keyboard.press("ArrowRight")
            time.sleep(0.5)

        # 截圖整個 viewport（投影片剛好 1280x720）
        screenshot = page.screenshot(type="png")
        img = Image.open(io.BytesIO(screenshot)).convert("RGB")

        # 裁掉底部控制列（約 30px）
        toolbar_h = 30
        img = img.crop((0, 0, img.width, img.height - toolbar_h))
        images.append(img)
        print(f"  截圖投影片 {i + 1}/{slide_count}")

    browser.close()

    if not images:
        raise RuntimeError("未擷取到任何投影片")

    images[0].save(str(pdf_path), "PDF", save_all=True, append_images=images[1:])


def _convert_slides_local(page, pdf_path: Path) -> None:
    """本地模式：逐張投影片截圖（無背景圖片）"""
    slide_count = page.evaluate("document.querySelectorAll('.slide-content').length")
    print(f"偵測到 {slide_count} 張投影片，逐頁截圖中...")

    images: list[Image.Image] = []
    for i in range(slide_count):
        screenshot = page.evaluate_handle(
            f"document.querySelectorAll('.slide-content')[{i}]"
        ).screenshot(type="png")
        img = Image.open(io.BytesIO(screenshot)).convert("RGB")
        images.append(img)

    if not images:
        raise RuntimeError("未擷取到任何投影片")

    images[0].save(str(pdf_path), "PDF", save_all=True, append_images=images[1:])


def _convert_normal(page, pdf_path: Path, landscape: bool) -> None:
    """一般 HTML 使用 Chromium 內建 PDF 引擎"""
    page.pdf(
        path=str(pdf_path),
        format="A4",
        landscape=landscape,
        print_background=True,
        margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
    )


def convert(html_path: str, output: str | None = None, landscape: bool = False) -> Path:
    html_file = Path(html_path).resolve()
    if not html_file.exists():
        raise FileNotFoundError(f"找不到檔案: {html_file}")

    pdf_path = Path(output).resolve() if output else html_file.with_suffix(".pdf")

    # 先偵測是否為 Google 簡報
    presentation_id = _extract_presentation_id(html_file)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 960})
        page.goto(html_file.as_uri(), wait_until="networkidle")
        is_slides = _is_slide_html(page)
        slide_count = _get_slide_count_from_html(page) if is_slides else 0

        if is_slides and presentation_id:
            browser.close()
            _convert_google_slides(p, presentation_id, slide_count, pdf_path)
        elif is_slides:
            print("(無法取得 Google 簡報 ID，使用本地模式)")
            _convert_slides_local(page, pdf_path)
            browser.close()
        else:
            _convert_normal(page, pdf_path, landscape)
            browser.close()

    print(f"已轉換: {pdf_path}")
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="HTML 轉 PDF 工具")
    parser.add_argument("input", help="HTML 檔案路徑")
    parser.add_argument("-o", "--output", help="輸出 PDF 路徑 (預設與輸入檔同名)")
    parser.add_argument("-l", "--landscape", action="store_true", help="橫向輸出")
    args = parser.parse_args()

    try:
        convert(args.input, args.output, args.landscape)
    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
