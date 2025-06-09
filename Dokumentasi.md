# Dokumentasi Kode Sistem Prediksi Lalu Lintas Berbasis AI

## Daftar Isi
- [Arsitektur Sistem](#arsitektur-sistem)
- [Komponen Utama](#komponen-utama)
- [API dan Machine Learning](#api-dan-machine-learning)
- [Data Processing](#data-processing)
- [Frontend Interface](#frontend-interface)
- [Main Application](#main-application)
- [Analisis Teknis](#analisis-teknis)
- [Perbandingan Model](#perbandingan-sistem)
## Arsitektur Sistem

Smart City Bengkulu menggunakan arsitektur multi-layer yang terdiri dari:

```
┌─────────────────────────────────────────┐
│           Frontend Layer                │
│         (halaman.html)                  │
├─────────────────────────────────────────┤
│          Controller Layer               │
│           (main.py)                     │
├─────────────────────────────────────────┤
│       Machine Learning Layer           │
│          (sistem.py)                    │
├─────────────────────────────────────────┤
│        Data Processing Layer           │
│           (data.py)                     │
└─────────────────────────────────────────┘
```

## Komponen Utama

### 1. Machine Learning Engine (`sistem.py`)

#### Class TrafficPredictionSystem

```python
class TrafficPredictionSystem:
    def __init__(self):
        self.models = {
            'Linear Regression': LinearRegression(),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100,50), 
                                         max_iter=1000, random_state=42)
        }
        self.trained_models = {}
        self.feature_cols = ['jam', 'hari', 'is_weekend', 'rush_hour']
```

**Fitur Utama:**
- **Dual Model Architecture**: Menggunakan dua algoritma ML berbeda untuk perbandingan performa
- **Feature Engineering**: Ekstraksi fitur temporal untuk analisis lalu lintas
- **Model Training Pipeline**: Proses pelatihan otomatis dengan train-test split
- **Performance Metrics**: Evaluasi menggunakan MAE dan R² Score

### 📐 Rumus Evaluasi Model

#### Mean Absolute Error (MAE)

Mengukur rata-rata kesalahan absolut:

```
MAE = (1/n) * ∑ |yᵢ - ŷᵢ|
```

* $yᵢ$ = nilai aktual
* $ŷᵢ$ = nilai prediksi
* $n$ = jumlah data

Semakin kecil MAE, semakin akurat model.

### 📐 Rumus Evaluasi Model

#### Mean Absolute Error (MAE)

Mengukur rata-rata kesalahan absolut:

```
MAE = (1/n) * ∑ |yᵢ - ŷᵢ|
```

* $yᵢ$ = nilai aktual
* $ŷᵢ$ = nilai prediksi
* $n$ = jumlah data

Semakin kecil MAE, semakin akurat model.

#### Method `train_models()`

```python
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
```

**Analisis Kode:**
- Menggunakan 80-20 split untuk training-testing
- Exception handling untuk stabilitas sistem
- Metrics calculation untuk evaluasi model

#### Method `predict()`

```python
def predict(self, jam, hari, model_name=None):
    is_weekend = 1 if hari in [6,7] else 0
    rush_hour = 1 if jam in [7,8,9,17,18,19] else 0
    features = pd.DataFrame([[jam, hari, is_weekend, rush_hour]], 
                          columns=self.feature_cols)
    
    if model_name and model_name in self.trained_models:
        return self.trained_models[model_name].predict(features)[0]
    else:
        preds = {}
        for name, model in self.trained_models.items():
            preds[name] = model.predict(features)[0]
        return preds
```

**Feature Engineering:**
- `is_weekend`: Binary flag untuk hari weekend (Sabtu-Minggu)
- `rush_hour`: Binary flag untuk jam sibuk (07:00-09:00, 17:00-19:00)
- Dynamic prediction untuk single atau multiple models

### 2. Data Processing Engine (`data.py`)

#### Traffic Data Generation

```python
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
            'jam': jam, 'hari': hari, 'is_weekend': is_weekend,
            'rush_hour': rush_hour, 'kecepatan': speed
        })
    return pd.DataFrame(data)
```

**Logika Simulasi Traffic:**
- **Base Speed**: 35 km/jam sebagai kecepatan normal
- **Rush Hour Penalty**: Pengurangan 10-20 km/jam saat jam sibuk
- **Weekend Bonus**: Peningkatan 5-10 km/jam saat weekend
- **Night Time Bonus**: Peningkatan 8-15 km/jam saat dini hari
- **Daytime Bonus**: Peningkatan 2-8 km/jam saat siang hari
- **Noise Addition**: Gaussian noise untuk realisme data

#### Road Network Management

```python
def load_road_network(area):
    folder = "cache_peta"
    os.makedirs(folder, exist_ok=True)
    filename = folder + "/" + area.replace(",", "").replace(" ", "_") + ".graphml"
    
    if os.path.exists(filename):
        return ox.load_graphml(filename)
    
    graph = ox.graph_from_place(area, network_type='drive')
    ox.save_graphml(graph, filename)
    return graph
```

**Optimasi Performa:**
- **Caching System**: Menyimpan graph jaringan jalan untuk mengurangi API calls
- **File-based Storage**: Menggunakan GraphML format untuk persistence
- **Lazy Loading**: Load graph hanya saat diperlukan

#### Geocoding dengan Fallback

```python
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
```

**Robustness Features:**
- **Memory Caching**: In-memory cache untuk koordinat yang sudah di-resolve
- **Fallback Coordinates**: Koordinat backup untuk lokasi umum di Bengkulu
- **Error Handling**: Graceful fallback ke koordinat default

#### Route Calculation

```python
def shortest_route(G, start, end):
    orig_node = ox.distance.nearest_nodes(G, start[1], start[0])
    dest_node = ox.distance.nearest_nodes(G, end[1], end[0])
    try:
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        return route
    except Exception:
        return None
```

**Algoritma Routing:**
- **Nearest Node Mapping**: Mapping koordinat GPS ke node terdekat di graph
- **Dijkstra Algorithm**: NetworkX shortest_path menggunakan algoritma Dijkstra
- **Weight-based Optimization**: Optimasi berdasarkan panjang jalan (length)

#### Congestion Detection

```python
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
```

**Simple Congestion Logic:**
- **Midpoint Detection**: Mendeteksi kemacetan di titik tengah rute
- **Threshold-based**: Berdasarkan prediksi kecepatan < threshold
- **Strategic Positioning**: Penempatan marker pada lokasi strategis

### 3. Frontend Interface (`halaman.html`)

#### Modern UI Design

```css
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
```

**Design Principles:**
- **Minimalist Approach**: Clean white background dengan subtle shadows
- **Typography**: Poppins font untuk modern appearance
- **Responsive Layout**: Flexbox-based centering
- **Color Palette**: Neutral grays dengan blue accents

#### Interactive Form Elements

```css
input[type="text"]:focus, input[type="number"]:focus, select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
}

button:hover {
    background: #1f2937;
    transform: translateY(-2px);
}
```

**UX Enhancements:**
- **Focus States**: Blue glow effect pada input focus
- **Hover Animations**: Subtle transform effects pada button hover
- **Visual Feedback**: Color transitions untuk interaksi user

#### Dynamic Status Indicators

```css
.status.lancar { color: #065f46; background: #d1fae5; }
.status.sedang { color: #78350f; background: #fde68a; }
.status.macet { color: #991b1b; background: #fecaca; }
```

**Traffic Status Classification:**
- **Lancar**: > 30 km/jam (Green theme)
- **Sedang**: 15-30 km/jam (Yellow theme)
- **Macet**: < 15 km/jam (Red theme)

#### Tab-based Interface

```javascript
function showTab(id) {
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));
    tabs.forEach(tab => {
        if (tab.textContent.toLowerCase() === (id === 'prediction' ? 'prediksi' : 'perbandingan model')) {
            tab.classList.add('active');
        }
    });
    const content = document.getElementById(id);
    if (content) {
        content.classList.add('active');
    }
}
```

**Interactive Features:**
- **Tab Switching**: Dynamic content switching tanpa page reload
- **Active State Management**: CSS class manipulation untuk visual feedback
- **Content Organization**: Separation antara prediction results dan model comparison

### 4. Main Application Controller (`main.py`)

#### Flask Application Setup

```python
app = Flask(__name__, template_folder='frontend')
traffic_system = TrafficPredictionSystem()

def analyze_performance(func, *args, **kwargs):
    tracemalloc.start()
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        'result': result,
        'time': end_time - start_time,
        'memory': peak / 1024  # in KB
    }
```

**Performance Monitoring:**
- **Time Tracking**: High-precision timing menggunakan `perf_counter()`
- **Memory Profiling**: Memory usage tracking dengan `tracemalloc`
- **Decorator Pattern**: Reusable performance analysis function

#### Route Handler - Main Endpoint

```python
@app.route('/', methods=['GET','POST'])
def index():
    predictions = None
    map_html = None
    error = None
    # ... parameter initialization
    
    if request.method == 'POST':
        # Form data extraction
        wilayah = request.form.get('wilayah', 'Bengkulu, Indonesia')
        lokasi_awal = request.form.get('lokasi_awal', 'Universitas Bengkulu')
        lokasi_tujuan = request.form.get('lokasi_tujuan', 'Pasar Panorama Bengkulu')
        
        try:
            jam = int(request.form.get('jam', 9))
            hari = int(request.form.get('hari', 1))
        except:
            error = "Jam dan Hari harus angka valid"
```

**Request Processing:**
- **Form Validation**: Input sanitization dan type conversion
- **Default Values**: Fallback values untuk semua parameters
- **Error Handling**: Graceful error handling dengan user feedback

#### Machine Learning Pipeline

```python
if not error:
    data = generate_traffic_data()
    model_results = traffic_system.train_models(data)
    all_predictions = traffic_system.predict(jam, hari)
    predictions = {}
    
    # Feature preparation
    is_weekend = 1 if hari in [6,7] else 0
    rush_hour = 1 if jam in [7,8,9,17,18,19] else 0
    features_df = pd.DataFrame([[jam, hari, is_weekend, rush_hour]],
                               columns=traffic_system.feature_cols)
```

**Pipeline Execution:**
1. **Data Generation**: Create synthetic traffic data
2. **Model Training**: Train semua models yang tersedia
3. **Feature Engineering**: Create feature vector untuk prediction
4. **Prediction Execution**: Run prediction dengan performance monitoring

#### Model Selection Logic

```python
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
    # ... single model execution
```

**Dynamic Model Selection:**
- **All Models Mode**: Run comparison antara semua available models
- **Single Model Mode**: Execute specific model yang dipilih user
- **Best Prediction**: Select highest speed prediction untuk route calculation

#### Route Processing Pipeline

```python
try:
    G = load_road_network(wilayah)
    start_coords = geocode_location(lokasi_awal)
    end_coords = geocode_location(lokasi_tujuan)
    
    route_perf = analyze_performance(shortest_route, G, start_coords, end_coords)
    route = route_perf['result']
    route_time_sec = route_perf['time']
    route_memory_kb = route_perf['memory']
    
    # Distance calculation
    main_distance = calculate_route_distance(G, route)
    total_distance_km = round(main_distance / 1000, 2)
    est_time_min = round(((main_distance / 1000) / (best_pred if best_pred > 0 else 1)) * 60, 2)
```

**Route Calculation Process:**
1. **Network Loading**: Load road network dengan caching
2. **Geocoding**: Convert location names ke coordinates
3. **Route Finding**: Calculate shortest path
4. **Performance Tracking**: Monitor execution time dan memory usage
5. **Distance Calculation**: Calculate total route distance
6. **Time Estimation**: Estimate travel time berdasarkan predicted speed

#### Alternative Route Generation

```python
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
        
        if alt_route:
            alt_distance = calculate_route_distance(G, alt_route)
            alt_distance_km = round(alt_distance / 1000, 2)
            alt_est_time_sec = round(((alt_distance / 1000) / (best_pred if best_pred > 0 else 1)) * 3600, 2)
    except:
        alt_route = None
```

**Alternative Route Logic:**
- **Congestion Detection**: Identify potential congestion points
- **Graph Modification**: Remove congested node untuk force alternative path
- **Alternative Calculation**: Calculate new route avoiding congestion
- **Comparison Metrics**: Calculate distance dan time untuk comparison

#### API Endpoint

```python
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
```

**RESTful API Features:**
- **JSON Input/Output**: Standard REST API format
- **Parameter Extraction**: Safe parameter extraction dengan defaults
- **Timestamp**: ISO format timestamp untuk tracking
- **Success Indicator**: Boolean success flag untuk error handling

## Analisis Teknis

### Performance Optimizations

1. **Ca
2. **Memory Management**
   - Memory profiling untuk setiap major operation
   - Tracemalloc integration untuk detailed memory tracking
   - Peak memory usage reporting

3. **Error Handling**
   - Graceful fallback untuk geocoding failures
   - Exception handling di setiap critical operation
   - User-friendly error messages

### Scalability Considerations

1. **Data Generation**
   - Synthetic data generation untuk consistent testing
   - Configurable dataset size (default: 1000 samples)
   - Random seed untuk reproducible results

2. **Model Architecture**
   - Extensible model dictionary untuk easy model addition
   - Pluggable ML algorithms
   - Performance metrics standardization

3. **Route Calculation**
   - OSMnx integration untuk real-world road networks
   - NetworkX graph algorithms untuk efficient pathfinding
   - Alternative route generation untuk traffic optimization


## Perbandingan Sistem

### 📊 Visualisasi Perbandingan Algoritma

![GUI Map Location](https://github.com/likeazwee/Sistem-Prediksi-Kemacetan-Lalu-Lintas-Berbasis-AI/blob/e38800ac4a1c8dedcc2a3971903ad6d366de0a53/Image_UI/perbandingan.png)

---

### Analisis Model

### 1. **Akurasi dan Error**
- **Linear Regression** menunjukkan akurasi yang sedikit lebih tinggi.
- **MAE (Mean Absolute Error)** lebih rendah pada Linear Regression (5.02 vs 5.08), menunjukkan prediksi lebih dekat ke nilai aktual.
- **R² Score**: Linear Regression menjelaskan variasi data lebih baik (0.775 vs 0.774).

### 2. **Prediksi Kecepatan**
- Linear Regression memprediksi kecepatan rata-rata: **20.17 km/jam**
- Neural Network memprediksi kecepatan rata-rata: **19.42 km/jam**

### 3. **Waktu Eksekusi**
- Neural Network memiliki waktu eksekusi yang lebih cepat (0.0017 s), namun perbedaannya sangat kecil dan tidak signifikan dalam aplikasi real-time.

---

### Kesimpulan Perbandingan

- **Linear Regression** unggul secara akurasi dan interpretabilitas, serta cocok untuk data sederhana atau jumlah fitur terbatas.
- **Neural Network** meskipun sedikit lebih cepat, tidak memberikan peningkatan signifikan dalam akurasi.
- Untuk penggunaan saat ini, **Linear Regression lebih direkomendasikan**.
- Namun, jika data menjadi lebih kompleks atau non-linear, **Neural Network** bisa dipertimbangkan untuk pengembangan ke depan.

---

## Kesimpulan Teknis

Sistem prediksi lalu lintas ini mendemonstrasikan implementasi end-to-end machine learning application dengan fokus pada:

- **Modular Architecture**: Separation of concerns dengan clear layer boundaries
- **Performance Monitoring**: Comprehensive tracking execution time dan memory usage
- **User Experience**: Modern web interface dengan interactive features
- **Scalability**: Extensible design untuk future enhancements
- **Reliability**: Robust error handling dan fallback mechanisms

Kode ini suitable untuk development lebih lanjut dan dapat dijadikan foundation untuk smart city traffic management systems yang lebih kompleks.
