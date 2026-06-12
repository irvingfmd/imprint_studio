import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1280, height: 800 });

// Inyectar tokens falsos para ver vistas autenticadas sin backend
async function injectAuth(role = 'CUSTOMER') {
  // JWT con payload mínimo (no se valida en frontend, solo existe)
  const fakeAccess = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwicm9sZSI6IkNVU1RPTUVSIn0.fake';
  await page.evaluate(({ access, role }) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', 'fake_refresh');
  }, { access: fakeAccess, role });
}

// Vista de pedidos del cliente (lista vacía — sin backend real)
await page.goto('http://localhost:5173/login');
await injectAuth('CUSTOMER');

// Mockear las llamadas de API para que no fallen
await page.route('**/api/v1/auth/me/', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data: { id: '1', phone: '+5219611234567', email: 'test@test.com', first_name: 'Irving', last_name: 'Martínez', role: 'CUSTOMER' } })
}));
await page.route('**/api/v1/orders/', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data: { count: 2, results: [
    { id: 'aaa-111', title: 'Figura de anime personalizada', status: 'PRINTING', priority: 'NORMAL', created_at: '2026-06-01T10:00:00Z' },
    { id: 'bbb-222', title: 'Logo empresarial 3D', status: 'QUOTED', priority: 'URGENT', created_at: '2026-06-05T14:30:00Z' },
  ]}})
}));

await page.goto('http://localhost:5173/orders');
await page.waitForTimeout(1500);
await page.screenshot({ path: 'screenshot_03_orders.png' });
console.log('✓ Lista de pedidos');

// Vista crear pedido
await page.goto('http://localhost:5173/orders/new');
await page.waitForTimeout(800);
await page.screenshot({ path: 'screenshot_04_create_order.png' });
console.log('✓ Crear pedido');

// Panel admin — dashboard
await page.route('**/api/v1/auth/me/', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data: { id: '1', phone: '+5219611234567', email: 'admin@test.com', first_name: 'Irving', last_name: 'Martínez', role: 'ADMIN' } })
}));
await page.route('**/api/v1/admin/dashboard/', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data: { pending_orders: 8, quoted_orders: 3, printing_orders: 5, ready_orders: 2, pending_payments: 4, monthly_revenue: '28500.00' } })
}));

await page.goto('http://localhost:5173/admin/dashboard');
await page.waitForTimeout(1500);
await page.screenshot({ path: 'screenshot_05_dashboard.png' });
console.log('✓ Dashboard admin');

// Admin — lista de pedidos
await page.route('**/api/v1/admin/orders/**', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data: { count: 4, results: [
    { id: 'aaa-111', title: 'Figura de anime personalizada', status: 'PRINTING', priority: 'NORMAL', created_at: '2026-06-01T10:00:00Z' },
    { id: 'bbb-222', title: 'Logo empresarial 3D', status: 'QUOTED', priority: 'URGENT', created_at: '2026-06-05T14:30:00Z' },
    { id: 'ccc-333', title: 'Prótesis de mano izquierda', status: 'PENDING_DEPOSIT', priority: 'EXPRESS', created_at: '2026-06-08T09:00:00Z' },
    { id: 'ddd-444', title: 'Piezas para impresora', status: 'READY', priority: 'NORMAL', created_at: '2026-06-09T16:00:00Z' },
  ]}})
}));

await page.goto('http://localhost:5173/admin/orders');
await page.waitForTimeout(1200);
await page.screenshot({ path: 'screenshot_06_admin_orders.png' });
console.log('✓ Admin pedidos');

await browser.close();
console.log('Done.');
