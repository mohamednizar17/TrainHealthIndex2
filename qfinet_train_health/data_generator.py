#!/usr/bin/env python3
"""
Training Data Generator for QFINET Train Health Index Model
Generates labeled sensor data from THI pipeline output
"""

import pandas as pd
import numpy as np
import glob
import os
from pathlib import Path
from datetime import datetime

class THIDataGenerator:
    """Generate training data with THI scores from sensor readings"""
    
    def __init__(self, sensor_data_path="../sensor_data"):
        """
        Initialize data generator
        
        Args:
            sensor_data_path: Path to sensor data CSV files from Dagster pipeline
        """
        self.sensor_data_path = sensor_data_path
        self.df = None
        
    def calculate_thi_score(self, row):
        """
        Calculate Train Health Index (THI) from sensor readings using scientific thresholds
        
        Based on ISO 10816 (vibration), brake temperature limits, and real train diagnostics:
        - 0-30: HEALTHY (all sensors in optimal range)
        - 30-60: WARNING (degradation detected)
        - 60-100: FAULTY (critical issues, requires maintenance)
        
        Args:
            row: Pandas row with sensor readings
            
        Returns:
            float: THI score 0-100 (weighted combination of all sensors)
        """
        
        # Define weighted scoring (total = 100%)
        weights = {
            'brake_temp': 0.25,      # 25% - Critical for safety
            'vibration': 0.25,       # 25% - ISO 10816 standard  
            'wheel_wear': 0.20,      # 20% - Mechanical integrity
            'engine_load': 0.15,     # 15% - Engine strain indicator
            'battery': 0.10,         # 10% - Electrical health
            'fuel_efficiency': 0.05  # 5%  - Engine efficiency
        }
        
        component_scores = {}
        
        # 1. BRAKE TEMPERATURE SCORING (0-100, lower temp = healthier)
        temp = row['Brake_Temperature_C']
        if temp < 40:  # Too cold (unusual, might be sensor issue)
            component_scores['brake_temp'] = 50
        elif 40 <= temp <= 80:  # OPTIMAL range
            component_scores['brake_temp'] = 5
        elif 80 < temp <= 100:  # WARNING zone
            component_scores['brake_temp'] = 40
        else:  # > 100 CRITICAL (brake fade risk, safety issue)
            component_scores['brake_temp'] = 95
        
        # 2. AXLE VIBRATION SCORING (ISO 10816 standard, 0-4 mms range)
        vibration = row['Axle_Vibration_mms']
        if vibration < 0.5:  # Very smooth
            component_scores['vibration'] = 5
        elif 0.5 <= vibration <= 1.0:  # OPTIMAL (new/well-maintained)
            component_scores['vibration'] = 10
        elif 1.0 < vibration <= 1.8:  # ACCEPTABLE (minor wear)
            component_scores['vibration'] = 35
        elif 1.8 < vibration <= 2.5:  # WARNING (ISO zone C - needs attention soon)
            component_scores['vibration'] = 60
        else:  # > 2.5 CRITICAL (ISO zone D - shutdown required)
            component_scores['vibration'] = 95
        
        # 3. WHEEL WEAR SCORING (0-100%)
        wheel_wear = row['Wheel_Wear_Percent']
        if wheel_wear < 30:  # New/minimal wear
            component_scores['wheel_wear'] = 5
        elif 30 <= wheel_wear <= 50:  # OPTIMAL operating range
            component_scores['wheel_wear'] = 15
        elif 50 < wheel_wear <= 70:  # WARNING (planned replacement soon)
            component_scores['wheel_wear'] = 50
        else:  # > 70 CRITICAL (immediate replacement needed)
            component_scores['wheel_wear'] = 90
        
        # 4. ENGINE LOAD SCORING (30-100%)
        load = row['Engine_Load_Percent']
        if 50 <= load <= 80:  # OPTIMAL operating range  
            component_scores['engine_load'] = 10
        elif 40 <= load < 50 or 80 < load <= 90:  # Acceptable margins
            component_scores['engine_load'] = 30
        elif load < 40 or 90 < load <= 95:  # WARNING zone (overwork risk)
            component_scores['engine_load'] = 55
        else:  # > 95 CRITICAL (engine strain, overheating risk)
            component_scores['engine_load'] = 85
        
        # 5. BATTERY VOLTAGE SCORING (10.5-14.5V range)
        battery = row['Battery_Voltage_V']
        if 12.5 <= battery <= 14.0:  # OPTIMAL operating range
            component_scores['battery'] = 5
        elif 12.0 <= battery < 12.5 or 14.0 < battery <= 14.2:  # Acceptable
            component_scores['battery'] = 20
        elif 11.5 <= battery < 12.0 or 14.2 < battery <= 14.5:  # WARNING
            component_scores['battery'] = 50
        else:  # < 11.5 or > 14.5 CRITICAL
            component_scores['battery'] = 90
        
        # 6. FUEL EFFICIENCY SCORING (kmL)
        fuel = row['Fuel_Efficiency_kmL']
        if fuel > 3.5:  # OPTIMAL efficiency
            component_scores['fuel_efficiency'] = 5
        elif 3.0 <= fuel <= 3.5:  # Good efficiency
            component_scores['fuel_efficiency'] = 15
        elif 2.5 <= fuel < 3.0:  # WARNING (10-15% worse than baseline)
            component_scores['fuel_efficiency'] = 40
        else:  # < 2.5 CRITICAL (engine problem indicator)
            component_scores['fuel_efficiency'] = 80
        
        # Calculate weighted THI score
        thi_score = sum(component_scores[k] * weights[k] for k in weights.keys())
        
        return round(thi_score, 2)
    
    def get_thi_class(self, thi_score):
        """
        Convert THI score to class label based on train health thresholds
        
        Args:
            thi_score: THI score 0-100
            
        Returns:
            str: Class label (Healthy, Warning, Faulty)
        """
        if thi_score < 30:
            return "Healthy"      # All sensors in good condition
        elif thi_score < 60:
            return "Warning"      # Degradation detected, maintenance recommended
        else:
            return "Faulty"       # Critical issues, immediate maintenance required
    
    def load_sensor_data(self):
        """
        Load all sensor data from CSV files
        
        Returns:
            pd.DataFrame: Combined sensor data
        """
        print(f"🔍 Looking for sensor data in: {self.sensor_data_path}")
        
        csv_files = glob.glob(os.path.join(self.sensor_data_path, "*.csv"))
        
        if not csv_files:
            print(f"⚠️  No CSV files found in {self.sensor_data_path}")
            print("   Make sure Dagster pipeline has generated data:")
            print("   Run: docker-compose up")
            print("   Then: Go to http://localhost:3000 → Launch Run")
            return None
        
        print(f"📂 Found {len(csv_files)} CSV files")
        
        # Load all CSVs
        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                print(f"   ✅ Loaded: {Path(csv_file).name} ({len(df)} records)")
                dfs.append(df)
            except Exception as e:
                print(f"   ❌ Error loading {csv_file}: {e}")
        
        if not dfs:
            return None
        
        # Combine all data
        self.df = pd.concat(dfs, ignore_index=True)
        print(f"\n✅ Total records: {len(self.df)}")
        
        return self.df
    
    def generate_training_data(self, output_path="training_data.csv"):
        """
        Generate labeled training data
        
        Args:
            output_path: Where to save the training data CSV
            
        Returns:
            pd.DataFrame: Training data with THI score and class label
        """
        if self.df is None:
            self.load_sensor_data()
        
        if self.df is None or len(self.df) == 0:
            print("❌ No data to process")
            return None
        
        print("\n📊 Calculating THI scores...")
        
        # Calculate THI score for each row
        self.df['THI_Score'] = self.df.apply(self.calculate_thi_score, axis=1)
        self.df['THI_Class'] = self.df['THI_Score'].apply(self.get_thi_class)
        
        # Print statistics
        print("\n📈 THI Score Statistics:")
        print(f"   Min: {self.df['THI_Score'].min():.2f}")
        print(f"   Max: {self.df['THI_Score'].max():.2f}")
        print(f"   Mean: {self.df['THI_Score'].mean():.2f}")
        print(f"   Std: {self.df['THI_Score'].std():.2f}")
        
        print("\n📋 Class Distribution:")
        class_counts = self.df['THI_Class'].value_counts()
        for cls, count in class_counts.items():
            pct = (count / len(self.df)) * 100
            print(f"   {cls}: {count} ({pct:.1f}%)")
        
        # Select only sensor columns + THI output (exclude Train_Number and Timestamp)
        feature_cols = ['Brake_Temperature_C', 'Axle_Vibration_mms', 'Wheel_Wear_Percent', 
                       'Engine_Load_Percent', 'Battery_Voltage_V', 'Fuel_Efficiency_kmL',
                       'THI_Score', 'THI_Class']
        training_df = self.df[feature_cols]
        
        # Save to CSV
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        training_df.to_csv(output_path, index=False)
        print(f"\n✅ Training data saved to: {output_path}")
        print(f"   Shape: {training_df.shape}")
        print(f"   Columns: {list(training_df.columns)}")
        
        return training_df
    
    def generate_synthetic_data(self, num_samples=1000, output_path="training_data_synthetic.csv"):
        """
        Generate synthetic sensor data if no real data available
        
        Args:
            num_samples: Number of samples to generate
            output_path: Where to save the data
            
        Returns:
            pd.DataFrame: Synthetic training data
        """
        print(f"\n🔮 Generating {num_samples} synthetic sensor readings...")
        
        # Generate synthetic data
        data = {
            'Train_Number': np.random.randint(10000, 20000, num_samples),
            'Timestamp': pd.date_range(start='2024-01-01', periods=num_samples, freq='5min'),
            'Brake_Temperature_C': np.random.normal(60, 15, num_samples),
            'Axle_Vibration_mms': np.random.normal(1.2, 0.5, num_samples),
            'Wheel_Wear_Percent': np.random.normal(45, 20, num_samples),
            'Engine_Load_Percent': np.random.normal(65, 15, num_samples),
            'Battery_Voltage_V': np.random.normal(13.2, 0.8, num_samples),
            'Fuel_Efficiency_kmL': np.random.normal(3.5, 0.8, num_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Clip values to realistic ranges
        df['Brake_Temperature_C'] = df['Brake_Temperature_C'].clip(20, 120)
        df['Axle_Vibration_mms'] = df['Axle_Vibration_mms'].clip(0.1, 4.0)
        df['Wheel_Wear_Percent'] = df['Wheel_Wear_Percent'].clip(10, 90)
        df['Engine_Load_Percent'] = df['Engine_Load_Percent'].clip(30, 100)
        df['Battery_Voltage_V'] = df['Battery_Voltage_V'].clip(10.5, 14.5)
        df['Fuel_Efficiency_kmL'] = df['Fuel_Efficiency_kmL'].clip(1.5, 5.0)
        
        # Calculate THI
        print("   📊 Calculating THI scores...")
        df['THI_Score'] = df.apply(self.calculate_thi_score, axis=1)
        df['THI_Class'] = df['THI_Score'].apply(self.get_thi_class)
        
        # Print statistics
        print("\n📈 Synthetic Data Statistics:")
        print(f"   Min THI: {df['THI_Score'].min():.2f}")
        print(f"   Max THI: {df['THI_Score'].max():.2f}")
        print(f"   Mean THI: {df['THI_Score'].mean():.2f}")
        
        print("\n📋 Class Distribution:")
        class_counts = df['THI_Class'].value_counts()
        for cls, count in class_counts.items():
            pct = (count / len(df)) * 100
            print(f"   {cls}: {count} ({pct:.1f}%)")
        
        # Select only sensor columns + THI output (exclude Train_Number and Timestamp)
        feature_cols = ['Brake_Temperature_C', 'Axle_Vibration_mms', 'Wheel_Wear_Percent', 
                       'Engine_Load_Percent', 'Battery_Voltage_V', 'Fuel_Efficiency_kmL',
                       'THI_Score', 'THI_Class']
        training_df = df[feature_cols]
        
        # Save
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        training_df.to_csv(output_path, index=False)
        print(f"\n✅ Synthetic data saved to: {output_path}")
        print(f"   Shape: {training_df.shape}")
        print(f"   Columns: {list(training_df.columns)}")
        
        return training_df


def main():
    """Generate training data"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate training data for QFINET model')
    parser.add_argument('--synthetic', action='store_true', help='Generate synthetic data instead')
    parser.add_argument('--samples', type=int, default=1000, help='Number of synthetic samples')
    parser.add_argument('--output', type=str, default='training_data.csv', help='Output file path')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("QFINET TRAINING DATA GENERATOR")
    print("="*60)
    
    generator = THIDataGenerator()
    
    if args.synthetic:
        generator.generate_synthetic_data(
            num_samples=args.samples,
            output_path=args.output
        )
    else:
        # Try to load real data first
        if generator.load_sensor_data() is not None:
            generator.generate_training_data(output_path=args.output)
        else:
            print("\n⚠️  No real sensor data found.")
            print("   Generating synthetic data instead...")
            generator.generate_synthetic_data(
                num_samples=args.samples,
                output_path=args.output
            )
    
    print("\n" + "="*60)
    print("✅ Data generation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
