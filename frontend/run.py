"""Servidor de desarrollo: API REST + interfaz Flet en un único proceso.

Uso (desde la raíz del proyecto):

    uv run python frontend/run.py

La API queda en http://127.0.0.1:8000 (Swagger en /docs) y la interfaz Flet
se sirve en la raíz http://127.0.0.1:8000/.

En producción (Render) se recomienda usar directamente:

    uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
"""

import os
import sys
from pathlib import Path

# Permite importar backend.* y frontend.* al ejecutar el script directamente
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "8000"))
    # En Render no conviene el modo reload.
    recargar = os.getenv("RENDER") is None
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=puerto,
        reload=recargar,
    )
