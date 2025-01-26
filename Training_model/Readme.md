

# README: Training Models for Accident Severity and Driver Behavior Classification

This repository contains scripts to train machine learning models for:  
1. **Accident Severity Prediction**: Classifies the severity of accidents (e.g., No Accident, Minor Accident, Major Accident).  
2. **Driver Behavior Classification**: Categorizes driver behavior (e.g., Normal, Aggressive, Careless).  

Both models use a synthetic dataset (`synthetic_driving_dataset.csv`) for training and testing.  

---

## Prerequisites  

### 1. Install Required Libraries  
Ensure you have the following Python libraries installed:  
```bash  
pip install pandas scikit-learn matplotlib seaborn joblib  
```  

### 2. Dataset  
The dataset file `synthetic_driving_dataset.csv` should be placed in the root directory. It must include:  
- **Features**: `speed`, `rpm`, `throttle`, `g_force`, `acceleration`, `brake_pressure`, `steering_angle`.  
- **Labels**:  
  - `accident_severity`: Severity of the accident.  
  - `driver_behavior`: Type of driver behavior.  

---

## Training the Models  

### 1. Accident Severity Model  
#### Script: `accident_severity_model.py`  

This script trains a **Random Forest Classifier** to predict accident severity.  

#### Workflow:  
1. Preprocesses the dataset using **StandardScaler** to scale feature values.  
2. Splits the scaled data into training and testing sets.  
3. Trains a Random Forest model on the training data.  
4. Saves the trained model and scaler for future use:  
   - `accident_severity_model.pkl`: The trained accident severity model.  
   - `scaler.pkl`: The scaler used for preprocessing.  

#### Command to Run:  
```bash  
python accident_severity_model.py  
```  

#### Output:  
- **Generated Files**:  
  - `accident_severity_model.pkl`  
  - `scaler.pkl`  

---

### 2. Driver Behavior Model  
#### Script: `driver_behavior_model.py`  

This script trains a **Random Forest Classifier** to classify driver behavior.  

#### Workflow:  
1. Loads the `scaler.pkl` file to preprocess the dataset.  
2. Splits the scaled data into training and testing sets.  
3. Trains a Random Forest model on the training data.  
4. Saves the trained model:  
   - `driver_behavior_model.pkl`: The trained driver behavior classification model.  

#### Command to Run:  
```bash  
python driver_behavior_model.py  
```  

#### Output:  
- **Generated File**:  
  - `driver_behavior_model.pkl`  

---

## Files Overview  

### **Scripts**  
- `accident_severity_model.py`: Trains and saves the accident severity model.  
- `driver_behavior_model.py`: Trains and saves the driver behavior classification model.  

### **Generated Files**  
- `accident_severity_model.pkl`: Model for accident severity prediction.  
- `driver_behavior_model.pkl`: Model for driver behavior classification.  
- `scaler.pkl`: Scaler used to preprocess data for both models.  

---

## Notes  

- Ensure the `scaler.pkl` file is used consistently for preprocessing data before training or inference.  
- Adjust hyperparameters in the scripts as needed for optimal performance.  

--- 

