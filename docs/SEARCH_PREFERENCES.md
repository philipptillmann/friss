# Suchbegriffe, BLS-Synonyme und gelernte Vorschläge (ab v1.36.0)

Unter **Einstellungen → Suchbegriffe und BLS-Synonyme** verwaltest du eigene Begriffe und bisher gelernte Suchzuordnungen.

## Eigenes Synonym anlegen

1. **Neues Synonym** wählen.
2. Den gewünschten Suchbegriff eingeben, z. B. **Backwürfel** oder **Zucker für Kaffee**.
3. Sprache der Suche auswählen: Deutsch oder Englisch.
4. Unter **BLS-Lebensmittel auswählen** nach dem tatsächlichen Lebensmittel suchen, z. B. **Haushaltszucker**. Einen Treffer anklicken; die gewählte Bezeichnung und der BLS-Code erscheinen darunter.
5. Speichern.

Suchst du danach auf Deutsch nach „Backwürfel“, schlägt Friss den ausgewählten BLS-Datensatz vor, auch wenn dieser Begriff in dessen Namen nicht vorkommt. Der Treffer bleibt als BLS gekennzeichnet; in der gemeinsamen Suche wird das passende Synonym daneben angezeigt. Es gilt ebenfalls in BLS-Suchen für Rezeptzutaten und anderen Eingabemasken.

- Vollständige passende Synonyme haben Vorrang, danach passende Synonym-Anfänge, danach bisherige gelernte/gewöhnliche Treffer. Du kannst also bereits nach „backw“ suchen.
- Groß-/Kleinschreibung, Akzente und Mehrfach-Leerzeichen werden wie in der bisherigen Suche normalisiert. Die eingegebene Schreibweise bleibt in der Verwaltung erhalten.
- Die Sprachzuordnung gilt für die Sprache der jeweiligen Suche. Für denselben Begriff können bei Bedarf deutsche und englische Zuordnungen angelegt werden.
- Ein Begriff kann mehrere BLS-Lebensmittel vorschlagen. Derselbe Begriff/Sprache/BLS-Code lässt sich nicht doppelt anlegen. Begriffe sind auf 80 Zeichen begrenzt.
- Ein Synonym ändert nur die Suche, keine Namen oder Nährwerte im BLS und keine bereits gespeicherten Mahlzeiten, Zutaten oder Rezepte.

## Bearbeiten und Löschen

In **Eigene Synonyme** auf **Bearbeiten** klicken, Suchbegriff/Sprache und bei Bedarf das BLS-Ziel ändern und speichern. **Löschen** entfernt das Synonym nach Bestätigung. Wenn das Lebensmittel weiterhin zum gewöhnlichen Namenstext passt, kann es danach als normaler Treffer erscheinen.

In **Gelernte Suchvorschläge** stehen bisherige Zuordnungen aus BLS- und gemeinsamer Suche, mit Sprache, Quelle und Anzahl der Auswahlen. Friss zählt denselben BLS-Klick, der technisch in beiden Suchhistorien gespeichert wurde, nur einmal.

- **Zuordnung bearbeiten** übernimmt den Begriff in das Formular. Bei einer BLS-Zuordnung ist das Ziel bereits ausgewählt; bei anderen Quellen wählst du ein BLS-Ziel. Beim Speichern wird diese gelernte Zuordnung durch dein eigenes Synonym ersetzt. Begriff und Sprache lassen sich dabei ebenfalls ändern.
- **Löschen** vergisst genau diese gelernte Zuordnung in beiden Suchhistorien. Das Lebensmittel selbst wird nicht gelöscht und kann in einer normalen Textsuche weiterhin auftauchen. Bei einer erneuten bewussten Auswahl kann Friss die Zuordnung wieder lernen; Löschen ist keine dauerhafte Sperrliste.
- **Suchbegriff oder Lebensmittel filtern** durchsucht die Begriffe sowie die deutschen/englischen Zielnamen und IDs. Bei mehr als 200 Ergebnissen je Liste den Filter weiter eingrenzen.

Wenn ein BLS-Datensatz später fehlt, ist sein Synonym in der Verwaltung als fehlend markiert. Du kannst es neu zuordnen oder löschen.

## Sicherung und Wiederherstellung

ZIP-Backups enthalten eigene Synonyme und die gelernten Suchhistorien. Die Wiederherstellung einer älteren Sicherung ohne Synonyme bleibt möglich; sie stellt diese ältere Datenlage **ohne eigene Synonyme** wieder her und ersetzt damit auch inzwischen angelegte Synonyme. Vor einer Wiederherstellung wie gewohnt eine aktuelle Sicherung aufbewahren.

## API

Alle Endpunkte benötigen die bestehende Authentifizierung:

- `GET /food-search/preferences?q=…`: eigene Synonyme und aggregierte gelernte Zuordnungen, maximal 200 Treffer pro Liste und Gesamtanzahlen für den Filter.
- `POST /food-search/synonyms`: `id` als UUID, `query`, `lang` (`de`/`en`), `bls_code`, `version: 0`. Optional `replace_learned` mit `query`, `lang`, `source`, `target` für die Umwandlung einer gelernten Zuordnung.
- `PUT /food-search/synonyms/{id}`: dieselben editierbaren Felder und die aktuelle `version`; die Version wird bei Änderungen erhöht.
- `DELETE /food-search/synonyms/{id}?version=…`: genau dieses Synonym löschen.
- `DELETE /food-search/preferences`: JSON mit `query`, `lang`, `source`, `target`, um genau eine gelernte Zuordnung zu vergessen.

Versionskonflikte überschreiben keine fremden Änderungen; die aktuelle Zuordnung vor weiterem Bearbeiten neu auswählen.
