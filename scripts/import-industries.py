#!/usr/bin/env python3
"""
Sanity content import — 5 industry pages (published, pending Philipp review of customer refs).

Usage:
  SANITY_WRITE_TOKEN=sk... python3 scripts/import-industries.py [--dry-run]
"""

import os
import sys
import uuid
import requests

PROJECT_ID = "8075qdie"
DATASET = "production"
API_VERSION = "v2024-01-01"
BASE_URL = f"https://{PROJECT_ID}.api.sanity.io/{API_VERSION}/data"

# Product IDs
ECART_ID      = "574774ec-fabb-43c9-8cd1-efe39b9fe5c8"
L_SERIE_ID    = "29d9bf8e-314f-4535-8ee0-25bafdd4d3bb"
XL_SERIE_ID   = "a4468474-a399-45f4-b061-62aab562b08f"


def key():
    return uuid.uuid4().hex[:12]

def block(text):
    return {
        "_type": "block", "_key": key(), "style": "normal",
        "children": [{"_type": "span", "_key": key(), "text": text, "marks": []}],
        "markDefs": [],
    }

def char(label, value):
    return {"_key": key(), "label": label, "value": value}

def req(label, value, notes=None):
    r = {"_key": key(), "label": label, "value": value}
    if notes:
        r["notes"] = notes
    return r

def faq(question, answer):
    return {"_key": key(), "question": question, "answer": answer}

def ref(doc_id):
    return {"_type": "reference", "_ref": doc_id}


# ---------------------------------------------------------------------------
# 1. Batteriemontage
# ---------------------------------------------------------------------------

