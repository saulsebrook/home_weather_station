from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

# Update the following so that filepaths match your own

OUTSIDE = 'path_to_local.jsonl'
INSIDE = 'path_to_local.jsonl'
GARAGE = 'path_to_local.jsonl'
AIRCRAFT_JSON = 'path_to_local/stats.json'

# Display Aircraft data
def aircraft_data():
    aircraft_tracked = 0
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

# Main webpage - shows current readings
@app.route('/')
def home():
    sensors = get_latest_readings()
    aircraft = aircraft_data()
    return render_template('index.html', sensors=sensors, aircraft=aircraft)

# History page with simple graph
@app.route('/history/<sensor_id>')
def history(sensor_id):
    data = get_sensor_history(sensor_id, limit=288)  # Last 24h if reporting every 5min
    return render_template('history.html', sensor_id=sensor_id, data=data)

@app.route('/history')
def history():
    all_data = {}
    for sensor_id in ['INSIDE', 'OUTSIDE', 'GARAGE']:
        all_data[sensor_id] = get_sensor_history(sensor_id, limit=576)  # Last 48h if reporting every 5min
    return render_template('all-history.html', sensor_id=sensor_id, all_data=all_data)

# API endpoint to get historical data as JSON
@app.route('/api/history/<sensor_id>')
def api_history(sensor_id):
    limit = request.args.get('limit', 100, type=int)
    data = get_sensor_history(sensor_id, limit)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
