@echo off
REM Lanzador rapido - Michell
REM Este me instala pygame solo la primera vez (si no lo tengo) y
REM luego abre la animacion.

title Corazon Rojo
python -c "import pygame" 2>nul
if errorlevel 1 (
    echo Instalando pygame por primera vez, un momento...
    python -m pip install pygame
)
python "%~dp0red_heart_pygame.py"
echo.
pause
