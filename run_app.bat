@echo off
setlocal

rem Always run from the project directory, even when launched by double-click.
cd /d "%~dp0"

set "PYTHON_CMD="

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
    goto :run
)

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :run
)

where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :run
)

echo.
echo Python 3 was not found.
echo Install Python from https://www.python.org/downloads/ and try again.
goto :error

:run
%PYTHON_CMD% "doc_scanner.py"
if errorlevel 1 (
    echo.
    echo Document Perspective Scanner could not start.
    echo Install the required packages with:
    echo   %PYTHON_CMD% -m pip install -r requirements.txt
    goto :error
)

endlocal
exit /b 0

:error
echo.
pause
endlocal
exit /b 1
