import json
import os
import numpy as np

def run_weather_model():
    
    # User Inputs
    city = input("Enter City Name (e.g., bengaluru): ").lower().strip()
    target_date = input("Enter Date (MM-DD, e.g., 06-15): ").strip()
    target_time = input("Enter Hour (00-23, e.g., 14): ").strip()

    # File path - ensures it reads from your local 'city' folder
    file_path = f"city/{city}.json"

    if not os.path.exists(file_path):
        print(f"Error: {city}.json not found in 'city' folder.")
        return

    with open(file_path, 'r') as f:
        # Load the local data
        data = json.load(f)[0]

    # Parameters to extract:
    # T2M: Temp, RH2M: Humidity, PRECTOTCORR: Rain Amount, WS2M: Wind Speed
    params = {
        'T2M': 'Temperature (°C)',
        'RH2M': 'Humidity (%)',
        'PRECTOTCORR': 'Rain Amount (mm/hr)',
        'WS2M': 'Wind Speed (m/s)'
    }
    
    years = ['2020', '2021', '2022', '2023', '2024']
    mmddhh = target_date.replace("-", "") + target_time
    
    print(f"\n--- Prediction for {city.upper()} on {target_date} at {target_time}:00 ---")

    for key, label in params.items():
        values = []
        for yr in years:
            # Construct key like '2020061514'
            full_key = yr + mmddhh
            val = data.get(f"data_{yr}", {}).get('properties', {}).get('parameter', {}).get(key, {}).get(full_key)
            
            if val is not None and val != -999.0:
                values.append(val)

        if values:
            avg = np.mean(values)
            std = np.std(values)
            
            # Special Logic for Rain Percentage
            if key == 'PRECTOTCORR':
                # Count years where rain was > 0.1mm
                years_with_rain = sum(1 for v in values if v > 0.1)
                rain_chance = (years_with_rain / len(years)) * 100
                print(f"Rain Probability: {rain_chance}%")
                print(f"Expected Rain Amount: {round(avg, 2)} mm (±{round(std, 2)})")
            else:
                print(f"{label}: {round(avg, 2)} (±{round(std, 2)})")
        else:
            print(f"{label}: No historical data found for this time.")

if __name__ == "__main__":
    run_weather_model()