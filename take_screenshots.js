const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  console.log('Navigating to http://localhost:4200 ...');
  try {
    await page.goto('http://localhost:4200', { waitUntil: 'networkidle' });
  } catch (e) {
    console.log('App not ready yet? Waiting 5 more seconds...');
    await page.waitForTimeout(5000);
    await page.goto('http://localhost:4200');
  }
  
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'screenshots/01_initial_state.png' });
  console.log('Saved: 01_initial_state.png');

  console.log('Analyzing THYAO...');
  await page.fill('input[placeholder="THYAO"]', 'THYAO');
  await page.click('button:has-text("ANALİZ ET")');
  
  // Analiz bitene kadar bekle (Loading spinner'ın gitmesini veya canvasın dolmasını bekleyebiliriz)
  await page.waitForTimeout(6000); 
  await page.screenshot({ path: 'screenshots/02_analysis_thyao.png' });
  console.log('Saved: 02_analysis_thyao.png');

  console.log('Opening Leaderboard (Altın Kralları)...');
  await page.click('button:has-text("ALTIN KRALLARI")');
  
  // Liderlerin gelmesi (Cache yoksa 15-20 sn, varsa 1 sn)
  console.log('Waiting for leaderboard data...');
  await page.waitForTimeout(15000); 
  await page.screenshot({ path: 'screenshots/03_leaderboard.png' });
  console.log('Saved: 03_leaderboard.png');

  await browser.close();
  console.log('All screenshots captured successfully.');
})();