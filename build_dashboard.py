#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = Path('/mnt/c/Users/82103/Documents/video_team_ops')
OUT = BASE / 'web_dashboard'

PROJECTS = BASE / 'video_projects.csv'
TASKS = BASE / 'tasks.csv'
SCHEDULE = BASE / 'upload_schedule.csv'
MEMBERS = BASE / 'team_members.csv'
DECISIONS = BASE / 'decision_log.md'
BRIEFINGS = BASE / 'daily_briefings.md'
TODAY_KST = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d')


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def compact_note(text: str, limit: int = 180) -> str:
    text = (text or '').replace('\r', '').replace('\n', ' ').strip()
    text = re.sub(r'\s+', ' ', text)
    if len(text) > limit:
        return text[:limit-1].rstrip() + '…'
    return text


def split_notes(text: str, limit_each: int = 95, max_items: int = 3):
    text = (text or '').replace('\r', '').strip()
    if not text or text == '미정':
        return []
    parts = [p.strip(' /') for p in re.split(r';\s*|\.\s+', text) if p.strip(' /')]
    out = []
    for p in parts:
        if len(p) > limit_each:
            p = p[:limit_each-1].rstrip() + '…'
        if p not in out:
            out.append(p)
        if len(out) >= max_items:
            break
    return out


