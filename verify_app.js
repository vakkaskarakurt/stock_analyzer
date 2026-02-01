const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:4200');

  console.log('--- Testing Autocomplete ---');
  await page.fill('input[placeholder="THYAO"]', 'THY');
  await page.waitForSelector('text=Türk Hava Yolları');
  console.log('OK: Autocomplete working.');

  console.log('--- Testing Chart Generation ---');
  await page.click('text=THYAO'); // Öneriden seç
  await page.waitForTimeout(5000);
  
  // TradingView grafiği içinde canvas var mı?
  const canvasCount = await page.locator('canvas').count();
  if (canvasCount > 0) {
    console.log(`OK: Chart rendered with ${canvasCount} canvases.`);
  } else {
    console.error('FAIL: No chart canvas found!');
    process.exit(1);
  }

  console.log('--- Testing Leaderboard ---');
  await page.click('text=ALTIN KRALLARI');
  await page.waitForSelector('.card-body h4'); // Hisse kodu başlıklarını bekle
  const cardCount = await page.locator('.card-body h4').count();
  console.log(`OK: Leaderboard loaded ${cardCount} stocks.`);

  console.log('--- ALL TESTS PASSED ---');
  await browser.close();
})();