BATTERIE = {
    "_type": "industry",
    "_id": str(uuid.uuid4()),
    "language": "de",
    "name": "Batteriemontage",
    "slug": {"_type": "slug", "current": "batteriemontage"},
    "tagline": "Welche Anforderungen Batteriemodul- und Packfertigung an ein Transportsystem stellt, wie gängige Ansätze im Vergleich abschneiden und welche KRUPS-Lösung zu Ihrem Prozess passt.",
    "metaTitle": "Fördersystem Batteriemontage — Anforderungen und Systemvergleich",
    "metaDescription": "Batteriemodul- und Packfertigung: Anforderungen an Nutzlast (300–1.500 kg), Positioniergenauigkeit (±1 mm), Werkstückversorgung und ESD. Systemvergleich und KRUPS-Lösung.",
    "characterBar": [
        char("Typisches Packgewicht inkl. Vorrichtung", "300–1.500 kg"),
        char("Positioniertoleranz an Fügestationen", "±1 mm"),
        char("Taktzeit pro Station", "60–90 s"),
        char("Umgebungsanforderungen", "ESD + ISO 8"),
    ],
    "whatMoves": [
        block("Eine Batteriepack-Montagelinie bewegt eine breite Bauteilklasse: einzelne Batteriemodule von 300–800 kg werden zu Modulstapeln verbunden, mit BMS, Kühlplatte und Gehäuse zu fertigen Packs von bis zu 1.500 kg integriert. Inklusive Montagevorrichtung und Transportträger kommen Gesamtgewichte bis 2.000 kg auf das Transportsystem. Zwischen den Stationen — Moduleinsetzen, HV-Verschraubung, Kühlplatten-Dichtungsprüfung, BMS-Konfiguration, End-of-Line-Test — muss jeder Pack wiederholgenau positioniert werden, damit Roboter und Werker ohne mechanische Nachpositionierung zugreifen können."),
        block("Eine typische OEM-Linie fertigt zwei bis vier Packvarianten im Mix: unterschiedliche Kapazitäten, Geometrien, Zellchemien. Taktzeiten liegen bei 60–90 s pro Station, Jahreskapazitäten bei 150.000–500.000 Packs, 24/7-Betrieb. Die Fertigung findet in ISO-8-nahen Umgebungen statt — partikelarm, aber keine echte Reinraumumgebung wie in der Zellproduktion."),
    ],
    "bottleneck": [
        block("Die Batteriepack-Fertigung verschärft mehrere Anforderungen gleichzeitig: hohe Nutzlast und Präzision, hohe Variantenvielfalt und 24/7-Verfügbarkeit, elektrische Bauteil-Energieversorgung für Tests und Sicherheit direkt neben HV-Komponenten. Jede einzelne Anforderung lässt sich mit einem Standardsystem lösen — die Kombination nicht. Ein AGV trägt 1.500 kg, positioniert aber zu grob. Eine Rollenbahn positioniert präzise, frisst aber Taktzeit durch An-/Abdocken. Ein Skid-Förderer skaliert schlecht auf Variantenmix."),
        block("Hinzu kommt die zeitliche Dimension: Ein EOL-Test (Isolationsprüfung, BMS-Kommunikation, Kapazitätsmessung) benötigt pro Pack 30–60 s elektrische Versorgung. Wenn diese Versorgung nur an der Teststation steckt, gehen pro Pack 10–15 s für Andocken und Trennen verloren — bei 300.000 Packs pro Jahr sind das 1.250 Stunden Zusatzbelegung einer Station. Eine durchgängige Werkstückversorgung auf der Transportstrecke macht aus Transportzeit Testzeit."),
    ],
    "requirements": [
        req("Nutzlast pro Träger", "300–1.500 kg", "mit Reserve bis 2.000 kg; Modul bis fertiger Pack auf derselben Linie"),
        req("Positioniergenauigkeit", "±1 mm", "an Fügestationen; robotergestützte HV-Verschraubung ohne Nachpositionierung"),
        req("Taktzeit / Durchsatz", "60–90 s / Station", "200.000–500.000 Packs/Jahr, 3-Schicht-Betrieb"),
        req("Variantenvielfalt", "2–4 Packvarianten", "Rekonfiguration im laufenden Betrieb"),
        req("Umgebung", "ESD + ISO-8-nah", "elektrostatische Empfindlichkeit der Zellelektronik, HV ab Modulstapelung"),
        req("Verfügbarkeit", ">99 %", "bei 3-Schicht-Betrieb; Jahreskapazität nicht kompensierbar"),
        req("Werkstückversorgung", "24–48 V DC, ≥200 W", "EOL-Test und BMS-Kommunikation während Transport"),
    ],
    "alternatives": [
        block("Drei Systemkategorien werden real eingesetzt. Schwerlast-AGV erreichen die Nutzlast, liefern aber typisch nur ±5–10 mm Positioniergenauigkeit und keine durchgängige Werkstückstromversorgung. Rollenbahnen mit Hubindexierung positionieren präzise, erzeugen aber 15–25 s Overhead pro Station für An-/Abdocken. Skid-Förderer sind für fixe Takte ausgelegt und skalieren schlecht auf 2–4 Packvarianten im Mix."),
        block("Keines dieser Systeme erfüllt gleichzeitig: Schwerlast, ±1 mm Positionierung, durchgängige Werkstückversorgung und Variantenflexibilität. Genau diese Kombination ist die Kernstärke schienengeführter Carrier-Systeme."),
    ],
    "solutionRouting": [
        block("Für die Batteriemontage empfiehlt KRUPS das LOGO!MAT eCart-System. Die passive Schieneninfrastruktur versorgt jeden Carrier mit 24–48 V DC — durchgängig, nicht nur an Stationen. EOL-Test und BMS-Kommunikation laufen parallel zum Transport. Positionierung auf ±0,6 mm an jeder Station ohne separaten Hubindexierungsschritt."),
        block("Bei Gesamtgewichten über 1.500 kg (schwere Pack-Varianten plus Vorrichtung) empfehlen wir eine technische Klärung der genauen Lastverteilung vor der Systemauswahl. Für Linien mit Modulgewichten unter 600 kg ist auch die XL-Serie als kostenoptimierte Alternative prüfenswert."),
    ],
    "recommendedProducts": [ref(ECART_ID), ref(XL_SERIE_ID)],
    "faq": [
        faq("Welche Nutzlast deckt ein schienengeführtes Transportsystem in der Batteriepack-Fertigung ab?", "Das eCart-System deckt 300–2.000 kg ab. Für einzelne Batteriemodule (300–800 kg) eignet sich eCart 600 oder eCart 700, für fertige Packs (bis 1.500 kg) eCart 700+, für schwere Sonderanwendungen bis 2.000 kg gibt es projektspezifische Konfigurationen."),
        faq("Wie wird die Stromversorgung für EOL-Tests während des Transports bereitgestellt?", "Die Schieneninfrastruktur versorgt jeden Carrier mit 24–48 V DC — durchgängig, nicht nur an Stationen. Isolationsprüfung und BMS-Kommunikation laufen parallel zum Transport, während der Carrier zur nächsten Station fährt."),
        faq("Ist das System für ISO-8-nahe Umgebungen in der Packfertigung geeignet?", "Ja. Die passive Schieneninfrastruktur hat keine abriebgefährdeten Bodenkontakte, und die Carrier erzeugen keinen signifikanten Partikelabrieb. Das System ist nicht für echte Reinräume (ISO 5–7) der Zellproduktion ausgelegt — wohl aber für die ISO-8-nahe Packfertigung."),
        faq("Was passiert, wenn ein Carrier ausfällt — steht die Linie still?", "Nein. Ein defekter Carrier wird an einer Ausschleusposition aus dem Kreislauf entfernt, die übrigen fahren weiter. Die Systemverfügbarkeit liegt bei >99,5 % im 24/7-Betrieb, unabhängig von einzelnen Carrier-Ausfällen."),
        faq("Wann ist ein AGV die bessere Wahl als ein schienengeführtes System?", "Wenn flexibler Routenwechsel oder gebäudeübergreifender Transport wichtiger ist als Positionierung und Werkstückversorgung. Schwerlast-AGV bis 1.500 kg existieren, erreichen aber typischerweise nur ±5–10 mm und bieten keine durchgängige Werkstromversorgung."),
    ],
    "cta": {
        "headline": "Projekt Batteriemontage besprechen",
        "description": "Gewicht, Takt, Stationslayout — wir rechnen durch, welche LOGO!MAT-Plattform zu Ihrer Packfertigung passt.",
        "buttonLabel": "Jetzt anfragen",
        "buttonUrl": "/kontakt",
    },
}

# ---------------------------------------------------------------------------
# 2. Antriebsstrang
# ---------------------------------------------------------------------------