PROJECT_OVERRIDES = {
    '스냅스': {
        'tone': 'risk',
        'status': '긴급 · 수정/컨펌준비 · 진행중',
        'stage': '수정 전달/컨펌 준비',
        'priority': '긴급',
        'due': '2026-07-02 오전/목중',
        'bullets': ['7/2(목) 오전 메인 수정본 전달 예정.', '목요일 중 컨펌 완료 시 7/7(화)~7/12(일) 총 60건 발행 예정.', '컨펌 완료 시점에 따라 발행 시작일 지연 가능.', '일별 배분은 미정이라 우선 주간 총량 60건으로 관리.', '표지영은 헤븐리젤리 원본 8개와 겹쳐 과부하 위험. 상하목장 2차는 신유빈 담당으로 전환되어 일부 완화.']
    },
    '비더후드': {'tone': 'risk', 'status': '업로드/비축 · 진행중', 'stage': '업로드/비축', 'bullets': ['정희헌 메인.', '7/2 업로드분까지 비축 완료.', '6/30 한은지 지원 투입 이력.', '7/3 유20 + 7/4 유15 잔여분 비축/예약 확인 필요.', '정희헌은 동아제약 4개 수정대기 상태라 상세 수정사항 수신 후 병행 일정 재확인 필요.']},
    '벤슨': {
        'tone': 'focus',
        'status': '높음 · 업로드/테스트 · 진행중',
        'stage': '업로드/썸넬 테스트',
        'priority': '높음',
        'due': '2026-07-01',
        'bullets': ['여기성 메인 중심.', '7/1 유10 업로드 대응.', '신규 소구는 수요일부터 반영 예정.', '7/1 썸넬 테스트 1세트 추가.', '테스트 기준/적용 영상 확인 필요.', '이재은은 듀오타이트 제작으로 전환 완료.']
    },
    '최유정': {'tone': 'risk', 'status': '긴급 · 편집 · 잔여 확인', 'stage': '편집/잔여 확인', 'bullets': ['김경은 오늘 출근.', '정희헌 중심으로 잔여/세이브본 확인 필요.', '이재은은 듀오타이트 제작 시작으로 추가 지원 여력 낮음.', '김경은 7/7 마지막 출근 예정이라 인수인계 필요.']},
    '동아제약': {'tone': 'waiting', 'status': '높음 · 수정대기 · 상세수정사항 대기', 'stage': '수정대기', 'priority': '높음', 'due': '미정', 'bullets': ['컨펌 보낸 4개 전부 수정 요청 수신.', '큰 수정 예정이며 고객사가 상세 수정사항 별도 전달 예정.', '일정 지연은 허용됨.', '정희헌은 상세 수정사항 수신 후 작업량 산정 및 수정본 일정 재확정 필요.', '비더후드 7/3 이후 잔여분과 병행 일정 체크.']},
    '삼양': {'tone': 'steady', 'bullets': ['탱글 3번 바리에이션 완료.', '4번 컨펌 추적.', '5/6번 후속 제작 병행.']},
    '미닉스': {
        'tone': 'risk',
        'status': '긴급 · 발행/바리에이션 · 컨펌완료',
        'stage': '발행/바리에이션',
        'priority': '긴급',
        'due': '2026-07-03',
        'bullets': ['원본 영상 4개 컨펌 완료.', '6/30(화) 원본 4개 발행.', '각 원본당 9개씩 총 36개 바리에이션.', '7/1~7/4 하루 9개 업로드, 제작 완료는 7/3(금) 퇴근 전.']
    },
    '볼보': {'tone': 'focus', 'status': '높음 · 제작/바리에이션 · 진행중', 'stage': '제작/바리에이션', 'priority': '높음', 'due': '2026-06-30', 'bullets': ['최성진 메인으로 진행.', '프로그램을 이용한 바리에이션 영상 25개 오늘 제작 중.', '산출물 품질/중복 검수 체크 필요.']},
    'CJ': {'tone': 'steady', 'bullets': ['한은지 메인.', '월/수/금 CJ 업무 고정.', '화/목은 타 프로젝트 지원 가능.', '6/30 화요일은 비더후드 지원 중.']},
    '아이돌종합': {'tone': 'waiting', 'bullets': ['김경은 오늘 출근.', '7/7 마지막 출근 예정.', '인수인계/후임 오너 확인 필요.']},
    '듀오타이트': {
        'owner': '이재은',
        'tone': 'focus',
        'status': '긴급 · 제작 시작 · 메인담당',
        'stage': '제작 시작',
        'priority': '긴급',
        'due': '2026-07-03',
        'bullets': [
            '기획 2건 완료 후 이재은 듀오타이트 제작 시작.',
            '메인영상 9건: 7/3(금)까지 완료 목표.',
            '잔여 7건 기획/제작 속도 확인 필요.',
            '7/13(월) 첫 라이브 목표. 컨펌이 빨라지면 일정 단축 가능.',
            '1주차 45건 + 2주차 47건 = 최소 92건 발행.',
            '3주차는 조회수 추이를 반영해 추가 바리에이션 제작/발행.',
            '목표 조회수 276,000.',
        ]
    },
    '뷰엑스 홍보영상': {'tone': 'focus', 'bullets': ['신유빈 관리중.', '팀 업무 분배와 함께 체크.']},
    '헤븐리젤리': {
        'tone': 'risk',
        'status': '긴급 · 신규/원본제작 · 진행중',
        'stage': '원본 제작',
        'priority': '긴급',
        'due': '2026-07-02',
        'bullets': ['오늘 신규 프로젝트로 표지영 담당 확정.', '내일 7/2(목)까지 원본영상 8개 산출 필요.', '스냅스 수정 7/2 오전 마감과 동시에 진행.', '상하목장 2차는 신유빈 담당으로 이관되어 표지영 부담 일부 완화.', '오늘 오후 제작 가능 시간 역산 및 지원 필요 여부 확인.']
    },
    '한손한끼': {
        'tone': 'waiting',
        'status': '종료 · 운영 제외',
        'stage': '종료',
        'priority': '낮음',
        'due': '미정',
        'bullets': ['일단 종료로 반영.', '6/30~7/4 반복 유5 물량은 영상팀 부하 계산에서 제외.']
    },
    '쿠쿠홈시스': {
        'owner': '표지영',
        'tone': 'waiting',
        'status': '소스 재전달 이슈 · 보류',
        'stage': '소스수급/일정 보류',
        'priority': '높음',
        'due': '미정',
        'bullets': ['표지영 메인.', '원본 영상 1개: 원래 7/1(수)까지였으나 고객사 소스 재전달 이슈로 연기.', '새 소스/새 마감 확인 전까지 제작 보류.', '7/3~7/4 유10 업로드/바리에이션 일정 영향 재확인 필요.']
    },
    '쿠쿠홍시스': {
        'title': '쿠쿠홈시스',
        'owner': '표지영',
        'tone': 'waiting',
        'status': '소스 재전달 이슈 · 보류',
        'stage': '소스수급/일정 보류',
        'priority': '높음',
        'due': '미정',
        'bullets': ['표지영 메인.', '원본 영상 1개: 원래 7/1(수)까지였으나 고객사 소스 재전달 이슈로 연기.', '새 소스/새 마감 확인 전까지 제작 보류.', '7/3~7/4 유10 업로드/바리에이션 일정 영향 재확인 필요.']
    },
    '딜로이트(상하목장)': {
        'owner': '신유빈',
        'tone': 'focus',
        'status': '1차 전달완료 · 2차 소스수급 · 진행중',
        'stage': '소스수급/2차 전달',
        'priority': '높음',
        'due': '2026-07-03',
        'bullets': ['1차 소스 40개 전달 완료.', '2차 소스 전달은 신유빈 담당.', '금요일 7/3까지 2차 각 4개 추가, 총 40개 전달 필요.', '최종 80개 기준. 기존 업로드 4개 소스 제외하고 신규 소스 기준.', '정리 경로: X:\\09 프로젝트\\01.영상 바이럴\\딜로이트(상하목장)\\00.소스\\02소스모음']
    },
}

