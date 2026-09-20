$ErrorActionPreference = "Stop"

$Repository = "https://github.com/bluetn514/proxylens.git"

Write-Host "ProxyLens GitHub publisher" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed." -ForegroundColor Red
    Write-Host "Install Git for Windows from https://git-scm.com/download/win, then run this file again."
    Read-Host "Press Enter to close"
    exit 1
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing GitHub CLI..."
        winget install --id GitHub.cli --exact --source winget
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    } else {
        Write-Host "GitHub CLI is not installed." -ForegroundColor Red
        Write-Host "Install it from https://cli.github.com, then run this file again."
        Read-Host "Press Enter to close"
        exit 1
    }
}

gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "A GitHub login page will open. Sign in as bluetn514 and approve GitHub CLI."
    gh auth login --hostname github.com --git-protocol https --web
}

gh auth setup-git

if (-not (Test-Path ".git")) {
    git init -b main
}

git config user.name "bluetn514"
git config user.email "bluetn514@users.noreply.github.com"

$existingRemote = git remote 2>$null | Select-String -SimpleMatch "origin"
if ($existingRemote) {
    git remote set-url origin $Repository
} else {
    git remote add origin $Repository
}

git add .
$changes = git status --porcelain
if ($changes) {
    git commit -m "feat: release ProxyLens 0.1.0"
}

git push -u origin main

if (-not (git tag --list "v0.1.0")) {
    git tag -a v0.1.0 -m "ProxyLens 0.1.0"
}
git push origin v0.1.0

Write-Host ""
Write-Host "Published: https://github.com/bluetn514/proxylens" -ForegroundColor Green
Write-Host "GitHub Actions is now building ProxyLens.exe."
Read-Host "Press Enter to close"

