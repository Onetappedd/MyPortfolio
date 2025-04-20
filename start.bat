@echo off
:: Display ASCII art banner
echo ==================================================
echo       PORTFOLIO MANAGEMENT SYSTEM STARTUP         
echo ==================================================

:: Check if Docker is installed
WHERE docker >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed. Please install Docker and try again.
    exit /b 1
)

:: Check if Docker Compose is installed
WHERE docker-compose >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Docker Compose is not installed. Please install Docker Compose and try again.
    exit /b 1
)

echo Starting Portfolio Management Application...

:: Build and start all services
docker-compose up --build -d

:: Wait for services to be ready
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

:: Check if services are running
docker ps -q -f name=portfolio-api >nul 2>nul
SET API_RUNNING=%ERRORLEVEL%
docker ps -q -f name=portfolio-ui >nul 2>nul
SET UI_RUNNING=%ERRORLEVEL%
docker ps -q -f name=portfolio-db >nul 2>nul
SET DB_RUNNING=%ERRORLEVEL%

IF %API_RUNNING% EQU 0 IF %UI_RUNNING% EQU 0 IF %DB_RUNNING% EQU 0 (
    echo ==================================================
    echo  Application started successfully!
    echo ------------------------------------------------
    echo  Frontend: http://localhost:3000
    echo  API: http://localhost:8000
    echo  API Documentation: http://localhost:8000/docs
    echo ------------------------------------------------
    echo  Portfolio Creator: http://localhost:3000/portfolio-creator.html
    echo  Portfolio Dashboard: http://localhost:3000/portfolio-dashboard.html
    echo ==================================================
) ELSE (
    echo Error: Some services failed to start. Check logs with 'docker-compose logs'
    exit /b 1
)

:: Open the application in the default browser
start "" http://localhost:3000

echo To stop the application, run: docker-compose down