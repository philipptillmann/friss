# Unfinished-entry inbox · Posteingang · v1.43.0

## English

Use **Inbox** to capture meals you cannot fully enter yet. Save **text, pictures, or both**, together with a capture timestamp and optional short title. Items are kept separately from diary entries, sorted newest capture first. They contribute **nothing** to Home, statistics, BAC or Health until explicitly completed.

### In the app

1. Open Inbox. Check the capture date/time (default now), optionally add a title, and type a description and/or use **Take a photo / Choose pictures**.
2. **Save unfinished entry** creates the draft and uploads its selected pictures. Wait for completion before leaving. If a picture upload fails, the draft already exists: repeat the same save to retry the pictures, or reopen the draft and attach the missing files. The original text/time are frozen for a save retry; **Clear / new capture** starts a new form without deleting a saved draft.
3. The list defaults to Unfinished. Choose Completed/All if needed; **Load more** retrieves older entries. Times are displayed in your browser timezone; sorting uses their actual instants, including different timezone offsets.
4. **Continue entry** opens original text, capture time and pictures. Click a picture to view its original. Additional pictures can be appended while unfinished.
5. Search for a BLS food, manual food, Open Food Facts product or saved recipe/drink. Select a result, enter the consumed amount/unit and confirm meal time. It defaults to the original capture time, not the time you finish processing the draft.
6. **Complete and log meal** creates one normal diary entry. The draft moves to Completed and links to that entry. Its original description, capture time and photographs are retained. Recipes use the usual portion/fraction/finished-weight/volume rules; foods require their correct g/ml basis. Incomplete or failed food resolution leaves the draft unfinished.

No recognition model runs in this inbox. You decide which food/recipe represents the capture. An unknown amount can remain pending until you know it. Completion currently creates **one food/product or one saved recipe** per draft; it does not split a description/photo into several ingredients. More conversion methods can be added later.

Delete a draft after confirmation if not needed. A completed diary entry is not deleted by deleting its inbox item. Archived originals and pictures remain on disk/in backups; this is not full data erasure. Conversely, deleting a diary entry does not reopen its draft. Repeating the same completion never creates a replacement or second entry. Open the diary entry to correct an already completed meal.

### Shortcut API

All requests need the usual header:

```http
Authorization: Bearer YOUR_FRISS_API_KEY
```

#### 1. Create the metadata/text draft

`POST http://spiesserver:8001/inbox` with `Content-Type: application/json`:

```json
{
  "timestamp": "2026-11-10T12:30:00+01:00",
  "title": "Lunch",
  "text": "Pasta at the restaurant; amount to check later."
}
```

`timestamp` is required and must include a timezone. `text` (up to 10,000 characters) and `title` (up to 200) are optional. For a photo-only capture, use empty text or omit it, then upload the photo in step 2. Metadata-only drafts are allowed for this two-stage workflow; do not assume the server received a picture until its upload succeeds. EXIF capture time is not automatically read; set timestamp in the Shortcut.

HTTP 201 returns:

```json
{
  "id": "SERVER_GENERATED_UUID",
  "timestamp": "2026-11-10T12:30:00+01:00",
  "title": "Lunch",
  "text": "Pasta at the restaurant; amount to check later.",
  "created_at": "2026-11-10T11:31:00+00:00",
  "status": "pending",
  "photos": [],
  "photo_upload_url": "/inbox/SERVER_GENERATED_UUID/photos"
}
```

The server generates the UUID. Retrying exactly the same timestamp/text/title returns the same draft. Keep the chosen timestamp and text unchanged during retries. A genuinely new capture needs a new timestamp (preserve sufficient precision), or different content; two identical captures at exactly the same time are treated as one. Deleted captures replay as `status: deleted`, not a new item.

#### 2. Upload pictures separately

`PUT http://spiesserver:8001` + `photo_upload_url` with the actual **binary image file** as the body, and `Content-Type: image/jpeg`, `image/png` or `image/webp`.

