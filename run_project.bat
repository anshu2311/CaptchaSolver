@echo off
echo  Setting up the project...

:: Step 1 - Create virtual environment
python -m venv venv
call venv\Scripts\activate

:: Step 2 - Install requirements
echo  Installing dependencies...
pip install -r requirements.txt

:: Step 3 - Start Flask server (in new window)
start cmd /k "cd /d %cd% && call venv\Scripts\activate && python gate.py"

:: Step 4 - Give server time to start
timeout /t 5 > nul

:: Step 5 - Run auto login script
echo  Running  login script...


pause
