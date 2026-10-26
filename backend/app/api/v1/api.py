from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    academico,
    auth,
    comunidad,
    dashboard,
    evaluacion,
    personas,
    reportes,
    servicios,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(
    personas.router, prefix="/personas", tags=["Personas (Alumnos, Docentes, Tutores)"]
)
api_router.include_router(
    academico.router, prefix="/academico", tags=["Gestión Académica"]
)
api_router.include_router(
    evaluacion.router, prefix="/academico", tags=["Evaluación (Notas y Asistencia)"]
)
api_router.include_router(
    servicios.router, prefix="/servicios", tags=["Servicios Escolares"]
)
api_router.include_router(
    comunidad.router,
    prefix="/comunidad",
    tags=["Comunidad (Admisiones, Contacto, Opiniones, Empleo)"],
)
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["Panel de control"]
)
api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes Excel"])
