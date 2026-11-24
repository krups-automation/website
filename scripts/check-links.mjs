#!/usr/bin/env node
/*
 * check-links — fails the build when a built page links to something that
 * does not exist.
 *
 * Reads every prerendered HTML file in dist/client (the Studio at /admin is
 * skipped), collects internal href/src targets and checks each one against
 * the built files, the server routes and, for "#fragment" links, the ids in
 * the target page. A link that only works because vercel.json redirects it is
 * reported too: internal links should point at the final URL.
 *
 * Run after `astro build` (wired as part of `postbuild`).
 */
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, dirname, posix } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(ROOT, 'dist', 'client');

// Routes rendered on the server or served by the platform: no file in dist/client.
const SERVER_PREFIXES = ['/api/', '/preview/', '/admin', '/_image', '/_vercel', '/_server-islands'];
const SERVER_EXACT = new Set(['/sitemap.xml']);

// "#…" links that are handled by a script instead of pointing at an element.
// #cookie-einstellungen re-opens the consent banner (CookieConsent.astro).
const SCRIPT_ANCHORS = new Set(['cookie-einstellungen']);

if (!existsSync(DIST)) {
  console.error('check-links: dist/client not found. Run `astro build` first.');
  process.exit(1);
}

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) {
      if (relative(DIST, full) === 'admin') continue;
      walk(full, out);
    } else if (name.endsWith('.html')) out.push(full);
  }
  return out;
}

/** dist file path -> the URL path it is served at */
function routeOf(file) {
  const rel = '/' + relative(DIST, file).split('\\').join('/');
  if (rel.endsWith('/index.html')) return rel.slice(0, -'index.html'.length).replace(/(.)\/$/, '$1');
  return rel.replace(/\.html$/, '');
}

function resolveFile(urlPath) {
  const clean = decodeURIComponent(urlPath).replace(/\/$/, '') || '/';
  const candidates = [join(DIST, clean), join(DIST, clean, 'index.html'), join(DIST, clean + '.html')];
  for (const c of candidates) {
    if (existsSync(c) && statSync(c).isFile()) return c;
  }
  return null;
}

// vercel.json redirect sources, as regular expressions
const redirects = JSON.parse(readFileSync(join(ROOT, 'vercel.json'), 'utf8')).redirects ?? [];
const redirectMatchers = redirects.map((r) => {
  const pattern = r.source
    .split(/(:[A-Za-z]+\*?)/)
    .map((part) =>
      part.startsWith(':')
        ? part.endsWith('*')
          ? '.*'
          : '[^/]+'
        : part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    )
    .join('');
  return new RegExp(`^${pattern}/?$`);
});
const isRedirected = (p) => redirectMatchers.some((m) => m.test(p));

const idCache = new Map();
function idsOf(file) {
  if (!idCache.has(file)) {
    const html = readFileSync(file, 'utf8');
    idCache.set(file, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
  }
  return idCache.get(file);
}

const problems = new Map(); // "kind target" -> Set(pages)
function report(kind, target, page) {
  const key = `${kind}\t${target}`;
  if (!problems.has(key)) problems.set(key, new Set());
  problems.get(key).add(page);
}

const files = walk(DIST);
let checked = 0;

for (const file of files) {
  const page = routeOf(file);
  const html = readFileSync(file, 'utf8');
  const targets = new Set(
    [...html.matchAll(/<(?:a|link|img|script|source|iframe)\b[^>]*?\s(?:href|src)="([^"]*)"/g)].map((m) => m[1])
  );

  for (const raw of targets) {
    if (!raw || /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(raw)) continue; // external, mailto:, data:, …
    checked++;
    const [beforeHash, hash = ''] = raw.split('#');
    const pathPart = beforeHash.split('?')[0];

    // same-page fragment
    if (pathPart === '') {
      if (hash && !SCRIPT_ANCHORS.has(hash) && !idsOf(file).has(hash)) report('missing anchor', `#${hash}`, page);
      continue;
    }

    const abs = pathPart.startsWith('/') ? pathPart : posix.join(page.endsWith('/') ? page : page + '/', pathPart);
    if (SERVER_EXACT.has(abs) || SERVER_PREFIXES.some((p) => abs === p || abs.startsWith(p))) continue;

    const target = resolveFile(abs);
    if (!target) {
      report(isRedirected(abs) ? 'links to a redirect' : 'broken link', abs, page);
      continue;
    }
    if (hash && target.endsWith('.html') && !idsOf(target).has(hash)) {
      report('missing anchor', `${abs}#${hash}`, page);
    }
  }
}

if (problems.size === 0) {
  console.log(`check-links: clean (${files.length} pages, ${checked} internal links).`);
  process.exit(0);
}

console.error(`check-links: ${problems.size} problem(s) in ${files.length} pages.\n`);
for (const [key, pages] of [...problems].sort()) {
  const [kind, target] = key.split('\t');
  const list = [...pages].sort();
  const shown = list.slice(0, 4).join(', ') + (list.length > 4 ? `, … (${list.length} pages)` : '');
  console.error(`  ${kind}: ${target}\n      on ${shown}`);
}
process.exit(1);
