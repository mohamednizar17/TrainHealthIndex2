@echo off
REM Run QFINET Streamlit Dashboard

echo Starting QFINET Train Health Index Dashboard...
echo.
echo Opening browser to http://localhost:8501
echo.

cd /d "%~dp0"
C:\Users\nizar\Desktop\THI\qfinet_train_health\venv\Scripts\python.exe -m streamlit run streamlit_app.py --client.showErrorDetails=false

pause
