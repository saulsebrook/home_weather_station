from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os
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
    Calculate feels-like temperature.
    - Below 27°C: Wind Chill (uses wind speed)
    - At or above 27°C: Heat Index (uses humidity)
    
    Args:
        temp_c: Temperature in Celsius
        humidity: Relative humidity (0-100)
        wind_speed_kmh: Wind speed in km/h
    
    Returns:
        Feels-like temperature in Celsius
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

    if temp_c >= 27:
        # Heat Index (Steadman's formula, adapted for Celsius)
        T = temp_c
        R = humidity
        hi = (-8.78469475556
              + 1.61139411 * T
              + 2.33854883889 * R
              - 0.14611605 * T * R
              - 0.012308094 * T**2
              - 0.016424828 * R**2
              + 0.002211732 * T**2 * R
              + 0.00072546 * T * R**2
              - 0.000003582 * T**2 * R**2)
        return round(hi, 1)
    else:
        # Wind Chill (JAG/TI formula, valid for temp <= 10°C and wind > 4.8 km/h)
        # Falls back to actual temp if wind is too low
        if wind_speed_kmh < 4.8 or temp_c > 10:
            return round(temp_c, 1)
        wc = (13.12
              + 0.6215 * temp_c
              - 11.37 * wind_speed_kmh**0.16
              + 0.3965 * temp_c * wind_speed_kmh**0.16)
        return round(wc, 1)