ANTRIEB = {
    "_type": "industry",
    "_id": str(uuid.uuid4()),
    "language": "de",
    "name": "Antriebsstrang",
    "slug": {"_type": "slug", "current": "antriebsstrang"},
    "tagline": "Welche Anforderungen die Achs-, Getriebe- und E-Achs-Montage an ein Transportsystem stellt, wie gängige Ansätze abschneiden und welche KRUPS-Lösung zum OEM- oder Tier-1-Prozess passt.",
    "metaTitle": "Fördersystem Antriebsstrang — Anforderungen und Systemvergleich",
    "metaDescription": "Achs-, Getriebe- und E-Achs-Montage: Nutzlasten 200–1.500 kg, 4–8 Varianten auf gemeinsamer Linie, öl- und fettbelastete Umgebung. Systemvergleich und KRUPS-Lösung.",
    "characterBar": [
        char("Achsen, Getriebe, E-Achsen", "200–1.500 kg"),
        char("An Verschraubungsstationen", "±0,5 mm"),
        char("Auf gemeinsamer Linie", "4–8 Varianten"),
        char("Dauerbelastung, keine Reinraum-Umgebung", "Öl + Fett"),
    ],
    "whatMoves": [
        block("Die Antriebsstrang-Montage umfasst Vorder- und Hinterachsen (200–600 kg), Differenziale und Getriebeeinheiten (150–400 kg), vollständige E-Achsen mit integriertem Motor und Getriebe (300–800 kg) sowie Sonderausführungen bis 1.500 kg. Alle Baugruppen teilen einen kritischen Prozessschritt: präzise Positionierung unter reproduzierbaren Bedingungen für Verschraubung, Öleinfüllung, Drehmomentmessung und Funktionsprüfung."),
        block("OEM-Linien und Tier-1-Zulieferer fertigen typisch 4–8 Antriebsstrang-Varianten auf gemeinsamer Strecke — Vorderachse Standard, Hinterachse Standard, Hinterachse Performance, E-Achse verschiedener Leistungsklassen. Der Variantenmix ändert sich mit Modellläufen und erfordert Umrüstbarkeit ohne Linienumbau."),
    ],
    "bottleneck": [
        block("Kettenförderer und Power-and-Free-Systeme dominieren historisch die Antriebsstrang-Montage. Sie lösen das Lastproblem, scheitern aber am Variantenmix: Fester Takt, ausgelegt auf die langsamste Variante, kostet bei einer 6-Varianten-Linie 15–25 % Kapazität. Jede neue Variante erfordert mechanischen Umbau der Haltepositionen."),
        block("Schwerlast-AGV erreichen theoretisch 1.500 kg, liefern aber in ölbelasteter Umgebung mit Bodensensorik Probleme — Schmutz auf dem Boden beeinträchtigt Navigation und Positionierung. ±5–10 mm Positioniergenauigkeit reicht für robotergestützte Schrauberführung bei Differenzial-Zahnradpaarungen nicht aus."),
    ],
    "requirements": [
        req("Nutzlast", "200–1.500 kg", "Achsen bis E-Achs-Module auf gemeinsamer Linie"),
        req("Positioniergenauigkeit", "±0,5 mm", "an Verschraubungsstationen für robotergestützte Anziehdrehmomente"),
        req("Variantenflexibilität", "4–8 Varianten", "Stationsreihenfolge und Taktzeit variieren je Variante"),
        req("Umgebung", "Öl- und fettbeständig", "dauerhafter Schmiermitteleintrag in Getriebe- und Achsmontage"),
        req("Verfügbarkeit", ">99,5 %", "3-Schicht-Betrieb, hohe Jahresstückzahlen"),
        req("Takt", "variabel je Variante", "kein Systemtakt an langsamster Variante ausrichten"),
    ],
    "alternatives": [
        block("Kettenförderer: Bewährt für hohe Lasten, aber fester Systemtakt und mechanischer Umbau bei neuen Varianten. Wirtschaftlich nur bei 1–2 Produkten ohne Variantenmix."),
        block("Schwerlast-AGV: Flexible Routenführung, aber ±5–10 mm Positionierung unzureichend für robotergeführte Verschraubung. Bodensensorik anfällig in öl- und spanbelasteter Umgebung."),
        block("Rollenbahn mit Hubindexierung: Präzise Positionierung (±0,1 mm), aber 15–25 s Overhead pro Station durch Andocken. Variantenumrüstung erfordert mechanische Anpassung der Hubeinheiten."),
    ],
    "solutionRouting": [
        block("Für Achsen und Getriebe bis 600 kg empfiehlt KRUPS die XL-Serie: 600 mm Bahnbreite, bis 600 kg Standard (1.000 kg mit Drehmodulen), bewährt in öl- und fettbelasteter Getriebemontage. Variantenprofile werden softwareseitig zugewiesen — kein mechanischer Umbau bei neuen Antriebsstrang-Varianten."),
        block("Für E-Achsen und schwere Sonderausführungen ab 800 kg und für Anwendungen mit Werkstückstromversorgung (Funktionsprüfung während Transport) ist das eCart-System die erste Wahl. Beide Systeme lassen sich in derselben Fabrikhalle betreiben — eCart für die schwere End-of-Line-Prüfung, XL-Serie für die vorangehende Montagestrecke."),
    ],
    "recommendedProducts": [ref(XL_SERIE_ID), ref(ECART_ID)],
    "faq": [
        faq("Wie präzise positioniert ein schienengeführtes System bei der Verschraubung von Zahnradpaarungen und Differentialen?", "Das eCart positioniert auf ±0,6 mm an jeder Station — ohne separaten Hubindexierungsschritt. Für die robotergestützte Verschraubung mit definierten Anziehdrehmomenten ist diese Genauigkeit ausreichend. Die XL-Serie erreicht ±0,1 mm mit Absteckern."),
        faq("Kann eine Linie gleichzeitig Vorderachsen, Hinterachsen, Getriebe und E-Achsen fertigen?", "Ja. Jeder Carrier wird bei der Werkstückaufnahme einem Variantenprofil zugewiesen, das Stationsfolge, Taktzeiten und Geschwindigkeitsprofile steuert. Ein Carrier mit Hinterachse Standard überspringt automatisch Stationen, die nur für E-Achsen relevant sind."),
        faq("Wie verhält sich das System bei dauerhafter Öl- und Fettbelastung?", "Das schienengeführte System hat keine Bodensensorik, die in ölbelasteter Umgebung verschmutzen kann. Die Schiene ist mechanisch robust. Die XL-Serie ist spezifisch für Getriebe- und Antriebsstrangumgebungen mit dauerhaftem Schmiermitteleintrag ausgelegt."),
        faq("Was passiert bei einem Carrier-Ausfall — steht die ganze Antriebsstranglinie still?", "Nein. Ein defekter Carrier wird an einer Ausschleusposition entfernt, die übrigen Carrier fahren weiter. Die Systemverfügbarkeit bleibt >99,5 % auch bei einzelnen Ausfällen. Im Unterschied dazu stoppt ein Kettenförderer-Ausfall die gesamte Linie."),
        faq("Wann ist ein Kettenförderer die bessere Wahl als ein schienengeführtes System?", "Wenn die Linie ein einzelnes Produkt in hohem Volumen ohne Variantenmix fertigt und die Nutzlast deutlich über 2.000 kg liegt. Für den OEM-typischen 4–8-Varianten-Mix ist der Kettenförderer strukturell im Nachteil."),
    ],
    "cta": {
        "headline": "Antriebsstrang-Projekt anfragen",
        "description": "Achs- oder Getriebegewicht, Variantenanzahl, Stationslayout — wir zeigen, welche LOGO!MAT-Plattform zur Aufgabe passt.",
        "buttonLabel": "Jetzt anfragen",
        "buttonUrl": "/kontakt",
    },
}

