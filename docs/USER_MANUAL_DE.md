# Friss – Benutzerhandbuch

**Für Version 1.43.0 · Stand: 10. November 2026**
[English manual](USER_MANUAL_EN.md) · [Projektübersicht](../README.md)

Friss ist ein selbst gehostetes Ernährungs- und Getränketagebuch. Dein Server speichert Einträge, Originaleingaben, Rezepte und Nährwertdaten. Du bedienst Friss im Browser am Computer oder über eine Verknüpfung auf dem iPhone-Home-Bildschirm. Friss ist eine Web-App, keine native iPhone-App. Zum Schreiben in Apple Health ist ein separater iPhone-Kurzbefehl erforderlich.

## Inhalt

1. [Erste Schritte](#1-erste-schritte)
2. [Home und Tageswerte](#2-home-und-tageswerte)
3. [Mahlzeiten und Lebensmittelsuche](#3-mahlzeiten-und-lebensmittelsuche)
4. [Eintragsdetails, Korrekturen und Kopieren](#4-eintragsdetails-korrekturen-und-kopieren)
5. [Getränke, Schnellwahl und BAC](#5-getränke-schnellwahl-und-bac)
6. [Rezepte](#6-rezepte)
7. [Favoriten und zuletzt benutzt](#7-favoriten-und-zuletzt-benutzt)
8. [Manuelle Lebensmittel, Webimport und Etikettenerkennung](#8-manuelle-lebensmittel-webimport-und-etikettenerkennung)
9. [Nährwerte und fehlende Angaben verstehen](#9-nährwerte-und-fehlende-angaben-verstehen)
10. [Statistik und Tagesprüfung](#10-statistik-und-tagesprüfung)
11. [Export nach Apple Health](#11-export-nach-apple-health)
12. [Einstellungen](#12-einstellungen)
13. [KI-Importe und iPhone-Kurzbefehle](#13-ki-importe-und-iphone-kurzbefehle)
14. [Datensicherung und Wiederherstellung](#14-datensicherung-und-wiederherstellung)
15. [Serverinstallation und Updates](#15-serverinstallation-und-updates)
16. [Probleme lösen](#16-probleme-lösen)

17. [Essensplanung, Vorrat und Einkaufsliste](#17-essensplanung-vorrat-und-einkaufsliste)

18. [Posteingang für unfertige Einträge](#18-posteingang-für-unfertige-einträge)

## 1. Erste Schritte

Öffne die Friss-Adresse deines Servers, beispielsweise `http://spiesserver:8001/`, und melde dich mit dem eingerichteten Passwort an. Verwende den tatsächlichen Hostnamen beziehungsweise die IP und den Port deiner Installation. Dein Gerät muss den Server erreichen können; unterwegs zuerst das VPN verbinden. Eine Offline-Erfassung ist nicht implementiert.

Auf dem iPhone öffnest du die Seite in Safari und wählst **Teilen → Zum Home-Bildschirm hinzufügen**. Starte Friss anschließend über das neue Icon. Safari und die installierte Web-App können getrennte Anmeldesitzungen haben. Eine Sitzung bleibt bis zu 30 Tage bestehen; Abmelden beziehungsweise eine Passwortänderung beendet die betreffenden Sitzungen. Apple Passwörter kann die Anmeldung ausfüllen.

Oben kannst du Deutsch oder Englisch wählen. Das Menü enthält **Home, Mahlzeiten, Getränke, Rezepte, Favoriten, Manuell, Statistik, Export, Einstellungen**, ergänzt um **Essensplanung, Vorrat, Einkaufsliste und Posteingang**. Die folgenden Bezeichnungen beziehen sich auf die deutsche Oberfläche.

Für einen ersten Test: Ziele in den Einstellungen setzen, unter Mahlzeiten ein Lebensmittel suchen, Menge eingeben und speichern. Danach Home und Statistik prüfen, bevor du Health oder automatisierte Importe einrichtest.

## 2. Home und Tageswerte

Home zeigt immer **heute in der lokalen Zeitzone deines Browsers**. Eine andere Datumswahl unter Mahlzeiten verändert Home nicht.

- Der kurze Fortschrittstext und die Zielkarten vergleichen die protokollierten Kalorien/Makronährstoffe mit deinen gespeicherten Tageszielen. Ziele sind freiwillig und unabhängig voneinander einstellbar.
- Das **Suchsymbol** öffnet die Lebensmittelsuche auf Mahlzeiten. Das **Barcodesymbol** startet die Barcode-Erfassung.
- **Nährwerte** enthält Kalorien, Makros und verwandte Hauptwerte; **Koffein / Alkohol** zeigt Koffein, Gramm reinen Alkohol und den aktuell geschätzten BAC; **Mikronährstoffe** enthält die weiteren erfassten Nährstoffe.
- Klicke auf einen Nährwertbetrag, um die beitragenden Einträge zu sehen. Weitere relevante unvollständige Einträge werden gesondert aufgeführt.
- Zahlen erscheinen mit höchstens zwei Nachkommastellen. Die gespeicherten Quelldaten werden dadurch nicht gerundet.

Die Getränke-Schnellwahl befindet sich auf **Getränke**, nicht auf Home.

## 3. Mahlzeiten und Lebensmittelsuche

Wähle den gewünschten Tagebuchtag und die Erfassungsart. Prüfe den Zeitpunkt: Er ist normalerweise mit jetzt vorbelegt und kann geändert werden. Speichern legt den Eintrag direkt im Tagebuch an. Apple Health wird separat übertragen.

### Gemeinsame Suche

Gib einen Lebensmittelnamen ein. Friss durchsucht die lokale **BLS-Datenbank**, **Open Food Facts**, deine **manuellen Lebensmittel** und, wo passend, gespeicherte **Lebensmittel- und Getränkerezepte**. Farbige Quellen-Tags unterscheiden die Treffer; Favoriten haben einen Stern. Rezepte und Getränke besitzen unterschiedliche Tags und getrennte Auswahllisten.

Wähle einen konkreten Treffer, gib die verzehrte Menge ein und speichere. Achte auf roh/gegart, Fettstufe und Zubereitung. Friss lernt, welchen Treffer du für einen Suchbegriff und eine Sprache auswählst. Die BLS-Suche findet auch Wortbestandteile: **Salz** kann **Speisesalz** vorschlagen. Exakte Namen und kürzere passende Bezeichnungen werden bevorzugt; gelernte Zuordnungen und eigene Synonyme behalten Vorrang.

Lokale Treffer können vor den Online-Ergebnissen aus Open Food Facts erscheinen. Ist Open Food Facts nicht erreichbar, bleibt die lokale Suche verfügbar. Ein gefundener Datensatz muss nicht alle Nährwerte enthalten.

### Erfassungsarten

| Art | Bedienung |
| --- | --- |
| Suche | BLS-Lebensmittel, eigenes Lebensmittel oder Rezept auswählen und die Menge in der passenden Einheit eingeben. BLS verwendet Gramm. |
| Barcode | Nummer eingeben oder Barcode fotografieren, erkannten Code auswählen, Menge eingeben und speichern. Produktdaten kommen aus Open Food Facts. |
| Foto | Lebensmittel fotografieren/hochladen und die Originaleingabe erhalten. Die normale Foto-Erfassung erkennt Lebensmittel und Nährwerte nicht automatisch; Lebensmittel/Menge zuordnen oder den externen KI-Import verwenden. |
| Text | Beschreibung eingeben. Mehrdeutige oder ungeklärte Eingaben anschließend einem Lebensmittel und einer Menge zuordnen. |
| Rezept essen / Getränk trinken | Gespeicherte Definition wählen und Portionen, Anteil, Gramm oder unterstützte Milliliter eintragen. Siehe Rezeptberechnung. |
| Manuelles Lebensmittel | Eine eigene Zutat wählen und Gramm oder Milliliter passend zu ihrer Bezugsmenge eingeben. |
| Zuletzt benutzt / Favoriten | Vorhandenes Lebensmittel wiederverwenden; Menge und Uhrzeit vor dem Speichern prüfen. |
| JSON-Import | Unterstützte KI-JSON einfügen/hochladen, Vorschau prüfen und speichern. Siehe Abschnitt 13. |

Die Barcode-Kamera arbeitet mit einem Foto, nicht mit einem durchgehenden Live-Scanner. Ein Scan allein bucht nichts. Bei Erkennungsproblemen schärfer fotografieren oder die Ziffern manuell eingeben.

Bei der normalen Erfassung darf die Menge zunächst leer bleiben. Der Eintrag bleibt zur Nachbearbeitung erhalten. Die BLS-Stapel-API verlangt dagegen eine positive Grammmenge.

## 4. Eintragsdetails, Korrekturen und Kopieren

Klicke unter Mahlzeiten auf einen Eintrag. Die Details zeigen Name, Quelle/Erfassungsart, Menge, Zeitpunkt, Verarbeitungs- und Health-Status sowie alle Nährwertbeiträge in derselben Reihenfolge wie Home. Angefügte Originalfotos lassen sich dort öffnen.

- **Zeitpunkt ändern:** Datum/Uhrzeit anpassen und speichern. Bei Getränken ist zusätzlich eine Endzeit möglich.
- **Nachbearbeiten:** Die gewählte Lebensmittelzuordnung und vorhandenen Eingaben werden wiederhergestellt. Du kannst beispielsweise nur die fehlende Menge ergänzen, statt neu zu suchen.
- **Eintrag kopieren:** Zielzeitpunkt wählen. Es entsteht ein neuer Eintrag mit gespeichertem Lebensmittel-/Rezeptstand und Nährwerten; das Original bleibt erhalten. Die Kopie beginnt mit Health ausstehend. Bei Getränken bleibt beim Verschieben die Dauer erhalten.
- **Löschen:** Einzelnen Eintrag nach Sicherheitsabfrage löschen. Der Tages-Reset entfernt nach Bestätigung die Tagebucheinträge des ausgewählten Tages. Datum sorgfältig prüfen.

Rezeptzutaten sind kein eigenständiger Tagesverzehr. Bearbeite sie im Rezept, statt sie als eigene Tagebuchmahlzeiten zu kopieren.

Änderungen und Löschungen in Friss korrigieren **keine** bereits geschriebenen Apple-Health-Werte. Originaldateien bleiben auf dem Server erhalten, auch nach dem Löschen eines Eintrags. Eine Tagebuchlöschung entfernt deshalb nicht alle archivierten Originale oder Sicherungen.

## 5. Getränke, Schnellwahl und BAC

Auf **Getränke** stehen zuerst die Schnellwahl-Bildkacheln, vier pro Reihe. Du richtest sie in den Einstellungen ein. Antippen bucht das hinterlegte Getränk/Rezept mit seiner Menge zum aktuellen Zeitpunkt. Ein Cappuccino aus einem Rezept erfasst beispielsweise auch Milch-/Espressonährwerte und bekanntes Koffein; er ist kein bloßer Koffeinzähler.

Darunter kannst du ein Getränkerezept auswählen oder anlegen. Lebensmittelrezepte und Getränkerezepte sind getrennte Kategorien. Die manuelle Getränkeeingabe für Wasser, Koffein und Alkohol bleibt verfügbar.

Für Alkohol verwendest du entweder:

- **Gramm reinen Alkohol**, oder
- **Getränkevolumen in ml und Volumenprozent (ABV)**.

Friss berechnet reinen Alkohol als `Volumen × ABV / 100 × 0,789`. Die manuelle Alkohol-/ABV-Erfassung ergänzt nicht automatisch sämtliche Getränkekalorien oder andere Nährwerte. Verwende dafür ein Produkt oder Getränkerezept.

### Erster/letzter Schluck und BAC-Kurve

Der Eintragszeitpunkt ist der erste Schluck. Optional gibst du **Letzter Schluck** an. Bei einem Getränk über Mitternacht wählst du für das Ende das Datum des Folgetags. Das Ende darf nicht vor dem Start liegen.

Die BAC-Berechnung verwendet protokollierten Alkohol, deine Körperparameter aus den Einstellungen sowie Aufnahme und Abbau. Mit Endzeit nimmt sie gleichmäßiges Trinken zwischen Start und Ende an. Ohne Endzeit wird eine sofortige Zufuhr mit anschließender Aufnahme modelliert. Mehrere Getränke werden gemeinsam berechnet, auch über Mitternacht; um 0 Uhr wird die modellierte Alkoholmenge nicht zurückgesetzt. Eine zukünftige Endzeit beschreibt für den Rest eine Prognose.

Die **gesamten Nährwerte und Alkoholgramm gehören im Tagebuch zum Starttag**. Das Ende verändert nur den BAC-Verlauf. Einzelne Schluckmuster kennt das Modell nicht. BAC bleibt eine Schätzung, kein Messwert und keine Grundlage für die Entscheidung, ob du fahren kannst.

## 6. Rezepte

Lege unter **Rezepte** ein Lebensmittelrezept mit Namen und Gesamt-Portionszahl an. Füge Zutaten mit den normalen Erfassungsarten hinzu. Prüfe, dass das gewünschte Rezept als Speicherziel gewählt ist. Zutaten zählen zum Rezept, nicht direkt zu heutigen Tageswerten oder Health.

Klicke eine Zutatenzeile an, um Lebensmittel, Menge oder Zeitpunkt zu ändern. Ungeklärte Lebensmittel/Mengen müssen vor dem Buchen des Rezeptverzehrs ergänzt werden. Die Zutatenzeitpunkte bleiben als Referenz erhalten.

### Einen Teil des Rezepts eintragen

| Einheit | Verwendeter Rezeptanteil |
| --- | --- |
| Portionen | Gegessene Portionen ÷ Gesamt-Portionszahl |
| Anteil | Direkt eingeben, z. B. `0,25` für ein Viertel |
| Gramm | Gegessene Gramm ÷ **fertiges Gesamtgewicht** |
| Milliliter bei Getränken | Getrunkene ml ÷ fertiges Gesamtvolumen |

Beispiel: Bei vier Portionen und 800 g fertigem Gesamtgewicht ergeben **eine Portion**, **0,25 des Rezepts** und **200 g** denselben Nährwertbeitrag.

Das Gesamtgewicht bezeichnet das ganze fertige Gericht nach dem Kochen. Friss ersetzt es **nicht automatisch durch die Summe der Zutatengewichte**. Ohne Gesamtgewicht kannst du Portionen und Anteile buchen; Gramm-Verzehr benötigt dieses Gewicht. Portionsberechnung funktioniert ohne Gesamtgewicht. Eine geänderte Portionszahl teilt die vorhandenen Zutaten anders auf; sie vervielfacht nicht automatisch deren Mengen. Kochverluste werden nicht automatisch modelliert.

### Wasser-, Koffein- und Alkoholzusätze

Optionale zusätzliche Mengen für Wasser (ml), Koffein (mg) und reinen Alkohol (g) gelten für das **ganze Rezept** und werden mit dem Verzehranteil skaliert. Ergänze nur Mengen, die nicht bereits durch Zutaten enthalten sind. Wasserzugabe verändert nicht automatisch das fertige Gesamtgewicht.

Ein Getränkerezept kann außerdem Gesamtvolumen und den **finalen Alkoholgehalt des ganzen Getränks** erhalten. Der finale ABV ersetzt die Alkoholberechnung aus den Zutaten und benötigt das Gesamtvolumen; nicht gleichzeitig zusätzliche reine Alkoholgramm eingeben. Andere Nährwerte kommen weiterhin aus den Zutaten.

### Duplizieren, Verschieben und Korrigieren

- **Rezept duplizieren** erzeugt eine unabhängige bearbeitbare Kopie einschließlich Zutaten und gespeicherter Metadaten. Es wird kein Verzehr gebucht.
- **Als Getränk verschieben** ändert die Kategorie, erhält aber Identität und Schnellwahl-Verknüpfungen. Vorhandene Tagebucheinträge behalten ihre Werte. Zurückverschieben ist ebenfalls möglich; gegebenenfalls vorher finalen ABV entfernen.
- **Nur für zukünftige Einträge speichern** verwendet die Definition für künftigen Rezeptverzehr. Bereits gebuchte Portionen behalten ihre Momentaufnahme.
- **Speichern und bisherige Einträge korrigieren** berechnet nach Bestätigung die bisherigen Verzehre dieses Rezepts neu. Verzehrte Mengen und Zeitpunkte bleiben erhalten. Dabei wird das aktuelle ganze Rezept angewendet: zuvor alle Zutaten prüfen.

Zutatenänderungen werden beim Bearbeiten bereits am Rezept gespeichert; die anschließende Speicherwahl steuert die rückwirkende Neuberechnung. Eine unabhängig duplizierte Definition wird bei Korrektur ihres Originals nicht mitgeändert.

### Chefkoch importieren

Öffne den Chefkoch-Rezeptimport, füge einen öffentlichen Rezeptlink ein und lade den Entwurf. Prüfe Titel, Portionen, Anleitung und Zutaten. Ordne bei Bedarf BLS-Lebensmittel und Grammengen zu und speichere als neues Rezept. Löffel, Stück, Bereiche und „nach Geschmack“ bleiben Originaltext, solange du keine passende Menge ergänzt. Importierte Rezepte werden nicht automatisch als Mahlzeit gebucht. [Ausführliche Anleitung](RECIPE_IMPORT.md).

## 7. Favoriten und zuletzt benutzt

**Zuletzt benutzt** bietet Lebensmittel aus bisherigen Tagebuch- und Rezeptzutaten-Einträgen an. Unter **Favoriten** kannst du wiederverwendbare Favoriten anlegen, bearbeiten und löschen; verwende sie anschließend bei Mahlzeiten und Zutaten. Prüfe vorgeschlagene Mengen, statt sie automatisch als heutige Menge zu übernehmen. Die gemeinsame Suche sowie manuelle/Barcode-Erfassung können zuletzt verwendete Mengen vorschlagen.

Ein Favorit ist ein wiederverwendbarer Lebensmitteleintrag, keine Getränke-Schnellwahlkachel. Ein-Klick-Kacheln richtest du getrennt in den Einstellungen ein. Das Entfernen eines Favoriten löscht keine Tagebucheinträge.

## 8. Manuelle Lebensmittel, Webimport und Etikettenerkennung

Unter **Manuell** legst du eigene Lebensmittel an. Trage Namen, optionale Notizen und bekannte Nährwerte ein. Wähle die Bezugsmenge **pro 100 g** oder **pro 100 ml**. Beim Verzehr muss die Mengeneinheit dazu passen. Ein leerer englischer Name übernimmt den deutschen Namen.

Unbekannte Felder leer lassen; 0 nur bei bekanntem Nullwert eintragen. Mindestens ein bekannter Nährwert ist erforderlich. Energie verwendet kcal, andere Felder die angezeigten Einheiten g/mg/µg/ml. Reiner Alkohol hat ein eigenes Feld. Die nicht editierbare **Salzmenge** unter Natrium verwendet **Salz = Natrium × 2,5** mit passender Massenumrechnung. Sie wird nicht nochmals als zusätzlicher Nährstoff addiert.

### Von einer Website importieren

Füge einen unterstützten **FDDB**-Produktlink (`fddb.info` oder `fddb.mobi`) oder **FoodData-Explorer**-Zutatenlink (`fooddata.the50.store`) ein. Lade die Nährwertvorschau, prüfe Bezugsmenge/Werte/Namen und speichere. Laden allein legt nichts an.

- FDDBs ausdrücklich angegebene 100-g-/100-ml-Basis wird berücksichtigt. Europäische Kohlenhydrate werden nicht nochmals um Ballaststoffe reduziert.
- Bei unterstützten US-/USDA-Gesamtkohlenhydraten aus FoodData werden bekannte Ballaststoffe abgezogen, um europäische verfügbare Kohlenhydrate zu erhalten. Ist die Umrechnung nicht begründbar, bleibt das Feld unbekannt.
- Veröffentlichte Einheiten werden soweit unterstützt umgerechnet. Nicht unterstützte und fehlende Werte bleiben unbekannt. Quelleninformationen bleiben erhalten.
- Das manuelle Ändern der Bezugsmenge rechnet die Zahlen **nicht** um. Zur Umrechnung von Masse und Volumen brauchst du die Dichte.

Importe hängen von Erreichbarkeit und Aufbau der jeweiligen Website ab. [FDDB-Anleitung](FDDB_IMPORT.md).

### Nährwertetikett fotografieren oder hochladen

Wähle **Nährwertetikett fotografieren** oder **Etikettbild hochladen**. Verwende eine scharfe, gerade Aufnahme mit eindeutiger **100-g-Spalte**. Friss führt deutsche/englische Texterkennung auf deinem Server aus und füllt Vorschläge ein. Namen ergänzen und alle Zahlen/Einheiten vor dem Speichern prüfen.

Dieser OCR-Ablauf interpretiert Portionsangaben, US Nutrition Facts und 100-ml-Tabellen nicht automatisch. Sie erfordern manuelle Eingabe/Umrechnung. Erkanntes Salz kann zu Natrium, kJ können zu kcal umgerechnet werden. Das Scanbild selbst wird dabei nicht archiviert; erkannter Text bleibt in den Notizen. Das ist Etiketten-Texterkennung, keine KI-Erkennung eines fotografierten Gerichts.

### Gespeicherte manuelle Lebensmittel ändern

Du kannst nur für die Zukunft speichern oder bisherige Verwendungen korrigieren. Nur Zukunft verändert weder alte Tagebucheinträge noch vorhandene Rezeptzutaten. Auch eine neu gebuchte Portion eines alten Rezepts verwendet weiterhin dessen gespeicherten Zutatenstand, bis dieser korrigiert wird.

Die rückwirkende Korrektur ersetzt dieses Lebensmittel in direkten Tagebuchverwendungen, Rezeptzutaten und alten Rezeptmomentaufnahmen, die es enthalten. Andere Zutaten und damalige Portions-/Gewichts-/Volumenparameter bleiben erhalten. Eine ganze Rezeptkorrektur verwendet dagegen dessen gesamten aktuellen Stand. Einheitenkonflikte oder laufende Health-Exporte können die Änderung vollständig blockieren. [Details zu Korrekturen](CORRECTING_HISTORY.md).

## 9. Nährwerte und fehlende Angaben verstehen

- **Unvollständig:** Mindestens ein Beitrag ist unbekannt. Eine angezeigte Zahl kann nur der bekannte Teil der tatsächlichen Aufnahme sein.
- **TR, <LOD, <LOQ:** Spuren-/Nachweisgrenzenangaben der Quelle, keine exakte Null.
- **Quelleinheit ungeprüft:** Friss kann eine alte beziehungsweise unbekannte Quelleinheit nicht sicher interpretieren. Die Rohzahl ist keine geprüfte Menge; Health-Export kann gesperrt sein.
- **Geschätzt:** Daten aus externer KI oder anderen Eingaben sind Schätzungen, keine unabhängigen Messungen durch Friss.
- **µg** bezeichnet Mikrogramm; JSON kann intern `mcg` verwenden. `1 mg = 1.000 µg`.

**Getrunkenes Wasser** ist ausdrücklich erfasstes Trinkwasser einschließlich entsprechender Rezeptzusätze. **Wasser in Lebensmitteln** ist der verbleibende veröffentlichte Lebensmittel-Wassergehalt; Trinkwasser wird dort nicht nochmals aufgeführt. Wasser in einem BLS-Kaffee/-Tee wird nicht automatisch zum explizit getrackten Trinkwasser. Weder das ganze Getränkevolumen noch das Lebensmittelgewicht wird pauschal als Wasser angenommen. Lebensmittelwasser darf in Gramm verbleiben.

Unter **Einstellungen** kannst du fehlende Werte als Null behandeln lassen. Die Option wertet fehlende Felder und Spuren-/Grenzangaben als angenommene Null aus, repariert aber nicht die Quelle. Sie ist umkehrbar und betrifft alte/neue Einträge, Rezeptberechnungen, Übersichten und Exporte. Fehlende Lebensmittel/Mengen sowie vorhandene Zahlen mit ungeprüften Einheiten müssen weiterhin nachbearbeitet werden. Die Tagesprüfung zeigt die ursprünglichen Datenlücken trotzdem.

## 10. Statistik und Tagesprüfung

Unter **Statistik → Verlauf** wählst du 7/30/90 Tage oder einen eigenen Zeitraum bis 366 Tage und anschließend einen erfassten Nährstoff. Diagramm, Summe, Durchschnitt und Tagestabelle folgen dieser Auswahl. Für Kalorien, Protein, Kohlenhydrate und Fett erscheint das aktuell eingestellte Tagesziel als gestrichelte Linie. Das sind die aktuellen Einstellungen, keine historischen Zielaufzeichnungen.

Tage ohne verwendbare Einträge bleiben Lücken. Durchschnitte verwenden Tage mit berechneten Werten, nicht automatisch alle Kalendertage. Unvollständige Tage sind gekennzeichnet. Tagesgrenzen richten sich nach Browserzeitzone und Sommer-/Winterzeit.

**Statistik → Tagesprüfung** ist für den Computer gedacht. Datum wählen oder Vorheriger/Nächster Tag/Heute verwenden. Jede Tagebuchbuchung steht in einer Zeile, jeder erfasste Nährwert in einer Spalte. Horizontal/vertikal scrollen; Überschriften und Eintragsnamen bleiben sichtbar. Namen öffnen Details in einem neuen Tab.

- `0`: bekannter Nullwert. Der Tooltip zeigt kleine Werte genauer als die gerundete Anzeige.
- Strich/orange: fehlender Quellenwert.
- Rot: Spuren-/Grenzangabe, ungeprüfte oder inkompatible Einheit; Tooltip prüfen.
- `*`: dieser fehlende Quellenwert kann wegen der Einstellung anderswo als Null angenommen werden.

Die Fußzeile addiert **bekannte, geprüfte Werte mit passenden Einheiten** und zählt Lücken je Spalte. Rezeptzutaten sind ausgeschlossen, verzehrte Portionen enthalten. BAC ist kein einzelner Nährwertbeitrag und hat keine Spalte. Nach einer Detailänderung den Tag erneut auswählen, um die Prüfung zu aktualisieren. [Details zur Tagesprüfung](DAILY_AUDIT.md).

## 11. Export nach Apple Health

Friss kann im Browser nicht direkt in Apple Health schreiben. **Export** bereitet eine Tagesdatei vor; ein separat eingerichteter iPhone-Kurzbefehl muss sie lesen und die Werte in Health protokollieren. Ein fertig installierbarer Health-Kurzbefehl wird nicht mitgeliefert.

1. Tagebuchtag vervollständigen/prüfen und Export öffnen.
2. **Tag exportieren** wählen. Friss reserviert eine unveränderliche Tagesdatei.
3. Datei laden/teilen und an deinen Health-Kurzbefehl übergeben.
4. Der Kurzbefehl liest `samples`, ordnet jeden `identifier` einer unterstützten Health-Aktion zu und verwendet **value, unit und timestamp** des jeweiligen Werts. Erteile auf dem iPhone die erforderlichen Berechtigungen. Nicht unterstützte Kategorien dürfen nicht still übersprungen werden.
5. Erst wenn alle Werte erfolgreich geschrieben wurden, in Friss **Health-Schreiben bestätigen** wählen. Dateidownload allein ist kein Erfolg; Friss kontrolliert Health nicht automatisch.
6. Bei Fehler oder Teilübertragung **Export fehlgeschlagen / unklar** wählen und Health manuell prüfen, bevor du weiter exportierst.

Status unterscheiden noch nicht exportiert, vorbereitet, bestätigt, unklar/manuell prüfen und seit Export geändert. Offene Einträge, ungeprüfte BLS-Einheiten und vorherige Einzelexporte können die Tagesreservierung blockieren. Bei aktivierter Nullannahme kann der Export ausdrücklich markierte angenommene Nullen enthalten; sonst werden fehlende Werte nicht erfunden.

Tageswerte erhalten 12 Uhr in der gewählten Tageszeitzone. Alkoholgramm und BAC werden nicht als Health-Ernährungswerte exportiert. Nutze die Einheiten der Datei, statt die Anzeigeeinheit der Oberfläche vorauszusetzen.

Bearbeiten, Löschen, geänderte Nullannahmen oder ein altes Backup können Friss und Health auseinanderbringen. Friss löscht/überschreibt alte Health-Werte niemals automatisch. Korrigiere sie auf dem iPhone vor einem erneuten Export; blindes Wiederholen kann doppelte Werte erzeugen.

## 12. Einstellungen

Unter **Einstellungen** verwaltest du Tagesziele für Kalorien/Makros, Nullannahmen, Körper-/BAC-Parameter, Getränke-Schnellwahl samt Bildern, Suchpräferenzen, API-Schlüssel und Datensicherung.

Schnellwahl-Presets können auf Lebensmittel oder Rezepte verweisen, damit alle Nährwerte erfasst werden. Lade ein Bild zur Wiedererkennung hoch und prüfe Menge/Rezeptverknüpfung. Bilder füllen kleine Kacheln, vier nebeneinander auf Getränke. Ein Bildwechsel verändert keine Nährwerte.

Unter **Suchbegriffe und BLS-Synonyme** eigenen Begriff anlegen, Sprache festlegen, BLS-Lebensmittel auswählen und speichern. Ein Synonym findet ein Lebensmittel auch ohne Namensübereinstimmung. Dort kannst du gelernte Zuordnungen verwalten/vergessen. Das verändert Vorschläge, keine BLS-Nährwerte oder alten Mahlzeiten. [Suchpräferenzen](SEARCH_PREFERENCES.md).

Unter **API für Kurzbefehle** kannst du den vorhandenen API-Schlüssel ausdrücklich anzeigen/kopieren. Er gehört in den Authorization-Header deines Kurzbefehls, nicht als Passwort in die Anmeldung oder in eine geteilte URL. Danach ausblenden; Seitenwechsel/Abmelden leeren die Anzeige. Fehlt die Konfiguration, muss der Schlüssel auf dem Server gesetzt werden.

## 13. KI-Importe und iPhone-Kurzbefehle

Friss ruft für dich kein externes KI-Modell und keine kostenpflichtige KI-API auf. Verwende deine gewählte KI-App beziehungsweise deinen Kurzbefehl separat. Es gibt drei unterschiedliche Formate:

| Ablauf | Eingabe und Nährwertbasis |
| --- | --- |
| Browser-JSON-Import / `/json-import/preview` und `/commit` | `friss-meal-v1`-Lebensmittelliste mit Datenbankverweisen oder ausdrücklicher Nährwertbasis (`100g`, `100ml` oder `total`, soweit vom Format unterstützt). Vor dem Speichern prüfen. |
| Direktes `POST /json-import` | `timestamp`, `original_message`, `ai`; Modellnährwerte gelten **für die ganze verzehrte Mahlzeit**. |
| BLS: `GET /bls/search`, `POST /bls/meals/preview`, `POST /bls/meals` | Echte BLS-Codes suchen, anschließend `items` mit `bls_code` und `grams` übergeben. **Friss berechnet Nährwerte.** |

Formate nicht vertauschen und Mahlzeiten-Gesamtwerte nicht nochmals mit dem Gewicht multiplizieren. Aufrufe verwenden `Authorization: Bearer DEIN_API_KEY`; JSON-POSTs zusätzlich `Content-Type: application/json`. Der Zeitpunkt benötigt eine Zeitzone, etwa `2026-11-07T12:30:00+01:00`.

Beim direkten KI-Import lässt du `ai` im Kurzbefehl als vollständigen Antworttext. Die JSON-Erzeugung übernimmt das korrekte Maskieren. IDs erzeugt der Server. Wiederhole bei Fehlern exakt dieselbe Anfrage mit demselben Zeitpunkt und KI-Text, damit keine Duplikate entstehen. Geänderte Daten erzeugen einen neuen Import, keine Bearbeitung des alten.

Beim BLS-Import erkennt die KI zuerst Lebensmittel. Der Kurzbefehl führt HTTP-Suchen aus, gibt die Ergebnisse an das Modell zurück und übermittelt anschließend nur echte Codes und positive Grammengen. Zuerst Vorschau verwenden. Das Modell erhält durch eine URL im Prompt nicht automatisch Zugang zu deinem privaten Server. Ein Stapel erzeugt einen Tagebucheintrag pro Lebensmittel, kein gespeichertes Rezept.

Optionale Originalfotos kannst du nach erfolgreichem Import mit `PUT /entries/{id}/photos` als Bilddatei hochladen. Ein Uploadfehler macht die Mahlzeit nicht rückgängig. Eintrags-ID behalten und nur den Upload wiederholen. HEIC vorher zu JPEG konvertieren; unterstützt sind statische JPEG/PNG/WebP bis jeweils 15 MiB/40 Megapixel, höchstens 20 Fotos je Eintrag. Identische Dateibytes beim selben Eintrag werden nicht doppelt gespeichert.

Vollständige Beispiele: [KI-Kurzbefehl und Fotos](AI_SHORTCUT.md) (Englisch) · [BLS-Ablauf und Prompt](BLS_API.md) · [Browser-JSON-Format](JSON_IMPORT.md) · [KI-Beispielanfrage](examples/ai-meal.json).

## 14. Datensicherung und Wiederherstellung

Unter **Einstellungen → Datensicherung und Wiederherstellung** wählst du **Sicherung herunterladen** und speicherst die ZIP getrennt vom Server. Sie enthält Daten-JSON, effektiv verwendete BLS-Lebensmittel, Tagebuch-/Rezeptmomentaufnahmen, eigene Lebensmittel, Favoriten, Einstellungen, Suchpräferenzen, Schnellwahlbilder, Exportstatus und archivierte Originaldateien/Fotos.

Nicht enthalten sind Passwörter, API-Schlüssel, `.env`, Sitzungen und Programmcode. Das Archiv enthält unverschlüsselte persönliche Daten; bewahre es geschützt auf. Ein Health-Tagesexport ist keine Datensicherung.

Wiederherstellen:

1. Kompatible Friss-ZIP auswählen und **Sicherung prüfen** wählen.
2. Vorschau prüfen; bis dahin wird nichts geändert.
3. **Daten wiederherstellen** wählen und Ersetzen bestätigen. Die Wiederherstellung **ersetzt** vorhandene Datensätze und Original-/BLS-Dateien; sie führt nichts zusammen.
4. Friss legt vorher eine Wiederherstellungs-ZIP unter `data/recovery/` ab. Nach dem Neuladen Tagebuch, Rezepte und Einstellungen kontrollieren, bevor du die heruntergeladene Sicherung verwirfst.

Server-Zugangsdaten bleiben unverändert. Apple Health wird nicht wiederhergestellt oder geändert; Exportkennzeichnungen entsprechen dem Backup-Zeitpunkt und können hinter tatsächlich erfolgten Health-Schreibvorgängen zurückliegen. Vor erneutem Export Health prüfen. Verwende die normale Einzel-Worker-Konfiguration und führe währenddessen keine unabhängigen Datenbank-/Dateiskripte aus. [Ausführliche Anleitung und Grenzen](BACKUPS.md) (Englisch).

## 15. Serverinstallation und Updates

Für eine bestehende Installation im Repository-Verzeichnis ausführen:

```bash
./update.sh
```

Das aktualisiert den Branch `server`, baut/startet Docker und prüft den Start. Einen Fork vorher synchronisieren. Datenbank-/Konfigurationssicherungen des Updaters ersetzen keine vollständige heruntergeladene ZIP oder Serversicherung.

Für eine neue Debian-/Docker-Installation sind die grundlegenden Administratorschritte:

```bash
git clone --branch server --single-branch https://github.com/philipptillmann/friss.git
cd friss
cp .env.example .env
mkdir -p data/bls data/originals
```

In `.env` einen zufälligen API-Schlüssel mit mindestens 32 Zeichen, die LAN-/VPN-Bind-IP des Servers und einen freien Port (Standard 8001) setzen. Passwort mit `python3 scripts/set-password.py` einrichten. Kompatible BLS-JSON nach `data/bls/` kopieren, anschließend:

```bash
sudo chown -R 10001:10001 data
docker compose up -d --build
```

BLS-Quelldaten werden nicht über Git mitgeliefert; eine kompatible Friss-Sicherung kann die effektiven Lebensmittel ebenfalls wiederherstellen. Die Repository-URL ist kleingeschrieben. Das Verzeichnis einer alten Installation kann weiterhin `Friss` heißen.

Dienst im vertrauenswürdigen LAN/VPN belassen. Für Zugriff außerhalb einer vertrauenswürdigen verschlüsselten Verbindung HTTPS verwenden; den Port nicht einfach öffentlich im Router freigeben. Bei HTTPS passend `FRISS_COOKIE_SECURE=true` setzen. Kamera-/Dateiauswahl hängt vom Browser ab; volle PWA-Funktionen benötigen einen sicheren Kontext.

Passwort ändern: Passwortskript ausführen und Container neu erstellen; alte Sitzungen werden ungültig. Das Passwortskript ändert den API-Schlüssel nicht. `.env` und Infrastruktur separat sichern.

## 16. Probleme lösen

| Problem | Prüfen/Handeln |
| --- | --- |
| Seite nicht erreichbar | Server/Docker aktiv, richtiger Port/IP/Hostname, VPN verbunden. Bei Namensauflösungsproblemen IP versuchen. |
| Container startet nicht | `docker compose logs --tail=100` ausführen. Bei belegtem Port freien `FRISS_PORT` wählen; Datenrechte müssen UID 10001 erlauben. Nicht Daten zurücksetzen/löschen, um Startprobleme zu beheben. |
| API verlangt Anmeldung | Authorization-Header auf `Bearer ` plus API-Schlüssel setzen. Die Browseranmeldung authentifiziert keinen separaten Kurzbefehl. |
| Ungültiges JSON | Richtiges Endpunktformat verwenden und Wörterbücher/Text durch Kurzbefehle serialisieren lassen. Gemeldete Zeile/Spalte prüfen, nicht blind Klammern ändern. |
| Keine BLS-Treffer | Prüfen, ob kompatible BLS-Daten geladen sind. Kürzeren Begriff oder eigenes Synonym versuchen; `/bls/search` zeigt die Gesamtzahl der Datenbank. |
| Produkt nicht gefunden / Webimport scheitert | Barcode kann bei Open Food Facts fehlen oder Quellseite geändert/unerreichbar sein. Manuelles Lebensmittel oder andere unterstützte Quelle verwenden. |
| Eintrag bleibt offen | Öffnen und gewähltes Lebensmittel, Menge, g-/ml-Basis sowie Quelleinheiten prüfen. Nullannahmen ersetzen keine fehlende Zuordnung/Menge. |
| Ziele nicht sichtbar | Einstellungen speichern, Home öffnen, bei Bedarf neu laden; dieselbe Server-URL/Sitzung prüfen. |
| Health-Export blockiert/unklar | Begründung lesen, offene Einträge/Einheiten klären und vorhandene Health-Werte vor Wiederholung prüfen. |
| Oberfläche nach Update veraltet | Seite neu laden/öffnen. Bei Icon-Änderung gegebenenfalls Home-Screen-Verknüpfung entfernen und neu hinzufügen; Serverdaten bleiben erhalten. |

Bei Fehlermeldungen App-Version, Seite, genaue Schritte und Fehlertext angeben. API-Schlüssel, Passwörter und persönliche Daten in Logs/Screenshots schwärzen.

## 17. Essensplanung, Vorrat und Einkaufsliste

Unter **Essensplanung** Rezepte/Getränke mit Menge und Vorbereitungsnotizen terminieren. **Vorbereitet** hält den Vorbereitungsstand fest; erst **Als gegessen eintragen** mit tatsächlichem Zeitpunkt bucht den Verzehr. Pläne behalten ihren gespeicherten Rezeptstand. **Vorrat** enthält verknüpfte Lebensmittelmengen und Datumshinweise. Die **Einkaufsliste** fasst Zutaten des Zeitraums zusammen und zieht passenden Vorrat ab; Häkchen und manuelle Artikel ergänzen die Liste.

Planung und Vorrat lassen sich in Einstellungen unabhängig ausschalten, ohne Daten zu löschen. Einkaufen bleibt verfügbar. Bestand wird manuell gepflegt: Essen und Abhaken ändern ihn nicht. Sicherungen enthalten die neuen Daten. [Vollständiger deutscher/englischer Ablauf mit Grenzen und API](PLANNING.md).

## 18. Posteingang für unfertige Einträge

Im **Posteingang** Text, Bilder oder beides mit Originaldatum/-zeit speichern. Unfertige Einträge zählen nicht zu Nährwerten, Statistik, BAC oder Health. Entwurf öffnen, Originale prüfen, Lebensmittel/Rezept samt Menge und Zeitpunkt wählen und ausdrücklich zu genau einem Tagebucheintrag abschließen. Text und Fotos bleiben erhalten. Unbekannte Mengen dürfen bis später offen bleiben.

Ein Kurzbefehl kann Zeit/Text/Titel per POST an `/inbox` senden und anschließend Bilddateien per PUT an `photo_upload_url` hochladen. Nährwerte, KI-Antwort und eigene UUID sind nicht nötig. Identische Wiederholungen vermeiden Duplikate. Sicherungen enthalten den Posteingang. [Vollständige deutsche/englische Anleitung und API](INBOX.md).
