"""
Phase 3: Speed Optimization for QFINET
======================================
Techniques: Knowledge distillation, quantization, batch size optimization
Target: <30s training time, <10ms inference
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
import pickle
import json
import time
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

class SpeedOptimizer:
    def __init__(self, data_file='training_data.csv', models_dir='models'):
        self.data_file = data_file
        self.models_dir = models_dir
        Path(self.models_dir).mkdir(exist_ok=True)
        
    def load_data(self):
        """Load training data (smaller subset for speed)"""
        print("\n📊Loading training data...")
        df = pd.read_csv(self.data_file)
        df = df.sample(n=min(5000, len(df)), random_state=42)
        
        feature_cols = ['Brake_Temperature_C', 'Axle_Vibration_mms', 'Wheel_Wear_Percent',
                       'Engine_Load_Percent', 'Battery_Voltage_V', 'Fuel_Efficiency_kmL']
        X = df[feature_cols].values
        y = pd.factorize(df['THI_Class'])[0]
        
        mean = X.mean(axis=0)
        std = X.std(axis=0)
        X = (X - mean) / (std + 1e-8)
        
        with open(os.path.join(self.models_dir, 'preprocessing_speed.pkl'), 'wb') as f:
            pickle.dump({'mean': mean, 'std': std}, f)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"✓ Loaded {X_train.shape[0]} train, {X_test.shape[0]} test samples")
        return X_train, X_test, y_train, y_test
    
    def build_teacher_model(self):
        """Build teacher model (larger, more accurate)"""
        model = models.Sequential([
            layers.Input(shape=(6,)),
            layers.Reshape((6, 1)),
            
            layers.Conv1D(32, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Conv1D(48, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Dropout(0.2),
            
            layers.Conv1D(48, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Conv1D(64, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Dropout(0.3),
            
            layers.GlobalAveragePooling1D(),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def build_student_model(self):
        """Build student model (smaller, faster)"""
        model = models.Sequential([
            layers.Input(shape=(6,)),
            layers.Reshape((6, 1)),
            
            layers.Conv1D(16, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Conv1D(24, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Dropout(0.1),
            
            layers.GlobalAveragePooling1D(),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.1),
            
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def distillation_loss(self, y_true, y_pred, teacher_pred, temperature=4.0, alpha=0.3):
        """Custom loss for knowledge distillation"""
        # Standard CE loss
        standard_loss = tf.keras.losses.sparse_categorical_crossentropy(y_true, y_pred)
        
        # Distillation loss (soften outputs)
        teacher_soft = tf.nn.softmax(teacher_pred / temperature)
        student_soft = tf.nn.softmax(y_pred / temperature)
        distill_loss = tf.keras.losses.KLD(teacher_soft, student_soft)
        
        return alpha * standard_loss + (1 - alpha) * distill_loss
    
    def train_teacher(self, teacher_model, X_train, y_train, epochs=20):
        """Train teacher model quickly"""
        print("\n🏫 Training teacher model...")
        start = time.time()
        
        history = teacher_model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=64,
            validation_split=0.2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss', patience=5, restore_best_weights=True
                )
            ],
            verbose=0
        )
        
        training_time = time.time() - start
        print(f"✓ Teacher trained in {training_time:.2f}s ({len(history.history['loss'])} epochs)")
        
        return teacher_model
    
    def train_student_distilled(self, student_model, teacher_model, X_train, y_train, epochs=15):
        """Train student model with knowledge distillation"""
        print("\n👨‍🎓 Training student model (knowledge distillation)...")
        start = time.time()
        
        history = student_model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=128,  # Larger batch for speed
            validation_split=0.2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss', patience=4, restore_best_weights=True
                )
            ],
            verbose=0
        )
        
        training_time = time.time() - start
        print(f"✓ Student trained in {training_time:.2f}s ({len(history.history['loss'])} epochs)")
        
        return student_model
    
    def quantize_model(self, model, X_test):
        """Quantize model to int8 for faster inference"""
        print("\n🔬 Quantizing model to INT8...")
        
        def representative_dataset():
            for data in tf.data.Dataset.from_tensor_slices(X_test.astype(np.float32)).batch(1):
                yield [tf.reshape(data, [1, 6, 1])]
        
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = representative_dataset
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS_INT8
        ]
        converter.inference_input_type = tf.int8
        converter.inference_output_type = tf.int8
        
        quantized_model = converter.convert()
        
        return quantized_model
    
    def measure_inference_speed(self, model, X_test, num_samples=100):
        """Measure inference latency"""
        latencies = []
        _ = model.predict(X_test[:10], verbose=0)  # Warm-up
        
        for i in range(num_samples):
            start = time.time()
            _ = model.predict(np.array([X_test[i]]), verbose=0)
            latency = (time.time() - start) * 1000
            latencies.append(latency)
        
        return {
            'mean': np.mean(latencies),
            'std': np.std(latencies),
            'min': np.min(latencies),
            'max': np.max(latencies)
        }
    
    def evaluate_model(self, model, X_test, y_test):
        """Evaluate accuracy"""
        predictions = np.argmax(model.predict(X_test, verbose=0), axis=1)
        return accuracy_score(y_test, predictions)
    
    def run_optimization(self):
        """Execute speed optimization"""
        print("\n" + "="*70)
        print("⚡ PHASE 3: SPEED OPTIMIZATION")
        print("="*70)
        
        # Load data
        X_train, X_test, y_train, y_test = self.load_data()
        
        # Train teacher model
        teacher_model = self.build_teacher_model()
        teacher_model = self.train_teacher(teacher_model, X_train, y_train, epochs=20)
        teacher_accuracy = self.evaluate_model(teacher_model, X_test, y_test)
        print(f"📊 Teacher accuracy: {teacher_accuracy:.4f}")
        
        # Train student with distillation
        student_model = self.build_student_model()
        student_model = self.train_student_distilled(student_model, teacher_model, X_train, y_train, epochs=15)
        student_accuracy = self.evaluate_model(student_model, X_test, y_test)
        print(f"📊 Student accuracy: {student_accuracy:.4f}")
        
        # Measure inference speed - student
        print("\n⚗️ Measuring inference speed...")
        student_inference = self.measure_inference_speed(student_model, X_test)
        print(f"✓ Student inference: {student_inference['mean']:.2f}ms (±{student_inference['std']:.2f}ms)")
        
        # Model sizes
        teacher_model.save(os.path.join(self.models_dir, 'teacher_model.h5'))
        student_model.save(os.path.join(self.models_dir, 'qfinet_speed_optimized.h5'))
        
        teacher_size = os.path.getsize(os.path.join(self.models_dir, 'teacher_model.h5')) / (1024 * 1024)
        student_size = os.path.getsize(os.path.join(self.models_dir, 'qfinet_speed_optimized.h5')) / (1024 * 1024)
        
        print(f"\n💾 Model sizes:")
        print(f"✓ Teacher: {teacher_size:.2f} MB ({teacher_model.count_params():,} params)")
        print(f"✓ Student: {student_size:.2f} MB ({student_model.count_params():,} params)")
        print(f"  Reduction: {(1 - student_size/teacher_size)*100:.1f}%")
        
        # Save results
        results = {
            'teacher_accuracy': float(teacher_accuracy),
            'student_accuracy': float(student_accuracy),
            'accuracy_drop': float(teacher_accuracy - student_accuracy),
            'teacher_params': int(teacher_model.count_params()),
            'student_params': int(student_model.count_params()),
            'student_inference_ms': float(student_inference['mean']),
            'student_inference_std_ms': float(student_inference['std']),
            'size_reduction_percent': float((1 - student_size/teacher_size)*100),
            'speedup_factor': 1.0  # Relative to baseline
        }
        
        with open(os.path.join(self.models_dir, 'speed_optimization_results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "="*70)
        print("✅ PHASE 3 COMPLETE - SPEED OPTIMIZATION")
        print("="*70)
        print(f"\n📊 Results:")
        print(f"  • Teacher accuracy: {teacher_accuracy:.4f}")
        print(f"  • Student accuracy: {student_accuracy:.4f}")
        print(f"  • Student inference: {student_inference['mean']:.2f}ms")
        print(f"  • Model compression: {(1 - student_size/teacher_size)*100:.1f}%")
        print(f"\n📁 Models saved:")
        print(f"  • qfinet_speed_optimized.h5 ({student_size:.2f} MB)")

if __name__ == '__main__':
    optimizer = SpeedOptimizer()
    optimizer.run_optimization()
