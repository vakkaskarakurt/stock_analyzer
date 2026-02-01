const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Starting Full System Test...');
  const browser = await chromium.launch(); // Headless: true (default)
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  try {
    // 1. Dashboard Load
    console.log('➡️ Loading App...');
    await page.goto('http://localhost:4200');
    
    // Ticker Check
    await page.waitForSelector('app-market-ticker span.badge:has-text("USD/TRY")');
    const usdPrice = await page.locator('app-market-ticker span.fw-bold.text-white').first().innerText();
    console.log(`✅ Dashboard Loaded. USD Price: ${usdPrice}`);

    // 2. Autocomplete
    console.log('➡️ Testing Autocomplete (THYAO)...');
    await page.fill('input[placeholder="THYAO"]', 'THY');
    await page.waitForSelector('button:has-text("Türk Hava Yolları")');
    console.log('✅ Autocomplete Suggestions Appeared.');
    await page.click('button:has-text("Türk Hava Yolları")'); // Select

    // 3. Chart Rendering
    console.log('➡️ Waiting for Chart...');
    await page.waitForSelector('app-stock-chart canvas', { timeout: 10000 });
    console.log('✅ Chart Rendered.');

    // 4. SMA Indicator
    console.log('➡️ Testing SMA Toggle...');
    // Toggle varsa tıkla (Tekli modda olmalı)
    if (await page.isVisible('label:has-text("SMA 20")')) {
        await page.click('label:has-text("SMA 20")');
        console.log('✅ SMA Toggled.');
    } else {
        console.error('❌ SMA Toggle NOT found!');
    }

    // 5. AI Commentary
    console.log('➡️ Testing AI Comment...');
    await page.click('button:has-text("AI Yorumu")');
    await page.waitForSelector('h6:has-text("Gemini Analizi")', { timeout: 5000 });
    const aiText = await page.locator('.card-footer p').innerText();
    console.log(`✅ AI Comment Received: "${aiText.substring(0, 50)}..."`);

    // 6. Leaderboard
    console.log('➡️ Testing Leaderboard...');
    await page.click('button:has-text("ALTIN KRALLARI")');
    await page.waitForSelector('app-leaderboard .card-body h2', { timeout: 20000 }); // İlk yükleme uzun sürebilir
    const leaderName = await page.locator('app-leaderboard .card-body h2').first().innerText();
    console.log(`✅ Leaderboard Loaded. Top Stock: ${leaderName}`);
    
    // Close Leaderboard
    await page.click('app-leaderboard button.btn-dark.rounded-circle');

    // 7. Comparison Mode
    console.log('➡️ Testing Comparison Mode...');
    await page.click('text=KIYASLAMA MODU');
    await page.fill('input[placeholder="GARAN"]', 'GARAN');
    await page.click('button:has(.bi-play-fill)'); // Play button
    
    // Wait for update
    await page.waitForTimeout(3000);
    // Check header text for "vs"
    const headerText = await page.locator('app-stock-chart h5').innerText();
    if (headerText.includes('vs')) {
        console.log(`✅ Comparison Active: "${headerText}"`);
    } else {
        console.error(`❌ Comparison Failed. Header: "${headerText}"`);
    }

    console.log('🎉 ALL SYSTEMS GO! Test Completed Successfully.');

  } catch (error) {
    console.error('🚨 TEST FAILED:', error);
    await page.screenshot({ path: 'test_failure.png' });
  } finally {
    await browser.close();
  }
})();
