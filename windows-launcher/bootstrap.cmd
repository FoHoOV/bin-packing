@echo off
REM Bootstrap launcher for binpacking application

REM Define URLs for the latest versions of the files.
REM Replace these URLs with the raw URLs from your repository.
set "MAIN_CMD_URL=https://raw.githubusercontent.com/FoHoOV/bin-packing/main/windows-launcher/main.cmd"
set "PS1_URL=https://raw.githubusercontent.com/FoHoOV/bin-packing/main/windows-launcher/binpacking.ps1"

REM Set local filenames
set "LOCAL_MAIN_CMD=main.cmd"
set "LOCAL_PS1=binpacking.ps1"

REM Download the latest main.cmd
echo Downloading latest main.cmd...
powershell -Command "Invoke-WebRequest -Uri '%MAIN_CMD_URL%' -OutFile '%LOCAL_MAIN_CMD%' -UseBasicParsing"

REM Download the latest binpacking.ps1
echo Downloading latest binpacking.ps1...
powershell -Command "Invoke-WebRequest -Uri '%PS1_URL%' -OutFile '%LOCAL_PS1%' -UseBasicParsing"

REM Call the downloaded main.cmd (which in turn runs binpacking.ps1)
echo Running main.cmd...
call %LOCAL_MAIN_CMD%

REM End of bootstrap
pause