# ---------------------------------------------------------------------------
# 3. Prüf- und Testautomation
# ---------------------------------------------------------------------------

PRUEF = {
    "_type": "industry",
    "_id": str(uuid.uuid4()),
    "language": "de",
    "name": "Prüf- und Testautomation",
    "slug": {"_type": "slug", "current": "pruef-testautomation"},
    "tagline": "Welche Anforderungen End-of-Line-Prüflinien an ein Transportsystem stellen, wie gängige Ansätze gegen elektrische Werkstückversorgung und Taktzeit-Effizienz abschneiden und welche KRUPS-Lösung passt.",
    "metaTitle": "Fördersystem Prüf- und Testautomation — Anforderungen und Systemvergleich",
    "metaDescription": "EOL-Prüflinien: 50–800 kg Prüflinge, 15–25 s Andock-Overhead konventionell, 10–20 Prüfstationen, <1 h Umrüstzeit. Systemvergleich und KRUPS-Lösung für Prüf- und Testautomation.",
    "characterBar": [
        char("Typische Prüflinge", "50–800 kg"),
        char("Konventioneller Andock-Overhead / Station", "15–25 s"),
        char("Prüfstationen pro Linie", "10–20"),
        char("Umrüstzeit für neue Prüfvarianten", "≤ 1 h"),
    ],
    "whatMoves": [
        block("Prüf- und Testlinien transportieren eine breite Gewichtsklasse: Elektromotoren und Getriebeeinheiten (50–400 kg), Batteriepacks und Antriebsmodule (300–800 kg), Steuergeräte und Sensorik (1–50 kg). Der Prüfling muss an jeder Station exakt positioniert sein — nicht weil der Transport schwierig wäre, sondern weil jede Messungenauigkeit direkt die Prüfaussage verfälscht."),
        block("Typische EOL-Prüflinien umfassen 10–20 Stationen: Sichtprüfung, Funktionsprüfung, Isolationsmessung, Drehmomentmessung, thermische Prüfung, Kommunikationstests. An jeder Station braucht der Prüfling elektrische Versorgung — nicht nur an Steckplätzen, sondern idealerweise durchgängig, damit Vorwärmung, Vorkonditionierung und Protokollierung bereits während des Transports laufen."),
    ],
    "bottleneck": [
        block("Prüflinien haben ein doppeltes Transportproblem: Das Werkstück muss nicht nur präzise an die Station — es muss dort exakt positioniert sein und elektrisch verbunden werden, damit Tests ablaufen. Konventionelle Lösungen arbeiten mit Stau-Rollenbahnen plus separater Kontaktierung an jeder Station: Andocken, Steckerverbindung herstellen, Test, Trennen, Weiterfahren. Dieser Overhead beträgt 15–25 s pro Station — bei 15 Stationen und 300.000 Prüflingen pro Jahr sind das über 2.000 Stunden verlorene Kapazität."),
        block("Hinzu kommt die Varianten-Herausforderung: Neue Prüfvarianten (neues Steuergerät, neue Motorgeneration) erfordern bei konventionellen Systemen mechanische Anpassungen an Halte- und Kontaktiereinheiten. Das kostet Wochen, nicht Stunden."),
    ],
    "requirements": [
        req("Nutzlast", "50–800 kg", "breite Prüflingklasse auf gemeinsamer Linie"),
        req("Positioniergenauigkeit", "±0,5–1 mm", "an Mess- und Prüfstationen für reproduzierbare Prüfergebnisse"),
        req("Werkstückversorgung", "24–48 V DC durchgängig", "EOL-Test, Vorkonditionierung und Protokollierung während Transport"),
        req("Umrüstzeit", "< 1 h", "neue Prüfvariante durch Parametrierung, kein mechanischer Umbau"),
        req("Verfügbarkeit", ">99,5 %", "keine mechanischen Kontaktiereinheiten als Störungsquelle"),
        req("Taktzeit-Effizienz", "< 5 s Positionierung", "kein Andock-/Trennaufwand pro Station"),
    ],
    "alternatives": [
        block("Stau-Rollenbahn mit separater Kontaktierung: Bewährt, aber 15–25 s Overhead pro Station durch Andocken und Steckerverbindung. Bei 15 Stationen und hohem Volumen ist das der größte Kapazitätskiller."),
        block("Handhabungsroboter zwischen Stationen: Hohe Flexibilität, aber Takt durch Roboter-Zykluszeit begrenzt. Wartungsintensiv, hohe Investition pro Station."),
        block("Manuelle Prüfinseln: Flexibel, aber Produktivitätsdeckel durch manuelle Transportzeit und fehlende Parallelisierung. Für >5.000 Prüflinge/Monat wirtschaftlich unterlegen."),
    ],
    "solutionRouting": [
        block("Für die Prüf- und Testautomation empfiehlt KRUPS das LOGO!MAT eCart-System. Die durchgängige Schienenversorgung mit 24–48 V DC eliminiert den Andock-Overhead vollständig — der Prüfling ist elektrisch verbunden, solange er auf dem Carrier ist. Positionierung auf ±0,6 mm ohne mechanische Kontaktiereinheiten."),
        block("Für leichte Prüflinge unter 250 kg und Linien, bei denen keine Werkstückstromversorgung erforderlich ist, ist die L-Serie oder T-Serie eine wirtschaftlichere Alternative mit gleicher Positioniergenauigkeit."),
    ],
    "recommendedProducts": [ref(ECART_ID), ref(L_SERIE_ID)],
    "faq": [
        faq("Wie stellt das eCart die Stromversorgung für elektrische Prüfungen während des Transports bereit?", "Die Schieneninfrastruktur versorgt jeden Carrier mit 24–48 V DC — durchgängig auf der gesamten Strecke, nicht nur an Prüfstationen. Das ermöglicht elektrische Vorkonditionierung, Vorwärmung und Funktionsprotokollierung bereits während der Fahrt zur Prüfstation."),
        faq("Was ist der Unterschied zwischen einem schienengeführten System und einer Stau-Rollenbahn mit separater Kontaktierung?", "Stau-Rollenbahnen erfordern pro Station 15–25 s Overhead (Andocken, Steckerverbindung, Trennen). Das schienengeführte System positioniert auf ±0,6 mm in <5 s ohne Steckerverbindung. Bei einer 15-Stationen-Linie und 300.000 Prüflingen/Jahr ergibt das über 2.000 h zurückgewonnene Kapazität."),
        faq("Wie schnell kann die Stationsreihenfolge bei neuen Prüfvarianten angepasst werden?", "Änderungen an Stationsreihenfolge, Prüfparametern und Geschwindigkeitsprofilen sind reine Software-Konfiguration — in <1 h parametriert. Wenn physische Haltepositionen verschoben werden müssen, ist mechanische Arbeit erforderlich, typisch 1–2 Tage."),
        faq("Wie hoch ist die Verfügbarkeit einer eCart-Prüflinie im Vergleich zu konventionellen Systemen?", ">99,5 % Systemverfügbarkeit im 24/7-Betrieb. Primärer Grund: keine mechanischen Kontaktiereinheiten — diese sind bei konventionellen Systemen die häufigste Störungsquelle. Wartungsintervall 10.000 Betriebsstunden."),
        faq("Für welche Prüfgewichte ist das System geeignet?", "Das eCart deckt Prüflinge von 50 kg bis 2.000 kg ab. Für typische Prüflinge in der Antriebstechnik (200–800 kg) sind eCart 600 oder eCart 700 die passenden Varianten. Leichte Elektronik-Prüflinge unter 250 kg laufen wirtschaftlicher auf der L-Serie oder T-Serie."),
    ],
    "cta": {
        "headline": "Prüflinie anfragen",
        "description": "Prüflinggewicht, Stationsanzahl, Takt und Versorgungsbedarf — wir zeigen, was in Ihrer EOL-Linie möglich ist.",
        "buttonLabel": "Jetzt anfragen",
        "buttonUrl": "/kontakt",
    },
}

