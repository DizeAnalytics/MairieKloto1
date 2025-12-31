@echo off
chcp 65001 >nul
echo ========================================
echo   Publication sur GitHub
echo   DizeAnalytics/MairieKloto1
echo ========================================
echo.

REM Configuration Git
echo [1/7] Configuration de Git...
git config --global user.email "dizeanalytics@gmail.com"
if errorlevel 1 goto error
git config --global user.name "DizeAnalytics"
if errorlevel 1 goto error
echo OK
echo.

REM Initialisation
echo [2/7] Initialisation du depot Git...
git init
if errorlevel 1 goto error
echo OK
echo.

REM Ajout des fichiers
echo [3/7] Ajout des fichiers...
git add .
if errorlevel 1 goto error
echo OK
echo.

REM Commit
echo [4/7] Creation du commit...
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"
if errorlevel 1 goto error
echo OK
echo.

REM Remote
echo [5/7] Configuration du remote GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
if errorlevel 1 goto error
echo OK
echo.

REM Branche main
echo [6/7] Configuration de la branche main...
git branch -M main
if errorlevel 1 goto error
echo OK
echo.

REM Push
echo [7/7] Envoi vers GitHub...
echo.
echo ATTENTION: Vous devrez vous authentifier avec:
echo - Username: dizeanalytics@gmail.com
echo - Password: Votre Personal Access Token GitHub
echo.
git push -u origin main
if errorlevel 1 goto error

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

