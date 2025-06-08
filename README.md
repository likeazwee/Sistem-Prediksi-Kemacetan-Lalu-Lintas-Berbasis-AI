
# 🚦 Sistem Prediksi Kemacetan Lalu Lintas Berbasis Kecerdasan Buatan

Aplikasi berbasis web untuk memprediksi kecepatan lalu lintas dan mendeteksi potensi kemacetan di wilayah tertentu. Sistem ini tidak menggunakan video CCTV, melainkan mengandalkan data waktu (jam, hari, hari libur, jam sibuk) serta simulasi data wilayah dan rute pengguna, dengan visualisasi rute dan hasil prediksi secara interaktif di peta.

---

## 👥 Anggota Kelompok 6

| Nama                     | GitHub                                      |
|--------------------------|---------------------------------------------|
| Habib Al-Qodri           | [HabibAlQodri](https://github.com/HabibAlQodri) |
| Yohanes Adi Prasetya     | [Feuriee](https://github.com/Feuriee)      |
| Agyl Wendi Pratama       | [likeazwee](https://github.com/likeazwee)  |

---


## 🔍 Fitur Utama

- Prediksi kecepatan kendaraan berdasarkan jam dan hari
- Analisis performa model AI (MAE dan R²)
- Perbandingan 4 model AI: Linear Regression, Decision Tree, Random Forest, dan Neural Network (MLP)
- Rekomendasi kondisi lalu lintas (lancar, sedang, macet)
- Visualisasi peta interaktif dengan jalur rute dan titik kemacetan
- Dukungan input lokasi menggunakan nama tempat (geocoding)

---

## 🧠 Model AI yang Digunakan

- **Linear Regression**
- **Decision Tree Regressor**
- **Random Forest Regressor**
- **MLP Neural Network**

Model dilatih menggunakan data simulasi yang mencakup:
- Jam dan hari
- Hari libur / akhir pekan
- Waktu sibuk (rush hour)

---

## 🗺️ Alur Sistem

1. **Input Pengguna**
   - Wilayah (contoh: `Bengkulu, Indonesia`)
   - Lokasi awal dan tujuan (nama tempat)
   - Jam dan hari
   - Model AI yang dipilih atau semua model

2. **Simulasi dan Pelatihan Data**
   - Data lalu lintas disimulasikan berdasarkan aturan probabilistik dan waktu
   - Setiap model dilatih ulang pada setiap permintaan

3. **Prediksi Kecepatan**
   - Model memprediksi kecepatan rata-rata kendaraan (dalam km/jam)
   - Status diklasifikasikan:
     - `> 30 km/jam` → **Lancar**
     - `15 – 30 km/jam` → **Sedang**
     - `< 15 km/jam` → **Macet**

4. **Visualisasi Peta**
   - Rute dari lokasi awal ke tujuan dihitung menggunakan OSMnx dan NetworkX
   - Titik kemacetan ditandai pada posisi tengah rute jika prediksi buruk

5. **Notifikasi Cerdas**
   - Sistem memberikan rekomendasi tindakan berdasarkan hasil prediksi

---

## 🛠️ Teknologi yang Digunakan

- **Python (Flask)** – Backend dan Web Server
- **scikit-learn** – Model AI/ML
- **OSMnx & NetworkX** – Jalur jalan dan rute optimal
- **Folium** – Visualisasi peta dan rute
- **HTML/CSS (render_template_string)** – Antarmuka web responsif

---

## 📦 Cara Menjalankan

1. **Install Dependensi**

```bash
pip install flask scikit-learn pandas numpy osmnx networkx folium
```

2. **Jalankan Aplikasi**

```bash
python main.py
```

3. **Akses via Browser**

Buka: [http://localhost:5000](http://localhost:5000)

---

## 📱 API Endpoint

### `POST /api/predict`

**Request Body Contoh:**

```json
{
  "jam": 17,
  "hari": 5
}
```

**Response:**

```json
{
  "success": true,
  "predictions": {
    "Linear Regression": 22.45,
    "Decision Tree": 18.32
  },
  "timestamp": "2025-06-08T12:00:00"
}
```

---

## 🎯 Tujuan Proyek

- Menyediakan sistem pendukung keputusan untuk pengelolaan lalu lintas
- Mengurangi potensi kemacetan secara preventif
- Memberikan informasi dan rute terbaik untuk pengguna
