#!/usr/bin/env node
/*
 * check-parity — how much of the live Joomla site does this build cover?
 *
 * Takes the inventory of live Joomla URLs, sends each one through the
 * vercel.json redirect map and looks at where it lands in the built site.
 * The result is the progress number for the parity plan
 * (docs/plans/2026-11-24-joomla-parity.md).
 *
 *   node scripts/check-parity.mjs            report
 *   node scripts/check-parity.mjs --strict   also exit 1 when a live URL has no
 *                                            rule or a rule points at a page
 *                                            that does not exist
 *   node scripts/check-parity.mjs --list     print every URL with its class
 *
 * Run after `astro build` (wired as part of `postbuild` with --strict).
 */
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(ROOT, 'dist', 'client');
const INVENTORY = join(ROOT, 'docs', 'plans', '2026-11-24-joomla-live-inventory.csv');
const args = new Set(process.argv.slice(2));

/* ── Judgement calls, kept as data ─────────────────────────────────────────── */

// Section landing pages. A redirect to one of these normally means "no real
// equivalent, fall back to the hub" …
const GENERIC = new Set(['/', '/produkte', '/unternehmen', '/kontakt', '/downloads', '/leistungen', '/branchen']);

// … unless the Joomla URL is itself that hub.
const HUBS = {
  '/de': '/',
  '/de/kontakt': '/kontakt',
  '/de/anwendungsbereiche': '/branchen',
  '/de/foerdersysteme/foerdersysteme-uebersicht': '/produkte',
  '/de/medien-downloads': '/downloads',
  '/de/unternehmen/unternehmen-uebersicht': '/unternehmen',
  // '/de/leistungen': '/leistungen'  ← add once the life-cycle hub is built (plan step 1.2)
};

// Redirects that land on a real page whose content is NOT the Joomla page's.
// They keep visitors off a 404 but do not count as covered. Remove an entry
// when its real page exists.
const INTERIM = new Set([
  '/de/leistungen/konzept-beratung',
  '/de/leistungen/projektstart-steuerungsintegration',
  '/de/leistungen/fertigung-lieferung',
  '/de/leistungen/montage-inbetriebnahme',
  // '/de/leistungen/service' keeps its slug; its text is still the pre-life-cycle version
]);

/* ── Inputs ────────────────────────────────────────────────────────────────── */

if (!existsSync(DIST)) {
  console.error('check-parity: dist/client not found. Run `astro build` first.');
  process.exit(1);
}

function parseCsv(text) {
  const rows = [];
  let row = [], field = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
    else if (c !== '\r') field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [head, ...body] = rows;
  return body.filter((r) => r.length === head.length).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

const inventory = parseCsv(readFileSync(INVENTORY, 'utf8'));
// "live" = Joomla answers 200 at this URL itself (not a redirect, not a 404)
const live = inventory.filter((r) => r.status === '200' && !r.final);

const routes = new Set();
(function walk(dir) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) {
      if (relative(DIST, full) === 'admin') continue;
      walk(full);
    } else if (name === 'index.html') {
      const rel = '/' + relative(DIST, dir).split('\\').join('/');
      routes.add(rel === '/' ? '/' : rel);
    }
  }
})(DIST);

const redirects = (JSON.parse(readFileSync(join(ROOT, 'vercel.json'), 'utf8')).redirects ?? []).map((r) => {
  const names = [];
  const pattern = r.source
    .split(/(:[A-Za-z]+\*?)/)
    .map((part) => {
      if (!part.startsWith(':')) return part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      names.push(part.replace(/[:*]/g, ''));
      return part.endsWith('*') ? '(.*)' : '([^/]+)';
    })
    .join('');
  return { re: new RegExp(`^${pattern}/?$`), names, destination: r.destination };
});

function resolve(path) {
  for (const r of redirects) {
    const m = r.re.exec(path);
    if (!m) continue;
    let dest = r.destination;
    r.names.forEach((n, i) => {
      dest = dest.replace(`:${n}*`, m[i + 1] ?? '').replace(`:${n}`, m[i + 1] ?? '');
    });
    return dest.replace(/(.)\/$/, '$1');
  }
  return null;
}

/* ── Classification ────────────────────────────────────────────────────────── */

const CLASSES = ['equivalent', 'interim target', 'generic fallback', 'English URL on a German page', 'BROKEN RULE', 'NO RULE'];

function classify(path) {
  const lang = path.split('/')[1];
  const dest = resolve(path);
  if (dest === null) return routes.has(path) ? ['equivalent', path] : ['NO RULE', ''];
  if (/^https?:/.test(dest)) return ['equivalent', dest];
  if (!routes.has(dest.split('#')[0])) return ['BROKEN RULE', dest];
  if (lang === 'en' && !dest.startsWith('/en')) return ['English URL on a German page', dest];
  if (INTERIM.has(path)) return ['interim target', dest];
  if (GENERIC.has(dest) && HUBS[path] !== dest) return ['generic fallback', dest];
  return ['equivalent', dest];
}

const result = live.map((r) => {
  const [cls, dest] = classify(r.path);
  return { path: r.path, lang: r.path.split('/')[1], cls, dest };
});

/* ── Report ────────────────────────────────────────────────────────────────── */

const count = (lang, cls) => result.filter((r) => r.lang === lang && r.cls === cls).length;
const total = (lang) => result.filter((r) => r.lang === lang).length;

console.log(`check-parity: ${live.length} live Joomla URLs (news not included), ${routes.size} built routes.\n`);
console.log('  ' + 'class'.padEnd(34) + 'DE'.padStart(5) + 'EN'.padStart(5));
for (const cls of CLASSES) {
  console.log('  ' + cls.padEnd(34) + String(count('de', cls)).padStart(5) + String(count('en', cls)).padStart(5));
}
console.log('  ' + 'total'.padEnd(34) + String(total('de')).padStart(5) + String(total('en')).padStart(5));
console.log(`\n  Covered: German ${count('de', 'equivalent')} of ${total('de')}, English ${count('en', 'equivalent')} of ${total('en')}.`);

const failures = result.filter((r) => r.cls === 'BROKEN RULE' || r.cls === 'NO RULE');
if (failures.length) {
  console.log('\n  Would be an error page after cutover:');
  for (const f of failures) console.log(`    ${f.cls.padEnd(12)} ${f.path}${f.dest ? '  ->  ' + f.dest : ''}`);
}

if (args.has('--list')) {
  console.log('');
  for (const r of result) console.log(`  ${r.cls.padEnd(30)} ${r.path}${r.dest ? '  ->  ' + r.dest : ''}`);
}

if (args.has('--strict') && failures.length) {
  console.error(`\ncheck-parity: ${failures.length} live URL(s) without a working target.`);
  process.exit(1);
}
