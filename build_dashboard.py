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
        'status': '긴급 · 수정완료 · 컨펌대기',
        'stage': '컨펌',
        'priority': '긴급',
        'due': '2026-07-02 목중',
        'bullets': ['표지영 스냅스 수정 완료.', '현재는 고객사 컨펌대기/목요일 중 컨펌 추적 단계.', '컨펌 완료 시 7/7(화)~7/12(일) 총 60건 발행 예정.', '컨펌 완료 시점에 따라 발행 시작일 지연 가능.', '표지영 현재진행은 헤븐리젤리 수정으로 이동.']
    },
    '비더후드': {'tone': 'focus', 'status': '높음 · 추가 20개 제작중 · 마무리권', 'stage': '제작/비축', 'priority': '높음', 'due': '2026-07-02', 'bullets': ['정희헌 메인.', '한은지 7/2 목요일 비더후드 지원/공동 작업 중.', '오늘 추가 20개 산출 시 이번주 물량 마무리 예상.', '완료 전 산출물/비축/예약 확인 필요.', '동아제약 상세 수정사항이 들어오면 정희헌 병행 충돌만 주의.']},
    '벤슨': {
        'tone': 'risk',
        'status': '높음 · 차주 추가발행 · 바리방식 검토',
        'stage': '추가발행/바리방식검토',
        'priority': '높음',
        'due': '2026-07-03 결정 / 7/6 시작',
        'bullets': ['여기성 메인.', '차주 추가 발행분은 7/6부터 시작 예정.', '고객사 기준이 빡빡해 프로그램 프바리 품질 리스크 큼.', '여기성 단독 손바리 지속 시 멘탈 부하 큼.', '기획팀 논의 이력 있음. 손바리/프바리 비율과 검수 기준 7/3까지 결정 필요.']
    },
    '최유정': {'tone': 'focus', 'status': '긴급 · 잔여 18개 · 김경은 단독진행', 'stage': '편집/잔여제작', 'priority': '긴급', 'due': '2026-07-03', 'bullets': ['김경은 혼자 진행 중.', '오늘 18개 더 나오면 이번주 물량 마무리.', '오늘 미달해도 내일 보완 가능성이 있어 운영상 가능권.', '정희헌 지원 현재진행 표시는 보류 처리.', '김경은 7/7 마지막 출근 예정이라 인수인계 리스크는 유지.']},
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
    '볼보': {'tone': 'focus', 'status': '높음 · 재택 제작 · 100개 목표', 'stage': '프로그램 바리/재택 제작', 'priority': '높음', 'due': '2026-07-03', 'bullets': ['최성진 1주일 재택근무, 집에서 볼보 진행 중.', '내일 7/3까지 볼보 100개 산출 목표.', '프로그램 바리라 가능권.', '볼보 고객사는 비교적 널널해 프바리 적용 가능.', '품질/중복 샘플 검수 필요.']},
    'CJ': {'tone': 'steady', 'bullets': ['한은지 메인.', '월/수/금 CJ 업무 고정.', '화/목은 타 프로젝트 지원 가능.', '7/2 목요일 현재 비더후드 추가 20개 작업 지원 중.']},
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
        'tone': 'focus',
        'status': '긴급 · 원본 8개 완료 · 수정중',
        'stage': '수정',
        'priority': '긴급',
        'due': '2026-07-02',
        'bullets': ['표지영이 7/1 야근으로 원본영상 8개 모두 완료.', '스냅스 수정 완료 후 현재 헤븐리젤리 수정 착수.', '후속 수정량과 완료 예상시각 확인 필요.', '스냅스는 수정 완료되어 고객사 컨펌대기로 전환.', '표지영 병목은 스냅스에서 헤븐리젤리 수정 대응으로 이동.']
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
    '여기성': '벤슨 메인. 차주 추가 발행분은 7/6부터 시작 예정. 고객사 기준이 빡빡해 프로그램 프바리 품질 리스크가 크고, 여기성 단독 손바리 지속 시 멘탈 부하가 큼. 손바리/프바리 혼합 비율과 검수 기준을 7/3까지 결정 필요.',
    '표지영': '스냅스 수정은 7/2 완료되어 고객사 컨펌대기로 전환. 현재 헤븐리젤리 수정 진행 중. 헤븐리젤리 원본 8개는 7/1 야근으로 완료했으며, 수정량/완료시각 확인 필요. 쿠쿠홈시스는 소스 재전달 이슈 보류.',
    '정희헌': '비더후드 추가 20개를 7/2 현재 한은지와 함께 작업 중. 완료 시 이번주 물량 마무리 예상. 동아제약은 컨펌 보낸 4개 전부 큰 수정 요청 수신, 고객사 상세 수정사항 대기.',
    '최성진': '볼보 메인. 7/2 기준 1주일 재택근무로 집에서 볼보 진행 중. 7/3까지 볼보 100개 산출 목표. 프로그램 바리라 가능권이며, 볼보 고객사는 비교적 널널하지만 품질/중복 검수는 필요.',
    '한은지': 'CJ 월/수/금 고정 업무. 화/목은 웬만하면 타 프로젝트 지원 가능. 7/2 목요일 현재 비더후드 추가 20개 작업을 정희헌과 지원/진행 중.',
    '김경은': '최유정 잔여 18개를 혼자 진행 중. 오늘 18개 추가 산출 시 이번주 마무리, 미달 시 내일 보완 가능. 아이돌종합도 보유하며 2026-07-07 마지막 출근 예정이라 인수인계 필요.',
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
        {'label': '표지영', 'title': '스냅스 수정완료 → 헤븐리젤리 수정 착수', 'body': '표지영은 스냅스 수정을 완료했고 스냅스는 고객사 컨펌대기로 전환. 현재는 헤븐리젤리 수정에 착수했으며 수정량/완료시각 확인 필요.'},
        {'label': '벤슨', 'title': '차주 추가발행 · 손바리/프바리 비율 결정 필요', 'body': '벤슨은 차주 추가 발행분이 7/6부터 시작 예정. 고객사 기준이 빡빡해 프로그램 프바리 품질 리스크가 크고, 여기성 단독 손바리 지속은 멘탈 부하가 큼. 손바리/프바리 비율과 검수 기준을 7/3까지 결정 필요.'},
        {'label': '볼보', 'title': '최성진 재택 · 7/3까지 100개 목표', 'body': '최성진은 일주일 재택근무로 집에서 볼보 진행 중. 내일 7/3까지 볼보 100개 산출 목표이며 프로그램 바리라 가능권. 품질/중복 샘플 검수 필요.'},
        {'label': '비더후드', 'title': '오늘 추가 20개 · 정희헌+한은지 작업중', 'body': '비더후드는 7/2 현재 정희헌·한은지가 작업 중. 오늘 20개 더 나오면 이번주 물량 마무리 예상. 완료 전 산출물/비축/예약 확인 필요.'},
        {'label': '최유정', 'title': '잔여 18개 · 김경은 단독진행', 'body': '최유정은 김경은 혼자 진행 중. 오늘 18개 더 나오면 이번주 마무리이며, 미달해도 내일까지 보완 가능성이 있어 가능권.'},
        {'label': '헤븐리젤리', 'title': '원본 8개 완료 · 수정중', 'body': '표지영이 7/1 야근으로 헤븐리젤리 원본 8개를 모두 완료했고, 7/2 스냅스 수정 완료 후 헤븐리젤리 수정에 착수. 후속 수정량/완료시각 확인 필요.'},
        {'label': '스냅스', 'title': '수정완료 · 컨펌대기', 'body': '표지영 스냅스 수정 완료. 현재는 고객사 컨펌대기이며, 목요일 중 컨펌 여부가 차주 60건 발행 시작을 좌우함.'},
        {'label': '상하목장', 'title': '1차 전달 완료 · 2차 신유빈 담당', 'body': '상하목장 1차 소스 40개는 전달 완료. 2차 소스 40개 전달은 금요일 7/3까지 신유빈이 담당. 표지영의 상하목장 소스 병목은 일부 해소.'},
        {'label': '동아제약', 'title': '4개 전부 큰 수정 요청 · 상세사항 대기', 'body': '동아제약은 컨펌 보낸 4개 모두 수정 요청 수신. 큰 수정 예정이며 고객사가 상세 수정사항을 별도 전달 예정. 일정 지연은 허용.'},
        {'label': '스냅스', 'title': '7/2 수정완료 → 컨펌 시 차주 60건', 'body': '스냅스는 7/2(목) 수정 완료 후 목요일 중 컨펌 완료 시 7/7(화)~7/12(일) 총 60건 전체 발행 예정. 컨펌 시점에 따라 시작일 지연 가능.'},
        {'label': '벤슨', 'title': '7/1 썸넬 테스트 1세트 추가', 'body': '벤슨 7/1 유10 및 신규 소구 반영과 함께 썸넬 테스트 1세트 추가. 여기성 메인 기준, 테스트 기준/적용 영상 확인 필요.'},
        {'label': '쿠쿠홈시스', 'title': '원본 1개 제작 일정 보류', 'body': '원래 7/1까지였던 원본 영상 1개 제작은 고객사 소스 재전달 이슈로 일단 연기. 새 소스/새 마감 확인 전까지 제작 보류이며, 7/3~7/4 유10 영향 재확인 필요.'},
        {'label': '듀오타이트', 'title': '이재은 제작 시작 · 7/3 메인 9건', 'body': '이재은이 듀오타이트 제작을 시작. 7/3(금) 메인영상 9건 마감 유지.'},
        {'label': '볼보', 'title': '과거 6/30 프로그램 바리 이력', 'body': '6/30에는 프로그램 바리 25개 제작 중으로 기록됐고, 7/2 최신 기준은 최성진 재택 환경에서 7/3까지 100개 산출 목표로 확대됨.'},
        {'label': '한손한끼', 'title': '일단 종료 · 운영 제외', 'body': '프로젝트 상태를 완료/종료로 변경. 6/30~7/4 반복 유5 물량은 영상팀 부하 계산에서 제외.'},
        {'label': '미닉스', 'title': '컨펌 완료 · 발행 페이즈', 'body': '원본 4개 컨펌 완료. 6/30 원본 4개 발행 후 7/1~7/4 하루 9개씩 바리에이션 발행.'},
        {'label': '듀오타이트 목표', 'title': '7/13 첫 라이브 목표', 'body': '1주차 최소 45건, 2주차 최소 47건. 최소 92건 발행과 목표 조회수 276,000 기준.'},
    ]

    # Latest operational bullets. Keep static overrides first so the generated
    # public briefing does not regress when older source logs are used.
    recent_updates = [
        {'heading': '2026-07-02 13:31 — 스냅스 수정 완료 / 헤븐리젤리 수정 착수', 'text': '표지영은 스냅스 수정을 완료했고 스냅스는 고객사 컨펌대기로 전환. 현재 헤븐리젤리 수정에 착수했으며, 수정량/완료 예상시각 확인 필요.'},
        {'heading': '2026-07-02 11:20 — 벤슨/볼보 바리에이션 운영 업데이트', 'text': '벤슨은 차주 추가 발행분에서 손바리/프바리 혼합 비율과 검수 기준 결정 필요. 볼보는 최성진 재택으로 7/3까지 100개 목표, 프로그램 바리라 가능권.'},
        {'heading': '2026-07-02 09:41 — 비더후드/최유정/헤븐리젤리/스냅스 오전 상태', 'text': '오전 기준 비더후드는 정희헌+한은지 작업중, 최유정은 김경은 단독 잔여 18개 진행. 헤븐리젤리는 원본 8개 완료/수정대기였고, 이후 13:31 최신 기준 표지영은 헤븐리젤리 수정으로 이동.'},
        {'heading': '2026-07-01 18:01 — 상하목장/동아제약 상태 변경', 'text': '상하목장 1차 소스는 전달 완료, 2차 소스 40개는 7/3까지 신유빈 담당. 동아제약은 컨펌 보낸 4개 모두 큰 수정 요청 수신, 상세 수정사항 대기이며 일정 지연은 허용.'},
        {'heading': '2026-07-01 15:45 — 스냅스 차주 발행 조건', 'text': '스냅스는 7/2 수정 완료 후 목요일 중 컨펌 완료 시 7/7~7/12 총 60건 발행 예정. 컨펌 지연 시 시작일도 밀릴 수 있음.'},
        {'heading': '2026-07-01 14:22 — 헤븐리젤리 신규/스냅스 수정', 'text': '당시 헤븐리젤리 원본 8개와 스냅스 수정이 7/2 마감으로 잡혔고 표지영 과부하를 주의했음. 7/2 13:31 최신 기준 스냅스 수정은 완료, 헤븐리젤리는 수정중.'},
        {'heading': '2026-07-01 00:00 — 벤슨 썸넬 테스트 추가', 'text': '벤슨 7/1 업무에 썸넬 테스트 1세트 추가. 여기성 메인, 신규 소구 반영과 함께 테스트 기준/적용 영상 확인 필요.'},
        {'heading': '2026-06-30 23:39 — 스냅스 원본 완료/상하목장 누락 정정', 'text': '스냅스 원본 6개 제작 완료 이력. 이후 7/1 수정 요청 반영, 7/2 13:31 기준 수정 완료/컨펌대기로 전환. 상하목장은 당시 표지영 소스 수집으로 누락 정정했고 7/1 18:01 기준 2차는 신유빈 담당.'},
        {'heading': '2026-06-30 17:34 — 쿠쿠홈시스 소스 이슈로 보류', 'text': '쿠쿠홈시스 원본 1개는 원래 7/1까지였으나 고객사 소스 재전달 이슈로 일단 연기. 새 소스/새 마감 확인 전까지 제작 보류이며 7/3~7/4 유10 영향 재확인 필요.'},
        {'heading': '2026-06-30 17:16 — 동아제약 과거 제작 예상', 'text': '동아제약은 6/30 당시 제작 진행으로 기록됐으나, 7/1 18:01 최신 기준 컨펌 보낸 4개 전부 큰 수정 요청 수신 및 상세 수정사항 대기 상태.'},
        {'heading': '2026-06-30 15:09 — 비더후드 7/2분 비축 이력', 'text': '과거 7/2 업로드분까지 비축 완료로 기록. 7/2 최신 기준은 정희헌+한은지가 추가 20개 작업 중이며 완료 시 이번주 마무리 예상.'},
        {'heading': '2026-06-30 14:41 — 이재은 듀오타이트 제작 시작', 'text': '이재은이 벤슨 지원을 마무리하고 듀오타이트 제작을 시작. 듀오타이트는 메인영상 9건 제작 진행중으로 전환, 7/3(금) 마감 유지.'},
        {'heading': '2026-06-30 14:00 — 한은지 지원 가능 패턴', 'text': '한은지는 월/수/금 CJ 고정, 화/목 타 프로젝트 지원 가능. 7/2 최신 기준 목요일 비더후드 추가 20개 작업을 정희헌과 진행 중.'},
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
            'lastUpdated': '2026-07-02 13:31 KST · 스냅스 수정완료 · 헤븐리젤리 수정 착수',
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