In Shortcuts use **Get Contents of URL → Method PUT → Request Body File**, not JSON/Form/base64. For several photos, **Repeat with Each** and upload to the same URL. Static JPEG/PNG/WebP are supported, up to 15 MiB and 40 megapixels each, maximum 20 images per draft. Convert HEIC to JPEG in the Shortcut first and keep the converted file for retries. Accepted bytes are stored without recompression. The browser also converts unsupported formats where it can decode them; keep JPEG/PNG/WebP files for best compatibility.

HTTP 200 returns photo `id`, `url`, `size` and `content_type`. Repeating identical bytes for the same draft does not duplicate the photo. A photo failure does not undo metadata/text: keep the returned draft ID and retry the upload only. Once completed, attach new images to the diary's `/entries/{entry_id}/photos` endpoint instead; inbox uploads are then rejected.

Text-only Shortcut: collect text and time → POST metadata → done. Photo/text Shortcut: collect photos/text/time → POST metadata → keep returned id/url → repeat binary PUT for each picture → done. No AI prompt, nutrients or client-generated UUID is required.

#### Reading and completing

- `GET /inbox?status=pending&limit=100&offset=0`: object with `items`, `total`, `limit`, `offset`. Status may be `pending`, `completed` or `all`; limit 1–500.
- `GET /inbox/{id}`: metadata/status and photo URLs.
- `GET /inbox/{id}/photos`: photo metadata list.
- `GET /inbox/{id}/photos/{photo_id}`: authenticated original image.
- `DELETE /inbox/{id}`: hides the draft; does not delete a diary entry or archive files.
- `POST /inbox/{id}/complete`: selected source and quantity. Example:

```json
{
  "source": "bls",
  "source_id": "REAL_CODE_FROM_SEARCH",
  "amount": 250,
  "unit": "g"
}
```

Use a real BLS code from `/bls/search` or `/search`. Other sources are `manual` (food UUID), `off` (barcode), or `recipe` (saved recipe UUID). Food units are g/ml matching the data; recipes support portion/fraction/g/ml with existing rules. Optional `timestamp` overrides the meal time without changing original capture metadata; optional `finished_at` supports drink duration. Timezones are required. The server calculates nutrients and returns `{id, status: "completed", entry_id}`. Health remains pending until separately exported.

An unchanged successful completion can be safely repeated. Different data after completion is rejected; refresh details and edit the diary instead. Unknown foods, invalid amounts/units or failed lookups do not complete the draft.

### Storage and backups

Inbox records, status and original text/metadata are stored separately in SQLite. Captures are also archived under `data/originals/inbox-<id>.json`; image files are stored as immutable originals. Completion copies images to the generated diary ID and stores its provenance. Friss ZIP backups include inbox data/files. Older backups restore with an empty inbox; restore new archives using v1.43.0 or newer. Credentials remain excluded as before.

## Deutsch

**Posteingang** erfasst unfertige Mahlzeiten als **Text, Bilder oder beides**, mit Aufnahmezeitpunkt und optionalem Titel. Die Liste ist nach Aufnahmezeit absteigend sortiert. Entwürfe bleiben getrennt vom Tagebuch und zählen bis zum Abschließen **nicht** zu Home, Statistik, BAC oder Health.

### Bedienung

1. Posteingang öffnen, Datum/Uhrzeit prüfen (Standard jetzt), Titel/Text und/oder Fotos erfassen. **Unfertigen Eintrag speichern** legt den Entwurf an und lädt ausgewählte Bilder hoch.
2. Bei fehlgeschlagenem Bild-Upload existiert der Entwurf bereits. Dieselbe Speicherung wiederholen oder Entwurf öffnen und fehlende Bilder anhängen. Für Wiederholungen bleiben Text/Zeit eingefroren; **Leeren / neue Erfassung** leert nur die Maske und löscht keinen gespeicherten Entwurf.
3. Unfertige/Abgeschlossene/Alle auswählen und bei Bedarf ältere Einträge mit **Mehr laden** abrufen. Die Anzeige verwendet deine Browserzeitzone; sortiert wird nach tatsächlichem Zeitpunkt.
4. **Eintrag fortsetzen** zeigt Originaltext, Zeit und Bilder. Bilder öffnen das Original. Solange unfertig, lassen sich weitere Bilder anhängen.
5. Lebensmittel oder Rezept suchen/auswählen, Menge/Einheit und Verzehrzeit prüfen. Die Zeit ist mit dem ursprünglichen Aufnahmezeitpunkt vorbelegt.
6. **Abschließen und Mahlzeit eintragen** erzeugt genau einen normalen Tagebucheintrag. Der Entwurf wird abgeschlossen und verlinkt den Verzehr. Originalbeschreibung, Aufnahmezeit und Bilder bleiben erhalten. Rezeptmengen folgen den bekannten Regeln, Lebensmittel benötigen ihre passende g-/ml-Basis. Fehlende Angaben oder fehlgeschlagene Auflösung lassen den Entwurf offen.

