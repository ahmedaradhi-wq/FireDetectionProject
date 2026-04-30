# =====================================================
# Hybrid IoT Fire Detection System
# Author: Ahmed Ali
#ahmed.a.radhi@nahrainuniv.edu.iq
# Description:
# This script reads real-time sensor data from Arduino,
# applies a hybrid ML model (Random Forest + XGBoost),
# updates Firebase, and sends Telegram alerts when fire is detected.
# =====================================================

# Import required libraries
import pandas as pd
import numpy as np
import serial
import time
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
import firebase_admin
from firebase_admin import credentials, db

# =====================================================
# Train Hybrid Model
# =====================================================
print("Training Hybrid Model...")

# Load dataset (update path as needed)
data = pd.read_csv("dataset.csv")

# Define input features and target variable
features = ["temp_C", "RH_pct", "CO_ppm"]
target = "fire_flag"

X = data[features]
y = data[target]

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Initialize models
rf = RandomForestClassifier(n_estimators=100, random_state=42)
xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')

# Train models
rf.fit(X_train, y_train)
xgb.fit(X_train, y_train)

# Evaluate models using ROC-AUC
rf_auc = roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1])
xgb_auc = roc_auc_score(y_test, xgb.predict_proba(X_test)[:, 1])

# Compute weights for hybrid model
w_rf = rf_auc / (rf_auc + xgb_auc)
w_xgb = xgb_auc / (rf_auc + xgb_auc)

print("Hybrid Model Ready\n")

# Store sensor data history
sensor_data = []

# =====================================================
# Firebase Setup
# =====================================================
# Load Firebase credentials
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://YOUR_PROJECT.firebaseio.com/'
})

print("Firebase Connected\n")

# =====================================================
# Telegram Setup
# =====================================================
# Telegram Bot credentials (replace with your own)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# Function to send alert via Telegram
def send_alert(sensor_id, lat, lon):

    # Generate timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    # Create Google Maps link
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"

    # Format alert message
    message = (
        f" *Fire Alert!* \n"
        f" Node: {sensor_id}\n"
        f" {timestamp}\n"
        f" {lat:.6f}, {lon:.6f}\n"
        f"[Open Map]({maps_link})"
    )

    # Telegram API URL
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Payload data
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    # Send request
    requests.post(url, data=payload)
    print(f"Alert Sent for Node {sensor_id}")

# =====================================================
# Serial Connection
# =====================================================
# Connect to Arduino via serial port
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

print("System Started...\n")

# Dictionary to track last known status (unused but reserved)
last_status = {}

# Anti-spam mechanism (5 minutes delay per node)
last_sent_time = {}
DELAY = 300

# =====================================================
#  Real-Time Data Processing Loop
# =====================================================
while True:

    # Read line from serial
    line = ser.readline().decode('utf-8').strip()
    if not line:
        continue

    # Split incoming data
    vals = [v for v in line.split(',') if v.strip() != '']

    # Validate data length
    if len(vals) != 6:
        print("Invalid data length:", line)
        continue

    # Convert values to float
    try:
        vals = [float(x) for x in vals]
    except ValueError:
        print("Invalid data format:", line)
        continue

    # Create sensor data dictionary
    sensor = {
        "lat": vals[0],
        "lon": vals[1],
        "temp_C": vals[2],
        "RH_pct": vals[3],
        "CO_ppm": vals[4],
        "sensor_id": vals[5],
    }

    sensor_id = int(sensor['sensor_id'])

    # =====================================================
    # Apply Hybrid Model Prediction
    # =====================================================
    X_new = np.array([[sensor[f] for f in features]])

    p_rf = rf.predict_proba(X_new)[:, 1][0]
    p_xgb = xgb.predict_proba(X_new)[:, 1][0]

    # Hybrid probability
    p_hybrid = (w_rf * p_rf) + (w_xgb * p_xgb)

    sensor["prob"] = p_hybrid

    # Fire classification 
    sensor["fire"] = int(p_hybrid >= 0.5)

    sensor_data.append(sensor)

    # =====================================================
    # Print Results
    # =====================================================
    status = "FIRE RISK!" if sensor["fire"] == 1 else "Safe"

    print(f"{sensor['lat']:.3f},{sensor['lon']:.3f} | "
          f"T={sensor['temp_C']}°C | RH={sensor['RH_pct']}% | CO={sensor['CO_ppm']} ppm | "
          f"→ {status} (P={sensor['prob']:.2f})|, ID={sensor_id}")

    # =====================================================
    # Firebase Update
    # =====================================================
    sensor_id = int(sensor["sensor_id"])
    lat = sensor["lat"]
    lon = sensor["lon"]
    temp = sensor["temp_C"]
    rh = sensor["RH_pct"]
    co = sensor["CO_ppm"]

    # Define fire status string
    fire_status = "Fire" if sensor["fire"] == 1 else "normal"

    # Update Firebase database
    sensor_ref = db.reference(f"sensors/{sensor_id}")
    sensor_ref.update({
        "lat": lat,
        "lon": lon,
        "status": fire_status
    })

    # =====================================================
    # Telegram Alert (with Anti-Spam)
    # =====================================================
    if sensor["fire"] == 1:

        current_time = time.time()

        # Send alert only if delay has passed
        if sensor_id not in last_sent_time or (current_time - last_sent_time[sensor_id] > DELAY):
            send_alert(sensor_id, sensor["lat"], sensor["lon"])
            last_sent_time[sensor_id] = current_time