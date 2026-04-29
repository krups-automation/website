#!/usr/bin/env python3
"""
Sanity content import — 7 service documents (1 Plan + 6 Run tier).

Usage:
  SANITY_WRITE_TOKEN=sk... python3 scripts/import-services.py [--dry-run]
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


def h2(text):
    return {
        "_type": "block",
        "_key": key(),
        "style": "h2",
        "children": [{"_type": "span", "_key": key(), "text": text, "marks": []}],
        "markDefs": [],
    }


def step(num, title, description):
    return {"_key": key(), "stepNumber": num, "title": title, "description": description}


def faq(question, answer):
    return {"_key": key(), "question": question, "answer": answer}


# ---------------------------------------------------------------------------
# Service definitions
# ---------------------------------------------------------------------------

SERVICES = [

    # -----------------------------------------------------------------------
    # 1. Planung — Plan tier
    # -----------------------------------------------------------------------
    {
        "_type": "service",
        "_id": str(uuid.uuid4()),
        "language": "de",
        "tier": "plan",
        "name": "Produktionsplanung",
        "slug": {"_type": "slug", "current": "planung"},
        "metaTitle": "Produktionsplanung — KRUPS Automation",
        "metaDescription": (
            "KRUPS plant Ihre Montagelinie: Layout, Taktzeitberechnung und Systemauslegung "
            "vor dem ersten Auftrag. Typisch 2–4 Wochen bis zur unterschriftsreifen Angebotsbasis."
        ),
        "summary": (
            "Bevor eine Schraube gedreht wird, rechnen wir die Linie durch. "
            "KRUPS übernimmt Layout, Taktzeitberechnung und Systemdimensionierung — "
            "so erhalten Sie eine belastbare Investitionsbasis, keine Schätzung."
        ),
        "processSteps": [
            step(1, "Anforderungsaufnahme", "Bauteilgewichte, Taktzeiten, Stationsanzahl, Schnittstellen, Umgebungsbedingungen — wir erfassen alles, was die Linie definiert."),
            step(2, "Layoutentwurf", "Wir entwickeln einen oder mehrere Grundriss-Vorschläge auf Basis Ihrer Hallenpläne. Engstellen, Zugänge und Materialfluss werden berücksichtigt."),
            step(3, "Taktzeitberechnung", "Rechnerische Ermittlung der erreichbaren Taktzeiten auf Basis der Streckengeometrie, Geschwindigkeiten und Stationszeiten."),
            step(4, "Systemauslegung", "Auswahl der geeigneten LOGO!MAT-Plattform (L/XL/T-Serie oder eCart), Dimensionierung von Antrieben, Stoppern und Peripherie."),
            step(5, "Angebotsbasis", "Strukturierte Systemspezifikation als Grundlage für ein verbindliches Angebot — kein Raum für Nachtragsrisiken."),
        ],
        "deliverables": [
            "Maßstäblicher 2D-Grundriss (PDF + DXF)",
            "Taktzeitberechnung mit Parametern und Annahmen",
            "Systemspezifikation: Plattform, Bahnbreite, Komponentenliste",
            "Investitionsrahmen als Angebotsbasis",
        ],
        "body": [
            block(
                "Die Planungsleistung ist keine Beraterstunde — sie ist der technische Kern "
                "unseres Angebotsprozesses. Wir entwickeln das Förderkonzept gemeinsam mit Ihrem "
                "Planungsteam, bevor Kosten verbindlich werden. Typische Planungsdauer: 2–4 Wochen "
                "ab vollständiger Anforderungsdokumentation."
            ),
            block(
                "Eingaben, die wir benötigen: Hallengrundriss (DXF oder PDF), Bauteilspezifikation "
                "(Gewicht, Abmessungen, Stückzahl/Jahr), Stationsanzahl und grobe Prozesszeiten. "
                "Alles andere entwickeln wir mit Ihnen."
            ),
        ],
        "faq": [
            faq(
                "Was kostet die Planungsleistung?",
                "Die Planung ist Teil unseres Angebotsprozesses und wird bei Auftragserteilung mit dem Auftragswert verrechnet. Sprechen Sie uns an — wir klären den Umfang vorab."
            ),
            faq(
                "Welche Unterlagen brauchen Sie von uns?",
                "Mindestens: Hallengrundriss, Bauteilgewicht und -abmessungen, angestrebte Taktzeit oder Jahresstückzahl, Stationsanzahl (grob). Je vollständiger die Eingaben, desto belastbarer das Ergebnis."
            ),
            faq(
                "Wie lange dauert die Planung?",
                "Typisch 2–4 Wochen ab vollständiger Anforderungsdokumentation. Für eilige Projekte sprechen Sie uns direkt an."
            ),
            faq(
                "Planen Sie auch für Bestandshallen mit wenig Platz?",
                "Ja. Wir arbeiten regelmäßig mit beengten Grundrissen, Säulenfeldern und bestehenden Anlagen. Die L-Serie und T-Serie lassen sich auch in engen Layouts führen."
            ),
        ],
    },

    # -----------------------------------------------------------------------
    # 2. Beratung — Run tier
    # -----------------------------------------------------------------------
    {
        "_type": "service",
        "_id": str(uuid.uuid4()),
        "language": "de",
        "tier": "run",
        "name": "Beratung",
        "slug": {"_type": "slug", "current": "beratung"},
        "metaTitle": "Beratung — KRUPS Automation",
        "metaDescription": (
            "Technische Beratung zu schienengeführten Fördersystemen: Machbarkeit, "
            "Systemauswahl und Grobkonzept — bevor Sie sich festlegen."
        ),
        "summary": (
            "Wir klären zuerst, ob ein LOGO!MAT-System die richtige Lösung für Ihre Aufgabe ist — "
            "und wenn ja, welche Plattform. Kein Verkaufsgespräch, sondern technische Bewertung "
            "durch Ingenieure mit Projekterfahrung."
        ),
        "processSteps": [
            step(1, "Erstgespräch", "Aufgabenstellung, Rahmenbedingungen, Zeitplan. Wir stellen die richtigen Fragen, um den Bedarf vollständig zu erfassen."),
            step(2, "Machbarkeitseinschätzung", "Technische Bewertung: Passt ein LOGO!MAT-System? Welche Plattform? Welche Einschränkungen gibt es?"),
            step(3, "Systemempfehlung", "Klare Empfehlung mit Begründung — inklusive Fällen, in denen ein anderes System besser geeignet wäre."),
            step(4, "Grobkonzept & nächste Schritte", "Schriftliche Zusammenfassung als Grundlage für eine Planungsbeauftragung oder ein Angebot."),
        ],
        "deliverables": [
            "Schriftliche Machbarkeitseinschätzung",
            "Systemempfehlung mit Begründung",
            "Grobe Investitionsschätzung (±30 %)",
            "Klare Empfehlung für nächste Schritte",
        ],
        "body": [
            block(
                "Unsere Beratung ist technisch, nicht verkaufsgetrieben. Wenn ein Kettenförderer "
                "oder ein AGV für Ihre Aufgabe besser geeignet ist als ein LOGO!MAT-System, sagen wir "
                "das — mit Begründung. Diese Ehrlichkeit ist die Basis für Projekte, die funktionieren."
            ),
            block(
                "Typische Beratungsgespräche dauern 60–90 Minuten. Das Ergebnis ist immer schriftlich "
                "dokumentiert, damit Ihre interne Entscheidung auf einer klaren Grundlage steht."
            ),
        ],
        "faq": [
            faq(
                "Für wen ist die Beratung geeignet?",
                "Für Planungsingenieure und Projektleiter, die eine neue Montagelinie konzipieren oder eine bestehende Lösung ersetzen wollen — und noch keine Systementscheidung getroffen haben."
            ),
            faq(
                "Beraten Sie auch zu Wettbewerbsprodukten?",
                "Wir erklären, wann LOGO!MAT-Systeme die bessere Wahl sind — und wann nicht. Wir empfehlen keine Wettbewerberprodukte, aber wir sagen klar, wenn ein anderes Systemkonzept besser passt."
            ),
            faq(
                "Wie läuft das Erstgespräch ab?",
                "Per Video-Call oder bei Ihnen vor Ort. Wir brauchen vorab: Aufgabenbeschreibung, grobe Bauteilspezifikation und einen Ansprechpartner mit technischem Hintergrund."
            ),
        ],
    },

    # -----------------------------------------------------------------------
    # 3. Projektierung — Run tier
    # -----------------------------------------------------------------------
    {
        "_type": "service",
        "_id": str(uuid.uuid4()),
        "language": "de",
        "tier": "run",
        "name": "Projektierung",
        "slug": {"_type": "slug", "current": "projektierung"},
        "metaTitle": "Projektierung — KRUPS Automation",
        "metaDescription": (
            "Detail-Engineering für LOGO!MAT-Fördersysteme: Layoutplanung, Elektroplanung, "
            "Stücklisten und CE-Dokumentation aus einer Hand."
        ),
        "summary": (
            "Aus dem Grundkonzept wird ein fertigungsreifes Projekt. KRUPS übernimmt die vollständige "
            "Detailplanung — Mechanik, Elektrik, Steuerungskonzept und CE-Dokumentation — "
            "bevor die Fertigung beginnt."
        ),
        "processSteps": [
            step(1, "Lastenheftanalyse", "Wir prüfen Ihr Lastenheft auf Vollständigkeit, Widersprüche und technische Machbarkeit. Offene Punkte werden vor der Detailplanung geklärt."),
            step(2, "Detaillayout", "Maßstäbliches 2D/3D-Layout mit allen Komponenten, Stationen, Zugängen und Schnittstellen zur Halleninfrastruktur."),
            step(3, "Stückliste & Komponentenspezifikation", "Vollständige Stückliste aller Baugruppen als Basis für Fertigung und Beschaffung."),
            step(4, "Elektroplanung", "Schaltschrankplanung, Verkabelungsschema, Schnittstellendefinition zu übergeordneten Systemen (SPS, MES, Sicherheitstechnik)."),
            step(5, "CE-Dokumentation", "Risikobeurteilung nach Maschinenrichtlinie, technische Unterlagen und Konformitätserklärung."),
        ],
        "deliverables": [
            "2D/3D-Detaillayout (PDF + DXF/STEP)",
            "Vollständige Stückliste",
            "Elektroplan (EPLAN oder äquivalent)",
            "Schnittstellendokumentation",
            "Risikobeurteilung & CE-Unterlagen",
        ],
        "body": [
            block(
                "Die Projektierung ist die aufwändigste Phase — und die wichtigste. "
                "Fehler in der Detailplanung sind in der Fertigung zehnmal teurer zu beheben "
                "als auf dem Zeichenbrett. Wir investieren diese Zeit bewusst, damit die Montage "
                "beim Kunden ohne Überraschungen verläuft."
            ),
            block(
                "Typische Projektierungsdauer: 4–8 Wochen, abhängig von Anlagenkomplexität "
                "und Vollständigkeit der Eingangsdaten. Alle Planungsunterlagen werden Ihnen "
                "digital übergeben und bleiben Ihr Eigentum."
            ),
        ],
        "faq": [
            faq(
                "Liefern Sie auch 3D-Modelle?",
                "Ja. Wir liefern STEP-Dateien für die Integration in Ihre Digitale Fabrik oder Ihr CAD-System."
            ),
            faq(
                "Arbeiten Sie mit unserem Lastenheft oder erstellen Sie ein eigenes?",
                "Beides ist möglich. Wenn kein Lastenheft vorliegt, entwickeln wir es gemeinsam auf Basis der Beratungsphase. Wenn ein Lastenheft vorliegt, prüfen wir es zuerst auf Machbarkeit und Vollständigkeit."
            ),
            faq(
                "Wer übernimmt die CE-Kennzeichnung?",
                "KRUPS als Hersteller der Anlage. Wir erstellen die vollständige CE-Dokumentation nach Maschinenrichtlinie 2006/42/EG und liefern die Konformitätserklärung mit der Anlage."
            ),
        ],
    },

    # -----------------------------------------------------------------------
    # 4. Fertigung — Run tier
    # -----------------------------------------------------------------------
    {
        "_type": "service",
        "_id": str(uuid.uuid4()),
        "language": "de",
        "tier": "run",
        "name": "Fertigung",
        "slug": {"_type": "slug", "current": "fertigung"},
        "metaTitle": "Fertigung — KRUPS Automation",
        "metaDescription": (
            "Eigenfertigung aller LOGO!MAT-Komponenten in Hilden: Zerspanung, Schweißen, "
            "Montage und Vorabnahme unter einem Dach. Keine Fremdvergabe an kritischen Baugruppen."
        ),
        "summary": (
            "KRUPS fertigt alle mechanischen Kernkomponenten selbst — in Hilden. "
            "Zerspanung, Schweißen, Montage und Vorabnahme unter einem Dach bedeutet: "
            "kürzere Reaktionszeiten, keine Schnittstellenverluste, volle Qualitätskontrolle."
        ),
        "processSteps": [
            step(1, "Materialbeschaffung & Arbeitsvorbereitung", "Projektspezifische Beschaffung aller Rohmaterialien und Kaufteile nach freigegebener Stückliste."),
            step(2, "Mechanische Fertigung", "Zerspanung, Blechbearbeitung und Schweißbaugruppen in der eigenen Fertigung in Hilden."),
            step(3, "Baugruppenmontage", "Mechanische Vormontage aller Baugruppen (Bahnabschnitte, Stopper, Weichen, Lifte) inklusive funktionaler Prüfung."),
            step(4, "Elektrischer Aufbau & Vorabnahme", "Schaltschrankaufbau, Verkabelung und Probelauf der vollständigen Anlage im Werk vor dem Versand."),
            step(5, "Versand & Dokumentation", "Fachgerechte Verpackung, Versandlogistik und Übergabe aller Fertigungsunterlagen."),
        ],
        "deliverables": [
            "Vollständige Anlage ab Werk, vorabgenommen",
            "Abnahmeprotokoll der Werksvorabnahme",
            "Fertigungsunterlagen & Prüfprotokolle",
            "Vollständige Ersatzteilliste",
        ],
        "body": [
            block(
                "Eigenfertigung ist keine Marketingaussage — sie ist die Grundlage unserer "
                "Liefertreue und Reaktionsgeschwindigkeit. Wenn eine Sonderkomponente gebraucht "
                "wird oder sich in der Montage etwas ändert, entscheiden wir im Haus, "
                "nicht über einen Lieferkanten-Ticketprozess."
            ),
            block(
                "Alle Rollen, Werkstückträger und mechanischen Kernbaugruppen werden bei KRUPS "
                "in Hilden gefertigt. Elektronik- und Antriebskomponenten beziehen wir von "
                "qualifizierten Partnern mit langjähriger Lieferbeziehung."
            ),
        ],
        "faq": [
            faq(
                "Können wir die Fertigung im Werk besichtigen?",
                "Ja. Wir empfehlen einen Werksbesuch — insbesondere zur Vorabnahme, bei der die vollständige Anlage in Betrieb gesetzt wird, bevor sie Hilden verlässt."
            ),
            faq(
                "Wie lange dauert die Fertigung?",
                "Typisch 8–16 Wochen nach abgeschlossener Projektierung, abhängig von Anlagengröße und Komponentenverfügbarkeit. Wir kommunizieren Liefertermine verbindlich nach Auftragsklärung."
            ),
            faq(
                "Fertigen Sie auch Einzelkomponenten für Bestandsanlagen?",
                "Ja. Ersatz- und Erweiterungskomponenten für bestehende LOGO!MAT-Systeme werden ebenfalls in Hilden gefertigt."
            ),
        ],
    },

    # -----------------------------------------------------------------------
    # 5. Montage — Run tier
    # -----------------------------------------------------------------------
    {
        "_type": "service",
        "_id": str(uuid.uuid4()),
        "language": "de",
        "tier": "run",
        "name": "Montage",
        "slug": {"_type": "slug", "current": "montage"},
        "metaTitle": "Montage & Inbetriebnahme — KRUPS Automation",
        "metaDescription": (
            "KRUPS-Techniker installieren und nehmen Ihre LOGO!MAT-Anlage direkt bei Ihnen vor Ort in Betrieb — "
            "inklusive Maschinenbediener-Schulung und Abnahmeprotokoll."
        ),
        "summary": (
            "Die Anlage kommt vorabgenommen aus Hilden. Unsere Monteure installieren sie bei Ihnen "
            "vor Ort, schließen alle Systeme an und nehmen die Linie gemeinsam mit Ihnen ab — "
            "bis alles im definierten Takt läuft."
        ),
        "processSteps": [
            step(1, "Baustellenplanung", "Montageplan, Krankapazitäten, Bodenbefestigungsplan und Zeitplan für die Unterbrechung laufender Produktion."),
            step(2, "Anlieferung & Aufstellung", "Koordinierte Anlieferung aller Baugruppen, Aufstellung und Ausrichtung nach Detailplan."),
            step(3, "Mechanische Montage", "Verbindung aller Bahnabschnitte, Montage von Stoppern, Weichen und Peripheriekomponenten."),
            step(4, "Elektrischer Anschluss", "Anschluss an Hausversorgung, Einbindung in die Sicherheitstechnik (Not-Halt, Schutzzäune) und Schnittstellen zur Kundensteuerung."),
            step(5, "Inbetriebnahme & Einfahren", "Parametrierung der Steuerung, Einfahren der Anlage, Optimierung der Taktzeiten auf den realen Produktionsprozess."),
            step(6, "Abnahme & Schulung", "Gemeinsame Abnahme nach vereinbarten Kriterien. Bedienerschulung für Maschinenbediener und Instandhaltung."),
        ],
        "deliverables": [
            "Vollständig installierte und abgenommene Anlage",
            "Abnahmeprotokoll mit Taktzeitmessung",
            "Betriebsanleitung & Wartungsplan",
            "Bedienerschulung (Bediener + Instandhaltung)",
        ],
        "body": [
            block(
                "Montage ist für uns nicht Aufstellung und Weiterfahren. Wir bleiben, bis die Linie "
                "im definierten Takt läuft — und die Mannschaft, die sie bedient, weiß was zu tun "
                "ist, wenn etwas nicht stimmt. Die Abnahme erfolgt nach schriftlich vereinbarten "
                "Kriterien, nicht nach Gutdünken."
            ),
            block(
                "Typische Montagezeiten: 1–3 Wochen vor Ort, abhängig von Anlagengröße. "
                "Für laufende Produktionsstätten planen wir Montagephasen in Abstimmung mit "
                "Ihrem Produktionsplan — Schicht- oder Wochenendmontagen sind möglich."
            ),
        ],
        "faq": [
            faq(
                "Wer stellt Kran und Hebemittel zur Verfügung?",
                "In der Regel der Kunde. Wir klären den Bedarf im Montageplan und geben Lastangaben rechtzeitig vor der Montage."
            ),
            faq(
                "Wie lange dauert die Schulung?",
                "Typisch ein halber Tag für Maschinenbediener, ein Tag für Instandhaltung. Umfang wird projektspezifisch vereinbart."
            ),
            faq(
                "Was passiert, wenn bei der Inbetriebnahme etwas nicht stimmt?",
                "Wir lösen es vor Ort. Unsere Monteure verlassen die Baustelle nicht, bevor die Abnahmekriterien erfüllt sind."
            ),
        ],
    },

    # -----------------------------------------------------------------------
    # 6. Steuerungsintegration — Run tier
    # -----------------------------------------------------------------------
    {
        "_type": "service",
        "_id": str(uuid.uuid4()),
        "language": "de",
        "tier": "run",
        "name": "Steuerungsintegration",
        "slug": {"_type": "slug", "current": "steuerungsintegration"},
        "metaTitle": "Steuerungsintegration — KRUPS Automation",
        "metaDescription": (
            "SPS-Programmierung und Schnittstellenintegration für LOGO!MAT-Systeme: "
            "Siemens TIA Portal, Profinet/Profibus, MES-Anbindung, Sicherheitstechnik nach PLe/SIL2."
        ),
        "summary": (
            "Das Fördersystem ist mechanisch fertig — jetzt muss es mit Ihrer Produktionswelt "
            "sprechen. KRUPS programmiert die Steuerung, definiert alle Schnittstellen und "
            "integriert das System in Ihre SPS-, MES- und Sicherheitsinfrastruktur."
        ),
        "processSteps": [
            step(1, "Schnittstellendefinition", "Gemeinsame Festlegung aller Schnittstellen: SPS-Protokoll, Signaldefinition, MES-Anbindung, Sicherheitskreise."),
            step(2, "SPS-Programmierung", "Programmentwicklung im Siemens TIA Portal (Standard). Andere Hersteller auf Anfrage."),
            step(3, "Visualisierung", "HMI-Oberfläche für Bediener und Instandhaltung: Anlagenstatus, Fehlerdiagnose, Parametrierung."),
            step(4, "Schnittstellentest (FAT)", "Fabrikabnahmetest im Werk: Alle Schnittstellen werden gegen den Kundensimulator oder reale Gegenstellen getestet."),
            step(5, "Integration & SAT vor Ort", "Integration in die reale Produktionsumgebung und Werksabnahmetest (SAT) direkt beim Kunden."),
        ],
        "deliverables": [
            "Lauffähiges SPS-Programm (Quellcode Kundenübergabe)",
            "HMI-Visualisierung",
            "Vollständige Schnittstellendokumentation",
            "FAT- und SAT-Protokolle",
            "Funktionale Sicherheitsdokumentation (PLe/SIL2)",
        ],
        "body": [
            block(
                "Unsere Steuerungslösungen sind für Siemens TIA Portal standardisiert — "
                "das ist die Realität in der Automobilindustrie. Auf Anfrage integrieren wir "
                "auch Beckhoff TwinCAT, Allen Bradley oder andere Plattformen, wenn Ihre "
                "Bestandsinfrastruktur das erfordert."
            ),
            block(
                "Sicherheitstechnik ist kein Anhang — sie ist Teil des Programms. Wir dimensionieren "
                "und dokumentieren alle sicherheitsrelevanten Funktionen nach PLe/SIL2 und liefern "
                "die Sicherheitsnachweise als Teil der CE-Dokumentation."
            ),
        ],
        "faq": [
            faq(
                "Welche SPS-Plattformen unterstützen Sie?",
                "Standard ist Siemens TIA Portal (S7-1200/1500). Auf Anfrage: Beckhoff TwinCAT, Allen Bradley. Für bestehende Simatic-Umgebungen bieten wir auch S7-300/400-Migrationen an."
            ),
            faq(
                "Können Sie unser bestehendes MES-System anbinden?",
                "Ja, sofern eine dokumentierte Schnittstelle (OPC-UA, MQTT, Profinet, REST-API) vorhanden ist. Wir implementieren auf Basis Ihrer Schnittstellenspezifikation."
            ),
            faq(
                "Erhalten wir den SPS-Quellcode?",
                "Ja. Der Quellcode wird vollständig übergeben — kein Passwortschutz, kein Vendor-Lock-in."
            ),
            faq(
                "Was ist PLe und warum ist es relevant?",
                "PLe ist die höchste Performancelevel-Kategorie nach EN ISO 13849. Für sicherheitsrelevante Förderfunktionen (Not-Halt, Personen im Gefahrenbereich) ist PLe oder SIL2 in der Automobilmontage Standard."
            ),
        ],
    },

    # -----------------------------------------------------------------------
    # 7. Service / After-Sales — Run tier
    # -----------------------------------------------------------------------
    {
        "_type": "service",
        "_id": str(uuid.uuid4()),
        "language": "de",
        "tier": "run",
        "name": "Service",
        "slug": {"_type": "slug", "current": "service"},
        "metaTitle": "Service & Instandhaltung — KRUPS Automation",
        "metaDescription": (
            "KRUPS-After-Sales: Ersatzteilversorgung ab Lager Hilden, telefonische Störungshotline, "
            "präventive Wartung und Retrofit für LOGO!MAT-Systeme jeder Baujahr-Generation."
        ),
        "summary": (
            "Eine LOGO!MAT-Anlage ist für Jahrzehnte ausgelegt. Wir stellen sicher, "
            "dass sie es auch bleibt: Ersatzteilversorgung, Wartung, Hotline und Retrofit "
            "aus einer Hand — auch für ältere Generationen."
        ),
        "processSteps": [
            step(1, "Ersatzteilversorgung", "Kritische Verschleißteile (Rollen, Riemen, Stopper) ab Lager in Hilden. Lieferzeit ab Lager: 1–3 Werktage für Deutschland."),
            step(2, "Telefonhotline", "Störungsunterstützung durch KRUPS-Techniker — direkt, ohne Ticket-Wartezeit. Erreichbar während Geschäftszeiten; auf Anfrage auch außerhalb."),
            step(3, "Präventive Wartung", "Regelmäßige Inspektion nach KRUPS-Wartungsplan: Verschleißprüfung, Schmierung, Justierung, Protokoll."),
            step(4, "Vor-Ort-Service", "Techniker-Einsatz bei Störungen, die sich nicht telefonisch lösen lassen — in der Regel innerhalb von 24–48 Stunden."),
            step(5, "Retrofit & Erweiterung", "Anpassung, Erweiterung oder Modernisierung bestehender LOGO!MAT-Anlagen — auch wenn die Anlage nicht von der aktuellen Generation ist."),
        ],
        "deliverables": [
            "Ersatzteil-Lieferung ab Lager Hilden",
            "Wartungsprotokoll mit Empfehlungen",
            "Störungsprotokoll & Ursachenanalyse",
            "Angebot Retrofit / Erweiterung auf Anfrage",
        ],
        "body": [
            block(
                "LOGO!MAT-Systeme laufen oft 15–25 Jahre. Wir kennen alle Generationen, "
                "weil wir sie gefertigt haben. Wenn Ihre Anlage aus den 90ern kommt, "
                "können wir trotzdem helfen — mit Ersatzteilen, Modernisierungspaketen "
                "oder einer vollständigen Steuerungsmigration."
            ),
            block(
                "Wartungsverträge mit definierten Reaktionszeiten sind auf Anfrage verfügbar. "
                "Sprechen Sie uns an — wir stellen ein Servicepaket zusammen, "
                "das zu Ihrer Produktionssituation und Instandhaltungsstrategie passt."
            ),
        ],
        "faq": [
            faq(
                "Warten Sie auch Anlagen, die nicht von KRUPS stammen?",
                "In der Regel nein — wir können nur für Systeme garantieren, die wir kennen. Für Fremdanlagen können wir eine Bestandsaufnahme anbieten und dann entscheiden."
            ),
            faq(
                "Wie lange sind Ersatzteile für ältere Generationen verfügbar?",
                "Wir bemühen uns, kritische Teile langfristig verfügbar zu halten. Für sehr alte Generationen sprechen Sie uns frühzeitig an — wir können oft Alternativen identifizieren oder Teile nachfertigen."
            ),
            faq(
                "Gibt es Wartungsverträge mit festen Reaktionszeiten?",
                "Ja, auf Anfrage. Wir passen die Konditionen an Ihre Betriebszeiten und Kritikalität der Linie an."
            ),
            faq(
                "Was ist bei einem Retrofit typischerweise inbegriffen?",
                "Typisch: Steuerungsaustausch (alte Simatic auf TIA Portal), Antriebstausch, Safety-Upgrade. Mechanik bleibt meist unverändert — das ist die Stärke des LOGO!MAT-Baukastenprinzips."
            ),
        ],
    },
]

# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv
    token = os.environ.get("SANITY_WRITE_TOKEN")

    if not token:
        print("Error: SANITY_WRITE_TOKEN not set.")
        sys.exit(1)

    mutations = [{"createOrReplace": s} for s in SERVICES]

    url = f"{BASE_URL}/mutate/{DATASET}"
    if dry_run:
        url += "?dryRun=true"
        print("DRY RUN — no changes will be written\n")

    print(f"Sending {len(mutations)} service documents to Sanity ({DATASET})...")
    for s in SERVICES:
        print(f"  [{s['tier'].upper()}] {s['name']} — /{s['slug']['current']}")
    print()

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
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
