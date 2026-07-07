# DESIGN.md — KRUPS Automation (Astro site)

This is the constitution `src/styles/tokens.css` refers to. One rule:

**Pages may only do layout. Type, color, tracking, motion, and elevation come from tokens or components — never raw values.**

Enforced by `scripts/design-lint.mjs`, wired into `npm run build` via `prebuild`. It fails on any `.astro` `<style>` block containing a raw `font-size: Npx`, a raw `letter-spacing: Npx`, a hex color, a raw `Nms` duration, or a raw `box-shadow`. Run it directly with `npm run lint:design`.

## Type scale

The full ratified scale — sizes, jobs, line-heights — is documented inline in `src/styles/tokens.css` under "Typography". One size per job; don't introduce a new `font-size` value without adding it there first and giving it a name.

## Color

- Light surfaces: `--color-bg` (Warm Paper), `--color-surface` (Clay), `--color-border`, `--color-muted`, `--color-text`.
- Dark surfaces: `--color-dark-bg` (Warm Charcoal), `--color-dark-surface`, `--color-dark-text`, `--color-dark-muted`.
- Accent: `--color-accent` (KRUPS Yellow) plus `-hover`/`-soft`/`-strong` variants for hover borders and ornaments — don't hand-roll a new `rgba(232, 181, 0, ...)`, add a named variant if one doesn't fit.
- Status colors (`--color-success`/`-warning`/`-error`) are pre-darkened for WCAG AA on light and tinted surfaces — don't re-lighten them for "brand consistency."

## Motion

Four durations: `--duration-micro` (100ms, state toggles) → `--duration-short` (200ms, hover/focus) → `--duration-medium` (350ms, panel/reveal) → `--duration-long` (700ms, page-level). Pair with `--ease-out`/`--ease-in`/`--ease-in-out`. No bespoke `Nms` values — if nothing fits, that's a sign the interaction needs rethinking, not a fifth duration token.

## Spacing

Base-8 scale, `--space-1` (4px) through `--space-32` (128px). Same rule as motion: snap to the nearest step rather than inventing an in-between value.

## Editorial rules (not enforced by lint, enforced by judgment)

- **Page hierarchy is intentional.** Index/router pages (`/produkte`, `/branchen`, `/leistungen`) get the light in-flow `PageHeader`; product/detail pages get the immersive charcoal hero band. That contrast encodes "overview vs. product" — don't add a full-bleed hero to an index page just because it "feels empty." A page that routes to two things should look like a router.
- **One illustration language.** The technical-drawing blueprint SVGs (line-work schematics in `--color-drawing-line`/`--color-text`) are the only illustration style. When a page feels sparse, extend that language — don't introduce photography-as-illustration, icon sets, or a second visual system alongside it.
- **Photography is real or absent.** Product photography must be actual KRUPS equipment. AI-generated concept renders are a credibility risk on a page selling engineered hardware — better an empty slot (or the blueprint treatment) than a fake hero shot.
- **EN and preview routes are first-class.** Any pass over `de` pages (spacing, type, color) applies equally to `src/pages/preview/en/` and the `en` locale — they are not a "someday" backlog, they break the "one person made this" illusion the moment someone clicks EN.
