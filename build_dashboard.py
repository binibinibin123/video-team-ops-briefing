#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from datetime import datetime

BASE = Path('/mnt/c/Users/82103/Documents/video_team_ops')
OUT = BASE / 'web_dashboard'

PROJECTS = BASE / 'video_projects.csv'
TASKS = BASE / 'tasks.csv'
MEMBERS = BASE / 'team_members.csv'
DECISIONS = BASE / 'decision_log.md'
BRIEFINGS = BASE / 'daily_briefings.md'


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
    '스냅스': {'tone': 'waiting', 'bullets': ['표지영 쿠쿠홈시스 메인 등록으로 우선순위 재확인 필요.', '기존 스냅스 원본 6개 일정은 별도 확인.', '신유빈은 지원/관리 기록 유지.']},
    '비더후드': {'tone': 'risk', 'bullets': ['표지영 지원 중단.', '정희헌 메인 중심으로 재정리.', '지원 공백 체크 필요.']},
    '벤슨': {'tone': 'steady', 'bullets': ['여기성 메인 중심.', '이재은 지원은 종료.', '신규 소구는 수요일부터 반영 예정.']},
    '최유정': {'tone': 'risk', 'bullets': ['김경은 휴무.', '정희헌과 이재은이 지원중.', '세이브본 부족 체크 필요.']},
    '동아제약': {'tone': 'waiting', 'bullets': ['남은 기획/자료 수급 대기.', '자료 들어오면 정희헌 제작 대응.', '비더후드와 병행이라 병목 주의.']},
    '삼양': {'tone': 'steady', 'bullets': ['탱글 3번 바리에이션 완료.', '4번 컨펌 추적.', '5/6번 후속 제작 병행.']},
    '미닉스': {
        'tone': 'risk',
        'status': '긴급 · 발행/바리에이션 · 컨펌완료',
        'stage': '발행/바리에이션',
        'priority': '긴급',
        'due': '2026-07-03',
        'bullets': ['원본 영상 4개 컨펌 완료.', '6/30(화) 원본 4개 발행.', '각 원본당 9개씩 총 36개 바리에이션.', '7/1~7/4 하루 9개 업로드, 제작 완료는 7/3(금) 퇴근 전.']
    },
    '볼보': {'tone': 'steady', 'bullets': ['최성진 메인으로 계속 진행.', '별도 지원 이슈 없음.']},
    'CJ': {'tone': 'steady', 'bullets': ['한은지 메인/현재진행.', '특이 리스크 없음.']},
    '아이돌종합': {'tone': 'waiting', 'bullets': ['김경은 휴무로 대기.', '복귀 후 재확인 필요.']},
    '듀오타이트': {'tone': 'waiting', 'bullets': ['이재은 메인 배정.', '현재 최유정 지원으로 착수 지연 가능.']},
    '뷰엑스 홍보영상': {'tone': 'focus', 'bullets': ['신유빈 관리중.', '팀 업무 분배와 함께 체크.']},
    '헤븐리젤리': {'tone': 'waiting', 'bullets': ['표지영 쿠쿠홈시스 집중 마감 이후 재확인.', '후속 우선순위 확인 필요.']},
    '한손한끼': {'tone': 'steady', 'bullets': ['오너/세부 제작 상태 확인 필요.', '반복 운영 항목으로 별도 체크.']},
    '쿠쿠홈시스': {
        'owner': '표지영',
        'tone': 'focus',
        'status': '긴급 · 제작/바리에이션 · 진행중',
        'stage': '제작/바리에이션',
        'priority': '긴급',
        'due': '2026-07-03',
        'bullets': ['표지영 메인 등록.', '원본 영상 1개: 7/1(수) 퇴근 전.', '바리에이션 14개: 7/3(금) 퇴근 전.', '이번 주 집중 마감으로 별도 추적.']
    },
    '쿠쿠홍시스': {
        'title': '쿠쿠홈시스',
        'owner': '표지영',
        'tone': 'focus',
        'status': '긴급 · 제작/바리에이션 · 진행중',
        'stage': '제작/바리에이션',
        'priority': '긴급',
        'due': '2026-07-03',
        'bullets': ['표지영 메인 등록.', '원본 영상 1개: 7/1(수) 퇴근 전.', '바리에이션 14개: 7/3(금) 퇴근 전.', '이번 주 집중 마감으로 별도 추적.']
    },
}

