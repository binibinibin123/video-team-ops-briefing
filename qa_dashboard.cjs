const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const outDir = path.join(__dirname, 'qa-artifacts');
fs.mkdirSync(outDir, { recursive: true });

async function inspect(page, targetUrl, viewport, label) {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', err => errors.push(err.message));
  await page.setViewportSize(viewport);
  await page.goto(targetUrl, { waitUntil: 'networkidle' });
  const result = await page.evaluate(() => {
    const visibleText = document.body.innerText;
    const required = [
      '영상팀 운영상황판',
      '업무 테이블',
      '오늘 변경',
      '팀 배치',
      '사람별 배치',
      '쿠쿠홈시스',
      '미닉스',
      '표지영',
      '총 36개 바리에이션',
      'Airtable',
      'Notion',
      'Linear'
    ];
    const missing = required.filter(t => !visibleText.includes(t));
    const overflow = [...document.querySelectorAll('body *')]
      .filter(el => {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;
        if (style.overflowX === 'visible' && el.scrollWidth > Math.ceil(el.clientWidth) + 2) return true;
        return false;
      })
      .slice(0, 14)
      .map(el => ({
        tag: el.tagName,
        cls: String(el.className || ''),
        text: el.innerText?.slice(0, 70),
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth
      }));
    return {
      title: document.title,
      missing,
      overflow,
      projectRows: document.querySelectorAll('.project-row').length,
      peopleRows: document.querySelectorAll('.person-row').length,
      peopleMini: document.querySelectorAll('.person-mini').length,
      changeCards: document.querySelectorAll('.change-card').length,
      summaryCards: document.querySelectorAll('.summary-card').length,
      hasSideRail: Boolean(document.querySelector('.side-rail')),
      h1: document.querySelector('h1')?.innerText,
    };
  });
  const screenshot = path.join(outDir, `dashboard-${label}.png`);
  await page.screenshot({ path: screenshot, fullPage: true });
  return { label, viewport, errors, result, screenshot };
}

(async () => {
  const targetUrl = process.argv[2] || 'http://127.0.0.1:8799/index.html';
  const browser = await chromium.launch({ headless: true });
  const desktop = await inspect(await browser.newPage(), targetUrl, { width: 1440, height: 1100 }, 'desktop');
  const mobile = await inspect(await browser.newPage(), targetUrl, { width: 390, height: 1100 }, 'mobile');
  await browser.close();
  console.log(JSON.stringify({ targetUrl, checks: [desktop, mobile] }, null, 2));
})();
