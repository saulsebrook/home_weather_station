from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

OUTSIDE = '/home/pi/weather-station/outside.jsonl'
INSIDE = '/home/pi/weather-station/inside.jsonl'
GARAGE = '/home/pi/weather-station/garage.jsonl'
AIRCRAFT_JSON = '/run/readsb/stats.json'

# Display Aircraft data
def aircraft_data():
    aircraft_tracked = 0;
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
    if not os.path.exists(OUTSIDE) or os.path.exists(INSIDE) or os.path.exists(GARAGE):
        return {}
    
    latest = {}
    for filepath in [OUTSIDE, INSIDE, GARAGE]:
     with open(filepath, 'r') as f:
        for line in f:
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
    if not os.path.exists(DATA_FILE):
        return []
    
    history = []
    with open(DATA_FILE, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            # Skip entries without sensor_id
            if 'sensor_id' not in data:
                continue
            if data['sensor_id'] == sensor_id:
                history.append(data)
    
    # Return most recent entries
    return history[-limit:]
# API endpoint - ESP32s POST data here
@app.route('/api/sensor', methods=['POST'])
def receive_data():
    data = request.json
    
    # Add timestamp if not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    
    # Save to JSONL file
    save_to_jsonl(data)
    
    return jsonify({'status': 'success'}), 200

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
    
    html = '''
    <html>
    <head>
        <title>{{ sensor_id }} History</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            canvas { max-width: 1000px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>{{ sensor_id }} - Historical Data</h1>
        <a href="/">← Back to Dashboard</a>
        
        <h2>Temperature</h2>
        <canvas id="tempChart"></canvas>
        
        <h2>Humidity</h2>
        <canvas id="humChart"></canvas>
        
        <h2>Pressure</h2>
        <canvas id="pressChart"></canvas>
        
        <script>
            const data = {{ data | tojson }};
            const timestamps = data.map(d => new Date(d.timestamp).toLocaleString());
            const temps = data.map(d => d.temperature);
            const humidity = data.map(d => d.humidity);
            const pressure = data.map(d => d.pressure);
            
            const chartConfig = (label, data, color) => ({
                type: 'line',
                data: {
                    labels: timestamps,
                    datasets: [{
                        label: label,
                        data: data,
                        borderColor: color,
                        backgroundColor: color + '33',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { ticks: { maxTicksLimit: 12 } }
                    }
                }
            });
            
            new Chart(document.getElementById('tempChart'), 
                chartConfig('Temperature (°C)', temps, 'rgb(255, 99, 132)'));
            new Chart(document.getElementById('humChart'), 
                chartConfig('Humidity (%)', humidity, 'rgb(54, 162, 235)'));
            new Chart(document.getElementById('pressChart'), 
                chartConfig('Pressure (hPa)', pressure, 'rgb(75, 192, 192)'));
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, sensor_id=sensor_id, data=data)

# API endpoint to get historical data as JSON
@app.route('/api/history/<sensor_id>')
def api_history(sensor_id):
    limit = request.args.get('limit', 100, type=int)
    data = get_sensor_history(sensor_id, limit)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
