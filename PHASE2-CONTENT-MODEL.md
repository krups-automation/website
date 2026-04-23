# Phase 2 — Content model plan

Scope: product / industry / service / customer / caseStudy / article / download Sanity schemas,
plus supporting types (author, tag, pillar, productFamily). Localization throughout.

Deferred to later Phase 2 items: real content entry, image helpers, schema.org JSON-LD,
Pagefind, PostHog, EN translations.

---

## Guiding principles

- **Tight structure for products / industries / services / caseStudies** — dedicated fields
  (specs table, FAQ, features) so editors fill forms rather than hand-composing markup.
- **Flexible body for articles + long-form intro text** — PortableText with embedded Image,
  Quote, Callout, Table blocks.
- **References for relationships** — no duplication of product spec data into industries or
  case studies; each entity is the single source of truth.
- **Localization via `@sanity/document-internationalization`** on every user-facing doc.
  Structural fields (references, flags, slugs) stay singular.

---

## Schemas

### Primary

#### `product`
LOGO!MAT eCart, L-Serie, XL-Serie, T-Serie. Potentially overview pages (Friktionsrollen,
Fördersysteme) if we treat them as `productFamily` landing pages instead.

```
name              string, required
slug              slug, required (source: name)
productFamily     reference -> productFamily
tagline           string, short headline
metaTitle         string
metaDescription   text
heroImage         image (with alt, caption)
intro             blockContent (short, PortableText)
specs             array of {label, value, unit, notes}
keyFeatures       array of {title, description, icon?}
useCases          array of reference -> industry
technicalDrawings array of image
faq               array of {question, answer}
downloads         array of reference -> download
relatedProducts   array of reference -> product
body              blockContent (long, optional)
```

#### `productFamily`
Groups eCart / Friktionsrollen (L, XL, T) / Fördersysteme-Übersicht pages.

```
name              string
slug              slug
description       text
heroImage         image
members           array of reference -> product
```

#### `industry`
Battery module assembly, drivetrain, test automation, commercial vehicles, heavy assembly.
Mirrors the v3 industry page structure from `/home/ckrups/projekte/content-ops`.

```
name                 string
slug                 slug
tagline              string
metaTitle            string
metaDescription      text
heroImage            image
characterBar         array of {label, value}  // 3-4 stats
whatMoves            blockContent  // materials, weights, cycles
bottleneck           blockContent  // why is it hard today
requirements         array of {label, value, notes}  // core-6
alternatives         blockContent  // external-only competitors
solutionRouting      blockContent  // how KRUPS solves
recommendedProducts  array of reference -> product
proof                array of reference -> caseStudy
faq                  array of {question, answer}
cta                  object {headline, description, buttonLabel, buttonUrl?}
```

#### `service` (Leistungen)
```
name              string
slug              slug
metaTitle         string
metaDescription   text
summary           text
heroImage         image
processSteps      array of {stepNumber, title, description}
deliverables      array of string
body              blockContent
relatedServices   array of reference -> service
faq               array of {question, answer}
```

Open question: need to read the current Leistungen pages on krups-automation.com to derive
the actual list.

#### `customer`
BMW, Ford, ŠKODA, VW, MINI, Tesla, ZF, EATON (confirmed public) + pending-confirmation ones.

```
name                    string, required
slug                    slug
logo                    image
industry                reference -> industry
country                 string
publiclyReferenceable   boolean, default false    // see open question
description             text (internal use, not rendered)
```

#### `caseStudy`
```
title                string
slug                 slug
metaTitle            string
metaDescription      text
customer             reference -> customer (optional)
anonymizedName       string (used when customer ref is empty, e.g. "German OEM, Bavaria")
industry             reference -> industry
products             array of reference -> product
challenge            blockContent
solution             blockContent
results              array of {metric, value, unit}
heroImage            image
gallery              array of image
publishedAt          datetime
body                 blockContent
```

Validation: require either `customer` or `anonymizedName` (not both empty).

#### `article` (Journal)
Flexible PortableText body per our agreement.

```
title              string
slug               slug
metaTitle          string
metaDescription    text
summary            text
heroImage          image
author             reference -> author
publishedAt        datetime
pillar             reference -> pillar
tags               array of reference -> tag
body               blockContent (rich: Image, Quote, Callout, Table, CodeBlock, Figure)
relatedArticles    array of reference -> article
relatedProducts    array of reference -> product
```

