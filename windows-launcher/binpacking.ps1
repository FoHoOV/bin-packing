# =====================================================
# Define the Root Directory (one level up from the scripts folder)
# =====================================================
$rootDir = Resolve-Path "$PSScriptRoot\.."

# Now use $rootDir for all relative paths
$binPackingUrl = "https://github.com/FoHoOV/bin-packing"
$binPackingDir = Join-Path $rootDir "binpacking"

# Set the CBC version you want to use (use just the version number)
$cbcVersion = "2.10.12"

# Construct the URL and zip file name using the version variable
$cbcURL = "https://github.com/coin-or/Cbc/releases/download/releases/$cbcVersion/Cbc-releases.$cbcVersion-w64-msvc17-md.zip"
$zipFileName = "Cbc-releases.$cbcVersion-w64-msvc17-md.zip"

# Directory where CBC binaries will be stored (each version gets its own folder)
$cbcBinariesRoot = Join-Path $rootDir "cbc-binaries"
$cbcBinariesDir = Join-Path $cbcBinariesRoot $cbcVersion

# =====================================================
# Ensure the CBC binaries root folder exists
# =====================================================
if (!(Test-Path -Path $cbcBinariesRoot)) {
    New-Item -ItemType Directory -Path $cbcBinariesRoot | Out-Null
}

# =====================================================
# Download and extract CBC binary if not already present for the current version
# =====================================================
if (!(Test-Path -Path $cbcBinariesDir)) {
    Write-Output "Downloading CBC version $cbcVersion..."
    if (!(Test-Path -Path $zipFileName)) {
        Invoke-WebRequest -Uri $cbcURL -OutFile $zipFileName
    }
    Expand-Archive -Path $zipFileName -DestinationPath $cbcBinariesDir -Force
    Remove-Item -Path $zipFileName -Force
} else {
    Write-Output "CBC version $cbcVersion already exists. Skipping download."
}

# =====================================================
# Update or clone the bin-packing repository
# =====================================================
if (!(Test-Path -Path $binPackingDir)) {
    Write-Output "Cloning bin-packing repository..."
    git clone $binPackingUrl $binPackingDir
} else {
    Write-Output "Updating bin-packing repository..."
    Push-Location $binPackingDir
    git reset --hard
    git pull
    Pop-Location
}

# =====================================================
# Ensure config.json exists in the root folder
# =====================================================
$configPath = Join-Path $rootDir "config.json"
if (!(Test-Path -Path $configPath)) {
    Write-Output "config.json not found. Creating a dummy config file..."
    $dummyConfig = @{
        input  = "Path to input CSV file like ./data/somefile.csv"
        output = "Path to output CSV file like ./data/somefile.csv"
        sum    = 0
    }
    $dummyConfig | ConvertTo-Json -Depth 3 | Out-File -Encoding utf8 $configPath
    Write-Error "A dummy config.json has been created at $configPath. Please update it with valid values and re-run the script."
    exit 1
}

# Read configuration (will error out if required fields are missing)
$config = Get-Content $configPath -Raw | ConvertFrom-Json
if (-not $config.input -or -not $config.output -or ($config.sum -eq $null)) {
    Write-Error "config.json is missing one or more required fields: input, output, or sum."
    exit 1
}

# Build command-line arguments from the configuration
$arguments = "--input `"$($config.input)`" --output `"$($config.output)`" --sum $($config.sum)"
Write-Output "Using parameters: $arguments"

# =====================================================
# Prepend the CBC binary bin folder to PATH for the current session
# =====================================================
$cbcBinPath = Join-Path $cbcBinariesDir "bin"
$env:PATH = "$cbcBinPath;" + $env:PATH
Write-Output "Added CBC bin folder ($cbcBinPath) to PATH for this session."

# =====================================================
# Install Python dependencies and run main.py from the bin-packing folder with parameters
# =====================================================
Push-Location $binPackingDir
python -m pip install pipenv --user
python -m pipenv install 
python -m pipenv run main.py $arguments
Pop-Location

Read-Host -Prompt "Press Enter to exit"
