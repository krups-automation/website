# Full evaluation — krups-website @ HEAD (2026-11-03)

> **Run context:** evaluated at commit `47bc22e` (HEAD, 2026-10-02), working tree clean, local build executed by the reviewer.
> This is NOT a `prompt.md` benchmark run (that protocol pins commit `8184856` pre-fixes) — this is a **post-fixes, whole-repo evaluation** including a live build and dist-output forensics. Do not score it against the `scoring.md` G1–G14 list as-is; see §"Benchmark delta" for the mapping.

---

## Verdict

Unusually disciplined rebuild — stack choices, failure semantics and build gates are above typical quality for an SME site. Weak spots are content-level consistency gaps (several collide with the GEO fact sheet work in `../ai-visibility-monitor/dossier-krups-group/`) and one strategic redirect decision (news archive). All pre-launch-fixable.

## 1. Tech stack — 9/10

- Astro 6.1.8 static-first + `@astrojs/vercel`: SSR only for `/preview/*` + `/api/*` (VERIFIED: prerender log shows 25 static pages; server bundle exists only for those routes).
- Sanity v5 embedded Studio at `/admin` (hash router). Studio bundles dominate `dist` (~100 of 106 MB) but are `/admin`-isolated (VERIFIED: `/admin/index.html` + chunked `resources*` bundles).
- `@portabletext/to-html` over React PortableText — no framework needed.
- Astro Fonts API, self-hosted Oswald/Barlow/JetBrains Mono; `preload` only on display fonts (`BaseLayout.astro:83–85`).
- **Zero client-side JS framework — empirically verified**: homepage ships **0 external `<script>`**, ~7 KB inline; eCart ~12.5 KB inline.
- Doc-level i18n (`@sanity/document-internationalization`), DE-first, EN mirror with pending banner.
- PostHog EU-hosted behind consent.

**Known wart (self-documented):** `react`, `react-dom`, `styled-components`, `@astrojs/react`, `@types/react*` unused — removal plan exists (`docs/plans/2026-08-25-remove-react-layer.md`), not yet applied → F10.

## 2. Architecture — 8.5/10

- **Content model complete:** 15 schemas incl. `article`, `caseStudy`, `pillar`, `tag`, `author`, `download`, `customer` — Journal + fall studies have query helpers, routes deferred (`docs/plans/2026-07-14-case-study-index.md`).
- **Failure semantics (good & rare):** `src/sanity/queries.ts` `safeFetch` — dev degrades to fallback data; **PROD builds fail loudly** on Sanity errors (G2 fix). No silent-green empty-page builds.
- **Preview auth:** HMAC-signed expiry cookie (`lib/preview-auth.ts`), 1 h TTL, timing-safe verify, `httpOnly`+`secure`+org-mode `sameSite`, allowlisted doc types (G6 fix).
- **Sitemap:** live server route, 1 h cache; DE/EN slug pairing with `xhtml:link` hreflang triples only where both languages exist — correct DE-first behavior.
- **Redirect map:** from a real 2026-07-06 crawl; explicit product/service rules + wildcards last (see F5 for the strategic problem with the news rules).

## 3. Build quality — 9/10 (harness-verified this run)

- `npm run build` green on node 24.14.0: design-lint → 42 s Vite → **12.4 s prerender (25 pages)** → 66 s server bundle.
- `design-lint.mjs` build gate: 5 patterns (raw font-size / letter-spacing / hex / ms / box-shadow), line-numbered output, exit 1. Remaining blind spots stays as ground-truth G12 → F16 (rgba()/clamp()/px-spacing unchecked).
- Shipped HTML (homepage, `/produkte/ecart`): single H1 ✓ · 0 missing img alts ✓ · canonical at **future prod domain** (`www.krups-automation.com`, stable `@id` anchors) ✓ · og/locale/twitter ✓ · skip-link ✓.
- JSON-LD per page: Organization → WebSite → (BreadcrumbList) → Product(→Brand→PropertyValue specs) → FAQPage where content exists (VERIFIED in dist).

## 4. Security — 8/10

