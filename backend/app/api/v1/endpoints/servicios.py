from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.schemas.servicios import (
    DeporteCreate,
    DeporteResponse,
    DeporteUpdate,
    GrupoDeporteCreate,
    GrupoDeporteDetalleResponse,
    GrupoDeporteResponse,
    GrupoDeporteUpdate,
    InscripcionComedorCreate,
    InscripcionComedorDetalleResponse,
    InscripcionComedorResponse,
    InscripcionDeporteCreate,
    InscripcionDeporteDetalleResponse,
    InscripcionDeporteResponse,
    InscripcionTransporteCreate,
    InscripcionTransporteDetalleResponse,
    InscripcionTransporteResponse,
    RecorridoTransporteCreate,
    RecorridoTransporteResponse,
    RecorridoTransporteUpdate,
)
from backend.app.services.servicios import servicios_escolares_service

router = APIRouter()


# --- DEPORTES ---
@router.get(
    "/deportes", response_model=list[DeporteResponse], summary="Listar deportes"
)
def listar_deportes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.get_deportes(db)


@router.post(
    "/deportes",
    response_model=DeporteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear deporte (solo ADMIN)",
)
def crear_deporte(
    deporte_in: DeporteCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.create_deporte(db, deporte_in)


@router.put(
    "/deportes/{id_deporte}",
    response_model=DeporteResponse,
    summary="Actualizar deporte (solo ADMIN)",
)
def actualizar_deporte(
    id_deporte: int,
    deporte_in: DeporteUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.update_deporte(db, id_deporte, deporte_in)


@router.delete(
    "/deportes/{id_deporte}",
    response_model=DeporteResponse,
    summary="Eliminar deporte (solo ADMIN)",
)
def eliminar_deporte(
    id_deporte: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.delete_deporte(db, id_deporte)


@router.post(
    "/deportes/grupos",
    response_model=GrupoDeporteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear grupo de deporte (solo ADMIN)",
)
def crear_grupo_deporte(
    grupo_in: GrupoDeporteCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.create_grupo_deporte(db, grupo_in)


@router.put(
    "/deportes/grupos/{id_grupo}",
    response_model=GrupoDeporteResponse,
    summary="Actualizar grupo de deporte (solo ADMIN)",
)
def actualizar_grupo_deporte(
    id_grupo: int,
    grupo_in: GrupoDeporteUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.update_grupo_deporte(db, id_grupo, grupo_in)


@router.delete(
    "/deportes/grupos/{id_grupo}",
    response_model=GrupoDeporteResponse,
    summary="Eliminar grupo de deporte (solo ADMIN)",
)
def eliminar_grupo_deporte(
    id_grupo: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.delete_grupo_deporte(db, id_grupo)


@router.get(
    "/deportes/grupos",
    response_model=list[GrupoDeporteDetalleResponse],
    summary="Listar grupos de deporte con detalle",
)
def listar_grupos_deporte(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.get_grupos_deporte(db)


@router.post(
    "/deportes/inscripciones",
    response_model=InscripcionDeporteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscribir alumno a deporte (ADMIN/TUTOR)",
)
def inscribir_deporte(
    inscripcion_in: InscripcionDeporteCreate,
    current_user: Usuario = Depends(require_roles("ADMIN", "PARENT")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.inscribir_deporte(db, inscripcion_in)


@router.get(
    "/deportes/inscripciones",
    response_model=list[InscripcionDeporteDetalleResponse],
    summary="Listar inscripciones a deportes con detalle",
)
def listar_inscripciones_deporte(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.get_inscripciones_deporte(db)


# --- TRANSPORTE ---
@router.get(
    "/transporte/recorridos",
    response_model=list[RecorridoTransporteResponse],
    summary="Listar recorridos de transporte",
)
def listar_recorridos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.get_recorridos(db)


@router.post(
    "/transporte/recorridos",
    response_model=RecorridoTransporteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear recorrido de transporte (solo ADMIN)",
)
def crear_recorrido(
    recorrido_in: RecorridoTransporteCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.create_recorrido(db, recorrido_in)


@router.put(
    "/transporte/recorridos/{id_recorrido}",
    response_model=RecorridoTransporteResponse,
    summary="Actualizar recorrido de transporte (solo ADMIN)",
)
def actualizar_recorrido(
    id_recorrido: int,
    recorrido_in: RecorridoTransporteUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.update_recorrido(db, id_recorrido, recorrido_in)


@router.delete(
    "/transporte/recorridos/{id_recorrido}",
    response_model=RecorridoTransporteResponse,
    summary="Eliminar recorrido de transporte (solo ADMIN)",
)
def eliminar_recorrido(
    id_recorrido: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.delete_recorrido(db, id_recorrido)


@router.post(
    "/transporte/inscripciones",
    response_model=InscripcionTransporteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscribir alumno a transporte (ADMIN/TUTOR)",
)
def inscribir_transporte(
    inscripcion_in: InscripcionTransporteCreate,
    current_user: Usuario = Depends(require_roles("ADMIN", "PARENT")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.inscribir_transporte(db, inscripcion_in)


@router.get(
    "/transporte/inscripciones",
    response_model=list[InscripcionTransporteDetalleResponse],
    summary="Listar pasajeros de transporte con detalle",
)
def listar_inscripciones_transporte(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.get_inscripciones_transporte(db)


@router.delete(
    "/transporte/inscripciones/{legajo_alumno}",
    response_model=InscripcionTransporteResponse,
    summary="Baja de transporte (ADMIN/TUTOR)",
)
def baja_transporte(
    legajo_alumno: int,
    current_user: Usuario = Depends(require_roles("ADMIN", "PARENT")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.baja_transporte(db, legajo_alumno)


# --- COMEDOR ---
@router.post(
    "/comedor/inscripciones",
    response_model=InscripcionComedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscribir alumno a comedor (ADMIN/TUTOR)",
)
def inscribir_comedor(
    inscripcion_in: InscripcionComedorCreate,
    current_user: Usuario = Depends(require_roles("ADMIN", "PARENT")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.inscribir_comedor(db, inscripcion_in)


@router.get(
    "/comedor/inscripciones",
    response_model=list[InscripcionComedorDetalleResponse],
    summary="Listar inscriptos al comedor con detalle",
)
def listar_inscripciones_comedor(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.get_inscripciones_comedor(db)


@router.delete(
    "/comedor/inscripciones/{legajo_alumno}",
    response_model=InscripcionComedorResponse,
    summary="Baja de comedor (ADMIN/TUTOR)",
)
def baja_comedor(
    legajo_alumno: int,
    current_user: Usuario = Depends(require_roles("ADMIN", "PARENT")),
    db: Session = Depends(get_db),
):
    return servicios_escolares_service.baja_comedor(db, legajo_alumno)
