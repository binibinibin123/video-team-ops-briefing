# DESIGN.md 적용 근거

이번 재디자인은 `VoltAgent/awesome-design-md`를 실제로 클론한 뒤 아래 세 파일을 기준으로 만들었다.

- `design-md/airtable/DESIGN.md`
- `design-md/notion/DESIGN.md`
- `design-md/miro/DESIGN.md`

## 선택 기준

영상팀 운영 브리핑은 예쁜 랜딩페이지가 아니라 **회사 내부 프로세스 상황판**이다. 그래서 브랜드 감성보다 다음 질문에 바로 답하는 UI가 우선이다.

1. 지금 병목은 어디인가?
2. 누가 메인이고 누가 지원인가?
3. 어떤 프로젝트가 대기/집중/진행 상태인가?
4. 오늘 바뀐 담당/지원 관계는 무엇인가?

## Airtable DESIGN.md → 기본 업무보드 뼈대

적용한 규칙:

- 흰 캔버스 중심: `canvas #ffffff`
- 짙은 잉크 텍스트: `primary/ink #181d26`
- 업무카드는 헤어라인 중심: `hairline #dddddd`
- 표면색은 과하지 않게: `surface-soft #f8fafc`
- 카드/버튼 라운드는 10~12px 중심
- 섹션은 큰 장식보다 여백과 정렬로 구분
- 그림자 최소화, color-block/헤어라인 중심

웹 적용 위치:

- 전체 배경과 보드 카드의 기본 색상
- 프로젝트 카드의 흰 카드 + 얇은 테두리
- 상단 헤더/내비게이션의 조용한 업무툴 느낌
- 과한 히어로 제거, 운영판형 첫 화면으로 변경

## Notion DESIGN.md → DB 카드/상태 태그

적용한 규칙:

- 기본 DB 카드: 흰 배경 + `hairline #e5e3df` 테두리
- 주요 보조 배경: `surface #f6f5f4`, `surface-soft #fafaf9`
- 파스텔 태그/카드 색상:
  - peach `#ffe8d4`
  - rose `#fde0ec`
  - mint `#d9f3e1`
  - lavender `#e6e0f5`
  - sky `#dcecfa`
  - yellow `#fef7d6`
- 상태 태그는 작은 라운드 배지로 처리

웹 적용 위치:

- 프로젝트 상태 배지
- 담당/일정/단계 메타 필드
- 사람별 업무 chip
- 병목/집중/대기/진행 컬럼의 연한 배경

## Miro DESIGN.md → 오늘 변경 sticky note

적용한 규칙:

- 화이트보드 가독성
- sticky note 강조:
  - yellow `#ffd02f`, `#fff4c4`
  - blue `#4262ff`
  - coral/teal 계열 강조색
- 큰 장식이 아니라 “오늘 바뀐 것”을 붙여놓는 용도로만 사용

웹 적용 위치:

- 오른쪽 `오늘 핵심 변경` sticky note 3개
- 배경의 아주 약한 그리드 질감
- 선택 필터/강조점에만 Miro 블루/옐로우 계열 사용

## 이전 버전과 달라진 점

이전 버전은 `Airtable/Notion/Miro 느낌`을 말로만 참고했고, 실제 DESIGN.md 토큰과 컴포넌트 규칙을 체계적으로 반영하지 못했다.

이번 버전은 다음을 바꿨다.

- 랜딩페이지식 큰 히어로 제거
- 첫 화면을 업무상황판으로 변경
- 프로젝트를 `병목 / 집중 / 대기 / 진행` 칸반으로 재배치
- 사람별 카드를 운영 배치 중심으로 재정리
- 업로드 수량성 문구는 메인 화면에서 제거하거나 업무 액션 문구로 축약
- CSS 최상단에 DESIGN.md 토큰 매핑을 명시
- `README.md`에 실제 참고 파일과 적용 방식을 기록

## 색상/컴포넌트 매핑 요약

- 기본 텍스트: Airtable `#181d26`
- 기본 테두리: Airtable `#dddddd`, Notion `#e5e3df`
- 기본 카드: Airtable/Notion 흰 DB 카드
- 병목: Airtable coral `#aa2d00` + 연한 peach
- 집중: Notion primary `#5645d4` + lavender
- 대기: Miro/Notion yellow 계열
- 진행: Airtable success green 계열
- 오늘 변경: Miro sticky note 계열
