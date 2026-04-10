#!/usr/bin/env python3

import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


RAW_API_BASE = os.environ.get("GOATCOUNTER_SITE_API", "")
API_TOKEN = os.environ.get("GOATCOUNTER_API_KEY", "")
ROOT_PATHS = [
    path.strip()
    for path in os.environ.get("GOATCOUNTER_ROOT_PATHS", "").split(",")
    if path.strip()
]
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(REPO_ROOT, "_config.yml")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "country-stats.json")
PREVIOUS_STATS_PATH = os.environ.get(
    "GOATCOUNTER_PREVIOUS_STATS_PATH",
    os.path.join(OUTPUT_DIR, "previous-country-stats.json"),
)
ALL_TIME_START = "2000-01-01T00:00:00Z"
COUNTRY_CODE_ALIASES = {
    "HK": "CN",
    "MO": "CN",
    "TW": "CN",
}
SUPPORTED_EXPORT_VERSIONS = {1}


class GoatCounterAPIError(RuntimeError):
    def __init__(self, status_code, url, message):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


def normalize_api_base(base):
    base = base.strip().rstrip("/")
    if not base:
        return ""
    if base.endswith("/api/v0"):
        return base
    # Accept either the site root or the explicit API base in the secret.
    return f"{base}/api/v0"


API_BASE = normalize_api_base(RAW_API_BASE)


def load_expected_site_code():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as config_file:
            for raw_line in config_file:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if not line.startswith("goatcounter_code"):
                    continue
                _, _, value = line.partition(":")
                return value.strip().strip('"').strip("'")
    except OSError:
        return ""

    return ""


def validate_api_base():
    expected_code = load_expected_site_code()
    if not expected_code:
        return

    hostname = (urllib.parse.urlparse(API_BASE).hostname or "").lower()
    expected_hostname = f"{expected_code}.goatcounter.com"

    if hostname.endswith(".goatcounter.com") and hostname != expected_hostname:
        raise RuntimeError(
            "GOATCOUNTER_SITE_API does not match _config.yml goatcounter_code: "
            f"expected {expected_hostname}, got {hostname or '<empty>'}."
        )


def api_request(path, query=None, method="GET", data=None, accept="application/json"):
    url = f"{API_BASE}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"

    payload = None if data is None else json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": accept,
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise GoatCounterAPIError(
                error.code,
                url,
                f"GoatCounter API endpoint was not found: {url}. "
                "Check GOATCOUNTER_SITE_API; it should usually look like "
                "https://<your-site>.goatcounter.com/api/v0"
            ) from error
        raise GoatCounterAPIError(
            error.code,
            url,
            f"GoatCounter API request failed ({error.code}): {url}",
        ) from error


def api_json_request(path, query=None, method="GET", data=None):
    return json.loads(api_request(path, query=query, method=method, data=data).decode("utf-8"))


def code_from_location(stat):
    value = (stat.get("id") or "").strip().upper()
    if not value:
        name = (stat.get("name") or "").strip().upper()
        if len(name) in (2, 5) and name[:2].isalpha():
            value = name

    if not value:
        return ""

    if "-" in value:
        value = value.split("-", 1)[0]

    return COUNTRY_CODE_ALIASES.get(value[:2], value[:2])


def stats_query(base_query):
    query = dict(base_query)
    if ROOT_PATHS:
        query["path_by_name"] = "true"
        query["include_paths"] = ROOT_PATHS
    return query


def get_locations():
    stats = []
    offset = 0

    while True:
        payload = api_json_request(
            "/stats/locations",
            query=stats_query({
                "start": ALL_TIME_START,
                "limit": 100,
                "offset": offset,
            }),
        )

        stats.extend(payload.get("stats", []))
        if not payload.get("more"):
            break
        offset += 100

    merged = {}
    for stat in stats:
        code = code_from_location(stat)
        count = int(stat.get("count", 0) or 0)
        if code and count > 0:
            merged[code] = merged.get(code, 0) + count

    countries = [{"code": code, "pageviews": count} for code, count in merged.items()]
    countries.sort(key=lambda item: (-item["pageviews"], item["code"]))
    return countries