Hier läuft kein KI-Modell. Die Zuordnung erfolgt bewusst durch dich. Eine unbekannte Menge darf bis später offen bleiben. Aktuell wird pro Entwurf **ein Lebensmittel/Produkt oder ein gespeichertes Rezept** gebucht; keine automatische Zerlegung eines Fotos/Textes in mehrere Zutaten. Weitere Umwandlungsmethoden können später ergänzt werden.

Löschen erfordert eine Bestätigung, entfernt keinen fertigen Tagebucheintrag und löscht archivierte Originale/Fotos nicht aus dem Dateisystem oder Backups. Umgekehrt öffnet das Löschen eines Verzehrs seinen Entwurf nicht erneut. Wiederholen einer abgeschlossenen Umwandlung erzeugt keinen neuen Verzehr. Bestehenden Verzehr im Tagebuch korrigieren.

### iPhone-Kurzbefehl

1. Text/Fotos und Datum sammeln; Datum einmal als ISO 8601 **mit Zeitzone** formatieren.
2. **Inhalt von URL abrufen**, POST an `http://spiesserver:8001/inbox`, Header `Authorization: Bearer DEIN_API_KEY` und `Content-Type: application/json`.
3. JSON-Felder `timestamp`, optional `text` und `title` verwenden. Bei reinem Foto Text leer lassen. UUID kommt vom Server. EXIF-Zeiten werden nicht automatisch übernommen.
4. Antwort-ID und `photo_upload_url` behalten. Für jedes Bild PUT an Serverbasisadresse plus diesen Pfad, Request Body **Datei**, Content-Type passend zum Bild. Kein base64, kein JSON-Bildfeld. HEIC vorher in JPEG konvertieren; JPEG/PNG/WebP bis 15 MiB/40 Megapixel, maximal 20 je Entwurf.
5. Metadaten und Bilder sind getrennte Schritte: Erst ein erfolgreicher Bild-Upload bestätigt das gespeicherte Foto. Bei Fehlern nur den fehlenden Schritt wiederholen und dieselben Daten/Dateien behalten.

Identische Zeit/Text/Titel ergeben beim Wiederholen denselben Entwurf. Für eine neue Erfassung neuen, ausreichend genauen Zeitpunkt verwenden; identische Erfassungen im exakt gleichen Moment werden zusammengefasst. Identische Bildbytes je Entwurf erzeugen kein Duplikat. Nach Abschließen neue Bilder am Tagebucheintrag hochladen.

API-Beispiele und Feldgrenzen stehen oben. Die API unterstützt Lesen, Löschen und explizites Abschließen mit BLS/eigenem Lebensmittel/Barcode/Rezept, übernimmt aber keine unbegründete g-/ml-Umrechnung. Abweichende Abschlussdaten nach erfolgter Buchung werden abgelehnt; Details aktualisieren und Verzehr bearbeiten. Health bleibt ein separater Export.

ZIP-Sicherungen enthalten Entwürfe, Status und Originaldateien. Alte Sicherungen ergeben einen leeren Posteingang; neue Archive mit Friss 1.43.0 oder neuer wiederherstellen. Zugangsdaten bleiben wie bisher ausgeschlossen.
