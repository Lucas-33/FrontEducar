from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.personas import (
    AlumnoCreate, AlumnoUpdate, AlumnoResponse,
    ProfesorCreate, ProfesorUpdate, ProfesorResponse,
    PadreCreate, PadreResponse,
    PadreAlumnoCreate, PadreAlumnoResponse,
)
from backend.app.services.personas import personas_service

router = APIRouter()

# ==================== ALUMNOS ====================

@router.get("/alumnos", response_model=List[AlumnoResponse], summary="Listar alumnos")
def listar_alumnos(
    solo_activos: bool = Query(True, description="Filtrar solo alumnos activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return personas_service.get_alumnos(db=db, solo_activos=solo_activos, skip=skip, limit=limit)

@router.get("/alumnos/{legajo}", response_model=AlumnoResponse, summary="Obtener alumno por legajo")
def obtener_alumno(legajo: int, db: Session = Depends(get_db)):
    return personas_service.get_alumno(db=db, legajo=legajo)

@router.post("/alumnos", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED, summary="Registrar alumno")
def crear_alumno(alumno_in: AlumnoCreate, db: Session = Depends(get_db)):
    return personas_service.create_alumno(db=db, alumno_in=alumno_in)

@router.put("/alumnos/{legajo}", response_model=AlumnoResponse, summary="Actualizar datos de un alumno")
def actualizar_alumno(legajo: int, alumno_in: AlumnoUpdate, db: Session = Depends(get_db)):
    return personas_service.update_alumno(db=db, legajo=legajo, alumno_in=alumno_in)

@router.delete("/alumnos/{legajo}", response_model=AlumnoResponse, summary="Baja lógica de un alumno")
def eliminar_alumno(legajo: int, db: Session = Depends(get_db)):
    return personas_service.delete_alumno(db=db, legajo=legajo)


# ==================== PROFESORES ====================

@router.get("/profesores", response_model=List[ProfesorResponse], summary="Listar profesores")
def listar_profesores(
    solo_activos: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return personas_service.get_profesores(db=db, solo_activos=solo_activos, skip=skip, limit=limit)

@router.get("/profesores/{legajo}", response_model=ProfesorResponse, summary="Obtener profesor por legajo")
def obtener_profesor(legajo: int, db: Session = Depends(get_db)):
    return personas_service.get_profesor(db=db, legajo=legajo)

@router.post("/profesores", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED, summary="Registrar profesor")
def crear_profesor(profesor_in: ProfesorCreate, db: Session = Depends(get_db)):
    return personas_service.create_profesor(db=db, profesor_in=profesor_in)

@router.put("/profesores/{legajo}", response_model=ProfesorResponse, summary="Actualizar profesor")
def actualizar_profesor(legajo: int, profesor_in: ProfesorUpdate, db: Session = Depends(get_db)):
    return personas_service.update_profesor(db=db, legajo=legajo, profesor_in=profesor_in)

@router.delete("/profesores/{legajo}", response_model=ProfesorResponse, summary="Baja lógica de un profesor")
def eliminar_profesor(legajo: int, db: Session = Depends(get_db)):
    return personas_service.delete_profesor(db=db, legajo=legajo)


# ==================== PADRES / TUTORES ====================

@router.get("/padres", response_model=List[PadreResponse], summary="Listar tutores")
def listar_padres(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100), db: Session = Depends(get_db)):
    return personas_service.get_padres(db=db, skip=skip, limit=limit)

@router.post("/padres", response_model=PadreResponse, status_code=status.HTTP_201_CREATED, summary="Registrar tutor")
def crear_padre(padre_in: PadreCreate, db: Session = Depends(get_db)):
    return personas_service.create_padre(db=db, padre_in=padre_in)

@router.post("/padre-alumno", response_model=PadreAlumnoResponse, status_code=status.HTTP_201_CREATED, summary="Vincular padre con alumno")
def vincular_padre_alumno(relacion_in: PadreAlumnoCreate, db: Session = Depends(get_db)):
    return personas_service.asociar_padre_alumno(db=db, relacion_in=relacion_in)