- `/api/contact`: per-IP sliding-window limit (5/10 min, per-instance documented), honeypot, per-field length caps, JSON validation, webhook env-only, complete status mapping 400/422/429/502/503 (G5 fix).
- Tokens: read token server-only; write token confined to `scripts/import-*.py` and present in `.env.example` (G10 fix).
- Minor: preview secret compared with `!==` (only the cookie HMAC uses `timingSafeEqual`) → F9.

## 5. Findings (harness format)

- id: F1
  title: Payload range wrong — "300–2.000 kg" vs. real 50–2,000 kg
  severity: medium · status: VERIFIED
  evidence: `src/lib/schema-org.ts:29` (Organization description); `dist`/`.vercel/output/static/produkte/ecart/index.html` meta description ("transportiert 300–2.000 kg"); `public/llms.txt` ("payloads from 300 to 2,000 kg")
  why it matters: conflicts with product reality (eCart 600 starts at 50 kg) and with the master-plan correction `8184856`; AI engines lift these exact claims (dossier-krups-group fact sheet §3).
  fix: Sanity content + `llms.txt` → "50–2,000 kg"; Organization/eCart descriptions per fact sheet.
- id: F2
  title: LinkedIn sameAs slug likely mismatched
  severity: medium · status: VERIFIED
  evidence: `src/lib/schema-org.ts:47` — `linkedin.com/company/krups-automation-gmbh/`; live research shows page slug `krups-automation`
  fix: verify + correct slug.
- id: F3
  title: Canonical email divergence
  severity: medium · status: VERIFIED
  evidence: schema-org contactPoint `info@krups-automation.com` vs. official `info@krups-online.de` used on the current Joomla site (impressum/footer)
  fix: decide one canonical (fact sheet §2, KRUPS Automation row).
- id: F4
  title: No KRUPS Group / parentOrganization node in the new schema
  severity: medium · status: VERIFIED (absence)
  evidence: `src/lib/schema-org.ts` emits company-only Organization; no `subOrganization`, no LOGOPART/LOFT nodes
  why it matters: at DNS cutover this build becomes the ONLY company schema surface — the group entity graph must live here (artifacts Block A already drafted in `../ai-visibility-monitor/dossier-krups-group/artifacts/schema-jsonld.md`).
  fix: fold group node + sister-company nodes into this build before launch; keep exactly one canonical graph.
- id: F5
  title: News archive 301 → homepage destroys the GEO citable fact layer
  severity: high · status: VERIFIED
  evidence: `vercel.json:104–111` (`/de/news/:path* → /`), `229–237` (`/en/news/:path* → /`); 66 DE / 48 EN archived articles (inventory in dossier-krups-group `03-signal-2`)
  why it matters: the news stream is the fact layer AI cites (case studies: MTU Aero Engines, Ford Cologne battery plant, DHF, Tesvolt…); redirecting to `/` discards content, URL equity and inbound links.
  fix: migrate evergreen items to `article`/`caseStudy` (schemas exist), enable `/fallstudien` + `/journal` routes, retarget redirects; only low-value items go `/`.
  correction (2026-11-04): the archive is 70 DE / 48 EN, and the dossier inventories only the 6-item series. DHF is a trade-press item about Turck, and the Cologne item does not name Ford. Full triage: `docs/plans/2026-11-04-news-migration.md`.
- id: F6
  title: SITE_URL hardcoded to vercel.app preview host
  severity: low · status: VERIFIED · evidence: `src/lib/schema-org.ts:3`
  fix: derive from env (` PUBLIC_SITE_URL`) — canonical behavior is already correct; purely hygiene.
- id: F7
  title: `hero-pick.html` dev tool ships publicly
  severity: low · status: VERIFIED · evidence: `public/hero-pick.html`
  fix: move to `scripts/` or exclude from build.
- id: F8
  title: `/ueber-krups` CMS page duplicates `/unternehmen`
  severity: medium · status: VERIFIED · evidence: prerender log built `/ueber-krups/index.html`; sitemap includes CMS page slugs generically
  fix: rename/delete doc in Sanity + 301; or map sitemap away.
