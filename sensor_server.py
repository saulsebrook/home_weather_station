from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

app = Flask(__name__)

# Update the following so that filepaths match your own

OUTSIDE = '/home/pi/weather-station/OUTSIDE.jsonl'
INSIDE = '/home/pi/weather-station/INSIDE.jsonl'
GARAGE = '/home/pi/weather-station/GARAGE.jsonl'
AIRCRAFT_JSON = '/run/readsb/stats.json'
STATS = '/home/pi/weather-station/STATS.json'
BATT = '/home/pi/weather-station/BATT.json'

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

# Display Aircraft data
def aircraft_data():
    with open(AIRCRAFT_JSON, 'r') as f:
        data = json.load(f);
        max_distance_m = data.get('total', {}).get('max_distance', 0)
        max_distance_nm = round(max_distance_m / 1852, 1) if max_distance_m > 0 else 0
    stats = {
        "current_aircraft":{
            "total": data.get('aircraft_with_pos', 0),
            "max_range": max_distance_nm,
            "total_messages": data.get('total', {}).get('messages_valid', {}),
            } 
        }
    return stats

# Helper function to append data to JSONL file
def save_to_jsonl(data):
    if data['sensor_id'] == 'OUTSIDE':    
        with open(OUTSIDE, 'a') as f:
            f.write(json.dumps(data) + '\n')
    if data['sensor_id'] == 'INSIDE':    
        with open(INSIDE, 'a') as f:
            f.write(json.dumps(data) + '\n')
    if data['sensor_id'] == 'GARAGE':    
        with open(GARAGE, 'a') as f:
            f.write(json.dumps(data) + '\n')

def batt_history():
    if not os.path.exists(BATT):
        return[]
    with open(BATT, 'r') as f:
        return json.load(f)

def write_batt(data):
    history = batt_history()
    history.append({'level': data['level'], 'value': data['value'], 'timestamp': data['timestamp']})
    history = history[-100:]
    with open(BATT, 'w') as f:
        json.dump(history, f, indent=2)
        
# Helper function to get latest reading for each sensor
def get_latest_readings():
    latest = {}
    for filepath in [OUTSIDE, INSIDE, GARAGE]:
        if not os.path.exists(filepath):
            continue  
        if os.path.getsize(filepath) == 0:
            continue  
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line.strip())
                # Skip entries without sensor_id
                if 'sensor_id' not in data:
                    continue
                sensor_id = data['sensor_id']
                # Keep only the most recent reading for each sensor
                if sensor_id not in latest or data['timestamp'] > latest[sensor_id]['timestamp']:
                    latest[sensor_id] = data
    return latest
    
# Helper function to get historical data for a specific sensor
def get_sensor_history(sensor_id, limit=100):
    file_map = {
        'OUTSIDE' : OUTSIDE,
        'INSIDE' : INSIDE,
        'GARAGE' : GARAGE
    }
    filepath = file_map.get(sensor_id)
    if not os.path.exists(filepath):
        return []
    
    history = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line.strip())
            # Skip entries without sensor_id
            if 'sensor_id' not in data:
                continue
            if data['sensor_id'] == sensor_id:
                history.append(data)
    
    # Return most recent entries
    return history[-limit:]

# API endpoint - POST and GET requests via /api/sensor
@app.route('/api/sensor', methods=['POST', 'GET'])
def receive_data():
    if request.method == 'POST':
        data = request.json
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        # Save to JSONL file
        save_to_jsonl(data)
        return jsonify({'status': 'success'}), 200
    else:
        latest = get_latest_readings()
        return jsonify(latest), 200

@app.route('/api/batt', methods=['POST'])
def receive_batt():
    data = request.json
    if not data:
        return jsonify({'status': 'fail'}), 400
        # Add timestamp if not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    # Save to JSONL file
    write_batt(data)
    return jsonify({'status': 'success'}), 200

# Main webpage - shows current readings
@app.route('/')
def home():
    sensors = get_latest_readings()
    aircraft = aircraft_data()
    batt_data = batt_history()
    battery = batt_data[-1] if batt_data else None
    feels_like = calculate_feelsLike()
    return render_template('index.html', battery=battery, sensors=sensors, aircraft=aircraft, feels_like=feels_like)

# History page with simple graph
@app.route('/history/<sensor_id>')
def history(sensor_id):
    data = get_sensor_history(sensor_id, limit=576)  # Last 24h if reporting every 5min
    return render_template('history.html', sensor_id=sensor_id, data=data)

@app.route('/history-data')
def history_data():
    all_data = {}
    for sensor_id in ['INSIDE', 'OUTSIDE', 'GARAGE']:
        all_data[sensor_id] = get_sensor_history(sensor_id, limit=576)  # Last 48h if reporting every 5min
    return render_template('all-history.html', all_data=all_data)

# API endpoint to get historical data as JSON
@app.route('/api/history/<sensor_id>')
def api_history(sensor_id):
    limit = request.args.get('limit', 100, type=int)
    data = get_sensor_history(sensor_id, limit)
    return jsonify(data)

@app.route('/batt')
def batt_lvl():
    history = batt_history()
    if not history:
        return jsonify({'error': 'No battery data'})
    return jsonify(history[-1])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
