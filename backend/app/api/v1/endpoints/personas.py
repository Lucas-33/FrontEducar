from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.schemas.personas import (
    AlumnoCreate,
    AlumnoResponse,
    AlumnoUpdate,
    PadreAlumnoCreate,
    PadreAlumnoResponse,
    PadreCreate,
    PadreResponse,
    ProfesorCreate,
    ProfesorResponse,
    ProfesorUpdate,
)
from backend.app.services.personas import personas_service
from backend.app.services.seguridad import seguridad_service

router = APIRouter()

# ==================== ALUMNOS ====================


@router.get(
    "/alumnos",
    response_model=list[AlumnoResponse],
    summary="Listar alumnos (ADMIN/DOCENTE)",
)
def listar_alumnos(
    solo_activos: bool = Query(True, description="Filtrar solo alumnos activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(require_roles("ADMIN", "TEACHER")),
    db: Session = Depends(get_db),
):
    return personas_service.get_alumnos(
        db=db, solo_activos=solo_activos, skip=skip, limit=limit
    )


@router.get(
    "/alumnos/{legajo}",
    response_model=AlumnoResponse,
    summary="Obtener alumno por legajo (propio, hijo o cualquier legajo para staff)",
)
def obtener_alumno(
    legajo: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rol = seguridad_service.get_rol_nombre(db, current_user)
    if rol == "STUDENT" and current_user.legajo_alumno != legajo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede consultar su propia ficha de alumno",
        )
    if rol == "PARENT":
        hijos = (
            personas_service.get_alumnos_de_padre(db, current_user.id_padre)
            if current_user.id_padre
            else []
        )
        if legajo not in {hijo.legajo for hijo in hijos}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede consultar la ficha de sus hijos",
            )
    return personas_service.get_alumno(db=db, legajo=legajo)


@router.post(
    "/alumnos",
    response_model=AlumnoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar alumno (solo ADMIN)",
)
def crear_alumno(
    alumno_in: AlumnoCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.create_alumno(db=db, alumno_in=alumno_in)


@router.put(
    "/alumnos/{legajo}",
    response_model=AlumnoResponse,
    summary="Actualizar datos de un alumno (solo ADMIN)",
)
def actualizar_alumno(
    legajo: int,
    alumno_in: AlumnoUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.update_alumno(db=db, legajo=legajo, alumno_in=alumno_in)


@router.delete(
    "/alumnos/{legajo}",
    response_model=AlumnoResponse,
    summary="Baja lógica de un alumno (solo ADMIN)",
)
def eliminar_alumno(
    legajo: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.delete_alumno(db=db, legajo=legajo)


# ==================== PROFESORES ====================


@router.get(
    "/profesores", response_model=list[ProfesorResponse], summary="Listar profesores"
)
def listar_profesores(
    solo_activos: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return personas_service.get_profesores(
        db=db, solo_activos=solo_activos, skip=skip, limit=limit
    )


@router.get(
    "/profesores/{legajo}",
    response_model=ProfesorResponse,
    summary="Obtener profesor por legajo",
)
def obtener_profesor(
    legajo: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return personas_service.get_profesor(db=db, legajo=legajo)


@router.post(
    "/profesores",
    response_model=ProfesorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar profesor (solo ADMIN)",
)
def crear_profesor(
    profesor_in: ProfesorCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.create_profesor(db=db, profesor_in=profesor_in)


@router.put(
    "/profesores/{legajo}",
    response_model=ProfesorResponse,
    summary="Actualizar profesor (solo ADMIN)",
)
def actualizar_profesor(
    legajo: int,
    profesor_in: ProfesorUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.update_profesor(
        db=db, legajo=legajo, profesor_in=profesor_in
    )


@router.delete(
    "/profesores/{legajo}",
    response_model=ProfesorResponse,
    summary="Baja lógica de un profesor (solo ADMIN)",
)
def eliminar_profesor(
    legajo: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.delete_profesor(db=db, legajo=legajo)


# ==================== PADRES / TUTORES ====================


@router.get(
    "/padres", response_model=list[PadreResponse], summary="Listar tutores (solo ADMIN)"
)
def listar_padres(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.get_padres(db=db, skip=skip, limit=limit)


@router.post(
    "/padres",
    response_model=PadreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar tutor (solo ADMIN)",
)
def crear_padre(
    padre_in: PadreCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.create_padre(db=db, padre_in=padre_in)


@router.get(
    "/padres/{id_padre}/alumnos",
    response_model=list[AlumnoResponse],
    summary="Listar hijos (alumnos) de un tutor",
)
def listar_alumnos_de_padre(
    id_padre: int,
    current_user: Usuario = Depends(require_roles("ADMIN", "TEACHER", "PARENT")),
    db: Session = Depends(get_db),
):
    # Un tutor solo puede consultar a sus propios hijos
    rol = seguridad_service.get_rol_nombre(db, current_user)
    if rol == "PARENT" and current_user.id_padre != id_padre:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede consultar los alumnos vinculados a su propio usuario",
        )
    return personas_service.get_alumnos_de_padre(db=db, id_padre=id_padre)


@router.post(
    "/padre-alumno",
    response_model=PadreAlumnoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Vincular padre con alumno (solo ADMIN)",
)
def vincular_padre_alumno(
    relacion_in: PadreAlumnoCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return personas_service.asociar_padre_alumno(db=db, relacion_in=relacion_in)
