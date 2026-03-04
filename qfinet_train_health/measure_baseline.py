"""
Measure Baseline Metrics for QFINET Model
==========================================
Records training time, model size, inference latency, and accuracy metrics.
Creates a benchmark CSV for tracking optimization progress.
"""

import os
import time
import json
import csv
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
import pickle
from datetime import datetime
from pathlib import Path

# Suppress TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

class BaselineMeasurer:
    def __init__(self, data_file='training_data.csv', models_dir='models'):
        self.data_file = data_file
        self.models_dir = models_dir
        self.results = {}
        
        # Create models directory if doesn't exist
        Path(self.models_dir).mkdir(exist_ok=True)
        
    def load_data(self):
        """Load and preprocess training data"""
        print("\n📊 Loading training data...")
        df = pd.read_csv(self.data_file)
        
        # Use a smaller subset for faster baseline measurement
        df = df.sample(n=min(5000, len(df)), random_state=42)
        
        # Features and labels
        feature_cols = ['Brake_Temperature_C', 'Axle_Vibration_mms', 'Wheel_Wear_Percent',
                       'Engine_Load_Percent', 'Battery_Voltage_V', 'Fuel_Efficiency_kmL']
        X = df[feature_cols].values
        y = pd.factorize(df['THI_Class'])[0]
        
        # Normalize features
        mean = X.mean(axis=0)
        std = X.std(axis=0)
        X = (X - mean) / (std + 1e-8)
        
        # Save preprocessing
        with open(os.path.join(self.models_dir, 'preprocessing.pkl'), 'wb') as f:
            pickle.dump({'mean': mean, 'std': std}, f)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"✓ Data loaded: {X_train.shape[0]} train, {X_test.shape[0]} test samples")
        return X_train, X_test, y_train, y_test
    
    def build_qfinet(self, input_size=6):
        """Build advanced QFINET architecture"""
        model = models.Sequential([
            layers.Input(shape=(input_size,)),
            layers.Reshape((input_size, 1)),
            
            # Multi-scale convolution block 1
            layers.Conv1D(32, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Conv1D(48, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Dropout(0.2),
            
            # Multi-scale convolution block 2
            layers.Conv1D(48, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Conv1D(64, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Dropout(0.3),
            
            # Quantum-inspired pooling (combined avg+max)
            layers.GlobalAveragePooling1D(),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def build_traditional_cnn(self, input_size=6):
        """Build traditional CNN baseline"""
        model = models.Sequential([
            layers.Input(shape=(input_size,)),
            layers.Reshape((input_size, 1)),
            
            layers.Conv1D(32, 3, padding='same', activation='relu'),
            layers.MaxPooling1D(2, padding='same'),
            layers.Dropout(0.2),
            
            layers.Conv1D(64, 3, padding='same', activation='relu'),
            layers.MaxPooling1D(2, padding='same'),
            layers.Dropout(0.2),
            
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def measure_training_time(self, model, X_train, y_train, epochs=30, batch_size=32):
        """Measure training time and convergence"""
        print(f"\n⏱️ Measuring training time... ({epochs} epochs)")
        
        start_time = time.time()
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss', patience=5, restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss', factor=0.5, patience=3, min_lr=0.00001
                )
            ],
            verbose=0
        )
        
        total_time = time.time() - start_time
        epochs_trained = len(history.history['loss'])
        time_per_epoch = total_time / epochs_trained
        
        return {
            'total_time_seconds': total_time,
            'time_per_epoch': time_per_epoch,
            'epochs_trained': epochs_trained,
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1])
        }
    
    def measure_model_size(self, model, model_name):
        """Measure model file size and parameter count"""
        # Count parameters
        total_params = model.count_params()
        
        # Save and measure file size
        model_path = os.path.join(self.models_dir, f'{model_name}_baseline.h5')
        model.save(model_path)
        file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
        
        return {
            'total_parameters': total_params,
            'file_size_mb': file_size_mb,
            'model_path': model_path
        }
    
    def measure_inference_latency(self, model, X_test, num_samples=100):
        """Measure inference time"""
        print(f"\n⚡ Measuring inference latency ({num_samples} samples)...")
        
        # Warm-up
        _ = model.predict(X_test[:10], verbose=0)
        
        # Measure
        latencies = []
        for i in range(num_samples):
            start = time.time()
            _ = model.predict(np.array([X_test[i]]), verbose=0)
            latency = (time.time() - start) * 1000  # milliseconds
            latencies.append(latency)
        
        return {
            'mean_latency_ms': np.mean(latencies),
            'std_latency_ms': np.std(latencies),
            'min_latency_ms': np.min(latencies),
            'max_latency_ms': np.max(latencies)
        }
    
    def measure_accuracy(self, model, X_test, y_test):
        """Measure accuracy and related metrics"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        predictions = np.argmax(model.predict(X_test, verbose=0), axis=1)
        
        return {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, average='weighted'),
            'recall': recall_score(y_test, predictions, average='weighted'),
            'f1_score': f1_score(y_test, predictions, average='weighted')
        }
    
    def run_baseline(self):
        """Execute complete baseline measurement"""
        print("\n" + "="*70)
        print("🔬 BASELINE MEASUREMENT - PHASE 1")
        print("="*70)
        
        # Load data
        X_train, X_test, y_train, y_test = self.load_data()
        
        # Measure QFINET
        print("\n" + "-"*70)
        print("📌 QFINET Model")
        print("-"*70)
        qfinet = self.build_qfinet()
        qfinet_training = self.measure_training_time(qfinet, X_train, y_train)
        qfinet_size = self.measure_model_size(qfinet, 'qfinet')
        qfinet_latency = self.measure_inference_latency(qfinet, X_test)
        qfinet_accuracy = self.measure_accuracy(qfinet, X_test, y_test)
        
        print(f"  ✓ Training time: {qfinet_training['total_time_seconds']:.2f}s ({qfinet_training['epochs_trained']} epochs)")
        print(f"  ✓ Model size: {qfinet_size['file_size_mb']:.2f} MB ({qfinet_size['total_parameters']:,} params)")
        print(f"  ✓ Inference: {qfinet_latency['mean_latency_ms']:.2f}ms (±{qfinet_latency['std_latency_ms']:.2f}ms)")
        print(f"  ✓ Accuracy: {qfinet_accuracy['accuracy']:.4f}")
        
        # Measure Traditional CNN
        print("\n" + "-"*70)
        print("📌 Traditional CNN Model")
        print("-"*70)
        trad_cnn = self.build_traditional_cnn()
        trad_training = self.measure_training_time(trad_cnn, X_train, y_train)
        trad_size = self.measure_model_size(trad_cnn, 'traditional_cnn')
        trad_latency = self.measure_inference_latency(trad_cnn, X_test)
        trad_accuracy = self.measure_accuracy(trad_cnn, X_test, y_test)
        
        print(f"  ✓ Training time: {trad_training['total_time_seconds']:.2f}s ({trad_training['epochs_trained']} epochs)")
        print(f"  ✓ Model size: {trad_size['file_size_mb']:.2f} MB ({trad_size['total_parameters']:,} params)")
        print(f"  ✓ Inference: {trad_latency['mean_latency_ms']:.2f}ms (±{trad_latency['std_latency_ms']:.2f}ms)")
        print(f"  ✓ Accuracy: {trad_accuracy['accuracy']:.4f}")
        
        # Save results
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'qfinet': {**qfinet_training, **qfinet_size, **qfinet_latency, **qfinet_accuracy},
            'traditional_cnn': {**trad_training, **trad_size, **trad_latency, **trad_accuracy}
        }
        
        # Save to JSON
        with open(os.path.join(self.models_dir, 'baseline_metrics.json'), 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save to CSV
        csv_file = os.path.join(self.models_dir, 'baseline_benchmark.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'QFINET', 'Traditional_CNN', 'Unit'])
            
            metrics = [
                ('Accuracy', 'accuracy', '%'),
                ('Precision', 'precision', '%'),
                ('Recall', 'recall', '%'),
                ('F1-Score', 'f1_score', '%'),
                ('Training Time', 'total_time_seconds', 'seconds'),
                ('Time per Epoch', 'time_per_epoch', 'seconds'),
                ('Epochs Trained', 'epochs_trained', 'count'),
                ('Model Size', 'file_size_mb', 'MB'),
                ('Parameters', 'total_parameters', 'count'),
                ('Inference Latency', 'mean_latency_ms', 'ms'),
                ('Inference Std Dev', 'std_latency_ms', 'ms')
            ]
            
            for metric_name, key, unit in metrics:
                qfinet_val = self.results['qfinet'].get(key, 'N/A')
                trad_val = self.results['traditional_cnn'].get(key, 'N/A')
                
                if isinstance(qfinet_val, (int, float)):
                    qfinet_val = f"{qfinet_val:.4f}" if isinstance(qfinet_val, float) else str(qfinet_val)
                if isinstance(trad_val, (int, float)):
                    trad_val = f"{trad_val:.4f}" if isinstance(trad_val, float) else str(trad_val)
                
                writer.writerow([metric_name, qfinet_val, trad_val, unit])
        
        print("\n" + "="*70)
        print("✅ BASELINE MEASUREMENT COMPLETE")
        print("="*70)
        print(f"\n📁 Results saved to:")
        print(f"   • {csv_file}")
        print(f"   • {os.path.join(self.models_dir, 'baseline_metrics.json')}")
        print("\n📊 Summary:")
        print(f"   QFINET Accuracy:        {self.results['qfinet']['accuracy']:.4f}")
        print(f"   Traditional CNN Accuracy: {self.results['traditional_cnn']['accuracy']:.4f}")
        print(f"   QFINET Training Time:    {self.results['qfinet']['total_time_seconds']:.2f}s")
        print(f"   QFINET Model Size:       {self.results['qfinet']['file_size_mb']:.2f} MB")
        print(f"   QFINET Inference:        {self.results['qfinet']['mean_latency_ms']:.2f}ms")
        
        return self.results

if __name__ == '__main__':
    measurer = BaselineMeasurer()
    measurer.run_baseline()
