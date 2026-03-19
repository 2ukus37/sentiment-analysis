@echo off
echo ========================================
echo Tesseract OCR Installation Helper
echo ========================================
echo.

echo Step 1: Checking if Tesseract is already installed...
tesseract --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Tesseract is already installed!
    tesseract --version
    echo.
    goto :install_python
) else (
    echo [!] Tesseract not found in PATH
    echo.
)

echo Step 2: Download and Install Tesseract
echo.
echo Please follow these steps:
echo 1. Download Tesseract from:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 2. Run the installer (tesseract-ocr-w64-setup-*.exe)
echo.
echo 3. During installation:
echo    - Note the installation path (usually C:\Program Files\Tesseract-OCR)
echo    - Check "Add to PATH" if available
echo.
echo 4. After installation, close this window and open a NEW command prompt
echo.
echo Opening download page in browser...
start https://github.com/UB-Mannheim/tesseract/wiki
echo.
pause
goto :end

:install_python
echo Step 3: Installing Python package (pytesseract)...
pip install pytesseract
if %errorlevel% == 0 (
    echo [OK] pytesseract installed successfully!
) else (
    echo [!] Failed to install pytesseract
    echo Try manually: pip install pytesseract
)
echo.

echo Step 4: Verifying installation...
python -c "import pytesseract; print('Python package OK')" 2>nul
if %errorlevel% == 0 (
    echo [OK] Python package verified!
) else (
    echo [!] Python package not found
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your terminal/command prompt
echo 2. Restart the Flask server
echo 3. Try uploading an image at http://localhost:5000
echo.
echo If you still have issues, see INSTALL_TESSERACT_GUIDE.md
echo.
pause

:end