PEOPLE_OVERRIDES = {
    '신유빈': '팀 리드. 업무 분배/우선순위 판단, 스냅스 지원·관리 기록 유지. 상하목장 2차 소스 40개를 7/3(금)까지 직접 전달 담당. 뷰엑스 홍보영상 관리중.',
    '이재은': '듀오타이트 제작 시작. 7/3(금)까지 메인영상 9건, 7/13(월) 첫 라이브 목표. 1주차 최소 45건/2주차 최소 47건, 최소 92건 발행과 목표 조회수 276,000 기준. 최유정 추가 지원 여력 낮음.',
    '여기성': '벤슨 메인. 7/1 유10 업로드와 신규 소구 반영, 썸넬 테스트 1세트 추가 세팅 확인 필요. 이재은은 듀오타이트 제작으로 전환 완료.',
    '표지영': '스냅스 메인 수정본 7/2 오전 전달 후 목요일 중 컨펌 추적. 컨펌 완료 시 7/7(화)~7/12(일) 총 60건 발행 예정. 헤븐리젤리 원본영상 8개 7/2까지 제작. 상하목장 1차는 전달 완료, 2차는 신유빈 담당으로 전환되어 일부 부담 완화. 쿠쿠홈시스는 소스 재전달 이슈 보류. 그래도 스냅스+헤븐리젤리 동시 마감 과부하 주의.',
    '정희헌': '비더후드 7/2 업로드분까지 비축 완료. 동아제약은 컨펌 보낸 4개 전부 큰 수정 요청 수신, 고객사 상세 수정사항 별도 전달 대기. 일정 지연은 허용되어 즉시 마감 압박은 완화. 7/3 이후 비더후드 잔여분 확인 필요.',
    '최성진': '볼보 메인. 6/30 프로그램을 이용한 바리에이션 영상 25개 제작 중. 산출물 품질/중복 검수 체크 필요.',
    '한은지': 'CJ 월/수/금 고정 업무. 화/목은 웬만하면 타 프로젝트 지원 가능. 6/30 화요일은 비더후드 지원 중.',
    '김경은': '오늘 출근. 아이돌종합/최유정 메인. 2026-07-07 마지막 출근 예정이라 인수인계 필요.',
    '조성주': '미닉스 원본 4개 컨펌 완료. 6/30(화) 원본 4개 발행, 7/1~7/4 하루 9개 업로드. 총 36개 바리에이션 제작·검수는 7/3(금) 퇴근 전 완료 필요.',
}


