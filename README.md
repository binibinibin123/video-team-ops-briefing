# 영상팀 운영상황판

GitHub Pages로 배포하는 읽기 전용 영상팀 운영 브리핑 보드입니다.

## 배포 URL

https://binibinibin123.github.io/video-team-ops-briefing/

## 이번 UI 방향

사용자 참고 이미지처럼 **짙은 좌측 사이드바 + 흰색 업무 OS + 고밀도 스프레드시트형 테이블 + 우측 변경/팀 배치 패널**로 재디자인했습니다.

이전 카드/칸반 중심 화면은 제거했고, 첫 화면에서 다음 항목이 바로 보이도록 바꿨습니다.

- 프로젝트 상태
- 담당자
- 단계
- 마감
- 오늘 액션
- 세부 체크
- 오늘 변경
- 팀 배치

## 디자인 기준

`VoltAgent/awesome-design-md`를 실제 클론한 뒤 아래 DESIGN.md를 기준으로 재디자인했습니다.

- `design-md/airtable/DESIGN.md`
  - 흰 캔버스, 짙은 잉크 텍스트, 헤어라인, 차분한 업무툴 테이블
- `design-md/notion/DESIGN.md`
  - DB 속성/상태 태그, 연회색 surface, compact property chip
- `design-md/linear.app/DESIGN.md`
  - 짙은 소프트웨어 레일, 단일 보라/블루 accent, dense SaaS UI 밀도

자세한 매핑은 [`DESIGN_MAPPING.md`](./DESIGN_MAPPING.md)에 기록했습니다.

## 화면 구성

- 좌측 워크스페이스 레일
- 상단 워크스페이스 바
- 운영 요약 카드
- 업무 테이블
- 오늘 변경 패널
- 팀 배치 패널
- 사람별 배치 매트릭스
- 최근 반영 로그

## 운영 원칙

- 업로드 수량만 크게 보여주는 화면이 아니라 프로젝트/사람별 현재 업무 중심 화면입니다.
- GitHub Pages 공개 링크이므로 민감 정보나 계정 정보는 넣지 않습니다.
- 검색 노출 최소화를 위해 `noindex`와 `robots.txt`를 적용했습니다. 단, 접근 제어는 아닙니다.

## 로컬 확인

```bash
python3 -m http.server 8799
node qa_dashboard.cjs http://127.0.0.1:8799/index.html
```