PEOPLE_OVERRIDES = {
    '신유빈': '팀 리드. 업무 분배/우선순위 판단, 스냅스 지원·관리 기록 유지, 쿠쿠홈시스/미닉스 주간 마감 체크, 뷰엑스 홍보영상 관리중.',
    '이재은': '벤슨 지원 종료. 현재 최유정 지원중. 듀오타이트 메인 착수는 최유정 지원 이후로 밀릴 수 있음.',
    '여기성': '벤슨 메인. 스냅스 메인에서 해제되어 벤슨 운영과 신규 소구 반영에 집중.',
    '표지영': '쿠쿠홈시스 메인 등록. 원본 1개는 7/1(수) 퇴근 전, 바리에이션 14개는 7/3(금) 퇴근 전까지 완료. 스냅스 후속 우선순위는 재확인 필요.',
    '정희헌': '비더후드 메인. 최유정은 이재은도 합류했지만, 동아제약 자료 수급 후 제작까지 겹쳐 병목 주의.',
    '최성진': '볼보 메인으로 계속 진행.',
    '한은지': 'CJ 메인으로 계속 진행.',
    '김경은': '현재 휴무. 아이돌종합/최유정 메인이나 최유정은 지원 인력으로 커버 중.',
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
        '미닉스 7월 1주차 40건': '미닉스 7월 1주차 컨펌 대응',
        '동아제약 7/1 제작분 3건': '동아제약 7/1 제작분 준비',
    }
    return replacements.get(title or '', title or '')


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


def build():
    projects_raw = read_csv(PROJECTS)
    tasks_raw = read_csv(TASKS)
    members_raw = read_csv(MEMBERS)

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
            'bullets': bullets[:4] or ['세부 상태 확인 필요'],
        })

    people_cards = []
    for m in members_raw:
        if str(m.get('active','')).upper() != 'TRUE':
            continue
        name = m.get('name','')
        tasks = tasks_by_assignee.get(name, [])
        task_summaries = []
        for t in tasks[:4]:
            task_summaries.append({
                'title': display_task_title(t.get('task_title','')),
                'status': t.get('status',''),
                'priority': t.get('priority',''),
                'due': t.get('due_date',''),
            })
        capacity = PEOPLE_OVERRIDES.get(name) or compact_note(m.get('capacity_notes') or m.get('notes') or '상태 확인 필요', 180)
        people_cards.append({
            'name': name,
            'role': m.get('role') or '팀원',
            'capacity': capacity,
            'tasks': task_summaries,
            'tone': 'risk' if any(k in capacity for k in ['병목','휴무','긴급','부족','컨펌대기']) else ('focus' if name in ['표지영','이재은','신유빈'] else 'steady'),
        })

    key_changes = [
        {'label': '쿠쿠홈시스', 'title': '표지영 메인 등록', 'body': '원본 영상 1개는 7/1(수) 퇴근 전, 바리에이션 14개는 7/3(금) 퇴근 전까지 완료.'},
        {'label': '미닉스', 'title': '원본 4개 컨펌 완료', 'body': '6/30(화) 원본 4개 발행. 각 원본당 9개씩 총 36개 바리에이션 진행.'},
        {'label': '미닉스 일정', 'title': '수~토 업로드 / 금요일 제작 완료', 'body': '7/1(수)부터 7/4(토)까지 하루 9개 업로드 기준. 제작·검수는 7/3(금) 퇴근 전까지 끝내야 함.'},
    ]

    # Recent operational bullets from logs
    recent_updates = extract_latest_markdown(BRIEFINGS, '이재은 지원 전환 반영', max_lines=6)
    if not recent_updates:
        recent_updates = extract_latest_markdown(BRIEFINGS, None, max_lines=6)

    stats = {
        'activeProjects': len([p for p in projects_raw if p.get('status') in {'진행중','대기','컨펌대기'}]),
        'activeTasks': len(active_tasks),
        'riskProjects': len([p for p in projects_raw if classify_project(p) == 'risk']),
        'teamMembers': len([m for m in members_raw if str(m.get('active','')).upper() == 'TRUE']),
    }

    data = {
        'meta': {
            'title': '영상팀 운영상황판',
            'lastUpdated': '2026-06-29 · 쿠쿠홈시스/미닉스 마감 일정 반영',
            'designReference': 'VoltAgent awesome-design-md 직접 적용: Airtable DESIGN.md 업무카드 + Notion DESIGN.md DB 태그 + Miro DESIGN.md sticky note',
            'privacyNote': 'GitHub Pages 공개 링크용 정적 브리핑. 검색 노출 최소화를 위해 noindex 메타 적용.',
        },
        'stats': stats,
        'keyChanges': key_changes,
        'projects': project_cards,
        'people': people_cards,
        'recentUpdates': recent_updates,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    build()
    print(OUT / 'data.json')
