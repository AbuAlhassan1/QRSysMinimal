Set objShell = CreateObject("WScript.Shell")
objShell.Run "powershell -WindowStyle Hidden -NoExit -Command "".\venv\Scripts\activate; uvicorn main:app --host 127.0.0.1 --port 8000""", 0, False