def get_total_pageviews():
    payload = api_json_request(
        "/stats/total",
        query=stats_query({
            "start": ALL_TIME_START,
        }),
    )
    return int(payload.get("total", 0) or 0)


def summarize_counts(total_pageviews, countries):
    return (
        f"total_pageviews={total_pageviews}, "
        f"total_countries={len(countries)}"
    )


def export_has_useful_data(total_pageviews, countries):
    return total_pageviews > 0 or bool(countries)


def fallback_to_export(api_total_pageviews, api_countries, reason):
    print(reason, file=sys.stderr)
    export_total_pageviews, export_countries = get_pageviews_from_export()
    print(
        "GoatCounter export result:",
        summarize_counts(export_total_pageviews, export_countries),
        file=sys.stderr,
    )

    if export_has_useful_data(export_total_pageviews, export_countries):
        return export_total_pageviews, export_countries

    print(
        "GoatCounter export was also empty; keeping stats API result.",
        file=sys.stderr,
    )
    return api_total_pageviews, api_countries


def wait_for_export(export_id):
    for _ in range(60):
        payload = api_json_request(f"/export/{export_id}")
        if payload.get("finished_at"):
            return
        time.sleep(2)
    raise RuntimeError("Timed out waiting for GoatCounter export.")


def normalize_path(path_value):
    if not path_value:
        return "/"
    cleaned = path_value.split("?", 1)[0]
    if not cleaned:
        return "/"
    return cleaned


def parse_bool(value):
    return str(value).strip().lower() == "true"


