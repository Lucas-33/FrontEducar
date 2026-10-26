from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.schemas.evaluacion import (
    AsistenciaDetalleResponse,
    AsistenciaLoteCreate,
    AsistenciaResponse,
    CalificacionCreate,
    CalificacionDetalleResponse,
    CalificacionResponse,
    CalificacionUpdate,
    ResumenAsistenciaResponse,
)
from backend.app.services.evaluacion import evaluacion_service
from backend.app.services.seguridad import seguridad_service

router = APIRouter()


def _contexto_acceso(db: Session, current_user: Usuario):
    """Devuelve (rol, legajos_permitidos) según el usuario autenticado.

    legajos_permitidos = None significa "sin restricción" (ADMIN/DOCENTE).
    """
    rol = seguridad_service.get_rol_nombre(db, current_user)
    if rol == "STUDENT":
        if not current_user.legajo_alumno:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no tiene un alumno vinculado",
            )
        return rol, [current_user.legajo_alumno]
    if rol == "PARENT":
        return rol, evaluacion_service.legajos_de_padre(db, current_user.id_padre)
    return rol, None


# ==================== CALIFICACIONES ====================


@router.get(
    "/calificaciones",
    response_model=list[CalificacionDetalleResponse],
    summary="Listar calificaciones (alumno/tutor ven solo las propias)",
)
def listar_calificaciones(
    legajo_alumno: int | None = Query(None),
    id_materia: int | None = Query(None),
    id_curso: int | None = Query(None),
    periodo: str | None = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rol, permitidos = _contexto_acceso(db, current_user)

    if rol == "STUDENT":
        return evaluacion_service.get_calificaciones_detalle(
            db,
            legajo_alumno=permitidos[0],
            id_materia=id_materia,
            id_curso=id_curso,
            periodo=periodo,
        )

    if rol == "PARENT":
        if legajo_alumno is not None:
            if legajo_alumno not in permitidos:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puede consultar las calificaciones de sus hijos",
                )
            return evaluacion_service.get_calificaciones_detalle(
                db,
                legajo_alumno=legajo_alumno,
                id_materia=id_materia,
                id_curso=id_curso,
                periodo=periodo,
            )
        return evaluacion_service.get_calificaciones_detalle(
            db,
            legajos_permitidos=permitidos,
            id_materia=id_materia,
            id_curso=id_curso,
            periodo=periodo,
        )

    return evaluacion_service.get_calificaciones_detalle(
        db,
        legajo_alumno=legajo_alumno,
        id_materia=id_materia,
        id_curso=id_curso,
        periodo=periodo,
    )


@router.post(
    "/calificaciones",
    response_model=CalificacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar calificación (ADMIN/DOCENTE)",
)
def crear_calificacion(
    calificacion_in: CalificacionCreate,
    current_user: Usuario = Depends(require_roles("ADMIN", "TEACHER")),
    db: Session = Depends(get_db),
):
    rol = seguridad_service.get_rol_nombre(db, current_user)
    legajo_profesor = current_user.legajo_profesor if rol == "TEACHER" else None
    return evaluacion_service.create_calificacion(db, calificacion_in, legajo_profesor)


@router.put(
    "/calificaciones/{id_calificacion}",
    response_model=CalificacionResponse,
    summary="Actualizar calificación (ADMIN/DOCENTE)",
)
def actualizar_calificacion(
    id_calificacion: int,
    calificacion_in: CalificacionUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN", "TEACHER")),
    db: Session = Depends(get_db),
):
    return evaluacion_service.update_calificacion(db, id_calificacion, calificacion_in)


@router.delete(
    "/calificaciones/{id_calificacion}",
    response_model=CalificacionResponse,
    summary="Eliminar calificación (ADMIN/DOCENTE)",
)
def eliminar_calificacion(
    id_calificacion: int,
    current_user: Usuario = Depends(require_roles("ADMIN", "TEACHER")),
    db: Session = Depends(get_db),
):
    return evaluacion_service.delete_calificacion(db, id_calificacion)


# ==================== ASISTENCIA ====================


@router.get(
    "/asistencia",
    response_model=list[AsistenciaDetalleResponse],
    summary="Listar asistencias (alumno/tutor ven solo las propias)",
)
def listar_asistencia(
    id_curso: int | None = Query(None),
    fecha: date | None = Query(None),
    legajo_alumno: int | None = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rol, permitidos = _contexto_acceso(db, current_user)

    if rol == "STUDENT":
        return evaluacion_service.get_asistencia_detalle(
            db, id_curso=id_curso, fecha=fecha, legajo_alumno=permitidos[0]
        )

    if rol == "PARENT":
        if legajo_alumno is not None:
            if legajo_alumno not in permitidos:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puede consultar las asistencias de sus hijos",
                )
            return evaluacion_service.get_asistencia_detalle(
                db, id_curso=id_curso, fecha=fecha, legajo_alumno=legajo_alumno
            )
        return evaluacion_service.get_asistencia_detalle(
            db, id_curso=id_curso, fecha=fecha, legajos_permitidos=permitidos
        )

    return evaluacion_service.get_asistencia_detalle(
        db, id_curso=id_curso, fecha=fecha, legajo_alumno=legajo_alumno
    )


@router.get(
    "/asistencia/resumen/{legajo_alumno}",
    response_model=ResumenAsistenciaResponse,
    summary="Resumen de presentismo de un alumno",
)
def resumen_asistencia(
    legajo_alumno: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _rol, permitidos = _contexto_acceso(db, current_user)
    if permitidos is not None and legajo_alumno not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede consultar el presentismo de sus hijos o el propio",
        )
    return evaluacion_service.resumen_asistencia(db, legajo_alumno)


@router.post(
    "/asistencia/lote",
    response_model=list[AsistenciaDetalleResponse],
    summary="Cargar asistencia de un curso completo (ADMIN/DOCENTE)",
)
def registrar_asistencia_lote(
    lote_in: AsistenciaLoteCreate,
    current_user: Usuario = Depends(require_roles("ADMIN", "TEACHER")),
    db: Session = Depends(get_db),
):
    rol = seguridad_service.get_rol_nombre(db, current_user)
    legajo_profesor = current_user.legajo_profesor if rol == "TEACHER" else None
    return evaluacion_service.registrar_asistencia_lote(db, lote_in, legajo_profesor)


@router.delete(
    "/asistencia/{id_asistencia}",
    response_model=AsistenciaResponse,
    summary="Eliminar un registro de asistencia (ADMIN/DOCENTE)",
)
def eliminar_asistencia(
    id_asistencia: int,
    current_user: Usuario = Depends(require_roles("ADMIN", "TEACHER")),
    db: Session = Depends(get_db),
):
    return evaluacion_service.delete_asistencia(db, id_asistencia)
