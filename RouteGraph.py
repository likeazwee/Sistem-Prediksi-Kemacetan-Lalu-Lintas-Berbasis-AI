predicted_speeds = {
    'A-B': 30,
    'B-C': 12,
    'C-D': 8,
    'D-E': 50,
    'E-F': 40,
    'B-D': 25,
    'C-E': 15
}

# Panjang jalan tiap ruas (km)
segment_lengths = {
    'A-B': 2,
    'B-C': 1,
    'C-D': 3,
    'D-E': 4,
    'E-F': 2,
    'B-D': 3,
    'C-E': 5
}

# Konversi ke waktu tempuh (menit) berdasarkan prediksi

def generate_graph(predicted_speeds, segment_lengths):
    import collections
    graph = collections.defaultdict(dict)

    for segment, speed in predicted_speeds.items():
        distance = segment_lengths[segment]  # dalam km
        time = distance / (speed / 60)  # waktu dalam menit
        src, dst = segment.split('-')

        graph[src][dst] = round(time, 2)
        graph[dst][src] = round(time, 2)  # anggap dua arah

    return dict(graph)

if __name__ == "__main__":
    graph = generate_graph(predicted_speeds, segment_lengths)
    from pprint import pprint
    pprint(graph)