def priority_rank(row):
    priority = row.get('priority', '')
    status = row.get('status', '')
    risk = row.get('risks', '')
    score = 0
    if '긴급' in priority: score += 100
    if '높음' in priority: score += 70
    if '진행' in status: score += 20
    if any(k in risk for k in ['병목', '부족', '지원', '컨펌', '휴무', '리스크']): score += 30
    return -score, row.get('project_title','')


def classify_project(row):
    title = row.get('project_title','')
    risk = row.get('risks','') + ' ' + row.get('dependencies','')
    if title in {'쿠쿠홈시스'}:
        return 'focus'
    if any(k in risk for k in ['병목', '부족', '휴무', '공백', '컨펌 전', '컨펌대기']):
        return 'risk'
    if row.get('status') == '대기':
        return 'waiting'
    return 'steady'


def status_label(row):
    bits = []
    if row.get('priority') and row.get('priority') != '미정':
        bits.append(row['priority'])
    if row.get('current_stage') and row.get('current_stage') != '미정':
        bits.append(row['current_stage'])
    if row.get('status') and row.get('status') != '미정':
        bits.append(row['status'])
    return ' · '.join(bits) or '상태 확인 필요'


def display_task_title(title: str) -> str:
    # The public briefing should show operational action, not upload/volume-like counts.
    replacements = {
        '미닉스 7월 1주차 40건': '미닉스 7월 1주차 바리에이션 발행',
        '동아제약 7/1 제작분 3건': '동아제약 7/1 제작분 준비',
    }
    return replacements.get(title or '', title or '')


def task_rank(t):
    priority_order = {'긴급': 0, '높음': 1, '보통': 2, '낮음': 3, '미정': 4, '': 5}
    status_order = {'진행중': 0, '검수대기': 1, '컨펌대기': 2, '대기': 3, '보류': 4, '미정': 5, '': 6}
    due = t.get('due_date') or '9999-12-31'
    if due == '미정':
        due = '9999-12-31'
    return (priority_order.get(t.get('priority', ''), 5), due, status_order.get(t.get('status', ''), 6), t.get('task_title', ''))


def extract_latest_markdown(path: Path, heading_contains: str | None = None, max_lines=8):
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8').splitlines()
    sections = []
    current = []
    current_heading = ''
    for line in lines:
        if line.startswith('## '):
            if current:
                sections.append((current_heading, current))
            current_heading = line[3:].strip()
            current = []
        elif current_heading:
            current.append(line)
    if current:
        sections.append((current_heading, current))
    if heading_contains:
        matches = [(h, c) for h, c in sections if heading_contains in h]
    else:
        matches = sections[-1:]
    if not matches:
        matches = sections[-1:]
    if not matches:
        return []
    heading, content = matches[-1]
    bullets = []
    for line in content:
        s = line.strip()
        if s.startswith('- '):
            bullets.append(s[2:])
        if len(bullets) >= max_lines:
            break
    return [{'heading': heading, 'text': b} for b in bullets]




WEEKDAY_KO = ['월', '화', '수', '목', '금', '토', '일']


def valid_date(value: str) -> bool:
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', value or ''))


def date_label(value: str) -> str:
    if not valid_date(value):
        return value or '미정'
    dt = datetime.strptime(value, '%Y-%m-%d')
    return f"{dt.month}/{dt.day}({WEEKDAY_KO[dt.weekday()]})"


def parse_decision_changes(path: Path):
    grouped = {}
    if not path.exists():
        return grouped
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        m = re.match(r'^-\s+(\d{4}-\d{2}-\d{2})(?:\s+((?:\d{1,2}:\d{2}\s*KST)|[^:]+?))?:\s*(.+)$', line)
        if not m:
            continue
        date, time_part, body = m.groups()
        label = (time_part or '').replace('KST', '').strip()
        grouped.setdefault(date, []).append({'time': label, 'text': compact_note(body, 150)})
    return grouped


