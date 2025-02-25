@echo off
REM Bootstrap launcher for the bin-packing application

REM Define folder for launcher scripts
set "scriptsFolder=scripts"

REM Create the scripts folder if it doesn't exist
if not exist "%scriptsFolder%" (
    mkdir "%scriptsFolder%"
)

REM Define URLs for the latest main.cmd and binpacking.ps1 files.
set "MAIN_CMD_URL=https://raw.githubusercontent.com/FoHoOV/bin-packing/refs/heads/main/windows-launcher/main.cmd"
set "PS1_URL=https://raw.githubusercontent.com/FoHoOV/bin-packing/refs/heads/main/windows-launcher/binpacking.ps1"

REM Set local file paths in the scripts folder
set "LOCAL_MAIN_CMD=%scriptsFolder%\main.cmd"
set "LOCAL_PS1=%scriptsFolder%\binpacking.ps1"

REM Download the latest main.cmd
echo Downloading latest main.cmd...
powershell -Command "Invoke-WebRequest -Uri '%MAIN_CMD_URL%' -OutFile '%LOCAL_MAIN_CMD%' -UseBasicParsing"

REM Download the latest binpacking.ps1
echo Downloading latest binpacking.ps1...
powershell -Command "Invoke-WebRequest -Uri '%PS1_URL%' -OutFile '%LOCAL_PS1%' -UseBasicParsing"

REM Call the downloaded main.cmd from the scripts folder
echo Running main.cmd...
call "%LOCAL_MAIN_CMD%"

pause
