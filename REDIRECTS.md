# Redirect map — Joomla → Astro

`vercel.json` holds the 301 map for the DNS cutover, built from a crawl of
krups-automation.com on 2026-07-06. Vercel matches top-down; specific rules
must stay above the `/de/:path*` catch-all.

## Design

- Every old `/de/...` URL 301s to its Astro equivalent; unmatched DE URLs
  fall through to `/` via the catch-all.
- Old `/en/...` URLs point at the **DE** pages until EN translations launch.
  There is deliberately **no `/en/:path*` catch-all** — the Astro site owns
  `/en/` routes, and a catch-all would shadow them.
- `/de/leistungen/:slug` maps 1:1 (old and new slugs are identical:
  beratung, fertigung, montage, projektierung, service, steuerungsintegration).

## Stopgap targets — retarget after Philipp's decisions

| Old URL | Current target | Better target once decided |
|---|---|---|
| `/de/kleinfoerdersysteme` + 4 sub-pages | `/produkte` | Kleinfördersysteme family pages, if the family stays on the site |
| `/de/foerdersysteme/sonderentwicklungen` | `/produkte` | a Sonderentwicklungen page |
| `/de/taktzeitberechnung`, `/en/takt-time-calculation` | `/kontakt` | ported calculator or the eCart quoter |
| `/de/news/*` (12 articles), `/en/news/*` | `/` | journal articles; the battery-pack reference article is the highest-value one |
| `/de/nachhaltigkeit`, `/en/sustainability` | `/unternehmen` | a Nachhaltigkeit page |
| `/de/ecart-broschuere-digital` | `/downloads` | fine as-is (PDF is on /downloads) |

## After EN launch

Re-point the `/en/...` rules from DE pages to their `/en/...` equivalents.
