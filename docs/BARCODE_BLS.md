# Barcode → BLS · v1.44.0

## English

**Barcode → BLS** is a separate capture method under **Meals** and in recipe/drink ingredient capture. The existing **Barcode** method continues to use Open Food Facts. The new mode uses your explicitly chosen BLS substitute and does not contact Open Food Facts.

1. Choose **Barcode → BLS**.
2. Photograph the barcode with the existing camera picker, or type its number (8–14 digits, keeping leading zeros).
3. If a link exists, the BLS food name/code appears. Enter the consumed/ingredient quantity **in grams** and save normally.
4. For a new barcode, Friss opens the linking area. Search BLS, select a result, then choose **Save barcode link**. No result is guessed or automatically accepted.
5. Now enter the amount and save the meal or recipe ingredient. The link is remembered for future scans on this server, including recipe ingredients. Saving the link itself does not record consumption.

Choose an appropriate food/preparation/fat level. BLS describes the chosen food, not necessarily the packaged product's actual composition. Micronutrients are available only where the BLS record supplies them; missing values remain subject to the normal missing-data policy. Product volume is not assumed to equal grams.

Use **Change link** to choose another BLS food, or **Remove link** after confirmation. This affects future capture only. Existing meals, ingredients and recipe snapshots retain their BLS code/data; link removal does not break later amount completion. Missing quantities can still be saved for review after the food is linked.

The resulting entry has a **BLS** source tag and retains the scanned barcode. Details identify its capture method as Barcode → BLS. No OFF nutrients are merged or double-counted. Editing an existing entry's food is not the same as changing its global barcode link.

If another device changes the link while you are entering the meal, Friss rejects the stale mapping instead of silently using a different food. Check the newly loaded link and save again. If the target was removed from the BLS database, link it to an available food first.

### API

Use the existing Friss authentication. All barcode paths preserve leading zeros.

- `GET /barcode-bls/{barcode}?lang=de`: `{barcode, version, linked, bls_code, food}`. `food` contains BLS code and German/English names. Unlinked barcodes return `linked: false`; the version may be nonzero after removal.
- `PUT /barcode-bls/{barcode}`: JSON `{"version":0,"bls_code":"REAL_BLS_CODE"}` for a new link. Use the current version returned by GET when changing/recreating it. The BLS code must exist. Identical save retries return the same link.
- `DELETE /barcode-bls/{barcode}?version=N`: removes the link for future entries, retains its version history for concurrency checks.
- `POST /entries`: use the normal entry format, with `type: "barcode_bls"`, `barcode`, timestamp with timezone and optional gram quantity. The server resolves the link; do not supply a guessed BLS code. Unknown/unavailable links return HTTP 409 **before writing an entry**.

Example entry after linking (replace UUID with a fresh client-generated entry ID, as required by the existing `/entries` API):

```json
{
  "id": "bd053a04-e431-41cc-afc2-1232f0171d63",
  "type": "barcode_bls",
  "barcode": "0123456789012",
  "barcode_bls_version": 1,
  "timestamp": "2026-11-11T12:30:00+01:00",
  "quantity": {"value": 150, "unit": "g"}
}
```

`barcode_bls_version` is optional for API clients but recommended: it rejects changes since the lookup. The browser uses it. Add `recipe_id` to record an ingredient instead of diary consumption. `quantity: null` retains a linked item for review. Normal entry retry rules apply: the same ID/content returns the saved entry even if the link subsequently changes; changing the request under the same ID conflicts.

Links are private to your Friss server and shared by its clients; they are not submitted to BLS or Open Food Facts. ZIP backups include the link table. Older archives restore an empty link collection. Restore archives containing links with Friss v1.44.0 or newer.

## Deutsch

**Barcode → BLS** ist eine zusätzliche Erfassungsart unter **Mahlzeiten** und bei Rezept-/Getränkezutaten. **Barcode** verwendet weiterhin Open Food Facts. Der neue Modus nutzt deine ausdrücklich gewählte BLS-Zuordnung ohne OFF-Abfrage.

1. **Barcode → BLS** wählen und Barcode fotografieren oder Nummer eingeben (8–14 Ziffern, führende Nullen erhalten).
2. Eine vorhandene Verknüpfung zeigt das BLS-Lebensmittel. Menge **in Gramm** eingeben und speichern.
3. Bei unbekanntem Barcode erscheint die Zuordnungsmaske: BLS durchsuchen, Treffer bewusst auswählen und **Barcode verknüpfen** wählen. Es wird nichts automatisch geraten.
4. Danach die Mahlzeit beziehungsweise Zutat speichern. Die Zuordnung bleibt für künftige Scans auf diesem Server erhalten. Verknüpfen allein bucht keinen Verzehr.

Passendes Lebensmittel, Zubereitung und Fettstufe auswählen. BLS-Werte beschreiben den gewählten Ersatz, nicht zwingend das konkrete verpackte Produkt. Fehlende Mikronährstoffe werden nicht erfunden. Milliliter werden nicht pauschal in Gramm umgerechnet.

**Verknüpfung ändern/entfernen** beeinflusst nur künftige Erfassungen. Bestehende Mahlzeiten, Rezeptzutaten und Rezeptmomentaufnahmen behalten ihren BLS-Stand. Auch nach Entfernen der Zuordnung lassen sich alte Mengen ergänzen. Nach Zuordnung darf die Menge zunächst leer bleiben und später nachbearbeitet werden.

Einträge tragen den Quellen-Tag **BLS**, behalten die Barcodenummer und zeigen in den Details Barcode → BLS als Erfassungsart. OFF-Nährwerte werden nicht addiert. Eine individuelle Lebensmittelkorrektur verändert keine globale Barcode-Zuordnung.

Ändert ein anderes Gerät die Zuordnung während der Eingabe, wird die alte Auswahl abgelehnt und die aktuelle Verknüpfung neu geladen. Prüfen und erneut speichern. Ein nicht mehr verfügbares BLS-Ziel muss zuerst ersetzt werden.

Die API oben verwendet die normale Authentifizierung, aktuelle Versionsnummern und bei `/entries` die vorhandene clientseitige UUID. Ein unbekannter Barcode wird vor dem Anlegen abgelehnt. `recipe_id` macht daraus eine Rezeptzutat. Identische Wiederholungen eines gespeicherten Eintrags verwenden dessen alten Stand, auch wenn die Zuordnung inzwischen geändert wurde.

Zuordnungen gelten auf deinem Server, nicht in öffentlichen Datenbanken. ZIP-Sicherungen enthalten sie; alte Sicherungen ergeben eine leere Zuordnungssammlung. Neue Archive mit Friss 1.44.0 oder neuer wiederherstellen.
