#!/usr/bin/env python3
"""
Import news articles from the live Joomla site into Sanity as article drafts.

Reads the public article pages (the Joomla API is not reachable, see
docs/plans/2026-11-24-joomla-parity.md D3), converts the article body to
Portable Text, uploads the images, and writes one draft per article.

Dates come from docs/plans/2026-11-25-news-dates.csv. Internal links are
resolved through vercel.json, so they point at pages of this site.

Each article gets a deterministic id (article-joomla-<joomla id>), so a re-run
replaces the draft in place. An article that has been published is skipped:
from then on Sanity is the source, and a re-import would overwrite edits.

Usage:
  python3 scripts/import-articles.py --dry-run           # writes JSON to scratch, no Sanity writes
  SANITY_WRITE_TOKEN=sk... python3 scripts/import-articles.py
  ... --only elektrisches-ecart-liftgate                  # one article
"""

import argparse
import csv
import hashlib
import json
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

PROJECT_ID = "8075qdie"
DATASET = "production"
API_VERSION = "v2024-01-01"
API = f"https://{PROJECT_ID}.api.sanity.io/{API_VERSION}"
JOOMLA = "https://www.krups-automation.com"
ROOT = Path(__file__).resolve().parent.parent

# First batch, agreed 2026-11-25 (docs/plans/2026-11-04-news-migration.md).
BATCH = [
    "die-neue-generation-logo-mat-ecart-drehmodule",
    "elektrisches-ecart-liftgate",
    "ecart-energiesparen",
    "neu-logomat-ecart-700plus",
    "dreiphasenleuchte-fur-zustandsmeldungen-des-ecarts",
    "batteriemontagen-in-der-e-mobility",
    "unser-logo-mat-ecart-im-direkten-vergleich",
    "jetzt-optional-erhaeltlich-fremdkoerperabweiser-fuer-die-logo-mat-e-serie",
    "unsere-produktneuheit-logo-mat-ecart-hubplattform",
    "die-neue-heavy-ausfuehrung-ecart700-heavy",
]

# Articles that describe a product generation that has since been replaced.
# They keep their text and get a dated note at the top instead of a rewrite.
GENERATION_NOTES = {
    "batteriemontagen-in-der-e-mobility": (
        "Beitrag aus dem Jahr {year}",
        "Dieser Beitrag beschreibt den damaligen LOGO!MAT eCart V2. "
        "Die aktuelle Generation finden Sie unter LOGO!MAT eCart.",
    ),
    "unser-logo-mat-ecart-im-direkten-vergleich": (
        "Beitrag aus dem Jahr {year}",
        "Dieser Beitrag beschreibt den damaligen LOGO!MAT eCart V2. "
        "Die aktuelle Generation finden Sie unter LOGO!MAT eCart.",
    ),
}

HEADING_STYLE = {"h2": "h2", "h3": "h2", "h4": "h3", "h5": "h3", "h6": "h4"}


