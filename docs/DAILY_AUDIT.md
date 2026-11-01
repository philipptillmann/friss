# Tagesprüfung der Nährwerte (ab v1.40.0)

Unter **Statistik → Tagesprüfung** gibt es eine für den Computer ausgelegte Tabelle. Der bisherige Diagramm-/Zeitraum-Bereich bleibt unter **Verlauf** erhalten.

## Bedienung

- Mit **Vorheriger Tag**, **Nächster Tag**, **Heute** oder dem Datumsfeld zwischen einzelnen Tagen wechseln.
- Jede Tagebuchbuchung ist eine Zeile: Eintrag, Uhrzeit, Menge, Quelle, Verarbeitungsstatus und Anzahl fehlender/ungeprüfter Felder.
- Alle derzeit erfassten Nährstoffe sind Spalten – auch wenn an diesem Tag keine Quelle einen Wert dafür liefert. Dazu kommen separat erfasstes Trinkwasser, Koffein und Alkohol in Gramm. Die Nährstoffreihenfolge entspricht Home.
- Die Tabelle horizontal zu den weiteren Nährstoffen und bei vielen Zeilen vertikal scrollen. Spaltenüberschriften und der Name des Eintrags bleiben im Tabellenbereich sichtbar. Auf großen Bildschirmen nutzt die Ansicht mehr Breite als die normale App.
- Eintragsnamen öffnen die bekannten Details in einem neuen Tab, damit die Tagesprüfung offen bleibt. Dort können Angaben nachbearbeitet werden; zum Aktualisieren der Prüfung den Tag erneut auswählen oder über die Tagesnavigation zurückkehren.
- Die Grenzen des Tages und Uhrzeiten verwenden die Zeitzone des Browsers, einschließlich Sommer-/Winterzeit. Rezeptzutaten werden ausgeschlossen; gebuchte Rezept-/Getränkeportionen stehen dagegen als eigene Zeilen in der Tabelle.

## Lücken erkennen

- **0**: ein bekannter Nullwert. Positive sehr kleine Werte können in der Anzeige auf zwei Nachkommastellen runden; der Tooltip zeigt mehr Genauigkeit.
- **— / orange**: dieser Wert wurde nicht geliefert bzw. ist unbekannt.
- **TR, <LOQ usw. / rot**: ursprüngliche Spur-/Nachweisgrenzenangabe; keine erfundene Zahl.
- **Rot mit Wert und Einheit**: Quelleinheit ungeprüft oder nicht mit der Spalteneinheit kompatibel. Die Originaleinheit bleibt am Wert/Tooltip erkennbar; es erfolgt keine g/ml-Umrechnung.
- **\***: dieser fehlende Quellenwert wird wegen der Null-Annahme-Einstellung in anderen Ansichten gegebenenfalls als 0 verwendet. Die Tagesprüfung zeigt die fehlende Quelle trotzdem an.

Die Zahl der Lücken ist ein Hinweis auf Datenvollständigkeit, kein Nachweis eines falschen Lebensmittels. Gerade einfache Getränke können viele nicht gelieferte Nährstoffe haben. Die Prüfung zeigt Quelldaten und schreibt keine künstlichen Nullwerte zurück.

**Summe bekannter Werte** addiert nur numerische, geprüfte Werte mit passender Einheit. Massen werden bei Bedarf zwischen g/mg/µg umgerechnet. Fehlende, angenommene oder ungeprüfte Werte werden nicht als tatsächliche Werte eingerechnet. Die zusätzlichen Spaltenhinweise zeigen, für wie viele Zeilen noch Daten fehlen/ungeprüft sind. Diese Summe ist bei Lücken kein vollständiger Tageswert und kann sich von einer Null-Annahme-Darstellung unterscheiden.

Nahrungswasser und separat erfasstes Trinkwasser sind wie auf Home getrennt. BAC ist kein Nährstoffbeitrag eines einzelnen Lebensmittels und erscheint deshalb nicht als Spalte.

## API

Authentifiziertes `GET /statistics/day?day=2026-11-01&tz=Europe/Berlin` liefert Tagesgrenzen, Spaltendefinitionen, Zeilen mit Nährstoffzellen und bekannte Summen. Zellstatus: `known`, `missing`, `qualifier`, `unverified`, `incompatible`; `assumed` kennzeichnet die optionale Null-Annahme separat. Es werden alle Tagebucheinträge des ausgewählten Tages berücksichtigt, ohne das 1.000-Einträge-Limit der normalen Liste. Die API und Tabelle sind rein lesend und ändern weder Tagebuch noch Health-Daten.
