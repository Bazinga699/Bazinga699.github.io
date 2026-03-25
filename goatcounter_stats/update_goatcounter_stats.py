#!/usr/bin/env python3

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


API_BASE = os.environ.get("GOATCOUNTER_SITE_API", "").rstrip("/")
API_TOKEN = os.environ.get("GOATCOUNTER_API_KEY", "")
ROOT_PATHS = [
    path.strip()
    for path in os.environ.get("GOATCOUNTER_ROOT_PATHS", "/,/index.html").split(",")
    if path.strip()
]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "country-stats.json")
ALL_TIME_START = "2000-01-01T00:00:00Z"
COUNTRY_CODE_ALIASES = {
    "HK": "CN",
    "MO": "CN",
    "TW": "CN",
}


def api_request(path, query=None):
    url = f"{API_BASE}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="GET",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def code_from_location(stat):
    value = (stat.get("id") or "").strip().upper()
    if not value:
        name = (stat.get("name") or "").strip().upper()
        if len(name) in (2, 5) and name[:2].isalpha():
            value = name

    if not value:
        return ""

    if "-" in value:
        return value.split("-", 1)[0]

    return COUNTRY_CODE_ALIASES.get(value[:2], value[:2])


def get_locations():
    stats = []
    offset = 0

    while True:
        payload = api_request(
            "/stats/locations",
            query={
                "start": ALL_TIME_START,
                "limit": 100,
                "offset": offset,
                "path_by_name": "true",
                "include_paths": ROOT_PATHS,
            },
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

    countries = [{"code": code, "visitors": count} for code, count in merged.items()]
    countries.sort(key=lambda item: (-item["visitors"], item["code"]))
    return countries


def get_total_visitors():
    payload = api_request(
        "/stats/total",
        query={
            "start": ALL_TIME_START,
            "path_by_name": "true",
            "include_paths": ROOT_PATHS,
        },
    )
    return int(payload.get("total", 0) or 0)


def main():
    if not API_BASE or not API_TOKEN:
        raise RuntimeError("GOATCOUNTER_SITE_API and GOATCOUNTER_API_KEY are required.")

    countries = get_locations()
    total_visitors = get_total_visitors()

    stats = {
        "title": "Visitors Around the World",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_unique_visitors": total_visitors,
        "total_countries": len(countries),
        "countries": countries,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
        json.dump(stats, output_file, ensure_ascii=True, indent=2)
        output_file.write("\n")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, urllib.error.URLError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