class Keys:
    """Deterministic _key values, so a re-import produces the same document."""

    def __init__(self, seed):
        self.seed = seed
        self.n = 0

    def __call__(self):
        self.n += 1
        return hashlib.sha1(f"{self.seed}:{self.n}".encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Redirects: resolve old Joomla links to pages of this site
# ---------------------------------------------------------------------------


def load_redirects():
    rules = json.loads((ROOT / "vercel.json").read_text())["redirects"]
    compiled = []
    for r in rules:
        src = r["source"]
        pattern = "^" + re.sub(r":(\w+)\*", r"(?P<\1>.*)", re.sub(r":(\w+)(?!\*)", r"(?P<\1>[^/]+)", src)) + "$"
        compiled.append((re.compile(pattern), r["destination"]))
    return compiled


def resolve_link(href, redirects):
    """Map a link from Joomla content to its target on this site (first match, like Vercel)."""
    if not href:
        return href
    parsed = urlparse(urljoin(JOOMLA + "/", href))
    if parsed.netloc not in ("www.krups-automation.com", "krups-automation.com"):
        return href
    path = parsed.path.rstrip("/") or "/"
    if re.search(r"\.(pdf|zip|docx?|xlsx?)$", path, re.I):
        return "file:" + JOOMLA + path  # uploaded to Sanity on import, see finalize()
    if "/component/jdownloads" in path:
        return "/downloads"
    for pattern, dest in redirects:
        m = pattern.match(path)
        if m:
            for k, v in m.groupdict().items():
                dest = dest.replace(f":{k}*", v).replace(f":{k}", v)
            return dest
    return path


# ---------------------------------------------------------------------------
# HTML → Portable Text
# ---------------------------------------------------------------------------


def clean(text):
    return re.sub(r"\s+", " ", text.replace("\xa0", " "))


class Converter:
    def __init__(self, key, redirects, images):
        self.key = key
        self.redirects = redirects
        self.images = images  # list of absolute image URLs to upload, filled while converting
        self.blocks = []

    def spans(self, node, marks=(), mark_defs=None):
        """Flatten inline content into spans with decorator and link marks."""
        out = []
        for child in node.children:
            if isinstance(child, NavigableString):
                text = clean(str(child))
                if text:
                    out.append({"_type": "span", "_key": self.key(), "text": text, "marks": list(marks)})
            elif isinstance(child, Tag):
                name = child.name
                if name == "br":
                    out.append({"_type": "span", "_key": self.key(), "text": "\n", "marks": list(marks)})
                elif name in ("strong", "b"):
                    out += self.spans(child, marks + ("strong",), mark_defs)
                elif name in ("em", "i"):
                    out += self.spans(child, marks + ("em",), mark_defs)
                elif name == "a" and child.get("href"):
                    k = self.key()
                    href = resolve_link(child["href"], self.redirects)
                    mark_defs.append({"_type": "link", "_key": k, "href": href,
                                      **({"blank": True} if href.startswith("http") else {})})
                    out += self.spans(child, marks + (k,), mark_defs)
                elif name == "img":
                    continue
                else:
                    out += self.spans(child, marks, mark_defs)
        return out

    def text_block(self, node, style="normal", list_item=None):
        mark_defs = []
        merged = []
        for c in self.spans(node, (), mark_defs):
            if merged and merged[-1]["marks"] == c["marks"]:
                merged[-1]["text"] += c["text"]
            else:
                merged.append(c)
        for c in merged:
            c["text"] = re.sub(r" *\n *", "\n", re.sub(r" {2,}", " ", c["text"]))
        while merged and not merged[0]["text"].strip():
            merged.pop(0)
        while merged and not merged[-1]["text"].strip():
            merged.pop()
        if not merged:
            return
        merged[0]["text"] = merged[0]["text"].lstrip()
        merged[-1]["text"] = merged[-1]["text"].rstrip()
        children = [c for c in merged if c["text"]]
        used = {m for c in children for m in c["marks"]}
        block = {
            "_type": "block",
            "_key": self.key(),
            "style": style,
            "markDefs": [m for m in mark_defs if m["_key"] in used],
            "children": children,
        }
        if list_item:
            block["listItem"] = list_item
            block["level"] = 1
        self.blocks.append(block)

    @staticmethod
    def image_url(img):
        """The full-size file when the image is a preview linked to it (sigplus galleries)."""
        a = img.find_parent("a")
        if a and re.search(r"\.(jpe?g|png|webp|gif)$", a.get("href", ""), re.I):
            return urljoin(JOOMLA + "/", a["href"])
        return urljoin(JOOMLA + "/", img["src"])

    def image_block(self, url, alt=""):
        self.images.append(url)
        self.blocks.append({"_type": "image", "_key": self.key(), "_source": url, "alt": alt})

    def walk(self, node):
        for el in node.children:
            if not isinstance(el, Tag):
                text = clean(str(el)).strip()
                if text:
                    self.blocks.append({"_type": "block", "_key": self.key(), "style": "normal",
                                        "markDefs": [], "children": [{"_type": "span", "_key": self.key(),
                                                                       "text": text, "marks": []}]})
                continue
            name = el.name
            if name == "h1":
                continue  # the title
            if name in HEADING_STYLE:
                self.text_block(el, HEADING_STYLE[name])
            elif name == "p":
                for img in el.find_all("img"):
                    self.image_block(self.image_url(img), img.get("alt", ""))
                self.text_block(el)
            elif name in ("ul", "ol"):
                for li in el.find_all("li", recursive=False):
                    self.text_block(li, list_item="bullet" if name == "ul" else "number")
            elif name == "table":
                # no table type in blockContent: one bullet per row, "Label: value"
                for tr in el.find_all("tr"):
                    cells = [clean(td.get_text(" ")).strip() for td in tr.find_all(["td", "th"])]
                    cells = [c for c in cells if c]
                    if cells:
                        fake = BeautifulSoup(f"<li>{': '.join(cells[:1])}{': ' + ' · '.join(cells[1:]) if len(cells) > 1 else ''}</li>", "html.parser").li
                        self.text_block(fake, list_item="bullet")
            elif name == "img":
                self.image_block(self.image_url(el), el.get("alt", ""))
            elif name == "iframe":
                src = el.get("src", "")
                m = re.search(r"youtube(?:-nocookie)?\.com/embed/([\w-]+)", src)
                if m:
                    href = f"https://www.youtube.com/watch?v={m.group(1)}"
                    fake = BeautifulSoup(f'<p><a href="{href}">Video auf YouTube ansehen</a></p>', "html.parser").p
                    self.text_block(fake)
            elif name == "div" and "sigplus-gallery" in (el.get("class") or []):
                for a in el.select("a.sigplus-image"):
                    self.image_block(urljoin(JOOMLA + "/", a["href"]), a.img.get("alt", "") if a.img else "")
            elif name in ("hr", "script", "style", "noscript"):
                continue
            else:
                self.walk(el)


# ---------------------------------------------------------------------------
# Article extraction
# ---------------------------------------------------------------------------


def load_dates():
    rows = csv.DictReader(open(ROOT / "docs/plans/2026-11-25-news-dates.csv", encoding="utf-8"))
    return {r["url"].rstrip("/").split("/")[-1]: r for r in rows if r["lang"] == "de"}


def published_at(row):
    value = row["published_at"]
    if re.fullmatch(r"\d{4}", value):
        return f"{value}-01-01T00:00:00Z", "year"
    return f"{value}T00:00:00Z", "day"


def extract(slug, dates, redirects):
    url = f"{JOOMLA}/de/news/{slug}"
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(attrs={"itemprop": "articleBody"})
    if body is None:
        raise RuntimeError(f"no articleBody on {url}")

    row = dates[slug]
    key = Keys(f"article-joomla-{row['joomla_id']}")
    images = []
    conv = Converter(key, redirects, images)
    conv.walk(body)

    h1 = body.find("h1")
    if h1:
        for br in h1.find_all("br"):
            br.replace_with(" ")
    title = clean(h1.get_text("")).strip() if h1 else clean(soup.title.get_text()).split(" – ")[0].strip()
    meta = soup.find("meta", attrs={"name": "description"})
    description = clean(meta["content"]).strip() if meta and meta.get("content") else None

    hero = None
    for ld in soup.find_all("script", type="application/ld+json"):
        m = re.search(r'"thumbnailUrl"\s*:\s*"([^"]+)"', ld.string or "")
        if m:
            hero = urljoin(JOOMLA + "/", m.group(1).replace("\\/", "/"))
            break
    # drop the hero from the body if it is also the first image there
    blocks = conv.blocks
    if hero and blocks and blocks[0]["_type"] == "image" and blocks[0]["_source"] == hero:
        blocks = blocks[1:]

    date, precision = published_at(row)
    if slug in GENERATION_NOTES:
        title_tpl, text = GENERATION_NOTES[slug]
        blocks.insert(0, {
            "_type": "callout", "_key": key(), "tone": "note",
            "title": title_tpl.format(year=date[:4]), "body": text,
        })

    return {
        "_id": f"drafts.article-joomla-{row['joomla_id']}",
        "_type": "article",
        "language": "de",
        "title": title,
        "slug": {"_type": "slug", "current": slug},
        "metaDescription": description,
        "summary": description,
        "publishedAt": date,
        "publishedAtPrecision": precision,
        "legacyUrl": f"/de/news/{slug}",
        "_hero": hero,
        "body": blocks,
    }


# ---------------------------------------------------------------------------
# Sanity
# ---------------------------------------------------------------------------


def upload_image(session, url, cache):
    if url in cache:
        return cache[url]
    data = requests.get(url, timeout=60).content
    ctype = mimetypes.guess_type(urlparse(url).path)[0] or "image/jpeg"
    filename = Path(urlparse(url).path).name
    r = session.post(f"{API}/assets/images/{DATASET}", params={"filename": filename},
                     data=data, headers={"Content-Type": ctype}, timeout=120)
    r.raise_for_status()
    asset_id = r.json()["document"]["_id"]
    cache[url] = asset_id
    return asset_id


def upload_file(session, url, cache):
    if url in cache:
        return cache[url]
    data = requests.get(url, timeout=60).content
    ctype = mimetypes.guess_type(urlparse(url).path)[0] or "application/octet-stream"
    r = session.post(f"{API}/assets/files/{DATASET}", params={"filename": Path(urlparse(url).path).name},
                     data=data, headers={"Content-Type": ctype}, timeout=120)
    r.raise_for_status()
    cache[url] = r.json()["document"]["url"]
    return cache[url]


def finalize(doc, asset_for, file_url=lambda u: u):
    """Replace image sources with asset references and Joomla file links with Sanity file URLs."""
    out = dict(doc)
    hero = out.pop("_hero")
    if hero:
        out["heroImage"] = {"_type": "image", "asset": {"_type": "reference", "_ref": asset_for(hero)},
                            "alt": out["title"]}
    body = []
    for b in out["body"]:
        if b["_type"] == "image":
            b = {"_type": "image", "_key": b["_key"], "alt": b.get("alt") or "",
                 "asset": {"_type": "reference", "_ref": asset_for(b["_source"])}}
        elif b["_type"] == "block":
            for m in b["markDefs"]:
                if m.get("href", "").startswith("file:"):
                    m["href"] = file_url(m["href"][5:])
                    m["blank"] = True
        body.append(b)
    out["body"] = body
    return {k: v for k, v in out.items() if v is not None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", action="append")
    ap.add_argument("--out", default=os.environ.get("IMPORT_OUT", "/tmp/import-articles"))
    args = ap.parse_args()

    slugs = args.only or BATCH
    dates = load_dates()
    redirects = load_redirects()
    docs = [extract(s, dates, redirects) for s in slugs]

    if args.dry_run:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for d in docs:
            (out / f"{d['slug']['current']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2))
        n_img = sum(1 for d in docs for b in d["body"] if b["_type"] == "image") + sum(1 for d in docs if d["_hero"])
        print(f"dry run: {len(docs)} articles, {n_img} images, JSON in {out}")
        return

    token = os.environ.get("SANITY_WRITE_TOKEN")
    if not token:
        sys.exit("SANITY_WRITE_TOKEN is not set")
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {token}"

    published = session.get(f"{API}/data/query/{DATASET}", params={
        "query": '*[_type == "article" && _id in $ids]._id',
        "$ids": json.dumps([d["_id"].removeprefix("drafts.") for d in docs]),
    }, timeout=30).json().get("result", [])

    cache = {}
    mutations = []
    for d in docs:
        if d["_id"].removeprefix("drafts.") in published:
            print(f"skip (published, Sanity is the source now): {d['slug']['current']}")
            continue
        mutations.append({"createOrReplace": finalize(d, lambda u: upload_image(session, u, cache),
                                                      lambda u: upload_file(session, u, cache))})
        print(f"draft: {d['slug']['current']}")

    if not mutations:
        print("nothing to write")
        return
    r = session.post(f"{API}/data/mutate/{DATASET}", json={"mutations": mutations}, timeout=60)
    r.raise_for_status()
    print(f"wrote {len(mutations)} drafts, uploaded {len(cache)} images")


if __name__ == "__main__":
    main()
