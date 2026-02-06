from flask import Flask, request, jsonify, render_template_string, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

DATA_FILE = '/home/pi/weather-station/sensor_data.jsonl'
AIRCRAFT_JSON = '/run/readsb/aircraft.json'

# Display Aircraft data
def aircraft_data():
    aircraft_tracked = 0;
    with open(AIRCRAFT_JSON, 'r') as f:
        data = json.load(f);
    for i in data['aircraft']:
        aircraft_tracked += 1;
        # or aircraft_tracked = len(data['aircraft']);
    return aircraft_tracked;

# Helper function to append data to JSONL file
def save_to_jsonl(data):
    with open(DATA_FILE, 'a') as f:
        f.write(json.dumps(data) + '\n')

# Helper function to get latest reading for each sensor
def get_latest_readings():
    if not os.path.exists(DATA_FILE):
        return {}
    
    latest = {}
    with open(DATA_FILE, 'r') as f:
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
