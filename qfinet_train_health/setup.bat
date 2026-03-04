@echo off
REM Windows Setup Script for QFINET Train Health Index
REM Creates virtual environment and installs dependencies

echo.
echo ============================================================
echo QFINET Train Health Index - Setup Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment
echo.
echo 🔨 Creating virtual environment...
if exist venv (
    echo ⚠️  Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo.
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

REM Upgrade pip
echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ⚠️  Warning: pip upgrade may have failed, continuing anyway...
)

REM Install requirements
echo.
echo 📚 Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully

REM Verify installation
echo.
echo ✔️  Verifying installation...
python -c "import tensorflow; import streamlit; import sklearn; print('✅ All packages verified!')"
if errorlevel 1 (
    echo ⚠️  Warning: Some packages may not be installed correctly
)

echo.
echo ============================================================
echo ✅ SETUP COMPLETE!
echo ============================================================
echo.
echo 📌 Next Steps:
echo.
echo 1. Make sure venv is activated (you should see (venv) in your prompt)
echo.
echo 2. Generate training data:
echo    python data_generator.py --synthetic
echo.
echo 3. Train models (open with Jupyter):
echo    jupyter notebook train_model.ipynb
echo.
echo 4. Launch dashboard:
echo    streamlit run streamlit_app.py
echo.
echo 📍 Current virtual environment path:
echo    %VIRTUAL_ENV%
echo.
echo ============================================================
echo.
pause
