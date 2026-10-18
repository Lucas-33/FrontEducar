from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.schemas.academico import (
    NivelEducativoCreate, NivelEducativoUpdate, NivelEducativoResponse,
    CursoCreate, CursoUpdate, CursoResponse,
    MateriaCreate, MateriaUpdate, MateriaResponse,
    MateriaCursoProfesorCreate, MateriaCursoProfesorUpdate, MateriaCursoProfesorResponse,
    AsignacionDetalleResponse,
)
from backend.app.schemas.servicios import HorarioCreate, HorarioUpdate, HorarioResponse
from backend.app.services.academico import academico_service

router = APIRouter()

# --- NIVELES ---
@router.get("/niveles", response_model=List[NivelEducativoResponse], summary="Listar niveles educativos")
def listar_niveles(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return academico_service.get_niveles(db)

@router.post("/niveles", response_model=NivelEducativoResponse, status_code=status.HTTP_201_CREATED, summary="Crear nivel educativo (solo ADMIN)")
def crear_nivel(
    nivel_in: NivelEducativoCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.create_nivel(db, nivel_in)

@router.put("/niveles/{id_nivel}", response_model=NivelEducativoResponse, summary="Actualizar nivel educativo (solo ADMIN)")
def actualizar_nivel(
    id_nivel: int,
    nivel_in: NivelEducativoUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.update_nivel(db, id_nivel, nivel_in)

@router.delete("/niveles/{id_nivel}", response_model=NivelEducativoResponse, summary="Eliminar nivel educativo (solo ADMIN)")
def eliminar_nivel(
    id_nivel: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.delete_nivel(db, id_nivel)

# --- CURSOS ---
@router.get("/cursos", response_model=List[CursoResponse], summary="Listar cursos")
def listar_cursos(
    id_nivel: Optional[int] = Query(None, description="Filtrar por nivel"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return academico_service.get_cursos(db, id_nivel=id_nivel)

@router.post("/cursos", response_model=CursoResponse, status_code=status.HTTP_201_CREATED, summary="Crear curso (solo ADMIN)")
def crear_curso(
    curso_in: CursoCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.create_curso(db, curso_in)

@router.put("/cursos/{id_curso}", response_model=CursoResponse, summary="Actualizar curso (solo ADMIN)")
def actualizar_curso(
    id_curso: int,
    curso_in: CursoUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.update_curso(db, id_curso, curso_in)

@router.delete("/cursos/{id_curso}", response_model=CursoResponse, summary="Eliminar curso (solo ADMIN)")
def eliminar_curso(
    id_curso: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.delete_curso(db, id_curso)

# --- MATERIAS ---
@router.get("/materias", response_model=List[MateriaResponse], summary="Listar materias")
def listar_materias(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return academico_service.get_materias(db)

@router.post("/materias", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED, summary="Crear materia (solo ADMIN)")
def crear_materia(
    materia_in: MateriaCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.create_materia(db, materia_in)

@router.put("/materias/{id_materia}", response_model=MateriaResponse, summary="Actualizar materia (solo ADMIN)")
def actualizar_materia(
    id_materia: int,
    materia_in: MateriaUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.update_materia(db, id_materia, materia_in)

@router.delete("/materias/{id_materia}", response_model=MateriaResponse, summary="Eliminar materia (solo ADMIN)")
def eliminar_materia(
    id_materia: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.delete_materia(db, id_materia)

# --- ASIGNACIÓN DOCENTE ---
@router.post("/asignaciones", response_model=MateriaCursoProfesorResponse, status_code=status.HTTP_201_CREATED, summary="Asignar profesor y materia a un curso (solo ADMIN)")
def asignar_materia_curso(
    asignacion_in: MateriaCursoProfesorCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.asignar_materia_profesor(db, asignacion_in)

@router.get("/asignaciones", response_model=List[AsignacionDetalleResponse], summary="Listar asignaciones con detalle (materia, curso, nivel y profesor)")
def listar_asignaciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return academico_service.get_asignaciones(db)

@router.put("/asignaciones/{id_materia}/{id_curso}", response_model=MateriaCursoProfesorResponse, summary="Actualizar asignación (solo ADMIN)")
def actualizar_asignacion(
    id_materia: int,
    id_curso: int,
    asignacion_in: MateriaCursoProfesorUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.update_asignacion(db, id_materia, id_curso, asignacion_in)

@router.delete("/asignaciones/{id_materia}/{id_curso}", response_model=MateriaCursoProfesorResponse, summary="Eliminar asignación (solo ADMIN)")
def eliminar_asignacion(
    id_materia: int,
    id_curso: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.delete_asignacion(db, id_materia, id_curso)

# --- HORARIOS ---
@router.get("/horarios", response_model=List[HorarioResponse], summary="Listar horarios / turnos")
def listar_horarios(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return academico_service.get_horarios(db)

@router.post("/horarios", response_model=HorarioResponse, status_code=status.HTTP_201_CREATED, summary="Crear horario / turno (solo ADMIN)")
def crear_horario(
    horario_in: HorarioCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.create_horario(db, horario_in)

@router.put("/horarios/{id_horario}", response_model=HorarioResponse, summary="Actualizar horario / turno (solo ADMIN)")
def actualizar_horario(
    id_horario: int,
    horario_in: HorarioUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.update_horario(db, id_horario, horario_in)

@router.delete("/horarios/{id_horario}", response_model=HorarioResponse, summary="Eliminar horario / turno (solo ADMIN)")
def eliminar_horario(
    id_horario: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return academico_service.delete_horario(db, id_horario)
