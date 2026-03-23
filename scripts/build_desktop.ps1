param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if ($Clean) {
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
}

Write-Host "[1/3] Installing dependencies..."
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip." }

python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements." }

Write-Host "[2/3] Building desktop app with PyInstaller..."
python -m PyInstaller tiktok_game.spec --clean
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

Write-Host "[3/3] Build completed."
Write-Host "Output file: dist\\PUSH-BATTLE.exe"
