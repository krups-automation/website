# Filterable Case-Study Index — Scope

**Why:** Content-strategy research (2026-07-14, memory `session-2026-07-14-content-strategy-research.md`) confirmed competitors (KUKA, Jungheinrich) partly win on *structure* — a searchable/filterable case-study library beats one-off blog posts. KRUPS' Sanity schema already supports this (`caseStudy.ts` has `industry` and `products` references); the frontend just doesn't consume it yet. No case studies exist in Sanity yet — this is infra to have ready before the first ones (Ford Cologne / BMW / SKODA / anonymized, per `content-ops/types/case-study.md`) are approved.

## What already exists

- `src/sanity/schemas/caseStudy.ts` — full schema: customer/anonymizedName, industry (ref), products (ref array), challenge/solution/body (blockContent), results (metric/value/unit array), hero + gallery images
- `src/sanity/schemas/industry.ts`, `customer.ts`, `product.ts` — referenceable filter dimensions already modeled
- Pattern to mirror: `src/pages/branchen/index.astro` + `[slug].astro` — same list→detail structure, same query helper pattern (`src/sanity/queries.ts`)

## What's missing

1. **Query helpers** in `src/sanity/queries.ts`: `getAllCaseStudies(lang, opts)`, `getCaseStudyBySlug(slug, lang, opts)` — same shape as `getAllIndustries`/`getIndustryBySlug` (lines 302-309 for reference), projecting `industry->name`, `products[]->name`, `customer->name`.
2. **`src/pages/fallstudien/index.astro`** (or `/referenzen/` — confirm URL with Philipp, matches nav naming) — list view, mirrors `branchen/index.astro` structure (numbered rows or cards).
3. **`src/pages/fallstudien/[slug].astro`** — detail view rendering challenge/solution/results/body via the existing `blockContent` renderer already used elsewhere on the site.
4. **Filter UI** — industry + product as the two filter dimensions (matches the schema's existing references, no new fields needed). Given expected volume (low double digits, not hundreds), client-side filtering on the already-fetched list is sufficient — no search backend needed. A simple `<select>` or pill-button row per dimension, filtering the rendered list via a small inline script (consistent with the site's current no-heavy-JS-framework approach).
5. **Schema markup** — `Article` JSON-LD per case study, per `content-ops/style-guide.md` §6 (already required for Case Study type; just needs wiring into the new detail page).
6. **Nav/internal linking** — add to main nav and cross-link from relevant `branchen/[slug].astro` and `produkte/` pages ("Referenzen in dieser Branche"), per style guide §3 "every page should link to 2-3 related pages."

## Explicitly out of scope for v1

- No full-text search — filter-only, dataset is too small to justify it
- No pagination — not needed until case-study count is large
- EN version — build DE first per style guide §4, translate once the first 2-3 case studies are live

## Sequencing

Build this once the first case study clears Philipp/customer approval (see `content-ops/types/case-study.md` prioritized candidates) — building the index against zero content risks getting the filter UX wrong. Reasonable trigger: start once 2+ case studies exist in Sanity.

## Effort estimate

Query helpers + list + detail page + basic filter: roughly the same order of effort as the existing `branchen` section (2 page types + 1 query file addition) — a half-day to a day of Astro work once content exists, not a large infra project.
