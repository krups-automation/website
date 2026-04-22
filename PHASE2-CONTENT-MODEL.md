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
