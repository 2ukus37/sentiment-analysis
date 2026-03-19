@echo off
echo Loading environment from .env...
for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b
python src/api/app_enhanced.py
