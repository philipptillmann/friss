# Open Food Facts vitamins and minerals · v1.46.1

## English

Friss now imports the available Open Food Facts fields for all currently supported HealthKit nutrition identifiers, including vitamins A, B1, B2, B3/niacin, B5, B6, B7/biotin, B12, C, D, E, K and folate; calcium, chloride, iron, magnesium, phosphorus, potassium, sodium, zinc, chromium, copper, iodine, manganese, molybdenum and selenium; cholesterol and mono-/polyunsaturated fats; plus the previously supported energy, macros, caffeine and food water when present. This does not create nutrients absent from the source.

The previous importer only copied calories/macros, sodium and caffeine. That caused missing vitamins for products such as **4316268448871 — Multivitamin + Mineralstoffe** even though OFF supplied them.

### Existing entries

Update Friss, open the entry and choose **Refresh from Open Food Facts**. This works even without a red exclamation. The entry is recalculated with its retained amount; previous data is archived. New barcode entries automatically use the expanded mapping. Older snapshots are not silently enriched merely by viewing Home/statistics/details: source mapping versioning preserves their historical interpretation until an explicit refresh/reprocessing. Existing Health export files remain unchanged; follow the existing Health correction process if previously exported.

For recipe ingredients, refresh the ingredient. Already logged recipe portions, frozen parent recipes and planned meals keep their snapshots; use the existing explicit correction workflow as needed. No re-entry, new barcode link or separate AI analysis is necessary for an ordinary OFF entry.

### Values and units

OFF's normalized mass values in `*_100g` are grams. The accompanying `*_unit`/`*_value` may describe the original label input in mg or µg and must not be applied to the normalized number again. Friss converts supported small mass nutrients to explicit mg/µg for display/storage, then scales by consumed grams ÷ 100. It reads `*_100g`, not a mix of per-serving and per-100-g values. Zero stays known zero; missing/null stays unknown unless the existing zero-assumption setting is enabled. Folate variants are not added together: `folates` has priority, with `vitamin-b9` as fallback only if absent/null.

As retrieved on 26 November 2026, the specified supplement's OFF record declares **per 100 g**:

| Nutrient | Value |
| --- | --- |
| Vitamin C | 80 mg |
| Vitamin E | 12 mg |
| B3 / niacin | 16 mg |
| B5 / pantothenic acid | 6 mg |
| B7 / biotin | 50 µg |
| Calcium | 200 mg |
| Magnesium | 112.5 mg |
| Phosphorus | 105 mg |
| Potassium | 300 mg |

These are the database's published amounts, **not an assumed tablet/daily-dose amount**. Enter the consumed weight; for example, 2 g contributes 1.6 mg vitamin C and 1 µg biotin from this record. Verify that OFF's reference basis matches the package label if you entered data there. Friss does not infer tablet weight or supplement dosage. The captured API response is retained as a regression fixture at `tests/fixtures/off-4316268448871.json`.

Sources: [product API](https://world.openfoodfacts.org/api/v2/product/4316268448871.json), [OFF nutrient taxonomy](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/taxonomies/nutrients.txt), [OFF normalization implementation](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/lib/ProductOpener/Nutrition.pm). Data supplied by Open Food Facts contributors; availability and values can change.

## Deutsch

Friss übernimmt jetzt die vorhandenen OFF-Felder für alle derzeit unterstützten HealthKit-Ernährungswerte: insbesondere Vitamine, Mineralstoffe/Spurenelemente sowie Cholesterin und einfach/mehrfach ungesättigte Fette zusätzlich zu den bisherigen Hauptwerten. Fehlende Quellenwerte werden nicht erfunden.

Die bisherige Zuordnung enthielt nur Kalorien/Makros, Natrium und Koffein. Deshalb fehlten beispielsweise bei **4316268448871 — Multivitamin + Mineralstoffe** Vitamine trotz vorhandener OFF-Daten.

Nach dem Update bestehenden Eintrag öffnen und **Aus Open Food Facts aktualisieren** wählen, auch wenn kein rotes Ausrufezeichen angezeigt wird. Neue OFF-Einträge verwenden die erweiterte Zuordnung automatisch. Alte Momentaufnahmen bleiben bis zur ausdrücklichen Aktualisierung/Nachbearbeitung unverändert; bloßes Anzeigen ergänzt sie nicht stillschweigend. Health-Dateien werden nicht überschrieben. Rezeptzutaten gezielt aktualisieren; bereits gebuchte Portionen, eingefrorene Unterrezepte und Pläne bei Bedarf über die vorhandenen Korrekturabläufe bearbeiten.

OFF liefert normalisierte `*_100g`-Massen in Gramm, auch wenn die ursprüngliche Eingabeeinheit mg/µg war. Friss wendet diese Eingabeeinheit nicht nochmals an, sondern rechnet kleine Nährstoffmengen in mg/µg um und skaliert dann mit Verzehrgramm ÷ 100. Angaben pro Portion werden nicht zusätzlich addiert. Bekannte Nullwerte bleiben null, fehlende Werte unbekannt; die vorhandene Null-Annahme-Einstellung bleibt maßgeblich. Folat-Felder werden nicht doppelt gezählt.

Die Tabelle oben zeigt die am 26. November 2026 veröffentlichten Werte dieses Produkts **pro 100 g**, nicht automatisch pro Tablette oder Tagesdosis. Beispielsweise ergeben 2 g daraus 1,6 mg Vitamin C und 1 µg Biotin. Tatsächlich verzehrtes Gewicht verwenden und gegebenenfalls Bezugsmenge bei OFF mit der Verpackung vergleichen. Tablettengewicht und Dosierung werden nicht geschätzt. Quelle, Normalisierung und Originalantwort für Regressionstests sind oben verlinkt.