def build_change_calendar(tasks_raw, schedule_raw, projects_raw):
    project_by_id = {p.get('project_id'): p.get('project_title') for p in projects_raw}
    changes_by_date = parse_decision_changes(DECISIONS)
    loads = {}
    dates = set(changes_by_date.keys())
    for row in schedule_raw:
        date = row.get('date', '')
        if not valid_date(date):
            continue
        dates.add(date)
        if str(row.get('included_in_video_team', '')).upper() == 'TRUE' and row.get('platform') == '유튜브':
            try:
                loads[date] = loads.get(date, 0) + int(row.get('count') or 0)
            except ValueError:
                pass

    events_by_date = {}
    for t in tasks_raw:
        if t.get('status') == '취소':
            continue
        date = t.get('due_date') if valid_date(t.get('due_date','')) else t.get('updated_at')
        if not valid_date(date):
            continue
        dates.add(date)
        event = {
            'person': t.get('assignee') or '미정',
            'project': project_by_id.get(t.get('project_id'), t.get('project_id') or '미정'),
            'title': display_task_title(t.get('task_title','')),
            'status': t.get('status') or '미정',
            'priority': t.get('priority') or '미정',
        }
        events_by_date.setdefault(date, []).append(event)

    days = []
    for date in sorted(d for d in dates if valid_date(d)):
        events = events_by_date.get(date, [])
        # Keep the calendar dense: urgent/high/current support items first.
        def event_rank(e):
            score = 0
            if '긴급' in e.get('priority',''): score -= 50
            if '높음' in e.get('priority',''): score -= 30
            if '진행' in e.get('status',''): score -= 10
            return score, e.get('person',''), e.get('title','')
        events = sorted(events, key=event_rank)
        days.append({
            'date': date,
            'label': date_label(date),
            'weekday': date_label(date).split('(')[-1].rstrip(')') if valid_date(date) else '',
            'load': f"유{loads[date]}" if date in loads else '물량 미정',
            'isToday': date == TODAY_KST,
            'events': events[:8],
            'changes': changes_by_date.get(date, [])[-5:],
        })
    return days

