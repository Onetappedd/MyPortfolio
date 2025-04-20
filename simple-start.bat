@echo off
echo ==================================================
echo       SIMPLIFIED PORTFOLIO SYSTEM STARTUP         
echo ==================================================

echo Starting basic services...
docker-compose -f docker-compose-simple.yml up -d

echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo Opening website...
start "" http://localhost:3000

echo To stop the application, run: docker-compose -f docker-compose-simple.yml down