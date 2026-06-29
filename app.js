const toneLabels = {
  risk: '병목 주의',
  focus: '집중 작업',
  waiting: '대기',
  steady: '진행중',
};

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

function renderPills(stats) {
  const items = [
    ['프로젝트', stats.activeProjects],
    ['진행 업무', stats.activeTasks],
    ['리스크', stats.riskProjects],
    ['팀원', stats.teamMembers],
  ];
  $('#heroPills').innerHTML = items.map(([label, value]) => `
    <span class="hero-pill"><strong>${value}</strong><span>${label}</span></span>
  `).join('');
}

function renderKeyChanges(items) {
  $('#keyChanges').innerHTML = items.map(item => `
    <article class="change-item">
      <span class="change-label">${safe(item.label)}</span>
      <h3>${safe(item.title)}</h3>
      <p>${safe(item.body)}</p>
    </article>
  `).join('');
}

function renderProjects(projects) {
  const grid = $('#projectGrid');
  const template = $('#projectTemplate');
  grid.innerHTML = '';
  projects.forEach(project => {
    const node = template.content.cloneNode(true);
    const card = $('.project-card', node);
    card.dataset.tone = project.tone || 'steady';
    $('.status-badge', node).textContent = toneLabels[project.tone] || safe(project.status);
    $('h3', node).textContent = safe(project.title);
    $('.owner', node).textContent = safe(project.owner);
    $('ul', node).innerHTML = (project.bullets || []).map(b => `<li>${safe(b)}</li>`).join('');
    $('.project-foot', node).textContent = `${safe(project.status)} · 마감 ${safe(project.due)}`;
    grid.appendChild(node);
  });
}

function renderPeople(people) {
  const grid = $('#peopleGrid');
  const template = $('#personTemplate');
  grid.innerHTML = '';
  people.forEach(person => {
    const node = template.content.cloneNode(true);
    const card = $('.person-card', node);
    card.dataset.tone = person.tone || 'steady';
    $('.avatar', node).textContent = initials(person.name);
    $('h3', node).textContent = safe(person.name);
    $('.role', node).textContent = safe(person.role);
    $('.capacity', node).textContent = safe(person.capacity);
    const tasks = person.tasks || [];
    $('.task-stack', node).innerHTML = tasks.length
      ? tasks.map(t => `<span class="task-chip">${safe(t.title)} · ${safe(t.status)}</span>`).join('')
      : '<span class="task-chip">진행중 업무 없음</span>';
    grid.appendChild(node);
  });
}

function renderUpdates(updates) {
  const list = $('#updatesList');
  list.innerHTML = updates.map(update => `
    <article class="timeline-item">
      <strong>${safe(update.heading).replace('2026-06-29 — ', '')}</strong>
      <p>${safe(update.text)}</p>
    </article>
  `).join('');
}

function wireFilters(projects) {
  $$('.filter').forEach(button => {
    button.addEventListener('click', () => {
      $$('.filter').forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      const filter = button.dataset.filter;
      $$('.project-card').forEach((card, index) => {
        const tone = projects[index]?.tone || 'steady';
        card.dataset.hidden = filter !== 'all' && tone !== filter ? 'true' : 'false';
      });
    });
  });
}

async function init() {
  const response = await fetch('./data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`data.json ${response.status}`);
  const data = await response.json();
  document.title = data.meta?.title || '영상팀 운영 브리핑';
  renderPills(data.stats || {});
  renderKeyChanges(data.keyChanges || []);
  renderProjects(data.projects || []);
  renderPeople(data.people || []);
  renderUpdates(data.recentUpdates || []);
  wireFilters(data.projects || []);
  $('#lastUpdated').textContent = data.meta?.lastUpdated || '';
  $('#designRef').textContent = data.meta?.designReference || '';
}

init().catch(error => {
  console.error(error);
  document.body.insertAdjacentHTML('afterbegin', `
    <div style="margin:16px;padding:16px;border-radius:16px;background:#fff0f0;color:#991b1b;font-weight:700;position:relative;z-index:99;">
      데이터를 불러오지 못했습니다: ${safe(error.message)}
    </div>
  `);
});
