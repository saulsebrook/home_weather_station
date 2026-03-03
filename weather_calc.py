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

def get_wind_speed():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -27.5,
        "longitude": 151.94,
        "current": "wind_speed_10m",
        "timezone": "Australia/Sydney",
        "forecast_days": 1,
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    current_wind_speed_10m = current.Variables(0).Value()
    return current_wind_speed_10m

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