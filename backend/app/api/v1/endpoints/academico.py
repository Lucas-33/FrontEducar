from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.academico import (
    NivelEducativoCreate, NivelEducativoResponse,
    CursoCreate, CursoResponse,
    MateriaCreate, MateriaResponse,
    MateriaCursoProfesorCreate, MateriaCursoProfesorResponse,
)
from backend.app.services.academico import academico_service

router = APIRouter()

# --- NIVELES ---
@router.get("/niveles", response_model=List[NivelEducativoResponse], summary="Listar niveles educativos")
def listar_niveles(db: Session = Depends(get_db)):
    return academico_service.get_niveles(db)

@router.post("/niveles", response_model=NivelEducativoResponse, status_code=status.HTTP_201_CREATED, summary="Crear nivel educativo")
def crear_nivel(nivel_in: NivelEducativoCreate, db: Session = Depends(get_db)):
    return academico_service.create_nivel(db, nivel_in)

# --- CURSOS ---
@router.get("/cursos", response_model=List[CursoResponse], summary="Listar cursos")
def listar_cursos(id_nivel: Optional[int] = Query(None, description="Filtrar por nivel"), db: Session = Depends(get_db)):
    return academico_service.get_cursos(db, id_nivel=id_nivel)

@router.post("/cursos", response_model=CursoResponse, status_code=status.HTTP_201_CREATED, summary="Crear curso")
def crear_curso(curso_in: CursoCreate, db: Session = Depends(get_db)):
    return academico_service.create_curso(db, curso_in)

# --- MATERIAS ---
@router.get("/materias", response_model=List[MateriaResponse], summary="Listar materias")
def listar_materias(db: Session = Depends(get_db)):
    return academico_service.get_materias(db)

@router.post("/materias", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED, summary="Crear materia")
def crear_materia(materia_in: MateriaCreate, db: Session = Depends(get_db)):
    return academico_service.create_materia(db, materia_in)

# --- ASIGNACIÓN DOCENTE ---
@router.post("/asignaciones", response_model=MateriaCursoProfesorResponse, status_code=status.HTTP_201_CREATED, summary="Asignar profesor y materia a un curso")
def asignar_materia_curso(asignacion_in: MateriaCursoProfesorCreate, db: Session = Depends(get_db)):
    return academico_service.asignar_materia_profesor(db, asignacion_in)