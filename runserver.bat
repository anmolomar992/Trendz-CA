@echo off
echo ==========================================
echo  Royal Cuts Barber Shop - Windows Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo Error: Python is not installed. Please install Python 3.10 or higher.
  exit /b 1
)

REM Get Python version
for /f "tokens=2" %%V in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PY_VERSION=%%V
echo Python version: %PY_VERSION%

REM Check for virtual environment
if exist venv (
  echo Activating virtual environment...
  call venv\Scripts\activate
) else (
  echo No virtual environment found. You may want to create one:
  echo   python -m venv venv
  echo   venv\Scripts\activate
  echo.
)

REM Check for required packages
echo Checking for required Python packages...
for %%P in (django psycopg2 requests dotenv) do (
  python -c "import %%P" >nul 2>&1
  if %errorlevel% neq 0 (
    if "%%P"=="psycopg2" (
      echo Installing psycopg2-binary...
      pip install psycopg2-binary
    ) else if "%%P"=="dotenv" (
      echo Installing python-dotenv...
      pip install python-dotenv
    ) else (
      echo Installing %%P...
      pip install %%P
    )
  ) else (
    echo - %%P is already installed.
  )
)

REM Check for .env file
if not exist .env (
  echo Creating .env file...
  (
    echo # Supabase connection details (required)
    echo SUPABASE_URL=https://phuhhrqzzqdfheuhqofi.supabase.co
    echo SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBodWhocnF6enFkZmhldWhxb2ZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI3NTAyMjEsImV4cCI6MjA1ODMyNjIyMX0.b4KLx3W1wliVO6fgHMaJIqN6vA9F5BMiUFqdD1tmsHo
    echo SUPABASE_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBodWhocnF6enFkZmhldWhxb2ZpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Mjc1MDIyMSwiZXhwIjoyMDU4MzI2MjIxfQ.HBoktk6j1cBqXbuT1wOwUDRsCAwMTDKyXC_qxs7n474
    echo.
    echo # Django settings (optional)
    echo DJANGO_DEBUG=True
    echo DJANGO_SECRET_KEY=django-insecure-q&kzhu^^^6j5%%n#ioc!2nh+9z4!yj-0kbxf+0!0c9_3qt-v3p=j&
    echo DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
    echo DJANGO_CSRF_TRUSTED_ORIGINS=https://*.replit.dev,https://*.replit.app,http://localhost:8000,http://127.0.0.1:8000
    echo.
    echo # Server settings (optional)
    echo PORT=8000
  ) > .env
  echo .env file created.
) else (
  echo .env file already exists.
)

REM Set default port
set PORT=8000
if "%1"=="" (
  for /f "tokens=2 delims==" %%P in ('findstr /i "^PORT=" .env') do set PORT=%%P
) else (
  set PORT=%1
)

echo.
echo Setup complete!
echo Starting Royal Cuts Barber Shop server...
echo.

REM Start the server
cd barbershop
echo Server is running at: http://localhost:%PORT%
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver 0.0.0.0:%PORT%

echo.
echo Server has stopped. Thank you for using Royal Cuts!
pause