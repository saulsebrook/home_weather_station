from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os
import openmeteo_requests
import pandas as pd
import requests_cache
import weather_calc
from retry_requests import retry

# Update the following so that filepaths match your own

OUTSIDE = '/home/pi/weather-station/OUTSIDE.jsonl'
INSIDE = '/home/pi/weather-station/INSIDE.jsonl'
GARAGE = '/home/pi/weather-station/GARAGE.jsonl'
AIRCRAFT_JSON = '/run/readsb/stats.json'
STATS = '/home/pi/weather-station/STATS.json'
BATT = '/home/pi/weather-station/BATT.json'
INIT_CONFIG = {'max_temp': 20, 'max_temp_date': None, 'min_temp': 20, 'min_temp_date': None, 'aircraft_max_distance': 200, 'aircraft_max_distance_date': None}
