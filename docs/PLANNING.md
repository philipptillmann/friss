# Meal planning, fridge inventory and shopping · v1.42.0

## English

Three new pages are available: **Meal planner**, **Fridge** and **Shopping list**. In **Settings → Planning and inventory**, meal planning and fridge inventory each have an independent on/off switch. Both start enabled. Disabling hides the corresponding page, prevents its operations and keeps its records. Shopping remains available: with planning off it contains manual items only; with inventory off no stock is subtracted. Re-enable to recover your records. Features are server-wide, like other Friss settings.

### Plan and prepare

1. First create and complete a recipe or drink using the existing recipe editors.
2. Open Meal planner, choose a date, recipe, amount/unit and optional meal slot and notes. Save.
3. Use portions, fraction, grams or ml, following existing recipe rules. Grams require finished weight; ml requires total volume. Portion/fraction planning does not need a weight.
4. Use the date range to inspect upcoming meals. Edit an item to reschedule it, change its amount, or mark it **Prepared**. Recipe notes/instructions retained in the snapshot can be expanded on its card.
5. Only when consumed, choose the actual eating time and **Mark eaten**, then confirm. One normal recipe diary entry is created, with nutrients and Health pending. Repeated clicks do not log twice. Planned/prepared meals alone never affect Home, statistics, BAC or Health.

A plan stores the recipe version at planning time. Editing its schedule/amount retains that version; switching to another recipe captures that recipe. To use a newer version of the same recipe, delete and recreate the pending plan. A later recipe correction does not change the plan. Once eaten, edit/correct the diary entry instead of the plan. Deleting a plan does not delete its logged meal. Deleting the logged meal does not reset its plan to uneaten; create a new plan for another consumption.

### Maintain fridge stock

Enter a name, amount and g/ml/piece unit, optional best-before/use-by date and notes. To subtract stock reliably, **Find food** and choose the same BLS code, manual-food ID or Open Food Facts barcode used by the recipe ingredient. A similar product name is not enough. Editing a name clears the linked reference; reselect the food if needed. Free-text items match other free-text ingredients only by their normalized exact name and unit.

Edit quantities or delete rows as stock is used. Multiple batches of the same food/unit are summed. Stock expiring before the selected planning range begins is excluded; later dates are not a guarantee of usability throughout the range. The dates are reminders, not food-safety advice. There is no automatic stock reservation or consumption deduction.

### Shop

Choose a start/end date (up to 366 days). The generated list combines ingredients from all **uneaten** plans in that range, using their snapshots and consumed fractions. Shared ingredients are summed, then matching stock is subtracted **once across the range**. Required, in-stock and to-buy amounts are displayed, including fully covered ingredients with zero to buy. Grams and ml are never interchanged, nor are different database IDs treated as identical.

Add/edit/delete manual shopping items for other purchases. They are independent of the range and are not reduced by fridge stock. Check off purchases; checkboxes persist. For generated rows, changed requirements, stock or date range give a fresh checkbox state. Checking does not add inventory or log nutrition. Bought stock must be entered explicitly. Drinking water additions are not automatic shopping items; pure caffeine/alcohol additions require manual purchases and produce a warning.

**Important:** stock is maintained manually in this release. Neither marking a meal eaten nor checking a purchase changes stock. Once a meal is eaten it leaves the generated requirements, so update stock as appropriate before relying on remaining plans. Lists for different date ranges are separate calculations, not inventory reservations.

### Backups and API

New records, toggles, recipe snapshots and shopping checks are included in downloadable Friss ZIP backups. Older backups restore with an empty planning collection; use v1.42.0 or newer to restore a backup containing the new table. Existing recipe/diary data is unchanged.

Authenticated endpoints:

- `GET/PUT /planning/settings`: version, planning_enabled, inventory_enabled.
- `GET /planning/meals?start=YYYY-MM-DD&end=YYYY-MM-DD`.
- `PUT /planning/meals/{uuid}`: version (0 for new), day, recipe_id, amount, unit, slot, notes, prepared.
- `POST /planning/meals/{uuid}/eat`: timestamp with timezone, optional finished_at. Safe repeat returns the original entry_id.
- `GET /planning/inventory`; `PUT /planning/inventory/{uuid}`: version, name, source (`bls|manual|off|text`), source_id, amount, unit (`g|ml|piece`), expires, notes.
- `GET /planning/shopping?start=…&end=…`; `PUT /planning/shopping/{uuid}` for manual items, same fields plus checked.
- `PUT /planning/check/{generated-id}`: checked, start, end. Stale generated rows are rejected.
- `DELETE /planning/{meals|inventory|shopping}/{uuid}?version=N`.

Updates use optimistic versions; reload on conflicts. UUIDs identify editable rows. Identical save retries at the same version/content return the existing row rather than duplicating it. Disabled features return a conflict for their operations; saved data remains. Existing API auth applies. No AI provider is involved in planning or shopping calculations.

## Deutsch

Drei neue Seiten: **Essensplanung**, **Vorrat** und **Einkaufsliste**. Unter **Einstellungen → Planung und Vorrat** lassen sich Essensplanung und Vorratsverwaltung unabhängig ausschalten. Beide sind anfangs aktiv. Ausschalten blendet die betreffende Seite aus, blockiert ihre Bedienung und erhält die Daten. Einkaufen bleibt verfügbar: ohne Planung nur manuelle Artikel, ohne Vorrat kein Abzug. Wieder einschalten stellt die Daten bereit. Die Schalter gelten serverweit.

