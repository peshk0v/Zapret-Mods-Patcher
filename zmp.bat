@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Zapret Modifications Patcher

echo.
echo  ====================================
echo    Zapret Modifications Patcher
echo          by peshk0v
echo  ====================================
echo.

set "MOD_PATH="
set "ZAPRET_PATH="

if not "%~1"=="" (
    set "MOD_PATH=%~1"
    for %%I in ("%~dp1.") do set "PARENT_DIR=%%~fI"

    echo  Archive: !MOD_PATH!
    echo.

    set "ARCH_FOUND=0"
    if exist "!PARENT_DIR!\bin" if exist "!PARENT_DIR!\lists" if exist "!PARENT_DIR!\utils" set "ARCH_FOUND=1"
    if "!ARCH_FOUND!"=="0" (
        if exist "!PARENT_DIR!\src" if exist "!PARENT_DIR!\custom-strategies" if exist "!PARENT_DIR!\user-lists" set "ARCH_FOUND=1"
    )

    if "!ARCH_FOUND!"=="1" (
        set "ZAPRET_PATH=!PARENT_DIR!"
        echo  Found Zapret in: !ZAPRET_PATH!
    ) else (
        for %%I in ("%~dp0.") do set "SELF_DIR=%%~fI"
        set "SELF_FOUND=0"
        if exist "!SELF_DIR!\bin" if exist "!SELF_DIR!\lists" if exist "!SELF_DIR!\utils" set "SELF_FOUND=1"
        if "!SELF_FOUND!"=="0" (
            if exist "!SELF_DIR!\src" if exist "!SELF_DIR!\custom-strategies" if exist "!SELF_DIR!\user-lists" set "SELF_FOUND=1"
        )
        if "!SELF_FOUND!"=="1" (
            set "ZAPRET_PATH=!SELF_DIR!"
            echo  Found Zapret in: !ZAPRET_PATH!
        ) else (
            echo  Archive is not in a Zapret folder.
            echo.
            set /p "ZAPRET_PATH=  Enter path to Zapret folder: "
        )
    )
) else (
    for %%I in ("%~dp0.") do set "SELF_DIR=%%~fI"

    set "SELF_FOUND=0"
    if exist "!SELF_DIR!\bin" if exist "!SELF_DIR!\lists" if exist "!SELF_DIR!\utils" set "SELF_FOUND=1"
    if "!SELF_FOUND!"=="0" (
        if exist "!SELF_DIR!\src" if exist "!SELF_DIR!\custom-strategies" if exist "!SELF_DIR!\user-lists" set "SELF_FOUND=1"
    )

    if "!SELF_FOUND!"=="1" (
        set "ZAPRET_PATH=!SELF_DIR!"
        echo  Found Zapret in: !ZAPRET_PATH!
        echo.
        set /p "MOD_PATH=  Enter path to mod archive (.zip): "
    ) else (
        set /p "ZAPRET_PATH=  Enter path to Zapret folder: "
        if "!ZAPRET_PATH!"=="" (
            echo  ERROR: No path entered.
            pause
            exit /b 1
        )
        echo.
        set /p "MOD_PATH=  Enter path to mod archive (.zip): "
    )
)

echo.

if "!ZAPRET_PATH!"=="" (
    echo  ERROR: Zapret path is empty.
    pause
    exit /b 1
)
if "!MOD_PATH!"=="" (
    echo  ERROR: Mod archive path is empty.
    pause
    exit /b 1
)

set "ZAPRET_PATH=!ZAPRET_PATH:"=!"
set "MOD_PATH=!MOD_PATH:"=!"

if not exist "!ZAPRET_PATH!" (
    echo  ERROR: Zapret folder not found: !ZAPRET_PATH!
    pause
    exit /b 1
)
if not exist "!MOD_PATH!" (
    echo  ERROR: Mod archive not found: !MOD_PATH!
    pause
    exit /b 1
)

set "ARCH="
set "LISTS_DIR="
set "BATS_DIR="

if exist "!ZAPRET_PATH!\bin" if exist "!ZAPRET_PATH!\lists" if exist "!ZAPRET_PATH!\utils" (
    set "ARCH=Flowseal"
    set "LISTS_DIR=!ZAPRET_PATH!\lists"
    set "BATS_DIR=!ZAPRET_PATH!"
)

if "!ARCH!"=="" (
    if exist "!ZAPRET_PATH!\src" if exist "!ZAPRET_PATH!\custom-strategies" if exist "!ZAPRET_PATH!\user-lists" (
        set "ARCH=Sergeydigl3"
        set "LISTS_DIR=!ZAPRET_PATH!\user-lists"
        set "BATS_DIR=!ZAPRET_PATH!\custom-strategies"
    )
)

if "!ARCH!"=="" (
    echo  ERROR: Could not determine Zapret architecture.
    echo  Make sure the path points to a valid Zapret installation.
    pause
    exit /b 1
)

echo  Architecture: !ARCH!
echo.

set "MOD_DIR=!ZAPRET_PATH!\mod"
if exist "!MOD_DIR!" rmdir /s /q "!MOD_DIR!"
mkdir "!MOD_DIR!" >nul 2>&1

echo  Extracting...
powershell -NoProfile -Command "Expand-Archive -LiteralPath '!MOD_PATH!' -DestinationPath '!MOD_DIR!' -Force" 2>nul
if errorlevel 1 (
    echo  ERROR: Failed to extract archive.
    if exist "!MOD_DIR!" rmdir /s /q "!MOD_DIR!"
    pause
    exit /b 1
)

set "PLIST=!LISTS_DIR!"
set "PBATS=!BATS_DIR!"

echo  Applying mod...
call :process_mod "!MOD_DIR!"

if exist "!MOD_DIR!" rmdir /s /q "!MOD_DIR!"

echo.
echo  ====================================
echo    Mod successfully installed!
echo    Architecture: !ARCH!
echo  ====================================
echo.
pause
exit /b 0

:process_mod
set "_mod=%~1"
for /r "%_mod%" %%f in (*.txt) do (
    set "_name=%%~nxf"
    if exist "%PLIST%\!_name!" (
        echo    Appending: !_name!
        echo. >> "%PLIST%\!_name!"
        type "%%f" >> "%PLIST%\!_name!"
    )
)
for /r "%_mod%" %%f in (*.bat) do (
    echo    Moving: %%~nxf
    move /y "%%f" "%PBATS%\" >nul 2>&1
)
for /r "%_mod%" %%f in (*.cmd) do (
    echo    Moving: %%~nxf
    move /y "%%f" "%PBATS%\" >nul 2>&1
)
for /r "%_mod%" %%f in (*.sh) do (
    echo    Moving: %%~nxf
    move /y "%%f" "%PBATS%\" >nul 2>&1
)
goto :eof
