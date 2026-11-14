#!/usr/bin/env bash
# Opción A (con GitHub CLI): gh repo create astro-health-monitor --public --source=. --push
# Opción B (manual): crea el repo vacío en github.com y reemplaza TU_USUARIO
git init -b main
git add .
git commit -m "estructura inicial del repositorio y README base"
git remote add origin https://github.com/TU_USUARIO/astro-health-monitor.git
git push -u origin main
