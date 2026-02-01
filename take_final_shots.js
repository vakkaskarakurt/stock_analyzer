const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 1200 });
  await page.goto('http://localhost:4200');
  
  // 1. Dashboard + AI Comment
  await page.fill('input[placeholder="THYAO"]', 'THY');
  await page.waitForSelector('button:has-text("THYAO")');
  await page.click('button:has-text("THYAO")');
  await page.waitForSelector('canvas', { timeout: 15000 });
  await page.click('button:has-text("AI Insight")');
  await page.waitForTimeout(3000); // Wait for AI
  await page.screenshot({ path: 'screenshots/v3_final_dashboard.png' });
  console.log('✅ Dashboard screenshot taken.');

  // 2. Leaderboard
  await page.click('button:has-text("GOLD LEADERS")');
  await page.waitForSelector('.glass-table tbody tr', { timeout: 30000 });
  await page.waitForTimeout(2000); // Wait for podium animation
  await page.screenshot({ path: 'screenshots/v3_final_leaderboard.png' });
  console.log('✅ Leaderboard screenshot taken.');

  await browser.close();
})();
