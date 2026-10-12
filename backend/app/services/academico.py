from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.repositories import (
    nivel_repository,
    curso_repository,
    materia_repository,
    materia_curso_profesor_repository,
    profesor_repository,
)
from backend.app.schemas.academico import (
    NivelEducativoCreate, CursoCreate, MateriaCreate, MateriaCursoProfesorCreate
)

class AcademicoService:
    # --- NIVELES ---
    def get_niveles(self, db: Session):
        return nivel_repository.get_multi(db)

    def create_nivel(self, db: Session, nivel_in: NivelEducativoCreate):
        return nivel_repository.create(db, nivel_in)

    # --- CURSOS ---
    def get_cursos(self, db: Session, id_nivel: int = None):
        if id_nivel:
            return curso_repository.get_by_nivel(db, id_nivel)
        return curso_repository.get_multi(db)

    def create_curso(self, db: Session, curso_in: CursoCreate):
        if not nivel_repository.get(db, curso_in.id_nivel):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El nivel educativo con ID {curso_in.id_nivel} no existe",
            )
        return curso_repository.create(db, curso_in)

    # --- MATERIAS ---
    def get_materias(self, db: Session):
        return materia_repository.get_multi(db)

    def create_materia(self, db: Session, materia_in: MateriaCreate):
        return materia_repository.create(db, materia_in)

    # --- MATERIA - CURSO - PROFESOR ---
    def asignar_materia_profesor(self, db: Session, asignacion_in: MateriaCursoProfesorCreate):
        if not materia_repository.get(db, asignacion_in.id_materia):
            raise HTTPException(status_code=404, detail="La materia especificada no existe")
        if not curso_repository.get(db, asignacion_in.id_curso):
            raise HTTPException(status_code=404, detail="El curso especificado no existe")
        if not profesor_repository.get_by_legajo(db, asignacion_in.legajo_profesor):
            raise HTTPException(status_code=404, detail="El profesor especificado no existe")

        existente = materia_curso_profesor_repository.get_by_materia_y_curso(
            db, asignacion_in.id_materia, asignacion_in.id_curso
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta materia ya se encuentra asignada en este curso",
            )
        return materia_curso_profesor_repository.create(db, asignacion_in)

academico_service = AcademicoService()