#!/usr/bin/env python3
"""
QFINET Superior Training Script
Train the quantum-inspired neural network with advanced architecture
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import time
import pickle
from pathlib import Path
import os

# Settings
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
np.random.seed(42)
tf.random.set_seed(42)

print(f"✅ TensorFlow version: {tf.__version__}")
print(f"✅ NumPy version: {np.__version__}")
print(f"✅ Pandas version: {pd.__version__}")

# ============================================================
# LOAD DATA
# ============================================================
data_path = "training_data.csv"

if not os.path.exists(data_path):
    print(f"⚠️  {data_path} not found. Run: python data_generator.py --synthetic")
    exit(1)

df = pd.read_csv(data_path)
print(f"\n📊 Dataset shape: {df.shape}")
print(f"📋 Class Distribution:\n{df['THI_Class'].value_counts()}")

# ============================================================
# PREPROCESS DATA
# ============================================================
feature_cols = ['Brake_Temperature_C', 'Axle_Vibration_mms', 'Wheel_Wear_Percent', 
                'Engine_Load_Percent', 'Battery_Voltage_V', 'Fuel_Efficiency_kmL']

X = df[feature_cols].values
y_class = df['THI_Class'].values

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y_class)
num_classes = len(label_encoder.classes_)

print(f"\n📋 Classes: {label_encoder.classes_}")

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Reshape for CNN
X_train_cnn = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test_cnn = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

print(f"📊 Train set: {X_train_cnn.shape}, Test set: {X_test_cnn.shape}")

# ============================================================
# BUILD SUPERIOR QFINET CNN MODEL
# ============================================================
def build_qfinet_model(input_shape, num_classes):
    """
    ADVANCED QFINET CNN with quantum-inspired optimizations
    """
    inputs = layers.Input(shape=input_shape, name='input')
    
    # Block 1: Initial feature extraction
    x = layers.Conv1D(32, kernel_size=3, padding='same', activation='relu')(inputs)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.Conv1D(32, kernel_size=5, padding='same', activation='relu')(x)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.MaxPooling1D(pool_size=2)(x)
    x = layers.Dropout(0.2)(x)
    
    # Block 2: Enhanced feature extraction
    x = layers.Conv1D(48, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.Conv1D(48, kernel_size=5, padding='same', activation='relu')(x)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.MaxPooling1D(pool_size=2)(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 3: Deep feature extraction
    x = layers.Conv1D(64, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.Conv1D(64, kernel_size=5, padding='same', activation='relu')(x)
    x = layers.BatchNormalization(momentum=0.9)(x)
    
    # Quantum-inspired pooling
    avg_pool = layers.GlobalAveragePooling1D()(x)
    max_pool = layers.GlobalMaxPooling1D()(x)
    concat = layers.concatenate([avg_pool, max_pool], name='quantum_pool')
    
    # Dense layers
    x = layers.Dense(256, activation='relu', name='dense1')(concat)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Dense(128, activation='relu', name='dense2')(x)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Dense(64, activation='relu', name='dense3')(x)
    x = layers.BatchNormalization(momentum=0.9)(x)
    x = layers.Dropout(0.2)(x)
    
    outputs = layers.Dense(num_classes, activation='softmax', name='output')(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name='QFINET_Advanced')
    return model


def build_traditional_cnn_model(input_shape, num_classes):
    """Traditional CNN baseline"""
    model = models.Sequential([
        layers.Conv1D(32, kernel_size=3, padding='same', activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        
        layers.Conv1D(64, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        
        layers.Conv1D(128, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling1D(),
        
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    return model

# Build models
qfinet_model = build_qfinet_model(X_train_cnn.shape[1:], num_classes)
traditional_model = build_traditional_cnn_model(X_train_cnn.shape[1:], num_classes)

print("\n" + "="*60)
print("🚀 SUPERIOR QFINET CNN MODEL")
print("="*60)
qfinet_params = qfinet_model.count_params()
traditional_params = traditional_model.count_params()
print(f"✓ QFINET Parameters: {qfinet_params:,}")
print(f"• Traditional Parameters: {traditional_params:,}")
print(f"⚡ Reduction: {(1 - qfinet_params/traditional_params) * 100:.1f}%")

# ============================================================
# COMPILE AND TRAIN
# ============================================================
qfinet_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.005, beta_1=0.9, beta_2=0.999),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

traditional_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("\n" + "="*60)
print("🚀 TRAINING SUPERIOR QFINET")
print("="*60)

start_time = time.time()
qfinet_history = qfinet_model.fit(
    X_train_cnn, y_train,
    epochs=30,
    batch_size=32,
    validation_split=0.2,
    verbose=1,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-7)
    ]
)
qfinet_train_time = time.time() - start_time

print("\n" + "="*60)
print("TRAINING TRADITIONAL CNN")
print("="*60)

start_time = time.time()
traditional_history = traditional_model.fit(
    X_train_cnn, y_train,
    epochs=30,
    batch_size=32,
    validation_split=0.2,
    verbose=1,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-7)
    ]
)
traditional_train_time = time.time() - start_time

# ============================================================
# EVALUATE MODELS
# ============================================================
print("\n" + "="*60)
print("EVALUATING MODELS")
print("="*60)

def compute_metrics(y_true, y_pred, model_name):
    """Compute evaluation metrics"""
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    print(f"\n{model_name}:")
    print(f"  Accuracy:  {acc:.3f}")
    print(f"  Precision: {prec:.3f}")
    print(f"  Recall:    {rec:.3f}")
    print(f"  F1-Score:  {f1:.3f}")
    
    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}

# QFINET evaluation
qfinet_pred = np.argmax(qfinet_model.predict(X_test_cnn), axis=1)
qfinet_metrics = compute_metrics(y_test, qfinet_pred, "🚀 QFINET (Superior)")

# Traditional evaluation
traditional_pred = np.argmax(traditional_model.predict(X_test_cnn), axis=1)
traditional_metrics = compute_metrics(y_test, traditional_pred, "Traditional CNN")

# ML Models
print("\n" + "="*60)
print("TRAINING TRADITIONAL ML MODELS")
print("="*60)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
rf_metrics = compute_metrics(y_test, rf_model.predict(X_test), "Random Forest")

svm_model = SVC(kernel='rbf', random_state=42)
svm_model.fit(X_train, y_train)
svm_metrics = compute_metrics(y_test, svm_model.predict(X_test), "SVM")

lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train, y_train)
lr_metrics = compute_metrics(y_test, lr_model.predict(X_test), "Logistic Regression")

# ============================================================
# SAVE MODELS
# ============================================================
print("\n" + "="*60)
print("SAVING MODELS")
print("="*60)

models_dir = Path("models")
models_dir.mkdir(exist_ok=True)

qfinet_model.save(models_dir / "qfinet_model.h5")
traditional_model.save(models_dir / "traditional_model.h5")

preprocessing_data = {
    'scaler': scaler,
    'label_encoder': label_encoder,
    'feature_cols': feature_cols
}
with open(models_dir / "preprocessing.pkl", 'wb') as f:
    pickle.dump(preprocessing_data, f)

print("✅ Models saved successfully!")

# ============================================================
# PERFORMANCE COMPARISON
# ============================================================
print("\n" + "="*60)
print("📊 FINAL PERFORMANCE COMPARISON")
print("="*60)

results = {
    '🚀 QFINET CNN': qfinet_metrics['accuracy'],
    'Traditional CNN': traditional_metrics['accuracy'],
    'Random Forest': rf_metrics['accuracy'],
    'SVM': svm_metrics['accuracy'],
    'Logistic Regression': lr_metrics['accuracy']
}

for model, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
    print(f"{model:25s} → {acc:.1%} accuracy")

print("\n" + "="*60)
print("✅ TRAINING COMPLETE!")
print("="*60)
