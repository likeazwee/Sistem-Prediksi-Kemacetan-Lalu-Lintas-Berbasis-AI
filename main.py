from flask import Flask, render_template, request, jsonify
import datetime
import os
import sys
import time
import tracemalloc
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Add directories to path
sys.path.append('data')
sys.path.append('API')

from data import (
    generate_traffic_data, 
    load_road_network, 
    geocode_location, 
    shortest_route, 
    detect_congestion_points, 
    create_map
)
from sistem import TrafficPredictionSystem

app = Flask(__name__, template_folder='frontend')
traffic_system = TrafficPredictionSystem()

def analyze_performance(func, *args, **kwargs):
    tracemalloc.start()
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"[DEBUG] Execution time: {end_time - start_time:.6f} seconds")  # debug
    return {
        'result': result,
        'time': end_time - start_time,
        'memory': peak / 1024  # in KB
    }

def calculate_route_distance(G, route):
    """Calculate total distance of a route"""
    distance = 0
    if route and len(route) > 1:
        for u, v in zip(route[:-1], route[1:]):
            try:
                edge_data = G.get_edge_data(u, v)[0]
                distance += edge_data.get('length', 0)
            except:
                continue
    return distance

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
    total_distance_km = 0
    alt_distance_km = 0
    est_time_min = 0
    alt_est_time_sec = 0
    route_time_sec = 0
    route_memory_kb = 0

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
            data = generate_traffic_data()
            model_results = traffic_system.train_models(data)
            all_predictions = traffic_system.predict(jam, hari)
            predictions = {}

            is_weekend = 1 if hari in [6,7] else 0
            rush_hour = 1 if jam in [7,8,9,17,18,19] else 0
            features_df = pd.DataFrame([[jam, hari, is_weekend, rush_hour]],
                                       columns=traffic_system.feature_cols)

            if model_type == 'all':
                for model_name in all_predictions:
                    if model_name in model_results:
                        pred_perf = analyze_performance(
                            traffic_system.trained_models[model_name].predict,
                            features_df
                        )
                        predictions[model_name] = {
                            'prediction': pred_perf['result'][0],
                            'metrics': model_results[model_name]['metrics'],
                            'time': pred_perf['time']
                        }
                best_pred = max(predictions.values(), key=lambda x: x['prediction'])['prediction']
            else:
                mapping = {
                    'linear': 'Linear Regression',
                    'neural_network': 'Neural Network'
                }
                chosen = mapping.get(model_type, 'Linear Regression')
                if chosen in traffic_system.trained_models:
                    pred_perf = analyze_performance(
                        traffic_system.trained_models[chosen].predict,
                        features_df
                    )
                    predictions[chosen] = {
                        'prediction': pred_perf['result'][0],
                        'metrics': model_results[chosen]['metrics'],
                        'time': pred_perf['time']
                    }
                    best_pred = pred_perf['result'][0]

            try:
                G = load_road_network(wilayah)
                start_coords = geocode_location(lokasi_awal)
                end_coords = geocode_location(lokasi_tujuan)

                route_perf = analyze_performance(shortest_route, G, start_coords, end_coords)
                route = route_perf['result']
                route_time_sec = route_perf['time']
                route_memory_kb = route_perf['memory']

                # Calculate main route distance
                main_distance = calculate_route_distance(G, route)
                total_distance_km = round(main_distance / 1000, 2)
                est_time_min = round(((main_distance / 1000) / (best_pred if best_pred > 0 else 1)) * 60, 2)

                congestion_points = detect_congestion_points(G, route, threshold=15 if best_pred < 15 else 5)
                alt_route = None
                alt_distance = 0
                
                if congestion_points and route:
                    mid_node = route[len(route)//2]
                    try:
                        G_alt = G.copy()
                        G_alt.remove_node(mid_node)

                        alt_perf = analyze_performance(shortest_route, G_alt, start_coords, end_coords)
                        alt_route = alt_perf['result']
                        
                        # Calculate alternative route distance
                        if alt_route:
                            alt_distance = calculate_route_distance(G, alt_route)
                            alt_distance_km = round(alt_distance / 1000, 2)
                            alt_est_time_sec = round(((alt_distance / 1000) / (best_pred if best_pred > 0 else 1)) * 3600, 2)
                    except:
                        alt_route = None
                        alt_distance_km = 0
                        alt_est_time_sec = 0
                
                map_html = create_map(G, route, start_coords, end_coords, congestion_points, alt_route=alt_route)
            except Exception as e:
                error = f"Error membuat peta: {str(e)}"

    return render_template(
        'halaman.html',
        wilayah=wilayah,
        lokasi_awal=lokasi_awal,
        lokasi_tujuan=lokasi_tujuan,
        jam=jam,
        hari=hari,
        model_type=model_type,
        predictions=predictions,
        best_prediction=best_pred,
        map_html=map_html,
        error=error,
        total_distance_km=total_distance_km,
        alt_distance_km=alt_distance_km,
        est_time_min=est_time_min,
        alt_est_time_sec=alt_est_time_sec,
        route_time_sec=route_time_sec,
        route_memory_kb=route_memory_kb
    )

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    jam = data.get('jam', 9)
    hari = data.get('hari', 1)
    traffic_data = generate_traffic_data()
    model_results = traffic_system.train_models(traffic_data)
    predictions = traffic_system.predict(jam, hari)
    return jsonify({
        'success': True,
        'predictions': predictions,
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚦 Smart City Bengkulu - Traffic Prediction System")
    data = generate_traffic_data()
    traffic_system.train_models(data)
    app.run(debug=True, host='0.0.0.0', port=5000)