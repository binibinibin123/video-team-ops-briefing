# 영상팀 운영상황판

GitHub Pages로 배포하는 읽기 전용 영상팀 운영 브리핑 보드입니다.

## 배포 URL

https://binibinibin123.github.io/video-team-ops-briefing/

## 디자인 기준

`VoltAgent/awesome-design-md`를 실제 클론한 뒤 아래 DESIGN.md를 기준으로 재디자인했습니다.

- `design-md/airtable/DESIGN.md`
  - 흰 캔버스, 짙은 잉크 텍스트, 헤어라인 업무카드, 10~12px 라운드, 최소 그림자
- `design-md/notion/DESIGN.md`
  - DB 카드 구조, 상태 태그, 파스텔 tinted cards, compact property chip
- `design-md/miro/DESIGN.md`
  - 오늘 변경사항 sticky note, 화이트보드형 가독성, 옐로우/블루 강조

자세한 매핑은 [`DESIGN_MAPPING.md`](./DESIGN_MAPPING.md)에 기록했습니다.

## 화면 구성

- 오늘 핵심 변경
- 프로젝트 보드
  - 병목 주의
  - 집중 작업
  - 대기
  - 진행중
- 사람별 배치
- 최근 반영 로그

## 운영 원칙

- 업로드 수량 중심 화면이 아니라 프로젝트/사람별 현재 업무 중심 화면입니다.
- GitHub Pages 공개 링크이므로 민감 정보나 계정 정보는 넣지 않습니다.
- 검색 노출 최소화를 위해 `noindex`와 `robots.txt`를 적용했습니다. 단, 접근 제어는 아닙니다.

## 로컬 확인

```bash
python3 -m http.server 8799
node qa_dashboard.cjs http://127.0.0.1:8799/index.html
```
