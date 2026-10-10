# Hanoi House/Apartment Listing Emailer (runs on GitHub Actions, no local computer needed)

Emails you real, individual house and apartment listings for sale in
Hanoi — exact asking prices, not district averages — with photos, an AI
sanity-review pass, and a linked live webpage with an interactive map.
Runs automatically on a schedule via GitHub Actions.

## What it actually does

1. **Fetches real listings** from Mogi.vn, per Hanoi district
   (`mogi.vn/ha-noi/<district>/mua-can-ho-chung-cu` and `.../mua-nha`),
   for two categories: **Căn hộ / Chung cư** (apartments) and **Nhà**
   (houses). Pages through each district until at least
   `MIN_LISTINGS_PER_CATEGORY` (default 50) listings pass every filter
   below, or the district list is exhausted.

2. **Filters out**:
   - Implausibly low prices (`< MIN_PLAUSIBLE_PRICE_TRIEU`, default 300
     triệu) — almost always a seller data-entry error, not a real price.
   - Listings posted more than `MAX_LISTING_AGE_DAYS` (default 365) days
     ago — an old price may no longer be current.
   - Listings over `MAX_PRICE_TRIEU` (hardcoded to 5 tỷ / 5000 triệu).
   - Listings outside Hanoi, or mentioning another major Vietnamese city
     — some district-scoped URLs occasionally surface cross-city content.
   - "Chung cư mini" (mini-apartment) listings — both by keyword
     (`chung cư mini`, `CCMN`, `CC Mini`, etc.) and by a softer heuristic
     (wording like "sổ hồng riêng từng phòng" + very small area).

3. **AI review pass**: the remaining listings are sent to an AI model
   (via Copilot CLI, called directly from the workflow — see
   `.github/workflows/send-house-price.yml`) with each listing's title,
   district, area, price, and scraped description text. The AI can
   `reject` a listing it judges to be a mini-apartment by wording alone,
   outside Hanoi, not real estate, or priced in a way that's inconsistent
   with its own description (e.g. a multi-story house with an elevator
   priced far below what that implies — usually a scraping/data error,
   not a real bargain). This step needs the `COPILOT_PAT` secret (a
   Personal Access Token with Copilot Requests permission, free tier is
   enough) — if it's missing or the step fails, the build falls back to
   the rule-based filters above rather than blocking the email.
   Because the prompt includes text written by sellers, the AI runs in
   its own workflow job with no repository permissions, no checkout and
   its shell, file-write and web tools denied, and the build only
   accepts `ok`/`reject` verdicts for listing ids it already has.

4. **Self-check pass** (`flag_suspicious`): independent of the AI step,
   flags (doesn't remove) any listing with an implausible price-per-m²,
   or where a price mentioned in the title disagrees with the price
   actually used — shown inline with a ⚠️ marker so you can eyeball it.

5. **Photos**: fetches each surviving listing's own detail page and
   pulls its photo gallery (its `og:image` plus other photos found on the
   page, up to `MAX_IMAGES_PER_LISTING`).

6. **Location**: geocodes each listing's full address via OpenStreetMap's
   free Nominatim API (no key needed), then generates a small map image
   (a real OSM tile with a marker drawn on it) appended to that listing's
   photo gallery. `docs/maps/` is cleaned up each run so it doesn't grow
   forever.

7. **Sends two things**:
   - An **email** (Gmail SMTP) with card-style listings, sorted
     cheapest-first per category, each with its photos.
   - A **GitHub Page** (`docs/index.html`, published to `main`) with the
     same listings in a nicer webpage layout, plus an interactive Leaflet
     map showing every geocoded listing's pin together — this is where
     you can actually see listings' locations relative to each other.
     **Requires GitHub Pages to be enabled**: Settings → Pages → Source:
     "Deploy from a branch" → Branch: `main`, Folder: `/docs`.

## Known limitations / things worth knowing

- Pagination on Mogi's citywide listing pages didn't reliably return new
  results when tested, so this fetches per-district pages instead
  (confirmed working URLs) rather than paginating one page.
- The photo-gallery and map-fetching steps each add one extra HTTP
  request per listing, so a full run can take a while - this is
  intentional (politeness delays are hardcoded) rather than a bug.
- Geocoding accuracy depends on Mogi's own address text being well
  formed; not every listing address matches the expected format, so not
  every listing gets a map pin.
- The AI review step's actual real-world reliability hasn't been
  extensively verified - watch the "AI review rejected N listing(s)"
  log line and the email's ⚠️ flags together to sanity-check it over
  time.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create a Gmail App Password (needs 2-Step Verification on):
   <https://myaccount.google.com/apppasswords>
3. Create a GitHub Personal Access Token with "Copilot Requests"
   permission (free Copilot tier is enough) for the AI review step.
4. Add repo secrets: `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`,
   `HOUSE_RECIPIENT`, `COPILOT_PAT`.
5. Enable GitHub Pages: Settings → Pages → Deploy from branch → `main` /
   `/docs`.
6. The workflow (`.github/workflows/send-house-price.yml`) runs
   `prepare` → AI review → `build` → publish page → `send` on its
   schedule, or trigger it manually via `workflow_dispatch`. Those run as
   three jobs (`prepare`, `ai-review`, `send`) that hand files to each
   other as run artifacts; only `send` can push to the repo.

Script commands, if running any phase manually:

```
python hanoi_house_price_emailer.py prepare   # fetch + rule-filter, writes listings.json + AI prompt
python hanoi_house_price_emailer.py build     # apply AI verdict, fetch photos/maps, build email + page
python hanoi_house_price_emailer.py send      # send the built email via Gmail SMTP
```
