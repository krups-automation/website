#!/usr/bin/env bash
set -euo pipefail

# Creates the Sanity -> Vercel rebuild webhook via the Sanity Management API.
# Run with: bash create-sanity-webhook.sh

TOKEN=$(node -e "
const c = JSON.parse(require('fs').readFileSync('/home/ckrups/.config/sanity/config.json','utf8'));
console.log(c.authToken || (c.authTokens && Object.values(c.authTokens)[0]?.token) || '');
")

if [ -z "$TOKEN" ]; then
  echo "ERROR: no Sanity auth token found. Run: npx sanity login --provider github"
  exit 1
fi

PROJECT_ID="8075qdie"
DEPLOY_HOOK_URL="https://api.vercel.com/v1/integrations/deploy/prj_3mMcaay3dpOzgCBBHeWIsO3cgKvM/ekJwk0Sl6l"

PAYLOAD=$(cat <<'JSON'
{
  "type": "document",
  "name": "Vercel rebuild",
  "description": "Trigger Vercel production rebuild on content change",
  "url": "__URL__",
  "dataset": "production",
  "httpMethod": "POST",
  "apiVersion": "v2021-03-25",
  "includeDrafts": false,
  "rule": {
    "on": ["create", "update", "delete"],
    "filter": "_type in [\"siteSettings\", \"page\"]",
    "projection": "{_id, _type, _rev}"
  }
}
JSON
)
PAYLOAD="${PAYLOAD//__URL__/$DEPLOY_HOOK_URL}"

echo "--- Creating webhook ---"
curl -sX POST "https://api.sanity.io/v2021-10-04/hooks/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
echo
