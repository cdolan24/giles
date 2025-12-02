# Reinstall backend dependencies
Write-Host "Installing backend dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt

# Reinstall frontend dependencies
Write-Host "Installing frontend dependencies..."
cd frontend
npm install
cd ..


# Start backend and frontend in separate PowerShell windows (fallback)
Write-Host "Starting backend and frontend in separate PowerShell windows..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; ..\.venv\Scripts\python.exe app.py" -WindowStyle Normal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start" -WindowStyle Normal

Write-Host "To load the browser extension:"
Write-Host "1. Open Chrome/Edge and go to chrome://extensions"
Write-Host "2. Enable Developer mode"
Write-Host "3. Click 'Load unpacked' and select the 'extension' folder"