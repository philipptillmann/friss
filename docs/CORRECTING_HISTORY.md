# Zutaten und Rezepte für Zukunft oder Vergangenheit korrigieren (v1.39.0)

Beim Bearbeiten einer **gespeicherten** manuellen Zutat unter **Manuell** sowie eines Rezepts/Getränks stehen zwei Speicheroptionen zur Verfügung:

- **Nur für zukünftige Einträge speichern**
- **Speichern und bisherige Einträge korrigieren**

Neue manuelle Zutaten haben nur den normalen Speichern-Button, da sie noch keine bisherigen Verwendungen besitzen.

## Manuell angelegte Zutat

**Nur Zukunft** aktualisiert die Lebensmitteldefinition. Neue direkte Verwendungen und neu hinzugefügte Rezeptzutaten verwenden diesen Stand. Alle bestehenden Mahlzeiten und Rezeptzutaten behalten ihre gespeicherte Momentaufnahme. Ein bestehendes Rezept mit alten Zutaten verwendet deshalb auch bei neuer Portionsbuchung weiterhin diese alten Zutatenstände, bis sie selbst korrigiert werden.

**Bisherige Einträge korrigieren** verlangt eine Bestätigung und aktualisiert gemeinsam:

1. Bisherige direkte Verwendungen dieser Zutat im Tagebuch, auch Kopien.
2. Vorhandene Rezept- und Getränkezutaten mit dieser Lebensmittel-ID.
3. Bereits gebuchte Rezept-/Getränkeportionen, deren damalige Momentaufnahme diese Zutat enthält – auch wenn das aktuelle Rezept inzwischen anders aussieht oder gelöscht wurde.

Mengen, Zeitpunkte, Trinkdauer und alle anderen Zutaten bleiben erhalten. Bei alten Rezeptportionen bleiben die damalige Portionszahl, das Gesamtgewicht/Volumen, zusätzliche Mengen und der Rezeptname erhalten. Nur der betreffende Lebensmittelstand wird ausgetauscht; die Nährwerte und gegebenenfalls Alkohol-/Koffeinmengen werden neu berechnet. Dadurch werden keine unabhängigen späteren Rezeptänderungen auf alte Portionen übertragen.

Wenn vorhandene Mengeneinheiten nicht zur neuen Bezugsmenge passen (z. B. gespeicherte Gramm gegenüber einer neuen 100-ml-Basis), wird die gesamte Korrektur abgelehnt. Es gibt keine Dichteannahme. Dann nur für die Zukunft speichern oder die betroffenen Daten einzeln mit passender Menge korrigieren. Auch bei nicht berechenbaren Rezeptmomentaufnahmen bricht die Korrektur ab, statt teilweise zu speichern.

## Rezept oder Getränk

Die Zukunftsoption speichert die aktuelle Rezeptdefinition für künftige Buchungen. Die Korrekturoption berechnet bereits gebuchte Portionen mit dem **aktuellen gesamten Rezeptstand** neu. Ihre Verzehrmengen, Zeitpunkte und Trinkdauer bleiben erhalten. Das ist der Unterschied zur manuellen Zutatenkorrektur, die in alten Rezeptmomentaufnahmen nur das betreffende Lebensmittel ersetzt.

Ein bloßes Zukunfts-Speichern einer manuellen Zutat verändert die bereits gespeicherten Rezeptzutaten nicht. Für deren Korrektur zuerst die Zutat mit der Korrekturoption speichern oder die Rezeptzutat ausdrücklich ersetzen/ändern.

## Originale, Health und Sicherheit

- Originaldateien bleiben unverändert. Vor rückwirklichen Änderungen wird der bisherige Eintrag als `data/originals/<id>-revision-<revision>.json` archiviert.
- Bereits exportierte Apple-Health-Samples und Exportpakete werden nicht überschrieben. Der Tagesexport erscheint nach einer relevanten Änderung als **geändert**. Korrekturen auf dem iPhone sind separat erforderlich; nicht blind erneut exportieren.
- Solange ein betroffener Export reserviert/in Bearbeitung ist (`claimed`), wird die Korrektur abgelehnt. Die Health-Übertragung zuerst abschließen bzw. den unklaren Export prüfen und entsprechend bestätigen.
- Definition und Datenbankeinträge ändern sich in einer Transaktion. Versionskonflikte, unpassende Einheiten oder blockierte Exporte verhindern die gesamte Änderung. Bei Konflikten den aktuellen Zutatenstand neu laden.
- ZIP-Backups enthalten Definitionen, korrigierte Momentaufnahmen und Revisionsdateien wie bisher.

API: `PUT /manual-ingredients/{id}` akzeptiert zusätzlich `amend_existing: true` (Standard false), zusammen mit der aktuellen `version`. Die Antwort enthält `amended_entries`, `amended_direct_entries` und `amended_recipe_entries`. Das Flag und die Zähler werden nicht als Lebensmittel-Nährwerte gespeichert. `PUT /recipes/{id}` verwendet weiterhin `amend_existing` für die Rezeptkorrektur.
