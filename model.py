import time
import joblib
import pandas as pd
import numpy as np
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from realtime_data.config import astra_client_id, astra_client_secret, astra_database_id, astra_app_name

# Initialize connection to Cassandra
def connect_to_cassandra():
    cloud_config = {
        'secure_connect_bundle': 'secure-connect-cassandra-db.zip'  # Path to your secure connect bundle
    }
    cluster = Cluster(cloud=cloud_config, auth_provider=PlainTextAuthProvider(astra_client_id, astra_client_secret))
    session = cluster.connect()
    session.set_keyspace("system1")
    return session

# Cassandra session
session = connect_to_cassandra()

# def fetch_numeric_features():
#     query = """
#         SELECT speed, rpm, throttle, g_force, acceleration, brake_pressure, steering_angle
#         FROM realtime_data
#         LIMIT 1
#     """
#     rows = session.execute(query)
#     latest_row = rows.one()

#     if latest_row:
#         # Extract numeric features
#         numeric_data = {
#             "speed": latest_row.speed,
#             "rpm": latest_row.rpm,
#             "throttle": latest_row.throttle,
#             "g_force": latest_row.g_force,
#             "acceleration": latest_row.acceleration,
#             "brake_pressure": latest_row.brake_pressure,
#             "steering_angle": latest_row.steering_angle
#         }
#         return numeric_data
#     else:
#         return None

def fetch_numeric_features():
    numeric_data = {
        "speed": 116.38918225943932,
        "rpm": 3960.53762558927,
        "throttle": 0.06265320345535452,
        "g_force": 1.438163645218391,
        "acceleration": -1.0808943705609098,
        "brake_pressure": 0.7066041289942178,
        "steering_angle": 28.60398662095716
    }
    return numeric_data


# Load the saved scaler and models using joblib
def load_models_and_scaler():
    scaler = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/scaler.pkl')  # Path to your scaler file
    accident_model = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/accident_severity_model.pkl')  # Path to your accident severity model
    behavior_model = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/driver_behavior_model.pkl')  # Path to your driver behavior model
    return scaler, accident_model, behavior_model

# Main workflow to fetch, preprocess, and predict
def main():
    # Fetch the latest numeric data from the database
    latest_numeric_data = fetch_numeric_features()
    
    if latest_numeric_data:
        print("Fetched data: ", latest_numeric_data)

        # Load the scaler and models
        scaler, accident_model, behavior_model = load_models_and_scaler()

        # Convert the fetched data into a DataFrame
        new_data = pd.DataFrame([latest_numeric_data])

        # Preprocess the new data using the saved scaler
        new_data_scaled = scaler.transform(new_data)
        print("Preprocessed data: ", new_data_scaled)

        # Predict accident severity using the preprocessed data
        accident_severity = accident_model.predict(new_data_scaled)
        print(f"Predicted Accident Severity: {accident_severity}")

        # Predict driver behavior using the preprocessed data
        driver_behavior = behavior_model.predict(new_data_scaled)
        print(f"Predicted Driver Behavior: {driver_behavior}")

    else:
        print("No data available.")

# Run the main workflow
if __name__ == "__main__":
    while True:
        main()
        print("\nWaiting for new data...\n")
        time.sleep(5)