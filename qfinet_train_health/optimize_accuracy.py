"""
Phase 2: Accuracy Optimization for QFINET
==========================================
Techniques: Data augmentation, ensemble voting, hyperparameter tuning with Optuna
Target: Reach 99%+ accuracy
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
import optuna
from optuna.trial import TrialState
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

class AccuracyOptimizer:
    def __init__(self, data_file='training_data.csv', models_dir='models'):
        self.data_file = data_file
        self.models_dir = models_dir
        Path(self.models_dir).mkdir(exist_ok=True)
        
    def load_data(self):
        """Load training data"""
        print("\n📊 Loading training data...")
        df = pd.read_csv(self.data_file)
        df = df.sample(n=min(10000, len(df)), random_state=42)
        
        feature_cols = ['Brake_Temperature_C', 'Axle_Vibration_mms', 'Wheel_Wear_Percent',
                       'Engine_Load_Percent', 'Battery_Voltage_V', 'Fuel_Efficiency_kmL']
        X = df[feature_cols].values
        y = pd.factorize(df['THI_Class'])[0]
        
        mean = X.mean(axis=0)
        std = X.std(axis=0)
        X = (X - mean) / (std + 1e-8)
        
        with open(os.path.join(self.models_dir, 'preprocessing.pkl'), 'wb') as f:
            pickle.dump({'mean': mean, 'std': std}, f)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"✓ Loaded {X_train.shape[0]} train, {X_test.shape[0]} test samples")
        return X_train, X_test, y_train, y_test
    
    def augment_data(self, X, y, factor=3):
        """Data augmentation with noise injection"""
        print(f"\n🔄 Augmenting data ({factor}x) with noise injection...")
        X_aug = [X]
        y_aug = [y]
        
        for i in range(factor - 1):
            # Add Gaussian noise
            noise_level = 0.02 * (i + 1)
            X_noisy = X + np.random.normal(0, noise_level, X.shape)
            X_aug.append(X_noisy)
            y_aug.append(y)
        
        X_augmented = np.vstack(X_aug)
        y_augmented = np.hstack(y_aug)
        
        print(f"✓ Augmented from {len(X)} to {len(X_augmented)} samples")
        return X_augmented, y_augmented
    
    def build_qfinet_advanced(self, trial=None, dropout1=0.2, dropout2=0.3,
                              conv_channels=32, dense_units=128):
        """Build QFINET with optional hyperparameter tuning"""
        model = models.Sequential([
            layers.Input(shape=(6,)),
            layers.Reshape((6, 1)),
            
            # Multi-scale convolution block 1
            layers.Conv1D(conv_channels, 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Conv1D(int(conv_channels * 1.5), 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Dropout(dropout1),
            
            # Multi-scale convolution block 2
            layers.Conv1D(int(conv_channels * 1.5), 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Conv1D(int(conv_channels * 2), 3, padding='same', activation='relu'),
            layers.BatchNormalization(momentum=0.9),
            layers.Dropout(dropout2),
            
            # Global pooling + dense layers
            layers.GlobalAveragePooling1D(),
            layers.Dense(dense_units, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(int(dense_units / 2), activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(3, activation='softmax')
        ])
        
        learning_rate = trial.suggest_float('learning_rate', 0.0001, 0.01, log=True) if trial else 0.001
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_with_early_stopping(self, model, X_train, y_train, epochs=50):
        """Train model with early stopping"""
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=32,
            validation_split=0.2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss', patience=7, restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss', factor=0.5, patience=4, min_lr=0.00001
                )
            ],
            verbose=0
        )
        return history
    
    def evaluate_model(self, model, X_test, y_test):
        """Evaluate model performance"""
        predictions = np.argmax(model.predict(X_test, verbose=0), axis=1)
        return accuracy_score(y_test, predictions)
    
    def hyperparameter_tuning(self, X_train, Y_train, X_val, y_val, n_trials=10):
        """Use Optuna to find best hyperparameters"""
        print(f"\n🔬 Hyperparameter tuning ({n_trials} trials) with Optuna...")
        
        def objective(trial):
            dropout1 = trial.suggest_float('dropout1', 0.1, 0.4)
            dropout2 = trial.suggest_float('dropout2', 0.2, 0.5)
            conv_channels = trial.suggest_int('conv_channels', 16, 64, step=16)
            dense_units = trial.suggest_int('dense_units', 64, 256, step=32)
            
            model = self.build_qfinet_advanced(
                trial, dropout1, dropout2, conv_channels, dense_units
            )
            
            history = self.train_with_early_stopping(model, X_train, Y_train, epochs=30)
            
            accuracy = self.evaluate_model(model, X_val, y_val)
            return accuracy
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
        
        best_trial = study.best_trial
        print(f"\n✓ Best accuracy: {best_trial.value:.4f}")
        print(f"✓ Best params: {best_trial.params}")
        
        return best_trial.params
    
    def build_ensemble(self, X_train, y_train, X_test, y_test):
        """Build ensemble of QFINET models"""
        print(f"\n🎯 Training ensemble (3 models with different seeds)...")
        
        ensemble_models = []
        ensemble_accuracies = []
        
        for i in range(3):
            print(f"  Model {i+1}/3...")
            tf.random.set_seed(42 + i)
            np.random.seed(42 + i)
            
            model = self.build_qfinet_advanced()
            self.train_with_early_stopping(model, X_train, y_train, epochs=40)
            
            accuracy = self.evaluate_model(model, X_test, y_test)
            ensemble_models.append(model)
            ensemble_accuracies.append(accuracy)
            print(f"    Model {i+1} accuracy: {accuracy:.4f}")
        
        return ensemble_models, ensemble_accuracies
    
    def ensemble_predict(self, models, X):
        """Average predictions from ensemble"""
        predictions = []
        for model in models:
            pred = model.predict(X, verbose=0)
            predictions.append(np.argmax(pred, axis=1))
        
        # Majority voting
        ensemble_preds = []
        for i in range(X.shape[0]):
            votes = [pred[i] for pred in predictions]
            ensemble_preds.append(max(set(votes), key=votes.count))
        
        return np.array(ensemble_preds)
    
    def run_optimization(self):
        """Execute accuracy optimization"""
        print("\n" + "="*70)
        print("🚀 PHASE 2: ACCURACY OPTIMIZATION")
        print("="*70)
        
        # Load data
        X_train, X_test, y_train, y_test = self.load_data()
        
        # Data augmentation
        X_train_aug, y_train_aug = self.augment_data(X_train, y_train, factor=3)
        
        # Hyperparameter tuning
        X_train_tune, X_val, y_train_tune, y_val = train_test_split(
            X_train_aug, y_train_aug, test_size=0.2, random_state=42
        )
        best_params = self.hyperparameter_tuning(X_train_tune, y_train_tune, X_val, y_val, n_trials=5)
        
        # Train optimized single model
        print(f"\n📈 Training optimized single model...")
        optimized_model = self.build_qfinet_advanced(
            trial=None,
            dropout1=best_params.get('dropout1', 0.2),
            dropout2=best_params.get('dropout2', 0.3),
            conv_channels=best_params.get('conv_channels', 32),
            dense_units=best_params.get('dense_units', 128)
        )
        
        self.train_with_early_stopping(optimized_model, X_train_aug, y_train_aug, epochs=50)
        single_accuracy = self.evaluate_model(optimized_model, X_test, y_test)
        print(f"✓ Optimized single model accuracy: {single_accuracy:.4f}")
        
        # Train ensemble
        ensemble_models, individual_accuracies = self.build_ensemble(
            X_train_aug, y_train_aug, X_test, y_test
        )
        
        # Ensemble prediction
        ensemble_predictions = self.ensemble_predict(ensemble_models, X_test)
        ensemble_accuracy = accuracy_score(y_test, ensemble_predictions)
        
        print(f"\n✨ Ensemble accuracy: {ensemble_accuracy:.4f} (avg individual: {np.mean(individual_accuracies):.4f})")
        
        # Save optimized model
        optimized_model.save(os.path.join(self.models_dir, 'qfinet_accuracy_optimized.h5'))
        
        # Save ensemble
        for i, model in enumerate(ensemble_models):
            model.save(os.path.join(self.models_dir, f'qfinet_ensemble_model_{i}.h5'))
        
        # Save results
        results = {
            'single_model_accuracy': float(single_accuracy),
            'ensemble_accuracy': float(ensemble_accuracy),
            'individual_accuracies': [float(acc) for acc in individual_accuracies],
            'best_hyperparameters': best_params,
            'data_augmentation_factor': 3,
            'ensemble_size': 3
        }
        
        with open(os.path.join(self.models_dir, 'accuracy_optimization_results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "="*70)
        print("✅ PHASE 2 COMPLETE - ACCURACY OPTIMIZATION")
        print("="*70)
        print(f"\n📊 Results:")
        print(f"  • Optimized Single Model: {single_accuracy:.4f}")
        print(f"  • Ensemble (3 models): {ensemble_accuracy:.4f}")
        print(f"  • Improvement: +{(ensemble_accuracy - 0.941) *100:.2f}%")
        print(f"\n📁 Models saved:")
        print(f"  • qfinet_accuracy_optimized.h5")
        print(f"  • qfinet_ensemble_model_0.h5, _1.h5, _2.h5")

if __name__ == '__main__':
    optimizer = AccuracyOptimizer()
    optimizer.run_optimization()
