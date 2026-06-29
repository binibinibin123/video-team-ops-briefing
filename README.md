# 영상팀 운영 브리핑 웹 대시보드

정적 GitHub Pages용 운영 브리핑판입니다.

## 디자인 기준

- VoltAgent `awesome-design-md` 참고
  - Airtable: 워크플로우 카드형 정보 구조
  - Notion: 상태 태그와 데이터베이스 카드 감각
  - Miro: 화이트보드형 가독성과 밝은 포인트 컬러
- 업로드 수량표가 아니라 프로젝트별/사람별 업무 배치를 보여주는 용도입니다.

## 구조

- `index.html`: 페이지 구조
- `styles.css`: 디자인 시스템
- `app.js`: 데이터 렌더링/필터
- `data.json`: 현재 영상팀 장부에서 생성된 브리핑 데이터
- `build_dashboard.py`: 로컬 CSV 장부에서 `data.json` 생성
