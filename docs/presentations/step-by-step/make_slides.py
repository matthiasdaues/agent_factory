"""Agent Factory Schritt für Schritt: diagrams on character grids, written to slides.txt."""

import re
import sys
import textwrap
from pathlib import Path

# Usage: python3 make_slides.py [slides.txt], then remark-deck build on this folder.
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("slides.txt")
TOO_WIDE = []
MARKERS = re.compile(r"\*\*|%%|__|~~|!!")
FOOTER = "agent factory · schritt für schritt"


class Canvas:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.cells = [[" "] * cols for _ in range(rows)]
        self.marks = []

    def put(self, x, y, text):
        for i, ch in enumerate(text):
            assert 0 <= x + i < self.cols and 0 <= y < self.rows, (x, y, text)
            self.cells[y][x + i] = ch

    def box(self, x, y, w, h, lines=(), align="center"):
        self.put(x, y, "┌" + "─" * (w - 2) + "┐")
        for r in range(1, h - 1):
            self.put(x, y + r, "│" + " " * (w - 2) + "│")
        self.put(x, y + h - 1, "└" + "─" * (w - 2) + "┘")
        for i, line in enumerate(lines):
            if len(line) > w - 4:
                TOO_WIDE.append((line, len(line), w - 4))
            pad = (w - 2 - len(line)) // 2 if align == "center" else 1
            self.put(x + 1 + pad, y + 1 + i, line)

    def vline(self, x, y1, y2, end=None):
        for y in range(y1, y2 + 1):
            self.put(x, y, "│")
        if end:
            self.put(x, y2, end)

    def hline(self, x1, x2, y, end=None):
        for x in range(x1, x2 + 1):
            self.put(x, y, "─")
        if end == "►":
            self.put(x2, y, end)
        elif end == "◄":
            self.put(x1, y, end)

    def mark(self, row, text, marker):
        self.marks.append((row, text, marker))

    def rows_out(self):
        out = ["".join(r).rstrip() for r in self.cells]
        for row, text, marker in self.marks:
            assert text in out[row], (row, text)
            out[row] = out[row].replace(text, f"{marker}{text}{marker}", 1)
        return out


def title(c, text, sub=None):
    c.put(4, 1, text)
    c.mark(1, text, "**")
    if sub:
        c.put(4, 2, sub)
        c.mark(2, sub, "%%")


def text(c, x, y, line, marker=None):
    c.put(x, y, line)
    if marker:
        c.mark(y, line, marker)


def slide(c, footer=FOOTER):
    rows = c.rows_out()
    for r in rows:
        assert len(MARKERS.sub("", r)) <= c.cols, r
    return f"```grid {c.cols}x{c.rows}\n" + "\n".join(rows) + f"\n```\n@footer {footer}"


slides = []

# 1. Titel ---------------------------------------------------------------------
c = Canvas(40, 10)
text(c, 3, 2, "AGENT FACTORY", "**")
text(c, 3, 3, "SCHRITT FÜR SCHRITT", "**")
text(c, 3, 5, "Wie aus einer Idee", "%%")
text(c, 3, 6, "geprüfter Code wird")
text(c, 3, 8, "eine Einführung", "~~")
slides.append(slide(c, "20. November 2026"))

# 2. Die eine Idee --------------------------------------------------------------
c = Canvas(62, 14)
text(c, 3, 2, "SIE ENTSCHEIDEN.", "**")
text(c, 3, 3, "DER ASSISTENT ARBEITET.", "**")
text(c, 3, 4, "SIE GEBEN JEDEN SCHRITT FREI.", "**")
text(c, 3, 6, "Die Factory baut nie alles auf einmal.")
text(c, 3, 7, "Sie arbeitet in kleinen, sichtbaren Schritten")
text(c, 3, 8, "und hält nach jedem an.")
text(c, 3, 10, "Eine KI arbeitet schnell, aber ungenau.", "%%")
text(c, 3, 11, "Dagegen hilft häufiges, billiges Prüfen:", "%%")
text(c, 3, 12, "durch ein Werkzeug, einen Test oder Sie.", "%%")
slides.append(slide(c))

