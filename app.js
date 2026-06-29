const toneLabels = {
  risk: '병목 주의',
  focus: '집중 작업',
  waiting: '대기',
  steady: '진행중',
};

const boardColumns = [
  { id: 'risk', title: '병목 주의', desc: '휴무·지원 공백·컨펌 대기처럼 오늘 먼저 봐야 하는 항목' },
  { id: 'focus', title: '집중 작업', desc: '담당 전환 또는 마감 전 집중 제작이 필요한 항목' },
  { id: 'waiting', title: '대기', desc: '자료/복귀/착수 순서 확인이 필요한 항목' },
  { id: 'steady', title: '진행중', desc: '오너가 잡혀 있고 특이 리스크가 낮은 항목' },
];

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

function countByTone(projects, tone) {
  return projects.filter(project => (project.tone || 'steady') === tone).length;
}

function renderPills(data) {
  const projects = data.projects || [];
  const stats = data.stats || {};
  const items = [
    ['프로젝트', stats.activeProjects ?? projects.length],
    ['병목', stats.riskProjects ?? countByTone(projects, 'risk')],
    ['집중', countByTone(projects, 'focus')],
    ['팀원', stats.teamMembers ?? (data.people || []).length],
  ];
  const wrap = $('#heroPills');
  wrap.innerHTML = '';
  items.forEach(([label, value]) => {
    const item = document.createElement('div');
    item.className = 'metric';
    const strong = document.createElement('strong');
    strong.textContent = value;
    const span = document.createElement('span');
    span.textContent = label;
    item.append(strong, span);
    wrap.appendChild(item);
  });
}

function renderKeyChanges(items) {
  const wrap = $('#keyChanges');
  wrap.innerHTML = '';
  (items || []).forEach(item => {
    const card = document.createElement('article');
    card.className = 'change-item';
    const label = document.createElement('span');
    label.className = 'change-label';
    label.textContent = safe(item.label);
    const title = document.createElement('h3');
    title.textContent = safe(item.title);
    const body = document.createElement('p');
    body.textContent = safe(item.body);
    card.append(label, title, body);
    wrap.appendChild(card);
  });
}

function createProjectCard(project) {
  const node = $('#projectTemplate').content.cloneNode(true);
  const card = $('.project-card', node);
  const tone = project.tone || 'steady';
  card.dataset.tone = tone;
  $('.status-badge', node).textContent = toneLabels[tone] || safe(project.status);
  $('h3', node).textContent = safe(project.title);
  $('.owner', node).textContent = safe(project.owner || '미정');
  $('.stage-pill', node).textContent = safe(project.stage || project.status || '상태 확인');
  $('.due-pill', node).textContent = project.due && project.due !== '미정' ? `일정 ${project.due}` : '일정 미정';
  const list = $('.project-bullets', node);
  list.innerHTML = '';
  (project.bullets || ['세부 상태 확인 필요']).slice(0, 4).forEach(text => {
    const li = document.createElement('li');
    li.textContent = safe(text);
    list.appendChild(li);
  });
  return node;
}

function renderProjects(projects) {
  const grid = $('#projectGrid');
  grid.innerHTML = '';
  boardColumns.forEach(column => {
    const projectsForColumn = projects.filter(project => (project.tone || 'steady') === column.id);
    const section = document.createElement('section');
    section.className = 'board-column';
    section.dataset.tone = column.id;
    section.innerHTML = `
      <div class="column-head">
        <h3>${column.title}</h3>
        <span>${projectsForColumn.length}</span>
      </div>
      <p class="column-desc">${column.desc}</p>
      <div class="card-stack"></div>
    `;
    const stack = $('.card-stack', section);
    projectsForColumn.forEach(project => stack.appendChild(createProjectCard(project)));
    grid.appendChild(section);
  });
}

function renderPeople(people) {
  const grid = $('#peopleGrid');
  grid.innerHTML = '';
  (people || []).forEach(person => {
    const node = $('#personTemplate').content.cloneNode(true);
    const card = $('.person-card', node);
    card.dataset.tone = person.tone || 'steady';
    $('.avatar', node).textContent = initials(person.name);
    $('h3', node).textContent = safe(person.name);
    $('.role', node).textContent = safe(person.role || '팀원');
    $('.capacity', node).textContent = safe(person.capacity || '상태 확인 필요');
    const stack = $('.task-stack', node);
    stack.innerHTML = '';
    const tasks = person.tasks || [];
    if (!tasks.length) {
      const chip = document.createElement('span');
      chip.className = 'task-chip';
      chip.textContent = '현재 표시 업무 없음';
      stack.appendChild(chip);
    } else {
      tasks.slice(0, 4).forEach(task => {
        const chip = document.createElement('span');
        chip.className = 'task-chip';
        chip.textContent = `${safe(task.title)} · ${safe(task.status)}`;
        stack.appendChild(chip);
      });
    }
    grid.appendChild(node);
  });
}

function renderUpdates(updates) {
  const list = $('#updatesList');
  list.innerHTML = '';
  (updates || []).forEach(update => {
    const item = document.createElement('article');
    item.className = 'timeline-item';
    const heading = document.createElement('strong');
    heading.textContent = safe(update.heading).replace('2026-06-29 — ', '');
    const body = document.createElement('p');
    body.textContent = safe(update.text);
    item.append(heading, body);
    list.appendChild(item);
  });
}

function wireFilters() {
  $$('.filter').forEach(button => {
    button.addEventListener('click', () => {
      $$('.filter').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      const filter = button.dataset.filter;
      $$('.board-column').forEach(column => {
        column.hidden = filter !== 'all' && column.dataset.tone !== filter;
      });
    });
  });
}

async function init() {
  const response = await fetch('./data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`data.json ${response.status}`);
  const data = await response.json();
  document.title = data.meta?.title || '영상팀 운영상황판';
  renderPills(data);
  renderKeyChanges(data.keyChanges || []);
  renderProjects(data.projects || []);
  renderPeople(data.people || []);
  renderUpdates(data.recentUpdates || []);
  wireFilters();
  $('#lastUpdated').textContent = data.meta?.lastUpdated || '';
  $('#designRef').textContent = data.meta?.designReference || '';
}

init().catch(error => {
  console.error(error);
  const warning = document.createElement('div');
  warning.style.cssText = 'margin:16px;padding:16px;border-radius:12px;background:#fff0f0;color:#991b1b;font-weight:700;position:relative;z-index:99;';
  warning.textContent = `데이터를 불러오지 못했습니다: ${safe(error.message)}`;
  document.body.prepend(warning);
});
