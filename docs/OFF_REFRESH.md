# Open Food Facts: empty nutrition warning and refresh · v1.46.0

## English

A red **!** appears immediately after the **Open Food Facts** source label in the meal/recipe-ingredient list, entry details and daily audit when the original product profile has no positive known nutritional values per 100 g: the values are absent, invalid or all zero. Hover or focus the button to read its explanation. The warning checks the saved source profile, not rounded portions or assumed zeros from Settings. A zero-energy product with another positive nutrient does not trigger it. Nutrition scores are not treated as nutrients.

This is a prompt to check the product, not proof that zeros are wrong: genuinely zero-valued products can also show it. Friss does not invent replacement calories or change your missing-value policy.

### Update a product after editing Open Food Facts

1. Correct the product in Open Food Facts as usual, making sure the barcode matches your entry.
2. In Friss tap the red **!** beside the source label. Confirm that you want to fetch current Open Food Facts data.
3. Alternatively, open the entry and choose **Refresh from Open Food Facts**. This button is available for direct OFF entries even if they have positive values and no warning.
4. Friss fetches the product again and recalculates **only this entry**, using its retained amount. The food name can also update. If the new profile contains positive values, the warning disappears; if still missing/all zero, it remains and can be retried later.

Timestamp, amount, barcode, photos, original input and Health/export records remain. The previous entry revision is archived before a change. Identical returned data does not create another revision. A failed lookup, missing product or malformed response leaves the saved entry unchanged. Concurrent edits require reloading rather than overwriting the newer state. A missing amount can remain unresolved even after its product data is refreshed.

Recipe ingredients can be refreshed. The current recipe totals then use the refreshed ingredient; already logged recipe portions, frozen parent-recipe ingredients and meal plans retain their old snapshots. To correct already logged consumption, use the existing explicit recipe-history correction workflow. Other uses of the same barcode are not automatically updated.

Prepared daily exports and active individual Health claims block refresh until finished/reviewed. Already confirmed Health samples/export files are never rewritten. If a refreshed diary entry was previously exported, Friss warns that Health needs separate review/correction and the existing daily-export change detection applies. Do not blindly export again.

Barcode → BLS entries, manual foods, AI-nutrient entries and recipe consumption snapshots are not refreshed from OFF. Their respective editing methods remain available. OFF search/indexing or server caching may take time to expose edits; Friss cannot force Open Food Facts to publish a change immediately.

### API

Authenticated `POST /entries/{id}/refresh-off`, JSON body:

```json
{"revision": 1}
```

Use the entry's current revision from `GET /entries/{id}` or `/details`. Returns:

```json
{
  "entry": {"id": "ENTRY_ID", "revision": 2, "off_nutrition_empty": false},
  "changed": true,
  "health_correction_required": false
}
```

`entry` above is abbreviated; the real response includes the retained entry and fresh food/nutrients. `409`: stale revision/concurrent change/active export. `422`: entry is not a direct OFF food. `502`: product unavailable/not found/invalid; no saved changes. `401`: authentication required. Normal entry/detail and recipe-ingredient responses include the derived `off_nutrition_empty` flag for OFF entries. No new database table or backup format is needed; archives include the updated records and revision originals.

## Deutsch

Ein rotes **!** steht hinter dem Quellen-Tag **Open Food Facts**, wenn im gespeicherten Originalprofil keine positiven bekannten Nährwerte pro 100 g vorhanden sind: Angaben fehlen, sind ungültig oder alle null. Es erscheint in Mahlzeiten-/Rezeptzutatenliste, Details und Tagesprüfung. Tooltip/Fokus erklärt den Hinweis. Geprüft wird die Quelle, nicht die gerundete Verzehrmenge oder eine Nullannahme aus Einstellungen. Null Kalorien allein reichen nicht, wenn ein anderer Nährwert positiv ist. Nährwert-Scores werden ignoriert.

Der Hinweis ist keine Feststellung, dass Nullwerte falsch sind; auch tatsächlich nährwertfreie Produkte können ihn zeigen. Es werden keine Ersatzkalorien erfunden.

### Nach Ergänzung bei Open Food Facts

1. Produktdaten bei Open Food Facts mit derselben Barcodenummer ergänzen.
2. In Friss auf **!** tippen und die Aktualisierung bestätigen.
3. Alternativ Eintrag öffnen und **Aus Open Food Facts aktualisieren** wählen. Dieser Button ist auch bei normalen OFF-Einträgen ohne Warnung verfügbar.
4. Friss lädt erneut und berechnet **nur diesen Eintrag** anhand seiner gespeicherten Menge. Name und Nährwerte werden aktualisiert. Bei positiven Quelldaten verschwindet die Warnung; bleibt alles leer/null, bleibt sie zum späteren Wiederholen stehen.

Zeitpunkt, Menge, Barcode, Fotos, Originaleingabe und Health-Nachweise bleiben erhalten. Der alte Stand wird bei Änderungen als Revision archiviert. Gleiche Daten erzeugen keine neue Revision. Bei Ausfall, unbekanntem Produkt oder ungültiger Antwort bleiben die alten Daten unverändert. Gleichzeitige Änderungen werden nicht überschrieben. Eine fehlende Menge muss weiterhin ergänzt werden.

Bei einer Rezeptzutat aktualisieren sich die aktuellen Rezeptwerte. Schon gebuchte Portionen, eingefrorene Unterrezepte und gespeicherte Pläne bleiben unverändert; gegebenenfalls den vorhandenen ausdrücklichen Korrekturablauf verwenden. Andere Verwendungen desselben Barcodes werden nicht automatisch geändert.

Vorbereitete Tagesexporte und laufende Health-Reservierungen blockieren die Aktualisierung. Bereits auf dem iPhone gespeicherte Health-Werte und Exportdateien werden nicht überschrieben. Bei betroffenen alten Exporten Health separat prüfen/korrigieren; erneuter Export kann sonst doppelte Werte verursachen.

Barcode → BLS, eigene Lebensmittel, KI-Nährwertimporte und gebuchte Rezeptmomentaufnahmen nutzen diesen OFF-Refresh nicht. Veröffentlichung beziehungsweise Caches bei Open Food Facts können Aktualisierungen verzögern.

API: `POST /entries/{id}/refresh-off` mit aktueller `revision`, normale Authentifizierung. Felder, Rückgaben und Fehlercodes stehen oben. Die abgeleitete Kennzeichnung lautet `off_nutrition_empty`. Vorhandene Sicherungen enthalten die aktualisierten Daten und Revisionsoriginale ohne Schemaänderung.
