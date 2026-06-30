const toneLabels = {
  risk: '병목',
  focus: '집중',
  waiting: '대기',
  steady: '진행',
};

const toneOrder = ['risk', 'focus', 'waiting', 'steady'];

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function safe(text) {
  return text == null ? '' : String(text);
}

function initials(name) {
  const s = safe(name).replace(/\s+/g, '');
  if (!s) return '?';
  return s.length >= 2 ? s.slice(-2) : s;
}

function shortDate(date) {
  const value = safe(date);
  if (!value || value === '미정') return '미정';
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return value;
  return `${Number(match[2])}/${Number(match[3])}`;
}

function countByTone(projects, tone) {
  return projects.filter(project => (project.tone || 'steady') === tone).length;
}

function taskCount(people) {
  return (people || []).reduce((sum, person) => sum + (person.tasks || []).length, 0);
}

function firstAction(project) {
  const bullets = project.bullets || [];
  return bullets[0] || project.status || '상태 확인 필요';
}

function detailText(project) {
  const bullets = (project.bullets || []).slice(1, 4);
  if (!bullets.length) return safe(project.status || '세부 체크 필요');
  return bullets.join(' / ');
}

function renderSummary(data) {
  const projects = data.projects || [];
  const people = data.people || [];
  const cards = [
    { label: '프로젝트', value: data.stats?.activeProjects ?? projects.length, sub: '운영 테이블 기준' },
    { label: '병목', value: data.stats?.riskProjects ?? countByTone(projects, 'risk'), sub: '오늘 우선 확인' },
    { label: '집중', value: countByTone(projects, 'focus'), sub: '마감 전 집중' },
    { label: '팀원', value: data.stats?.teamMembers ?? people.length, sub: `${taskCount(people)}개 표시 업무` },
  ];

  const wrap = $('#summaryCards');
  wrap.innerHTML = '';
  cards.forEach(card => {
    const node = document.createElement('article');
    node.className = 'summary-card';
    node.innerHTML = `
      <span>${card.label}</span>
      <strong>${card.value}</strong>
      <em>${card.sub}</em>
    `;
    wrap.appendChild(node);
  });
}

function priorityClass(project) {
  if ((project.priority || '').includes('긴급') || project.tone === 'risk') return 'critical';
  if ((project.priority || '').includes('높음') || project.tone === 'focus') return 'high';
  if (project.tone === 'waiting') return 'waiting';
  return 'normal';
}

function renderProjects(projects) {
  const rows = $('#projectRows');
  rows.innerHTML = '';

  const sorted = [...(projects || [])].sort((a, b) => {
    const ta = toneOrder.indexOf(a.tone || 'steady');
    const tb = toneOrder.indexOf(b.tone || 'steady');
    if (ta !== tb) return ta - tb;
    return safe(a.due).localeCompare(safe(b.due), 'ko');
  });

  sorted.forEach((project, index) => {
    const tone = project.tone || 'steady';
    const row = document.createElement('tr');
    row.className = 'project-row';
    row.dataset.tone = tone;
    row.innerHTML = `
      <td>
        <span class="status-dot ${tone}"></span>
        <span class="status-chip ${priorityClass(project)}">${toneLabels[tone] || '진행'}</span>
      </td>
      <td>
        <div class="project-name">
          <span class="row-index">${String(index + 1).padStart(2, '0')}</span>
          <strong>${safe(project.title)}</strong>
        </div>
      </td>
      <td><span class="owner-chip">${safe(project.owner || '미정')}</span></td>
      <td><span class="stage-text">${safe(project.stage || '미정')}</span></td>
      <td><span class="date-pill">${shortDate(project.due)}</span></td>
      <td class="action-cell">${safe(firstAction(project))}</td>
      <td class="detail-cell">${safe(detailText(project))}</td>
    `;
    rows.appendChild(row);
  });
}

function renderKeyChanges(items) {
  const wrap = $('#keyChanges');
  wrap.innerHTML = '';
  (items || []).forEach((item, index) => {
    const card = document.createElement('article');
    card.className = 'change-card';
    card.innerHTML = `
      <span class="change-no">0${index + 1}</span>
      <div>
        <small>${safe(item.label)}</small>
        <strong>${safe(item.title)}</strong>
        <p>${safe(item.body)}</p>
      </div>
    `;
    wrap.appendChild(card);
  });
}

