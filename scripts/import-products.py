#!/usr/bin/env python3
"""
Sanity content import — Friktionsrollenförderer products (L/XL/T-Serie).

Usage:
  SANITY_WRITE_TOKEN=sk... python3 scripts/import-products.py [--dry-run]

Requires a token with Editor or Administrator role:
  manage.sanity.io → project 8075qdie → API → Tokens → Add API token → Editor

What it does:
  1. Patches L-Serie (already exists) — adds intro, keyFeatures, faq
  2. Creates XL-Serie
  3. Creates T-Serie
  4. Patches Friktionsrollenförderer family — sets members array to L/XL/T
"""

import json
import os
import sys
import uuid
import requests

PROJECT_ID = "8075qdie"
DATASET = "production"
API_VERSION = "v2024-01-01"
BASE_URL = f"https://{PROJECT_ID}.api.sanity.io/{API_VERSION}/data"

FRIKTIONS_FAMILY_ID = "a8c128bd-f17e-4a3f-bb4c-8e00f1947130"
L_SERIE_ID = "29d9bf8e-314f-4535-8ee0-25bafdd4d3bb"
XL_SERIE_ID = str(uuid.uuid4())
T_SERIE_ID = str(uuid.uuid4())


def key():
    return uuid.uuid4().hex[:12]


def block(text):
    return {
        "_type": "block",
        "_key": key(),
        "style": "normal",
        "children": [{"_type": "span", "_key": key(), "text": text, "marks": []}],
        "markDefs": [],
    }


def spec(label, value, unit=None, notes=None):
    s = {"_key": key(), "label": label, "value": value}
    if unit:
        s["unit"] = unit
    if notes:
        s["notes"] = notes
    return s


def feature(title, description):
    return {"_key": key(), "title": title, "description": description}


def faq(question, answer):
    return {"_key": key(), "question": question, "answer": answer}


# ---------------------------------------------------------------------------
# L-Serie content (patches existing doc — specs already set)
# ---------------------------------------------------------------------------

L_INTRO = [
    block(
        "Die L-Serie ist die vielseitigste Serie im LOGO!MAT Baukastensystem. "
        "Mit vier verfügbaren Bahnbreiten (229, 286, 400 und 514 mm) und dem "
        "umfangreichsten Komponentenkatalog deckt sie die meisten Anwendungen in der "
        "Montageautomation ab. Werkstückträger bis 250 kg werden auf friktionsgetriebenen "
        "Rollen entlang vormontierter Bahnsegmente transportiert. Der Antrieb erfolgt "
        "über einen Drehstrommotor mit wartungsarmem Kettenantrieb."
    ),
    block(
        "Verfügbare Höhen von 170 bis über 1.000 mm, mehrstöckige Streckenführung möglich. "
        "Die L-Serie ist auch als Powered-Zone-Transfersystem ohne Werkstückträger verfügbar, "
        "zum Beispiel für den KLT-Transport (Kunststoffbehälter direkt auf der Bahn)."
    ),
]

L_FEATURES = [
    feature("Werkstückträger", "Ölresistent, kurvengängig, integrierter Rücklaufstopp, ESD-fähig. Standardschnittstellen für kundenspezifische Aufnahmen. Möglichkeit zum Durchgreifen von unten."),
    feature("Stopper", "Pneumatisch oder elektrisch, gedämpft/ungedämpft, stufenlos einstellbar."),
    feature("Abstecker", "Pneumatische Fixierung des Werkstückträgers an der Station. Grundlage für reproduzierbare Positionierung."),
    feature("Hub-Indexierstationen", "Pneumatisch, 3–300 mm Hub, ±0,1 mm Positioniergenauigkeit."),
    feature("Ecken", "Passive 90°-Umlenkung für kurvengängige Werkstückträger. LOGO!MAT ist das Original der passiven Eckumlenkung."),
    feature("Drehmodule", "Pneumatisch oder elektrisch, 90° und 270°. Flache Bauform, verschiedene Ausführungen."),
    feature("Lifte", "Vertikale Niveauänderungen für mehrstöckige Streckenführung, bis 4.500 mm Hub."),
    feature("Schnelleinzug", "Streckenweise Transportgeschwindigkeit bis zu 70 m/min für kürzere Taktzeiten."),
]

