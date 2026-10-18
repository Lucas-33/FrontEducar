"""Entrada para ejecutar la interfaz Flet sola (`flet run` o `flet build`).

Uso (desde la raíz del proyecto):

    uv run flet run

Requiere el backend en marcha en http://127.0.0.1:8000 (ver frontend/run.py).
"""
import sys
from pathlib import Path

# Permite importar frontend.* al ejecutar el script directamente
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import flet as ft

from frontend.app.main_view import main

if __name__ == "__main__":
    ft.run(main)
