#!/usr/bin/env python3
"""
Sanity content import — customer reference docs.

Usage:
  SANITY_WRITE_TOKEN=sk... python3 scripts/import-customers.py [--dry-run]

Idempotent: uses createIfNotExists with deterministic _ids (customer-<slug>),
so re-running never clobbers edits made in the Studio.

publiclyReferenceable is true for the 7 names already shown on
unternehmen.astro; MINI stays false until Philipp confirms.
"""

import json
import os
import sys
import requests

PROJECT_ID = "8075qdie"
DATASET = "production"
API_VERSION = "v2024-01-01"
MUTATE_URL = f"https://{PROJECT_ID}.api.sanity.io/{API_VERSION}/data/mutate/{DATASET}"

CUSTOMERS = [
    {"name": "BMW", "slug": "bmw", "country": "Deutschland", "public": True},
    {"name": "Volkswagen", "slug": "volkswagen", "country": "Deutschland", "public": True},
    {"name": "Tesla", "slug": "tesla", "country": "USA", "public": True},
    {"name": "Ford", "slug": "ford", "country": "USA", "public": True},
    {"name": "ŠKODA", "slug": "skoda", "country": "Tschechien", "public": True},
    {"name": "ZF", "slug": "zf", "country": "Deutschland", "public": True},
    {"name": "Eaton", "slug": "eaton", "country": "USA", "public": True},
    {"name": "MINI", "slug": "mini", "country": "Großbritannien", "public": False},
]


def doc(c):
    return {
        "_id": f"customer-{c['slug']}",
        "_type": "customer",
        "name": c["name"],
        "slug": {"_type": "slug", "current": c["slug"]},
        "country": c["country"],
        "publiclyReferenceable": c["public"],
    }


def main():
    dry_run = "--dry-run" in sys.argv
    mutations = [{"createIfNotExists": doc(c)} for c in CUSTOMERS]

    if dry_run:
        print(json.dumps({"mutations": mutations}, indent=2, ensure_ascii=False))
        return

    token = os.environ.get("SANITY_WRITE_TOKEN")
    if not token:
        sys.exit("SANITY_WRITE_TOKEN not set")

    resp = requests.post(
        MUTATE_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"mutations": mutations},
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"Mutation failed ({resp.status_code}): {resp.text}")

    results = resp.json().get("results", [])
    for r in results:
        print(f"{r.get('operation', '?'):8s} {r.get('id')}")
    print(f"\n{len(results)} documents processed.")


if __name__ == "__main__":
    main()
