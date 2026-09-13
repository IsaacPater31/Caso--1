@echo off
chcp 65001 >nul
echo ========================================================
echo   Sistema Difuso de Alerta Temprana - Canal del Dique
echo ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH del sistema.
    echo Por favor instala Python 3.8 o superior y marca la opcion "Add Python to PATH".
    pause
    exit /b 1
)

if not exist venv (
    echo [INFO] Creando entorno virtual local (venv)...
    python -m venv venv
)

echo [INFO] Activando entorno e instalando dependencias (numpy, matplotlib)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo.
echo [INFO] Lanzando el sistema...
echo ========================================================
python main.py %*

echo.
pause
