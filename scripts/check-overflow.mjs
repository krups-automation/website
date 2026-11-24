#!/usr/bin/env node
/*
 * check-overflow — does any built page scroll sideways on a phone?
 *
 * Serves dist/client from a throwaway local server, opens every prerendered
 * page at 390 px wide in headless Chrome and compares the document's scroll
 * width with the viewport. Pages that are wider are listed with the elements
 * that stick out.
 *
 * Local check: it needs a Chrome or Chromium on this machine (set CHROME_PATH
 * to point at one). Where none is found (the Vercel build, for instance) it
 * says so and exits 0, so it never blocks a deploy.
 *
 *   npm run build && npm run check:overflow
 */
import { createServer } from 'node:http';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(ROOT, 'dist', 'client');
const WIDTH = 390;
const HEIGHT = 844;

if (!existsSync(DIST)) {
  console.error('check-overflow: dist/client not found. Run `astro build` first.');
  process.exit(1);
}

const chrome = [
  process.env.CHROME_PATH,
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].find((p) => p && existsSync(p));

if (!chrome) {
  console.log('check-overflow: skipped, no Chrome found (set CHROME_PATH to run it).');
  process.exit(0);
}

const routes = [];
(function walk(dir) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) {
      if (relative(DIST, full) === 'admin') continue;
      walk(full);
    } else if (name === 'index.html') {
      const rel = '/' + relative(DIST, dir).split('\\').join('/');
      routes.push(rel === '/' ? '/' : rel + '/');
    }
  }
})(DIST);
routes.sort();

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.webp': 'image/webp', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff', '.txt': 'text/plain',
};

const server = createServer((req, res) => {
  const path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let file = join(DIST, path);
  if (!file.startsWith(DIST)) { res.writeHead(403).end(); return; }
  if (existsSync(file) && statSync(file).isDirectory()) file = join(file, 'index.html');
  if (!existsSync(file)) { res.writeHead(404).end(); return; }
  res.writeHead(200, { 'Content-Type': TYPES[extname(file)] ?? 'application/octet-stream' });
  res.end(readFileSync(file));
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const base = `http://127.0.0.1:${server.address().port}`;

const { chromium } = await import('playwright-core');
const browser = await chromium.launch({ executablePath: chrome, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });

const wide = [];
for (const route of routes) {
  await page.goto(base + route, { waitUntil: 'load' });
  const found = await page.evaluate(() => {
    const vw = window.innerWidth;
    const scroll = document.documentElement.scrollWidth;
    if (scroll <= vw + 1) return null;
    const culprits = [];
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.right > vw + 1) {
        const cls = typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).join('.') : '';
        culprits.push(`${el.tagName.toLowerCase()}${cls} (right edge ${Math.round(r.right)} px)`);
      }
    }
    return { scroll, vw, culprits: culprits.slice(0, 4) };
  });
  if (found) wide.push({ route, ...found });
}

await browser.close();
server.close();

if (wide.length === 0) {
  console.log(`check-overflow: clean (${routes.length} pages at ${WIDTH} px).`);
  process.exit(0);
}

console.error(`check-overflow: ${wide.length} of ${routes.length} pages scroll sideways at ${WIDTH} px.\n`);
for (const w of wide) {
  console.error(`  ${w.route}  is ${w.scroll} px wide in a ${w.vw} px viewport`);
  for (const c of w.culprits) console.error(`      ${c}`);
}
process.exit(1);
