"""
Dagster Pipeline for Indian Railways Sensor Data Generation
Generates synthetic sensor data and exports to CSV for analysis
This file defines the pipeline ops and job that will run in Dagster
"""
from dagster import job, op, graph, Int, Nothing
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path
import os

# ==================== SENSOR DATA GENERATION ====================
def generate_sensor_reading(train_no: int, timestamp: str) -> dict:
    """
    Generate a single sensor reading with realistic parameters
    
    Args:
        train_no: Train identifier
        timestamp: ISO format timestamp
        
    Returns:
        dict: Single sensor data record
    """
    return {
        "Train_Number": train_no,
        "Timestamp": timestamp,
        "Brake_Temperature_C": round(random.uniform(30, 120), 2),
        "Axle_Vibration_mms": round(random.uniform(0.1, 4.0), 2),
        "Wheel_Wear_Percent": round(random.uniform(10, 90), 2),
        "Engine_Load_Percent": round(random.uniform(40, 100), 2),
        "Battery_Voltage_V": round(random.uniform(10.5, 14.5), 2),
        "Fuel_Efficiency_kmL": round(random.uniform(2, 5), 2)
    }

# ==================== DAGSTER OPERATIONS ====================

@op
def fetch_train_list():
    """
    Fetch list of active trains for data generation
    
    Returns:
        list: List of train numbers
    """
    # Sample train numbers
    train_numbers = [10103, 10104, 10111, 10112, 10215, 10216, 
                     10217, 10218, 12345, 12346]
    return train_numbers

@op
def generate_sensor_data(train_numbers: list):
    """
    Generate 100 sensor records across all trains
    Each record contains sensor readings with timestamp
    
    Args:
        train_numbers: List of train numbers to generate data for
        
    Returns:
        list: List of sensor records
    """
    records = []
    base_time = datetime.now() - timedelta(hours=1)
    
    # Generate 100 total records across all trains
    for i in range(100):
        train_no = train_numbers[i % len(train_numbers)]
        timestamp = base_time + timedelta(minutes=i)
        
        record = generate_sensor_reading(
            train_no=train_no,
            timestamp=timestamp.isoformat()
        )
        records.append(record)
    
    return records

@op
def create_dataframe(sensor_records: list):
    """
    Convert sensor records to pandas DataFrame
    
    Args:
        sensor_records: List of sensor data records
        
    Returns:
        pd.DataFrame: DataFrame with sensor data
    """
    df = pd.DataFrame(sensor_records)
    return df

@op
def validate_data(df: pd.DataFrame):
    """
    Validate data quality and integrity
    
    Args:
        df: Input DataFrame
        
    Returns:
        dict: Validation results
    """
    validation_report = {
        "total_records": len(df),
        "timestamp_range": {
            "start": str(df["Timestamp"].min()),
            "end": str(df["Timestamp"].max())
        },
        "unique_trains": int(df["Train_Number"].nunique()),
        "missing_values": df.isnull().sum().to_dict(),
        "column_count": len(df.columns),
        "columns": list(df.columns)
    }
    
    # Print validation summary
    print("\n" + "="*60)
    print("SENSOR DATA VALIDATION REPORT")
    print("="*60)
    print(f"Total Records Generated: {validation_report['total_records']}")
    print(f"Unique Trains: {validation_report['unique_trains']}")
    print(f"Time Range: {validation_report['timestamp_range']['start']} to {validation_report['timestamp_range']['end']}")
    print(f"Data Quality: {'✅ PASSED' if all(v == 0 for v in validation_report['missing_values'].values()) else '⚠️ ISSUES'}")
    print("="*60 + "\n")
    
    return validation_report

@op
def export_to_csv(df: pd.DataFrame):
    """
    Export sensor data to CSV file
    
    Args:
        df: DataFrame to export
        
    Returns:
        str: Path to exported CSV file
    """
    # Create output directory if it doesn't exist
    output_dir = Path("/app/sensor_data") if os.path.exists("/app") else Path(__file__).parent.parent / "sensor_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"sensor_data_{timestamp}.csv"
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Sensor data exported to: {output_file}")
    print(f"   Records: {len(df)}")
    print(f"   Size: {output_file.stat().st_size / 1024:.2f} KB\n")
    
    return str(output_file)

@op
def generate_summary_report(csv_path: str):
    """
    Generate comprehensive summary report
    
    Args:
        csv_path: Path to exported CSV
        
    Returns:
        dict: Summary report
    """
    # Read the CSV to get stats
    df = pd.read_csv(csv_path)
    
    summary = {
        "execution_time": datetime.now().isoformat(),
        "status": "COMPLETED",
        "output_file": csv_path,
        "statistics": {
            "total_records": len(df),
            "unique_trains": int(df["Train_Number"].nunique()),
            "sensor_statistics": {}
        }
    }
    
    # Add statistics for each sensor
    sensor_columns = [col for col in df.columns if col not in ["Train_Number", "Timestamp"]]
    for col in sensor_columns:
        summary["statistics"]["sensor_statistics"][col] = {
            "mean": round(float(df[col].mean()), 2),
            "min": round(float(df[col].min()), 2),
            "max": round(float(df[col].max()), 2),
            "std": round(float(df[col].std()), 2)
        }
    
    return summary

# ==================== DAGSTER JOB ====================

@job
def sensor_data_pipeline():
    """
    Main Dagster job for sensor data generation
    
    Pipeline Flow:
    1. Fetch list of trains
    2. Generate 100 sensor records
    3. Convert to DataFrame
    4. Validate data quality
    5. Export to CSV
    6. Generate summary report
    """
    trains = fetch_train_list()
    records = generate_sensor_data(trains)
    df = create_dataframe(records)
    validation_results = validate_data(df)
    csv_path = export_to_csv(df)
    summary = generate_summary_report(csv_path)

# ==================== EXECUTION ====================

if __name__ == "__main__":
    # Execute the job
    from dagster import execute_job
    
    print("\n" + "="*60)
    print("INDIAN RAILWAYS SENSOR DATA PIPELINE")
    print("="*60)
    print("Starting sensor data generation...\n")
    
    result = execute_job(sensor_data_pipeline)
    
    if result.success:
        print("✅ Pipeline execution completed successfully!")
    else:
        print("❌ Pipeline execution failed!")

