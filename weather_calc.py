from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os
import math
import openmeteo_requests
import pandas as pd
import requests_cache
from sensor_data import *
from config_py import *
from retry_requests import retry

import time

import os

WIND_CACHE_FILE = '/tmp/wind_cache.json'
WIND_CACHE_TTL = 600

_cache_session = requests_cache.CachedSession('/home/pi/weather-station/.cache', expire_after=3600)
_retry_session = retry(_cache_session, retries=5, backoff_factor=0.2)
_openmeteo = openmeteo_requests.Client(session=_retry_session)

def get_wind_speed():
    # Read-only: the wind-refresh systemd timer is the sole writer of this cache.
    # The page must never make the (slow, blocking) API call itself.
    try:
        with open(WIND_CACHE_FILE, 'r') as f:
            cached = json.load(f)
            return cached['value']          # serve it even if stale — never block
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return 0                            # no cache yet → safe default, page still fast

def calculate_feelsLike():
    """
    Calculate apparent temperature using the Australian BOM formula,
    which accounts for wind speed, humidity, and temperature together.
    
    Formula: AT = Ta + 0.33*e - 0.70*ws - 4.00
    Where:
        Ta = air temperature (°C)
        e  = water vapour pressure (hPa)
        ws = wind speed (m/s) at 10m height
    
    Returns:
        Apparent temperature in Celsius
    """
    latest = get_latest_readings()
    outside = latest.get('OUTSIDE')
    if not outside:
        return None

    temp_c = outside['temperature']
    humidity = outside['humidity']

    try:
        wind_speed_kmh = get_wind_speed()
    except Exception:
        wind_speed_kmh = 0

    # Convert wind speed from km/h to m/s
    wind_speed_ms = wind_speed_kmh / 3.6

    # Water vapour pressure (hPa) using the Magnus approximation
    e = (humidity / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))

    # BOM Apparent Temperature formula
    at = temp_c + (0.33 * e) - (0.70 * wind_speed_ms) - 4.00

    return round(at, 1)
