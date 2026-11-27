# Eigene Lebensmittel: Barcodes und Etiketten-OCR · v1.47.0

## Deutsch

Unter **Manuell** kannst du einem Lebensmittel einen oder mehrere Barcodes zuordnen und seine Nährwerte von einem fotografierten oder hochgeladenen Etikett übernehmen. Es wird keine externe KI benötigt; die Texterkennung läuft mit Tesseract auf deinem Server.

### Barcode verknüpfen

1. Manuelles Lebensmittel anlegen oder bearbeiten.
2. Im Feld **Barcodes für dieses Lebensmittel** Nummern eintragen (eine je Zeile; 8–14 Ziffern, führende Nullen erhalten) oder **Barcode hinzufügen: fotografieren** wählen.
3. Namen, Bezugsmenge (100 g/100 ml) und bekannte Nährwerte prüfen und speichern.

Ein Barcode darf nur einem manuellen Lebensmittel zugeordnet sein. Doppelbelegungen werden mit Hinweis auf das bereits verknüpfte Lebensmittel abgelehnt. Mehrere Barcodes beim gleichen Lebensmittel sind möglich (bis zu 50). Zum Lösen Nummer entfernen und das Lebensmittel speichern; zum Übertragen zuerst am bisherigen Lebensmittel entfernen. Auch die Löschung einer Definition gibt ihre Barcodes frei.

Beim **normalen Barcode-Scan** unter Mahlzeiten und Rezept-/Getränkezutaten prüft Friss zuerst die eigene Datenbank. Bei Treffer erscheinen Name und Bezugsmenge; beim Speichern werden deren Nährwerte verwendet, ohne OFF-Abfrage. Ohne eigenen Treffer gilt der bisherige Open-Food-Facts-Ablauf. Ein Produkt pro 100 ml verlangt eine Verbrauchsmenge in ml; Gramm und Volumen werden nicht gleichgesetzt.

Die ausdrücklich gewählte Erfassung **Barcode → BLS** bleibt getrennt und verwendet weiter deine BLS-Zuordnung. Vorhandene OFF-Einträge wechseln beim bloßen Anzeigen oder OFF-Aktualisieren nicht zu einer inzwischen angelegten eigenen Definition.

Barcode-Verzehr mit eigenem Treffer wird als manuelles Lebensmittel mit gespeichertem Definitionsstand, Barcode und Herkunft erfasst. Alte Verzehre behalten ihre Daten, auch nach Löschen/Ändern einer Barcode-Verknüpfung. Für Nährwertkorrekturen gelten weiterhin die beiden Speicheroptionen Zukunft/bisherige Verwendungen. Das normale Wiederholen derselben Eintrags-ID erzeugt keinen neuen Verzehr und behält den ursprünglich verwendeten Stand.

### Nährwertetikett fotografieren/hochladen

1. Im manuellen Editor nach Bedarf Barcode und Namen eingeben.
2. **Nährwertetikett fotografieren** oder **Etikettbild hochladen** wählen. Eine scharfe Aufnahme mit nur einer eindeutigen Wertespalte verwenden.
3. Bei einer klaren **100-g-Tabelle** kann die OCR-Bezugsmenge leer bleiben.
4. Bei anderen Angaben unter **Bezugsmenge des fotografierten Etiketts** die bestätigte Basis eingeben:
   - **6 g**, wenn alle fotografierten Werte pro 6-g-Tablette gelten.
   - **100 ml** für eine 100-ml-Tabelle.
   - Eine andere bekannte Gramm-/Millilitermenge für die jeweilige Portion.
5. Friss rechnet die Vorschläge auf 100 g beziehungsweise 100 ml um. Barcode und Name bleiben erhalten. Bei einer gespeicherten Definition bleibt der Bearbeitungsmodus erhalten; es entsteht nicht ungefragt ein neues Lebensmittel.
6. Erkannte Werte, Einheiten, Bezugsmenge und Namen sorgfältig prüfen. Erst **Speichern** beziehungsweise eine der Korrekturoptionen legt/ändert die Definition. OCR allein bucht weder Lebensmittel noch Verzehr.

Beispiel: Foto zeigt **80 mg Vitamin C pro 6-g-Tablette**. Vorschlag im manuellen Lebensmittel: rund **1.333,33 mg pro 100 g**. Beim späteren Verzehr von **6 g** werden wieder **80 mg** gebucht. Das Tablettengewicht muss bekannt sein und wird nicht geschätzt.

