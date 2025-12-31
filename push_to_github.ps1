# Script PowerShell pour initialiser Git et pousser vers GitHub
# Usage: .\push_to_github.ps1

Write-Host "=== Configuration Git pour MairieKloto1 ===" -ForegroundColor Green
Write-Host ""

# Vérifier si Git est installé
try {
    $gitVersion = git --version
    Write-Host "Git détecté: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Git n'est pas installé!" -ForegroundColor Red
    Write-Host "Veuillez installer Git depuis https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Configuration de Git..." -ForegroundColor Cyan
git config --global user.email "dizeanalytics@gmail.com"
git config --global user.name "DizeAnalytics"

Write-Host ""
Write-Host "Initialisation du dépôt Git..." -ForegroundColor Cyan
git init

Write-Host ""
Write-Host "Ajout des fichiers..." -ForegroundColor Cyan
git add .

Write-Host ""
Write-Host "Création du commit initial..." -ForegroundColor Cyan
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"

Write-Host ""
Write-Host "Ajout du remote GitHub..." -ForegroundColor Cyan
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git

Write-Host ""
Write-Host "Renommage de la branche principale..." -ForegroundColor Cyan
git branch -M main

Write-Host ""
Write-Host "=== Prêt à pousser vers GitHub ===" -ForegroundColor Green
Write-Host ""
Write-Host "Exécutez la commande suivante pour pousser:" -ForegroundColor Yellow
Write-Host "git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "NOTE: Vous devrez peut-être vous authentifier avec votre Personal Access Token GitHub" -ForegroundColor Yellow
Write-Host ""

$push = Read-Host "Voulez-vous pousser maintenant? (O/N)"
if ($push -eq "O" -or $push -eq "o" -or $push -eq "Y" -or $push -eq "y") {
    Write-Host ""
    Write-Host "Pousser vers GitHub..." -ForegroundColor Cyan
    git push -u origin main
} else {
    Write-Host ""
    Write-Host "Vous pouvez pousser plus tard avec: git push -u origin main" -ForegroundColor Cyan
}

