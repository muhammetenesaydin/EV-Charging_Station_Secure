# PowerShell build script for creating executables using PyInstaller
# Usage: powershell -ExecutionPolicy Bypass -File build_exe.ps1

param(
    [switch]$Clean
)

Write-Host "[BUILD] Starting build process..." -ForegroundColor Cyan

if ($Clean) {
    Write-Host "[CLEAN] Removing previous build artifacts..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
    Get-ChildItem -Filter *.spec | Remove-Item -Force -ErrorAction SilentlyContinue
}

# Ensure dependencies are installed
Write-Host "[STEP] Installing requirements..." -ForegroundColor Cyan
pip install -r requirements.txt

# Build main simulation CLI exe
Write-Host "[STEP] Building simulation executable (main.exe)..." -ForegroundColor Cyan
pyinstaller --name CANSim --onefile --clean main.py

# Build Streamlit UI starter exe
Write-Host "[STEP] Building UI executable (run_ui.exe)..." -ForegroundColor Cyan
pyinstaller --name CANSimUI --onefile --clean run_ui.py

Write-Host "[DONE] Build finished. Executables in 'dist' folder:" -ForegroundColor Green
Get-ChildItem dist
