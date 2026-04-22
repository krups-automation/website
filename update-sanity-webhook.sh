#!/usr/bin/env bash
set -euo pipefail

# Updates the existing Sanity -> Vercel rebuild webhook so its filter covers
# every schema we now publish. Idempotent — safe to re-run whenever new
# schemas are added.
#
# Run with: bash update-sanity-webhook.sh

TOKEN=$(node -e "
const c = JSON.parse(require('fs').readFileSync('/home/ckrups/.config/sanity/config.json','utf8'));
console.log(c.authToken || (c.authTokens && Object.values(c.authTokens)[0]?.token) || '');
")

if [ -z "$TOKEN" ]; then
  echo "ERROR: no Sanity auth token found. Run: npx sanity login --provider github"
  exit 1
fi

PROJECT_ID="8075qdie"
HOOK_ID="e19cTgdVAFxB1GAd"

PAYLOAD=$(cat <<'JSON'
{
  "rule": {
    "on": ["create", "update", "delete"],
    "filter": "_type in [\"siteSettings\",\"page\",\"product\",\"productFamily\",\"download\",\"industry\",\"service\",\"customer\",\"caseStudy\",\"article\",\"author\",\"tag\",\"pillar\"]",
    "projection": "{_id, _type, _rev}"
  }
}
JSON
)

echo "--- Updating webhook $HOOK_ID ---"
curl -sX PATCH "https://api.sanity.io/v2021-10-04/hooks/projects/$PROJECT_ID/$HOOK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
echo
