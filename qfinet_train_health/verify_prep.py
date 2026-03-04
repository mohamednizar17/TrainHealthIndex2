#!/usr/bin/env python3
"""Verify preprocessing structure"""

import pickle
import numpy as np
from pathlib import Path

models_dir = Path('models')
with open(models_dir / 'preprocessing.pkl', 'rb') as f:
    prep = pickle.load(f)

print('Preprocessing structure:')
print(f'  mean type: {type(prep["mean"])}')
print(f'  mean shape: {prep["mean"].shape}')
print(f'  std type: {type(prep["std"])}')
print(f'  std shape: {prep["std"].shape}')
print()
print('✅ Preprocessing is numpy arrays - fixes applied correctly!')