def load_rows(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    return [row for row in reader if row]


def decode_csv_bytes(raw_bytes):
    if raw_bytes[:2] == b"\x1f\x8b":
        raw_bytes = gzip.decompress(raw_bytes)
    return raw_bytes.decode("utf-8")


def export_format_version(path_field):
    prefix, separator, _ = path_field.partition(",")
    if separator and prefix.isdigit():
        return int(prefix)
    return 1


def detect_field(row, suffix):
    for key in row.keys():
        if key.endswith(suffix):
            return key
    raise KeyError(f"Could not find field ending with {suffix}")


def is_root_path(path_value):
    if not ROOT_PATHS:
        return True

    normalized = normalize_path(path_value)
    candidates = {normalized, normalized.rstrip("/")}

    for root_path in ROOT_PATHS:
        root_normalized = normalize_path(root_path)
        if normalized == root_normalized:
            return True
        if normalized.rstrip("/") == root_normalized.rstrip("/"):
            return True
        if root_normalized in candidates or root_normalized.rstrip("/") in candidates:
            return True

    return False


def country_code_from_export_row(location_value):
    value = (location_value or "").strip().upper()
    if not value:
        return ""
    if "-" in value:
        value = value.split("-", 1)[0]
    return COUNTRY_CODE_ALIASES.get(value[:2], value[:2])


def get_pageviews_from_export():
    export = api_json_request("/export", method="POST")
    export_id = export.get("id")
    if not export_id:
        raise RuntimeError("Failed to create GoatCounter export.")

    wait_for_export(export_id)
    csv_bytes = api_request(f"/export/{export_id}/download", accept="text/csv")
    rows = load_rows(decode_csv_bytes(csv_bytes))
    if not rows:
        return 0, []

    sample = rows[0]
    path_field = detect_field(sample, "Path")
    export_version = export_format_version(path_field)
    if export_version not in SUPPORTED_EXPORT_VERSIONS:
        raise RuntimeError(
            f"Unsupported GoatCounter export CSV version {export_version}."
        )
    event_field = detect_field(sample, "Event")
    location_field = detect_field(sample, "Location")
    bot_field = detect_field(sample, "Bot")

    total_pageviews = 0
    country_totals = {}

    for row in rows:
        if parse_bool(row.get(event_field, "")):
            continue
        if row.get(bot_field, "").strip() not in ("", "0"):
            continue
        if not is_root_path(row.get(path_field, "")):
            continue

        total_pageviews += 1
        code = country_code_from_export_row(row.get(location_field, ""))
        if code:
            country_totals[code] = country_totals.get(code, 0) + 1

    countries = [{"code": code, "pageviews": count} for code, count in country_totals.items()]
    countries.sort(key=lambda item: (-item["pageviews"], item["code"]))
    return total_pageviews, countries


def collect_pageview_stats():
    try:
        total_pageviews = get_total_pageviews()
        countries = get_locations()
        print(
            "GoatCounter stats API result:",
            summarize_counts(total_pageviews, countries),
            file=sys.stderr,
        )

        # Some GoatCounter setups return partial stats payloads, such as a
        # non-zero total with no country breakdown. The export endpoint is more
        # reliable for publishing the map data, so prefer it when the stats API
        # result is empty or incomplete.
        if total_pageviews == 0 or not countries:
            return fallback_to_export(
                total_pageviews,
                countries,
                "Stats API returned incomplete data; falling back to GoatCounter export.",
            )

        return total_pageviews, countries
    except GoatCounterAPIError as error:
        if error.status_code != 404:
            raise
        return fallback_to_export(
            0,
            [],
            "Stats API returned 404; falling back to GoatCounter export.",
        )


def normalize_country_entries(countries):
    normalized = []
    for item in countries or []:
        code = (item.get("code") or "").strip().upper()
        count = int(item.get("pageviews") or item.get("visitors") or 0)
        if code and count > 0:
            normalized.append({"code": code, "pageviews": count})

    normalized.sort(key=lambda item: (-item["pageviews"], item["code"]))
    return normalized


def normalize_stats_payload(payload):
    countries = normalize_country_entries(payload.get("countries"))
    total_pageviews = int(
        payload.get("total_pageviews")
        or payload.get("total_unique_visitors")
        or 0
    )

    return {
        "title": payload.get("title") or "Pageviews Around the World",
        "updated_at": payload.get("updated_at") or "",
        "total_pageviews": total_pageviews,
        "total_countries": len(countries),
        "countries": countries,
    }


def build_stats_payload(total_pageviews, countries):
    return {
        "title": "Pageviews Around the World",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_pageviews": total_pageviews,
        "total_countries": len(countries),
        "countries": countries,
    }


def load_previous_stats():
    if not PREVIOUS_STATS_PATH or not os.path.exists(PREVIOUS_STATS_PATH):
        return "", None

    try:
        with open(PREVIOUS_STATS_PATH, encoding="utf-8") as previous_file:
            raw = previous_file.read()
        return raw, normalize_stats_payload(json.loads(raw))
    except (OSError, json.JSONDecodeError, ValueError):
        return "", None


def main():
    if not API_BASE or not API_TOKEN:
        raise RuntimeError("GOATCOUNTER_SITE_API and GOATCOUNTER_API_KEY are required.")

    validate_api_base()
    print(f"Using GoatCounter API base: {API_BASE}", file=sys.stderr)
    total_pageviews, countries = collect_pageview_stats()
    previous_raw, previous_stats = load_previous_stats()

    if (
        not export_has_useful_data(total_pageviews, countries)
        and previous_stats
        and export_has_useful_data(
            previous_stats["total_pageviews"],
            previous_stats["countries"],
        )
    ):
        print(
            "Fresh GoatCounter stats were empty; keeping the previous published stats.",
            file=sys.stderr,
        )
        output_text = previous_raw if previous_raw.endswith("\n") else f"{previous_raw}\n"
    else:
        stats = build_stats_payload(total_pageviews, countries)
        output_text = json.dumps(stats, ensure_ascii=True, indent=2) + "\n"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
        output_file.write(output_text)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, urllib.error.URLError, json.JSONDecodeError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
