const $ = (selector, root = document) => root.querySelector(selector);

const state = {
  data: null,
  days: [],
  byDate: new Map(),
  currentMonth: null,
  todayDate: null,
  modalOpenedAt: 0,
};

function safe(text) {
  return text == null ? '' : String(text);
}

function parseISO(value) {
  const match = safe(value).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return null;
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
}

function toISO(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function monthKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
}

function monthTitle(date) {
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월`;
}

function dayLabel(date) {
  const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
  return `${date.getMonth() + 1}/${date.getDate()}(${weekdays[date.getDay()]})`;
}

function addMonths(date, amount) {
  return new Date(date.getFullYear(), date.getMonth() + amount, 1);
}

function startOfCalendar(date) {
  const first = new Date(date.getFullYear(), date.getMonth(), 1);
  const start = new Date(first);
  start.setDate(first.getDate() - first.getDay());
  return start;
}

function endOfCalendar(date) {
  const last = new Date(date.getFullYear(), date.getMonth() + 1, 0);
  const end = new Date(last);
  end.setDate(last.getDate() + (6 - last.getDay()));
  return end;
}

function eventTone(event) {
  const text = `${event.priority || ''} ${event.status || ''}`;
  if (text.includes('긴급')) return 'risk';
  if (text.includes('높음') || text.includes('진행')) return 'focus';
  if (text.includes('대기') || text.includes('직전')) return 'waiting';
  return 'steady';
}

function normalizeDay(day) {
  return {
    date: safe(day.date),
    label: safe(day.label),
    weekday: safe(day.weekday),
    load: safe(day.load || '물량 미정'),
    isToday: Boolean(day.isToday),
    events: Array.isArray(day.events) ? day.events : [],
    changes: Array.isArray(day.changes) ? day.changes : [],
  };
}

function firstUsefulDate(days) {
  const today = days.find(day => day.isToday) || days.find(day => day.date === '2026-06-30') || days[0];
  const parsed = parseISO(today?.date);
  return parsed || new Date();
}

function updateStats() {
  const today = state.days.find(day => day.isToday) || state.days.find(day => day.date === toISO(state.todayDate));
  $('#loggedDayCount').textContent = String(state.days.length);
  $('#todayLoad').textContent = today?.load || '미정';
  $('#todayEventCount').textContent = String(today?.events?.length || 0);
}

function renderMonth() {
  const grid = $('#monthGrid');
  grid.innerHTML = '';
  $('#calendarTitle').textContent = monthTitle(state.currentMonth);

  const start = startOfCalendar(state.currentMonth);
  const end = endOfCalendar(state.currentMonth);
  const cursor = new Date(start);
  const currentKey = monthKey(state.currentMonth);

  while (cursor <= end) {
    const iso = toISO(cursor);
    const stored = state.byDate.get(iso);
    const day = stored || {
      date: iso,
      label: dayLabel(cursor),
      weekday: ['일', '월', '화', '수', '목', '금', '토'][cursor.getDay()],
      load: '물량 미정',
      isToday: iso === toISO(state.todayDate),
      events: [],
      changes: [],
    };
    const outside = monthKey(cursor) !== currentKey;
    const hasLogs = (day.events?.length || 0) + (day.changes?.length || 0) > 0;
    const visibleEvents = (day.events || []).slice(0, 3);
    const moreCount = Math.max(0, (day.events?.length || 0) - visibleEvents.length);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `calendar-cell${outside ? ' outside' : ''}${day.isToday ? ' today' : ''}${hasLogs ? ' has-log' : ''}`;
    button.setAttribute('aria-label', `${day.label} 상세 보기`);
    button.dataset.date = iso;
    button.innerHTML = `
      <span class="cell-topline">
        <span class="cell-date">${cursor.getDate()}</span>
        ${day.load && day.load !== '물량 미정' ? `<em class="cell-load">${safe(day.load)}</em>` : ''}
      </span>
      <span class="cell-events">
        ${visibleEvents.map(event => `
          <span class="cell-event ${eventTone(event)}">
            <b>${safe(event.person || '미정')}</b>
            <i>${safe(event.project || '')}</i>
          </span>
        `).join('')}
        ${moreCount ? `<span class="cell-more">+${moreCount}개 더</span>` : ''}
        ${!visibleEvents.length && !day.changes?.length ? '<span class="cell-empty">기록 없음</span>' : ''}
      </span>
      ${day.changes?.length ? `<span class="cell-change-count">변경 ${day.changes.length}</span>` : ''}
    `;
    button.addEventListener('click', () => openDayModal(iso));
    grid.appendChild(button);
    cursor.setDate(cursor.getDate() + 1);
  }
}

function renderModalEvents(events) {
  const wrap = $('#modalEvents');
  wrap.innerHTML = '';
  if (!events.length) {
    wrap.innerHTML = '<p class="modal-empty">이 날짜에 표시된 담당자 업무가 아직 없어요.</p>';
    return;
  }
  events.forEach(event => {
    const item = document.createElement('article');
    item.className = `modal-item ${eventTone(event)}`;
    item.innerHTML = `
      <div class="modal-item-main">
        <strong>${safe(event.person || '미정')}</strong>
        <span>${safe(event.project || '프로젝트 미정')}</span>
      </div>
      <p>${safe(event.title || '업무 제목 미정')}</p>
      <div class="modal-tags">
        <em>${safe(event.status || '상태 미정')}</em>
        <em>${safe(event.priority || '우선순위 미정')}</em>
      </div>
    `;
    wrap.appendChild(item);
  });
}

function renderModalChanges(changes) {
  const wrap = $('#modalChanges');
  wrap.innerHTML = '';
  if (!changes.length) {
    wrap.innerHTML = '<p class="modal-empty">이 날짜에 표시된 변경 로그가 아직 없어요.</p>';
    return;
  }
  changes.forEach(change => {
    const item = document.createElement('article');
    item.className = 'modal-item change';
    item.innerHTML = `
      <div class="modal-item-main">
        <strong>${safe(change.time || 'log')}</strong>
        <span>변경 기록</span>
      </div>
      <p>${safe(change.text || '')}</p>
    `;
    wrap.appendChild(item);
  });
}

function openDayModal(iso) {
  const parsed = parseISO(iso) || state.todayDate;
  const day = state.byDate.get(iso) || {
    date: iso,
    label: dayLabel(parsed),
    weekday: '',
    load: '물량 미정',
    events: [],
    changes: [],
  };

  $('#modalEyebrow').textContent = day.isToday ? 'TODAY DETAIL' : 'DAY DETAIL';
  $('#modalTitle').textContent = `${day.label || dayLabel(parsed)} 상세`;
  $('#modalSubtitle').textContent = `${day.load || '물량 미정'} · 업무 ${day.events.length}개 · 변경 ${day.changes.length}개`;
  $('#modalEventCount').textContent = String(day.events.length);
  $('#modalChangeCount').textContent = String(day.changes.length);
  renderModalEvents(day.events || []);
  renderModalChanges(day.changes || []);

  const modal = $('#dayModal');
  state.modalOpenedAt = performance.now();
  modal.hidden = false;
  document.body.classList.add('modal-open');
  $('.day-modal-panel').focus();
}

function closeDayModal(reason = 'button') {
  if (reason === 'backdrop' && performance.now() - state.modalOpenedAt < 250) return;
  $('#dayModal').hidden = true;
  document.body.classList.remove('modal-open');
}

function wireControls() {
  $('#prevMonth').addEventListener('click', () => {
    state.currentMonth = addMonths(state.currentMonth, -1);
    renderMonth();
  });
  $('#nextMonth').addEventListener('click', () => {
    state.currentMonth = addMonths(state.currentMonth, 1);
    renderMonth();
  });
  $('#todayMonth').addEventListener('click', () => {
    state.currentMonth = new Date(state.todayDate.getFullYear(), state.todayDate.getMonth(), 1);
    renderMonth();
  });
  $('#modalClose').addEventListener('click', () => closeDayModal('button'));
  $('[data-close-modal]').addEventListener('click', () => closeDayModal('backdrop'));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !$('#dayModal').hidden) closeDayModal('escape');
  });
}

async function initCalendar() {
  const response = await fetch('./data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`data.json ${response.status}`);
  const data = await response.json();
  state.data = data;
  state.days = (data.changeCalendar || []).map(normalizeDay);
  state.byDate = new Map(state.days.map(day => [day.date, day]));
  state.todayDate = firstUsefulDate(state.days);
  state.currentMonth = new Date(state.todayDate.getFullYear(), state.todayDate.getMonth(), 1);

  document.title = `날짜별 변경 캘린더 · ${data.meta?.title || '영상팀 운영상황판'}`;
  $('#calendarUpdated').textContent = data.meta?.lastUpdated || '';
  $('#calendarDesignRef').textContent = data.meta?.designReference || '';
  updateStats();
  renderMonth();
  wireControls();
}

initCalendar().catch(error => {
  console.error(error);
  const warning = document.createElement('div');
  warning.className = 'load-warning';
  warning.textContent = `캘린더 데이터를 불러오지 못했습니다: ${safe(error.message)}`;
  document.body.prepend(warning);
});
