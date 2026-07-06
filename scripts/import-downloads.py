#!/usr/bin/env python3
"""
Sanity content import — download documents (brochures, datasheets).

Uploads the PDFs from ~/projekte/website/downloads/ as Sanity file assets and
creates `download` documents.

Usage:
  SANITY_WRITE_TOKEN=sk... python3 scripts/import-downloads.py [--dry-run]

Idempotent: deterministic _ids (download-<slug>) with createIfNotExists;
existing docs are skipped entirely (including the asset upload).
"""

import json
import os
import sys
import urllib.parse

import requests

PROJECT_ID = "8075qdie"
DATASET = "production"
API_VERSION = "v2024-01-01"
BASE = f"https://{PROJECT_ID}.api.sanity.io/{API_VERSION}"

SRC_DIR = os.path.expanduser("~/projekte/website/downloads")

DOWNLOADS = [
    # --- Broschüren: eCart ---
    {"file": "Broschüre_Logomat E_D_2022-06-15.pdf", "slug": "logomat-ecart-broschuere-de",
     "title": "LOGO!MAT eCart Broschüre", "lang": "de", "category": "brochure",
     "desc": "Produktbroschüre LOGO!MAT eCart — schienengeführtes Fördersystem für Lasten von 300 bis 2.000 kg."},
    {"file": "Broschüre_Logomat E_E_2022-06-17.pdf", "slug": "logomat-ecart-brochure-en",
     "title": "LOGO!MAT eCart Brochure", "lang": "en", "category": "brochure",
     "desc": "Product brochure LOGO!MAT eCart — rail-guided conveyor system for loads from 300 to 2,000 kg."},
    {"file": "KRUPS Automation_eCart_franzoesisch.pdf", "slug": "logomat-ecart-brochure-fr",
     "title": "LOGO!MAT eCart Brochure (FR)", "lang": "fr", "category": "brochure",
     "desc": "Brochure produit LOGO!MAT eCart — système de convoyage guidé sur rails."},
    # --- Broschüren: T-Serie ---
    {"file": "Broschüre_Logomat T_D_2022_06_09.pdf", "slug": "logomat-t-serie-broschuere-de",
     "title": "LOGO!MAT T-Serie Broschüre", "lang": "de", "category": "brochure",
     "desc": "Produktbroschüre LOGO!MAT T-Serie Friktionsrollenförderer."},
    {"file": "Broschüre_Logomat T_E_2022_06_29.pdf", "slug": "logomat-t-series-brochure-en",
     "title": "LOGO!MAT T-Series Brochure", "lang": "en", "category": "brochure",
     "desc": "Product brochure LOGO!MAT T-Series friction roller conveyor."},
    # --- Broschüren: Transfersysteme ---
    {"file": "Broschüre_Transportsysteme_D_2021-09-21.pdf", "slug": "logomat-transfersysteme-broschuere-de",
     "title": "LOGO!MAT Transfersysteme Broschüre", "lang": "de", "category": "brochure",
     "desc": "Übersichtsbroschüre der LOGO!MAT Transfersysteme (L- und XL-Serie)."},
    {"file": "Broschüre_Transportsysteme_E_2021_09_21.pdf", "slug": "logomat-transfer-systems-brochure-en",
     "title": "LOGO!MAT Transfer Systems Brochure", "lang": "en", "category": "brochure",
     "desc": "Overview brochure of the LOGO!MAT transfer systems (L and XL series)."},
    {"file": "KRUPS Automation_Transfersysteme_franzoesisch.pdf", "slug": "logomat-transfer-systems-brochure-fr",
     "title": "LOGO!MAT Systèmes de Transport (FR)", "lang": "fr", "category": "brochure",
     "desc": "Brochure des systèmes de transfert LOGO!MAT (séries L et XL)."},
    # --- Broschüren: Kleinfördersysteme + Modul-/Stahlkettenbänder ---
    {"file": "KF-Broschuere_K_2020.pdf", "slug": "kleinfoerdersysteme-broschuere",
     "title": "Kleinfördersysteme Broschüre", "lang": "de", "category": "brochure",
     "desc": "Broschüre der KRUPS Kleinfördersysteme — Gurtförderer, Zahnriemenförderer, Drehtische."},
    {"file": "KRUPS-Automation-Modul-und-Stahlkettenband-2019.pdf", "slug": "modul-stahlkettenbaender-broschuere",
     "title": "Modul- und Stahlkettenbänder Broschüre", "lang": "de", "category": "brochure",
     "desc": "Broschüre der KRUPS Modul- und Stahlkettenbänder."},
    # --- Datenblätter & Zeichnungen ---
    {"file": "Datenblätter Drehtisch3.pdf", "slug": "datenblaetter-drehtische",
     "title": "Datenblätter Drehtische", "lang": "de", "category": "datasheet",
     "desc": "Technische Datenblätter der KRUPS Drehtische."},
    {"file": "Kleinförderbänder Typ 30.pdf", "slug": "datenblatt-kleinfoerderband-kf-30",
     "title": "Datenblatt Kleinförderband KF-30", "lang": "de", "category": "datasheet",
     "desc": "Technisches Datenblatt Kleinförderband Typ KF-30."},
    {"file": "Kleinförderbänder Zeichnungen.pdf", "slug": "kleinfoerderbaender-zeichnungen",
     "title": "Kleinförderbänder Zeichnungen", "lang": "de", "category": "drawing",
     "desc": "Technische Zeichnungen der KRUPS Kleinförderbänder."},
]


