from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.academico import NivelEducativo, Curso, Materia, MateriaCursoProfesor
from backend.app.schemas.academico import (
    NivelEducativoCreate, NivelEducativoBase,
    CursoCreate, CursoBase,
    MateriaCreate, MateriaBase,
    MateriaCursoProfesorCreate, MateriaCursoProfesorBase,
)
from backend.app.repositories.base import CRUDBase

class NivelEducativoRepository(CRUDBase[NivelEducativo, NivelEducativoCreate, NivelEducativoBase]):
    def __init__(self):
        super().__init__(NivelEducativo)

class CursoRepository(CRUDBase[Curso, CursoCreate, CursoBase]):
    def __init__(self):
        super().__init__(Curso)

    def get_by_nivel(self, db: Session, id_nivel: int) -> List[Curso]:
        stmt = select(Curso).where(Curso.id_nivel == id_nivel)
        return list(db.scalars(stmt).all())

class MateriaRepository(CRUDBase[Materia, MateriaCreate, MateriaBase]):
    def __init__(self):
        super().__init__(Materia)

class MateriaCursoProfesorRepository(CRUDBase[MateriaCursoProfesor, MateriaCursoProfesorCreate, MateriaCursoProfesorBase]):
    def __init__(self):
        super().__init__(MateriaCursoProfesor)

    def get_by_materia_y_curso(self, db: Session, id_materia: int, id_curso: int) -> Optional[MateriaCursoProfesor]:
        stmt = select(MateriaCursoProfesor).where(
            MateriaCursoProfesor.id_materia == id_materia,
            MateriaCursoProfesor.id_curso == id_curso,
        )
        return db.scalars(stmt).first()

    def get_by_curso(self, db: Session, id_curso: int) -> List[MateriaCursoProfesor]:
        stmt = select(MateriaCursoProfesor).where(MateriaCursoProfesor.id_curso == id_curso)
        return list(db.scalars(stmt).all())

    def get_by_profesor(self, db: Session, legajo_profesor: str) -> List[MateriaCursoProfesor]:
        stmt = select(MateriaCursoProfesor).where(MateriaCursoProfesor.legajo_profesor == legajo_profesor)
        return list(db.scalars(stmt).all())

nivel_repository = NivelEducativoRepository()
curso_repository = CursoRepository()
materia_repository = MateriaRepository()
materia_curso_profesor_repository = MateriaCursoProfesorRepository()