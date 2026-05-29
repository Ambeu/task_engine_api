$root = $PSScriptRoot

Write-Host "=== Task Engine ===" -ForegroundColor Cyan

# Lance le worker dans une nouvelle fenetre PowerShell
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$root'; Write-Host '[ WORKER ]' -ForegroundColor Yellow; .\.venv\Scripts\celery -A celery_app worker --loglevel=info --pool=solo"
)

Start-Sleep -Milliseconds 1500

# Lance l'API dans la fenetre courante
Write-Host "API  -> http://localhost:8000" -ForegroundColor Green
Write-Host "Docs -> http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
.\.venv\Scripts\uvicorn api.main:app --reload --port 8000
