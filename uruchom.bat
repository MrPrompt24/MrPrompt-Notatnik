@echo off
setlocal EnableDelayedExpansion
title MrPrompt Notatnik

set "PY="

REM 1. Sprawdz bezposrednia sciezke do Python 3.13 w AppData
if exist "%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe" (
    set "PY=%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe"
    goto :found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :found
)

REM 2. Sprawdz inne wersje Pythona w AppData
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\pythonw.exe" (
        set "PY=%%D\pythonw.exe"
        goto :found
    )
    if exist "%%D\python.exe" (
        set "PY=%%D\python.exe"
        goto :found
    )
)

REM 3. Sprawdz launcher pyw / py
where pyw >nul 2>&1
if not errorlevel 1 (
    set "PY=pyw"
    goto :found
)
where py >nul 2>&1
if not errorlevel 1 (
    set "PY=py"
    goto :found
)

REM 4. Sprawdz pythonw / python w PATH
where pythonw >nul 2>&1
if not errorlevel 1 (
    set "PY=pythonw"
    goto :found
)
where python >nul 2>&1
if not errorlevel 1 (
    set "PY=python"
    goto :found
)

:notfound
echo.
echo  [UWAGA] Do dzialania MrPrompt Notatnik potrzebny jest Python,
echo  a nie znaleziono go na tym komputerze.
echo.
echo  Za chwile otworzy sie strona pobierania Pythona:
echo      https://www.python.org/downloads/windows/
echo.
echo  1. Pobierz i zainstaluj Pythona (zaznacz "Add python.exe to PATH").
echo  2. Uruchom ten plik (uruchom.bat) ponownie.
echo.
start "" "https://www.python.org/downloads/windows/"
pause
exit /b 1

:found
cd /d "%~dp0"

REM Jednorazowo: doinstaluj wymagane biblioteki, jesli ich brakuje
set "PYC=!PY:pythonw=python!"
if /i "!PYC!"=="pyw" set "PYC=py"
"!PYC!" -c "import PIL, spylls, tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo Instaluje wymagane biblioteki ^(jednorazowo^)...
    "!PYC!" -m pip install -r "%~dp0requirements.txt"
)

start "" "!PY!" "%~dp0main.py" %*
exit /b 0
