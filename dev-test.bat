@echo off
echo ==========================================
echo   Starting Stock Analyzer (Unified Log)
echo   Press Ctrl+C to stop both services.
echo ==========================================

npx concurrently -k --names "BACKEND,FRONTEND" --prefix-colors "blue,magenta" "cd Backend\StockAnalyzer.Api && dotnet run" "cd Frontend && npm start"