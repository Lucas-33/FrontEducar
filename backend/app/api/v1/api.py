from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, personas, academico, servicios

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(personas.router, prefix="/personas", tags=["Personas (Alumnos, Docentes, Tutores)"])
api_router.include_router(academico.router, prefix="/academico", tags=["Gestión Académica"])
api_router.include_router(servicios.router, prefix="/servicios", tags=["Servicios Escolares"])