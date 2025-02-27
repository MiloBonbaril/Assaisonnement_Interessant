@echo off
REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Upgrade pip
pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

echo Virtual environment setup complete. To activate it, run "venv\Scripts\activate".