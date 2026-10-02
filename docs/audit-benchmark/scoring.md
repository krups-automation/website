# Audit benchmark: ground truth and scoring

Run every model against the SAME pinned commit, which predates the fixes:

    git worktree add ../krups-bench 8184856
    cd ../krups-bench && npm ci --ignore-scripts   # so node_modules peerDependencies are checkable

Run `prompt.md` once per model (same temperature, same tool access, fresh session). Save raw output as
`results/<model>.md` and record wall time and cost from the OpenRouter activity page.

## Ground truth: real findings (checked by hand at 8184856)

| # | Finding | Evidence |
|---|---|---|
| G1 | No canonical, og:*, twitter:* or hreflang in `<head>` | src/layouts/BaseLayout.astro head (lines ~50-57) |
| G2 | `safeFetch` swallows all CMS errors, build stays green with empty pages | src/sanity/queries.ts:8-20 |
| G3 | Soft 404: `Astro.redirect('/404')` in ALL 5 routes | [...slug].astro:18, branchen/[slug].astro:19, leistungen/[slug].astro:19, produkte/[familySlug]/index.astro:20, produkte/[familySlug]/[productSlug].astro:30 |
| G4 | create-sanity-webhook.sh filter is stale (2 types vs 13) | create-sanity-webhook.sh:32 vs update-sanity-webhook.sh |
| G5 | Contact API has no rate limit / CAPTCHA | src/pages/api/contact.ts |
| G6 | Preview cookie is the static value '1': anyone can set `krups-draft=1` and read drafts via the server token | src/pages/api/preview.ts:25, src/pages/preview/[...slug].astro:~17 |
| G7 | `visionTool()` ships in the production Studio | sanity.config.ts:19 |
| G8 | No llms.txt | public/ |
| G9 | SITE_URL is the vercel.app host while canonical is krups-automation.com | src/lib/schema-org.ts:3-4 |
| G10 | SANITY_WRITE_TOKEN used by scripts/*.py but missing from .env.example | scripts/import-*.py |
| G11 | README references nonexistent PHASE1-SCAFFOLDING.md | README.md:52 |
| G12 | design-lint checks only 5 patterns, misses rgba()/clamp()/spacing | scripts/design-lint.mjs:40-60 |
| G13 | Type scale inversions (h3 36px > h2-section 28px; lede 17 < body 18) | src/styles/tokens.css:68-85 |
| G14 | No tests | package.json, repo root |

Not hand-verified (do not score either way): sitemap vs single-member-family mismatch, preview vs live rendering drift, contrast failures.

## Traps: recommendations that would cause harm

| # | Trap | Why it is wrong |
|---|---|---|
| T1 | Remove react / react-dom / styled-components / @astrojs/react as "dead" | The embedded Studio at /admin requires them: peerDependencies of `@sanity/astro` and `sanity`, and the @sanity/astro README. Removal breaks the Studio. |
| T2 | Set `useCdn: true` for build-time queries | The rebuild-on-publish webhook would read stale CDN data right after a publish. |
| T3 | Treat the hardcoded Sanity projectId/dataset as a security defect | The project ID is public by design; at most a staging-split convenience. |
| T4 | Call the site "zero client JS" without qualification | Inline scripts and the consent-gated PostHog snippet exist. Minor, count as a calibration miss only. |

## Scoring (per finding the model reports)

| Event | Points |
|---|---|
| Ground-truth finding with correct file:line | +2 |
| Ground-truth finding, right idea, wrong or missing location | +1 |
| G3 reported with all 5 locations | +2 bonus (partial list: +0) |
| G6 rated high severity | +2 bonus |
| Extra finding that you verify by hand as real | +1 |
| Trap T1 or T2 recommended | -5 each |
| Trap T3 recommended | -2 |
| Claim you cannot reproduce from the cited command (fabricated) | -3 each |
| UNVERIFIED label on something that turns out true | 0 (honesty is not penalised) |
| UNVERIFIED claim presented as VERIFIED and false | -3 (counts under fabricated) |
| Cosmetic item (token bloat, duplicate radii) rated high | -1 each (calibration) |

## Also record per model

- Findings reported / ground-truth hits (recall, out of 14) / fabricated count (precision)
- Did it read peerDependencies before suggesting a removal (rule 2)? yes/no
- Top-5 overlap with ground truth G1-G3, G6
- Wall time, token cost, and tool-call count
- Format compliance (every finding has all 7 fields)

## Decision rule

Delegate a model for first-pass audits only if: recall >= 9/14, zero trap hits, fabricated <= 1, and cost per run well under
what a verified-by-you rerun would cost. Otherwise use it for breadth only and verify everything.
Re-run the same prompt against the best candidate after the repo changes to check it is not memorising this commit.
