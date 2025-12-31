@echo off
echo === Configuration Git pour MairieKloto1 ===
echo.

REM Configuration Git
echo Configuration de Git...
git config --global user.email "dizeanalytics@gmail.com"
git config --global user.name "DizeAnalytics"

echo.
echo Initialisation du depot Git...
git init

echo.
echo Ajout des fichiers...
git add .

echo.
echo Creation du commit initial...
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"

echo.
echo Ajout du remote GitHub...
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git

echo.
echo Renommage de la branche principale...
git branch -M main

echo.
echo === Pret a pousser vers GitHub ===
echo.
echo Execution de la commande pour pousser...
echo NOTE: Vous devrez peut-etre vous authentifier avec votre Personal Access Token GitHub
echo.

git push -u origin main

echo.
echo === Termine ===
pause

