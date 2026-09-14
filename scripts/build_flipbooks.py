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
      background-color: #121212;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .header-bar {
      height: 48px;
      padding: 0 16px;
      background: #1e1e1e;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #333;
      flex-shrink: 0;
    }
    .back-btn {
      color: #aaa;
      text-decoration: none;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .back-btn:hover { color: #fff; }
    .header-title {
      font-size: 15px;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 60%;
    }
    .container {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 12px;
      overflow: hidden;
      position: relative;
    }
    .flip-book {
      max-width: 100%;
      max-height: 100%;
      box-shadow: 0 12px 36px rgba(0,0,0,0.8);
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
      height: 56px;
      padding: 0 16px;
      background: #1e1e1e;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 12px;
      border-top: 1px solid #333;
      flex-shrink: 0;
    }
    .btn {
      background: #2a2a2a;
      border: 1px solid #444;
      color: #fff;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
    }
    .btn:hover { background: #3a3a3a; }
    .page-jump-box {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: #bbb;
    }
    .page-jump-input {
      width: 48px;
      background: #111;
      border: 1px solid #444;
      color: #fff;
      text-align: center;
      padding: 4px;
      border-radius: 4px;
      font-size: 13px;
    }
    .page-jump-input:focus {
      outline: 1px solid #3b82f6;
    }
  </style>
</head>
<body>
  <div class="header-bar">
    <a href="../" class="back-btn">‹ 서가 목록</a>
    <span class="header-title">__DISPLAY_TITLE__</span>
    <span style="font-size: 12px; color: #777;">드래그로 넘김</span>
  </div>

  <div class="container" id="bookContainer">
    <div id="flipbook" class="flip-book">
      __PAGES_HTML__
    </div>
  </div>

  <div class="controls">
    <button class="btn" id="btnPrev">‹ 이전</button>
    <div class="page-jump-box">
      <input type="number" id="pageInput" class="page-jump-input" min="1" max="__TOTAL_PAGES__" value="1">
      <span>/ __TOTAL_PAGES__</span>
      <button class="btn" id="btnJump" style="padding: 4px 8px; font-size: 11px;">이동</button>
    </div>
    <button class="btn" id="btnNext">다음 ›</button>
  </div>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const container = document.getElementById('bookContainer');
      const el = document.getElementById('flipbook');
      const totalPages = __TOTAL_PAGES__;

      // 뷰포트 비율에 맞춘 동적 크기 계산 (상하단 잘림 방지)
      const containerH = container.clientHeight;
      const baseH = Math.max(400, containerH - 20);
      const baseW = Math.round(baseH * 0.707); // 3:4 ~ A4 비율

      const pageFlip = new St.PageFlip(el, {
        width: baseW,
        height: baseH,
        size: "stretch",
        minWidth: 280,
        maxWidth: 1200,
        minHeight: 380,
        maxHeight: 1600,
        maxShadowOpacity: 0.3,
        showCover: true,
        mobileScrollSupport: false,
        hoverPageFlip: false // 2. 마우스 호버 넘김 비활성화
      });

      pageFlip.loadFromHTML(document.querySelectorAll('.page'));
      el.style.visibility = 'visible';

      const pageInput = document.getElementById('pageInput');

      function syncPageInput() {
        const current = pageFlip.getCurrentPageIndex() + 1;
        pageInput.value = current;
      }

      pageFlip.on('flip', syncPageInput);

      document.getElementById('btnPrev').addEventListener('click', () => pageFlip.flipPrev());
      document.getElementById('btnNext').addEventListener('click', () => pageFlip.flipNext());

      // 3. 페이지 바로가기 (엔터키 & 버튼)
      function jumpToPage() {
        let val = parseInt(pageInput.value, 10);
        if (isNaN(val)) return;
        if (val < 1) val = 1;
        if (val > totalPages) val = totalPages;
        pageFlip.flip(val - 1);
      }

      document.getElementById('btnJump').addEventListener('click', jumpToPage);
      pageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') jumpToPage();
      });
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
  <title>디지털 간행물 보관소</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f4f6f8;
      color: #1e293b;
      padding: 30px 16px;
    }
    .container {
      max-width: 1040px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 28px;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 14px;
    }
    h1 {
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }
    /* 5. 3:4 비율의 가지런한 서가 그리드 */
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 24px;
    }
    .card {
      background: #fff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 14px rgba(0,0,0,0.06);
      transition: transform 0.2s, box-shadow 0.2s;
      display: flex;
      flex-direction: column;
      text-decoration: none;
      color: inherit;
    }
    .card:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.12);
    }
    /* 1. 첫 페이지 미리보기 (3:4 비율) */
    .cover-wrapper {
      width: 100%;
      aspect-ratio: 3 / 4;
      background: #e2e8f0;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .cover-wrapper img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .card-body {
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .card-title {
      font-size: 15px;
      font-weight: 600;
      color: #0f172a;
      line-height: 1.3;
    }
    .card-info {
      font-size: 12px;
      color: #64748b;
      display: flex;
      justify-content: space-between;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>간행물 보관소</h1>
    </header>
    <div class="grid">
      __CARDS_HTML__
    </div>
  </div>
</body>
</html>
"""

def main():
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(SITE_DIR, exist_ok=True)

    # 최신순(내림차순) 정렬: 2026-06, 2026-03 순서로 노출
    pdf_files = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")), reverse=True)
    cards_data = []

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        slug = os.path.splitext(filename)[0]
        display_title = slug.replace("_", " ")

        out_folder = os.path.join(SITE_DIR, slug)
        images_folder = os.path.join(out_folder, "images")
        os.makedirs(images_folder, exist_ok=True)

        print(f"변환 중: {filename}")
        images = convert_from_path(pdf_path, dpi=130)
        total_pages = len(images)
        pages_html = []

        for idx, img in enumerate(images):
            img_name = f"page_{idx+1:03d}.webp"
            img_full_path = os.path.join(images_folder, img_name)
            img.save(img_full_path, "WEBP", quality=85)
            pages_html.append(f'<div class="page"><img src="images/{img_name}" alt="페이지 {idx+1}"></div>')

        html_content = HTML_TEMPLATE.replace("__TITLE__", slug)\
                                    .replace("__DISPLAY_TITLE__", display_title)\
                                    .replace("__PAGES_HTML__", "\n      ".join(pages_html))\
                                    .replace("__TOTAL_PAGES__", str(total_pages))

        with open(os.path.join(out_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        # 메인 가판대용 첫 페이지 표지 경로
        cover_url = f"{slug}/images/page_001.webp"
        cards_data.append((slug, display_title, cover_url, total_pages))

    if cards_data:
        cards_html = "\n".join([
            f'''<a href="{slug}/" class="card">
              <div class="cover-wrapper">
                <img src="{cover_url}" alt="{title} 표지">
              </div>
              <div class="card-body">
                <div class="card-title">{title}</div>
                <div class="card-info">
                  <span>디지털 간행물</span>
                  <span>{pages}쪽</span>
                </div>
              </div>
            </a>'''
            for slug, title, cover_url, pages in cards_data
        ])
    else:
        cards_html = '<p style="color: #64748b;">등록된 간행물이 없습니다. pdfs 폴더에 PDF를 추가해 주세요.</p>'

    root_html = INDEX_TEMPLATE.replace("__CARDS_HTML__", cards_html)
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_html)

    print("전체 개선 빌드 완료!")

if __name__ == "__main__":
    main()