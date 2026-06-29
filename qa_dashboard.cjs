const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1200 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', err => errors.push(err.message));
  const targetUrl = process.argv[2] || 'http://127.0.0.1:8799/index.html';
  await page.goto(targetUrl, { waitUntil: 'networkidle' });
  const result = await page.evaluate(() => {
    const visibleText = document.body.innerText;
    const required = ['영상팀 운영 브리핑', '오늘 핵심 변경', '스냅스', '이재은', '최유정', '프로젝트별 현재 상태', '사람별 지금 하는 일'];
    const missing = required.filter(t => !visibleText.includes(t));
    const overflow = [...document.querySelectorAll('body *')]
      .filter(el => {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;
        if (style.overflowX === 'visible' && el.scrollWidth > Math.ceil(el.clientWidth) + 2) return true;
        return false;
      })
      .slice(0, 12)
      .map(el => ({ tag: el.tagName, cls: el.className, text: el.innerText?.slice(0, 60), scrollWidth: el.scrollWidth, clientWidth: el.clientWidth }));
    return {
      title: document.title,
      missing,
      overflow,
      projectCards: document.querySelectorAll('.project-card').length,
      peopleCards: document.querySelectorAll('.person-card').length,
      h1: document.querySelector('h1')?.innerText,
    };
  });
  await page.screenshot({ path: '/mnt/c/Users/82103/Documents/video_team_ops/web_dashboard/dashboard-preview.png', fullPage: true });
  await browser.close();
  console.log(JSON.stringify({ errors, result }, null, 2));
})();