# 3. Fünf Begriffe ---------------------------------------------------------------
c = Canvas(99, 25)
title(c, "FÜNF BEGRIFFE", "mehr Wortschatz braucht es für den Anfang nicht")
c.box(4, 5, 20, 4, ["PLAYBOOK", "das Rezept"])
c.hline(24, 31, 6, "►")
c.put(25, 5, "ruft")
c.box(32, 5, 20, 4, ["AGENT", "eine Aufgabe"])
c.hline(52, 59, 6, "►")
c.put(53, 5, "liefert")
c.box(60, 5, 16, 4, ["ARTEFAKT", "ein Dokument"])
c.hline(76, 80, 6, "►")
c.box(81, 5, 15, 4, ["GATE", "prüft"])
c.vline(42, 9, 10, "▼")
c.put(44, 9, "folgt")
c.box(32, 11, 20, 4, ["SKILL", "das Vorgehen"])
c.box(4, 11, 20, 4, ["CONTEXT", "der Steckbrief"])
c.hline(24, 27, 12)
c.put(28, 12, "┘")
c.vline(28, 8, 11)
c.put(28, 7, "┌")
c.hline(29, 31, 7, "►")
c.put(15, 10, "Wissen")
rows = [("Agent", "eine Aufgabe: Anforderungen schreiben, Architektur prüfen, einen Fehler beheben"),
        ("Skill", "die Arbeitsanweisung, nach der ein Agent seine Aufgabe erledigt"),
        ("Playbook", "das Rezept: welche Agenten in welcher Reihenfolge, für eine typische Lage"),
        ("Gate", "eine automatische Prüfung, die Fehler fängt, bevor Sie Zeit verlieren"),
        ("Context", "wenige Dateien, in denen das Projekt Stack, Ablauf und Regeln festhält")]
for i, (word, meaning) in enumerate(rows):
    y = 17 + i
    text(c, 4, y, word, "**")
    c.put(15, y, meaning)
text(c, 4, 23, "Den Katalog liest der Assistent selbst: INDEX.yaml listet jeden Agenten, Skill und Playbook.", "~~")
slides.append(slide(c))

# 4. Arbeiter und Prüfer ------------------------------------------------------------
c = Canvas(99, 25)
title(c, "WER ARBEITET, PRÜFT NICHT", "Autor und Prüfer sind nie derselbe Agent")
c.box(4, 5, 22, 5, ["AUTOR", "Sitzung 1"])
c.hline(26, 34, 7, "►")
c.box(35, 5, 26, 5, ["ARTEFAKT", "Spezifikation, Archi-", "tektur oder Code"])
c.hline(61, 68, 7, "►")
c.box(69, 5, 26, 5, ["PRÜFER", "neue, leere Sitzung", "sieht nur das Artefakt"])
c.vline(82, 10, 12)
c.put(82, 12, "┘")
c.hline(15, 81, 12)
c.put(15, 12, "┌")
c.vline(15, 10, 11)
c.put(15, 10, "▲")
c.put(40, 11, "Befunde gehen an den Autor zurück")
c.mark(11, "Befunde gehen an den Autor zurück", "~~")
text(c, 4, 14, "Warum: Den Fehler, den man selbst übersieht, findet man selbst nicht.")
text(c, 4, 15, "Derselbe blinde Fleck, der ihn erzeugt, verbirgt ihn auch.")
pairs = [("requirements-agent", "spec-review-agent"),
         ("architecture-agent", "architecture-review-agent"),
         ("implementation-agent", "code-review-agent, qa-agent"),
         ("die gebaute Software", "reconciliation-agent")]
text(c, 4, 17, "Autor", "**")
text(c, 33, 17, "Prüfer", "**")
for i, (a, b) in enumerate(pairs):
    c.put(4, 18 + i, a)
    c.put(27, 18 + i, "──►")
    c.put(33, 18 + i, b)
text(c, 4, 23, "Die Trennung machen Sie: Für jede Prüfung öffnen Sie eine neue Sitzung.", "**")
slides.append(slide(c))

# 5. Die erste Sitzung -----------------------------------------------------------------
c = Canvas(99, 25)
title(c, "DIE ERSTE SITZUNG", "VIRGIL begrüßt Sie und bietet vier Türen an")
c.box(34, 4, 31, 4, ["VIRGIL", "Führer, Lehrer, Vermittler"])
c.vline(49, 8, 9)
c.hline(13, 85, 10)
for x in (13, 37, 61, 85):
    c.put(x, 10, "┬" if x not in (13, 85) else ("┌" if x == 13 else "┐"))
    c.put(x, 11, "▼")