L_FAQ = [
    faq(
        "Für welche Lasten ist die L-Serie geeignet?",
        "Die L-Serie transportiert Werkstückträger bis 250 kg. Für schwerere Baugruppen (bis 1.000 kg) steht die XL-Serie zur Verfügung."
    ),
    faq(
        "Welche Bahnbreiten sind lieferbar?",
        "Die L-Serie ist in vier Bahnbreiten erhältlich: 229 mm, 286 mm, 400 mm und 514 mm. Damit deckt sie die größte Bandbreite an Werkstückträgerdimensionen im LOGO!MAT-Portfolio ab."
    ),
    faq(
        "Kann die L-Serie mehrstöckig aufgebaut werden?",
        "Ja. Über Lifte mit bis zu 4.500 mm Hub lassen sich mehrstöckige Streckenführungen realisieren, z. B. für Rücklaufstrecken unter der Montagelinie."
    ),
    faq(
        "Wie unterscheidet sich die L-Serie von der T-Serie?",
        "Die L-Serie bietet vier Bahnbreiten und den vollständigen Komponentenkatalog (19 Standardkomponenten). Die T-Serie ist auf eine Bahnbreite (400 mm) und zwei Grundmodule reduziert — wirtschaftlicher für standardisierte Anwendungen, weniger flexibel bei Sonderlösungen."
    ),
    faq(
        "Ist KLT-Transport möglich?",
        "Ja. Die L-Serie kann als Powered-Zone-System ohne Werkstückträger betrieben werden, sodass Kunststoffbehälter (KLT) direkt auf der Bahn transportiert werden."
    ),
]

# ---------------------------------------------------------------------------
# XL-Serie content (new document)
# ---------------------------------------------------------------------------

XL_SPECS = [
    spec("Max. Traglast (Standard)", "bis 600", "kg"),
    spec("Max. Traglast (mit Drehmodulen)", "bis 1.000", "kg"),
    spec("Bahnbreite", "600", "mm"),
    spec("Höhe (Oberkante Rollen)", "450–1.000", "mm"),
    spec("Positioniergenauigkeit", "±0,1", "mm"),
    spec("Mehrstöckige Führung", "Ja", None, "über Lifte bis 4.300 mm Hub"),
]

XL_INTRO = [
    block(
        "Die XL-Serie ist die Schwerlast-Serie im LOGO!MAT Baukastensystem. "
        "Mit einer Bahnbreite von 600 mm und einer Traglast bis 600 kg im Standardbetrieb "
        "(bis 1.000 kg mit Drehmodulumlenkungen) ist sie für schwere Baugruppen in der "
        "Montage- und Testautomation ausgelegt. Werkstückträger werden auf "
        "friktionsgetriebenen Rollen entlang vormontierter Bahnsegmente transportiert."
    ),
    block(
        "Verfügbare Höhen von 450 bis 1.000 mm, mehrstöckige Streckenführung möglich. "
        "Die robuste Konstruktion mit einstellbaren Friktionsrollen und hochwertigen "
        "Kugellagern gewährleistet zuverlässigen Dauerbetrieb auch unter hoher Last."
    ),
]

XL_FEATURES = [
    feature("Werkstückträger", "Kufendesign, solide Indexierhülsen, kurvengängig, verschleißarme Laufflächen — ausgelegt für dauerhaften Betrieb unter hoher Last."),
    feature("Stopper", "Pneumatisch oder elektrisch, aktive Endlage, 40–1.000 kg einstellbar."),
    feature("Abstecker", "Pneumatisch, nachrüstbar, ±0,3 mm Positioniertoleranz."),
    feature("Hub-Indexierstationen", "Bis 600 kg, 3–300 mm Hub, ±0,1 mm Positioniergenauigkeit."),
    feature("Drehmodule", "Elektrisch, FU notwendig, 90° und 270°, Abgänge im 90°-Raster."),
    feature("Ecken", "Bis 600 kg/WT, fest angetriebene Rollen, abgedeckte Zwischenräume."),
    feature("Lifte", "Kurbellifte bis 600 mm, Zahnriemenlifte bis 4.300 mm, Servo optional."),
    feature("Shuttles", "Hub-Querausschleusung, pneumatischer Hub, elektrische Bewegung, bis 600 kg."),
]

XL_FAQ = [
    faq(
        "Wie schwer dürfen die Werkstückträger auf der XL-Serie sein?",
        "Im Standardbetrieb bis 600 kg. Mit Drehmodulumlenkungen sind Lasten bis 1.000 kg möglich. Die XL-Serie ist die Plattform für Achsen, Motoren und schwere Antriebsstrangkomponenten."
    ),
    faq(
        "Warum hat die XL-Serie nur eine Bahnbreite?",
        "600 mm ist die optimierte Breite für schwere Werkstückträger im Antriebsstrang-Segment. Im Gegensatz zur L-Serie mit vier Breiten ist die XL-Serie konsequent auf eine Lastkategorie ausgelegt."
    ),
    faq(
        "Ist die XL-Serie für ölige Umgebungen geeignet?",
        "Ja. Werkstückträger und Rollenbaugruppen sind für Kühlschmierstoff- und Hydraulikumgebungen ausgelegt — bewährt in der Getriebe- und Antriebsstrangmontage."
    ),
    faq(
        "Kann ich XL-Serie und L-Serie in derselben Linie kombinieren?",
        "Die Serien sind mechanisch nicht direkt koppelbar, da Bahnbreite und Werkstückträgerprinzip sich unterscheiden. Übergaben zwischen den Systemen sind über Liftmodule oder manuelle Übergabestationen möglich. Sprechen Sie uns für Ihre konkrete Layoutaufgabe an."
    ),
    faq(
        "Welche Positioniergenauigkeit erreicht die XL-Serie?",
        "±0,1 mm an Hub-Indexierstationen — dieselbe Genauigkeit wie L- und T-Serie, trotz der deutlich höheren Traglast."
    ),
]

