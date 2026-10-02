You are auditing the codebase in the current directory (Astro + Sanity + Vercel marketing site). It is read-only: do not modify files.

Scope: architecture, build quality, security, SEO/GEO, and dependency hygiene.

Rules (these matter more than coverage):
1. Every finding MUST include `file:line` and the exact command (grep, sed, cat) that proves it. If you cannot point to evidence in the repo, do not report it.
2. Before recommending removal of any dependency, config option or integration, check who requires it: read `node_modules/*/package.json` peerDependencies and the package READMEs. State what you checked.
3. Before recommending a performance or caching change, state what else in the system depends on the current behaviour (build triggers, webhooks, data freshness).
4. Do not report style preferences or cosmetic issues as high severity. Severity = user-visible, security, data-loss or SEO impact.
5. Mark each finding VERIFIED (you ran the command and saw the evidence) or UNVERIFIED (inferred). Do not hide UNVERIFIED items; do not present them as facts.
6. Report each distinct location. If a pattern occurs in N files, list all N.

Output format, one block per finding:
- id: F<n>
- title:
- severity: high | medium | low
- status: VERIFIED | UNVERIFIED
- evidence: file:line + command
- why it matters:
- recommended fix:
- what could break if the fix is applied:

End with a ranked top-5 and a list of things you checked and found to be fine.
