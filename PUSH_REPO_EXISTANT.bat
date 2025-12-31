@echo off
chcp 65001 >nul
echo ========================================
echo   Publication sur GitHub
echo   DizeAnalytics/MairieKloto1 (existant)
echo ========================================
echo.

REM Configuration Git
echo [1/8] Configuration de Git...
git config --global user.email "dizeanalytics@gmail.com"
if errorlevel 1 goto error
git config --global user.name "DizeAnalytics"
if errorlevel 1 goto error
echo OK
echo.

REM Initialisation
echo [2/8] Initialisation du depot Git local...
git init
if errorlevel 1 goto error
echo OK
echo.

REM Ajout des fichiers
echo [3/8] Ajout des fichiers...
git add .
if errorlevel 1 goto error
echo OK
echo.

REM Commit
echo [4/8] Creation du commit...
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"
if errorlevel 1 goto error
echo OK
echo.

REM Remote - supprimer si existe deja
echo [5/8] Configuration du remote GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
if errorlevel 1 goto error
echo OK
echo.

REM Branche main
echo [6/8] Configuration de la branche main...
git branch -M main
if errorlevel 1 goto error
echo OK
echo.

REM Récupérer les fichiers existants si nécessaire
echo [7/8] Recuperation des fichiers existants (si necessaire)...
git fetch origin
if errorlevel 1 goto fetch_error
git pull origin main --allow-unrelated-histories --no-edit 2>nul
if errorlevel 1 goto pull_skip
echo OK
echo.
goto push

:pull_skip
echo Info: Pas de fichiers existants a recuperer ou conflits mineurs - on continue
echo.

:push
REM Push
echo [8/8] Envoi vers GitHub...
echo.
echo ATTENTION: Vous devrez vous authentifier avec:
echo - Username: dizeanalytics@gmail.com
echo - Password: Votre Personal Access Token GitHub
echo.
git push -u origin main --force
if errorlevel 1 goto push_retry

echo.
echo ========================================
echo   SUCCESS! Projet publie sur GitHub
echo   https://github.com/DizeAnalytics/MairieKloto1
echo ========================================
pause
exit /b 0

:push_retry
echo.
echo Tentative sans --force...
git push -u origin main
if errorlevel 1 goto error
goto success

:fetch_error
echo Info: Le depot est peut-etre vide, on continue...
echo.
goto push

:success
echo.
echo ========================================
echo   SUCCESS! Projet publie sur GitHub
echo   https://github.com/DizeAnalytics/MairieKloto1
echo ========================================
pause
exit /b 0

:error
echo.
echo ========================================
echo   ERREUR lors de l'execution
echo ========================================
echo.
echo Verifiez que:
echo 1. Git est correctement installe
echo 2. Le depot GitHub existe: https://github.com/DizeAnalytics/MairieKloto1
echo 3. Vous avez les droits d'acces au depot
echo.
pause
exit /b 1

