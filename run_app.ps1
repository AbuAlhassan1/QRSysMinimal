# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run application
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload 