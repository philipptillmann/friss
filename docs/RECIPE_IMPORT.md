# Rezepte von Chefkoch importieren (ab v1.35.0)

1. **Rezepte → Rezept von Chefkoch importieren** öffnen.
2. Einen öffentlichen Chefkoch-Rezeptlink einfügen, z. B. `https://www.chefkoch.de/rezepte/393031127655461/Spaghetti-Bolognese.html`.
3. **Rezept laden und prüfen** wählen. Es wurde noch nichts gespeichert.
4. Titel, Portionen, Zubereitung und Zutaten prüfen und bei Bedarf ändern. Zutaten können entfernt oder ergänzt werden. Ein bekanntes fertiges Gesamtgewicht kann eingetragen werden.
5. Pro Zutat bei Bedarf einen BLS-Treffer auswählen. Bei Änderung des Suchnamens werden alte Treffer verworfen; mit **BLS suchen** neue Treffer laden. Es wird kein Treffer automatisch ausgewählt.
6. **Als neues Rezept speichern** übernimmt den Entwurf in die normale Rezeptverwaltung. Dort lassen sich das Rezept und seine Zutaten weiter bearbeiten. Der Chefkoch-Quellenlink bleibt sichtbar und wird auch beim späteren Speichern und Duplizieren erhalten.

## Mengen und Nährwerte

- Eindeutige g/kg/mg-Angaben werden in Gramm übernommen; ml/cl/dl/l in Milliliter. Dezimalkomma und einfache Brüche werden unterstützt.
- Stückzahlen, EL/TL, „nach Bedarf“ und Mengenbereiche bleiben als Originaltext erhalten. Ein Gewicht wird nicht geschätzt. Fehlende Grammzahl später ergänzen oder die Zutat entfernen, wenn sie nicht verwendet wird.
- Milliliter sind keine Gramm. BLS-Zuordnung zu einer Zutat mit ml lässt sie bis zur passenden Mengenangabe unvollständig; ohne bekannte Dichte wird nichts automatisch umgerechnet.
- BLS-Zutaten mit bekannter Grammmenge werden regulär berechnet. Unzugeordnete Zutaten oder fehlende Mengen erscheinen als **Nachbearbeiten**. Vor dem Buchen von Rezeptportionen müssen alle Zutaten zugeordnet und vollständig sein. In der Zutatenliste auf **Nachbearbeiten** oder in den Details auf **Eintrag nachbearbeiten** klicken.
- Die Nährwerte berechnet Friss aus den zugeordneten Zutaten. Chefkochs Kalorien-/Makro-Zusammenfassung wird nicht zusätzlich addiert. Es werden keine Mikronährwerte erfunden.
- Die importierten Mengen gehören zur gesamten Rezeptmenge. Das Ändern der Portionszahl teilt diese Menge in mehr/weniger Portionen; es skaliert nicht automatisch alle Zutaten. Ein bekanntes fertiges Gesamtgewicht hat wie bisher Vorrang für Grammportionen; fehlt es, gelten die normalen Friss-Regeln.
- Ein Import erzeugt ein **Lebensmittelrezept**, keine Mahlzeit und keinen Health-Export. Ein Getränkerezept kann anschließend über die vorhandene Funktion nach **Getränke** verschoben werden.

## Herkunft und Zuverlässigkeit

Chefkoch liefert strukturierte Recipe-Daten im HTML. Friss übernimmt daraus Titel, Portionsangabe, Zutaten und Zubereitung. Die Originalangaben und Quelle bleiben zusätzlich in `import_source` am Rezept sowie als `data/originals/recipe-import-<id>.json` erhalten; bearbeitete Zutaten erhalten ihre ursprüngliche Zeile in den Import-Metadaten. Die vorhandenen ZIP-Backups sichern diese Daten mit.

Jeder Klick auf „Als neues Rezept speichern“ verwendet eine feste Import-ID für Wiederholungen. Bei unklarer Übertragung erneut speichern, ohne einen neuen Entwurf zu beginnen: So entsteht kein zweites Rezept. Beim Verwerfen eines unklaren Imports zuerst die Rezeptliste prüfen. Das bewusste spätere Importieren desselben Links ist weiterhin möglich und erstellt ein neues Rezept.

Es wird ausschließlich von erlaubten Chefkoch-Rezeptadressen geladen. Trackingparameter werden entfernt, Weiterleitungen validiert, Seitengröße und Wartezeit begrenzt. Friss führt keine Webseitenskripte aus, benötigt keinen Chefkoch-Login und lädt keine Rezeptbilder. Sind Inhalte gesperrt, entfernt oder nicht strukturiert verfügbar, erscheint eine Fehlermeldung; bis zum Speichern entstehen keine neuen Daten. Ein Import ist von der Erreichbarkeit und dem Seitenformat von Chefkoch abhängig.

## API

Authentifizierung wie bisher über API-Key oder Dashboard-Sitzung:

- `POST /recipe-import/preview`: `{ "url": "https://www.chefkoch.de/rezepte/…/….html", "lang": "de" }`. Liefert den Entwurf mit `source`, `ingredients` und optionalen BLS-Treffern, ohne Speicherung.
- `POST /recipe-import/commit`: `id` (UUID), `name`, `servings`, `notes`, optional `finished_weight_g`, unverändertes `source`-Objekt aus der Vorschau sowie bearbeitete `ingredients` mit `name`, `original_line`, optionaler `quantity` und optionalem `bls_code`. Wiederholungen benötigen dieselbe ID und dieselben Daten. Rezept und Zutaten werden gemeinsam gespeichert.
