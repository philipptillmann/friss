# OCR: recognized text but no imported nutrients · v1.47.1

## English

Recognizing letters is separate from interpreting nutrition values. Friss can read a photo yet import nothing if the reference amount is missing/ambiguous, units cannot be read, columns conflict or the table uses unsupported US carbohydrate conventions. It now explains the reason and lets you correct/reprocess the text without another upload.

### Recover a failed import

1. Look at the message below the scan buttons. If no nutrients were accepted, **Recognized text** opens automatically.
2. Confirm the label's reference amount above the photo buttons. If the package says per 100 g but OCR missed that header, enter **100** and select **g**. For a known per-tablet 6-g basis use **6 g** instead; do not guess the basis.
3. In **Compare with the label and correct the text**, repair OCR errors only after checking the package. For example, `Fett 6,69` has no recognized unit; Friss cannot know whether the final 9 was a misread `g`. Likewise, it cannot infer whether `21 g` was originally `2,1 g`. Add/correct units and decimal points explicitly from the source.
4. Press **Reprocess text**. Only the recognized/corrected text and confirmed reference are sent; no new photo or OCR run is needed. A partial result shows how many nutrient suggestions were accepted and explains skipped values.
5. Review the nutrient fields and save the food when correct. Name, barcodes and existing editor identity are retained. Parsing itself creates no food or diary entry. Original OCR and corrected text are retained in notes when suggestions are applied.

`<`, `>`, and similar bounds remain unknown rather than being imported as exact values. Missing units, multiple number/unit columns, conflicting declarations and impossible mass values are left blank. A confirmed serving basis cannot override a conflicting printed 100-g/ml column. US total carbohydrates still require manual review.

When energy is printed on separate kJ and kcal lines, explicit **kcal takes priority**. Previously those lines could incorrectly conflict, especially when the kJ line contained a thousands separator. For the reported text `Energie [kj] 1.273 kJ` / `Energie [kcal] 302 kcal`, the recognized energy is now **302 kcal**, not an inferred conversion of `1.273`.

### Text preview API

Authenticated `POST /manual-ingredients/parse-label`:

```json
{
  "text": "Energie [kj] 1.273 kJ\nEnergie [kcal] 302 kcal\nKohlenhydrate 50 g",
  "reference_amount": 100,
  "reference_unit": "g"
}
```

Returns the same review-only draft structure as photo OCR: `text`, `basis`, normalized `nutrients`, `warnings`, `issues`, and confirmed basis fields when accepted. No data is written. Text is limited to 30,000 characters. Reference parameters follow existing OCR rules; absent reference requires an unambiguous supported header. The image endpoint also returns `issues` now.

Issue codes:

| Code | Meaning |
| --- | --- |
| `reference_required` | Confirm the missing/ambiguous reference amount. |
| `reference_conflict` | Confirmed reference disagrees with a fixed detected column. |
| `us_label` | US Nutrition Facts/total carbohydrates need manual review. |
| `ambiguous_or_missing_units` | A supported row has multiple values or no clear unit. |
| `qualifier_values` | Bounds such as < or > are not exact quantities. |
| `conflicting_values` | Different declarations of one nutrient conflict. |
| `implausible_mass` | A macro amount exceeds its stated reference mass. |
| `no_supported_values` | No usable supported nutrient could be extracted. |

## Deutsch

Texterkennung und Nährwertzuordnung sind zwei Schritte. Lesbarer Text allein reicht nicht, wenn die Bezugsmenge fehlt oder Werte/Einheiten unklar sind. Friss erklärt jetzt die Ursache und erlaubt eine erneute Textauswertung ohne neues Foto.

1. Bei fehlgeschlagener Übernahme öffnet sich **Erkannter Text** automatisch.
2. Oben die tatsächliche Bezugsmenge bestätigen: beispielsweise **100 g**, wenn dieser Tabellenkopf auf dem Etikett stand, aber nicht erkannt wurde. Bei einer bekannten 6-g-Tablette entsprechend **6 g** wählen.
3. Im bearbeitbaren Textfeld OCR-Fehler nach Vergleich mit der Verpackung korrigieren. `Fett 6,69` enthält keine erkannte Einheit; ein `9` wird nicht als `g` geraten. Auch aus `21 g` wird nicht automatisch `2,1 g`.
4. **Text erneut auswerten** wählen. Es wird kein Foto erneut hochgeladen. Teilweise erkannte Daten werden mit Anzahl und Hinweisen auf ausgelassene Angaben angezeigt.
5. Nährwertfelder prüfen und ausdrücklich speichern. Name, Barcodes und Bearbeitungsmodus bleiben erhalten. Auswertung allein speichert nichts; Original-OCR und korrigierter Text bleiben bei Übernahme in den Notizen.

Angaben mit `<` oder `>` bleiben unbekannt; fehlende Einheiten, widersprüchliche Werte und mehrdeutige Spalten werden nicht geraten. Gedruckte kJ- und kcal-Zeilen gelten nicht mehr als zwei konkurrierende Energiewerte: ausdrücklich erkannte kcal haben Vorrang. Im gemeldeten Beispiel werden **302 kcal** übernommen, sobald die 100-g-Basis bestätigt ist.

Die API oben liefert strukturierte Fehlerhinweise (`issues`) und eine rein lesende Vorschau. Es werden keine Lebensmittel, Mahlzeiten oder Health-Werte angelegt, bevor du sie regulär speicherst.
