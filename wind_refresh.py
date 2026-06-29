#!/usr/bin/env python3
"""
wind_refresh.py — fetch current wind speed from Open-Meteo and write it to the
cache file. Run by a systemd timer every few minutes so the web app never has to
make this (slow, blocking, external) call during a page load.

The Flask app only ever READS /tmp/wind_cache.json; this script is the only writer.
"""
import json
import time
import sys

import openmeteo_requests
import requests_cache
from retry_requests import retry

WIND_CACHE_FILE = "/tmp/wind_cache.json"

# Same session setup as the app had, but here it's off the request path so the
# retries/backoff can't hurt anyone's page load.
_cache_session = requests_cache.CachedSession(
    "/home/pi/weather-station/.cache", expire_after=3600
)
_retry_session = retry(_cache_session, retries=5, backoff_factor=0.2)
_openmeteo = openmeteo_requests.Client(session=_retry_session)


def fetch_wind():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -27.5,
        "longitude": 151.94,
        "current": "wind_speed_10m",
        "timezone": "Australia/Sydney",
        "forecast_days": 1,
    }
    responses = _openmeteo.weather_api(url, params=params)
    current = responses[0].Current()
    return current.Variables(0).Value()


def main():
    try:
        wind = fetch_wind()
    except Exception as ex:
        # Don't clobber a good cache with an error. Just log and leave the last
        # known value in place for the app to keep serving.
        print(f"wind_refresh: fetch failed, keeping existing cache: {ex}", file=sys.stderr)
        return 1

    tmp = WIND_CACHE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"value": wind, "timestamp": time.time()}, f)
    # Atomic replace so a reader never sees a half-written file.
    import os
    os.replace(tmp, WIND_CACHE_FILE)
    print(f"wind_refresh: wrote {wind} m/s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
