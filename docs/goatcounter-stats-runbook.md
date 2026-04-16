# GoatCounter Visitor Stats Runbook

This document records the root cause, the effective fix, and the operating checklist for the homepage visitor stats widget.

## Context

The homepage shows a country-level pageview widget backed by GoatCounter. The data flow is:

1. Browser pageviews are sent to GoatCounter from `_includes/analytics.html`.
2. `.github/workflows/goatcounter_stats.yaml` runs daily and on page builds.
3. `goatcounter_stats/update_goatcounter_stats.py` reads GoatCounter stats and publishes `country-stats.json` to the `goatcounter-stats` branch.
4. `_includes/fetch_goatcounter_stats.html` loads that JSON and renders the homepage widget.

The recurring failure was not a single display bug. Several different failure modes produced the same visible symptom: the homepage either showed zero data or kept showing stale data.

## What Finally Fixed It

The stable fix was commit `1e7f1b6` (`Harden GoatCounter stats diagnostics`), built on top of commit `ad8b79f` (`Bypass broken GoatCounter script and preserve stats`).

The important parts are:

1. The browser no longer depends on `https://gc.zgo.at/count.js`.

   `_includes/analytics.html` sends a direct GoatCounter `/count` image request to `https://bazinga699.goatcounter.com/count`. This avoids losing tracking when the external script host or TLS chain is unavailable.

2. The stats job no longer publishes empty data over valid data.

   `goatcounter_stats/update_goatcounter_stats.py` fetches the previous published JSON first. If the fresh GoatCounter result is empty, but the previous JSON has useful counts, it keeps the previous stats instead of overwriting the branch with zeros.

3. The stats job now distinguishes "checked" from "fresh".

   The generated JSON can include:

   ```json
   {
     "source_status": "fresh",
     "updated_at": "...",
     "checked_at": "..."
   }
   ```

   If GoatCounter is empty or temporarily unavailable and previous stats are reused, `source_status` becomes `using_previous_stats`, `checked_at` advances, and `updated_at` remains the last known good data timestamp.

4. The GoatCounter API base is validated.

   The script normalizes `GOATCOUNTER_SITE_API` to `/api/v0` and validates that the host matches `_config.yml`'s `goatcounter_code`. This catches cases where the secret points to the wrong GoatCounter host or to the wrong URL shape.

5. API failures are diagnosable.

   Retryable API failures (`404`, `429`, `5xx`) are retried. If they still fail, the workflow log includes the endpoint path and a short response body, while still avoiding printing the API token.

## Why Earlier Fixes Did Not Fully Work

Earlier fixes mostly added fallback paths after the stats API returned empty or failed. Those were useful, but they did not fully separate these cases:

1. Tracking was not recording new visits.
2. GoatCounter had data, but the API/export path returned empty.
3. GitHub Actions published a zero-result JSON over the last valid JSON.
4. The homepage displayed stale data without saying whether the job had run.

Because all four looked similar on the homepage, each fix appeared to work after a manual push or rerun, then failed again during later scheduled runs.

The correct approach was to make each layer explicit:

1. Tracking layer: direct `/count` pixel.
2. Fetch layer: validated GoatCounter API base, retry, and export fallback.
3. Publish layer: preserve last valid data when fresh data is empty.
4. Display layer: show whether the data is fresh or reused from the last successful run.

## Expected Healthy State

A healthy `country-stats.json` should look like:

```json
{
  "title": "Pageviews Around the World",
  "updated_at": "2026-04-13T12:17:01.951419+00:00",
  "checked_at": "2026-04-13T12:17:01.951419+00:00",
  "source_status": "fresh",
  "total_pageviews": 48,
  "total_countries": 5,
  "countries": [
    { "code": "CN", "pageviews": 31 }
  ]
}
```

`source_status: fresh` means the job read useful data from GoatCounter in that run.

`source_status: using_previous_stats` means the job ran, but GoatCounter returned empty or unusable data, so the site intentionally kept the last valid counts.

## GitHub Secrets

Required repository secrets:

```text
GOATCOUNTER_SITE_API=https://bazinga699.goatcounter.com/api/v0
GOATCOUNTER_API_KEY=<GoatCounter API token>
```

`GOATCOUNTER_SITE_API` may also be set to `https://bazinga699.goatcounter.com`; the script normalizes it to `/api/v0`. It must not point to `goatcounter.com`, another GoatCounter site, or a specific stats endpoint.

## Daily Check

Use these checks when the homepage looks stale:

1. Check the latest workflow run.

   Open GitHub Actions and inspect `Update GoatCounter Visitor Map`.

2. Check the generated JSON.

   ```sh
   curl -L https://raw.githubusercontent.com/Bazinga699/Bazinga699.github.io/goatcounter-stats/country-stats.json
   ```

3. Interpret `source_status`.

   `fresh`: GoatCounter returned usable data. If the homepage still looks stale, suspect browser/CDN cache.

   `using_previous_stats`: the workflow ran but GoatCounter returned empty or failed. Inspect the `Generate visitor stats` log.

4. Read the workflow log lines.

   Healthy log:

   ```text
   Using GoatCounter API base: bazinga699.goatcounter.com/api/v0
   GoatCounter stats API result: total_pageviews=..., total_countries=...
   ```

   Empty-data fallback:

   ```text
   Stats API returned incomplete data; falling back to GoatCounter export.
   Fresh GoatCounter stats were empty; keeping the previous published stats.
   ```

   API path/secret issue:

   ```text
   GOATCOUNTER_SITE_API does not match _config.yml goatcounter_code
   ```

## Do Not Repeat These Mistakes

Do not treat a successful GitHub Actions run as proof that the visitor data is fresh. The job can succeed while intentionally preserving previous stats.

Do not overwrite `goatcounter-stats/country-stats.json` with zeros when GoatCounter returns empty data. Empty fresh data is less trustworthy than the last valid published data.

Do not debug only the homepage UI. The UI is downstream; always inspect the JSON and the `Generate visitor stats` log first.

Do not rely on manual reruns as evidence. A manual run can coincide with fresh page visits or transient GoatCounter availability. The daily scheduled run is the real test.

## Relevant Files

```text
_includes/analytics.html
_includes/fetch_goatcounter_stats.html
.github/workflows/goatcounter_stats.yaml
goatcounter_stats/update_goatcounter_stats.py
_config.yml
```

