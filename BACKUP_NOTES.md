# Backup notes - house-price-emailer

Made because GitHub access was unavailable at the time (both the repo's
codeload download and its GitHub Pages site returned 404 when checked).
This is everything needed to redeploy the project from scratch, whether
that's back to the same repo once access is restored, or a brand new one.

## What's in this backup

- `hanoi_house_price_emailer.py` - the main script. **Note:** this
  includes one feature (price-drop tracking, see below) that was
  mid-implementation when this backup was made - it's syntactically
  valid and imports cleanly, but hasn't been tested as thoroughly as the
  rest of the file. Everything else has been tested.
- `.github/workflows/send-house-price.yml` - the GitHub Actions workflow
  that runs the script on a schedule.
- `requirements.txt` - Python dependencies (requests, beautifulsoup4,
  certifi, Pillow).
- `README.md` - fuller description of what the project does.
- `reference/` - not needed to redeploy, kept for context:
  - the two most recent demo HTML files (what a sample email/page look
    like)
  - `old-debug-tools/` - one-off diagnostic scripts used earlier in
    development, safe to ignore or delete.

## What this does NOT include

- **`state/` contents** - the dedup state (which listings were already
  sent today, price history for drop detection) lives on a separate
  orphan git branch (`house-price-state`) in the repo, persisted by the
  workflow itself. That's runtime state, not something this conversation
  ever had a copy of - it'll just start fresh (empty) on first run after
  redeploying, which is harmless (worst case: a few listings repeat once
  that wouldn't have otherwise).
- **Repo secrets** - `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`,
  `HOUSE_RECIPIENT`, `COPILOT_PAT`. These were never visible to this
  conversation and need to be re-added in the new repo's Settings →
  Secrets.
- **GitHub Pages setting** - Settings → Pages → Deploy from branch →
  `main` / `/docs`. Needs to be re-enabled on whichever repo this ends
  up in.

## Redeploying

1. Create/open the repo, add the files above at the repo root (workflow
   file goes in `.github/workflows/`).
2. Add the four secrets listed above.
3. Enable GitHub Pages (branch `main`, folder `/docs`).
4. Run the workflow once manually (Actions tab → the workflow →
   "Run workflow") to confirm it works before waiting for the schedule.

## Project summary, for context

Scrapes real individual house/apartment listings (not price averages) for
Hanoi from Mogi.vn, filters them (price ceiling, plausibility, age,
distance from center, spam/mini-apartment detection), runs them through
an AI review pass, fetches photos and generates a location map image for
each, and sends the result as both an email and a companion GitHub Pages
website with an interactive map. Full history of every design decision
and bug fix is preserved in the Claude conversation this was built in -
worth referring back to that if picking this up in a new session, since
many non-obvious fixes (Unicode normalization, chunk-boundary parsing,
clickbait price handling, font rendering) aren't otherwise documented
anywhere except in code comments.
