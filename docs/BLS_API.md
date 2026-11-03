# Mahlzeiten aus BLS-Lebensmitteln per API (ab 1.41.0)

Neben `POST /json-import` für mitgelieferte KI-Nährwerte gibt es jetzt einen zweiten Weg: **BLS suchen → Codes und Gramm übergeben → Friss berechnet die Nährwerte**. Die KI muss keine Nährstofflisten erzeugen und keine BLS-IDs auswendig kennen. Die lokale BLS-Datenbank auf dem Server bleibt erforderlich.

Alle Aufrufe verwenden denselben API-Schlüssel aus den Einstellungen:

```http
Authorization: Bearer DEIN_API_KEY
```

Bei POST zusätzlich `Content-Type: application/json`. Die API ist über dein Heimnetz/VPN erreichbar. Ein KI-Modell in der ChatGPT-App hat dadurch nicht automatisch Zugriff auf deinen privaten Server. Im Kurzbefehl müssen die Suchaufrufe ausgeführt und deren Ergebnisse wieder an das Modell übergeben werden. Ein KI-Agent mit HTTP-Werkzeugen kann die Aufrufe selbst ausführen.

## 1. Kandidaten suchen

```http
GET http://spiesserver:8001/bls/search?q=Milch&lang=de&limit=10
```

`q`: 1–200 Zeichen, `lang`: `de` oder `en`, `limit`: 1–100, Standard 10. Die persönliche BLS-Sortierung einschließlich Synonymen wird verwendet. Die kompakte Antwort enthält keine vollständigen Nährstofflisten:

```json
{
  "query": "Milch",
  "lang": "de",
  "database_count": 10000,
  "results": [
    {
      "bls_code": "CODE_AUS_DEINER_DATENBANK",
      "name": "Vollmilch 3,5 % Fett",
      "name_de": "Vollmilch 3,5 % Fett",
      "name_en": "Whole milk 3.5% fat",
      "quantity_unit": "g",
      "nutrition_basis": "100g",
      "synonym": null
    }
  ]
}
```

Bezeichnungen, Anzahl und Codes oben sind nur ein Formatbeispiel. **Nur tatsächlich zurückgegebene Codes verwenden.** `database_count` ist die Gesamtzahl aller lokal vorhandenen BLS-Lebensmittel, nicht die Anzahl der Treffer. Bei leerer Datenbank oder erfolgloser Suche ist `results` leer. In dem Fall Suchbegriff ändern; keine ID erfinden. Die bestehende API `GET /foods?q=...` liefert bei Bedarf ausführliche BLS-Datensätze mit Nährwerten.

## 2. Vorschau oder Eintragen

Vorschau: `POST /bls/meals/preview`. Speichern: `POST /bls/meals`. **Beide verwenden exakt denselben Body:**

```json
{
  "timestamp": "2026-11-03T12:30:00+01:00",
  "title": "Milch mit Zimt",
  "original_message": "150 g Vollmilch und 2 g Zimt",
  "items": [
    {"bls_code": "MILCH_CODE_AUS_SUCHE", "grams": 150},
    {"bls_code": "ZIMT_CODE_AUS_SUCHE", "grams": 2, "notes": "Menge geschätzt"}
  ]
}
```

Die Beispielcodes vor dem Senden durch Suchergebnisse ersetzen.

- `timestamp` ist erforderlich, mit Zeitzone (ISO 8601). Im Kurzbefehl selbst setzen.
- `title`, `original_message` und `notes` sind optional.
- `items` enthält 1–100 Lebensmittel, je ein echter `bls_code` und eine positive `grams`-Zahl. **Keine Nährwerte und keine UUID erforderlich.**
- Auch Getränke aus BLS benötigen Gramm. Keine Gleichsetzung von ml und g ohne bekannte Dichte. Unbekannte Mengen zuerst klären; fehlende Mengen werden in dieser API abgelehnt.
- Die Vorschau zeigt pro Lebensmittel die berechneten Nährwerte für die angegebene Menge, Status und Warnungen. Sie schreibt keine Dateien oder Einträge. Fehlende Werte und Kennzeichnungen wie `TR` bleiben unbekannt.
- Speichern legt einen normalen Tagebucheintrag pro Lebensmittel an, mit BLS-Quelle, derselben Zeit, gemeinsamem Mahlzeitentitel und Originaltext in den Importmetadaten. Es entsteht kein gespeichertes Rezept. Die Einträge funktionieren mit Tageswerten und dem vorhandenen Health-Export.
- Alle Lebensmittel werden vor dem Schreiben geprüft und gemeinsam gespeichert. Unbekannter Code, ungültige Menge oder fehlende Zeitzone ergibt `422`, ohne teilweise eingetragene Mahlzeit.

