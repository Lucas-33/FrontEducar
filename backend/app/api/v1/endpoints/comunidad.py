from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.schemas.comunidad import (
    MensajeContactoCreate,
    MensajeContactoResponse,
    OpinionCreate,
    OpinionResponse,
    PostulacionEmpleoCreate,
    PostulacionEmpleoResponse,
    SolicitudInscripcionCreate,
    SolicitudInscripcionEstadoUpdate,
    SolicitudInscripcionResponse,
)
from backend.app.services.comunidad import comunidad_service

router = APIRouter()

# ==================== SOLICITUDES DE INSCRIPCIÓN ====================

@router.post(
    "/solicitudes",
    response_model=SolicitudInscripcionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar solicitud de admisión (formulario público, sin login)",
)
def crear_solicitud(solicitud_in: SolicitudInscripcionCreate, db: Session = Depends(get_db)):
    return comunidad_service.crear_solicitud(db, solicitud_in)

@router.get(
    "/solicitudes",
    response_model=List[SolicitudInscripcionResponse],
    summary="Listar solicitudes de admisión (solo ADMIN)",
)
def listar_solicitudes(
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.get_solicitudes(db)

@router.put(
    "/solicitudes/{id_solicitud}/estado",
    response_model=SolicitudInscripcionResponse,
    summary="Aprobar o rechazar una solicitud (solo ADMIN)",
)
def cambiar_estado_solicitud(
    id_solicitud: int,
    payload: SolicitudInscripcionEstadoUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.cambiar_estado_solicitud(
        db, id_solicitud, payload.estado, payload.observaciones
    )

# ==================== MENSAJES DE CONTACTO ====================

@router.post(
    "/contacto",
    response_model=MensajeContactoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar consulta desde el formulario de contacto (público, sin login)",
)
def crear_mensaje(mensaje_in: MensajeContactoCreate, db: Session = Depends(get_db)):
    return comunidad_service.crear_mensaje(db, mensaje_in)

@router.get(
    "/contacto",
    response_model=List[MensajeContactoResponse],
    summary="Listar mensajes de contacto (solo ADMIN)",
)
def listar_mensajes(
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.get_mensajes(db)

@router.put(
    "/contacto/{id_mensaje}/leido",
    response_model=MensajeContactoResponse,
    summary="Marcar un mensaje como leído (solo ADMIN)",
)
def marcar_mensaje_leido(
    id_mensaje: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.marcar_mensaje_leido(db, id_mensaje)

# ==================== OPINIONES ====================

@router.post(
    "/opiniones",
    response_model=OpinionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar opinión pública (queda pendiente de moderación)",
)
def crear_opinion(opinion_in: OpinionCreate, db: Session = Depends(get_db)):
    return comunidad_service.crear_opinion(db, opinion_in)

@router.get(
    "/opiniones",
    response_model=List[OpinionResponse],
    summary="Listar opiniones aprobadas (público, sin login)",
)
def listar_opiniones_publicas(db: Session = Depends(get_db)):
    return comunidad_service.get_opiniones_aprobadas(db)

@router.get(
    "/opiniones/todas",
    response_model=List[OpinionResponse],
    summary="Listar todas las opiniones, incluidas las pendientes (solo ADMIN)",
)
def listar_todas_las_opiniones(
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.get_opiniones(db)

@router.put(
    "/opiniones/{id_opinion}/aprobar",
    response_model=OpinionResponse,
    summary="Aprobar una opinión para su publicación (solo ADMIN)",
)
def aprobar_opinion(
    id_opinion: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.aprobar_opinion(db, id_opinion, True)

@router.delete(
    "/opiniones/{id_opinion}",
    response_model=OpinionResponse,
    summary="Rechazar / eliminar una opinión (solo ADMIN)",
)
def eliminar_opinion(
    id_opinion: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.eliminar_opinion(db, id_opinion)

# ==================== POSTULACIONES LABORALES ====================

@router.post(
    "/postulaciones",
    response_model=PostulacionEmpleoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar postulación laboral (público, sin login)",
)
def crear_postulacion(postulacion_in: PostulacionEmpleoCreate, db: Session = Depends(get_db)):
    return comunidad_service.crear_postulacion(db, postulacion_in)

@router.get(
    "/postulaciones",
    response_model=List[PostulacionEmpleoResponse],
    summary="Listar postulaciones laborales (solo ADMIN)",
)
def listar_postulaciones(
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return comunidad_service.get_postulaciones(db)
