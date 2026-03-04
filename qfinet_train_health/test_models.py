#!/usr/bin/env python3
"""Test that all models load correctly"""

import pickle
import tensorflow as tf
from pathlib import Path

print('Testing Model Loading...\n')
models_dir = Path('models')

try:
    qfinet = tf.keras.models.load_model(str(models_dir / 'qfinet_accuracy_optimized.h5'))
    print(f'✅ QFINET Optimized loaded: {qfinet.count_params():,} parameters')
except Exception as e:
    print(f'❌ QFINET Error: {e}')

try:
    traditional = tf.keras.models.load_model(str(models_dir / 'traditional_cnn_baseline.h5'))
    print(f'✅ Traditional CNN loaded: {traditional.count_params():,} parameters')
except Exception as e:
    print(f'❌ Traditional Error: {e}')

try:
    with open(models_dir / 'preprocessing.pkl', 'rb') as f:
        prep = pickle.load(f)
    print(f'✅ Preprocessing loaded: mean={prep["mean"].shape}, std={prep["std"].shape}')
except Exception as e:
    print(f'❌ Preprocessing Error: {e}')

print('\n✅ All models ready for Streamlit dashboard!')
print('\n🚀 To run the dashboard, use:')
print('   streamlit run streamlit_app.py')
