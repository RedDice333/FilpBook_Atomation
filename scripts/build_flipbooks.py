import os
import glob
import shutil
from pdf2image import convert_from_path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT_DIR, "pdfs")
SITE_DIR = os.path.join(ROOT_DIR, "_site")

# 사이트 기본 정보 (원하시는 이름으로 수정 가능)
SITE_NAME = "간행물 서가"
SITE_DESC = "간행물 온라인 플립북 보관소"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>__TITLE__</title>
  <meta property="og:title" content="__TITLE__" />
  <meta property="og:description" content="페이지를 넘겨 간행물을 감상하세요." />
  <meta property="og:image" content="__THUMBNAIL__" />
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
    .header-bar a {
      color: #888;
      text-decoration: none;
      font-size: 13px;
    }
    .header-bar a:hover { color: #fff; }
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
    <a href="../">← 전체 목록</a>
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
  <title>__SITE_NAME__</title>
  <meta property="og:title" content="__SITE_NAME__" />
  <meta property="og:description" content="__SITE_DESC__" />
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 960px;
      margin: 0 auto;
      padding: 40px 20px;
      background: #f8fafc;
      color: #1e293b;
    }
    header {
      margin-bottom: 36px;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 16px;
    }
    h1 { font-size: 26px; font-weight: 700; color: #0f172a; }
    p.desc { font-size: 14px; color: #64748b; margin-top: 6px; }
    .gallery {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 24px;
    }
    .card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      overflow: hidden;
      text-decoration: none;
      color: inherit;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      transition: transform 0.2s, box-shadow 0.2s;
      display: flex;
      flex-direction: column;
    }
    .card:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .card-thumb {
      width: 100%;
      height: 280px;
      background-color: #f1f5f9;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      border-bottom: 1px solid #f1f5f9;
    }
    .card-thumb img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .card-body {
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .card-title {
      font-size: 15px;
      font-weight: 600;
      color: #0f172a;
      line-height: 1.4;
    }
    .card-badge {
      align-self: flex-start;
      background: #eff6ff;
      color: #2563eb;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 500;
    }
  </style>
</head>
<body>
  <header>
    <h1>__SITE_NAME__</h1>
    <p class="desc">__SITE_DESC__</p>
  </header>
  <div class="gallery">
    __ITEM_LIST__
  </div>
</body>
</html>
"""

def main():
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(SITE_DIR, exist_ok=True)

    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    items_info = []

    for pdf_path in sorted(pdf_files, reverse=True):  # 최신 호수가 앞으로 오도록 정렬
        filename = os.path.basename(pdf_path)
        raw_title = os.path.splitext(filename)[0]
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

        first_thumb = "images/page_001.webp"

        html_content = HTML_TEMPLATE.replace("__TITLE__", raw_title)\
                                    .replace("__THUMBNAIL__", first_thumb)\
                                    .replace("__PAGES_HTML__", "\n      ".join(pages_html))\
                                    .replace("__TOTAL_PAGES__", str(total_pages))

        with open(os.path.join(out_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        items_info.append((slug, raw_title, first_thumb, total_pages))

    # 루트 가판대(갤러리 카드형) 목록 생성
    if items_info:
        cards_html = []
        for slug, display_title, thumb, pages in items_info:
            card = f"""
    <a href="{slug}/" class="card">
      <div class="card-thumb">
        <img src="{slug}/{thumb}" alt="{display_title}" loading="lazy">
      </div>
      <div class="card-body">
        <span class="card-title">{display_title}</span>
        <span class="card-badge">{pages}쪽</span>
      </div>
    </a>"""
            cards_html.append(card)
        items_html = "\n".join(cards_html)
    else:
        items_html = '<p style="color:#888;">등록된 간행물이 없습니다. pdfs 폴더에 PDF를 업로드해 주세요.</p>'

    root_html = INDEX_TEMPLATE.replace("__SITE_NAME__", SITE_NAME)\
                              .replace("__SITE_DESC__", SITE_DESC)\
                              .replace("__ITEM_LIST__", items_html)

    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_html)

    print("전체 빌드 완료!")

if __name__ == "__main__":
    main()