Fire Detection System – Project README

---

Overview
This project presents a complete IoT-based Fire Detection System integrated with Machine Learning (ML) and a mobile application for real-time monitoring and alerting. The system detects fire hazards using environmental sensors and instantly notifies users and emergency responders through a cloud-connected infrastructure.

A key component of this system is a hybrid Machine Learning model (RF-XGB), which improves early fire detection and reduces false alarms.

---

Machine Learning Model (RF-XGB)

Model Description
The system uses a hybrid model combining:

* Random Forest (RF)
* XGBoost (XGB)

This ensemble approach enhances prediction accuracy compared to a single model.

How the Model Works

1. Environmental data is collected:

   * Temperature
   * Relative Humidity
   * Wind Speed
   * CO Concentration

2. Data is processed by both models:

   * Random Forest captures general patterns
   * XGBoost captures complex nonlinear relationships

3. Outputs are combined using:

  weighted Voting mechanism

4. Final Output:

   * Fire probability (0 to 1)
   * Classification (0 = No Fire, 1 = Fire)

Advantages

* Early fire detection before visible flames
* High accuracy due to hybrid modeling
* Robust against noise and sensor errors
* Reduced false positives using confirmation logic
* Suitable for real-time processing

---

Project Structure

AI-model+IoT gate-way/
Base-station/
Mobile-Application/
Node-deployments/
Sensor node/
Sink-node/
dataset/
MLR/

---

AI-model + IoT Gateway

* Receives sensor data from base stations
* Runs RF-XGB hybrid model
* Sends predictions to cloud database
* Sends instant fire alerts to users via Telegram
*Connected to the cloud database or backend server
*Provides real-time notifications even if the mobile app is closed

---

Base-station

* Collects data from multiple sensor nodes
* Transfers data to sink node or gateway

---

Mobile-Application

* Displays real-time sensor data
* Shows fire alerts instantly
* Connected to cloud database (e.g., Firebase)

---

Node-deployments

* Contains node placement strategies
* Optimizes sensor distribution and coverage

---

Sensor node

* Measures environmental data:

  * Temperature
  * Humidity
  * CO gas
* Sends data wirelessly

---

Sink-node

* Central receiver in the network
* Forwards data to gateway

---

dataset

* Historical environmental data
* Fire labels (0 = No Fire, 1 = Fire)
* Used for training and evaluation

---

MLR (Logistic Regression)

This module includes:

Python scripts for training Logistic Regression models
Extraction of model coefficients
Fire probability prediction in sensor nodes to reduce network traffic and power consumption.

---

System Workflow

1. Sensor nodes collect environmental data
2. Data is sent to base stations
3. Base stations forward data to sink node
4. Gateway processes data using RF-XGB model
5. Fire probability is computed
6. Results are stored in cloud database
7. Mobile application retrieves data in real time
8. Alerts are sent instantly if fire is detected

---

Real-Time Performance

* Low-latency system
* Detection within seconds
* Supports fast emergency response

---

Technologies Used

* Arduino / Embedded Systems
* nRF24L01 Wireless Communication
* Python (Random Forest, XGBoost, Logistic Regression)
* Firebase Realtime Database
* Android Development

---

Project Goals

* Early fire detection using AI
* Reduce emergency response time
* Minimize false alarms
* Provide real-time monitoring
*reduce network traffic and power consumption
*increase the life time of sensor nodes

---
Datasets used in this study include:

1. NASA FIRMS Fire Dataset:
This dataset provides active fire detection points collected via satellite observations. It includes latitude, longitude, and fire radiative power.
Access link: https://firms.modaps.eosdis.nasa.gov/

2. Meteorological Data:
Environmental variables such as temperature, humidity, and wind speed were used. 

---
Author
Ahmed Ali
ahmed.a.radhi@nahrainuniv.edu.iq

---

License
This project is for academic and research purposes.
