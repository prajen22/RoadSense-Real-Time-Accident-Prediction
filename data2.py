import numpy as np
import random
import time
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import uuid
from config import astra_client_id, astra_client_secret

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

# Create Cassandra table with `reverse_timestamp`
def create_realtime_data_table():
    """
    Creates the realtime_data table with reverse_timestamp for ordering and reward table.
    """
    session.execute("""
        CREATE TABLE IF NOT EXISTS realtime_data (
            vehicle_id UUID,
            reverse_timestamp BIGINT,
            sno BIGINT,
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
            PRIMARY KEY (vehicle_id, reverse_timestamp)
        ) WITH CLUSTERING ORDER BY (reverse_timestamp ASC);
    """)
    

# Generate random data
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
        'latitude': float(np.random.uniform(6.0, 37.0)),        # Latitude (India region)
        'longitude': float(np.random.uniform(68.0, 97.0)),      # Longitude (India region)

    }

# Generate reverse timestamp
def generate_reverse_timestamp():
    """
    Generates a reverse timestamp by negating the current timestamp in milliseconds.
    """
    return -1 * int(time.time() * 1000)

# Insert data into Cassandra
def insert_data(data, reverse_timestamp, sno):
    query = """
        INSERT INTO realtime_data (
            vehicle_id, reverse_timestamp, sno, timestamp, speed, rpm, throttle, g_force, 
            acceleration, brake_pressure, steering_angle, latitude, longitude
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (
        data["vehicle_id"],
        reverse_timestamp,
        sno,
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
def truncate():
    session.execute("TRUNCATE TABLE realtime_data")

# Main function to generate and insert real-time data
def main():
    create_realtime_data_table()
    vehicle_id = uuid.uuid4()  # Assign a unique vehicle ID
    truncate()
    print(f"Generating real-time data for vehicle ID: {vehicle_id}")

    sno = 1  # Initial sno value
    try:
        while True:
            
            data = generate_data(vehicle_id)
            reverse_timestamp = generate_reverse_timestamp()
            insert_data(data, reverse_timestamp, sno)
            print(f"Inserted data with sno {sno}: {data}")
            sno += 1
            time.sleep(5)  # Simulate real-time data every second
    except KeyboardInterrupt:
        print("\nStopped data generation.\n")
    except Exception as e:
        print(f"Error: {e}")

# Run the script
if __name__ == "__main__":
    main()
