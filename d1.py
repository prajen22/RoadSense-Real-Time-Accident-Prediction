import streamlit as st
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import bcrypt
from realtime_data.config import astra_client_id, astra_client_secret, astra_database_id, astra_app_name
from opencage.geocoder import OpenCageGeocode
import time
from datetime import datetime
import numpy as np
import joblib
import pandas as pd
import threading
from streamlit_autorefresh import st_autorefresh


from back import BackgroundCSSGenerator
import random as rd

st.set_page_config(page_title="UYIR", layout="wide", initial_sidebar_state="collapsed")



# OpenCage API Key (Replace with your own key)
OPENCAGE_API_KEY = "5dc1ade772ba45e8838e85e824291718"
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

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

# Login Functionality
def login():
    if st.session_state.get("logged_in", False):
        st.info("You are already logged in!")
        return

    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        try:
            result = session.execute("SELECT password FROM user WHERE username = %s", (username,))
            record = result.one()
            if record and bcrypt.checkpw(password.encode('utf-8'), record.password.encode('utf-8')):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()  # Reload the page after login
            else:
                st.error("Invalid username or password.")
        except Exception as e:
            st.error(f"Error: {e}")


# Create User Table if not exists
def create_user_table():
    session.execute("""
        CREATE TABLE IF NOT EXISTS user (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)

# Sign-Up Functionality
def sign_up():
    st.title("Sign Up")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    
    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            try:
                session.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, hashed_password))
                st.success("Account created successfully! Please log in.")
            except Exception as e:
                st.error(f"Error: {e}")

# Fetch Latest Data
def fetch_latest_data():
    query = """
        SELECT vehicle_id, speed, rpm, throttle, g_force, acceleration, brake_pressure, 
               steering_angle, latitude, longitude, timestamp
        FROM realtime_data
        LIMIT 1
    """
    rows = session.execute(query)
    latest_row = rows.one()
    return {col: getattr(latest_row, col) for col in latest_row._fields} if latest_row else None

# Get Address from Geocoder
def get_address(latitude, longitude):
    try:
        results = geocoder.reverse_geocode(latitude, longitude)
        if results:
            return results[0]['formatted']
    except Exception as e:
        st.error(f"Error fetching address: {e}")
    return "Unknown Location"

import streamlit as st
import time

def inject_css():
    st.markdown("""
        <style>
            /* Link to Font Awesome for icons */
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
            
            /* Center and style the header and description */
            .center-header {
                text-align: center;
                font-weight: bold;
                font-size: 32px;
                color: #1e88e5;
                margin-bottom: 20px;
            }
            .center-description {
                text-align: center;
                font-weight: bold;
                font-size: 18px;
                color: #555;
                margin-bottom: 40px;
            }

            /* Styling for the container */
            .container-box {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                margin-top: 20px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .container-box:hover {
                transform: scale(1.02);
                box-shadow: 0 12px 28px rgba(102, 51, 153, 0.4);
            }

            /* Card styling */
            .metric {
                background: linear-gradient(135deg, #f0f8ff, #e8f5e9);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
                transition: transform 0.3s ease, box-shadow 0.3s ease, opacity 0.3s ease;
                height: 100%;
                margin: 10px;
                position: relative;
            }
            .metric:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(30, 144, 255, 0.4);
                background: linear-gradient(135deg, #d7cce6, #b2ebf2);
            }
            .metric .icon {
                font-size: 50px;
                color: #1e88e5;
                margin-bottom: 15px;
                transition: transform 0.3s ease, color 0.3s ease;
            }
            .metric:hover .icon {
                transform: rotate(15deg);
                color: #ff6347;  /* Change icon color on hover */
            }
            .metric h2 {
                font-size: 26px;
                color: #1e88e5;
                margin: 0;
                animation: fadeIn 1s ease;
            }
            .metric p {
                font-size: 18px;
                color: #555;
                margin: 5px 0 0;
            }

            /* Animation keyframes */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }

            /* Divider styling */
            .custom-divider {
                height: 2px;
                background: linear-gradient(90deg, rgba(128, 0, 128, 0.3), rgba(0, 191, 255, 0.3));
                border: none;
                margin: 20px 0;
            }
        </style>
    """, unsafe_allow_html=True)

# Map metrics to their corresponding icons
def get_metric_icon(metric_name):
    icon_map = {
    "Speed (km/h)": "fas fa-tachometer-alt",  # Simpler icon for speed
    "RPM": "fas fa-cogs",
    "Throttle": "fas fa-gas-pump",
    "G-Force": "fas fa-fist-raised",
    "Acceleration (m/s²)": "fas fa-running",
    "Brake Pressure": "fas fa-bicycle",
    "Steering Angle (°)": "fas fa-road",  # Simpler icon for steering
    "Location": "fas fa-map-marker-alt"
}

    return icon_map.get(metric_name, "fas fa-question-circle")

# Display Metrics in a Grid (3 Cards per Row with Enhanced UI)
def display_metrics_in_grid(data):
    latitude = data.get('latitude', None)
    longitude = data.get('longitude', None)
    address = get_address(latitude, longitude) if latitude and longitude else "Unknown Location"

    metrics = {
        "Speed (km/h)": data.get('speed', 'N/A'),
        "RPM": data.get('rpm', 'N/A'),
        "Throttle": data.get('throttle', 'N/A'),
        "G-Force": data.get('g_force', 'N/A'),
        "Acceleration (m/s²)": data.get('acceleration', 'N/A'),
        "Brake Pressure": data.get('brake_pressure', 'N/A'),
        "Steering Angle (°)": data.get('steering_angle', 'N/A'),
        "Location": address,
    }

    metric_items = list(metrics.items())
    num_metrics = len(metric_items)
    num_cols = 3

    # Start a container for the entire grid
    with st.container():
        # Loop through metrics and display 3 cards per row
        for i in range(0, num_metrics, num_cols):
            cols = st.columns(num_cols)  # Create 3 equal-width columns
            for j, col in enumerate(cols):
                if i + j < num_metrics:
                    key, value = metric_items[i + j]
                    with col:
                        icon = get_metric_icon(key)
                        st.markdown(
                            f"""
                            <div class="metric">
                                <i class="{icon} icon"></i>
                                <h2>{value}</h2>
                                <p>{key}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            # Add a styled divider under each row
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# Real-Time Metrics Tab







def fetch_numeric_features():
    query = """
        SELECT speed, rpm, throttle, g_force, acceleration, brake_pressure, steering_angle
        FROM realtime_data
        LIMIT 1
    """
    rows = session.execute(query)
    latest_row = rows.one()

    if latest_row:
        # Extract numeric features
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
    else:
        return None
    
def load_models_and_scaler():
    scaler = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/scaler.pkl')  # Path to your scaler file
    accident_model = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/accident_severity_model.pkl')  # Path to your accident severity model
    behavior_model = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/driver_behavior_model.pkl')  # Path to your driver behavior model
    return scaler, accident_model, behavior_model
        

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

def main_app():
    st.title("UYIR Application")

    # Define tabs
    tab1, tab2 = st.tabs(["Real-Time Metrics", "Prediction Results"])

    with st.sidebar:
        st.header("Authentication")
        auth_option = st.radio("Choose an option", ["Login", "Sign Up"])
        if auth_option == "Login":
            login()
        elif auth_option == "Sign Up":
            sign_up()

    # Shared state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = True

    # Start background threads for Tab 1 and Tab 2
    if "tab1_thread" not in st.session_state:
        st.session_state["tab1_thread"] = threading.Thread(target=run_tab1, daemon=True)
        st.session_state["tab1_thread"].start()

    if "tab2_thread" not in st.session_state:
        st.session_state["tab2_thread"] = threading.Thread(target=run_tab2, daemon=True)
        st.session_state["tab2_thread"].start()

# Continuous Tab 1 Functionality
def run_tab1():
    while True:
        if st.session_state.get("logged_in", False):
            with st.tabs(["Real-Time Metrics", "Prediction Results"])[0]:
                st.markdown('<h1 class="center-header">Real-Time Metrics and Predictions</h1>', unsafe_allow_html=True)
                st.markdown('<p class="center-description">Displaying real-time data dynamically along with accident risk and driver behavior predictions.</p>', unsafe_allow_html=True)

                # Placeholders for dynamic content
                metrics_placeholder = st.empty()
                prediction_placeholder = st.empty()

                # Fetch and display data
                data = fetch_latest_data()
                if data:
                    with metrics_placeholder.container():
                        display_metrics_in_grid(data)

                    # Simulate predictions
                    with prediction_placeholder.container():
                        st.write("### Predictions")
                        st.write("Accident Risk: Moderate")
                        st.write("Driving Behavior: Normal")
                time.sleep(5)  # Refresh every 5 seconds

# Continuous Tab 2 Functionality
def run_tab2():
    while True:
        if st.session_state.get("logged_in", False):
            with st.tabs(["Real-Time Metrics", "Prediction Results"])[1]:
                st.title("Prediction Results")

                # Fetch and display predictions
                numeric_features = fetch_numeric_features()
                if numeric_features:
                    scaler, accident_model, behavior_model = load_models_and_scaler()

                    # Scale the numeric features
                    numeric_data_array = np.array(list(numeric_features.values())).reshape(1, -1)
                    scaled_data = scaler.fit_transform(numeric_data_array)  # Use fit_transform for mock

                    # Mock predictions
                    accident_prediction = 1  # Replace with accident_model.predict(scaled_data)[0]
                    behavior_prediction = 0  # Replace with behavior_model.predict(scaled_data)[0]

                    accident_labels = {
                        0: "No Accident Risk",
                        1: "Moderate Accident Risk",
                        2: "High Accident Risk"
                    }
                    behavior_labels = {
                        0: "Normal Driving Behavior",
                        1: "Reckless Driving",
                        2: "Aggressive Driving"
                    }

                    st.write("### Accident Risk Prediction")
                    st.write(f"Prediction: {accident_prediction} - **{accident_labels[accident_prediction]}**")

                    st.write("### Driving Behavior Prediction")
                    st.write(f"Prediction: {behavior_prediction} - **{behavior_labels[behavior_prediction]}**")
                else:
                    st.error("No data available for predictions.")
                time.sleep(5)  # Refresh every 5 seconds

# Run Application
if __name__ == "__main__":
    main_app()