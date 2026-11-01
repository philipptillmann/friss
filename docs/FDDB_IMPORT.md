# FDDB-Import: mobile und bisherige Links (ab v1.37.0)

Unter **Manuell → Nährwerte importieren** werden beide deutschen Produktlink-Formate unterstützt:

- `https://fddb.mobi/de/bitburger_bitburger_0_0prozent_alkoholfrei.html`
- `https://fddb.info/db/de/lebensmittel/naturprodukt_zimt_gemahlen_1053/index.html`

Nach dem Laden die Vorschau prüfen und die eigene Zutat speichern. Quelle und Originalwerte bleiben gespeichert. Trackingparameter werden entfernt. Erlaubte Weiterleitungen zwischen FDDB-Produktseiten werden geprüft; andere Hosts und Nicht-Produktseiten werden nicht abgerufen. Größenlimits, Zeitlimits und Authentifizierung bleiben bestehen.

## 100 g und 100 ml unterscheiden

Die mobile FDDB-Seite enthält eine andere Nährwertdarstellung und bei Getränken häufig Angaben **pro 100 ml**. Friss liest die ausdrücklich genannte Basis aus der Nährwerttabelle, nicht aus der Portionsübersicht oder dem Produktnamen.

Eigene Lebensmittel besitzen deshalb eine **Bezugsmenge** von 100 g oder 100 ml. Beim Import wird sie passend vorbelegt. Diese Basis gilt für alle eingegebenen Nährwerte und die zusätzliche Alkoholmenge.

- Bei einem Lebensmittel pro 100 ml erfolgt die Mengenangabe beim Verzehr ebenfalls in ml. Das gilt für die gemeinsame Suche, die Auswahl eigener Zutaten, Favoriten, zuletzt benutzte Zutaten und Rezepte.
- Beispiel des genannten Bitburger-Eintrags: FDDB veröffentlicht **33 kcal pro 100 ml**. 500 ml ergeben daher **165 kcal** und **39 g Kohlenhydrate**. Friss übernimmt die veröffentlichten Werte; deren inhaltliche Richtigkeit muss weiterhin geprüft werden.
- Es erfolgt keine Umrechnung zwischen g und ml und keine Annahme einer Dichte von 1. Eine unpassende Mengeneinheit bleibt zur Nachbearbeitung offen.
- Das Ändern der Bezugsmenge im Editor rechnet die Zahlen **nicht** um. Für eine korrekte Umrechnung ist die Dichte erforderlich. Bei einer nachträglich geänderten Basis werden unpassende alte Vorschlagsmengen nicht ungeprüft übernommen.
- Bestehende eigene Zutaten ohne Basisangabe verwenden weiterhin 100 g. Schon gespeicherte Mahlzeiten und Rezeptzutaten behalten ihren gespeicherten Stand und ihre damalige Basis.
- Milliliter eines Getränks werden nicht automatisch als getrunkenes Wasser gebucht; das bestehende getrennte Wassertracking bleibt bestehen.

Mobile Tabellen, Vitamine und Mineralstoffe werden im Nährwertabschnitt gelesen; Werte aus Flaschen-/Glasportionen werden nicht nochmals addiert. „Chlor“ wird dem Chlorid-Feld zugeordnet. Salz wird, falls kein direkter Natriumwert vorhanden ist, nach der üblichen Beziehung Salz = 2,5 × Natrium umgerechnet. FDDB-Kohlenhydrate sind europäische Angaben und werden nicht nochmals um Ballaststoffe reduziert. Fehlende Werte bleiben unbekannt.

## API

`POST /manual-ingredients/import` verwendet wie bisher `{ "url": "…" }`. Die Vorschau enthält jetzt `basis_unit: "g"` oder `"ml"`. Beim Speichern/Ändern einer eigenen Zutat wird dieses Feld mitgesendet. Fehlt es bei einem Import mit ausdrücklich deklarierter `source.basis_ml`, erkennt der Server die ml-Basis anhand dieser Quelle; normale ältere Eingaben bleiben bei g.

Die Quellenmetadaten verwenden entweder `basis_g: 100` oder `basis_ml: 100`; die jeweils andere Angabe ist null. Beim Verzehr eine passende `quantity.unit` senden. Sicherungen enthalten diese Angaben automatisch als Teil der gespeicherten Zutaten und Momentaufnahmen.
