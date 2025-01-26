import pandas as pd
import numpy as np

# Set a random seed for reproducibility
np.random.seed(42)

# Number of samples to generate
num_samples = 1000

# Simulate synthetic data
data = {
    'speed': np.random.uniform(0, 120, num_samples),  # Speed in km/h
    'rpm': np.random.uniform(800, 4000, num_samples),  # RPM
    'throttle': np.random.uniform(0, 1, num_samples),  # Throttle (0 to 1)
    'g_force': np.random.uniform(0, 5, num_samples),  # G-force (0 to 5)
    'acceleration': np.random.uniform(-5, 5, num_samples),  # Acceleration (m/s²)
    'brake_pressure': np.random.uniform(0, 1, num_samples),  # Brake Pressure (0 to 1)
    'steering_angle': np.random.uniform(-45, 45, num_samples),  # Steering angle in degrees
}

# Generate accident severity labels based on certain conditions

def label_accident(row):
    # Conditions for Major Accident (high speed, high G-force, hard braking)
    if row[0] > 90 and row[3] > 4 and row[5] > 0.7:
        return 2  # Major Accident
    
    # Conditions for Minor Accident (medium speed, moderate braking, sharp turn)
    elif (row[0] > 50 and row[0] <= 90 and row[3] > 2) or (row[5] > 0.5 and row[4] < -2):
        return 1  # Minor Accident
    
    # Conditions for No Accident (normal driving behavior)
    else:
        return 0  # No Accident

# Generate driver behavior labels based on driving patterns

def label_driver_behavior(row):
    # Aggressive Driving (high speed, hard acceleration, high throttle, sharp turns)
    if row[0] > 90 and row[4] > 3 and row[2] > 0.8 and abs(row[6]) > 30:
        return 1  # Aggressive Driver
    
    # Careless Driving (speeding, erratic braking, low throttle, inconsistent acceleration)
    elif row[0] > 80 and row[5] > 0.7 and row[2] < 0.2:
        return 2  # Careless Driver
    
    # Normal Driving (moderate speed, smooth acceleration, appropriate throttle)
    else:
        return 0  # Normal Driver

# Convert the data dictionary to a numpy array for easier processing
data_array = np.array(list(zip(*data.values())))

# Apply the accident labeling function to each row
accident_severity = np.apply_along_axis(label_accident, 1, data_array)

# Apply the driver behavior labeling function to each row
driver_behavior = np.apply_along_axis(label_driver_behavior, 1, data_array)

# Add the labels to the dataset
data['accident_severity'] = accident_severity
data['driver_behavior'] = driver_behavior

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('synthetic_driving_data_with_behavior_and_accident.csv', index=False)

print("Synthetic dataset with accident and driver behavior labels generated and saved to 'synthetic_driving_data_with_behavior_and_accident.csv'")