# ---------------------------------------------------------------------------
# 4. Nutzfahrzeuge
# ---------------------------------------------------------------------------

NUTZFAHR = {
    "_type": "industry",
    "_id": str(uuid.uuid4()),
    "language": "de",
    "name": "Nutzfahrzeuge",
    "slug": {"_type": "slug", "current": "nutzfahrzeuge"},
    "tagline": "Welche Anforderungen Rahmen- und Kabinenmontage in der Nutzfahrzeugfertigung an ein Transportsystem stellen, wie gängige Ansätze mit Überlängen und Variantenmix umgehen und welche KRUPS-Lösung passt.",
    "metaTitle": "Fördersystem Nutzfahrzeug-Montage — Anforderungen und Systemvergleich",
    "metaDescription": "Nutzfahrzeug-Rahmenmontage: 800–2.000 kg, bis 8 m Werkstücklänge, 50–200 Grundkonfigurationen, 3–8 min variabler Stationstakt. Systemvergleich und KRUPS eCart-Lösung.",
    "characterBar": [
        char("Rahmen und Kabinen", "800–2.000 kg"),
        char("Werkstücklänge", "bis 8 m"),
        char("Grundkonfigurationen auf einer Linie", "50–200"),
        char("Stationstakt variiert je Variante", "3–8 min"),
    ],
    "whatMoves": [
        block("Die Nutzfahrzeugmontage transportiert Lkw-Rahmen (800–2.000 kg, 6–8 m Länge), Buskarosserien, Spezialfahrzeug-Chassis und Kabinen-Rohbauten. Die Werkstücklänge ist die erste Herausforderung: Standardsysteme sind für Pkw-Dimensionen (1,5–2,5 m) ausgelegt — Lkw-Rahmen von 6–8 m sprengen diese Klasse."),
        block("Die zweite Herausforderung ist die Variantentiefe. Ein Lkw-Hersteller fertigt nicht drei Modelle — er fertigt 50–200 Grundkonfigurationen: verschiedene Radstände, Motorvarianten, Aufbauspezifikationen für Betonmischer, Kühlfahrzeuge, Kranträger. Jede Konfiguration hat andere Stationstakte. Ein Premium-Chassis mit 12-Gang-Automatik benötigt an Station 7 acht Minuten, der Basis-Rahmen drei Minuten."),
    ],
    "bottleneck": [
        block("Die Nutzfahrzeugmontage hat zwei Besonderheiten, die Standardsysteme überfordern: Werkstücklängen von 6–8 m und stark variable Stationstakte. Schleppkettenförderer und Power-and-Free-Systeme tragen das Gewicht, erzwingen aber einen festen Takt — ausgelegt auf die langsamste Variante. Eine Basis-Kabine, die an Station 5 nur drei Minuten braucht, wartet dann acht Minuten, weil das Premium-Chassis an Station 4 noch nicht fertig ist."),
        block("Dieses Takt-Synchronisationsproblem kostet bei 50–200 Variantenkonfigurationen 20–35 % Kapazität. Gleichzeitig macht die Werkstücklänge AGV-Systeme unpraktisch: Ein 8-m-Rahmen braucht ein Spezialfahrzeug, das in engen Hallenlayouts kaum manövrierbar ist."),
    ],
    "requirements": [
        req("Nutzlast", "800–2.000 kg", "Lkw-Rahmen und Kabinen inkl. Vorrichtung"),
        req("Werkstücklänge", "bis 8 m", "Tandem-Carrier-Konfiguration erforderlich"),
        req("Variantenflexibilität", "50–200 Konfigurationen", "individuelle Stationstakte je Variante, kein Systemtakt"),
        req("Stationstakt", "3–8 min variabel", "Carrier fahren unabhängig, kein Warten auf langsamste Variante"),
        req("Sicherheit", "PLd nach EN ISO 13849", "Werker-Arbeitsplatz direkt am Rahmen während Transport"),
        req("Verfügbarkeit", ">99 %", "3-Schicht-Betrieb, hohe Jahresstückzahlen"),
    ],
    "alternatives": [
        block("Schleppkettenförderer: Bewährt für schwere Lasten und große Längen, aber fester Systemtakt. Bei 50–200 Variantenkonfigurationen kostet der Takt-Ausgleich 20–35 % Kapazität. Varianten-Umrüstung erfordert mechanischen Umbau."),
        block("Power-and-Free: Flexibler als Schleppkette, aber komplex, wartungsintensiv und für Überlängen schwierig zu konfigurieren. Stationstakt-Entkopplung ist begrenzt."),
        block("Schwerlast-AGV: Theoretisch flexible Routenführung, aber 8-m-Spezialfahrzeuge sind in engen Layouts unpraktisch. ±10 mm Positionierung unzureichend für präzise Anbauteile."),
    ],
    "solutionRouting": [
        block("Für Nutzfahrzeugrahmen empfiehlt KRUPS das LOGO!MAT eCart-System in Tandem-Konfiguration: Zwei Standard-Carrier fahren synchron und tragen gemeinsam den langen Rahmen. Die Steuerung synchronisiert beide Carrier auf exakten Abstand — kein Spezialgehänge, kein Sonderrahmen erforderlich."),
        block("Jeder Carrier fährt unabhängig: Ein Premium-Fahrgestell, das an Station 7 acht Minuten benötigt, steht acht Minuten — der Basis-Rahmen an Station 8 fährt nach drei Minuten weiter, ohne zu warten. Variantenumstellung ist automatisch, 0 s Rüstzeit. Performance Level d nach EN ISO 13849 für sichere Werker-Arbeit am Bauteil."),
    ],
    "recommendedProducts": [ref(ECART_ID)],
    "faq": [
        faq("Wie transportiert das eCart Lkw- und Busrahmen von 6–8 m Länge?", "Über Tandem-Konfiguration: Zwei Standard-Carrier fahren synchron und tragen gemeinsam den langen Rahmen. Die Steuerung synchronisiert beide Carrier und hält exakten Abstand. Kein Spezialgehänge, kein Sonderrahmen."),
        faq("Wie geht das System mit dem variablen Takt bei unterschiedlichen Fahrzeugvarianten um?", "Jeder Carrier fährt unabhängig. Ein Premium-Fahrgestell, das an Station 7 acht Minuten benötigt, steht acht Minuten — der Basis-Rahmen an Station 8 fährt nach drei Minuten weiter, ohne zu warten. Kein Systemtakt, der alle auf die langsamste Variante zwingt."),
        faq("Wie schnell kann auf einen anderen Rahmentyp umgestellt werden?", "Die Umstellung ist vollautomatisch — 0 s Rüstzeit. Wenn Carrier 14 einen Busrahmen aufnimmt, aktiviert die Steuerung automatisch das Tandem mit Carrier 15, passt Taktzeiten an allen Stationen an und ändert das Fahrprofil."),
        faq("Wie sicher ist das System bei direkter Werker-Arbeit am Bauteil?", "Performance Level d nach EN ISO 13849. Carrier bremsen Bewegungsenergie aktiv über Sicherheitsstoßleisten ab. Schleppkettenförderer begrenzen nur die Antriebskraft, nehmen die kinetische Energie beim Aufprall aber nicht aktiv auf."),
        faq("Wann ist ein Schleppkettenförderer die bessere Wahl als ein schienengeführtes System?", "Wenn ein einzelner Produkttyp in hohem Volumen ohne Variantenmix gefertigt wird und die maximale Nutzlast über 2.000 kg liegt. Für den Nutzfahrzeug-typischen Mix aus 50–200 Grundkonfigurationen mit variablen Stationstakten ist der Schleppkettenförderer strukturell unterlegen."),
    ],
    "cta": {
        "headline": "Rahmenmontage anfragen",
        "description": "Rahmengewicht, Länge, Variantenmix, Stationstakte — wir legen die Tandem-Konfiguration für Ihren Grundriss aus.",
        "buttonLabel": "Jetzt anfragen",
        "buttonUrl": "/kontakt",
    },
}

