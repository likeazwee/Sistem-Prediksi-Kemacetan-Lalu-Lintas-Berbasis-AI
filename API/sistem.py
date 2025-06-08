import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

class TrafficPredictionSystem:
    def __init__(self):
        self.models = {
            'Linear Regression': LinearRegression(),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100,50), max_iter=1000, random_state=42)
        }
        self.trained_models = {}
        self.feature_cols = ['jam', 'hari', 'is_weekend', 'rush_hour']

    def train_models(self, data):
        """Train all ML models with given data"""
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
        """Predict traffic speed for given time and day"""
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