def build():
    projects_raw = read_csv(PROJECTS)
    tasks_raw = read_csv(TASKS)
    members_raw = read_csv(MEMBERS)
    schedule_raw = read_csv(SCHEDULE) if SCHEDULE.exists() else []

    # Active tasks by assignee/project
    active_tasks = [t for t in tasks_raw if t.get('status') not in {'완료', '취소'}]
    tasks_by_assignee = {}
    for t in active_tasks:
        tasks_by_assignee.setdefault(t.get('assignee','미정'), []).append(t)

    project_cards = []
    for p in sorted(projects_raw, key=priority_rank):
        if p.get('status') == '완료':
            continue
        title = p.get('project_title','')
        if not title:
            continue
        override = PROJECT_OVERRIDES.get(title, {})
        bullets = override.get('bullets')
        if not bullets:
            bullets = []
            bullets.extend(split_notes(p.get('dependencies'), max_items=2))
            bullets.extend(split_notes(p.get('risks'), max_items=2))
            if not bullets:
                bullets.extend(split_notes(p.get('notes'), max_items=2))
        project_cards.append({
            'title': override.get('title') or title,
            'owner': override.get('owner') or p.get('owner') or '미정',
            'status': override.get('status') or status_label(p),
            'stage': override.get('stage') or p.get('current_stage') or '미정',
            'priority': override.get('priority') or p.get('priority') or '미정',
            'due': override.get('due') or p.get('upload_due_date') or '미정',
            'tone': override.get('tone') or classify_project(p),
            'bullets': bullets[:7] or ['세부 상태 확인 필요'],
        })

    people_cards = []
    for m in members_raw:
        if str(m.get('active','')).upper() != 'TRUE':
            continue
        name = m.get('name','')
        tasks = sorted(tasks_by_assignee.get(name, []), key=task_rank)
        task_summaries = []
        for t in tasks[:4]:
            task_summaries.append({
                'title': display_task_title(t.get('task_title','')),
                'status': t.get('status',''),
                'priority': t.get('priority',''),
                'due': t.get('due_date',''),
            })
        if name == '이재은':
            task_summaries = [
                {'title': '벤슨 지원 마무리', 'status': '완료', 'priority': '높음', 'due': '2026-06-30'},
                {'title': '듀오타이트 제작 시작', 'status': '진행중', 'priority': '긴급', 'due': '2026-06-30'},
                {'title': '듀오타이트 메인영상 9건', 'status': '7/3까지', 'priority': '긴급', 'due': '2026-07-03'},
            ]
        elif name == '정희헌':
            for task in task_summaries:
                if task['title'] == '최유정 지원':
                    task['title'] = '최유정 잔여 지원'
                    task['status'] = '잔여 확인'
        capacity = PEOPLE_OVERRIDES.get(name) or compact_note(m.get('capacity_notes') or m.get('notes') or '상태 확인 필요', 180)
        people_cards.append({
            'name': name,
            'role': m.get('role') or '팀원',
            'capacity': capacity,
            'tasks': task_summaries,
            'tone': 'risk' if any(k in capacity for k in ['병목','휴무','긴급','부족','컨펌대기']) else ('focus' if name in ['표지영','이재은','신유빈'] else 'steady'),
        })

    key_changes = [
        {'label': '상하목장', 'title': '1차 전달 완료 · 2차 신유빈 담당', 'body': '상하목장 1차 소스 40개는 전달 완료. 2차 소스 40개 전달은 금요일 7/3까지 신유빈이 담당. 표지영의 상하목장 소스 병목은 일부 해소.'},
        {'label': '동아제약', 'title': '4개 전부 큰 수정 요청 · 상세사항 대기', 'body': '동아제약은 컨펌 보낸 4개 모두 수정 요청 수신. 큰 수정 예정이며 고객사가 상세 수정사항을 별도 전달 예정. 일정 지연은 허용.'},
        {'label': '스냅스', 'title': '7/2 수정본 전달 → 컨펌 시 차주 60건', 'body': '스냅스는 7/2(목) 오전 메인 수정본 전달 후 목요일 중 컨펌 완료 시 7/7(화)~7/12(일) 총 60건 전체 발행 예정. 컨펌 시점에 따라 시작일 지연 가능.'},
        {'label': '헤븐리젤리', 'title': '신규 프로젝트 · 표지영 담당 · 원본 8개', 'body': '헤븐리젤리 신규 프로젝트 표지영 담당 확정. 2026-07-02까지 원본영상 8개 산출 필요. 스냅스 수정과 동시 마감이라 표지영 부하 주의.'},
        {'label': '벤슨', 'title': '7/1 썸넬 테스트 1세트 추가', 'body': '벤슨 7/1 유10 및 신규 소구 반영과 함께 썸넬 테스트 1세트 추가. 여기성 메인 기준, 테스트 기준/적용 영상 확인 필요.'},
        {'label': '쿠쿠홈시스', 'title': '원본 1개 제작 일정 보류', 'body': '원래 7/1까지였던 원본 영상 1개 제작은 고객사 소스 재전달 이슈로 일단 연기. 새 소스/새 마감 확인 전까지 제작 보류이며, 7/3~7/4 유10 영향 재확인 필요.'},
        {'label': '비더후드', 'title': '7/2 업로드분까지 비축 완료', 'body': '정희헌 메인 비더후드는 2026-07-02 업로드분까지 비축 완료. 7/3 유20·7/4 유15 잔여분은 확인 필요.'},

        {'label': '한은지', 'title': 'CJ 월/수/금 고정 · 화/목 지원 가능', 'body': '오늘 6/30(화)은 비더후드 지원 이력. 비더후드 7/2분까지 비축 완료.'},
        {'label': '듀오타이트', 'title': '이재은 제작 시작 · 7/3 메인 9건', 'body': '이재은이 듀오타이트 제작을 시작. 7/3(금) 메인영상 9건 마감 유지.'},
        {'label': '볼보', 'title': '프로그램 바리에이션 25개 제작 중', 'body': '최성진이 오늘 프로그램을 이용한 바리에이션 영상 25개 제작 중. 품질/중복 검수 필요.'},
        {'label': '한손한끼', 'title': '일단 종료 · 운영 제외', 'body': '프로젝트 상태를 완료/종료로 변경. 6/30~7/4 반복 유5 물량은 영상팀 부하 계산에서 제외.'},
        {'label': '미닉스', 'title': '컨펌 완료 · 발행 페이즈', 'body': '원본 4개 컨펌 완료. 6/30 원본 4개 발행 후 7/1~7/4 하루 9개씩 바리에이션 발행.'},
        {'label': '김경은', 'title': '오늘 출근 · 7/7 마지막 출근', 'body': '6/29 휴무였고 6/30 출근. 최유정/아이돌종합 인수인계 플랜 필요.'},
        {'label': '듀오타이트 목표', 'title': '7/13 첫 라이브 목표', 'body': '1주차 최소 45건, 2주차 최소 47건. 최소 92건 발행과 목표 조회수 276,000 기준.'},
    ]

    # Latest operational bullets. Keep static overrides first so the generated
    # public briefing does not regress when older source logs are used.
    recent_updates = [
        {'heading': '2026-07-01 18:01 — 상하목장/동아제약 상태 변경', 'text': '상하목장 1차 소스는 전달 완료, 2차 소스 40개는 7/3까지 신유빈 담당. 동아제약은 컨펌 보낸 4개 모두 큰 수정 요청 수신, 상세 수정사항 대기이며 일정 지연은 허용.'},
        {'heading': '2026-07-01 15:45 — 스냅스 차주 발행 조건', 'text': '스냅스는 7/2 오전 메인 수정본 전달 후 목요일 중 컨펌 완료 시 7/7~7/12 총 60건 발행 예정. 컨펌 지연 시 시작일도 밀릴 수 있음.'},
        {'heading': '2026-07-01 14:22 — 헤븐리젤리 신규/스냅스 수정', 'text': '헤븐리젤리 신규 프로젝트는 표지영 담당, 7/2까지 원본영상 8개 필요. 스냅스 수정은 7/2 오전까지 완료 필요. 표지영 과부하 주의.'},
        {'heading': '2026-07-01 00:00 — 벤슨 썸넬 테스트 추가', 'text': '벤슨 7/1 업무에 썸넬 테스트 1세트 추가. 여기성 메인, 신규 소구 반영과 함께 테스트 기준/적용 영상 확인 필요.'},
        {'heading': '2026-06-30 23:39 — 스냅스 원본 완료/상하목장 누락 정정', 'text': '스냅스 원본 6개 제작 완료 이력. 이후 7/1 수정 요청 반영으로 현재는 7/2 오전까지 수정 진행중. 상하목장은 당시 표지영 소스 수집으로 누락 정정했고, 7/1 18:01 기준 2차는 신유빈 담당으로 전환.'},
        {'heading': '2026-06-30 17:34 — 쿠쿠홈시스 소스 이슈로 보류', 'text': '쿠쿠홈시스 원본 1개는 원래 7/1까지였으나 고객사 소스 재전달 이슈로 일단 연기. 새 소스/새 마감 확인 전까지 제작 보류이며 7/3~7/4 유10 영향 재확인 필요.'},
        {'heading': '2026-06-30 17:16 — 동아제약 과거 제작 예상', 'text': '동아제약은 6/30 당시 제작 진행으로 기록됐으나, 7/1 18:01 최신 기준 컨펌 보낸 4개 전부 큰 수정 요청 수신 및 상세 수정사항 대기 상태.'},
        {'heading': '2026-06-30 15:09 — 비더후드 비축/동아제약 진행', 'text': '비더후드는 7/2 업로드분까지 비축 완료. 동아제약은 이후 7/1 최신 기준 4개 수정요청/상세 수정사항 대기로 전환.'},
        {'heading': '2026-06-30 14:41 — 이재은 듀오타이트 제작 시작', 'text': '이재은이 벤슨 지원을 마무리하고 듀오타이트 제작을 시작. 듀오타이트는 메인영상 9건 제작 진행중으로 전환, 7/3(금) 마감 유지.'},
        {'heading': '2026-06-30 14:00 — 한은지 비더후드 지원', 'text': '한은지는 보통 월/수/금 CJ 고정 업무. 화/목은 타 프로젝트 지원 가능하며, 오늘 6/30(화)은 비더후드 지원 중.'},
        {'heading': '2026-06-30 13:44 — 듀오타이트 기획 2건 완료', 'text': '듀오타이트 기획 2건 완료. 이후 14:41에 이재은 제작 시작으로 전환.'},
        {'heading': '2026-06-30 10:53 — 볼보 바리에이션 제작', 'text': '최성진이 프로그램을 이용한 볼보 바리에이션 영상 25개를 오늘 제작 중. 산출물 품질/중복 검수 체크 필요.'},
        {'heading': '2026-06-30 — 한손한끼 종료 반영', 'text': '한손한끼는 일단 종료. 프로젝트 상태를 완료/종료로 변경하고, 6/30~7/4 반복 유5 물량은 영상팀 부하 계산에서 제외.'},
        {'heading': '2026-06-30 — 오늘 업무 종료', 'text': '6/29 당일 업무는 종료 상태로 기록하고, 이후 새 착수 포커스는 듀오타이트로 전환.'},
        {'heading': '2026-06-30 — 듀오타이트 메인담당 전환', 'text': '이재은: 듀오타이트 메인 담당자. 기획 2건 완료 후 제작 시작. 메인영상 9건 7/3(금) 완료 목표.'},
        {'heading': '2026-06-30 — 미닉스 컨펌 완료', 'text': '미닉스 원본 4개 컨펌 완료. 6/30 원본 4개 발행 후 7/1~7/4 하루 9개씩 바리에이션 발행.'},
        {'heading': '2026-06-30 — 김경은 출근/퇴사 예정 반영', 'text': '김경은은 6/29 휴무였고 6/30 출근. 2026-07-07 마지막 출근 예정으로 최유정/아이돌종합 인수인계 필요.'},
        {'heading': '2026-06-30 — 듀오타이트 발행/조회수 목표', 'text': '7/13(월) 첫 라이브 목표. 1주차 최소 45건, 2주차 최소 47건, 3주차는 조회수 추이 반영 추가 바리에이션. 최소 92건/목표 조회수 276,000.'},
    ]
    recent_updates.extend(extract_latest_markdown(BRIEFINGS, None, max_lines=3))

    stats = {
        'activeProjects': len(project_cards),
        'activeTasks': sum(len(person['tasks']) for person in people_cards),
        'riskProjects': len([p for p in project_cards if p.get('tone') == 'risk']),
        'teamMembers': len(people_cards),
    }

    data = {
        'meta': {
            'title': '영상팀 운영상황판',
            'lastUpdated': '2026-07-01 18:01 KST · 상하목장 1차 완료/2차 신유빈 담당 · 동아제약 4개 수정대기 반영',
            'designReference': 'VoltAgent awesome-design-md 직접 적용: Airtable DESIGN.md 테이블/헤어라인 + Notion DESIGN.md DB 속성 태그 + Linear.app DESIGN.md 다크 사이드레일',
            'privacyNote': 'GitHub Pages 공개 링크용 정적 브리핑. 검색 노출 최소화를 위해 noindex 메타 적용.',
        },
        'stats': stats,
        'keyChanges': key_changes,
        'projects': project_cards,
        'people': people_cards,
        'recentUpdates': recent_updates,
        'changeCalendar': build_change_calendar(tasks_raw, schedule_raw, projects_raw),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    build()
    print(OUT / 'data.json')
