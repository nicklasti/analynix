# Analynix

A Django site that grades US stocks against their industry peers, with price
charts, headlines and an optional AI analyst write-up.

This is the 2026 rebuild of the original `Analynix` folder: same site and
templates, with the grading scheme fixed, the data pipeline rewritten for current
libraries, and the old bugs removed (see "What changed" below).

## Run it locally

```bash
python3.14 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # then set DJANGO_SECRET_KEY and DJANGO_DEBUG=1
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Run the tests with `.venv/bin/python manage.py test myapp`.

**On a Mac with iCloud Drive syncing the Desktop:** iCloud offloads files it thinks you
don't need, which makes Python hang. Anything named `*.nosync` is left alone, so on this
Mac `.venv` is a link to `.venv.nosync` and the database lives in `data.nosync/`
(`DATABASE_PATH=data.nosync/db.sqlite3` in `.env`).

## Updating the data

| Command | What it does | Time (all stocks) |
| --- | --- | --- |
| `manage.py update_fundamentals` | finviz screener: fundamentals for every stock | ~20 min |
| `manage.py update_prices` | Yahoo Finance: full daily price history | ~20-40 min |
| `manage.py grade_stocks` | recompute every grade (see below) | seconds |
| `manage.py update_ebitda` | finviz income statements: TTM EBITDA growth | ~3.5 hours |
| `manage.py update_news` | finviz: latest 6 headlines per stock | ~4-5 hours |
| `manage.py ai_analysis` | OpenAI write-up and grade, then regrade (needs `OPENAI_API_KEY`) | ~4 hours, ~$10 |
| `manage.py update_all` | all of the above, in order | |
| `manage.py run_scheduler` | prices + headlines on weeknights, `update_all` on Saturdays | runs forever |

`update_prices`, `update_news` and `ai_analysis` accept tickers, e.g.
`manage.py update_prices AAPL MSFT`. `update_fundamentals --min-market-cap "+Small (over $300mln)"`
limits the universe to larger companies.

## When things update (on the server)

| What | When |
| --- | --- |
| Stock price on a stock page | live: refreshed from Yahoo when someone opens the page, at most once a minute, and shared with everyone (`/api/quote`) |
| Price history (charts) | weeknights 22:30 UTC, after the US market closes |
| Headlines | weeknights, right after the prices |
| Fundamentals, ratios, EBITDA growth, grades, AI write-ups | Saturdays from 06:00 UTC (`update_all`, about 12 hours) |

When the server starts it also runs `update_all` if none has finished in the last six
days, so a restart or deploy in the middle of an update picks it up again.

## How grading works

The rules live in [`myapp/grading.py`](myapp/grading.py), which is plain Python with tests in
[`myapp/tests/test_grading.py`](myapp/tests/test_grading.py).

1. Each stock is compared with its industry on eleven metrics: revenue (TTM), revenue
   growth (TTM), EBITDA growth (TTM), EPS growth (Fwd), earnings (TTM), profit margin
   (TTM), P/E (TTM), P/E (Fwd), EPS (TTM), P/S (TTM) and P/B (MRQ). TTM = last 12 months,
   Fwd = analysts' estimate for next year, MRQ = most recent quarter. If fewer than 10
   stocks in the industry report a metric, it is compared with its sector instead (the
   site marks those medians "(sector)"). There is no forward EBITDA growth or forward
   P/B: no free source publishes those forecasts.
2. Its percentile for each metric is the share of peers it beats (lower is better for
   the four valuation ratios). Ratios are only graded when positive, so a loss-making
   company gets N/A for P/E; its losses already count through earnings, margin and EPS.
   Missing numbers are skipped, not counted as zero or as an F-.
3. Percentiles become letters on a symmetric bell curve: top 3% A+, middle 14% C,
   bottom 3% F-.
4. The overall score is the average of the percentiles (plus the AI grade, weighted like
   one metric, when there is a current one), ranked against every other stock. The same
   curve turns it into the overall grade. Top Rated = B or better; Low Rated = D or worse.

To change the weights, the curve or the peer-group size, edit the constants at the top
of `grading.py` and run `manage.py grade_stocks`.

## Google Ads

The AdSense code is on every page, `/ads.txt` is served, and the privacy policy AdSense
requires is at `/privacy`. Ads only show once the site runs on your own domain
(nixreenr.com; AdSense won't serve on `*.fly.dev`), that domain is approved under
**Sites** in AdSense, and AdSense's **Privacy & messaging** consent message is turned on
for visitors in the EU and UK.

## Home screen app

The site is a progressive web app: `templates/pwa/` has the manifest, the service
worker (it only shows an offline message; pages always load fresh) and the popup that
offers "Add to Home Screen" on a visitor's first visit. Chrome, Edge and Samsung
Internet get a one-tap install button; iPhones and iPads get the two taps (Share, then
Add to Home Screen), since Safari has no install button for websites. "Not now" hides
the popup for two weeks. Icons are in `static/icons/`.

## Deploying to fly.io

The Dockerfile runs the site with gunicorn and the scheduler in the same machine, so
both use the SQLite database on the volume mounted at `/data`. You don't need Docker
installed: `fly deploy` builds the image on fly's servers. (Docker Desktop is only
needed to run the container on your own machine.)

```bash
brew upgrade flyctl                      # the installed flyctl is from 2024
fly volumes create analynix_data --size 3 --region ewr
fly secrets set DJANGO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
fly secrets set OPENAI_API_KEY=...       # optional; the account needs API credits
fly deploy
```

On first boot with an empty database the container runs `update_all` once in the
background, so the site fills itself (about 25 minutes for fundamentals and prices,
then several hours of headlines). The old `nixreenz` app still has a stopped `cron`
machine from the previous setup; remove it with `fly machine destroy <id>`.

**Custom domain through Cloudflare:** add the domain to `DJANGO_ALLOWED_HOSTS` and
`DJANGO_CSRF_TRUSTED_ORIGINS` in `fly.toml`, run `fly certs add <domain>`, and create
the DNS records it prints in Cloudflare (a CNAME to `nixreenz.fly.dev`). With
Cloudflare's proxy on, set SSL/TLS to "Full (strict)".

## What changed from the original

**Grading**
- The variance was divided by the number of stocks one extra time, so every "standard
  deviations from the mean" score was inflated 1.4x to 13x depending on industry size;
  27% of stocks ended up F- and 15% A+. Grades are now percentile-based and follow the
  bell curve above.
- Missing values were stored as 0 and averaged in; "N/A" counted as F- (and a missing
  AI grade as -35 points). Missing values are now skipped.
- P/S "N/A" set the P/B grade by mistake, so 94 stocks showed the previous stock's P/S grade.
- The cutoffs were lopsided (e.g. A- spanned 0.2 standard deviations, B spanned 2) and
  EPS used a mirrored table, so an average stock got B- on most metrics but C- on EPS.
- The Top and Low Rated lists each held 1,000 of 1,875 stocks, so 124 stocks were on
  both. The lists are now B-or-better and D-or-worse, sorted by score.
- The AI grade counted 5x; it now counts like one metric, and grades from the old
  pipeline (which were based on the old miscalculated grades) don't count.

**Code and data**
- Django 4.0 / Python 3.9 -> Django 6.1 / Python 3.14, current pandas, yfinance,
  finvizfinance, plotly and openai; `pandas_datareader` and `django-crontab` removed.
- The 4,300-line `scripts/secondscript.py` is now `myapp/pipeline/` plus management commands.
- New stocks were never added (`update()` doesn't raise when a row is missing, so the
  `create()` fallback never ran), and stocks whose price download failed were deleted.
- News "summaries" were generated from the article URL alone (the model couldn't open
  it); they're gone. The AI analysis is now one JSON request per stock.
- The secret key and OpenAI key are read from the environment instead of the code.
- On fly.io the database lived inside the Docker image (no volume), so every deploy
  reset the data. It now lives on a volume, and the scheduler runs next to the site.
- Smaller fixes: the stock page crashed for stocks without an AI analysis, P/B and P/S
  columns were swapped on the list pages, the 404 page returned status 200, `/copyright`
  pointed at a deleted template, plotly.js was inlined into every stock page (several MB),
  and a script error fired on every page.
