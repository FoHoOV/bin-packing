# ====================================
# Configuration
# ====================================
# URL for the bin-packing repository
$binPackingUrl = "https://github.com/FoHoOV/bin-packing"
$binPackingDir = ".\binpacking"

# Set the CBC version you want to use (use just the version number)
$cbcVersion = "2.10.12"

# Construct the URL and zip file name using the version variable
$cbcURL = "https://github.com/coin-or/Cbc/releases/download/releases/$cbcVersion/Cbc-releases.$cbcVersion-w64-msvc17-md.zip"
$zipFileName = "Cbc-releases.$cbcVersion-w64-msvc17-md.zip"

# Directory where CBC binaries will be stored (each version gets its own folder)
$cbcBinariesRoot = ".\cbc-binaries"
$cbcBinariesDir = "$cbcBinariesRoot\$cbcVersion"

# ====================================
# Ensure the CBC binaries root folder exists
# ====================================
if (!(Test-Path -Path $cbcBinariesRoot)) {
    New-Item -ItemType Directory -Path $cbcBinariesRoot | Out-Null
}

# ====================================
# Download and extract CBC binary if not already present for the current version
# ====================================
if (!(Test-Path -Path $cbcBinariesDir)) {
    Write-Output "Downloading CBC version $cbcVersion..."
    # Download the zip file if it hasn't been downloaded already
    if (!(Test-Path -Path $zipFileName)) {
        Invoke-WebRequest -Uri $cbcURL -OutFile $zipFileName
    }
    # Extract the zip file into the version-specific folder
    Expand-Archive -Path $zipFileName -DestinationPath $cbcBinariesDir -Force
    # Remove the zip file after extraction
    Remove-Item -Path $zipFileName -Force
} else {
    Write-Output "CBC version $cbcVersion already exists. Skipping download."
}

# ====================================
# Update or clone the bin-packing repository
# ====================================
if (!(Test-Path -Path $binPackingDir)) {
    Write-Output "Cloning bin-packing repository..."
    git clone $binPackingUrl $binPackingDir
} else {
    Write-Output "Updating bin-packing repository..."
    Push-Location $binPackingDir
    # Reset any changes (so that the CBC binary update doesn’t show up as a local change)
    git reset --hard
    git pull
    Pop-Location
}

# ====================================
# Copy the CBC binary into the bin-packing folder
# ====================================
# Assuming the zip file extracts to a folder structure like "cbc\bin\cbc.exe"
$sourceCbcExe = Join-Path $cbcBinariesDir "bin"
# Prepend the bin folder to the PATH environment variable for this session
$env:PATH = "$cbcBinPath;" + $env:PATH
Write-Output "Added CBC bin folder to PATH for this session."

# ====================================
# Install Python dependencies and run main.py from the bin-packing folder
# ====================================
Push-Location $binPackingDir
python -m pip install pipenv --user
python -m pipenv install 
python -m pipenv run main.py
Pop-Location

Read-Host -Prompt "Press Enter to exit"
