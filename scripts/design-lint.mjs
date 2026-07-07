#!/usr/bin/env node
/*
 * Design-lint — enforces DESIGN.md: pages may only do layout.
 * Fails (exit 1) if any .astro file writes raw type, color, tracking,
 * motion, or elevation values in a <style> block instead of using a
 * token from src/styles/tokens.css.
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, extname } from 'node:path';

const ROOT = join(import.meta.dirname, '..', 'src');

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) walk(full, out);
    else if (extname(full) === '.astro') out.push(full);
  }
  return out;
}

// Only lint the <style> block(s) of each file — frontmatter/markup can
// legitimately contain numbers (specs data, viewBox coords, etc.).
function styleBlocks(source) {
  const blocks = [];
  const re = /<style[^>]*>([\s\S]*?)<\/style>/g;
  let m;
  while ((m = re.exec(source))) blocks.push({ text: m[1], index: m.index });
  return blocks;
}

function lineOf(source, offset) {
  return source.slice(0, offset).split('\n').length;
}

const RULES = [
  {
    name: 'raw font-size (px)',
    re: /font-size:\s*[0-9]/g,
    hint: 'use a --font-size-* token',
  },
  {
    name: 'raw letter-spacing (px)',
    re: /letter-spacing:\s*-?[0-9.]+px/g,
    hint: 'use a --tracking-* token',
  },
  {
    name: 'hex color',
    re: /#[0-9a-fA-F]{3,8}\b/g,
    hint: 'use a --color-* token',
  },
  {
    name: 'raw ms duration',
    re: /\b[0-9]+ms\b/g,
    hint: 'use a --duration-* token',
  },
  {
    name: 'raw box-shadow',
    re: /box-shadow:\s*[0-9-]/g,
    hint: 'use a --shadow-* token',
  },
];

const files = walk(ROOT);
let violations = 0;

for (const file of files) {
  const source = readFileSync(file, 'utf-8');
  for (const block of styleBlocks(source)) {
    for (const rule of RULES) {
      rule.re.lastIndex = 0;
      let m;
      while ((m = rule.re.exec(block.text))) {
        const line = lineOf(source, block.index + m.index);
        console.error(`${file}:${line}  ${rule.name} — ${m[0].trim()}  (${rule.hint})`);
        violations++;
      }
    }
  }
}

if (violations > 0) {
  console.error(`\ndesign-lint: ${violations} violation(s) in ${files.length} files checked.`);
  process.exit(1);
}
console.log(`design-lint: clean (${files.length} files checked).`);