### Planen und vorbereiten

1. Zuerst ein Rezept oder Getränk anlegen und seine Zutaten vervollständigen.
2. In Essensplanung Datum, Rezept, Menge/Einheit sowie optional Mahlzeit und Notizen wählen und speichern.
3. Portionen, Anteil, Gramm oder ml folgen den bekannten Rezeptregeln. Gramm brauchen fertiges Gewicht, ml ein Gesamtvolumen; Portionen/Anteile kein Gewicht.
4. Über den Zeitraum kommende Mahlzeiten ansehen. Eintrag bearbeiten, um Datum/Menge zu ändern oder ihn als **Vorbereitet** zu kennzeichnen. Gespeicherte Rezeptnotizen/Zubereitung lassen sich aufklappen.
5. Erst nach dem Verzehr tatsächlichen Zeitpunkt wählen und **Als gegessen eintragen** bestätigen. Es entsteht eine normale Rezeptbuchung mit Nährwerten und Health ausstehend. Wiederholtes Klicken erzeugt keinen zweiten Verzehr. Nur geplante/vorbereitete Mahlzeiten zählen nicht zu Home, Statistik, BAC oder Health.

Ein Plan speichert den Rezeptstand beim Anlegen. Termin-/Mengenänderungen erhalten ihn; ein anderes gewähltes Rezept übernimmt dessen Stand. Für eine neue Version desselben Rezepts den offenen Plan löschen und neu anlegen. Spätere Rezeptkorrekturen verändern den Plan nicht. Nach dem Essen den Tagebucheintrag korrigieren. Löschen eines Plans löscht keinen Verzehr. Löschen des Verzehrs macht den Plan nicht wieder offen; für erneuten Verzehr einen neuen Plan anlegen.

### Vorrat pflegen

Name, Menge und g/ml/Stück sowie optional Haltbarkeits-/Verbrauchsdatum und Notizen eintragen. Über **Lebensmittel suchen** möglichst dasselbe BLS-Lebensmittel, dieselbe eigene Zutat oder denselben Open-Food-Facts-Barcode wie in der Rezeptzutat verknüpfen. Ähnliche Namen allein reichen nicht. Namenänderungen lösen die Verknüpfung; gegebenenfalls erneut auswählen. Freitext passt nur zu anderen Freitextzutaten mit gleichem normalisiertem Namen und gleicher Einheit.

Mengen manuell aktualisieren oder verbrauchte Zeilen löschen. Mehrere Bestände desselben Lebensmittels/derselben Einheit werden addiert. Ein Datum vor Beginn des gewählten Planungszeitraums schließt den Bestand aus; spätere Daten garantieren nicht die Verwendbarkeit im ganzen Zeitraum. Datumsangaben sind Erinnerungen, keine Sicherheitsbewertung. Es gibt keine automatische Reservierung oder Verbrauchsabbuchung.

### Einkaufen

Zeitraum bis 366 Tage wählen. Die erzeugte Liste fasst Zutaten aller **noch nicht gegessenen** Pläne dieses Zeitraums mit ihren gespeicherten Rezeptständen und Verzehranteilen zusammen. Gemeinsame Zutaten werden addiert, passender Vorrat wird **einmal für den ganzen Zeitraum** abgezogen. Benötigt, Vorhanden und Einkaufen werden angezeigt, einschließlich vollständig gedeckter Zutaten mit Nullbedarf. Gramm und ml werden nicht umgerechnet; unterschiedliche Datenbank-IDs werden nicht gleichgesetzt.

Andere Artikel manuell hinzufügen/bearbeiten/löschen. Diese gelten unabhängig vom Zeitraum; Vorrat wird von ihnen nicht abgezogen. Gekaufte Artikel abhaken; Häkchen bleiben gespeichert. Geänderter Bedarf, Bestand oder Zeitraum setzt bei generierten Zeilen das Häkchen zurück. Abhaken bucht weder Vorrat noch Ernährung. Einkäufe ausdrücklich zum Vorrat hinzufügen. Wasserzusätze erzeugen keinen Einkaufsartikel; zusätzliche reine Koffein-/Alkoholmengen erfordern manuelle Artikel und erzeugen einen Hinweis.

**Wichtig:** Vorrat wird in dieser Version manuell gepflegt. Weder „gegessen“ noch „gekauft“ verändert den Bestand. Gegessene Pläne fallen aus dem Bedarf; vor weiteren Einkaufsberechnungen Bestand passend aktualisieren. Verschiedene Zeiträume sind unabhängige Berechnungen, keine Vorratsreservierungen.

Neue Daten, Schalter, Rezeptstände und Häkchen sind in ZIP-Sicherungen enthalten. Alte Backups ergeben eine leere Planungssammlung; zum Wiederherstellen neuer Backups Friss 1.42.0 oder neuer verwenden. Bestehende Rezept-/Tagebuchdaten bleiben unverändert. Die API ist oben mit Feldern/Endpunkten dokumentiert; Änderungen benötigen die aktuelle Versionsnummer. Für Planung/Einkaufsberechnung wird kein KI-Anbieter aufgerufen.
