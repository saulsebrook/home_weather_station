from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os
import openmeteo_requests
import pandas as pd
import requests_cache
from weather_calc import *
from config_py import *
from retry_requests import retry

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

def save_stats(data):
    updated = False
    aircraft_stats = aircraft_data()
    today = datetime.now().strftime('%Y-%m-%d %H:%M')

    if not os.path.exists(STATS):
        with open(STATS, 'w') as f:
            json.dump(INIT_CONFIG, f, indent=2)
    with open(STATS, 'r') as f:
        stats = json.load(f)

    if data['sensor_id'] == 'OUTSIDE':
        if data['temperature'] > stats['max_temp']:
            stats['max_temp'] = data['temperature']
            stats['max_temp_date'] = today
            updated = True
        if data['temperature'] < stats['min_temp']:
            stats['min_temp'] = data['temperature']
            stats['min_temp_date'] = today
            updated = True
        
    if stats['aircraft_max_distance'] < aircraft_stats['current_aircraft']['max_range']:
        stats['aircraft_max_distance'] = aircraft_stats['current_aircraft']['max_range']
        stats['aircraft_max_distance_date'] = today
        updated = True

    if updated:
        with open(STATS, 'w') as f:
            json.dump(stats, f, indent=2)


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

def get_stats():
    if not os.path.exists(STATS):
        return {}

    with open(STATS, 'r') as f:
        stats = json.load(f)

    return stats

