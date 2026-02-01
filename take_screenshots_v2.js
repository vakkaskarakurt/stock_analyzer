const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  console.log('Navigating...');
  try {
    await page.goto('http://localhost:4200', { waitUntil: 'networkidle' });
  } catch (e) {
    await page.waitForTimeout(3000);
    await page.goto('http://localhost:4200');
  }

  // 1. Initial Dashboard (Ticker Check)
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'screenshots/v2_01_dashboard_ticker.png' });
  console.log('Saved: Dashboard Ticker');

  // 2. Enable Comparison Mode
  console.log('Activating Comparison Mode...');
  // Checkbox'ı bul ve tıkla (label üzerinden bulmak daha güvenli)
  await page.click('text=KIYASLAMA MODU'); 
  await page.waitForTimeout(500);

  // 3. Fill THYAO
  console.log('Entering Stocks...');
  await page.fill('input[placeholder="THYAO"]', 'THYAO');
  
  // 4. Fill GARAN (Comparison Input)
  await page.fill('input[placeholder="GARAN"]', 'GARAN');
  
  // 5. Analyze
  await page.click('button:has(.bi-play-fill)'); // Play icon button
  
  console.log('Waiting for chart...');
  await page.waitForTimeout(5000); // API responses + Animation
  
  await page.screenshot({ path: 'screenshots/v2_02_comparison_chart.png' });
  console.log('Saved: Comparison Chart');

  await browser.close();
})();
