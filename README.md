# KRUPS Automation — Website

Source code for the [krups-automation.com](https://krups-automation.com) rebuild — **Astro 6 + Sanity v5 + Vercel**.
**Not yet live** — DNS still points to the old Joomla site; see § 1 "Planned / deferred".

---

## 1) Current state & plan

### Stack as-built

- **Astro 6** — fully static, with selective server rendering only for draft-preview routes
- **Sanity v5** — embedded Studio at `/admin`; DE/EN via `@sanity/document-internationalization`
- **Vercel** — production hosting; auto-deploy on push to `main`
- **Self-hosted fonts** — Oswald, Barlow, JetBrains Mono (Astro Fonts API, primed from Google)
- **`@portabletext/to-html`** — Sanity PortableText → HTML for body content
- **No client-side JS framework** — interactivity is vanilla inline scripts (consent banner, PostHog)
- **Design system as law** — `src/styles/tokens.css` + `scripts/design-lint.mjs` build gate (runs via `prebuild`; fails on raw font-size / letter-spacing / hex colors / `Nms` durations / raw box-shadow in any `.astro` `<style>` block). Constitution: `DESIGN.md`.

### What's built

- **Sanity content model complete** — 15 schemas (`siteSettings`, `page`, `blockContent`, `author`, `tag`, `pillar`, `download`, `productFamily`, `product`, `industry`, `service`, `customer`, `caseStudy`, `article`) per `PHASE2-CONTENT-MODEL.md`
- **Typed query layer** — `src/sanity/queries.ts` GROQ fetchers for every content type (draft-aware) **plus hardcoded fallback data**, so pages render even if Sanity errors or is empty
- **Routes (`src/pages/`)**:

  ```
  /                                  DE homepage (hero, proof, products, Plan·Build·Run, why, industries)
  /produkte/                         product-family overview
  /produkte/[familySlug]/            family landing (eCart, Friktionsrollen)
  /produkte/[familySlug]/[productSlug]/  product detail
  /leistungen/                       6 "Run" services overview
  /leistungen/[slug]                 Run service detail
  /planung                           Plan-tier service (Produktionsplanung)
  /branchen/                         industry overview (5 industries)
  /branchen/[slug]                   industry detail
  /unternehmen /kontakt /downloads   static pages (downloads pulls from Sanity)
  /impressum /datenschutz /cookie-richtlinien   legal pages via Sanity `page` docs
  /[...slug]                         dynamic renderer for Sanity `page` docs
  /404  /sitemap.xml.ts
  /en/  /en/[...slug]                EN mirrored tree ("translation pending" banner)
  /preview/[...slug] + /preview/en   draft preview (server-rendered)
  /api/preview  /api/exit-preview  /api/contact (N8N webhook relay)
  ```

- **301 redirect map** — `vercel.json` (crawl of the old Joomla site, 2026-07-06). EN rules currently point at DE pages until translations ship; stopgap targets pending decisions (`REDIRECTS.md`)
- **Import tooling** — `scripts/import-{products,industries,services,customers,downloads,legal-pages}.py`
- **Analytics** — PostHog (EU host) loaded only after explicit cookie consent

### Planned / deferred

1. **Content entry in Sanity** — manual for products/industries/services/customers, scripted for ~13 PDFs (per `PHASE2-CONTENT-MODEL.md`)
2. **Pre-launch checklist** — DNS switch, webhook verification (see `PHASE2-CONTENT-MODEL.md` § "Webhook filter update"; original plan `PHASE1-SCAFFOLDING.md`)
3. **EN translations** — DE-first launch; EN renders a banner until the second pass
4. **Case-study index** (`/fallstudien`) — query helpers already exist; list/detail pages deliberately deferred until 2+ case studies exist in Sanity (`docs/plans/2026-07-14-case-study-index.md`)
5. **Journal** — starts fresh after launch (article queries exist; no routes yet)
6. **Redirect retargeting** — replace stopgap destinations once Philipp decides (e.g. `/de/kleinfoerdersysteme`, `/de/taktzeitberechnung`, `/de/nachhaltigkeit`)

### Known wart

`styled-components` and `@types/react*` look unused, and `src/` contains no React code — **but do not remove the React layer.** The embedded Studio at `/admin` needs it: `react`, `react-dom` and `styled-components` are peer dependencies of `sanity` and `@sanity/astro`, and the Studio route mounts with `client:only="react"`, which needs `@astrojs/react`. Public pages ship none of it.

---

## 2) Recommended target state (and why)

**Keep the stack as-is.** Target:

- Astro 6 static-first + Vercel — SSR only for `/preview` + `/api`
- Sanity v5, embedded Studio, doc-level i18n — mirrors `/` + `/en/`, supports DE-first
- `tokens.css` + `design-lint` gate — brand rules enforced mechanically
- Self-hosted fonts, PortableText→HTML, PostHog (EU) behind consent, fallback data in queries
- **No client-side JS framework on public pages** — interactivity stays vanilla inline scripts; React is confined to the Studio at `/admin`

Removing the React layer was planned on 2026-08-25 and withdrawn: see `docs/plans/2026-08-25-remove-react-layer.md`.

`useCdn` stays `false`. The site is built when content is published, and the Sanity CDN can still serve the previous version at that moment, so a rebuild could ship old text. Optional: minimal tests for `queries.ts` projections and `src/lib/schema-org.ts` if coverage is ever wanted.

---

## 3) The delta

| # | Current | Target | Action |
|---|---|---|---|
| 1 | README structure listed stale scaffolding | matches § 1 tree | done by this rewrite |
| 2 | `useCdn: false` | `useCdn: false` | keep: the CDN can serve stale content to a publish-triggered build |
| 3 | no tests (optional) | minimal query/schema-org tests | add if/when desired |

---

## Commands

| Command | Action |
| :--- | :--- |
| `npm install` | Install dependencies |
| `npm run dev` | Local dev server at `localhost:4321` |
| `npm run build` | Design-lint (`prebuild`) then production build to `./dist/` |
| `npm run lint:design` | Run the design-token gate standalone |
| `npm run preview` | Preview the production build locally |

## Environment variables

Copy `.env.example` to `.env`; production values live in Vercel. Referenced keys (from code):

- `SANITY_API_READ_TOKEN` — server-only; read token for draft fetching
- `SANITY_PREVIEW_SECRET` — server-only; signs the draft cookie. Never expose it through a `PUBLIC_` variable: `/admin` JS is public, only Studio data sits behind Sanity login
- `PUBLIC_POSTHOG_KEY` / `PUBLIC_POSTHOG_HOST` — analytics (host defaults to `https://eu.i.posthog.com`); feature off when key absent
- `N8N_CONTACT_WEBHOOK` — server-only; `/api/contact` relay target

## Content + preview workflow

1. Editor opens `/admin`, edits/creates a doc, saves (draft)
2. **Open preview** (three-dot menu / Ctrl+Alt+O) → `/api/preview?...` with a 1 h Sanity preview secret → `/preview/<slug>`. Getting a 401 on a long-open tab? Reload the Studio
3. Yellow "PREVIEW MODE — SHOWING DRAFT" banner above the page
4. Publish → Sanity webhook triggers Vercel rebuild

## i18n model

Document-level internationalization; each doc carries `language` (`de`/`en`). DE at `/`, EN at `/en/`; path-based language switch in the header. EN renders a "translation pending" banner until translated (DE-first launch). Schemas with translations: `page`, `siteSettings`, `product`, `productFamily`, `download`, `industry`, `service`, `caseStudy`, `article`.

## Deployment

Push to `main` → Vercel builds automatically. Preview routes are server-rendered Vercel Functions; everything else is prerendered static HTML. Redirect map lives in `vercel.json` and ships with each deploy.
