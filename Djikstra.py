
import heapq

# Representasi graf jalan (simpul: nama lokasi, bobot: waktu tempuh atau tingkat kemacetan)
graph = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
    'D': {'B': 5, 'C': 8, 'E': 2, 'F': 6},
    'E': {'C': 10, 'D': 2, 'F': 2},
    'F': {'D': 6, 'E': 2}
}

def dijkstra(graph, start, goal):
    queue = [(0, start, [])]  # (total_cost, current_node, path)
    visited = set()

    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        if node == goal:
            return (cost, path)

        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return (float('inf'), [])  # Jika tidak ditemukan

# Contoh pemakaian
start_node = 'A'
goal_node = 'F'

cost, path = dijkstra(graph, start_node, goal_node)
print(f"Rute terbaik dari {start_node} ke {goal_node}: {' -> '.join(path)}")
print(f"Total bobot (estimasi waktu/tempuh): {cost}")
