from flask import Flask, render_template_string, request, jsonify
import osmnx as ox
import networkx as nx
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np
import folium
import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Smart City Bengkulu - Traffic Prediction</title>
    <style>
        /* Reset and basic */
        body {
            margin: 0; 
            font-family: 'Poppins', sans-serif;
            background: #ffffff;
            color: #6b7280;
            line-height: 1.6;
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
        }
        .container {
            max-width: 1200px;
            width: 100%;
        }
        h1 {
            font-weight: 700;
            font-size: 48px;
            color: #111827;
            margin-bottom: 0.5em;
        }
        p.subtitle {
            font-size: 18px;
            color: #4b5563;
            margin-bottom: 2em;
        }
        form {
            background: #f9fafb;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
            margin-bottom: 2.5em;
        }
        .form-row {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 1.5em;
        }
        .form-group {
            flex: 1 1 280px;
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #374151;
        }
        input[type="text"], input[type="number"], select {
            padding: 10px 12px;
            border: 1.5px solid #d1d5db;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        input[type="text"]:focus, input[type="number"]:focus, select:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
        }
        button {
            background: #111827;
            color: white;
            padding: 14px 32px;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 18px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.3s ease;
            margin-right: 12px;
            user-select: none;
        }
        button:hover {
            background: #1f2937;
            transform: translateY(-2px);
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #e5e7eb;
            margin-bottom: 1em;
        }
        .tab {
            color: #6b7280;
            padding: 12px 24px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: color 0.3s, border-color 0.3s;
            user-select: none;
        }
        .tab.active {
            color: #111827;
            border-color: #2563eb;
        }
        .tab-content {
            display: none;
            background: #f9fafb;
            padding: 20px 30px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
        }
        .tab-content.active {
            display: block;
        }
        .result-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 0 10px rgb(0 0 0 / 0.05);
            padding: 20px;
            margin-bottom: 20px;
            color: #111827;
        }
        .result-title {
            font-weight: 700;
            font-size: 20px;
            margin-bottom: 12px;
        }
        .metric-line {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 16px;
        }
        .status {
            display: inline-block;
            font-weight: 700;
            padding: 8px 20px;
            border-radius: 9999px;
            margin-top: 12px;
        }
        .status.lancar {
            color: #065f46;
            background: #d1fae5;
        }
        .status.sedang {
            color: #78350f;
            background: #fde68a;
        }
        .status.macet {
            color: #991b1b;
            background: #fecaca;
        }
        #map {
            border-radius: 12px;
            box-shadow: 0 1px 6px rgb(0 0 0 / 0.1);
            width: 100%;
            height: 600px;
            margin-top: 30px;
        }
        .alert {
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            font-weight: 600;
            font-size: 18px;
        }
        .alert.success {
            background: #d1fae5;
            color: #065f46;
        }
        .alert.warning {
            background: #fde68a;
            color: #78350f;
        }
        .alert.danger {
            background: #fecaca;
            color: #991b1b;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🚦 Smart City Bengkulu</h1>
    <p class="subtitle">Sistem Prediksi Lalu Lintas Berbasis Kecerdasan Buatan</p>

    <form method="POST">
        <div class="form-row">
            <div class="form-group">
                <label>Wilayah:</label>
                <input type="text" name="wilayah" required value="{{ wilayah or 'Bengkulu, Indonesia' }}" />
            </div>
            <div class="form-group">
                <label>Lokasi Awal:</label>
                <input type="text" name="lokasi_awal" required value="{{ lokasi_awal or 'Universitas Bengkulu' }}" />
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Lokasi Tujuan:</label>
                <input type="text" name="lokasi_tujuan" required value="{{ lokasi_tujuan or 'Pasar Panorama Bengkulu' }}" />
            </div>
            <div class="form-group">
                <label>Jam (0-23):</label>
                <input type="number" name="jam" min="0" max="23" required value="{{ jam or 9 }}" />
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Hari (1=Senin, 7=Minggu):</label>
                <select name="hari" required>
                    {% for i in range(1, 8) %}
                    <option value="{{ i }}" {% if hari == i %}selected{% endif %}>
                        {{ ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu'][i-1] }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>Model AI:</label>
                <select name="model_type">
                    <option value="all" {% if model_type == 'all' %}selected{% endif %}>Semua Model (Perbandingan)</option>
                    <option value="linear" {% if model_type == 'linear' %}selected{% endif %}>Linear Regression</option>
                    <option value="decision_tree" {% if model_type == 'decision_tree' %}selected{% endif %}>Decision Tree</option>
                    <option value="random_forest" {% if model_type == 'random_forest' %}selected{% endif %}>Random Forest</option>
                    <option value="neural_network" {% if model_type == 'neural_network' %}selected{% endif %}>Neural Network</option>
                </select>
            </div>
        </div>
        <button type="submit">Analisis Lalu Lintas</button>
    </form>

    {% if predictions %}
    <div class="tabs">
        <div class="tab active" onclick="showTab('prediction')">Prediksi</div>
        <div class="tab" onclick="showTab('comparison')">Perbandingan Model</div>
        <div class="tab" onclick="showTab('recommendation')">Rekomendasi</div>
    </div>

    <div id="prediction" class="tab-content active">
        {% for model, result in predictions.items() %}
        <div class="result-card">
            <div class="result-title">{{ model }}</div>
            <div class="metric-line">
                <span>Kecepatan Prediksi:</span>
                <strong>{{ "%.1f"|format(result.prediction) }} km/h</strong>
            </div>
            {% set status_class = "lancar" if result.prediction > 30 else ("sedang" if result.prediction > 15 else "macet") %}
            {% set status_text = "Lancar" if result.prediction > 30 else ("Sedang" if result.prediction > 15 else "Macet") %}
            <div class="status {{ status_class }}">Status: {{ status_text }}</div>
            <div class="metric-line">
                <span>MAE:</span>
                <span>{{ "%.2f"|format(result.metrics.mae) }}</span>
            </div>
            <div class="metric-line">
                <span>R² Score:</span>
                <span>{{ "%.3f"|format(result.metrics.r2) }}</span>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="comparison" class="tab-content">
        {% for model, result in predictions.items() %}
        <div class="result-card" style="border-left: 5px solid #2563eb;">
            <div class="result-title">{{ model }}</div>
            <div class="metric-line">Akurasi: {{ "%.1f"|format(result.metrics.r2 * 100) }}%</div>
            <div class="metric-line">Error: {{ "%.2f"|format(result.metrics.mae) }}</div>
        </div>
        {% endfor %}
    </div>

    <div id="recommendation" class="tab-content">
        <div class="alert
            {{ 'danger' if best_prediction < 15 else ('warning' if best_prediction < 30 else 'success') }}">
            {% if best_prediction < 15 %}
            <p><strong>Kemacetan Tinggi Terdeteksi!</strong></p>
            <ul>
                <li>Aktifkan sistem peringatan dini kepada warga</li>
                <li>Optimasi pengaturan lampu lalu lintas</li>
                <li>Buka rute alternatif jika tersedia</li>
                <li>Kirim notifikasi ke aplikasi mobile warga</li>
            </ul>
            {% elif best_prediction < 30 %}
            <p><strong>Lalu Lintas Sedang</strong></p>
            <ul>
                <li>Monitor kondisi lalu lintas secara real-time</li>
                <li>Sesuaikan timing lampu lalu lintas</li>
                <li>Informasikan kondisi ke pengguna jalan</li>
            </ul>
            {% else %}
            <p><strong>Lalu Lintas Lancar</strong></p>
            <ul>
                <li>Kondisi optimal untuk perjalanan</li>
                <li>Pertahankan pengaturan lalu lintas saat ini</li>
                <li>Waktu ideal untuk aktivitas transportasi</li>
            </ul>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {% if map_html %}
        <div id="map">{{ map_html|safe }}</div>
    {% endif %}

    <script>
        const tabs = document.querySelectorAll('.tab');
        const contents = document.querySelectorAll('.tab-content');
        function showTab(id) {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            // Activate clicked tab by id
            // Activate tab button by matching data-target attribute (or we map id to tab)
            // Here find tab that triggers this id
            tabs.forEach(tab => {
                if (tab.textContent.toLowerCase() === (id === 'prediction' ? 'prediksi' : (id === 'comparison' ? 'perbandingan model' : 'rekomendasi'))) {
                    tab.classList.add('active');
                }
            });
            const content = document.getElementById(id);
            if (content) {
                content.classList.add('active');
            }
        }
    </script>
</div>
</body>
</html>
"""

class TrafficPredictionSystem:
    def __init__(self):
        self.models = {
            'Linear Regression': LinearRegression(),
            'Decision Tree': DecisionTreeRegressor(random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100,50), max_iter=1000, random_state=42)
        }
        self.trained_models = {}
        self.feature_cols = ['jam', 'hari', 'is_weekend', 'rush_hour']

    def generate_traffic_data(self):
        np.random.seed(42)
        n = 1000
        data = []
        for _ in range(n):
            jam = np.random.randint(0,24)
            hari = np.random.randint(1,8)
            is_weekend = 1 if hari in [6,7] else 0
            rush_hour = 1 if jam in [7,8,9,17,18,19] else 0
            base_speed = 35
            if rush_hour:
                base_speed -= np.random.uniform(10,20)
            if is_weekend:
                base_speed += np.random.uniform(5,10)
            if 22 <= jam or jam <= 6:
                base_speed += np.random.uniform(8,15)
            elif 10 <= jam <= 16:
                base_speed += np.random.uniform(2,8)
            speed = max(5, base_speed + np.random.normal(0,5))
            data.append({
                'jam': jam,
                'hari': hari,
                'is_weekend': is_weekend,
                'rush_hour': rush_hour,
                'kecepatan': speed
            })
        return pd.DataFrame(data)

    def train_models(self, data):
        X = data[self.feature_cols]
        y = data['kecepatan']
        X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

        results = {}
        for name, model in self.models.items():
            try:
                model.fit(X_train, y_train)
                self.trained_models[name] = model
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                results[name] = {
                    'model': model,
                    'metrics': {'mae': mae, 'r2': r2}
                }
            except Exception:
                continue
        return results

    def predict(self, jam, hari, model_name=None):
        is_weekend = 1 if hari in [6,7] else 0
        rush_hour = 1 if jam in [7,8,9,17,18,19] else 0
        features = pd.DataFrame([[jam, hari, is_weekend, rush_hour]], columns=self.feature_cols)
        if model_name and model_name in self.trained_models:
            return self.trained_models[model_name].predict(features)[0]
        else:
            preds = {}
            for name, model in self.trained_models.items():
                preds[name] = model.predict(features)[0]
            return preds

def load_road_network(area):
    folder = "cache_peta"
    import os
    os.makedirs(folder, exist_ok=True)
    filename = folder + "/" + area.replace(",", "").replace(" ", "_") + ".graphml"
    if os.path.exists(filename):
        return ox.load_graphml(filename)
    graph = ox.graph_from_place(area, network_type='drive')
    ox.save_graphml(graph, filename)
    return graph

def geocode_location(location, cache={}):
    if location in cache:
        return cache[location]
    try:
        coord = ox.geocode(location)
        cache[location] = coord
        return coord
    except Exception:
        fallback = {
            'universitas bengkulu': (-3.7666, 102.2592),
            'pasar panorama bengkulu': (-3.7950, 102.2612),
            'bengkulu': (-3.8004, 102.2655)
        }
        loc_lower = location.lower()
        for key, val in fallback.items():
            if key in loc_lower:
                cache[location] = val
                return val
        default = (-3.8004, 102.2655)
        cache[location] = default
        return default

def shortest_route(G, start, end):
    orig_node = ox.distance.nearest_nodes(G, start[1], start[0])
    dest_node = ox.distance.nearest_nodes(G, end[1], end[0])
    try:
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        return route
    except Exception:
        return None

def detect_congestion_points(G, route, threshold=15):
    if not route or len(route) < 2:
        return []
    points = []
    mid_idx = len(route)//2
    node = route[mid_idx]
    lat = G.nodes[node]['y']
    lon = G.nodes[node]['x']
    points.append((lat, lon))
    return points

def create_map(G, route, start_coords, end_coords, congestion_points):
    center_lat = (start_coords[0] + end_coords[0]) / 2
    center_lon = (start_coords[1] + end_coords[1]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")

    folium.Marker(location=start_coords, popup="Lokasi Awal", icon=folium.Icon(color="green", icon="play")).add_to(m)
    folium.Marker(location=end_coords, popup="Lokasi Tujuan", icon=folium.Icon(color="red", icon="stop")).add_to(m)

    if route and len(route) > 1:
        route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route if n in G.nodes]
        folium.PolyLine(route_coords, color='blue', weight=4, opacity=0.8).add_to(m)

    for lat, lon in congestion_points:
        folium.Marker(
            location=[lat, lon],
            popup="Titik Kemacetan",
            icon=folium.Icon(color="orange", icon="exclamation-triangle", prefix='fa')
        ).add_to(m)
    return m._repr_html_()

traffic_system = TrafficPredictionSystem()

@app.route('/', methods=['GET','POST'])
def index():
    predictions = None
    map_html = None
    error = None
    wilayah = ""
    lokasi_awal = ""
    lokasi_tujuan = ""
    jam = 9
    hari = 1
    model_type = "all"
    best_pred = 0

    if request.method == 'POST':
        wilayah = request.form.get('wilayah', 'Bengkulu, Indonesia')
        lokasi_awal = request.form.get('lokasi_awal', 'Universitas Bengkulu')
        lokasi_tujuan = request.form.get('lokasi_tujuan', 'Pasar Panorama Bengkulu')
        try:
            jam = int(request.form.get('jam', 9))
            hari = int(request.form.get('hari', 1))
        except:
            error = "Jam dan Hari harus angka valid"
        model_type = request.form.get('model_type', 'all')

        if not error:
            data = traffic_system.generate_traffic_data()
            model_results = traffic_system.train_models(data)
            all_predictions = traffic_system.predict(jam, hari)
            predictions = {}
            if model_type == 'all':
                for model_name, pred in all_predictions.items():
                    if model_name in model_results:
                        predictions[model_name] = {
                            'prediction': pred,
                            'metrics': model_results[model_name]['metrics']
                        }
                best_pred = max(predictions.values(), key=lambda x: x['prediction'])['prediction']
            else:
                mapping = {
                    'linear': 'Linear Regression',
                    'decision_tree': 'Decision Tree',
                    'random_forest': 'Random Forest',
                    'neural_network': 'Neural Network'
                }
                chosen = mapping.get(model_type, 'Linear Regression')
                pred = all_predictions[chosen] if chosen in all_predictions else None
                if pred is not None and chosen in model_results:
                    predictions[chosen] = {
                        'prediction': pred,
                        'metrics': model_results[chosen]['metrics']
                    }
                    best_pred = pred

            try:
                G = load_road_network(wilayah)
                start_coords = geocode_location(lokasi_awal)
                end_coords = geocode_location(lokasi_tujuan)
                route = shortest_route(G, start_coords, end_coords)
                congestion_points = detect_congestion_points(G, route, threshold=15 if best_pred < 15 else 5)
                map_html = create_map(G, route, start_coords, end_coords, congestion_points)
            except Exception as e:
                error = f"Error membuat peta: {str(e)}"

    return render_template_string(
        HTML_TEMPLATE,
        wilayah=wilayah,
        lokasi_awal=lokasi_awal,
        lokasi_tujuan=lokasi_tujuan,
        jam=jam,
        hari=hari,
        model_type=model_type,
        predictions=predictions,
        best_prediction=best_pred,
        map_html=map_html,
        error=error
    )

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    jam = data.get('jam', 9)
    hari = data.get('hari', 1)
    traffic_data = traffic_system.generate_traffic_data()
    model_results = traffic_system.train_models(traffic_data)
    predictions = traffic_system.predict(jam, hari)
    return jsonify({
        'success': True,
        'predictions': predictions,
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚦 Smart City Bengkulu - Traffic Prediction System")
    data = traffic_system.generate_traffic_data()
    traffic_system.train_models(data)
    app.run(debug=True, host='0.0.0.0', port=5000)