#### `download`
PDFs (brochures), STEP files, data sheets.

```
title              string
slug               slug
file               file (Sanity asset)    // see open question on hosting
fileType           string enum: pdf | step | dxf | zip | other
language           string enum: de | en | fr | multilingual
description        text
relatedProducts    array of reference -> product
relatedIndustries  array of reference -> industry
gated              boolean, default false    // gated = requires lead form
```

### Supporting

- `author` — name, role, photo, bio, slug
- `tag` — name, slug (used for article filtering)
- `pillar` — name, slug, description (ties to content-ops pillar model — hard schema so
  editors pick from defined list, not free text)

---

## Localization

All user-facing doc types get `@sanity/document-internationalization` wrappers (DE default,
EN). That already exists for `siteSettings` + `page` — same pattern applied to every new
primary doc.

Fields inside docs that localize per-document:
- `name` / `title`, `tagline`, `metaTitle`, `metaDescription`, `summary`
- All `blockContent` body fields
- `characterBar`, `specs`, `keyFeatures`, `requirements`, `faq`, `cta`, `results` —
  localized at field level via `internationalizedArray` where nested

References, slugs (structural), dates, booleans, enums: not localized.

---

## Webhook filter update

Current filter only fires on `siteSettings` + `page`. After Phase 2 schemas land, update to:

```
_type in ["siteSettings","page","product","productFamily","industry","service",
          "customer","caseStudy","article","author","tag","pillar","download"]
```

Script: `create-sanity-webhook.sh` — re-run after deleting the current hook, or PATCH the
existing one via the API using the existing hook ID `e19cTgdVAFxB1GAd`.

---

## Implementation order

Each step: write schema files in `src/sanity/schemas/`, register in `schemas/index.ts`
(auto-picks-up in Studio), verify in the embedded Studio at `/admin`.

1. **Shared foundation**: `blockContent` config (reusable rich-text definition with custom
   marks / blocks), `author`, `tag`, `pillar`
2. **Products**: `productFamily` → `product` (depends on download, so skeleton references
   come later), `download`
3. **Industries**: `industry` (references `product`, `caseStudy`)
4. **Services**: `service`
5. **Proof**: `customer`, `caseStudy`
6. **Journal**: `article`
7. **Studio structure**: customize left-nav desk structure so editors see sensible groupings
   (Products, Industries, Services, Proof, Journal, Settings)
8. **Queries + types**: extend `src/sanity/queries.ts` with typed GROQ fetchers per schema
   (kept server-side where needed for drafts)
9. **Webhook filter update**: PATCH hook `e19cTgdVAFxB1GAd` to match new `_type` list

Commit per step (9 commits). Each verifiable in Studio before moving on.

---

## Decisions (confirmed 2026-04-22)

1. **Services list (confirmed — 6 services)** from current Joomla site:
   - Beratung (Consultation) — `/de/leistungen/beratung`
   - Projektierung (Project Engineering) — `/de/leistungen/projektierung`
   - Fertigung (Manufacturing) — `/de/leistungen/fertigung`
   - Montage (Assembly/Installation) — `/de/leistungen/montage`
   - Steuerungsintegration (Control System Integration) — `/de/leistungen/steuerungsintegration`
   - Service (Maintenance/Support) — `/de/leistungen/service`
2. **Download hosting** — Sanity Asset CDN.
3. **Customer publicReferenceable default** — `false` (explicit opt-in).
4. **caseStudy validation** — enforce "either customer OR anonymizedName is filled".
5. **productFamily** — gets landing-page content fields (hero, intro, features). Not purely
   a grouping concept. Friktionsrollen overview page renders from its `productFamily` doc.

---

## Out of Phase 2 schema scope

