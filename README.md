# KRUPS Automation — Website

Source code for [krups-automation.com](https://krups-automation.com) — Astro 6 + Sanity v5 + Vercel.

## Stack

- **Astro 6** — static site with selective server rendering for preview routes
- **Sanity v5** — embedded Studio at `/admin`, DE/EN via `@sanity/document-internationalization`
- **Vercel** — production hosting + auto-deploy on git push
- **Self-hosted fonts** — Oswald, Barlow, JetBrains Mono via Astro Fonts API
- **PortableText → HTML** — for Sanity body content

## Structure

```
src/
  components/     Button, Card, Badge, Section, SiteHeader, SiteFooter, Breadcrumbs
  layouts/        BaseLayout (html wrapper + Sanity siteSettings fetch)
  pages/
    index.astro       DE homepage
    [...slug].astro   DE dynamic page renderer
    en/               EN equivalents
    preview/          Draft preview routes (server-rendered)
    api/
      preview.ts      Sets preview cookie and redirects
      exit-preview.ts Clears preview cookie
  sanity/
    schemas/        siteSettings + page schema
    queries.ts      GROQ queries + fallback data
    draft-client.ts Authenticated client for preview (drafts perspective)
  styles/
    tokens.css      Design tokens from DESIGN.md
    reset.css
    base.css        Base typography (h1-h4, body, mono utilities)
sanity.config.ts    Studio config (structure, vision, i18n, productionUrl resolver)
astro.config.mjs    Astro + Vercel adapter + fonts + @sanity/astro integration
```

## Commands

| Command           | Action                                        |
| :---------------- | :-------------------------------------------- |
| `npm install`     | Install dependencies                          |
| `npm run dev`     | Local dev server at `localhost:4321`          |
| `npm run build`   | Build production output to `./dist/`          |
| `npm run preview` | Preview the production build locally          |

## Environment variables

Copy `.env.example` to `.env` and fill in values. For production these live in Vercel.

- `SANITY_API_READ_TOKEN` — server-only; read-only token for fetching drafts (create at [sanity.io/manage/project/8075qdie/api](https://www.sanity.io/manage/project/8075qdie/api))
- `SANITY_PREVIEW_SECRET` — server-only; guards `/api/preview` endpoint
- `PUBLIC_PREVIEW_SECRET` — same value, exposed to Sanity Studio bundle so "Open preview" can sign URLs

## Content + preview workflow

1. Editor opens [`/admin`](/admin), edits or creates a document, clicks Save (creates a draft)
2. Clicks **Open preview** (three-dot menu or Ctrl+Alt+O) → opens `/api/preview?...` → redirects to `/preview/<slug>`
3. Yellow banner "PREVIEW MODE — SHOWING DRAFT" appears above the page
4. Editor reviews → back in Studio, clicks **Publish** → Sanity webhook triggers Vercel rebuild (after webhook setup)

## i18n model

- Document-level internationalization via `@sanity/document-internationalization`
- Each document has a `language` field (`de` or `en`)
- URL structure: DE at `/` (default), EN at `/en/`
- Language switcher in header: path-based swap (works for mirrored URL structures)

## Deployment

- Push to `main` → Vercel builds automatically via the connected GitHub integration
- Preview mode routes are server-rendered as Vercel Functions; everything else is prerendered static HTML

See `PHASE1-SCAFFOLDING.md` in the parent `website/` directory for the original plan and acceptance criteria.