- id: F9
  title: Preview secret non-timing-safe compare
  severity: low · status: VERIFIED · evidence: `src/pages/api/preview.ts` `secret !== SECRET`
  fix: `timingSafeEqual(Buffer.from(a), Buffer.from(b))`.
- id: F10
  title: Unused React/styled-components layer
  severity: medium · status: VERIFIED · evidence: `package.json:17–31`, `astro.config.mjs:54` (`react()`), `tsconfig.json:10–13`; zero `.tsx`/`.jsx`
  fix: apply existing removal plan; closes design-gate CSS-in-JS bypass.
  correction (2026-11-04): WRONG, do not apply. This is trap T1 in `scoring.md`; removal breaks the Studio at `/admin`. The removal plan is withdrawn.
- id: F11
  title: hreflang emitted only when `alternatePath` passed — DE pages currently bare
  severity: low (pre-launch) · status: VERIFIED · evidence: built pages show `hreflang: []`; `BaseLayout.astro:66–72`
  fix: wire alternates during EN pass.
- id: F12
  title: Homepage meta description is the fallback tagline
  severity: low · status: VERIFIED · evidence: dist `name="description" content="Schienengeführte Fördersysteme für Präzisionsmontage."`
  fix: per-page descriptions (fields already exist on schema).
- id: F14
  title: Stale local `.vercel/output` (July artifacts incl. `_hero-candidates/`)
  severity: low · status: VERIFIED · fix: `rm -rf .vercel/output` locally; CI is clean.
- id: F15
  title: Stray draft `src/content/hidden-cost-audit-content-DRAFT.md` inside `src/`
  severity: low · status: VERIFIED · fix: relocate to `docs/`.
- id: F16
  title: design-lint coverage still G12-scoped (5 patterns; rgba()/clamp()/px-spacing unchecked)
  severity: low · status: VERIFIED · evidence: `scripts/design-lint.mjs:37–63`
  fix: extend RULES (or accept as documented limitation).

## 6. Benchmark delta — G1–G14 ground truth at `8184856` vs. HEAD

| G | Status at HEAD | Evidence |
|---|---|---|
| G1 head missing (canonical/og/twitter/hreflang) | **fixed** — commit `ba75eca` | BaseLayout.astro:65–81 |
| G2 green empty-page builds | **fixed** (fail-loud) — `ba75eca` | queries.ts safeFetch |
| G3 soft 404s | **fixed** — `ba75eca` (404 handling) | 404.astro + route changes |
| G4 stale webhook filter | pending verification pre-launch | update-sanity-webhook.sh shipped; re-run at cutover |
| G5 contact no rate limit | **fixed** — `ecf9de2` | api/contact.ts + rate-limit.ts |
| G6 preview cookie forgeable | **fixed** — `ecf9de2` | preview-auth.ts HMAC |
| G7 visionTool ships in prod Studio | **fixed** — `ecf9de2` | dev-gated |
| G8 no llms.txt | **fixed** — `ba75eca` | public/llms.txt |
| G9 SITE_URL vercel.app | RESIDUAL → F6 | schema-org.ts:3 |
| G10 write token missing from .env.example | **fixed** | .env.example |
| G11 README stale PHASE1 reference | fixed in doc rewrite | README.md references only PHASE2 |
| G12 design-lint 5 patterns only | RESIDUAL → F16 | design-lint.mjs |
| G13 type-scale inversions | fixed in token ratification (`8184856` itself) | tokens.css |
| G14 no tests | still none (accepted as optional per README) | package.json |

## 7. Pre-launch priority list (consolidated)

1. Sanity content fact-sheet alignment: payload ranges (F1), variant naming (`eCart 700 Heavy`), canonical email (F3), `/ueber-krups` dedupe (F8) — then `llms.txt` update.
2. Fold group + sister-company JSON-LD into this build (F4) — single canonical entity graph at cutover.
3. News migration plan + redirect retargeting (F5) — decide before ENABLE-ing DNS.
4. Apply React-layer removal (F10), remove `hero-pick.html` (F7), fix LinkedIn sameAs (F2).
5. Small hygiene: F6, F9, F14, F15; optional F12, F16.
6. Then: webhook verification (G4), EN translations pass + hreflang wiring (F11), DNS switch.
