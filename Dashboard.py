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
from twilio.rest import Client
import time
import pandas as pd




from back import BackgroundCSSGenerator
import random as rd

st.set_page_config(page_title="UYIR", layout="wide", initial_sidebar_state="collapsed")


# Twilio Credentials (Make sure to replace these with your actual credentials)
TWILIO_ACCOUNT_SID = 'AC5ef25d3c6123ab87fa7eb9fd5d4e48cf'
TWILIO_AUTH_TOKEN = 'c533139e651574e9b40afbb4e3385ef5'
TWILIO_PHONE_NUMBER = '+17178336953'



# OpenCage API Key (Replace with your own key)
OPENCAGE_API_KEY = "5dc1ade772ba45e8838e85e824291718"
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)


# Function to send SMS via Twilio
def send_sms(to_phone_number):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.calls.create(
        url='http://demo.twilio.com/docs/voice.xml',
        from_=TWILIO_PHONE_NUMBER,
        to=to_phone_number
    )
    print(f"called sent to {to_phone_number}")

# Modify your prediction logic to include SMS notification
def check_and_send_sms_for_accident(latest_numeric_data):
    scaler, accident_model, behavior_model = load_models_and_scaler()

    # Predict accident and behavior
    new_data = pd.DataFrame([latest_numeric_data])
    new_data_scaled = scaler.transform(new_data)

    accident_prediction = accident_model.predict(new_data_scaled)[0]
    behavior_prediction = behavior_model.predict(new_data_scaled)[0]

    # If the accident risk is moderate or high (1 or 2), send SMS
    if accident_prediction in [1, 2]:  # Moderate or High Accident Risk
        message = f"ALERT: Accident risk detected! Severity: {accident_prediction} (Moderate or High)"
        phone_numbers = '+919500716115'
        
        send_sms(phone_numbers)
    
    else:
        print("there is no accident !")
    
    return accident_prediction, behavior_prediction

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

# Load Models and Scaler for Predictions
def load_models_and_scaler():
    scaler = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/scaler.pkl')  # Path to your scaler file
    accident_model = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/accident_severity_model.pkl')  # Path to your accident severity model
    behavior_model = joblib.load('C:/Users/praje/OneDrive/AppData/Desktop/project/UYIR/model_and_scaler_file/driver_behavior_model.pkl')  # Path to your driver behavior model
    return scaler, accident_model, behavior_model

# Function to display predictions
def display_predictions(accident_prediction, behavior_prediction):
    # Define labels for accident prediction
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

    # Display predictions in cards
    st.markdown("<div class='container-box'>", unsafe_allow_html=True)
    st.markdown("<h2>Prediction Results</h2>", unsafe_allow_html=True)
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="metric">
            <i class="fas fa-exclamation-triangle icon"></i>
            <h2>{accident_labels[accident_prediction]}</h2>
            <p>Accident Risk</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="metric">
            <i class="fas fa-car icon"></i>
            <h2>{behavior_labels[behavior_prediction]}</h2>
            <p>Driver Behavior</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


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
        "speed": latest_row.speed,
            "rpm": latest_row.rpm,
            "throttle": latest_row.throttle,
            "g_force": latest_row.g_force,
            "acceleration": latest_row.acceleration,
            "brake_pressure": latest_row.brake_pressure,
            "steering_angle": latest_row.steering_angle
        }
        return numeric_data
    else:
        return None

# Real-Time Data Tab
def tabs(username):
    st.title(f"Welcome, {username}")
    tab1 = st.tabs(["Real-Time Metrics and Predictions"])[0]
    inject_css()

    with tab1:
        # Use the custom classes to center and style header and description
        st.markdown('<h1 class="center-header">Real-Time Metrics and Predictions</h1>', unsafe_allow_html=True)
        st.markdown('<p class="center-description">Displaying real-time data dynamically along with accident risk and driver behavior predictions.</p>', unsafe_allow_html=True)

        # Placeholder for dynamic content
        metrics_placeholder = st.empty()
        prediction_placeholder = st.empty()

        while True:
            # Fetch latest data
            data = fetch_latest_data()  # Replace with actual data fetching logic
            if data:
                with metrics_placeholder.container():
                    display_metrics_in_grid(data)
                
                # Fetch and display predictions
                latest_numeric_data = fetch_numeric_features()

                if latest_numeric_data:
                    # scaler, accident_model, behavior_model = load_models_and_scaler()
                    # new_data = pd.DataFrame([latest_numeric_data])
                    # new_data_scaled = scaler.transform(new_data)

                    # accident_prediction = accident_model.predict(new_data_scaled)[0]
                    # behavior_prediction = behavior_model.predict(new_data_scaled)[0]
                    with prediction_placeholder.container():


                        accident_prediction, behavior_prediction = check_and_send_sms_for_accident(latest_numeric_data)
                        display_predictions(accident_prediction, behavior_prediction)
                        
            time.sleep(5)  # Refresh every 5 seconds



    

    







# Main Function
def main():
    # Ensure the user table exists (idempotent operation)
    create_user_table()

    # Initialize session state variables if not already set
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""

    # Check login status
    if st.session_state["logged_in"]:
        # Render the main tabs interface
        try:
            tabs(st.session_state["username"])
            
        except Exception as e:
            st.error(f"An error occurred while loading the main interface: {e}")
    else:
        # Show login or sign-up options in the sidebar
        choice = st.sidebar.selectbox("Select Action", ["Login", "Sign Up"])
        if choice == "Sign Up":
            try:
                sign_up()
            except Exception as e:
                st.error(f"An error occurred during sign-up: {e}")
        elif choice == "Login":
            try:
                login()
            except Exception as e:
                st.error(f"An error occurred during login: {e}")

# Entry point
if __name__ == "__main__":
    main()
    

