@echo off
REM Lanzador rapido - Michell
REM Nomas le doy doble clic a este archivo y se abre la animacion
REM en su propia ventana negra, sin tener que abrir Visual Studio.

title I Love You
mode con: cols=100 lines=40
python "%~dp0corazon_i_love_you.py"
echo.
pause