c.put(49, 10, "┴")
doors = [("H", "HILFE", ["Ich bin neu", "und brauche", "Orientierung"]),
         ("K", "HAUSHALT", ["Zustand prüfen,", "neu einrichten,", "aktualisieren"]),
         ("P", "PROJEKT", ["Arbeit beginnen", "oder fortsetzen:", "ein Playbook"]),
         ("O", "OFFENE BÜHNE", ["Einfach reden,", "bis die Idee", "Gestalt annimmt"])]
for x, (key, name, lines) in zip((3, 27, 51, 75), doors):
    c.box(x, 12, 21, 6, [f"{key}: {name}", *lines])
text(c, 4, 20, "Fragen Sie jederzeit: „Wo bin ich?“ oder „Was ist ein Gate?“")
text(c, 4, 22, "Der beste erste Schritt ist poc-spike: eine Idee, ein kleines lauffähiges Ding,")
text(c, 4, 23, "in Minuten. Sie sehen dem Zusammenspiel zu, bevor Sie sich auf etwas festlegen.")
c.mark(22, "poc-spike", "**")
slides.append(slide(c))

# 6. Einrichten ---------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "EINRICHTEN", "einmal pro Projekt: installieren, dann anpassen")
c.box(3, 5, 27, 6, ["INIT-FACTORY", "verdrahtet die Factory", "und scannt das Projekt"])
c.hline(30, 34, 7, "►")
c.box(35, 4, 38, 9, [])
text(c, 37, 4, " FITTING: SECHS SCHRITTE ", "**")
fit = ["1  Modellmatrix: welches Modell wofür",
       "2  Projekt-Fingerabdruck bestätigen",
       "3  Agent-Kontext: wo das Wissen liegt",
       "4  Testregime: wie das Projekt testet",
       "5  Pre-commit-Hooks entscheiden",
       "6  Zähler für Befund-IDs setzen"]
for i, line in enumerate(fit):
    c.put(37, 6 + i, line)
c.hline(73, 79, 7, "►")
c.box(80, 5, 17, 5, ["BEREIT", "für das erste", "Playbook"])
files = [("model.conf", "ordnet Stufen wie economy, standard, strong echten Modellen zu"),
         ("project-context.json", "was der Scan fand: Sprachen, Frameworks, CI, Linter, Tests"),
         ("docs/agent-context.md", "Schaltzentrale: welcher Agent wo im Projekt nachliest"),
         ("docs/testing.yaml", "die Testbefehle und die Schwellen der Gates")]
text(c, 4, 17, "Was danach auf der Platte liegt", "**")
for i, (f, d) in enumerate(files):
    c.put(4, 19 + i, f)
    c.put(28, 19 + i, d)
slides.append(slide(c))

# 7. Fünf Arbeitsarten ---------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "DER WEG EINER IDEE", "fünf Arten von Arbeit und der Abgleich, jede mit Autor und Prüfer")
work = [("ANFORDERUNG", ["Was bauen", "wir, für", "wen?"]),
        ("ARCHITEKTUR", ["Welche Form", "hat es?"]),
        ("PLANUNG", ["kleine,", "unabhängige", "Stories"]),
        ("UMSETZUNG", ["erst Test,", "dann Code"]),
        ("QUALITÄT", ["prüfen und", "Fehler", "jagen"]),
        ("ABGLEICH", ["Doku gegen", "den Code"])]
xs = [3, 19, 35, 51, 67, 83]
for i, (x, (name, lines)) in enumerate(zip(xs, work)):
    c.box(x, 5, 15, 6, [name, *lines])
    if i < len(xs) - 1:
        c.put(x + 15, 7, "►")
authors = ["requirements", "architecture", "planning", "implementation", "qa", "reconciliation"]
checks = ["spec-review", "architecture-", "backlog-lint", "code-review", "Fehlerjagd", "Befunde an"]
checks2 = ["", "review (ATAM)", "und Sie", "", "mit Tests", "den Eigentümer"]
text(c, 3, 12, "Autor", "~~")
text(c, 3, 15, "Prüfer", "~~")
for x, a, b, b2 in zip(xs, authors, checks, checks2):
    c.put(x, 13, a[:15])
    c.put(x, 16, b[:15])
    if b2:
        c.put(x, 17, b2[:15])
