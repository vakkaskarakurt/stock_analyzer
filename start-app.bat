@echo off
echo ==========================================
echo   Starting Stock Analyzer (Full Stack)
echo ==========================================

echo 1. Launching Backend (ASP.NET Core)...
start "StockAnalyzer Backend" cmd /k "cd Backend\StockAnalyzer.Api && dotnet run"

echo 2. Launching Frontend (Angular)...
start "StockAnalyzer Frontend" cmd /k "cd Frontend && npm start"

echo ==========================================
echo   Both services are starting...
echo   Backend will be at: http://localhost:5035
echo   Frontend will be at: http://localhost:4200
echo ==========================================
