import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
import folium
import os

def generate_traffic_data():
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

def load_road_network(area):
    folder = "cache_peta"
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

def create_map(G, route, start_coords, end_coords, congestion_points, alt_route=None):
    center_lat = (start_coords[0] + end_coords[0]) / 2
    center_lon = (start_coords[1] + end_coords[1]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    folium.Marker(location=start_coords, popup="Lokasi Awal", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(location=end_coords, popup="Lokasi Tujuan", icon=folium.Icon(color="red")).add_to(m)

    if route and len(route) > 1:
        route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route if n in G.nodes]
        folium.PolyLine(route_coords, color='orange', weight=5, tooltip="Jalur Utama").add_to(m)

    if alt_route and len(alt_route) > 1:
        alt_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in alt_route if n in G.nodes]
        folium.PolyLine(alt_coords, color='blue', weight=4, dash_array='5, 10', tooltip="Jalur Alternatif").add_to(m)

    for lat, lon in congestion_points:
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
            popup='Titik Kemacetan'
        ).add_to(m)

    legend_html = """
     <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 0 5px rgba(0,0,0,0.3);">
         <strong>Legenda:</strong><br>
         <i style="background: red; width: 12px; height: 12px; display: inline-block;"></i> Titik Macet<br>
         <i style="background: orange; width: 12px; height: 12px; display: inline-block;"></i> Jalur Utama<br>
         <i style="background: blue; width: 12px; height: 12px; display: inline-block;"></i> Jalur Alternatif<br>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m._repr_html_()
