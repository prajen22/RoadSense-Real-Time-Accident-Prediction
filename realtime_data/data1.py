import numpy as np
import random
import time
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import uuid
from config import astra_client_id, astra_client_secret, astra_database_id, astra_app_name



# Initialize Cassandra connection
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

# Create Cassandra table
def create_realtime_data_table():
    """
    Creates the realtime_data table with a proper schema in Cassandra.
    """
    session.execute("""
        CREATE TABLE IF NOT EXISTS realtime_data (
            vehicle_id UUID,
            timestamp TIMESTAMP,
            speed FLOAT,
            rpm FLOAT,
            throttle FLOAT,
            g_force FLOAT,
            acceleration FLOAT,
            brake_pressure FLOAT,
            steering_angle FLOAT,
            latitude FLOAT,
            longitude FLOAT,
            PRIMARY KEY (vehicle_id, timestamp)
        ) WITH CLUSTERING ORDER BY (timestamp DESC)
    """)

# Generate random data using the specified ranges
def generate_data(vehicle_id):
    return {
        'vehicle_id': vehicle_id,
        'timestamp': datetime.now(),
        'speed': float(np.random.uniform(0, 120)),            # Speed in km/h
        'rpm': float(np.random.uniform(800, 4000)),           # RPM
        'throttle': float(np.random.uniform(0, 1)),           # Throttle (0 to 1)
        'g_force': float(np.random.uniform(0, 5)),            # G-force (0 to 5)
        'acceleration': float(np.random.uniform(-5, 5)),      # Acceleration (m/s²)
        'brake_pressure': float(np.random.uniform(0, 1)),     # Brake Pressure (0 to 1)
        'steering_angle': float(np.random.uniform(-45, 45)),  # Steering angle in degrees
        'latitude': float(np.random.uniform(-90, 90)),        # Latitude
        'longitude': float(np.random.uniform(-180, 180)),     # Longitude
    }

# Insert data into Cassandra
def insert_data(data):
    query = """
        INSERT INTO realtime_data (
            vehicle_id, timestamp, speed, rpm, throttle, g_force, acceleration, 
            brake_pressure, steering_angle, latitude, longitude
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (
        data["vehicle_id"],
        data["timestamp"],
        data["speed"],
        data["rpm"],
        data["throttle"],
        data["g_force"],
        data["acceleration"],
        data["brake_pressure"],
        data["steering_angle"],
        data["latitude"],
        data["longitude"],
    ))

# Main function to generate and insert real-time data
def main():
    create_realtime_data_table()
    vehicle_id = uuid.uuid4()  # Assign a unique vehicle ID
    print(f"Generating real-time data for vehicle ID: {vehicle_id}")

    try:
        while True:
            data = generate_data(vehicle_id)
            insert_data(data)
            print(f"Inserted data: {data}")
            time.sleep(1)  # Simulate real-time data every second
    except KeyboardInterrupt:
        print("\n Stopped data generation. \n ")
    except Exception as e:
        print(f"Error: {e}")

# Run the script
if __name__ == "__main__":
    main()
