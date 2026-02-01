const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Starting Full System Verification (V3.0.1 UI) - Take 2...');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 1200 });

  try {
    console.log('➡️ Loading App...');
    await page.goto('http://localhost:4200');
    await page.waitForTimeout(2000); // Wait for initial animation
    
    // 1. Ticker Verification
    await page.waitForSelector('app-market-ticker');
    const tickerText = await page.innerText('app-market-ticker');
    console.log(`✅ Market Ticker active: ${tickerText.substring(0, 20)}...`);

    // 2. Autocomplete
    console.log('➡️ Searching for THYAO...');
    await page.fill('input[placeholder="THYAO"]', 'THY');
    await page.waitForSelector('button:has-text("THYAO")');
    await page.click('button:has-text("THYAO")');
    console.log('✅ THYAO Selected.');

    // 3. Chart & AI
    await page.waitForSelector('app-stock-chart canvas', { timeout: 15000 });
    console.log('✅ Chart Loaded.');
    
    await page.click('button:has-text("AI Insight")');
    await page.waitForSelector('.bi-robot');
    console.log('✅ AI Insight received.');
    await page.screenshot({ path: 'screenshots/v3_01_dashboard.png' });

    // 4. Leaderboard (The big one)
    console.log('➡️ Opening Leaderboard...');
    await page.click('button:has-text("GOLD LEADERS")');
    await page.waitForSelector('.glass-table tbody tr', { timeout: 30000 });
    
    const firstStock = await page.innerText('.card-glass h1');
    const rowCount = await page.locator('.glass-table tbody tr').count();
    console.log(`✅ Leaderboard verified. Top: ${firstStock}, Total Rows: ${rowCount}`);
    
    await page.screenshot({ path: 'screenshots/v3_02_leaderboard.png' });

    console.log('🎉 VERIFICATION COMPLETE. Everything is working perfectly.');

  } catch (error) {
    console.error('🚨 TEST FAILED:', error);
    await page.screenshot({ path: 'screenshots/v3_error.png' });
  } finally {
    await browser.close();
  }
})();