text(c, 4, 20, "Sie geben jede Übergabe frei.", "**")
text(c, 4, 21, "Kleine Aufgaben nehmen kürzere Playbooks, die nur die nötigen Arten berühren.")
text(c, 4, 22, "Muss etwas nachgebessert werden, korrigieren Sie das Artefakt direkt.")
text(c, 4, 23, "Es gibt kein „Zurück in eine frühere Phase“.")
slides.append(slide(c))

# 8. Anforderungen ---------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "1  ANFORDERUNGEN", "erst klären, was gebaut wird; dann prüfen, ob es widerspruchsfrei ist")
c.box(3, 5, 17, 5, ["IDEE", "im Gespräch", "mit VIRGIL"])
c.hline(20, 23, 7, "►")
c.box(24, 5, 17, 5, ["PROPOSAL", "bereit zur", "Entscheidung"])
c.hline(41, 44, 7, "►")
c.box(45, 4, 26, 7, ["REQUIREMENTS-AGENT", "PRD · .feature-Datei", "Scope-Map", "Lückenbericht"])
c.hline(71, 74, 7, "►")
c.box(75, 4, 21, 7, ["SPEC-REVIEW", "neue Sitzung", "spec-lint, dann", "inhaltlich"])
c.vline(57, 11, 11)
c.hline(45, 67, 12); c.put(45, 12, "┌"); c.put(67, 12, "┐"); c.put(57, 12, "┴")
c.put(45, 13, "▼"); c.put(67, 13, "▼")
c.box(33, 14, 24, 5, ["DOMAIN-MODELING", "Glossar, Entitäten,", "Zustandsautomaten"])
c.box(58, 14, 19, 5, ["TEST-STRATEGY", "QA-Strategie", "je Feature"])
text(c, 79, 12, "SPEC-Befunde gehen", "~~")
text(c, 79, 13, "an ihren Eigentümer", "~~")
text(c, 4, 20, "Die .feature-Datei ist die Abnahme-Spezifikation in Gherkin. Sie gehört dem")
text(c, 4, 21, "Stakeholder, nicht dem Entwickler, und läuft später als Test.")
text(c, 4, 23, "Offene SPEC-Befunde? Dann Schleife: beheben, erneut prüfen. Sonst weiter.", "**")
slides.append(slide(c))

# 9. Architektur -------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "2  ARCHITEKTUR", "die großen Entscheidungen bewusst treffen und festhalten, bevor Code sie festlegt")
c.box(3, 5, 30, 8, ["ARCHITECTURE-AGENT", "", "arc42-Kapitel", "Structurizr-Modell (C4)", "ADRs, Pugh-Matrix bei", "echten Alternativen"])
c.hline(33, 39, 8, "►")
c.box(40, 5, 26, 8, ["ARCHITECTURE-REVIEW", "", "neue Sitzung", "arch-lint, dann ATAM:", "Qualitätsziele gegen", "die Entscheidungen"])
c.hline(66, 72, 8, "►")
c.box(73, 6, 23, 6, ["AGENT-KONTEXT", "nachführen,", "concern-lint,", "Ihre Freigabe"])
c.vline(53, 13, 15)
c.put(53, 15, "┘")
c.hline(18, 52, 15)
c.put(18, 15, "┌")
c.vline(18, 13, 14)
c.put(18, 13, "▲")
c.put(20, 16, "ATAM-Befunde: Schleife, bis keiner mehr offen ist")
c.mark(16, "ATAM-Befunde: Schleife, bis keiner mehr offen ist", "~~")
text(c, 4, 18, "Das Modell in architecture.dsl ist die eine Quelle. Diagramme und Kapitel")
text(c, 4, 19, "werden daraus abgeleitet, nicht umgekehrt.")
text(c, 4, 21, "Erst wenn der Agent-Kontext sauber ist und Sie ihn freigeben, darf geplant werden.", "**")
slides.append(slide(c))

