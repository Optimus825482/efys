# EFYS - GitHub'a Push Script (PowerShell)
# Kullanım: .\PUSH_TO_GITHUB.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EFYS → GitHub Push & Auto-Deploy" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Renk tanımları
$success = "Green"
$error = "Red"
$warning = "Yellow"
$info = "Cyan"

# Git kurulu mu kontrol et
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git bulunamadı! Git kurmanız gerekiyor." -ForegroundColor $error
    Write-Host "İndirin: https://git-scm.com/download/win" -ForegroundColor $warning
    exit 1
}

Write-Host "✅ Git kurulu" -ForegroundColor $success

# Repository klasöründe miyiz?
if (!(Test-Path ".git")) {
    Write-Host "📁 Git repository başlatılıyor..." -ForegroundColor $info
    git init
    git branch -M main
    Write-Host "✅ Git repository başlatıldı" -ForegroundColor $success
}

# Remote repository kontrolü
$remote = git remote get-url origin 2>$null
if (!$remote) {
    Write-Host "🔗 Remote repository ekleniyor..." -ForegroundColor $info
    git remote add origin https://github.com/Optimus825482/efys.git
    Write-Host "✅ Remote repository eklendi" -ForegroundColor $success
} elseif ($remote -ne "https://github.com/Optimus825482/efys.git") {
    Write-Host "⚠️  Remote repository farklı: $remote" -ForegroundColor $warning
    Write-Host "🔄 Remote repository güncelleniyor..." -ForegroundColor $info
    git remote set-url origin https://github.com/Optimus825482/efys.git
    Write-Host "✅ Remote repository güncellendi" -ForegroundColor $success
}

# Git status
Write-Host ""
Write-Host "📊 Değişiklikler:" -ForegroundColor $info
git status --short

# Commit message
Write-Host ""
$commitMessage = Read-Host "💬 Commit mesajı (boş bırakırsanız otomatik oluşturulur)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "Update: EFYS - $timestamp"
}

# Git add
Write-Host ""
Write-Host "📦 Değişiklikler stage'e alınıyor..." -ForegroundColor $info
git add .
Write-Host "✅ Tüm değişiklikler eklendi" -ForegroundColor $success

# Git commit
Write-Host ""
Write-Host "💾 Commit yapılıyor..." -ForegroundColor $info
git commit -m "$commitMessage"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit başarılı" -ForegroundColor $success
} else {
    Write-Host "⚠️  Commit oluşturulamadı (değişiklik yok olabilir)" -ForegroundColor $warning
}

# Git push
Write-Host ""
Write-Host "🚀 GitHub'a push yapılıyor..." -ForegroundColor $info
Write-Host "Repository: https://github.com/Optimus825482/efys.git" -ForegroundColor $info
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  ✅ PUSH BAŞARILI!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Sonraki Adımlar:" -ForegroundColor $info
    Write-Host ""
    Write-Host "1️⃣  GitHub Actions'ı izleyin:" -ForegroundColor White
    Write-Host "   https://github.com/Optimus825482/efys/actions" -ForegroundColor $warning
    Write-Host ""
    Write-Host "2️⃣  Deployment loglarını takip edin" -ForegroundColor White
    Write-Host "   GitHub → Actions → Latest workflow run" -ForegroundColor $warning
    Write-Host ""
    Write-Host "3️⃣  Deployment tamamlandığında site kontrolü:" -ForegroundColor White
    Write-Host "   https://yourdomain.com" -ForegroundColor $warning
    Write-Host ""
    Write-Host "⏱️  Tahmini deployment süresi: 2-3 dakika" -ForegroundColor $info
    Write-Host ""
    
    # GitHub Actions sayfasını aç (opsiyonel)
    $openBrowser = Read-Host "GitHub Actions sayfasını tarayıcıda açmak ister misiniz? (E/H)"
    if ($openBrowser -eq "E" -or $openBrowser -eq "e") {
        Start-Process "https://github.com/Optimus825482/efys/actions"
    }
    
} else {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "  ❌ PUSH BAŞARISIZ!" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔍 Olası Nedenler:" -ForegroundColor $warning
    Write-Host "1. GitHub authentication gerekiyor" -ForegroundColor White
    Write-Host "2. Repository'e yazma izniniz yok" -ForegroundColor White
    Write-Host "3. İnternet bağlantısı yok" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Çözüm:" -ForegroundColor $info
    Write-Host "git config --global user.name 'Your Name'" -ForegroundColor $warning
    Write-Host "git config --global user.email 'your.email@example.com'" -ForegroundColor $warning
    Write-Host ""
    Write-Host "🔐 GitHub Personal Access Token gerekebilir:" -ForegroundColor $info
    Write-Host "https://github.com/settings/tokens" -ForegroundColor $warning
    Write-Host ""
}

Write-Host ""
Write-Host "📖 Daha fazla bilgi: GITHUB_DEPLOYMENT_SETUP.md" -ForegroundColor $info
Write-Host ""
