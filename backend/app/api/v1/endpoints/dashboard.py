"""Resumen numérico para el panel de control administrativo."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.repositories import (
    alumno_repository,
    curso_repository,
    deporte_repository,
    grupo_deporte_repository,
    inscripcion_comedor_repository,
    inscripcion_transporte_repository,
    nivel_repository,
    profesor_repository,
)
from backend.app.services.comunidad import comunidad_service

router = APIRouter()


@router.get("/resumen", summary="Resumen de métricas para el dashboard (solo ADMIN)")
def resumen_dashboard(
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    comunidad = comunidad_service.resumen(db)

    transporte_activos = [
        i for i in inscripcion_transporte_repository.get_multi(db, limit=1000) if i.estado == "ACTIVO"
    ]
    comedor_activos = [
        i for i in inscripcion_comedor_repository.get_multi(db, limit=1000) if i.estado == "ACTIVO"
    ]

    return {
        "alumnos_activos": len(alumno_repository.get_activos(db, limit=1000)),
        "docentes_activos": len(profesor_repository.get_activos(db, limit=1000)),
        "cursos": len(curso_repository.get_multi(db, limit=500)),
        "niveles": len(nivel_repository.get_multi(db, limit=100)),
        "deportes": len(deporte_repository.get_multi(db, limit=200)),
        "grupos_deporte": len(grupo_deporte_repository.get_multi(db, limit=300)),
        "transporte_activos": len(transporte_activos),
        "comedor_activos": len(comedor_activos),
        "solicitudes_pendientes": comunidad["solicitudes_pendientes"],
        "mensajes_no_leidos": comunidad["mensajes_no_leidos"],
        "opiniones_pendientes": comunidad["opiniones_pendientes"],
    }
