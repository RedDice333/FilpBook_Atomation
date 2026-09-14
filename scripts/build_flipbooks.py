import os
import glob
import shutil
from pdf2image import convert_from_path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT_DIR, "pdfs")
SITE_DIR = os.path.join(ROOT_DIR, "_site")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>__TITLE__</title>
  <script src="https://cdn.jsdelivr.net/npm/page-flip/dist/js/page-flip.browser.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: #1a1a1a;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }
    .header-bar {
      height: 48px;
      padding: 0 16px;
      background: #111;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 14px;
      font-weight: 600;
      border-bottom: 1px solid #2a2a2a;
      flex-shrink: 0;
    }
    .container {
      flex: 1;
      width: 100%;
      height: calc(100vh - 100px);
      display: flex;
      justify-content: center;
      align-items: center;
      position: relative;
      overflow: hidden;
      padding: 10px;
    }
    .flip-book {
      box-shadow: 0 12px 36px rgba(0,0,0,0.5);
      visibility: hidden;
      transform-style: preserve-3d;
      backface-visibility: hidden;
      will-change: transform;
    }
    .page {
      background-color: #ffffff;
      width: 100%;
      height: 100%;
      overflow: hidden;
      box-shadow: inset 0 0 15px rgba(0,0,0,0.05);
    }
    .page img {
      width: 100%;
      height: 100%;
      object-fit: fill;
      display: block;
      user-select: none;
      -webkit-user-drag: none;
    }
    .controls {
      height: 52px;
      padding: 0 16px;
      background: #111;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 20px;
      border-top: 1px solid #2a2a2a;
      flex-shrink: 0;
    }
    .btn {
      background: #2a2a2a;
      border: 1px solid #444;
      color: #fff;
      padding: 6px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      transition: all 0.2s;
    }
    .btn:hover { background: #3a3a3a; }
    .page-indicator {
      font-size: 13px;
      color: #aaa;
      min-width: 80px;
      text-align: center;
      font-variant-numeric: tabular-nums;
    }
  </style>
</head>
<body>
  <div class="header-bar">
    <span>__TITLE__</span>
    <span style="color: #777; font-size: 12px;">모바일은 가로 모드를 권장합니다</span>
  </div>
  <div class="container" id="bookContainer">
    <div id="flipbook" class="flip-book">
      __PAGES_HTML__
    </div>
  </div>
  <div class="controls">
    <button class="btn" id="btnPrev">이전</button>
    <span class="page-indicator" id="pageNumber">1 / __TOTAL_PAGES__</span>
    <button class="btn" id="btnNext">다음</button>
  </div>

  <script>
    window.addEventListener('load', function() {
      const el = document.getElementById('flipbook');
      const baseWidth = 550;
      const baseHeight = 778;

      const pageFlip = new St.PageFlip(el, {
        width: baseWidth,
        height: baseHeight,
        size: "stretch",
        minWidth: 280,
        maxWidth: 900,
        minHeight: 400,
        maxHeight: 1270,
        drawShadow: true,
        maxShadowOpacity: 0.4,
        showCover: true,
        usePortrait: true,
        mobileScrollSupport: false,
        useMouseEvents: true,
        flippingTime: 700
      });

      pageFlip.loadFromHTML(document.querySelectorAll('.page'));
      el.style.visibility = 'visible';

      const pageNumEl = document.getElementById('pageNumber');
      function updatePageDisplay() {
        const current = pageFlip.getCurrentPageIndex() + 1;
        pageNumEl.textContent = current + ' / __TOTAL_PAGES__';
      }

      pageFlip.on('flip', updatePageDisplay);

      document.getElementById('btnPrev').addEventListener('click', () => pageFlip.flipPrev());
      document.getElementById('btnNext').addEventListener('click', () => pageFlip.flipNext());
    });
  </script>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>간행물 플립북 보관소</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 800px;
      margin: 40px auto;
      padding: 0 20px;
      background: #f8fafc;
      color: #334155;
    }
    h1 { font-size: 24px; margin-bottom: 20px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
    ul { list-style: none; padding: 0; }
    li {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      margin-bottom: 12px;
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.2s;
    }
    li:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    a {
      text-decoration: none;
      color: #2563eb;
      font-weight: 600;
      font-size: 16px;
    }
    .badge {
      background: #eff6ff;
      color: #1d4ed8;
      font-size: 12px;
      padding: 4px 8px;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <h1>간행물 모아보기</h1>
  <ul>
    __ITEM_LIST__
  </ul>
</body>
</html>
"""

def main():
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(SITE_DIR, exist_ok=True)

    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    items_info = []

    for pdf_path in sorted(pdf_files):
        filename = os.path.basename(pdf_path)
        raw_title = os.path.splitext(filename)[0]
        
        # 공백(띄어쓰기)을 하이픈(-)으로 치환하여 메신저 링크 끊김 방지
        slug = raw_title.replace(" ", "-")

        out_folder = os.path.join(SITE_DIR, slug)
        images_folder = os.path.join(out_folder, "images")
        os.makedirs(images_folder, exist_ok=True)

        print(f"변환 중: {filename} -> {slug}")
        images = convert_from_path(pdf_path, dpi=130)
        total_pages = len(images)
        pages_html = []

        for idx, img in enumerate(images):
            img_name = f"page_{idx+1:03d}.webp"
            img_full_path = os.path.join(images_folder, img_name)
            img.save(img_full_path, "WEBP", quality=85)
            pages_html.append(f'<div class="page"><img src="images/{img_name}" alt="페이지 {idx+1}"></div>')

        # 화면 상단 타이틀은 원본 파일명(raw_title)을 유지하고 URL 폴더는 slug로 생성
        html_content = HTML_TEMPLATE.replace("__TITLE__", raw_title)\
                                    .replace("__PAGES_HTML__", "\n      ".join(pages_html))\
                                    .replace("__TOTAL_PAGES__", str(total_pages))

        with open(os.path.join(out_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        items_info.append((slug, raw_title, total_pages))

    # 루트 index.html 목록 생성
    if items_info:
        items_html = "\n".join([
            f'<li><a href="{slug}/" target="_blank">{display_title}</a><span class="badge">{pages}쪽</span></li>'
            for slug, display_title, pages in items_info
        ])
    else:
        items_html = '<li>등록된 간행물이 없습니다. pdfs 폴더에 PDF를 업로드해 주세요.</li>'

    root_html = INDEX_TEMPLATE.replace("__ITEM_LIST__", items_html)
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_html)

    print("전체 빌드 완료!")

if __name__ == "__main__":
    main()