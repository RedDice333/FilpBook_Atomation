# 간행물 자동 플립북 배포 시스템

이 저장소는 `pdfs/` 폴더에 PDF 파일을 올리면 GitHub Actions를 통해 모바일/PC 지원 플립북으로 자동 변환하여 GitHub Pages로 배포합니다.

## 폴더 구조
- `.github/workflows/deploy.yml`: GitHub Actions 자동 빌드 & 배포 설정
- `pdfs/`: 간행물 PDF 파일을 올리는 폴더 (예: `2026_spring.pdf`)
- `scripts/build_flipbooks.py`: PDF를 페이지별 이미지 및 플립북 HTML로 빌드하는 스크립트

## 사용 방법 (실무자용)
1. GitHub 웹에서 `pdfs/` 폴더에 원하는 PDF 파일을 업로드하고 커밋합니다.
2. 1~2분 후 자동으로 빌드가 완료됩니다.
3. `https://<내아이디>.github.io/<레포명>/<PDF파일명>/` 주소를 복사해 노션에 `/임베드`로 붙여넣습니다.