Die Texterkennung umfasst Hauptnährwerte sowie unterstützte Vitamine/Mineralstoffe, einschließlich B1/B2/B3/B5/B6/B7/B12 und Folat. Sie ist fehleranfällig; unbekannte oder mehrdeutige Angaben bleiben leer. Mehrere Wertespalten, widersprüchliche feste Bezugsgrößen und US-Gesamtkohlenhydrate werden nicht automatisch interpretiert. Eine bestätigte Portionsmenge darf keine gedruckte 100-g-Spalte in eine andere Bezugsgröße umdeuten. Keine Dichteannahme bei g/ml.

Erkannter Text und die Bezugsangabe stehen in den Notizen. Die OCR-Bilddatei wird wie bisher nur verarbeitet, nicht als Produktfoto archiviert. Webimporte bleiben zusätzlich verfügbar. Barcodes und manuelle Nährwerte sind Bestandteil der bestehenden ZIP-Sicherung; keine neue Datenbanktabelle nötig.

### API

Normale Friss-Authentifizierung verwenden.

- `POST /manual-ingredients` / `PUT /manual-ingredients/{id}`: zusätzlich `barcodes: ["4316268448871"]`. PUT benötigt die aktuelle Version; `[]` löst alle Zuordnungen. Wird das Feld von einem älteren Client weggelassen, bleiben vorhandene Barcodes erhalten.
- `GET /barcodes/{barcode}`: `{barcode, source: "manual"|"off", food: <eigene Definition>|null}`. Keine OFF-Netzabfrage; liefert nur lokale Priorität/Basis.
- Normales `POST /entries` mit `type: "barcode"` und `barcode` verwendet automatisch einen lokalen Treffer und speichert eine manuelle Momentaufnahme. Das gilt ebenfalls für Barcode-Verarbeitung aus Importen. Ohne lokalen Treffer folgt OFF. Bestehende gespeicherte OFF-Snapshots bleiben beim Nachbearbeiten/Refresh auf ihrer Quelle.
- `POST /manual-ingredients/scan-label`: Bildbytes; optional `?reference_amount=6&reference_unit=g` (oder `ml`). Vorschau enthält auf `100g`/`100ml` normalisierte Nährwerte, `basis_unit` und `reference_amount`. Ohne bestätigte Menge gilt die bisherige eindeutige 100-g-Erkennung. `reference_unit` allein ändert diese Basis nicht.

Kein API-Aufruf darf aus einem echten Barcode eine Zahl ohne führende Nullen machen; Barcodes bleiben Strings. Konflikte ergeben 409, ungültige Codes/Referenzmengen 422. Ein OCR-Fehler verändert keine gespeicherte Definition.

## English

Under **Manual**, foods can have up to 50 unique barcode strings. Type one per line or photograph a barcode, then save the food. A barcode can belong to only one manual food; collisions are rejected. Remove it from its old food before assigning it elsewhere.

Normal meal/recipe barcode capture now prefers your manual database and uses its stored nutrients/basis without contacting Open Food Facts. If no local mapping exists, OFF remains the fallback. Per-100-ml foods use ml; there is no density conversion. Explicit **Barcode → BLS** remains separate. Old entries retain their own snapshots, even after a link is removed. Refreshing an existing OFF entry still refreshes OFF, not a new local mapping.

**Photograph nutrition label / Upload label image** reads the label on your server. Barcode and name are retained. Review all suggestions and save; scanning itself creates no food or meal. If editing a saved food, OCR stays in that editor rather than silently creating another food.

Leave the OCR reference amount blank for a clear per-100-g column. For a known per-tablet/serving basis enter the confirmed amount, e.g. **6 g**; for a per-100-ml label enter **100 ml**. Friss normalizes to the chosen 100-g/100-ml basis. Example: 80 mg vitamin C per 6-g tablet becomes 1,333.33 mg per 100 g, so logging 6 g contributes 80 mg. No tablet weight or density is inferred.

Ambiguous columns, conflicting fixed bases and US total-carbohydrate labels are not guessed. Missing values remain blank and OCR requires human checking. Recognized text/reference information stays in notes; scan image files are processed but not archived by this OCR flow.

The existing manual-food create/update APIs accept `barcodes`. Omitted barcodes on update are preserved; explicit empty list removes them. `GET /barcodes/{code}` exposes local matching without a remote request. `POST /manual-ingredients/scan-label?reference_amount=6&reference_unit=g` accepts image bytes and returns a review-only normalized draft. All endpoints require authentication. Manual barcode links are included automatically in existing JSON/ZIP backups.
