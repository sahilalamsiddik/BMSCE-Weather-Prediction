import json
import os
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Time Series Prediction Function
def time_series_forecast(values):
    if len(values) < 2:
        return values[-1] if values else None

    # Convert to numpy array
    y = np.array(values)
    x = np.arange(len(y))  # [0,1,2,3,4]

    # Linear regression (trend)
    slope, intercept = np.polyfit(x, y, 1)

    # Predict next value
    next_x = len(y)
    prediction = slope * next_x + intercept

    # Moving average (last 3 values smoothing)
    moving_avg = np.mean(y[-3:])

    # Final prediction = blend of both
    final_prediction = (prediction + moving_avg) / 2

    return float(final_prediction)


@app.get("/predict")
def run_weather_model(city: str, date: str, time: str):

    city = city.lower().strip()
    target_date = date  # MM-DD
    target_time = time  # HH

    file_path = f"city/{city}.json"

    if not os.path.exists(file_path):
        return {"error": f"{city}.json not found"}

    with open(file_path, 'r') as f:
        data = json.load(f)[0]

    params = {
        'T2M': 'Temperature',
        'RH2M': 'Humidity',
        'PRECTOTCORR': 'Rain',
        'WS2M': 'Wind'
    }

    years = ['2020', '2021', '2022', '2023', '2024']
    mmddhh = target_date.replace("-", "") + target_time

    result = {}

    for key, label in params.items():
        values = []

        for yr in years:
            full_key = yr + mmddhh

            val = data.get(f"data_{yr}", {}).get('properties', {}).get('parameter', {}).get(key, {}).get(full_key)

            if val is not None and val != -999.0:
                values.append(val)

        if values:
            # 🔥 Time Series Prediction
            prediction = time_series_forecast(values)

            if key == 'PRECTOTCORR':
                years_with_rain = sum(1 for v in values if v > 0.1)
                rain_chance = (years_with_rain / len(values)) * 100

                result["rain_probability"] = round(rain_chance, 2)
                result["rain_amount"] = round(prediction, 2)

            else:
                result[label.lower()] = round(prediction, 2)

        else:
            result[label.lower()] = None

    return result