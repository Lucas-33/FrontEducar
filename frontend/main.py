"""Entrada para ejecutar la interfaz Flet sola (`flet run` o `flet build`).

Uso (desde la raíz del proyecto):

    uv run flet run

Requiere el backend en marcha en http://127.0.0.1:8000 (ver frontend/run.py).

Dentro de un paquete generado con `flet build` (APK/AAB) el contenido de
este directorio es la raíz de la app, por eso se importa `app.main_view`
en lugar de `frontend.app.main_view`.
"""

import sys
from pathlib import Path

# Asegura que `app` (frontend/app) sea importable sin importar desde dónde
# se ejecute el script: dentro del APK esta es la raíz de la app empaquetada.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import flet as ft  # noqa: I001  (el sys.path de arriba debe ejecutarse antes)

from app.main_view import main

if __name__ == "__main__":
    ft.run(main)
