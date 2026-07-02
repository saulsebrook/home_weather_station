
from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import subprocess
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

AIRBAND_ACTIVE_CONFIG = "/usr/local/etc/rtl_airband_active.conf"
CUSTOM_CONF_PATH = "/usr/local/etc/rtl_airband_custom.conf"

AIRBAND_CONFIGS = {
    "All_freq": "/usr/local/etc/rtl_airband_CTR_E_W_CTAF.conf",
    "TWB_CTAF": "/usr/local/etc/rtl_airband_CTAF.conf",
    "YBOK": "/usr/local/etc/rtl_airband_YBOK.conf",
    # Add more preset configs here as you create them
    "CTR": "/usr/local/etc/rtl_airband_CTR.conf",    
# Add more preset configs here as you create them
}

@app.route('/api/airband', methods=['GET', 'POST'])
def airband():
    if request.method == 'POST':
        config_name = request.json.get('config')
        if config_name not in AIRBAND_CONFIGS:
            return jsonify({'status': 'error', 'message': 'Unknown config'}), 400
        config_path = AIRBAND_CONFIGS[config_name]
        subprocess.run(['sudo', 'ln', '-sf', config_path, AIRBAND_ACTIVE_CONFIG])
        subprocess.run(['sudo', 'systemctl', 'restart', 'rtl_airband'])
        return jsonify({'status': 'success', 'config': config_name})
    else:
        result = subprocess.run(['sudo', 'systemctl', 'is-active', 'rtl_airband'],
                               capture_output=True, text=True)
        return jsonify({'status': result.stdout.strip()})
        # Read symlink to find current config name
        current_config = None
        try:
            current_path = os.readlink(AIRBAND_ACTIVE_CONFIG)
            for name, path in AIRBAND_CONFIGS.items():
                if path == current_path:
                    current_config = name
                    break
            if not current_config:
                current_config = 'Custom'
        except Exception:
            pass
        return jsonify({'status': result.stdout.strip(), 'config': current_config})

@app.route('/api/airband/custom', methods=['POST'])
def airband_custom():
    data = request.json
    raw_freqs = data.get('freq', '')
    raw_labels = data.get('label', '')

    if not raw_freqs:
        return jsonify({'status': 'error', 'message': 'No frequency provided'}), 400

    freqs = [f.strip() for f in raw_freqs.split(',') if f.strip()]

    if raw_labels:
        labels = [l.strip() for l in raw_labels.split(',') if l.strip()]
        while len(labels) < len(freqs):
            labels.append(f'{freqs[len(labels)]} MHz')
    else:
        labels = [f'{f} MHz' for f in freqs]

    freqs_str = ', '.join(freqs)
    labels_str = ', '.join(f'"{l}"' for l in labels)
    name = raw_labels if raw_labels else freqs_str

    config_content = f"""devices:
(
    {{
        type = "rtlsdr";
        serial = "AIRBAND";
        gain = 29.0;
        mode = "scan";
        channels: (
            {{
                freqs = ({freqs_str});
                labels = ( {labels_str} );
                modulation = "am";
                outputs: (
                    {{
                        type = "icecast";
                        server = "192.168.1.133";
                        port = 8000;
                        mountpoint = "custom.mp3";
                        mountpoint = "ATC.mp3";
                        send_scan_freq_tags = true;
                        username = "source";
                        password = "password";
                        name = "{name}";
                        description = "Custom: {freqs_str}";
                    }}
                );
            }}
        );
    }}
);
"""

    with open(CUSTOM_CONF_PATH, 'w') as f:
        f.write(config_content)

    subprocess.run(['sudo', 'ln', '-sf', CUSTOM_CONF_PATH, AIRBAND_ACTIVE_CONFIG])
    subprocess.run(['sudo', 'systemctl', 'restart', 'rtl_airband'])

    return jsonify({'status': 'success', 'freqs': freqs, 'labels': labels})

@app.route('/api/debug/feelslike')
def debug_feelslike():
    latest = get_latest_readings()
    outside = latest.get('OUTSIDE', {})
    temp_c = outside.get('temperature')
    humidity = outside.get('humidity')
    
    try:
        wind_speed_kmh = get_wind_speed()
        wind_error = None
    except Exception as ex:
        wind_speed_kmh = 0
        wind_error = str(ex)
    
    wind_speed_ms = wind_speed_kmh / 3.6
    e = (humidity / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
    at = temp_c + (0.33 * e) - (0.70 * wind_speed_ms) - 4.00

    return jsonify({
        "temp_c": temp_c,
        "humidity": humidity,
        "wind_speed_kmh": wind_speed_kmh,
        "wind_speed_ms": round(wind_speed_ms, 3),
        "vapour_pressure_e": round(e, 3),
        "apparent_temp": round(at, 1),
        "wind_error": wind_error
    })

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
    data = get_sensor_history(sensor_id, limit=2016)  # Last 24h if reporting every 5min
    return render_template('history.html', sensor_id=sensor_id, data=data)

@app.route('/history-data')
def history_data():
    all_data = {}
    for sensor_id in ['INSIDE', 'OUTSIDE', 'GARAGE']:
        all_data[sensor_id] = get_sensor_history(sensor_id, limit=2016)  # Last 48h if reporting every 5min
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
    app.run(host='0.0.0.0', port=5000, threaded=True)