Speicherantwort (HTTP 201):

```json
{
  "id": "SERVER_GENERIERTE_BATCH_UUID",
  "status": "completed",
  "count": 2,
  "entry_ids": ["EINTRAG_UUID_1", "EINTRAG_UUID_2"],
  "needs_review": 0,
  "title": "Milch mit Zimt",
  "timestamp": "2026-11-03T12:30:00+01:00",
  "source": "BLS"
}
```

Details abrufen: `GET /entries/EINTRAG_UUID_1`. `needs_review: 0` heißt, dass die Verarbeitung abgeschlossen ist, nicht dass jeder Mikronährstoff in der Quelle bekannt ist. Prüfe fehlende Nährwerte in der Vorschau oder Tagesprüfung.

Friss erzeugt alle IDs. Derselbe Body mit demselben Zeitpunkt erzeugt beim Wiederholen keine Duplikate; nach Netzwerkfehlern **unverändert erneut senden**. Ein veränderter Body, etwa mit anderer Zeit oder Menge, ist eine neue Mahlzeit und keine Korrektur. Zur Korrektur bestehende Einträge bearbeiten/löschen. Nach dem Löschen lässt sich derselbe Import nicht durch Wiederholung wiederherstellen.

## 3. iPhone-Kurzbefehl

1. Foto/Beschreibung erfassen und Datum/Uhrzeit festlegen. Zeitpunkt einmal als ISO 8601 mit Zeitzone formatieren und für alle Wiederholungen behalten.
2. KI bitten, eine kurze Liste von Lebensmitteln und Grammengen zu erkennen. Bei Fotos Schätzungen kennzeichnen.
3. Pro Lebensmittel mit **Inhalt von URL abrufen**, Methode GET, `/bls/search?q=SUCHBEGRIFF&lang=de` aufrufen. Suchbegriff URL-kodieren und den Authorization-Header setzen.
4. Suchergebnisse zusammen mit der Beschreibung an die KI geben. Sie wählt aus den echten Codes aus und liefert das kleine JSON unten. Bei mehreren Durchläufen alle endgültig gewählten Lebensmittel sammeln.
5. Ein Wörterbuch mit `timestamp`, `original_message`, dem KI-`title` und der KI-`items`-Liste erstellen. `items` als Liste übernehmen, nicht als JSON-Text in Anführungszeichen. Kein `raw`- oder `ai`-Feld verwenden.
6. Zunächst per POST an `/bls/meals/preview` senden und anzeigen. Zum Buchen denselben Body per POST an `/bls/meals` senden. Als Request Body **JSON** wählen, beide Header setzen.

### Nachricht an das Modell nach der Suche

> Wähle für meine Mahlzeit passende Lebensmittel ausschließlich aus den beigefügten BLS-Suchergebnissen. Antworte nur mit einem JSON-Objekt mit title und items. Jedes Element von items enthält bls_code und grams (positive Zahl), optional notes. Nutze nur Codes, die in den Suchergebnissen tatsächlich vorkommen. Keine Nährwerte, keine IDs und keine Zeitstempel erzeugen. Beachte roh/gegart, Fettstufe und Produktart. Keine Doppelzählung von Gericht und Zutaten. Verwende die verzehrte Grammmenge; Schätzungen in notes kennzeichnen. Keine ml-zu-g-Umrechnung ohne bekannte Dichte. Wenn kein passender Treffer oder keine belastbare Menge vorhanden ist, gib {"title":"Rückfrage erforderlich","items":[]} zurück; der Kurzbefehl muss dann stoppen und Rückfrage oder neue Suche ermöglichen. Namen und Hinweise auf Deutsch.
>
> Meine Beschreibung: [Originaltext und erkannte Lebensmittel/Mengen]
>
> BLS-Suchergebnisse: [Antworten aus Schritt 3]

Der Kurzbefehl muss die Rückfrage erkennen (`items` leer) und darf dann nicht speichern. Beispiel der erwarteten KI-Antwort, wiederum mit echten Codes aus der Suche zu ersetzen:

```json
{
  "title": "Milch mit Zimt",
  "items": [
    {"bls_code": "MILCH_CODE_AUS_SUCHE", "grams": 150},
    {"bls_code": "ZIMT_CODE_AUS_SUCHE", "grams": 2}
  ]
}
```

Das Foto muss dafür nicht zur Berechnung auf Friss hochgeladen werden. Bei Bedarf kann es anschließend über die bestehende Foto-API an eine zurückgegebene Eintrags-ID angehängt werden.
