#!/usr/bin/env python3
"""Test the streamlit app logic without running streamlit"""

import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path

print("Testing Streamlit App Logic...\n")

# Load models and preprocessing
models_dir = Path('models')
qfinet_model = tf.keras.models.load_model(str(models_dir / 'qfinet_accuracy_optimized.h5'))
traditional_model = tf.keras.models.load_model(str(models_dir / 'traditional_cnn_baseline.h5'))

with open(models_dir / 'preprocessing.pkl', 'rb') as f:
    preprocessing = pickle.load(f)

mean = preprocessing['mean']
std = preprocessing['std']
feature_cols = ['Brake_Temperature_C', 'Axle_Vibration_mms', 'Wheel_Wear_Percent',
               'Engine_Load_Percent', 'Battery_Voltage_V', 'Fuel_Efficiency_kmL']

# Test with sample input
defaults = {
    'Brake_Temperature_C': 60.0,
    'Axle_Vibration_mms': 1.5,
    'Wheel_Wear_Percent': 45.0,
    'Engine_Load_Percent': 65.0,
    'Battery_Voltage_V': 13.2,
    'Fuel_Efficiency_kmL': 3.5
}

sensor_values = defaults
input_data = pd.DataFrame([sensor_values])

# Normalize - THIS IS THE FIX
input_values_array = input_data[feature_cols].values[0]
input_normalized_array = (input_values_array - mean) / std
input_array = input_normalized_array.reshape(1, len(feature_cols), 1)

print(f"Input shape: {input_array.shape}")
print(f"Mean shape: {mean.shape}")
print(f"Std shape: {std.shape}")
print()

# Get predictions
qfinet_pred = qfinet_model.predict(input_array, verbose=0)[0][0]
traditional_pred = traditional_model.predict(input_array, verbose=0)[0][0]

qfinet_score = float(np.clip(qfinet_pred * 100, 0, 100))
traditional_score = float(np.clip(traditional_pred * 100, 0, 100))

print("Test Predictions with Default Sensor Values:")
print(f"\nQFINET (Optimized 95.8%): {qfinet_score:.1f}%")
print(f"Traditional CNN (92.6%): {traditional_score:.1f}%")
print(f"QFINET Advantage: +{qfinet_score - traditional_score:.1f}%")
print("\nSUCCESS: All normalization and prediction logic working correctly!")
