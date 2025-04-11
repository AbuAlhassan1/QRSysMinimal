# QR System

A web application built with FastAPI for QR code management.

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- PowerShell

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd QRSys
   ```

2. Run the setup script to create a virtual environment and install dependencies:
   ```
   .\setup_env.ps1
   ```

This script will:
- Create a Python virtual environment in the `venv` directory
- Activate the virtual environment
- Install all required packages from `requirements.txt`

## Running the Application

To start the application, run:
```
.\run_app.ps1
```

This will:
- Activate the virtual environment
- Start the application with Uvicorn at http://127.0.0.1:8000

Once running, you can access:
- API documentation at http://127.0.0.1:8000/docs
- Admin dashboard at http://127.0.0.1:8000/admin

## Manual Setup (without scripts)

If you prefer to set up manually:

1. Create and activate virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ``` 