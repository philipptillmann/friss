# Rezepte als Zutaten · Nested recipes · v1.45.0

## Deutsch

Ein gespeichertes Lebensmittel- oder Getränkerezept kann als Zutat eines anderen Rezepts verwendet werden. Mehrere Stufen sind möglich, etwa **Tomatensauce → Bolognese → Lasagne**. Ein Rezept darf weder direkt noch indirekt sich selbst enthalten. Die maximale Verschachtelungstiefe beträgt acht Rezeptstufen.

### Hinzufügen

1. Unterrezept anlegen und alle Lebensmittel/Mengen vervollständigen.
2. Übergeordnetes Rezept unter **Rezepte** oder **Getränke** auswählen.
3. Bei den Zutaten entweder gemeinsam nach dem Unterrezept suchen oder **Rezept als Zutat / Getränk als Zutat** auswählen.
4. Verwendete Menge für das **ganze übergeordnete Rezept** angeben und speichern. Das aktuell bearbeitete Rezept wird nicht als eigene Zutat angeboten; indirekte Kreise prüft der Server.

| Mengenangabe für das Unterrezept | Voraussetzung | Beispiel |
| --- | --- | --- |
| Portionen | Gesamt-Portionszahl des Unterrezepts | 2 von 8 Portionen = 25 % |
| Anteil | Kein Gewicht/Volumen nötig | 0,25 = ein Viertel |
| Gramm | Fertiges Gesamtgewicht des Unterrezepts | 150 g von 600 g = 25 % |
| Milliliter | Gesamtvolumen des Unterrezepts | 100 ml von 400 ml = 25 % |

Portionen und Anteile funktionieren ausdrücklich **ohne Gesamtgewicht**. Die Summe der Zutatengewichte wird nicht als fertiges Gewicht angenommen. Einheiten werden nicht über unbekannte Dichten ineinander umgerechnet. Das Gewicht des übergeordneten fertigen Gerichts ist für dessen späteren Gramm-Verzehr separat nötig.

### Nährwerte, Bearbeitung und Verzehr

Nährwerte, Koffein, separat erfasstes Wasser und Alkohol des Unterrezepts werden anteilig übernommen. Fehlende Angaben und Null-Annahmen folgen den bestehenden Regeln. Zutaten sind kein eigener Tagesverzehr und werden nicht separat nach Health exportiert. Erst das Essen des übergeordneten Rezepts zählt zum Tagebuch.

In der Zutatenliste eine Rezeptzutat öffnen und in den Details ihre Menge ändern. Die vorhandene Einheit bleibt erhalten; die gespeicherten Nährwerte werden entsprechend skaliert. Für eine andere Einheit die Zutat entfernen und neu mit der gewünschten Einheit hinzufügen. Ein bloßes Entfernen einer Zutat aus dem Rezept verändert keine bereits gebuchten Portionen.

Jede Rezeptzutat speichert eine **Momentaufnahme** des verwendeten Unterrezepts einschließlich seiner Unterzutaten. Spätere Änderungen am Unterrezept ändern weder das übergeordnete Rezept noch alte Verzehre automatisch. Für den neuesten Unterrezeptstand die alte Zutat entfernen und neu hinzufügen. Bei anschließendem Speichern des übergeordneten Rezepts gilt wie bisher:

- **Nur Zukunft:** bereits gebuchte Portionen bleiben unverändert.
- **Bisherige Einträge korrigieren:** direkte Buchungen dieses übergeordneten Rezepts werden mit seinem aktuellen Zutatenstand neu berechnet. Andere Rezepte, die dieses wiederum als eingefrorene Zutat verwenden, bleiben unverändert.

Die ausdrücklich gewählte rückwirkende Korrektur einer **manuellen Lebensmitteldefinition** erreicht dagegen auch deren Verwendungen innerhalb verschachtelter Momentaufnahmen. Andere Zutaten, damalige Portionenzahl und Gesamtgewicht/Volumen bleiben erhalten. Aktive Health-Exporte blockieren betroffene Korrekturen. Apple-Health-Daten auf dem iPhone werden weiterhin nicht automatisch korrigiert.

### Essensplanung, Einkauf und Sicherung