# ---------------------------------------------------------------------------
# T-Serie content (new document)
# ---------------------------------------------------------------------------

T_SPECS = [
    spec("Max. Traglast", "bis 250", "kg"),
    spec("Bahnbreite", "400", "mm"),
    spec("Höhe (Oberkante Rollen)", "400–1.000", "mm"),
    spec("Positioniergenauigkeit", "±0,1", "mm"),
    spec("Grundmodule für komplette Linien", "2", None, "Bahnstrecke + Drehmodul"),
]

T_INTRO = [
    block(
        "Die T-Serie ist die kompakte, kostenoptimierte Serie im LOGO!MAT Baukastensystem. "
        "Mit einer festen Bahnbreite von 400 mm und einem reduzierten Komponentenumfang "
        "ermöglicht sie den Aufbau kompletter Montagelinien mit nur zwei Grundmodulen — "
        "Bahnstrecke und Drehmodul. Werkstückträger bis 250 kg werden auf "
        "friktionsgetriebenen Rollen transportiert."
    ),
    block(
        "Verfügbare Höhen von 400 bis 1.000 mm. Die T-Serie eignet sich besonders für "
        "standardisierte Anwendungen, bei denen eine schlanke, wirtschaftliche Lösung "
        "gefragt ist — ohne Kompromisse bei Positioniergenauigkeit und Zuverlässigkeit. "
        "Anlagenerweiterungen sind ohne großen Planungsaufwand möglich."
    ),
]

T_FEATURES = [
    feature("Werkstückträger", "Kufendesign, standardisierte Schnittstelle, Rücklaufsperre, ESD-fähig, ölbeständig."),
    feature("Stopper", "Pneumatisch oder elektrisch, aktive Endlage, 10–250 kg einstellbar."),
    feature("Abstecker", "±0,2 mm Positionstoleranz, pneumatisch."),
    feature("Hub-Indexierstationen", "0–250 kg, 3–300 mm Hub, pneumatisch."),
    feature("Drehmodule", "Pneumatisch oder elektrisch, 90° oder optional 180°, beidseitiger Bahnantrieb, selbststeuernd als Ecke."),
    feature("Lifte", "Kurbellifte bis 600 mm, Zahnriemenlifte bis 4.300 mm."),
    feature("Shuttles", "Elektrisch, pneumatischer Hub, bis 3 Spuren, Friktionskupplung."),
    feature("Andockwagen", "Einhandbedienung, beidseitig andockbar, mechanische Rücklaufsperren."),
]

T_FAQ = [
    faq(
        "Was macht die T-Serie günstiger als die L-Serie?",
        "Die T-Serie hat eine feste Bahnbreite (400 mm), einen reduzierten Komponentenumfang und ist konsequent auf Standardanwendungen optimiert. Das senkt Planungs- und Fertigungsaufwand gegenüber der flexibleren L-Serie."
    ),
    faq(
        "Für welche Anwendungen ist die T-Serie am besten geeignet?",
        "Standardisierte Montagelinien mit definierten Taktzeiten und gleichförmigen Werkstückträgern bis 250 kg. Besonders stark, wenn schnell eine wirtschaftliche Lösung gebraucht wird und keine Sonderkomponenten erforderlich sind."
    ),
    faq(
        "Kann ich die T-Serie später zur L-Serie upgraden?",
        "Die Systeme sind nicht direkt ineinanderüberführbar — Bahnbreite und Werkstückträger sind unterschiedlich. Eine schrittweise Erweiterung der T-Serie-Linie ist jedoch innerhalb des T-Serie-Portfolios problemlos möglich."
    ),
    faq(
        "Welche Positioniergenauigkeit erreicht die T-Serie?",
        "±0,1 mm an Hub-Indexierstationen — gleich wie L- und XL-Serie."
    ),
    faq(
        "Was bedeutet '2 Grundmodule für komplette Linien'?",
        "Eine vollständige Transferlinie (Umlaufbahn) lässt sich aus nur zwei Modultypen aufbauen: Bahnstrecke und Drehmodul als Eckumlenkung. Das vereinfacht Planung, Bestellung und Lagerhaltung erheblich."
    ),
]

# ---------------------------------------------------------------------------
# Build mutations
# ---------------------------------------------------------------------------

