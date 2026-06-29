# DESIGN.md 적용 근거

이번 버전은 사용자가 제공한 1280×720 참고 이미지를 기준으로 UI 골격을 다시 잡고, `VoltAgent/awesome-design-md`를 실제로 클론해 아래 세 파일의 토큰을 보조 기준으로 적용했다.

- `design-md/airtable/DESIGN.md`
- `design-md/notion/DESIGN.md`
- `design-md/linear.app/DESIGN.md`

## 참고 이미지에서 반영한 화면 구조

이미지의 핵심은 카드형 랜딩/칸반이 아니라 **업무용 SaaS의 고밀도 데이터베이스 화면**이었다.

적용한 구조:

1. 좌측 약 74px 폭의 짙은 남색 사이드 레일
2. 상단 얇은 워크스페이스 바
3. 흰색/연회색 캔버스 위의 작은 요약 카드
4. 중앙의 스프레드시트형 프로젝트 테이블
5. 오른쪽의 오늘 변경/팀 배치 보조 패널
6. 하단의 사람별 배치 매트릭스와 변경 로그
7. 11~13px 중심의 작은 업무툴 타이포그래피
8. 굵은 그림자보다 헤어라인/행 구분선 중심의 밀도감

## Airtable DESIGN.md → 중앙 업무 테이블

적용한 규칙:

- 흰 캔버스: `canvas #ffffff`
- 짙은 잉크 텍스트: `primary/ink #181d26`
- 헤어라인: `hairline #dddddd`
- 보조 표면: `surface-soft #f8fafc`
- 카드/테이블 패널 라운드: 8~12px 중심
- 그림자는 최소화하고 표 행/열 구분선을 우선

웹 적용 위치:

- 중앙 `업무 테이블` 패널
- 프로젝트 테이블의 행/열 헤어라인
- 요약 카드와 하단 테이블 카드의 흰 표면
- 텍스트 기본 색상과 업무툴식 차분한 대비

## Notion DESIGN.md → DB 속성/상태 태그

적용한 규칙:

- `brand-navy #0a1530` 계열을 워크스페이스/사이드 레일에 반영
- `surface #f6f5f4`, `surface-soft #fafaf9`를 보조 배경으로 사용
- `hairline #e5e3df` 계열로 DB 카드/속성 경계 구성
- compact property chip 구조
- pastel status tint:
  - peach/risk
  - lavender/focus
  - yellow/waiting
  - mint/steady

웹 적용 위치:

- 상태 chip: 병목/집중/대기/진행
- 담당자 chip, 날짜 chip, 업무 token
- 사람별 배치 매트릭스의 compact DB 속성 표현

## Linear.app DESIGN.md → 어두운 레일과 소프트웨어 밀도

적용한 규칙:

- 어두운 소프트웨어 캔버스 감각: `canvas #010102`, surface ladder 컨셉
- 단일 보라/블루 accent: `primary #5e6ad2`
- 작은 caption/body 중심의 dense UI
- pill/compact button의 8px 내외 라운드와 낮은 채도

웹 적용 위치:

- 좌측 짙은 사이드 레일
- 활성 네비게이션/상태 dot의 single accent
- 필터 버튼/상단 정보 pill
- 고밀도 SaaS 관리 화면 느낌

## 이전 버전에서 제거한 것

- 큰 히어로 문구
- 칸반 컬럼 중심 화면
- Miro sticky-note 중심의 밝은 화이트보드 감성
- 카드가 화면을 과하게 차지하는 레이아웃

이번 버전은 참고 이미지처럼 **“캡처된 업무툴 화면”**에 가깝게 보이도록, 한 화면에 프로젝트 행·담당자·마감·오늘 액션·세부 체크가 동시에 들어오게 만들었다.

## 색상/컴포넌트 매핑 요약

- 좌측 레일: Notion `brand-navy #0a1530` + Linear dark surface 감각
- 포인트: Linear `#5e6ad2`
- 기본 텍스트: Airtable `#181d26`
- 기본 테두리: Airtable `#dddddd`, Notion `#e5e3df`
- 기본 표면: Airtable/Notion 흰 캔버스와 연회색 surface
- 병목: Airtable coral `#aa2d00` + peach tint
- 집중: Notion primary/lavender tint
- 대기: Notion yellow tint
- 진행: green/mint tint
