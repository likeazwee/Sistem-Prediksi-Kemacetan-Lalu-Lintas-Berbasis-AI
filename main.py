# main.py
from RouteGraph import generate_graph, predicted_speeds, segment_lengths
from Djikstra import dijkstra

# Bangun graf berdasarkan prediksi kecepatan
traffic_graph = generate_graph(predicted_speeds, segment_lengths)

# Tentukan titik awal dan tujuan
start = 'A'
goal = 'F'

# Jalankan algoritma Dijkstra
total_time, path = dijkstra(traffic_graph, start, goal)

# Tampilkan hasil
print(f"\n>> Rute optimal dari {start} ke {goal}: {' -> '.join(path)}")
print(f">> Estimasi waktu tempuh: {total_time:.2f} menit")
