# News archive migration — Plan

**Status:** Interim redirects applied in `vercel.json`. Migration waits on the decisions below.

**Why:** the Joomla archive sent every news URL to `/` (audit finding F5). At DNS cutover that drops the content and turns each URL into a redirect to an unrelated page.

**Inventory:** `2026-11-04-news-archive-inventory.csv`, crawled from the live site on 2026-11-04. One row per URL, with class, interim redirect, translation slug, archive position and word count.

---

## What the archive actually is

70 DE and 48 EN items, median about 186 words. Most are short announcements, not articles.

| Class | DE | EN | Treatment |
|---|---|---|---|
| `proof` | 5 | 2 | Customer or project evidence; needs a naming decision first |
| `migrate` | 22 | 14 | Evergreen product and technical content, move to `article` |
| `group` | 11 | 9 | Group company stories; feed the entity pages from F4 and the dossier |
| `retire` | 32 | 23 | Fairs, staff, films, local events; redirect only |

## Corrections to the audit (F5)

- **Thin proof layer.** Only MTU Aero Engines is a named customer story with substance.
- **Cologne item:** says "einem führenden Automobilhersteller in Köln" and never names Ford. Adding the name would be a new public claim.
- **DHF and CURRENT items:** trade-press features about suppliers (Turck, E-T-A), not customer cases. Classed `retire`.
- **BMW item:** only a trend link about Debrecen, not a customer reference. Classed `retire`.
- **TESVOLT item:** 97 words. **Battery pack item:** 74 words and anonymous. Neither is a case study as written.
- **`caseStudy` fit:** none of these has result metrics, so `results` would be empty. MTU can use the type; the rest fit `article` better.

## Blockers

1. **Dates. RESOLVED 2026-11-25:** `2026-11-25-news-dates.csv` has a date for all 118 URLs. Source: two exports of the Joomla admin article list (sorted by created and by publish start). The API is not reachable (see parity plan D3).
   - Joomla's dates are unreliable in clusters: 2020-05-04 (site move, 45 items) and 2022-09-22/26 (articles copied with "save as copy", e.g. `automatica-2025`). Those are treated as unknown.
   - `published_at` takes `created`, else `publish_up`, else the paired translation's date, else the date or year in the article's image path. `date_source` says which.
   - 35 items have a year only (`image year`). Show only the year for those, and store 1 January with the source kept, so nothing claims a precise date it does not have.
   - Doubtful: the 2020-10-29 group (5 items, among them the Hubplattform via EN) and the 2021-06-29 group (4). Plausible, but check against the article text in the fact pass.
2. **Stale facts in keepers.** Every migrated item needs a fact pass. Known so far:
   - `haake-technik-krups-automation`: "Startup" wording and 1.360 kg (fact sheet: 1,350 kg).
   - Three items use the old "eCart V2" name.
   - The automated scan only covers patterns, so it does not replace reading each item.
3. **No EN route.** `/en/journal` does not exist, and EN product pages do not exist either, so EN redirects go to DE pages, as the existing EN rules do.

## Decisions needed

| # | Decision | Owner | Recommendation |
|---|---|---|---|
| 1 | Who exports `created` dates from Joomla? | Carlo | CSV export of `id, alias, created, language` from the news category |
| 2 | Migrate 22 items, or only a first batch? | Carlo | First batch of about 10, by product relevance |
| 3 | URL: `/journal`, and `/fallstudien` or `/referenzen`? | Philipp | `/journal` plus `/referenzen`, once there are 2+ case studies (see `2026-07-14-case-study-index.md`) |
| 4 | May MTU stay named in a case study? Name Ford? | Philipp | Keep MTU if approved; keep Cologne anonymous |
| 5 | Group items: entity pages or `article`? | Carlo | Entity pages per dossier §2.6; `/unternehmen` until they exist |

## Sequence

1. Get dates (decision 1).
2. Build `/journal` index and `[slug]` with `Article` JSON-LD including `datePublished`.
3. Write `scripts/import-articles.py`, matching the other import scripts, as drafts in Sanity.
4. Fact pass, then publish. Writes to the production dataset need confirmation.
5. Retarget each migrated URL in `vercel.json` to `/journal/<slug>`, and point `/de/news` and the wildcard at `/journal`.
6. Repeat for EN after the translation pass.

## Interim redirects

Each of the 118 URLs now has its own rule ahead of the `/de/news/:path*` and `/en/news/:path*` wildcards, pointing at the closest existing page. The wildcards still go to `/` and only catch unknown URLs. These rules do nothing for visitors until DNS cutover, because `krups-website.vercel.app` has no news URLs in use.
