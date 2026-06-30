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
    '벤슨': {'tone': 'focus', 'bullets': ['여기성 메인 중심.', '6/30 오전 현재 이재은 지원 중.', '오후에는 이재은이 듀오타이트로 전환 예정.', '신규 소구는 수요일부터 반영 예정.']},
    '최유정': {'tone': 'risk', 'status': '긴급 · 편집 · 잔여 확인', 'stage': '편집/잔여 확인', 'bullets': ['김경은 오늘 출근.', '정희헌 중심으로 잔여/세이브본 확인 필요.', '이재은은 현재 벤슨 지원 후 오후 듀오타이트 예정이라 추가 지원 여력 낮음.', '김경은 7/7 마지막 출근 예정이라 인수인계 필요.']},
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
    '볼보': {'tone': 'focus', 'status': '높음 · 제작/바리에이션 · 진행중', 'stage': '제작/바리에이션', 'priority': '높음', 'due': '2026-06-30', 'bullets': ['최성진 메인으로 진행.', '프로그램을 이용한 바리에이션 영상 25개 오늘 제작 중.', '산출물 품질/중복 검수 체크 필요.']},
    'CJ': {'tone': 'steady', 'bullets': ['한은지 메인/현재진행.', '특이 리스크 없음.']},
    '아이돌종합': {'tone': 'waiting', 'bullets': ['김경은 오늘 출근.', '7/7 마지막 출근 예정.', '인수인계/후임 오너 확인 필요.']},
    '듀오타이트': {
        'owner': '이재은',
        'tone': 'focus',
        'status': '긴급 · 기획대기/오후착수 · 메인담당',
        'stage': '기획대기/오후착수',
        'priority': '긴급',
        'due': '2026-07-03',
        'bullets': [
            '이재은 메인. 오전 현재 벤슨 지원 중.',
            '기획팀 기획안은 6/30 오후 전달 예정 → 오후 착수 예상.',
            '메인영상 9건: 7/3(금)까지 완료 목표.',
            '7/13(월) 첫 라이브 목표. 컨펌이 빨라지면 일정 단축 가능.',
            '1주차 45건 + 2주차 47건 = 최소 92건 발행.',
            '3주차는 조회수 추이를 반영해 추가 바리에이션 제작/발행.',
            '목표 조회수 276,000.',
        ]
    },
    '뷰엑스 홍보영상': {'tone': 'focus', 'bullets': ['신유빈 관리중.', '팀 업무 분배와 함께 체크.']},
    '헤븐리젤리': {'tone': 'waiting', 'bullets': ['표지영 쿠쿠홈시스 집중 마감 이후 재확인.', '후속 우선순위 확인 필요.']},
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
    '이재은': '현재 벤슨 지원 중. 기획팀에서 듀오타이트 기획안이 6/30 오후 전달 예정이라 오후부터 듀오타이트 전환 예상. 7/3(금)까지 메인영상 9건, 7/13(월) 첫 라이브 목표. 1주차 최소 45건/2주차 최소 47건, 최소 92건 발행과 목표 조회수 276,000 기준.',
    '여기성': '벤슨 메인. 6/30 유20 피크에 오전 이재은 지원 중이나 오후부터는 이재은이 듀오타이트로 전환 예정. 신규 소구 반영까지 체크.',
    '표지영': '쿠쿠홈시스 메인 등록. 원본 1개는 7/1(수) 퇴근 전, 바리에이션 14개는 7/3(금) 퇴근 전까지 완료. 스냅스 후속 우선순위는 재확인 필요.',
    '정희헌': '비더후드 메인. 최유정 잔여 지원과 동아제약 자료 수급 후 제작이 겹쳐 병목 주의.',
    '최성진': '볼보 메인. 6/30 프로그램을 이용한 바리에이션 영상 25개 제작 중. 산출물 품질/중복 검수 체크 필요.',
    '한은지': 'CJ 메인으로 계속 진행.',
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
            'bullets': bullets[:7] or ['세부 상태 확인 필요'],
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
        if name == '이재은':
            task_summaries = [
                {'title': '벤슨 오전 지원', 'status': '진행중', 'priority': '높음', 'due': '2026-06-30'},
                {'title': '듀오타이트 기획안 수급/오후 착수', 'status': '오후 예정', 'priority': '긴급', 'due': '2026-06-30'},
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
        {'label': '이재은', 'title': '벤슨 오전 지원 → 듀오타이트 오후 착수', 'body': '현재 벤슨 지원 중. 기획팀 듀오타이트 기획안은 오후 전달 예정이라 오후부터 듀오타이트 전환 예상.'},
        {'label': '볼보', 'title': '프로그램 바리에이션 25개 제작 중', 'body': '최성진이 오늘 프로그램을 이용한 바리에이션 영상 25개 제작 중. 품질/중복 검수 필요.'},
        {'label': '한손한끼', 'title': '일단 종료 · 운영 제외', 'body': '프로젝트 상태를 완료/종료로 변경. 6/30~7/4 반복 유5 물량은 영상팀 부하 계산에서 제외.'},
        {'label': '듀오타이트', 'title': '기획안 오후 도착 후 착수', 'body': '이재은 메인. 오전은 벤슨 지원, 오후 기획안 수급 후 메인영상 9건을 7/3(금)까지 완료 목표.'},
        {'label': '미닉스', 'title': '컨펌 완료 · 발행 페이즈', 'body': '원본 4개 컨펌 완료. 6/30 원본 4개 발행 후 7/1~7/4 하루 9개씩 바리에이션 발행.'},
        {'label': '김경은', 'title': '오늘 출근 · 7/7 마지막 출근', 'body': '6/29 휴무였고 6/30 출근. 최유정/아이돌종합 인수인계 플랜 필요.'},
        {'label': '듀오타이트 목표', 'title': '7/13 첫 라이브 목표', 'body': '1주차 최소 45건, 2주차 최소 47건. 최소 92건 발행과 목표 조회수 276,000 기준.'},
    ]

    # Latest operational bullets. Keep static overrides first so the generated
    # public briefing does not regress when older source logs are used.
    recent_updates = [
        {'heading': '2026-06-30 10:53 — 이재은 벤슨 지원/듀오타이트 오후 착수', 'text': '이재은은 현재 벤슨 지원 중. 기획팀에서 듀오타이트 기획안이 오후 전달 예정이라 오후부터 듀오타이트 착수 예상.'},
        {'heading': '2026-06-30 10:53 — 볼보 바리에이션 제작', 'text': '최성진이 프로그램을 이용한 볼보 바리에이션 영상 25개를 오늘 제작 중. 산출물 품질/중복 검수 체크 필요.'},
        {'heading': '2026-06-30 — 한손한끼 종료 반영', 'text': '한손한끼는 일단 종료. 프로젝트 상태를 완료/종료로 변경하고, 6/30~7/4 반복 유5 물량은 영상팀 부하 계산에서 제외.'},
        {'heading': '2026-06-30 — 오늘 업무 종료', 'text': '6/29 당일 업무는 종료 상태로 기록하고, 이후 새 착수 포커스는 듀오타이트로 전환.'},
        {'heading': '2026-06-30 — 듀오타이트 메인담당 전환', 'text': '이재은: 듀오타이트 메인 담당자. 6/30 오전은 벤슨 지원 중이며, 기획안 오후 도착 후 메인영상 9건을 7/3(금)까지 완료 목표.'},
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
            'lastUpdated': '2026-06-30 10:53 KST · 이재은 벤슨 지원/듀오타이트 오후 착수/볼보 25개 제작 반영',
            'designReference': 'VoltAgent awesome-design-md 직접 적용: Airtable DESIGN.md 테이블/헤어라인 + Notion DESIGN.md DB 속성 태그 + Linear.app DESIGN.md 다크 사이드레일',
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
