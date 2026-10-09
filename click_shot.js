const puppeteer = require('puppeteer-core');

(async () => {
  const url = process.argv[2] || 'http://127.0.0.1:5094/';
  const clickText = process.argv[3] || 'Kênh Zalo Gateway';
  const outPath = process.argv[4] || '/tmp/click_shot.png';

  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu', '--window-size=1600,1000'],
    defaultViewport: { width: 1600, height: 1000 },
  });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });

  const clicked = await page.evaluate((text) => {
    const els = Array.from(document.querySelectorAll('button, a, div, span'));
    const target = els.find(el => el.textContent && el.textContent.trim().includes(text) && el.children.length < 4);
    if (target) { target.click(); return true; }
    return false;
  }, clickText);

  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: outPath });
  await browser.close();
  console.log(JSON.stringify({ clicked, outPath }));
})().catch(e => { console.error(e); process.exit(1); });
