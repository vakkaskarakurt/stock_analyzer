const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  console.log('Navigating...');
  try {
    await page.goto('http://localhost:4200', { waitUntil: 'networkidle' });
  } catch (e) {
    await page.goto('http://localhost:4200');
  }

  // 1. Candlestick Chart
  console.log('Analyzing THYAO (Candlestick)...');
  await page.fill('input[placeholder="THYAO"]', 'THYAO');
  await page.click('button:has(.bi-play-fill)'); 
  
  await page.waitForTimeout(5000); // Chart render süresi
  await page.screenshot({ path: 'screenshots/v3_01_candlestick.png' });
  console.log('Saved: Candlestick Chart');

  // 2. Comparison (Line Chart)
  console.log('Comparison Mode (Line Chart)...');
  await page.click('text=KIYASLAMA MODU'); 
  await page.waitForTimeout(500);
  await page.fill('input[placeholder="GARAN"]', 'GARAN');
  await page.click('button:has(.bi-play-fill)');
  
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'screenshots/v3_02_comparison.png' });
  console.log('Saved: Comparison Chart');

  await browser.close();
})();
