#!/usr/bin/env python3

import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone


API_BASE = os.environ.get("GOATCOUNTER_SITE_API", "").rstrip("/")
API_TOKEN = os.environ.get("GOATCOUNTER_API_KEY", "")
ROOT_PATHS = {
    path.strip()
    for path in os.environ.get("GOATCOUNTER_ROOT_PATHS", "/,/index.html").split(",")
    if path.strip()
}
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "country-stats.json")


def api_request(path, method="GET", data=None, accept="application/json"):
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": accept,
    }
    payload = None if data is None else json.dumps(data).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def wait_for_export(export_id):
    for _ in range(60):
        payload = json.loads(api_request(f"/export/{export_id}").decode("utf-8"))
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
    rows = []
    for row in reader:
        if row:
            rows.append(row)
    return rows


def decode_csv_bytes(raw_bytes):
    if raw_bytes[:2] == b"\x1f\x8b":
        raw_bytes = gzip.decompress(raw_bytes)
    return raw_bytes.decode("utf-8")


def detect_field(row, suffix):
    for key in row.keys():
        if key.endswith(suffix):
            return key
    raise KeyError(f"Could not find field ending with {suffix}")


def build_stats(rows):
    if not rows:
        return {
            "title": "Visitor Map",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_unique_visitors": 0,
            "total_countries": 0,
            "countries": [],
        }

    sample = rows[0]
    path_field = detect_field(sample, "Path")
    event_field = detect_field(sample, "Event")
    session_field = detect_field(sample, "Session")
    location_field = detect_field(sample, "Location")

    total_sessions = set()
    countries = defaultdict(set)

    for row in rows:
        if parse_bool(row.get(event_field, "")):
            continue

        path = normalize_path(row.get(path_field, ""))
        if path not in ROOT_PATHS:
            continue

        session = row.get(session_field, "").strip()
        if not session:
            continue

        location = row.get(location_field, "").strip().upper()
        country_code = location.split("-", 1)[0] if location else ""

        total_sessions.add(session)
        if country_code:
            countries[country_code].add(session)

    country_items = [
        {"code": code, "visitors": len(sessions)}
        for code, sessions in countries.items()
    ]
    country_items.sort(key=lambda item: (-item["visitors"], item["code"]))

    return {
        "title": "Visitors Around the World",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_unique_visitors": len(total_sessions),
        "total_countries": len(country_items),
        "countries": country_items,
    }


def main():
    if not API_BASE or not API_TOKEN:
        raise RuntimeError("GOATCOUNTER_SITE_API and GOATCOUNTER_API_KEY are required.")

    export = json.loads(api_request("/export", method="POST").decode("utf-8"))
    export_id = export.get("id")
    if not export_id:
        raise RuntimeError("Failed to create GoatCounter export.")

    wait_for_export(export_id)
    csv_bytes = api_request(f"/export/{export_id}/download", accept="text/csv")
    csv_text = decode_csv_bytes(csv_bytes)
    rows = load_rows(csv_text)
    stats = build_stats(rows)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
        json.dump(stats, output_file, ensure_ascii=True, indent=2)
        output_file.write("\n")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, urllib.error.URLError, KeyError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