# 10. Planung --------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "3  PLANUNG", "Spezifikation und Architektur werden zu kleinen Stories")
plan = [("EPICS", ["Fähigkeiten", "schneiden"]),
        ("TESTBARKEIT", ["wem gehört", "welcher Test?"]),
        ("SCHNITTE", ["Stories je", "Epic skizziert"]),
        ("STORIES", ["ST-NNNN.md", "schreiben"])]
for i, (name, lines) in enumerate(plan):
    x = 3 + i * 21
    c.box(x, 5, 18, 5, [name, *lines])
    if i < 3:
        c.put(x + 18, 7, "─►")
c.put(4, 4, "planning-agent, create-backlog in Phasen; nach jeder Phase geben Sie frei")
c.mark(4, "planning-agent, create-backlog in Phasen; nach jeder Phase geben Sie frei", "~~")
c.vline(75, 10, 11, "▼")
c.box(62, 12, 27, 4, ["BACKLOG-LINT", "Schema, Abhängigkeiten"])
c.vline(75, 16, 17, "▼")
c.box(62, 18, 27, 3, ["IHRE FREIGABE"])
text(c, 4, 13, "Jede Story hat:", "**")
for i, line in enumerate(["ein Ziel und Akzeptanzkriterien",
                          "eine Priorität nach MoSCoW",
                          "Abhängigkeiten zu anderen Stories",
                          "die Dateien, die sie berührt",
                          "eine Stufe (tier) und ihre Gates"]):
    c.put(6, 14 + i, "· " + line)
text(c, 4, 21, "Gute Stories sind INVEST: unabhängig, verhandelbar, wertvoll, schätzbar, klein, testbar.")
text(c, 4, 23, "Einrichtung wie Testrunner oder CI steckt in der ersten Story, die sie braucht.", "~~")
slides.append(slide(c))

# 11. Umsetzung ---------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "4  UMSETZUNG", "Test zuerst, Gates nach jeder Story, ein Review über das ganze Feature")
c.box(3, 4, 24, 5, ["IMPLEMENTATION", "verteilt Stories in", "Wellen"])
c.hline(27, 31, 6, "►")
c.box(32, 4, 22, 5, ["DEVELOPER", "rot, grün, umbauen", "je Story"])
c.hline(54, 58, 6, "►")
c.box(59, 3, 22, 7, ["GATES", "crap-score", "mutation-testing", "test-design-verify", "dependency-check"])
c.hline(81, 85, 6, "►")
c.box(86, 4, 10, 5, ["MERGE", "der", "Story"])
c.vline(70, 10, 11)
c.put(70, 12, "┘")
c.hline(43, 69, 12)
c.put(43, 12, "┌")
c.vline(43, 9, 11)
c.put(43, 9, "▲")
c.put(48, 11, "rot")
c.put(4, 13, "FRISCHER DEVELOPER: nur Gate-Bericht und betroffene Dateien")
c.mark(13, "FRISCHER DEVELOPER:", "**")
c.put(4, 14, "3 Versuche, dann eine Modellstufe höher, 3 weitere")
c.mark(14, "3 Versuche, dann eine Modellstufe höher, 3 weitere", "~~")
c.box(3, 16, 34, 5, ["NACH DER LETZTEN WELLE", "CODE-REVIEW über das ganze", "Feature, neue Sitzung"])
c.hline(37, 41, 18, "►")
c.box(42, 16, 25, 5, ["IMPL-BEFUNDE", "Prüfer nennt Fakten,", "Regel setzt Schwere"])
c.hline(67, 71, 18, "►")
c.box(72, 16, 24, 5, ["BLOCKIEREND?", "beheben, erneut", "prüfen, alles frisch"])
text(c, 4, 22, "Ein Wiederholungs-Review prüft jeden alten Befund und dann alles neu:")
text(c, 4, 23, "Eine Korrektur kann einen Fehler bringen, den der erste Durchgang nie sah.", "~~")
slides.append(slide(c))