# ---------------------------------------------------------------------------
# 5. Schwermontage und Maschinenbau
# ---------------------------------------------------------------------------

SCHWER = {
    "_type": "industry",
    "_id": str(uuid.uuid4()),
    "language": "de",
    "name": "Schwermontage und Maschinenbau",
    "slug": {"_type": "slug", "current": "schwermontage"},
    "tagline": "Welche Anforderungen Schwermontage und Maschinenbau mit hoher Variantenvielfalt und mittleren Stückzahlen an ein Transportsystem stellen, wie gängige Ansätze abschneiden und welche KRUPS-Lösung zum Produktspektrum passt.",
    "metaTitle": "Fördersystem Schwermontage und Maschinenbau — Anforderungen und Systemvergleich",
    "metaDescription": "Schwermontage und Maschinenbau: 50–2.000 kg, 20–80 Produktvarianten, 5–30 Einheiten/Schicht, 10–15 Stationen auf 60–80 m. Systemvergleich und KRUPS-Lösung.",
    "characterBar": [
        char("Produktgewichtsspektrum", "50–2.000 kg"),
        char("Stationen auf 60–80 m typisch", "10–15"),
        char("Mittlere Stückzahlen, hohe Varianz", "5–30 / Schicht"),
        char("Produktvarianten auf gemeinsamer Linie", "20–80"),
    ],
    "whatMoves": [
        block("Schwermontage und Maschinenbau umfassen Hochdruckreiniger, Kompressoren, Pumpen, Industrieroboter, Landmaschinen-Komponenten und Großgeräte. Das Produktgewicht variiert von 50 kg (kleine Pumpen, Elektromotoren) bis 2.000 kg (schwere Kompressoren, Industriegetriebe). Gemeinsam ist allen: viele Varianten, mittlere Stückzahlen, hoher Manuell-Anteil."),
        block("Eine typische Linie fertigt 20–80 Produktvarianten: verschiedene Leistungsklassen, Kundenkonfigurationen, Exportvarianten. Die Stückzahl pro Schicht liegt bei 5–30 Einheiten — zu viel für Inselmontage, zu wenig für hochautomatisierte Fließfertigung. Der Transport zwischen 10–15 Stationen auf 60–80 m Linienlänge bindet überraschend viel Kapazität, wenn er manuell oder mit Flurförderzeug erfolgt."),
    ],
    "bottleneck": [
        block("Schwermontage-Betriebe arbeiten häufig mit Inselmontage oder manuellem Stapler-Transport zwischen Arbeitsstationen. Das kostet: 5–10 min Transportzeit pro Station, Positionieraufwand durch Werker, hoher Kranaufwand bei Gewichten über 500 kg. Die Kapazitätsspanne liegt beim Transport, nicht bei der eigentlichen Montagearbeit."),
        block("Konventionelle Fördersysteme (Kettenförderer, Rollenbahnen) sind auf engen Produktspektren ausgelegt. Bei 20–80 Varianten mit unterschiedlichen Gewichten, Abmessungen und Montagestackzeiten scheitern sie entweder am Taktproblem (alle auf die langsamste Variante ausgelegt) oder erfordern ständige mechanische Umrüstung."),
    ],
    "requirements": [
        req("Nutzlast", "50–2.000 kg", "breites Produktspektrum auf gemeinsamer Linie"),
        req("Variantenflexibilität", "20–80 Varianten", "individuelle Stationstakte, kein Systemtakt"),
        req("Stückzahl", "5–30 / Schicht", "zu viel für Inselmontage, zu wenig für Vollautomatisierung"),
        req("Linienlänge", "60–80 m typisch", "10–15 Stationen, mehrere Produktionsbereiche"),
        req("Erweiterbarkeit", "ohne Betriebsunterbrechung", "neue Stationen durch Softwareparametrierung"),
        req("Wartungsaufwand", "minimal", "Maschinenbau-Betriebe haben keine dedizierte Förderanlagen-Instandhaltung"),
    ],
    "alternatives": [
        block("Inselmontage mit manuellem Transport: Flexibel für Kleinstserien, aber 5–10 min Transportaufwand pro Station und Kranabhängigkeit bei Schwerlast. Ab 10 Einheiten/Schicht wirtschaftlich unterlegen."),
        block("Kettenförderer: Robust für hohe Lasten, aber fester Takt und mechanische Umbauaufwände bei neuen Varianten. Für 20–80-Varianten-Mix ungeeignet."),
        block("Klassische Rollenbahn: Präzise für einheitliche Produkte. Bei unterschiedlichen Gewichten (50–2.000 kg) und Abmessungen auf einer Linie technisch und wirtschaftlich problematisch."),
    ],
    "solutionRouting": [
        block("Für Schwermontage und Maschinenbau mit breitem Variantenmix empfiehlt KRUPS das LOGO!MAT eCart-System. Carrier fahren unabhängig — ein 150-kg-Hochdruckreiniger und ein 600-kg-Kompressor laufen auf gleicher Strecke, jeder Carrier auf seinem eigenen Profil. Neue Produktvarianten werden durch Softwareparametrierung eingeführt, kein mechanischer Umbau."),
        block("Für Betriebe mit Produktgewichten ausschließlich unter 600 kg ist die XL-Serie eine wirtschaftlichere Alternative bei gleicher Variantenflexibilität. Wartungsintervall 10.000 Betriebsstunden — bei 2-Schicht-Betrieb 2–3 Jahre zwischen Wartungszyklen."),
    ],
    "recommendedProducts": [ref(ECART_ID), ref(XL_SERIE_ID)],
    "faq": [
        faq("Ab welcher Stückzahl lohnt sich der Umstieg von Inselmontage auf eine schienengeführte Montagelinie?", "Als Faustformel: ab ca. 10–15 Einheiten pro Schicht beginnt der Produktivitätsvorteil die Investition zu rechtfertigen. Bei weniger als 3 Einheiten pro Tag ist manueller Transport wirtschaftlicher. Der Break-even liegt abhängig von Produkt und Stationszahl typisch bei 2–4 Jahren."),
        faq("Kann eine Linie Produkte mit unterschiedlichem Gewicht gleichzeitig transportieren?", "Ja. Auf der eCart-Linie können unterschiedliche Carrier-Typen gemischt eingesetzt werden — ein 150-kg-Hochdruckreiniger und ein 600-kg-Kompressor laufen auf gleicher Strecke, jeder Carrier auf seinen eigenen Parametern."),
        faq("Wie lange läuft das System ohne planmäßige Wartung?", "Das Wartungsintervall beträgt 10.000 Betriebsstunden — bei 2-Schicht-Betrieb 2–3 Jahre zwischen Wartungszyklen. Kettenförderer benötigen Wartung alle 500–2.000 h (Kettenspannung, Schmierung, Verschleiß)."),
        faq("Kann die Linie nachträglich erweitert werden, ohne den Betrieb zu unterbrechen?", "Ja. Neue Stationen werden durch Hinzufügen von Stoppeinheiten auf der bestehenden Schienenstrecke integriert, die Halteposition wird programmiert, das Carrier-Profil wird angepasst. Linienerweiterungen dauern typisch 1–3 Tage und lassen sich auf Wochenenden legen."),
        faq("Wann ist eine klassische Rollenbahn die bessere Wahl als eCart?", "Wenn die Produkte einheitlich sind, die Losgrößen hoch und der Takt für alle Varianten gleich ist. Für den Maschinenbau-typischen Mix aus 20–80 Varianten mit individuellem Stationstakt ist die Rollenbahn strukturell unterlegen."),
    ],
    "cta": {
        "headline": "Schwermontage-Projekt anfragen",
        "description": "Produktgewicht, Variantenanzahl, Stationslayout — wir legen aus, was auf 60–80 m Linienlänge möglich ist.",
        "buttonLabel": "Jetzt anfragen",
        "buttonUrl": "/kontakt",
    },
}

# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------

INDUSTRIES = [BATTERIE, ANTRIEB, PRUEF, NUTZFAHR, SCHWER]


def main():
    dry_run = "--dry-run" in sys.argv
    token = os.environ.get("SANITY_WRITE_TOKEN")
    if not token:
        print("Error: SANITY_WRITE_TOKEN not set.")
        sys.exit(1)

    mutations = [{"createOrReplace": ind} for ind in INDUSTRIES]

    url = f"{BASE_URL}/mutate/{DATASET}"
    if dry_run:
        url += "?dryRun=true"
        print("DRY RUN — no changes will be written\n")

    print(f"Sending {len(mutations)} industry documents to Sanity ({DATASET})...")
    for ind in INDUSTRIES:
        print(f"  {ind['name']} — /{ind['slug']['current']}")
    print()

    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"mutations": mutations},
        timeout=30,
    )

    if resp.ok:
        result = resp.json()
        print("Success!")
        if dry_run:
            print("Dry run passed — re-run without --dry-run to apply.")
        else:
            print(f"Transaction ID: {result.get('transactionId', 'n/a')}")
            print(f"Results: {len(result.get('results', []))} documents created")
    else:
        print(f"Error {resp.status_code}:")
        print(resp.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
