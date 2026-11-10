# Friss user manual

**For version 1.43.0 · Updated 10 November 2026**
[Deutsches Handbuch](USER_MANUAL_DE.md) · [Project overview](../README.md)

Friss is a self-hosted food and drink diary. Your server stores entries, original inputs, recipes and nutrient data. You can use the browser on a computer or add the site to your iPhone Home Screen. It is a web app, not a native iPhone app. Apple Health writes require a separate iPhone Shortcut.

## Contents

1. [Getting started](#1-getting-started)
2. [Home and daily values](#2-home-and-daily-values)
3. [Meals and food search](#3-meals-and-food-search)
4. [Entry details, corrections and copying](#4-entry-details-corrections-and-copying)
5. [Drinks, quick adds and BAC](#5-drinks-quick-adds-and-bac)
6. [Recipes](#6-recipes)
7. [Favorites and recently used foods](#7-favorites-and-recently-used-foods)
8. [Manual foods, website import and label scanning](#8-manual-foods-website-import-and-label-scanning)
9. [Understanding nutrients and missing data](#9-understanding-nutrients-and-missing-data)
10. [Statistics and daily audit](#10-statistics-and-daily-audit)
11. [Export to Apple Health](#11-export-to-apple-health)
12. [Settings](#12-settings)
13. [AI imports and iPhone Shortcuts](#13-ai-imports-and-iphone-shortcuts)
14. [Backup and restore](#14-backup-and-restore)
15. [Server setup and updates](#15-server-setup-and-updates)
16. [Troubleshooting](#16-troubleshooting)

17. [Meal planning, fridge inventory and shopping](#17-meal-planning-fridge-inventory-and-shopping)

18. [Unfinished-entry inbox](#18-unfinished-entry-inbox)

## 1. Getting started

Open your server's Friss address, for example `http://spiesserver:8001/`, and sign in with the configured password. Use the actual hostname/IP and port of your installation. The server must be reachable from your device; away from home, connect your VPN first. Friss does not support offline capture.

On iPhone, open the site in Safari, choose **Share → Add to Home Screen**, and launch it from the new icon. Safari and the installed web app may have separate login sessions. Sessions last up to 30 days; signing out or changing the server password ends the applicable sessions. Apple Passwords can help fill the login form.

Choose English or German at the top. The navigation contains **Home, Meals, Drinks, Recipes, Favorites, Manual, Statistics, Export, Settings**, plus **Meal planner, Fridge, Shopping list and Inbox**. Labels below refer to the English interface; button wording may vary slightly with language.

For a first test, set your goals in Settings, search for a food under Meals, enter its amount and save. Check Home and Statistics before setting up Health export or automation.

## 2. Home and daily values

Home always shows **today in your browser's local timezone**. Selecting another date on Meals does not change the day on Home.

- The short progress text and goal cards compare recorded calories/macros with your saved daily targets. Goals are optional and independently configurable.
- The **search** icon opens the food search on Meals. The **barcode** icon opens the barcode capture flow.
- **Nutritional values** lists calories, macros and related main values; **Caffeine / Alcohol** includes caffeine, pure alcohol grams and current estimated BAC; **Micronutrients** contains the further tracked nutrient values.
- Click a nutrient amount to see the entries contributing to it, with any other relevant incomplete entries listed separately.
- Numbers are displayed with at most two decimal places. This does not round the stored source values.

Drink quick-add tiles are on **Drinks**, not Home.

## 3. Meals and food search

Choose the desired diary day and capture method. Check the entry time: it normally starts at now and can be changed. Saving records the entry immediately; Apple Health transfer is separate.

### Shared search

Enter a food name. Friss searches the local **BLS** database, **Open Food Facts**, your **manual foods**, and saved **food/drink recipes** where appropriate. Source tags distinguish the results; favorites carry a star. Food recipes and drink recipes have distinct tags and selections.

Choose the actual result, enter the consumed amount and save. Match details such as raw/cooked, fat percentage and preparation. The search remembers which result you select for that search phrase and language. BLS search also matches word parts: searching **Salz** can suggest **Speisesalz**. Exact names and shorter matches are favored, while your learned choices and explicit synonyms retain priority.

Local results can appear before online Open Food Facts results. If Open Food Facts is unavailable, local searching still works. A product's presence does not guarantee a complete nutrient profile.

### Capture methods

| Method | What to do |
| --- | --- |
| Search | Select a BLS/manual food or recipe and enter the amount in the required unit. BLS uses grams. |
| Barcode | Type the barcode or photograph it. Select the detected code, enter the amount and save. Product data comes from Open Food Facts. |
| Photo | Capture/upload a food photo and retain it as the original input. Ordinary photo capture does not itself recognize the food or its nutrients; assign the food and amount, or use the external AI-import workflow. |
| Text | Enter a description. Ambiguous or unresolved inputs need a database assignment and amount afterward. |
| Recipe / drink | Choose a saved definition and log portions, a fraction, grams or supported milliliters. See the recipe rules below. |
| Manual food | Select one of your saved foods and enter grams or milliliters matching its reference basis. |
| Recently used / favorites | Reuse a previously used food or saved favorite, checking amount and time before saving. |
| JSON import | Paste/upload supported AI JSON, review the draft, then save. See section 13. |

The barcode camera flow uses a photograph rather than a continuous live scanner. A scan alone does not book a meal. If the code cannot be read, try a sharper photograph or enter its digits manually.

An amount may initially be left empty in normal capture. The entry remains for review and can be completed later. This is different from the BLS batch API, which requires a positive gram amount.

## 4. Entry details, corrections and copying

Click an entry under Meals to open its details. These show name, source tag/capture method, amount, time, processing and Health status, and all nutrient contributions in the same order as Home. Attached original photos can be opened there.

- **Change time:** adjust date/time and save. Drink entries can also have a finish time.
- **Reprocess/edit:** the existing food and entered fields are restored. Add the missing amount or change the relevant values, rather than starting the search again.
- **Copy entry:** choose the destination date/time. A new entry retains the saved food/recipe snapshot and nutrients; the original stays in place. The copy starts with Health pending. For drinks, the duration is retained when shifting the time.
- **Delete:** delete an individual entry after confirmation. The day-reset option removes the diary entries for the selected day after confirmation. Check the date carefully.

Recipe ingredients are not separate diary consumption. Edit them inside the recipe rather than copying them as standalone diary meals.

Changes/deletions in Friss do **not** remove or correct samples already written to Apple Health. Original input files are retained on the server even after an entry is deleted; deleting a diary entry is not a full erasure of its archived originals or backups.

## 5. Drinks, quick adds and BAC

The first section on **Drinks** contains quick-add image tiles, four per row. Configure them in Settings. One tap logs the configured drink/recipe and quantity at the current time. A recipe-based cappuccino records its milk/espresso nutrients as well as any known caffeine; it is not merely a caffeine counter.

Below the tiles, choose or create a drink recipe. Food and drink recipes are separate categories. The manual drink entry remains available for water, caffeine and alcohol.

For alcohol, enter either:

- **Pure alcohol in grams**, or
- **Drink volume in ml and alcohol percentage (ABV)**.

Friss calculates pure alcohol as `volume × ABV / 100 × 0.789`. Manual alcohol/ABV capture does not automatically supply all drink calories or other nutrients. Use a product or drink recipe when these are needed.

### Start, finish and the BAC curve

Set the entry time to the first sip. Optionally enter **Last sip**. For a drink crossing midnight, use the next date for the finish. The finish cannot precede the start.

The BAC calculation uses logged alcohol, your body parameters in Settings, absorption and elimination. When a finish is supplied, it assumes uniform drinking between start and finish. Without one, intake is treated as immediate followed by absorption. Several drinks are combined, including those spanning midnight; midnight does not reset the modeled alcohol amount. A future finish makes the remainder a projection.

The drink's **whole nutrient/alcohol amount belongs to the diary day of its start**. The finish only changes the BAC timing. The model cannot know individual sip patterns. BAC is an estimate, not a measurement or a basis for deciding whether it is safe to drive.

## 6. Recipes

On **Recipes**, create a food recipe with a name and total number of portions. Add ingredients using the normal capture methods. Verify that the capture destination is the intended recipe. Ingredients contribute to the recipe, not directly to today's totals or Health.

Click an ingredient row to edit its amount, food or time. An unresolved food or amount must be completed before the recipe can be consumed. Ingredient dates are retained for reference.

### Logging part of a recipe

| Unit | Fraction of recipe used |
| --- | --- |
| Portions | Consumed portions ÷ total portions |
| Fraction | Enter the fraction directly, e.g. `0.25` for one quarter |
| Grams | Consumed grams ÷ **finished total weight** |
| Milliliters, for drinks | Consumed ml ÷ finished total volume |

Example: a recipe with four portions and a finished weight of 800 g gives the same contribution for **one portion**, **0.25 of the recipe**, or **200 g**.

The finished weight means the whole prepared dish after cooking. Friss does **not** automatically substitute the sum of ingredient weights. Without a finished weight, use portions or fractions; gram consumption requires that weight. Portion calculations do not need it. Changing portion count divides the existing ingredients differently; it does not multiply all ingredient quantities. Cooking losses are not automatically modeled.

### Water, caffeine and alcohol additions

Optional extra water (ml), caffeine (mg) and pure alcohol (g) apply to the **whole recipe** and are scaled with the consumed fraction. Add only quantities not already represented by ingredients. Adding water does not automatically adjust the finished weight.

A drink recipe can also have finished volume and the **final ABV of the complete drink**. This final ABV replaces alcohol calculated from ingredients and requires total volume; do not combine it with extra pure-alcohol grams. Other nutrients still come from the ingredients.

### Duplicating, moving and correcting recipes

- **Duplicate recipe** creates an independent editable copy, including ingredients and saved metadata. It does not book consumption.
- **Move to Drinks** changes a food recipe's category while keeping its identity and quick-add links. Existing diary entries retain their values. Moving back is possible; remove final ABV first if required.
- **Save for future entries only** uses the current definition for future recipe consumption. Existing logged portions retain their snapshot.
- **Save and amend existing entries** recalculates previously logged portions of that recipe after confirmation. Their consumed amounts and times are retained. This applies the current whole recipe, so check all ingredients first.

Ingredient edits are stored on the recipe as you make them; the final recipe save choice controls historical recalculation. An independent duplicated recipe is not amended when correcting its original.

### Importing from Chefkoch

Choose the Chefkoch recipe importer, paste a public recipe link and load the draft. Review title, portions, instructions and ingredients. Assign BLS foods and gram amounts where needed, then save as a new recipe. Spoonfuls, pieces, ranges and “to taste” remain original text unless you supply a usable quantity. Imported recipes do not automatically become diary meals. [Detailed importer guide](RECIPE_IMPORT.md) (German).

## 7. Favorites and recently used foods

**Recently used** offers foods used in diary entries or recipes. **Favorites** lets you create, edit and delete reusable favorites; use them from meal/ingredient capture. Check the suggested quantity rather than assuming it is today's amount. Shared search and direct manual/barcode capture can suggest the last-used amount.

A favorite is a reusable food entry, not a drink quick-add tile. Configure one-tap tiles separately in Settings. Removing a favorite does not delete its diary entries.

## 8. Manual foods, website import and label scanning

Open **Manual** to create your own food. Enter names, optional notes and known nutrient values. Select the reference basis **per 100 g** or **per 100 ml**. Consumption must use the matching unit. An empty English name falls back to the German name.

Leave unknown values empty; enter 0 only for a known zero. At least one known nutrient is required. Energy is kcal; other fields use their displayed g/mg/µg/ml units. Pure alcohol has its own field. The read-only **salt equivalent** under sodium uses **salt = sodium × 2.5**, with the appropriate mass conversion. It is not an additional nutrient to add again.

### Import from a website

Paste a supported **FDDB** product URL (`fddb.info` or `fddb.mobi`) or **FoodData Explorer** ingredient URL (`fooddata.the50.store`). Load the nutrient preview, check basis/values/names, then save. Loading alone creates no food.

- FDDB's explicitly stated 100-g/100-ml basis is respected. European carbohydrates are not reduced by fiber again.
- For supported USDA-style FoodData values, total carbohydrates are converted to European available carbohydrates by subtracting known fiber. If that conversion cannot be justified, the field remains unknown.
- Published units are converted where supported. Unsupported or missing values stay unknown. Source information is retained.
- Changing the reference basis manually does **not** convert the numbers. A density is needed to convert mass and volume.

Imports depend on the source site's availability and structure. [FDDB guide](FDDB_IMPORT.md) (German).

### Photograph or upload a nutrition label

Choose **Photograph nutrition label** or **Upload label image**. Use a sharp, straight image containing a clear **per-100-g** column. Friss runs German/English OCR on your server and fills suggestions; enter the name and check every value and unit before saving.

This OCR flow does not automatically interpret per-serving, US Nutrition Facts or per-100-ml tables. Those require manual entry/conversion. Recognized salt may be converted to sodium and kJ to kcal. The scan image itself is not archived by this flow; recognized text is retained in notes. This is label OCR, not AI recognition of a plated meal.

### Changing a saved manual food

Choose future-only saving or amendment of existing uses. Future-only changes do not alter old diary entries or existing recipe ingredients. Even a newly consumed portion of an old recipe still uses that recipe's stored ingredient snapshot until corrected.

Amending existing uses replaces this food in direct diary uses, recipe ingredients and historical recipe snapshots containing it. Other ingredients and the historical portion/weight/volume parameters are preserved. By contrast, amending a whole recipe applies its current whole definition. Unit conflicts or active Health exports can block a correction instead of partially applying it. [Correction details](CORRECTING_HISTORY.md) (German).

## 9. Understanding nutrients and missing data

- **Incomplete:** one or more contributions are unknown. A displayed numeric sum may be only a known part of the actual intake.
- **TR, <LOD, <LOQ:** source trace/detection-limit labels, not exact numeric zero.
- **Source unit unverified:** Friss cannot safely interpret a legacy/source unit. A displayed raw number must not be treated as a verified amount; affected Health export may be blocked.
- **Estimated:** external AI or supplied data is an estimate, not independently measured by Friss.
- **µg** means micrograms; JSON may use `mcg` internally. `1 mg = 1,000 µg`.

**Drinking water** is explicitly recorded water, including applicable recipe water additions. **Water in foods** is the remaining source-reported food water, kept separate so drinking water is not listed twice. BLS coffee/tea water does not automatically count as explicitly tracked drinking water. Neither a drink's entire volume nor a food's weight is assumed to be water. Food water may remain in grams.

In **Settings**, the missing-values option treats absent fields and trace/limit labels as assumed zero in calculations; it does not repair the source data. It is reversible and affects existing as well as new entries, recipe calculations, summaries and exports. Missing food identities/quantities or nonempty values with unverified units still need review. The daily audit deliberately continues to show the original gaps.

## 10. Statistics and daily audit

In **Statistics → Trends**, choose 7/30/90 days or a custom range up to 366 days, then select a tracked nutrient. The chart, sums, averages and day table follow that selection. Current daily targets for calories, protein, carbohydrates and fat appear as a dashed goal line when configured. They are today's settings, not historical goal records.

Days without usable entries remain gaps. Averages use days with calculated values, not automatically every calendar day. Incomplete days remain marked. Day boundaries follow the browser timezone and daylight saving changes.

**Statistics → Daily audit** is intended for a computer. Select a date or use previous/next/today. Each diary entry is a row and every tracked nutrient a column. Scroll horizontally/vertically; headers and entry names remain visible. Click a name to open details in a new tab.

- `0`: known zero. Hover to inspect small values beyond display rounding.
- Dash/orange: missing source value.
- Red: qualifier, unverified unit or incompatible unit; inspect the tooltip.
- `*`: a missing source value may be assumed zero elsewhere because of your setting.

The footer adds **known, verified compatible values** and counts gaps per column. Recipe ingredients are excluded; consumed portions are included. BAC is not an individual nutrient contribution and has no column. After editing a detail, reselect the day to refresh the audit. [Audit details](DAILY_AUDIT.md) (German).

## 11. Export to Apple Health

Friss's browser cannot write to Apple Health directly. The **Export** page prepares a daily file; a separately configured iPhone Shortcut must read it and log the samples in Health. No ready-to-install Health Shortcut is supplied.

1. Complete/review the diary day, then open Export.
2. Choose **Export day**. Friss reserves an immutable daily export.
3. Download/share the file to your Health-writing Shortcut.
4. The Shortcut reads `samples`, maps every `identifier` to its supported Health logging action, and uses each sample's **value, unit and timestamp**. Grant the required Health permissions on iPhone. Do not silently skip unsupported categories.
5. Only after all writes succeed choose **Confirm Health write** in Friss. Downloading a file alone is not success and Friss does not automatically verify Health.
6. After a failure or partial write choose **Export failed / uncertain** and inspect Health manually before any further export.

Export status distinguishes not exported, prepared, confirmed, uncertain/review, and changed since export. Unresolved entries, unverified BLS units and previous individual exports can block daily preparation. If missing-as-zero is enabled, export may contain explicitly flagged assumed zeros; otherwise missing values are not fabricated.

Daily samples use noon in the chosen day timezone. Alcohol grams and BAC are not exported as Health nutrition samples. Follow the units in the file rather than assuming they match the screen's display unit.

Editing, deleting, changing zero assumptions or restoring an old backup can make Friss and Health disagree. Friss never automatically deletes/rewrites old Health samples. Resolve those on iPhone before re-exporting; blindly repeating writes can double-count.

## 12. Settings

Use **Settings** for daily macro/calorie goals, missing-value assumptions, body/BAC parameters, drink quick-add definitions/images, search preferences, API-key access and backup/restore.

Quick-add presets can reference a food or recipe so all its nutrients are recorded. Upload an image to identify the tile; keep amounts and recipe links correct. Images fill small tiles, four across on Drinks. Updating an image does not change the food's nutrient content.

Under **Search terms and BLS synonyms**, create a phrase, choose its language, select the intended BLS food and save. A synonym can find a BLS food even without a matching name. Manage or forget learned selections there too. This changes suggestions, not BLS nutrient data or old meals. [Search preferences guide](SEARCH_PREFERENCES.md) (German).

Under **API for Shortcuts**, explicitly reveal/copy the existing API key. Use it in your Shortcut's Authorization header, not as your dashboard password or part of a shared URL. Hide it afterward; navigation/logout clears the displayed value. If no key is configured, it must be set on the server.

## 13. AI imports and iPhone Shortcuts

Friss does not run an external AI model or use a paid AI API on your behalf. Use your chosen AI app/Shortcut separately. There are three distinct formats:

| Workflow | Input and nutrient basis |
| --- | --- |
| Browser JSON import / `/json-import/preview` and `/commit` | `friss-meal-v1` items with database references or explicit nutrition basis (`100g`, `100ml`, or `total` as supported by the format). Review before saving. |
| One-step `POST /json-import` | `timestamp`, `original_message`, `ai`; model nutrients are **totals for the whole consumed meal**. |
| BLS `GET /bls/search`, `POST /bls/meals/preview`, `POST /bls/meals` | Search real BLS codes, then supply `items` with `bls_code` and `grams`. **Friss calculates nutrients.** |

Do not interchange these request formats or multiply meal-total nutrients by weight again. Requests use `Authorization: Bearer YOUR_API_KEY`; JSON POSTs use `Content-Type: application/json`. Timestamp needs a timezone, e.g. `2026-11-07T12:30:00+01:00`.

For one-step AI import, keep `ai` as the model's response text in the Shortcut; JSON serialization handles escaping. Server IDs are automatic. Retry the exact same request with the same timestamp/AI text to avoid duplicates. Changed data makes a new import rather than editing an existing one.

For BLS import, let the model identify foods, make HTTP searches in the Shortcut, give results back to the model, then submit only real codes and positive gram amounts. Preview first. The model does not automatically gain access to your private server merely because its URL is in a prompt. A batch creates one diary entry per food, not a saved recipe.

Optional original meal photos can be uploaded after a successful import to `PUT /entries/{id}/photos` as binary image files. A failed photo upload does not undo the meal. Keep the returned entry ID and retry the file upload. HEIC must first be converted to JPEG; static JPEG/PNG/WebP are supported, up to 15 MiB/40 megapixels each and 20 photos per entry. Identical bytes for the same entry are not duplicated.

Full examples: [AI Shortcut and photos](AI_SHORTCUT.md) · [BLS workflow and prompt](BLS_API.md) (German) · [Browser JSON format](JSON_IMPORT.md) (German) · [Example AI request](examples/ai-meal.json).

## 14. Backup and restore

In **Settings → Backup and restore**, choose **Download backup** and save the ZIP somewhere separate from your server. It contains data JSON, effective BLS foods, diary and recipe snapshots, manual foods, favorites, settings, search preferences, quick-add images, export status and archived original files/photos.

It does **not** contain passwords, API keys, `.env`, login sessions or application code. It is unencrypted personal data; keep it private. An Apple Health day export is not a backup.

To restore:

1. Select a compatible Friss ZIP and choose **Check backup**.
2. Review the preview; inspection changes nothing.
3. Choose **Restore data** and confirm replacement. Restore **replaces**, not merges, the current datasets and original/BLS files.
4. Friss keeps a pre-restore recovery ZIP under `data/recovery/`. After reload, check diary, recipes and settings before discarding your downloaded backup.

Server credentials remain as configured. Apple Health is not restored or modified; restored export flags describe the backup's time and may lag actual Health writes. Inspect Health before exporting again. Use the standard single-worker setup and avoid concurrent external database/file scripts during backup/restore. [Full backup guide and limits](BACKUPS.md).

## 15. Server setup and updates

For an existing installation, use the repository directory and run:

```bash
./update.sh
```

This updates the `server` branch, builds/restarts Docker and checks startup. If using a fork, synchronize its branch first. The updater's database/configuration backups are not a substitute for a complete downloadable ZIP or server backup.

For a new Debian/Docker installation, the basic administrator steps are:

```bash
git clone --branch server --single-branch https://github.com/philipptillmann/friss.git
cd friss
cp .env.example .env
mkdir -p data/bls data/originals
```

Edit `.env`: set a random API key of at least 32 characters, a server LAN/VPN bind IP and an unused port (default 8001). Configure a password with `python3 scripts/set-password.py`. Copy your compatible BLS JSON to `data/bls/`, then:

```bash
sudo chown -R 10001:10001 data
docker compose up -d --build
```

BLS source data is not bundled in Git; a compatible Friss backup can also restore the effective foods. Use the lowercase repository URL. The directory name of an existing installation may still be `Friss`.

Keep the service on your trusted LAN/VPN. Use HTTPS for access outside a trusted encrypted connection; do not simply forward the port to the public internet. For HTTPS set `FRISS_COOKIE_SECURE=true` as appropriate. Camera/file choices depend on browser; full PWA features require a secure context.

Changing password: run the password script and recreate the container; old sessions are invalidated. The password script does not rotate the API key. Keep `.env` and infrastructure backups separately.

## 16. Troubleshooting

| Symptom | Check/action |
| --- | --- |
| Site unreachable | Server/Docker running, correct port/IP/hostname, VPN connected. Try the IP if local hostname resolution fails. |
| Container fails to start | Run `docker compose logs --tail=100`. A busy port requires a free `FRISS_PORT`; data permissions must allow UID 10001. Do not reset/delete data to fix startup. |
| API says login required | Set the Authorization header to `Bearer ` plus the API key. A browser session does not authenticate a separate Shortcut request. |
| Invalid JSON | Use the endpoint's correct format and let Shortcuts serialize dictionaries/text. Check reported line/column; do not add/remove brackets blindly. |
| No BLS results | Check that compatible BLS data was loaded. Try a shorter term or an explicit synonym; `/bls/search` reports total database count. |
| Product not found / online importer fails | Barcode may be absent from Open Food Facts, or source site unavailable/changed. Create a manual food or use another supported source. |
| Entry remains unresolved | Reopen it; check selected food, amount, g/ml basis and source units. Zero assumptions do not fix an unknown food or quantity. |
| Goals not visible | Save Settings, return to Home and reload if needed; verify you are on the same server URL/session. |
| Health export blocked or uncertain | Read its reason, complete entries/check units, and inspect existing Health samples before retrying. |
| Interface looks stale after an update | Reload/reopen the site. Home Screen icon changes may require removing/re-adding the web app; this does not delete server data. |

When reporting a problem, include app version, page, exact steps and the error text. Redact API keys/passwords and personal information from logs or screenshots.

## 17. Meal planning, fridge inventory and shopping

Use **Meal planner** to schedule saved food/drink recipes, portions and preparation notes. Mark **Prepared** to track meal prep; **Mark eaten** with the actual time creates the diary entry. Plans retain their saved recipe version. **Fridge** stores source-linked quantities and expiry reminders. **Shopping list** combines ingredients for your range and subtracts matching stock, with purchased checkboxes and manual items.

Under Settings, planning and inventory can be switched off independently without deleting their data. Shopping stays available. Stock quantities are maintained manually: eating and checking purchases do not change them. Backups include all new records. [Complete English/German workflow, boundaries and API](PLANNING.md).

## 18. Unfinished-entry inbox

Use **Inbox** to capture text, pictures or both with their original date/time. Unfinished items do not affect nutrition, statistics, BAC or Health. Open a draft, review originals and select a food or recipe with its amount/time to complete exactly one diary entry. Text and photos remain attached. Keep unknown amounts pending until you can complete them.

A Shortcut can POST timestamp/text/title to `/inbox`, then PUT picture files to its returned `photo_upload_url`. No nutrients, AI output or client UUID is needed. Identical retries avoid duplicates. Inbox data is included in backups. [Complete English/German instructions and API](INBOX.md).