# 12. Qualität und Abgleich ------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "5  QUALITÄT UND ABGLEICH", "unabhängig prüfen, Fehler jagen, dann Doku und Code abgleichen")
c.box(3, 4, 30, 8, ["QA-AGENT", "neue Sitzung", "Fagan-Inspektion", "Sicherheit nach OWASP", "Fehlerjagd"])
c.hline(33, 37, 7, "►")
c.box(38, 4, 22, 8, ["PREMERGE-CHECK", "dann Merge", "nach dev", "durch Sie"])
c.hline(60, 64, 7, "►")
c.box(65, 4, 31, 8, ["RECONCILIATION", "auf dev, neue Sitzung", "Spezifikation und", "Architektur gegen den", "gebauten Code"])
text(c, 4, 14, "Die Fehlerjagd, Fehler für Fehler:", "**")
hunt = ["1  Test schreiben, der den Fehler zeigt: er ist rot",
        "2  Code reparieren: der Test wird grün und bleibt",
        "3  erneut jagen, bis eine Runde nichts mehr findet"]
for i, line in enumerate(hunt):
    c.put(6, 15 + i, line)
text(c, 4, 19, "Jede Abweichung im Abgleich geht an ihren Eigentümer:", "**")
c.put(6, 20, "Code-Fehler an den Developer, Doku-Drift an den Autor des Dokuments.")
text(c, 4, 22, "Keine offenen Befunde mehr: fertig. Das Projekt ist bereit für das nächste Feature.", "**")
slides.append(slide(c))

# 12b. Wissensfluss -----------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "WISSENSFLUSS", "nach vorn wächst die Festlegung, nach hinten korrigiert der Code die Annahmen")
text(c, 3, 4, "FLUSS NACH VORN", "**")
c.put(22, 4, "ungewiss ")
c.hline(31, 85, 4, "►")
text(c, 87, 4, "spezifisch", "~~")
forward = [("PROPOSAL", "was, für wen"), ("SPEZIFIKATION", "Verhalten"),
           ("ARCHITEKTUR", "Form, Grenzen"), ("PLANUNG", "Stories"), ("BAUEN", "Code, Tests")]
for i, (name, line) in enumerate(forward):
    x = 3 + i * 19
    c.box(x, 5, 17, 4, [name, line])
    if i < 4:
        c.put(x + 17, 6, "─►")
# Rückkanal: von der Reconciliation hinauf zu jeder Stufe, die Annahmen festlegt
for x in (11, 30, 49, 68):
    c.put(x, 9, "▲")
    c.put(x, 10, "│")
c.hline(11, 68, 11)
c.put(11, 11, "└"); c.put(30, 11, "┴"); c.put(49, 11, "┼"); c.put(68, 11, "┘")
c.put(49, 12, "│")
text(c, 13, 12, "Befunde an den Eigentümer", "~~")
c.vline(87, 9, 12, "▼")
c.box(79, 13, 17, 5, ["CODE-REVIEW", "das ganze", "Feature"])
c.hline(77, 78, 15, "◄")
c.box(60, 13, 17, 5, ["QA", "prüfen,", "Fehler jagen"])
c.hline(58, 59, 15, "◄")
c.box(40, 13, 18, 5, ["RECONCILIATION", "Doku gegen", "den Code"])
text(c, 4, 14, "FLUSS NACH HINTEN", "**")
c.put(4, 15, "Der gebaute Code prüft die")
c.put(4, 16, "„halbfesten Annahmen“.")
text(c, 4, 19, "Nach vorn legt jede Stufe fest, was die vorige offen ließ.", "**")
c.put(4, 20, "Jede Festlegung ruht auf Annahmen. Sie sind fest genug zum Weiterbauen,")
c.put(4, 21, "aber erst der Code zeigt, ob sie halten.")
text(c, 4, 23, "Hält eine Annahme nicht, korrigiert der Eigentümer sein Dokument, nicht nur den Code.", "**")
slides.append(slide(c))

# 13. Gates ------------------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "WAS DIE MASCHINEN PRÜFEN", "bevor Sie hinsehen, fängt ein Gate den Fehler")
c.box(3, 4, 44, 15, [])
text(c, 5, 4, " BEI JEDEM COMMIT ", "**")
hooks = [("mdformat", "Markdown einheitlich"),
         ("link-check", "Links führen ins Ziel"),
         ("mermaid-lint", "Diagramme brechen nicht"),
         ("spec-lint", "Spezifikation stimmig"),
         ("arch-lint", "Architektur und Modell"),
         ("backlog-lint", "Stories vollständig"),
         ("concern-lint", "Agent-Kontext gültig"),
         ("matrix-lint", "Modellmatrix gültig"),
         ("statemachine-lint", "Automaten stimmig"),
         ("finding-lint", "Schwere nach Regel"),
         ("index-lint", "Katalog aktuell")]
