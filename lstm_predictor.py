import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from keras.models import Sequential
from keras.layers import LSTM, Dense

# 1. Simulasi data kecepatan
np.random.seed(42)
base_speed = 40 + np.random.normal(0, 5, 288)  # 288 = 24 jam * 60 / 5 menit
rush_hours = list(range(70, 100)) + list(range(210, 240))
for i in rush_hours:
    base_speed[i] -= np.random.uniform(10, 25)

speed_series = np.clip(base_speed, 0, 80)
df = pd.DataFrame({'speed': speed_series})

# Plot data kecepatan
plt.figure(figsize=(10, 4))
df.plot(title='Kecepatan Kendaraan per 5 Menit')
plt.xlabel('Interval ke-5 menit')
plt.ylabel('Kecepatan (km/jam)')
plt.grid(True)
plt.show()

# 2. Normalisasi & Preprocessing
scaler = MinMaxScaler()
scaled_speed = scaler.fit_transform(df[['speed']])

def create_sequences(data, time_steps=10):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:i + time_steps])
        y.append(data[i + time_steps])
    return np.array(X), np.array(y)

time_steps = 10
X, y = create_sequences(scaled_speed, time_steps)

# 3. Model LSTM
model = Sequential()
model.add(LSTM(64, activation='relu', input_shape=(X.shape[1], 1)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

# Latih model
history = model.fit(X, y, epochs=20, batch_size=16, validation_split=0.2)

# 4. Prediksi
predicted = model.predict(X)
predicted_speed = scaler.inverse_transform(predicted)

# 5. Visualisasi
plt.figure(figsize=(12, 5))
plt.plot(df['speed'][time_steps:].values, label='Aktual')
plt.plot(predicted_speed, label='Prediksi', alpha=0.7)
plt.title('Prediksi Kecepatan Kendaraan dengan LSTM')
plt.xlabel('Interval ke-5 menit')
plt.ylabel('Kecepatan (km/jam)')
plt.legend()
plt.grid(True)
plt.show()

# 6. Evaluasi
actual_speed = df['speed'][time_steps:].values
mae = mean_absolute_error(actual_speed, predicted_speed)
rmse = np.sqrt(mean_squared_error(actual_speed, predicted_speed))

print(f'MAE: {mae:.2f} km/jam')
print(f'RMSE: {rmse:.2f} km/jam')
