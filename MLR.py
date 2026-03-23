# =====================================================
# Fire Detection using Logistic Regression (MLR)
# Author: Ahmed Ali
# ahmed.a.radhi@nahrainuniv.edu.iq
# Description:
# This script trains a Logistic Regression model to
# predict fire occurrence based on environmental data.
#
# The model uses:
#   - Temperature (°C)
#   - Relative Humidity (%)
#   - CO Concentration (ppm)
#
# The output is:
#   - Probability of fire occurrence
#   - Model coefficients (feature importance)
#
# =====================================================

# ================================
# Import Required Libraries
# ================================
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# ================================
#  1. Load Dataset
# ================================
# Load dataset from a CSV file
# NOTE: Update the file path as needed
data = pd.read_csv("dataset.csv")

# ================================
# 2. Define Features and Target
# ================================
# Input features (independent variables)
# These environmental factors influence fire occurrence
X = data[['temperature_2m', 'relative_humidity_2m (%)', 'CO_ppm']]

# Target variable (dependent variable)
# 0 → No Fire
# 1 → Fire Detected
y = data['fire']

# ================================
# 3. Split Dataset
# ================================
# Split data into:
#   - 80% Training data
#   - 20% Testing data
# random_state ensures reproducibility of results
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ================================
# 4. Train Logistic Regression Model
# ================================
# Initialize the Logistic Regression model
model = LogisticRegression()

# Train the model using training data
model.fit(X_train, y_train)

# ================================
# 5. Extract Model Coefficients
# ================================
# Coefficients indicate the importance (weight) of each feature
coefficients = model.coef_[0]

# Intercept represents the bias term of the model
intercept = model.intercept_[0]

# ================================
# 6. Display Model Parameters
# ================================
# Print intercept and feature coefficients
features = X.columns

print("Intercept:", intercept)

for f, c in zip(features, coefficients):
    print(f"Coefficient for {f}: {c}")

# ================================
# 7. Logistic Regression Equation
# ================================
# Construct the linear equation:
# z = b0 + b1*x1 + b2*x2 + b3*x3
equation = f"z = {intercept}"

for f, c in zip(features, coefficients):
    equation += f" + ({c} * {f})"

print("\nLogistic Regression Equation:")
print(equation)

# ================================
# 8. Probability Function (Sigmoid)
# ================================
# The logistic function converts z into probability:
#
# P(fire) = 1 / (1 + exp(-z))
#
# Output range:
#   0 → No Fire
#   1 → Fire
#
print("\nProbability Equation:")
print("P(fire) = 1 / (1 + exp(-z))")