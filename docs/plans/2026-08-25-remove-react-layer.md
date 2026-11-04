# Remove unused React / styled-components layer — Plan

**Status:** WITHDRAWN 2026-11-04 — do not apply; it would break the Studio at `/admin`.

**Why withdrawn:** this plan only looked at `src/`. `react`, `react-dom` and `styled-components` are
peer dependencies of `sanity` and `@sanity/astro`, and the Studio route uses `client:only="react"`,
which needs `@astrojs/react` and the `react()` integration. See trap T1 in
`docs/audit-benchmark/scoring.md`. Kept for the record; everything below is superseded.

---

**Why:** The project declares a full React toolchain but uses none of it. This plan removes the dead
config + dependencies. Verified facts: zero `.tsx`/`.jsx` files in `src/`, zero `client:` island
directives, zero `import ... from 'react'` or `styled-components` imports anywhere in `src/`. All
existing interactivity (cookie consent, PostHog, scroll reveal) is plain vanilla inline `<script>`.

---

## What (the three files that mention React)

| File | Current | After |
|---|---|---|
| `package.json` — `dependencies` | `@astrojs/react`, `react`, `react-dom`, `styled-components`, `@types/react`, `@types/react-dom` | six lines removed |
| `astro.config.mjs` | `import react from '@astrojs/react';` + `react(),` in `integrations: [...]` | import + entry removed |
| `tsconfig.json` — `compilerOptions` | `"jsx": "react-jsx"`, `"jsxImportSource": "react"` | both overrides removed (keep `extends: "astro/tsconfigs/strict"`) |

**Nothing in `src/` changes.** No source code is deleted; behavior and output are byte-for-byte
identical (Astro only emits a React runtime when a component is actually hydrated via `client:`, and
none is).

---

## Why

1. **Closes the loophole in the design gate.** `scripts/design-lint.mjs` only inspects `.astro`
   `<style>` blocks. It cannot see inside JavaScript, so a `styled-components` style like
   `color: #e8b500` lives in JS, bypasses the lint, and violates `DESIGN.md` — the rule ratified in
   commit `8184856`. Because `styled-components` is already in `package.json`, that loophole is open
   today. Removing it makes the token gate total.
2. **Protects Astro's core advantage (zero shipped JS).** With React + CSS-in-JS installed and
   configured, there's a path to accidentally hydrate an island and ship a ~50 KB runtime bundle,
   erasing the static/SEO/performance win. With the integration gone, that path doesn't exist.
3. **Removes pure dead weight.** Six packages in `node_modules` (styled-components is heavy), a
   compiler integration added to every build, and tsconfig JSX settings pointed at a compiler nothing
   invokes — with zero runtime benefit today.

---

## How (exact edits)

1. **`package.json`** — delete these six lines from `dependencies`:
   - `"@astrojs/react": "^5.0.3",`
   - `"react": "^19.2.5",`
   - `"react-dom": "^19.2.5",`
   - `"styled-components": "^6.4.1",`
   - `"@types/react": "^19.2.14",`
   - `"@types/react-dom": "^19.2.3",`
2. **`astro.config.mjs`** — delete `import react from '@astrojs/react';` and the `react(),` entry in
   the `integrations` array (the `sanity({...})` entry stays).
3. **`tsconfig.json`** — delete `"jsx": "react-jsx"` and `"jsxImportSource": "react"` from
   `compilerOptions`.

Then validate (run on the machine, not sandboxed):

```bash
npm install                 # prunes removed packages from node_modules + package-lock.json
npm run lint:design         # design gate still clean
npm run build               # production build passes
```

---

## Explicitly not in scope

- No changes to `src/` (components, layouts, pages, sanity schemas, queries).
- No changes to `DESIGN.md`, `tokens.css`, or the lint rules themselves.
- README § 3 delta table row 1–3 already describes this; mark them done once applied.
- The homepage-hero photography decision (separate thread, not part of this).

## Reversibility

Fully reversible if a real React island is ever needed (e.g. an interactive calculator): re-add
`@astrojs/react` + `react`, re-register the integration, add one `client:` component. This makes
framework use an explicit decision rather than an accident.

## Effort estimate

~10 minutes of edits + `npm install`/`npm run build` to validate. Should be a single small commit:
e.g. `chore: remove unused React/styled-components layer`.
