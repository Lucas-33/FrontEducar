from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import flet.fastapi as flet_fastapi

from backend.app.core.database import engine, Base
import backend.app.models.alumno  # Asegura que el modelo se registre en SQLAlchemy
from frontend.app.main_view import main as flet_main

# 1. Crear automáticamente las tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

# 2. Instancia principal de FastAPI
app = FastAPI(
    title="Educar para Transformar - API & Web",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 3. Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Endpoint de salud / prueba de la API
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "message": "API REST funcionando correctamente"}

# (Aquí se irán incluyendo los routers con app.include_router en los próximos pasos)

# 5. Montar la interfaz de Flet en la raíz
# NOTA: Se monta AL FINAL para que las rutas de la API (/api/... y /docs) tengan prioridad
app.mount("/", flet_fastapi.app(flet_main))