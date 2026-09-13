#!/usr/bin/env bash
echo "========================================================"
echo "  Sistema Difuso de Alerta Temprana - Canal del Dique"
echo "========================================================"
echo ""

if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 no esta instalado o no esta en el PATH."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[INFO] Creando entorno virtual local (venv)..."
    python3 -m venv venv
fi

echo "[INFO] Activando entorno e instalando dependencias (numpy, matplotlib)..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "[INFO] Lanzando el sistema..."
echo "========================================================"
python main.py "$@"