def headers(token, content_type=None):
    h = {"Authorization": f"Bearer {token}"}
    if content_type:
        h["Content-Type"] = content_type
    return h


def existing_doc_ids(token):
    q = urllib.parse.quote('*[_type == "download"]._id')
    resp = requests.get(f"{BASE}/data/query/{DATASET}?query={q}", headers=headers(token), timeout=30)
    resp.raise_for_status()
    return set(resp.json()["result"])


def upload_asset(token, path, filename):
    with open(path, "rb") as f:
        data = f.read()
    resp = requests.post(
        f"{BASE}/assets/files/{DATASET}?filename={urllib.parse.quote(filename)}",
        headers=headers(token, "application/pdf"),
        data=data,
        timeout=300,
    )
    if resp.status_code != 200:
        sys.exit(f"Asset upload failed for {filename} ({resp.status_code}): {resp.text[:300]}")
    return resp.json()["document"]["_id"]


def main():
    dry_run = "--dry-run" in sys.argv

    missing = [d for d in DOWNLOADS if not os.path.exists(os.path.join(SRC_DIR, d["file"]))]
    if missing:
        sys.exit("Missing source files:\n" + "\n".join(d["file"] for d in missing))

    if dry_run:
        for d in DOWNLOADS:
            size = os.path.getsize(os.path.join(SRC_DIR, d["file"])) / 1e6
            print(f"download-{d['slug']:45s} {d['category']:9s} {d['lang']:2s} {size:5.1f} MB  {d['title']}")
        return

    token = os.environ.get("SANITY_WRITE_TOKEN")
    if not token:
        sys.exit("SANITY_WRITE_TOKEN not set")

    existing = existing_doc_ids(token)
    created = skipped = 0
    for d in DOWNLOADS:
        doc_id = f"download-{d['slug']}"
        if doc_id in existing:
            print(f"skip     {doc_id} (exists)")
            skipped += 1
            continue
        # Clean ASCII-ish filename for the CDN
        clean_name = f"{d['slug']}.pdf"
        asset_id = upload_asset(token, os.path.join(SRC_DIR, d["file"]), clean_name)
        doc = {
            "_id": doc_id,
            "_type": "download",
            "title": d["title"],
            "slug": {"_type": "slug", "current": d["slug"]},
            "file": {"_type": "file", "asset": {"_type": "reference", "_ref": asset_id}},
            "category": d["category"],
            "fileType": "pdf",
            "language": d["lang"],
            "description": d["desc"],
            "gated": False,
        }
        resp = requests.post(
            f"{BASE}/data/mutate/{DATASET}",
            headers=headers(token, "application/json"),
            json={"mutations": [{"createIfNotExists": doc}]},
            timeout=60,
        )
        if resp.status_code != 200:
            sys.exit(f"Doc create failed for {doc_id} ({resp.status_code}): {resp.text[:300]}")
        print(f"create   {doc_id}")
        created += 1

    print(f"\n{created} created, {skipped} skipped.")


if __name__ == "__main__":
    main()
