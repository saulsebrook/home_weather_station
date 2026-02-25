from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os
import openmeteo_requests
import pandas as pd
import requests_cache
from weather_calc import *
from sensor_data import *
from config_py import *
from retry_requests import retry

app = Flask(__name__)

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
        save_stats(data)
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
    stats = get_stats()
    sensors = get_latest_readings()
    aircraft = aircraft_data()
    batt_data = batt_history()
    battery = batt_data[-1] if batt_data else None
    feels_like = calculate_feelsLike()
    return render_template('index.html', battery=battery, stats=stats, sensors=sensors, aircraft=aircraft, feels_like=feels_like)

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
