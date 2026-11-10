// Exporta cada pieza (`.ad[data-name]`) de un HTML a PNG, a una o varias densidades.
// Uso: node export_pieces.mjs <banners.html> <carpeta_salida> [escalas=1,2]
// Requiere: npm i playwright  (y `npx playwright install chromium` la primera vez)
// Los JPG se generan después con to_jpg.py (color completo 4:4:4, límite de peso).
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const [, , src, out, scales = '1,2'] = process.argv;
if (!src || !out) {
  console.error('Uso: node export_pieces.mjs <banners.html> <carpeta_salida> [escalas=1,2]');
  process.exit(1);
}
fs.mkdirSync(out, { recursive: true });

const browser = await chromium.launch();
for (const dpr of scales.split(',').map(Number)) {
  const page = await browser.newPage({ viewport: { width: 2200, height: 1200 }, deviceScaleFactor: dpr });
  await page.goto('file://' + path.resolve(src), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => [...document.images].every(i => i.complete), null, { timeout: 60000 });
  await page.waitForTimeout(400);
  const broken = await page.evaluate(() => [...document.images].filter(i => !i.naturalWidth).map(i => i.getAttribute('src')));
  if (broken.length && dpr === Number(scales.split(',')[0])) {
    console.warn('⚠ Imágenes que no cargaron (revisa las rutas):', [...new Set(broken)].join(', '));
  }
  for (const el of await page.$$('.ad[data-name]')) {
    const name = await el.getAttribute('data-name');
    const suffix = dpr === 1 ? '' : `@${dpr}x`;
    await el.screenshot({ path: path.join(out, `${name}${suffix}.png`) });
  }
  await page.close();
}
await browser.close();
