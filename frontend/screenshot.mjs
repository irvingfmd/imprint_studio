import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1280, height: 800 });

// Login
await page.goto('http://localhost:5173/login');
await page.waitForTimeout(1000);
await page.screenshot({ path: 'screenshot_01_login.png' });
console.log('✓ Login');

// Register
await page.goto('http://localhost:5173/register');
await page.waitForTimeout(500);
await page.screenshot({ path: 'screenshot_02_register.png' });
console.log('✓ Register');

await browser.close();
console.log('Done.');
