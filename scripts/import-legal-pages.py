#!/usr/bin/env python3
"""
Sanity content import — legal pages (Impressum, Datenschutz, Cookie-Richtlinie).

Fetches the pages from the live Joomla site, converts the main content to
Portable Text, and creates `page` documents (language=de).

Usage:
  SANITY_WRITE_TOKEN=sk... python3 scripts/import-legal-pages.py [--dry-run]

Idempotent: createIfNotExists with deterministic _ids (page-<slug>), so
re-running never clobbers Studio edits. Delete the doc first to re-import.

The Joomla cookie table (PHPSESSID / Google Analytics) does not apply to the
Astro site and is replaced with the actual mechanisms (localStorage consent
key + PostHog after opt-in). Flag for legal review before launch.
"""

import base64
import json
import os
import re
import sys
import uuid
from html.parser import HTMLParser

import requests

PROJECT_ID = "8075qdie"
DATASET = "production"
API_VERSION = "v2024-01-01"
MUTATE_URL = f"https://{PROJECT_ID}.api.sanity.io/{API_VERSION}/data/mutate/{DATASET}"

PAGES = [
    {
        "slug": "impressum",
        "title": "Impressum",
        "source": "https://www.krups-automation.com/de/impressum",
        "meta": "Impressum der KRUPS Automation GmbH, Dernbach — Angaben gemäß § 5 TMG.",
    },
    {
        "slug": "datenschutz",
        "title": "Datenschutzerklärung",
        "source": "https://www.krups-automation.com/de/datenschutz",
        "meta": "Datenschutzerklärung der KRUPS Automation GmbH gemäß DSGVO.",
    },
    {
        "slug": "cookie-richtlinien",
        "title": "Cookie-Richtlinie",
        "source": "https://www.krups-automation.com/de/cookie-richtlinien",
        "meta": "Cookie-Richtlinie der KRUPS Automation GmbH — eingesetzte Cookies und Einwilligung.",
    },
]

BLOCK_TAGS = {"h2": "h2", "h3": "h3", "h4": "h4", "p": "normal", "blockquote": "blockquote"}


def key():
    return uuid.uuid4().hex[:12]