def ref(doc_id):
    return {"_type": "reference", "_ref": doc_id}


mutations = [
    # 1. Patch L-Serie — add intro, keyFeatures, faq
    {
        "patch": {
            "id": L_SERIE_ID,
            "set": {
                "intro": L_INTRO,
                "keyFeatures": L_FEATURES,
                "faq": L_FAQ,
            },
        }
    },

    # 2. Create XL-Serie
    {
        "createOrReplace": {
            "_type": "product",
            "_id": XL_SERIE_ID,
            "language": "de",
            "name": "XL-Serie",
            "slug": {"_type": "slug", "current": "xl-serie"},
            "tagline": "Die Schwerlast-Serie für Achsen, Motoren und Antriebsstrangbaugruppen bis 1.000 kg.",
            "metaTitle": "LOGO!MAT XL-Serie — Friktionsrollenförderer bis 1.000 kg",
            "metaDescription": "Die LOGO!MAT XL-Serie: Schwerlast-Friktionsrollenförderer bis 600 kg (1.000 kg mit Drehmodulen), 600 mm Bahnbreite, ±0,1 mm Positioniergenauigkeit. Bewährt in Getriebe- und Antriebsstrangmontage.",
            "productFamily": ref(FRIKTIONS_FAMILY_ID),
            "intro": XL_INTRO,
            "specs": XL_SPECS,
            "keyFeatures": XL_FEATURES,
            "faq": XL_FAQ,
        }
    },

    # 3. Create T-Serie
    {
        "createOrReplace": {
            "_type": "product",
            "_id": T_SERIE_ID,
            "language": "de",
            "name": "T-Serie",
            "slug": {"_type": "slug", "current": "t-serie"},
            "tagline": "Die kompakte, kostenoptimierte Serie — komplette Montagelinien mit nur 2 Modulen.",
            "metaTitle": "LOGO!MAT T-Serie — Kompakte Friktionsrollenförderer bis 250 kg",
            "metaDescription": "Die LOGO!MAT T-Serie: Schlankes Transfersystem bis 250 kg, feste 400 mm Bahnbreite, nur 2 Grundmodule für komplette Linien. Wirtschaftlich, schnell geplant, zuverlässig.",
            "productFamily": ref(FRIKTIONS_FAMILY_ID),
            "intro": T_INTRO,
            "specs": T_SPECS,
            "keyFeatures": T_FEATURES,
            "faq": T_FAQ,
        }
    },

    # 4. Patch Friktionsrollenförderer family — set members array
    {
        "patch": {
            "id": FRIKTIONS_FAMILY_ID,
            "set": {
                "members": [
                    ref(L_SERIE_ID),
                    ref(XL_SERIE_ID),
                    ref(T_SERIE_ID),
                ]
            },
        }
    },
]

# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv
    token = os.environ.get("SANITY_WRITE_TOKEN")

    if not token:
        print("Error: SANITY_WRITE_TOKEN environment variable not set.")
        print()
        print("Generate a write token:")
        print("  1. Go to https://manage.sanity.io/projects/8075qdie/api")
        print("  2. Tokens → Add API token → Name: 'import-script', Role: Editor")
        print("  3. Run: SANITY_WRITE_TOKEN=sk... python3 scripts/import-products.py")
        sys.exit(1)

    url = f"{BASE_URL}/mutate/{DATASET}"
    if dry_run:
        url += "?dryRun=true"
        print("DRY RUN — no changes will be written\n")

    payload = {"mutations": mutations}

    print(f"Sending {len(mutations)} mutations to Sanity ({DATASET})...")
    if dry_run:
        print(f"  L-Serie ID:  {L_SERIE_ID} (patch)")
        print(f"  XL-Serie ID: {XL_SERIE_ID} (create)")
        print(f"  T-Serie ID:  {T_SERIE_ID} (create)")
        print(f"  Family ID:   {FRIKTIONS_FAMILY_ID} (patch members)")
    print()

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if resp.ok:
        result = resp.json()
        print("Success!")
        if dry_run:
            print("Dry run passed — re-run without --dry-run to apply changes.")
        else:
            print(f"Transaction ID: {result.get('transactionId', 'n/a')}")
            print(f"Results: {len(result.get('results', []))} documents affected")
            print()
            print("Next steps:")
            print("  1. Open Studio at https://krups-website.vercel.app/admin")
            print("  2. Verify XL-Serie and T-Serie documents")
            print("  3. Check Friktionsrollenförderer family — members should show L/XL/T")
            print(f"  4. Note new IDs for future use:")
            print(f"     XL_SERIE_ID = '{XL_SERIE_ID}'")
            print(f"     T_SERIE_ID  = '{T_SERIE_ID}'")
    else:
        print(f"Error {resp.status_code}:")
        print(resp.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