Die Einkaufsliste löst Unterrezepte rekursiv bis auf ihre Lebensmittel auf und skaliert jede Stufe mit dem jeweiligen Anteil. Passender Vorrat wird danach wie bisher einmal je Lebensmittel/Einheit abgezogen. Gespeicherte Pläne bleiben eigene Momentaufnahmen. Die vorhandene ZIP-Sicherung enthält Rezeptzutaten, verschachtelte Momentaufnahmen und Originale automatisch; es gibt keine zusätzliche Datenbanktabelle.

### API

Authentifiziertes `POST /recipes/{parent_recipe_id}/ingredients/recipe`:

```json
{
  "id": "15c4dc23-303d-4b3f-af12-10aff99f1f37",
  "recipe_id": "e06bde17-c6e6-4dcb-9370-4cfca5ff8f96",
  "timestamp": "2026-11-24T12:30:00+01:00",
  "unit": "portion",
  "amount": 2
}
```

UUIDs durch eigene Eintrags-ID beziehungsweise vorhandene Rezept-IDs ersetzen. Die Pfad-ID ist das übergeordnete Rezept, `recipe_id` im Body das Unterrezept. `unit`: `portion`, `fraction`, `g`, `ml`; Anteil höchstens 1. Der Zeitstempel benötigt eine Zeitzone. Die Antwort ist eine normale Rezeptbuchung mit `recipe_id` als Zutatenziel und eingefrorenem `recipe_snapshot`. HTTP 201 bedeutet gespeichert; gleiche ID/Inhalt lässt sich ohne Duplikat wiederholen, abweichender Inhalt mit gleicher ID ergibt 409. Selbstverweise, Kreise, zu große Tiefe und fehlendes Gewicht/Volumen werden abgelehnt. Unvollständige Unterrezepte müssen zuerst ergänzt werden.

Mengenänderung: vorhandenes `PATCH /entries/{id}/amount` mit aktueller `revision` und `quantity: {value, unit}`. Entfernen: vorhandenes `DELETE /entries/{id}`. `POST /recipes/{id}/intake` bleibt die API für tatsächlichen Tagebuchverzehr, nicht zum Anlegen einer Rezeptzutat.

## English

Saved food/drink recipes can now be ingredients of other recipes, for example **tomato sauce → bolognese → lasagne**. Select the parent under Recipes/Drinks, search for a saved recipe in ingredient capture or choose **Recipe as ingredient / Drink as ingredient**, then enter the amount used in the **whole parent recipe**.

- **Portions:** consumed portions divided by the child's total portions; no finished weight needed.
- **Fraction:** e.g. 0.25 of the child; no weight/volume needed.
- **Grams:** require the child's finished total weight.
- **Milliliters:** require its total volume.

No inferred ingredient-weight total or mass/volume conversion is used. Complete the child's ingredients before adding it. Self references, indirect cycles and nesting beyond eight recipe levels are rejected.

All nutrients, caffeine, explicitly tracked drinking water and alcohol scale with the fraction. Recipe ingredients do not count as diary consumption or separate Health exports. Open an ingredient's details to edit its amount in the same unit. For a different unit, remove and re-add it.

The child and its ingredients are frozen at insertion. Later child edits do not automatically change the parent or previously logged portions. Remove/re-add the child ingredient to use its latest state. Parent **future-only** saving retains old diary meals; **amend existing entries** recalculates that parent's direct logged meals from its current definition. Other recipes holding older snapshots are not automatically changed.

Explicit amendment of a manual-food definition does recurse into nested historical snapshots containing that food, preserving other ingredients and original recipe parameters. Health corrections on iPhone remain separate and active exports block affected changes.

Shopping lists recursively expand child recipes to base foods before subtracting stock. Meal plans stay frozen. Existing ZIP backups include all nested data automatically.

API: `POST /recipes/{parent}/ingredients/recipe` with a new ingredient `id`, child `recipe_id`, timezone-aware `timestamp`, `unit` and `amount` (example above). Identical retries are safe; different data under the same ID conflicts. Use the existing entry amount endpoint to edit quantity and DELETE to remove an ingredient. The existing recipe `/intake` endpoint continues to log actual diary consumption.