class PortableTextConverter(HTMLParser):
    """Flat Joomla article HTML -> Portable Text blocks."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.current = None  # {style, listItem?, children, markDefs}
        self.marks = []  # active decorator/annotation keys
        self.list_type = None
        self.skip_depth = 0  # inside script/style/form/table/nav
        self.mail_attrs = None

    # -- block helpers -------------------------------------------------
    def _open_block(self, style, list_item=None):
        self._close_block()
        self.current = {
            "_type": "block",
            "_key": key(),
            "style": style,
            "children": [],
            "markDefs": [],
        }
        if list_item:
            self.current["listItem"] = list_item
            self.current["level"] = 1

    def _close_block(self):
        junk = " \t\n﻿​ "
        if self.current and any(c["text"].strip(junk) for c in self.current["children"]):
            self.blocks.append(self.current)
        self.current = None

    def _span(self, text):
        if self.current is None:
            if not text.strip():
                return
            self._open_block("normal")
        self.current["children"].append(
            {"_type": "span", "_key": key(), "text": text, "marks": list(self.marks)}
        )

    # -- parser events -------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        if self.skip_depth:
            self.skip_depth += 1
            return
        if tag in ("script", "style", "form", "table", "nav", "figure", "iframe") or (
            tag == "ul" and "breadcrumb" in cls
        ) or (tag == "div" and "table-responsive" in cls):
            self.skip_depth = 1
            return
        if tag == "joomla-hidden-mail":
            self.mail_attrs = a
            return
        if tag in BLOCK_TAGS and not self.list_type:
            self._open_block(BLOCK_TAGS[tag])
        elif tag in ("ul", "ol"):
            self._close_block()
            self.list_type = "bullet" if tag == "ul" else "number"
        elif tag == "li" and self.list_type:
            self._open_block("normal", list_item=self.list_type)
        elif tag == "br":
            self._span("\n")
        elif tag in ("strong", "b"):
            self.marks.append("strong")
        elif tag in ("em", "i"):
            self.marks.append("em")
        elif tag == "a" and a.get("href"):
            href = a["href"]
            if href.startswith("/"):
                href = "https://www.krups-automation.com" + href
            if href.startswith(("http", "mailto:", "tel:")):
                mk = key()
                if self.current is None:
                    self._open_block("normal")
                self.current["markDefs"].append({"_type": "link", "_key": mk, "href": href})
                self.marks.append(mk)

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "joomla-hidden-mail":
            addr = None
            if self.mail_attrs:
                try:
                    first = base64.b64decode(self.mail_attrs.get("first", "")).decode()
                    last = base64.b64decode(self.mail_attrs.get("last", "")).decode()
                    addr = f"{first}@{last}"
                except Exception:
                    pass
            if addr:
                mk = key()
                if self.current is None:
                    self._open_block("normal")
                self.current["markDefs"].append(
                    {"_type": "link", "_key": mk, "href": f"mailto:{addr}"}
                )
                self.marks.append(mk)
                self._span(addr)
                self.marks.pop()
            self.mail_attrs = None
        elif tag in BLOCK_TAGS or tag == "li":
            self._close_block()
        elif tag in ("ul", "ol"):
            self.list_type = None
        elif tag in ("strong", "b") and "strong" in self.marks:
            self.marks.remove("strong")
        elif tag in ("em", "i") and "em" in self.marks:
            self.marks.remove("em")
        elif tag == "a" and self.marks:
            self.marks.pop()

    def handle_data(self, data):
        if self.skip_depth or self.mail_attrs is not None:
            return
        text = re.sub(r"\s+", " ", data)
        if text and text != " ":
            self._span(text)

    def result(self):
        self._close_block()
        return self.blocks


def bullet(text):
    return {
        "_type": "block",
        "_key": key(),
        "style": "normal",
        "listItem": "bullet",
        "level": 1,
        "children": [{"_type": "span", "_key": key(), "text": text, "marks": []}],
        "markDefs": [],
    }


# Replacement for the Joomla cookie table — the Astro site's actual mechanisms.
NEW_COOKIE_ITEMS = [
    "krups-cookie-consent (Local Storage, notwendig, krups-automation.com): "
    "speichert Ihre Einwilligungsentscheidung, bis Sie sie im Browser löschen.",
    "PostHog-Analyse-Cookies (ph_*, Analyse, nur nach Einwilligung): anonyme "
    "Nutzungsstatistik zur Verbesserung der Website, Laufzeit bis zu 1 Jahr.",
]


def fetch_main(url):
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    m = re.search(r"<main[^>]*>(.*?)</main>", resp.text, re.S)
    if not m:
        sys.exit(f"No <main> found at {url}")
    html = m.group(1)
    # Drop the H1 (rendered from doc title) and Joomla chrome
    html = re.sub(r"<h1[^>]*>.*?</h1>", "", html, flags=re.S)
    return html


def build_doc(page):
    conv = PortableTextConverter()
    conv.feed(fetch_main(page["source"]))
    body = conv.result()
    if page["slug"] == "cookie-richtlinien":
        # "Cookie-Einstellungen ändern" is a javascript: link on the old site;
        # turn it into the consent-banner re-open hook (#cookie-einstellungen)
        for b in body:
            text = "".join(c["text"] for c in b["children"]).strip()
            if text == "Cookie-Einstellungen ändern":
                mk = key()
                b["markDefs"].append(
                    {"_type": "link", "_key": mk, "href": "#cookie-einstellungen"}
                )
                for c in b["children"]:
                    c["marks"].append(mk)
        body.extend(bullet(t) for t in NEW_COOKIE_ITEMS)
    return {
        "_id": f"page-{page['slug']}",
        "_type": "page",
        "title": page["title"],
        "language": "de",
        "slug": {"_type": "slug", "current": page["slug"]},
        "metaDescription": page["meta"],
        "body": body,
    }


def main():
    dry_run = "--dry-run" in sys.argv
    mutations = [{"createIfNotExists": build_doc(p)} for p in PAGES]

    if dry_run:
        for m in mutations:
            d = m["createIfNotExists"]
            print(f"\n===== {d['_id']} — {len(d['body'])} blocks =====")
            for b in d["body"][:60]:
                txt = "".join(c["text"] for c in b["children"])
                prefix = f"[{b.get('listItem', b['style'])}]"
                print(f"{prefix:10s} {txt[:100]}")
        return

    token = os.environ.get("SANITY_WRITE_TOKEN")
    if not token:
        sys.exit("SANITY_WRITE_TOKEN not set")
    resp = requests.post(
        MUTATE_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"mutations": mutations},
        timeout=60,
    )
    if resp.status_code != 200:
        sys.exit(f"Mutation failed ({resp.status_code}): {resp.text}")
    for r in resp.json().get("results", []):
        print(f"{r.get('operation', '?'):8s} {r.get('id')}")


if __name__ == "__main__":
    main()