function renderPeopleCompact(people) {
  const wrap = $('#peopleCompact');
  wrap.innerHTML = '';
  (people || []).slice(0, 9).forEach(person => {
    const item = document.createElement('article');
    item.className = 'person-mini';
    item.dataset.tone = person.tone || 'steady';
    const tasks = person.tasks || [];
    item.innerHTML = `
      <span class="avatar">${initials(person.name)}</span>
      <div>
        <strong>${safe(person.name)}</strong>
        <p>${tasks[0] ? safe(tasks[0].title) : safe(person.capacity).slice(0, 38)}</p>
      </div>
      <em>${tasks.length || 0}</em>
    `;
    wrap.appendChild(item);
  });
}

function renderPeopleTable(people) {
  $('#peopleCount').textContent = `${(people || []).length}명`;
  const rows = $('#peopleRows');
  rows.innerHTML = '';
  (people || []).forEach(person => {
    const tasks = person.tasks || [];
    const row = document.createElement('tr');
    row.className = 'person-row';
    row.dataset.tone = person.tone || 'steady';
    row.innerHTML = `
      <td>
        <div class="person-name">
          <span class="avatar">${initials(person.name)}</span>
          <div><strong>${safe(person.name)}</strong><small>${safe(person.role || '팀원')}</small></div>
        </div>
      </td>
      <td>${safe(person.capacity)}</td>
      <td>${tasks.length ? tasks.map(task => `<span class="task-token">${safe(task.title)} · ${safe(task.status)}</span>`).join('') : '<span class="task-token muted">표시 업무 없음</span>'}</td>
    `;
    rows.appendChild(row);
  });
}

function renderUpdates(updates) {
  const list = $('#updatesList');
  list.innerHTML = '';
  (updates || []).forEach(update => {
    const item = document.createElement('article');
    item.className = 'update-item';
    item.innerHTML = `
      <strong>${safe(update.heading).replace(/^\d{4}-\d{2}-\d{2} — /, '')}</strong>
      <p>${safe(update.text)}</p>
    `;
    list.appendChild(item);
  });
}

function renderCalendar(days) {
  const wrap = $('#calendarGrid');
  if (!wrap) return;
  wrap.innerHTML = '';

  (days || []).forEach(day => {
    const card = document.createElement('article');
    card.className = `calendar-day${day.isToday ? ' today' : ''}`;
    const events = (day.events || []).slice(0, 5);
    const changes = (day.changes || []).slice(0, 3);
    card.innerHTML = `
      <div class="calendar-head">
        <div>
          <span>${safe(day.weekday)}</span>
          <strong>${safe(day.label)}</strong>
        </div>
        <em>${safe(day.load)}</em>
      </div>
      <div class="calendar-block">
        <small>누가 뭐 했는지</small>
        ${events.length ? events.map(event => `
          <div class="calendar-event">
            <b>${safe(event.person)}</b>
            <p>${safe(event.project)} · ${safe(event.title)}</p>
            <i>${safe(event.status)}</i>
          </div>
        `).join('') : '<p class="calendar-empty">표시 업무 없음</p>'}
      </div>
      <div class="calendar-block changes">
        <small>변경 로그</small>
        ${changes.length ? changes.map(change => `
          <div class="calendar-change">
            <b>${safe(change.time || 'log')}</b>
            <p>${safe(change.text)}</p>
          </div>
        `).join('') : '<p class="calendar-empty">변경 로그 없음</p>'}
      </div>
    `;
    wrap.appendChild(card);
  });
}

function wireFilters() {
  $$('.filter').forEach(button => {
    button.addEventListener('click', () => {
      $$('.filter').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      const filter = button.dataset.filter;
      $$('.project-row').forEach(row => {
        row.hidden = filter !== 'all' && row.dataset.tone !== filter;
      });
    });
  });
}

async function init() {
  const response = await fetch('./data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`data.json ${response.status}`);
  const data = await response.json();

  document.title = data.meta?.title || '영상팀 운영상황판';
  $('#lastUpdated').textContent = data.meta?.lastUpdated || '';
  $('#designRef').textContent = data.meta?.designReference || '';

  renderSummary(data);
  renderProjects(data.projects || []);
  renderKeyChanges(data.keyChanges || []);
  renderPeopleCompact(data.people || []);
  renderPeopleTable(data.people || []);
  renderUpdates(data.recentUpdates || []);
  renderCalendar(data.changeCalendar || []);
  wireFilters();
}

init().catch(error => {
  console.error(error);
  const warning = document.createElement('div');
  warning.className = 'load-warning';
  warning.textContent = `데이터를 불러오지 못했습니다: ${safe(error.message)}`;
  document.body.prepend(warning);
});
