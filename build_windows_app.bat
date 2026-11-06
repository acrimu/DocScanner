@echo off
setlocal

rem Always run from the project directory, even when launched by double-click.
cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :python_found
)

where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_found
)

echo.
echo Python 3 was not found.
echo Install Python from https://www.python.org/downloads/ and try again.
goto :error

:python_found
if not exist ".build-venv\Scripts\python.exe" (
    %PYTHON_CMD% -m venv ".build-venv"
    if errorlevel 1 goto :error
)

".build-venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

".build-venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :error

".build-venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "Document Perspective Scanner" ^
    --collect-all tkinterdnd2 ^
    doc_scanner.py
if errorlevel 1 goto :error

echo.
echo Build complete: dist\Document Perspective Scanner\Document Perspective Scanner.exe
pause
endlocal
exit /b 0

:error
echo.
echo The Windows app build failed. Review the error above and try again.
pause
endlocal
exit /b 1
