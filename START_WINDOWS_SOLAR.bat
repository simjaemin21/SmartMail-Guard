@echo off
cd /d "%~dp0"
if "%UPSTAGE_API_KEY%"=="" (
  echo First set an Upstage API key for this console session:
  echo   set UPSTAGE_API_KEY=YOUR_API_KEY
  echo Then execute START_WINDOWS_SOLAR.bat
  pause
  exit /b 1
)
where py >nul 2>nul && (py -3 app\server.py) || (python app\server.py)
pause
