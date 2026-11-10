import os

import flet.fastapi as flet_fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app import (
    models,  # noqa: F401  (registra todas las tablas en Base.metadata)
)
from backend.app.api.v1.api import api_router
from backend.app.core.database import Base, engine
from frontend.app.main_view import main as flet_main

# 1. Crear automáticamente las tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

# 2. Instancia principal de FastAPI
app = FastAPI(
    title="Educar para Transformar - API & Web",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 3. Middleware de CORS
#    - Local: localhost / 127.0.0.1
#    - Render: RENDER_EXTERNAL_URL se agrega automáticamente
#    - Otros orígenes: variable CORS_ORIGINS separada por comas
_origenes = ["http://localhost:8000", "http://127.0.0.1:8000"]

_render_url = os.getenv("RENDER_EXTERNAL_URL")
if _render_url:
    _origenes.append(_render_url.rstrip("/"))

_origenes += [
    origen.strip()
    for origen in os.getenv("CORS_ORIGINS", "").split(",")
    if origen.strip()
]

# Quitamos duplicados conservando el orden.
_origenes = list(dict.fromkeys(_origenes))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origenes,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Endpoint de salud / prueba de la API
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "message": "API REST funcionando correctamente"}


# Conectar routers REST
app.include_router(api_router, prefix="/api/v1")

# 5. Montar la interfaz de Flet en la raíz
# NOTA: Se monta AL FINAL para que las rutas de la API (/api/... y /docs) tengan prioridad
app.mount("/", flet_fastapi.app(flet_main))
