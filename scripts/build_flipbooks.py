import os
import glob
import json
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
  <title>{title}</title>
  <script src="https://cdn.jsdelivr.net/npm/page-flip/dist/js/page-flip.browser.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: #1e1e1e;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .header-bar {
      padding: 10px 16px;
      background: #111;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 14px;
      font-weight: 600;
      border-bottom: 1px solid #333;
    }
    .container {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 10px;
      overflow: hidden;
      position: relative;
    }
    .flip-book {
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      background: #2b2b2b;
      visibility: hidden;
    }
    .page {
      background-color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }
    .page img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      user-select: none;
      -webkit-user-drag: none;
    }
    .controls {
      padding: 10px;
      background: #111;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 16px;
      border-top: 1px solid #333;
    }
    .btn {
      background: #333;
      border: 1px solid #555;
      color: #fff;
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      transition: background 0.2s;
    }
    .btn:hover { background: #444; }
    .page-indicator {
      font-size: 13px;
      color: #bbb;
      min-width: 80px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="header-bar">
    <span>{title}</span>
    <span style="color: #888; font-size: 12px;">마우스 드래그 또는 버튼으로 넘기기</span>
  </div>
  <div class="container">
    <div id="flipbook" class="flip-book">
      {pages_html}
    </div>
  </div>
  <div class="controls">
    <button class="btn" id="btnPrev">이전</button>
    <span class="page-indicator" id="pageNumber">1 / {total_pages}</span>
    <button class="btn" id="btnNext">다음</button>
  </div>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const el = document.getElementById('flipbook');
      const pageFlip = new St.PageFlip(el, {
        width: 550,
        height: 770,
        size: "stretch",
        minWidth: 315,
        maxWidth: 1000,
        minHeight: 420,
        maxHeight: 1400,
        maxShadowOpacity: 0.5,
        showCover: true,
        mobileScrollSupport: false
      });

      pageFlip.loadFromHTML(document.querySelectorAll('.page'));
      el.style.visibility = 'visible';

      const pageNumEl = document.getElementById('pageNumber');
      function updatePageDisplay() {
        const current = pageFlip.getCurrentPageIndex() + 1;
        pageNumEl.textContent = `${current} / {total_pages}`;
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
    {item_list}
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
        slug = os.path.splitext(filename)[0]
        out_folder = os.path.join(SITE_DIR, slug)
        images_folder = os.path.join(out_folder, "images")
        os.makedirs(images_folder, exist_ok=True)

        print(f"변환 중: {filename} -> {slug}")
        # Convert PDF pages to WebP/PNG images
        images = convert_from_path(pdf_path, dpi=130)
        total_pages = len(images)
        pages_html = []

        for idx, img in enumerate(images):
            img_name = f"page_{idx+1:03d}.webp"
            img_full_path = os.path.join(images_folder, img_name)
            img.save(img_full_path, "WEBP", quality=85)
            pages_html.append(f'<div class="page"><img src="images/{img_name}" alt="페이지 {idx+1}"></div>')

        html_content = HTML_TEMPLATE.format(
            title=slug,
            pages_html="\n      ".join(pages_html),
            total_pages=total_pages
        )

        with open(os.path.join(out_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        items_info.append((slug, total_pages))

    # Create root index.html
    if items_info:
        items_html = "\n".join([
            f'<li><a href="{slug}/" target="_blank">{slug}</a><span class="badge">{pages}쪽</span></li>'
            for slug, pages in items_info
        ])
    else:
        items_html = '<li>등록된 간행물이 없습니다. pdfs 폴더에 PDF를 업로드해 주세요.</li>'

    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE.format(item_list=items_html))

    print("전체 빌드 완료!")

if __name__ == "__main__":
    main()
