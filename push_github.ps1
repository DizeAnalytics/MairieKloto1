# Script pour pousser le projet sur GitHub
Write-Host "=== Publication sur GitHub ===" -ForegroundColor Green
Write-Host "Dépôt: DizeAnalytics/MairieKloto1" -ForegroundColor Cyan
Write-Host ""

# Fonction pour exécuter une commande git via cmd
function Invoke-GitCommand {
    param($command)
    Write-Host "Exécution: $command" -ForegroundColor Yellow
    $result = cmd /c "$command 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: $result" -ForegroundColor Red
        return $false
    }
    Write-Host "OK" -ForegroundColor Green
    return $true
}

# Configuration
Write-Host "[1/7] Configuration Git..." -ForegroundColor Cyan
Invoke-GitCommand "git config --global user.email `"dizeanalytics@gmail.com`""
Invoke-GitCommand "git config --global user.name `"DizeAnalytics`""

# Initialisation
Write-Host ""
Write-Host "[2/7] Initialisation du dépôt..." -ForegroundColor Cyan
Invoke-GitCommand "git init"

# Ajout des fichiers
Write-Host ""
Write-Host "[3/7] Ajout des fichiers..." -ForegroundColor Cyan
Invoke-GitCommand "git add ."

# Commit
Write-Host ""
Write-Host "[4/7] Création du commit..." -ForegroundColor Cyan
Invoke-GitCommand "git commit -m `"Initial commit: Plateforme web Mairie de Kloto 1`""

# Remote
Write-Host ""
Write-Host "[5/7] Configuration du remote..." -ForegroundColor Cyan
cmd /c "git remote remove origin 2>nul"
Invoke-GitCommand "git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git"

# Branche main
Write-Host ""
Write-Host "[6/7] Configuration de la branche main..." -ForegroundColor Cyan
Invoke-GitCommand "git branch -M main"

# Push
Write-Host ""
Write-Host "[7/7] Envoi vers GitHub..." -ForegroundColor Cyan
Write-Host ""
Write-Host "ATTENTION: Vous devrez vous authentifier:" -ForegroundColor Yellow
Write-Host "- Username: dizeanalytics@gmail.com" -ForegroundColor White
Write-Host "- Password: Votre Personal Access Token GitHub" -ForegroundColor White
Write-Host ""

Invoke-GitCommand "git push -u origin main"

Write-Host ""
Write-Host "=== TERMINÉ ===" -ForegroundColor Green
Write-Host "Vérifiez sur: https://github.com/DizeAnalytics/MairieKloto1" -ForegroundColor Cyan