for i, (h, d) in enumerate(hooks):
    c.put(5, 6 + i, f"{h:<19}{d}")
c.box(50, 4, 46, 8, [])
text(c, 52, 4, " NACH JEDER STORY ", "**")
sem = [("crap-score", "Komplexität und Abdeckung"),
       ("mutation-testing", "fangen die Tests Fehler?"),
       ("test-design-verify", "vorgeschriebene Tests da?"),
       ("dependency-check", "Abhängigkeitsregeln")]
for i, (h, d) in enumerate(sem):
    c.put(52, 6 + i, f"{h:<19}{d}")
c.box(50, 13, 46, 6, [])
text(c, 52, 13, " VOR DEM MERGE ", "**")
c.put(52, 15, "premerge-check: alle Gates bestanden,")
c.put(52, 16, "Basis aktuell, nur erlaubte Dateien")
text(c, 4, 21, "Schlägt ein Gate an, arbeitet das System richtig.", "**")
text(c, 4, 22, "Beheben Sie die Ursache. Umgehen Sie den Alarm nicht.")
slides.append(slide(c))

# 14. Welches Playbook ----------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "WELCHES PLAYBOOK, WANN", "das Rezept passend zur Lage")
books = [("Prüfen, ob eine grobe Idee überhaupt trägt", "poc-spike"),
         ("Ein technisches Risiko vor der Entscheidung klären", "technical-poc"),
         ("Einen gemeldeten Fehler beheben", "bug-fix"),
         ("Die Doku wieder mit dem Code in Einklang bringen", "documentation-update"),
         ("Ein neues Projekt richtig bauen, von Anfang bis Ende", "greenfield-development"),
         ("Die Factory in bestehenden Code einführen", "brownfield-onboarding"),
         ("Ein Feature zu einem Factory-Projekt hinzufügen", "feature-addition"),
         ("Code umbauen, ohne sein Verhalten zu ändern", "refactoring"),
         ("Eine Architektur gegen Qualitätsziele bewerten", "architecture-review"),
         ("Ein Thema mit belegten Quellen erkunden", "research-survey"),
         ("Eine Behauptung durch Widerlegungsversuche testen", "research-topic")]
text(c, 4, 4, "Sie wollen …", "**")
text(c, 62, 4, "Beginnen Sie mit", "**")
c.put(4, 5, "─" * 91)
for i, (want, book) in enumerate(books):
    c.put(4, 6 + i, want)
    c.put(62, 6 + i, book)
text(c, 4, 19, "Ein Playbook beschreibt einen typischen Weg, keinen Zwang. Welche Agenten gerade")
text(c, 4, 20, "laufen dürfen, ergibt sich aus den Artefakten, die schon da sind.")
text(c, 4, 22, "Unsicher? Wählen Sie im Menü P. VIRGIL fragt nach und schlägt das Rezept vor.", "~~")
slides.append(slide(c))

# 15. Drei Gewohnheiten -----------------------------------------------------------------------------------------
c = Canvas(62, 14)
text(c, 3, 1, "DREI GEWOHNHEITEN", "**")
habits = [("Lesen, bevor Sie freigeben.", "Ihr Ja ist das letzte Gate. Es zählt am meisten."),
          ("Die Gates arbeiten lassen.", "Ein Alarm ist kein Defekt. Ursache beheben."),
          ("Ein kleiner Schritt nach dem anderen.", "So wird Rauschen korrigiert, bevor es wächst.")]
for i, (head, body) in enumerate(habits):
    y = 3 + i * 3
    text(c, 3, y, f"{i + 1}  {head}", "**")
    c.put(6, y + 1, body)
text(c, 3, 12, "Anfangen: ein poc-spike. Der Rest kommt beim Tun.", "~~")
slides.append(slide(c))

assert not TOO_WIDE, TOO_WIDE
header = ("% title: Agent Factory Schritt für Schritt\n% topic: agent-factory-schritt-fuer-schritt\n"
          "% date: 2026-11-20\n% lang: de\n")
OUT.write_text(header + "\n---\n".join(slides) + "\n")
print(f"{len(slides)} slides written to {OUT}")
