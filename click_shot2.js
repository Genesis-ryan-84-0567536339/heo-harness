const puppeteer = require('puppeteer-core');

(async () => {
  const url = process.argv[2] || 'http://127.0.0.1:5094/';
  const groupText = process.argv[3];
  const leafText = process.argv[4];
  const outPath = process.argv[5] || '/tmp/click_shot2.png';

  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu', '--window-size=1600,1000'],
    defaultViewport: { width: 1600, height: 1000 },
  });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

  await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });

  const clickByText = async (text) => {
    return await page.evaluate((t) => {
      const btns = Array.from(document.querySelectorAll('button.nav-hub-item'));
      const target = btns.find(el => el.textContent && el.textContent.trim().startsWith(t));
      if (target) { target.click(); return true; }
      return false;
    }, text);
  };

  let groupClicked = null;
  if (groupText) {
    groupClicked = await clickByText(groupText);
    await new Promise(r => setTimeout(r, 500));
  }
  const leafClicked = await clickByText(leafText);
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: outPath });
  await browser.close();
  console.log(JSON.stringify({ groupClicked, leafClicked, outPath, errors }));
})().catch(e => { console.error(e); process.exit(1); });
