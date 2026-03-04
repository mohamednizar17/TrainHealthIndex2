 pp#!/bin/bash
# Linux/Mac Setup Script for QFINET Train Health Index
# Creates virtual environment and installs dependencies

echo ""
echo "============================================================"
echo "QFINET Train Health Index - Setup Script"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not found!"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "✅ Python found"
python3 --version

# Create virtual environment
echo ""
echo "🔨 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists, skipping creation"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: pip upgrade may have failed, continuing anyway..."
fi

# Install requirements
echo ""
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed successfully"

# Verify installation
echo ""
echo "✔️  Verifying installation..."
python -c "import tensorflow; import streamlit; import sklearn; print('✅ All packages verified!')"
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Some packages may not be installed correctly"
fi

echo ""
echo "============================================================"
echo "✅ SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "📌 Next Steps:"
echo ""
echo "1. Make sure venv is activated (you should see (venv) in your prompt)"
echo ""
echo "2. Generate training data:"
echo "   python data_generator.py --synthetic"
echo ""
echo "3. Train models (open with Jupyter):"
echo "   jupyter notebook train_model.ipynb"
echo ""
echo "4. Launch dashboard:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "📍 Current virtual environment path:"
echo "   $VIRTUAL_ENV"
echo ""
echo "============================================================"
echo ""