- Navigation / menu schema (we'll handle nav additions when we wire actual pages)
- Footer column content schema (footer currently reads from `siteSettings` — extend when needed)
- Forms / lead-capture schema (gated downloads flag is declared but the form itself comes later)
- Redirects table (Joomla-to-new-site redirects — separate concern, handled at Vercel rewrite level)

---

## Phase 2 item 3 — Content migration decisions (2026-04-23 interview)

**Narrative frame:** Plan · Build · Run (three-stage lifecycle). Top nav becomes
`Planung · Produkte · Leistungen · Branchen · Unternehmen`.

### Product structure (Q1)
- **2 families:** `eCart`, `Friktionsrollenförderer`.
- **4 products:** eCart V3, L-Serie, XL-Serie, T-Serie. eCart family has 1 product today; symmetry with Friktionsrollen is deliberate + future-proofs for variants.
- **Sonderentwicklungen** is NOT a product or service doc — integrated as a section inside each family's landing page ("need something custom?" → contact deeplink). No schema of its own.

### Consulting offer (Q1 follow-up)
- **New `Planung` page** at top of nav for production-line-planning consulting. Reuse `service` schema now; promote to `consultingOffer` if content outgrows it.
- Launch with placeholder/teaser content until Philipp green-lights; nav item + URL exist from day one for SEO.
- Plan · Build · Run section added to homepage between Products and Industries to tie the narrative.

### Product copy (Q2)
- **Hybrid (C):** port specs + feature lists verbatim (Philipp-approved factual content); rewrite hero/intro/FAQ to match homepage voice + style guide.

### Industry pages (Q3)
- **Source:** content-ops v3 mockups (content-complete, Variant C locked, FAQPage schema ready).
- **Workflow:** enter in Sanity as drafts (C). Tighten to public-approved customers only (BMW, Ford, ŠKODA, VW, MINI, Tesla, ZF, EATON). Philipp review unblocks publish.

### Leistungen — schema routing (Q4)
- **One `service` schema, two routes:**
  - `/planung` renders the single "Plan" doc (Produktionsplanung).
  - `/leistungen/<slug>` renders the 6 "Run" docs (Beratung, Projektierung, Fertigung, Montage, Steuerungsintegration, Service).
- Schema gets a `tier: 'plan' | 'run'` field to drive the routing.
- **Copy:** fresh rewrite for all 7 (old Joomla copy is thin/generic; nothing worth porting verbatim).

### Journal / blog (Q5)
- **Start fresh** with content-ops pillar model post-launch.
- Old Joomla blog posts NOT migrated. First journal article lands post-launch.
- Backlink audit on old blog URLs: optional, later (skip if no high-value territory).

### Redirects (Q6)
- **URL strategy:** clean slugs (already decided in Phase 1 — DE at root, EN under `/en/`).
- **When:** build the map at cutover, not per-page.
- **Orphans:** redirect to most relevant category when obvious, homepage as fallback, 404 only when honest.

### Language (Q7)
- **DE-first launch.** EN rendered with "translation pending, view German" banner until second pass.
- **EN translation pathway:** Claude drafts → Philipp/Viktor review. Second pass after DE is stable (~2-3 weeks post-launch).

### Entry method (Q8)
- **Manual in Studio** for products (4), industries (5), services (7), customers (8) — gives us a free QC pass.
- **Scripted** for downloads (13 PDFs in `website/downloads/`) — upload to Sanity Asset CDN + create `download` docs programmatically.

### Customer whitelist (confirmed public)
BMW, Ford, ŠKODA, VW, MINI, Tesla, ZF, EATON. Everything else waits for Philipp confirmation.

---

## Execution order — Phase 2 item 3

1. **Schema tweaks**
   - Add `tier` field to `service` schema (values: `plan`, `run`).
   - Small schema updates driven by interview decisions, if any surface during entry.
2. **Three-stage homepage section** (Plan · Build · Run teaser band between Products and Industries).
3. **Top nav** — add "Planung" item, rename "Leistungen" section in nav to reflect the Run tier (or leave as "Leistungen" since it's the more familiar label).
4. **Astro routes**
   - `/produkte` — family overview (2 families)
   - `/produkte/[familySlug]` — family landing page (eCart, friktionsrollen)
   - `/produkte/[familySlug]/[productSlug]` — product detail (V3, L-Serie, XL, T)
   - `/planung` — single Plan-tier service page
   - `/leistungen` — overview of 6 Run services
   - `/leistungen/[slug]` — Run service detail
   - `/branchen` — overview of 5 industries
   - `/branchen/[slug]` — industry detail
5. **Content entry** (manual in Studio)
   - 8 customer docs (tiny)
   - 2 product family docs
   - 4 product docs (hybrid copy)
   - 7 service docs (fresh copy — 6 Run + 1 Plan placeholder)
   - 5 industry docs as drafts (from content-ops v3)
6. **Downloads script** — upload 13 PDFs to Sanity + create download docs
7. **JSON-LD for Product / Service / FAQPage** (completes Phase 2 item 5b)
8. **Deploy, QC, iterate**
