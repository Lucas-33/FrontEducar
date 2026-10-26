from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.personas import Alumno, Padre, PadreAlumno, Profesor
from backend.app.repositories.base import CRUDBase
from backend.app.schemas.personas import (
    AlumnoCreate,
    AlumnoUpdate,
    PadreAlumnoBase,
    PadreAlumnoCreate,
    PadreCreate,
    PadreUpdate,
    ProfesorCreate,
    ProfesorUpdate,
)


class AlumnoRepository(CRUDBase[Alumno, AlumnoCreate, AlumnoUpdate]):
    def __init__(self):
        super().__init__(Alumno)

    def get_by_legajo(self, db: Session, legajo: int) -> Alumno | None:
        stmt = select(Alumno).where(Alumno.legajo == legajo)
        return db.scalars(stmt).first()

    def get_by_dni(self, db: Session, dni: str) -> Alumno | None:
        stmt = select(Alumno).where(Alumno.dni == dni)
        return db.scalars(stmt).first()

    def get_by_curso(self, db: Session, id_curso: int) -> list[Alumno]:
        stmt = select(Alumno).where(Alumno.id_curso == id_curso)
        return list(db.scalars(stmt).all())

    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> list[Alumno]:
        stmt = (
            select(Alumno)
            .where(Alumno.estado_alumno == "ACTIVO")
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def soft_delete(self, db: Session, legajo: int) -> Alumno | None:
        alumno = self.get_by_legajo(db, legajo)
        if alumno:
            alumno.estado_alumno = "INACTIVO"
            db.commit()
            db.refresh(alumno)
        return alumno


class ProfesorRepository(CRUDBase[Profesor, ProfesorCreate, ProfesorUpdate]):
    def __init__(self):
        super().__init__(Profesor)

    def get_by_legajo(self, db: Session, legajo: int) -> Profesor | None:
        stmt = select(Profesor).where(Profesor.legajo == legajo)
        return db.scalars(stmt).first()

    def get_by_dni(self, db: Session, dni: str) -> Profesor | None:
        stmt = select(Profesor).where(Profesor.dni == dni)
        return db.scalars(stmt).first()

    def get_activos(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> list[Profesor]:
        stmt = (
            select(Profesor)
            .where(Profesor.estado == "ACTIVO")
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def soft_delete(self, db: Session, legajo: int) -> Profesor | None:
        profesor = self.get_by_legajo(db, legajo)
        if profesor:
            profesor.estado = "INACTIVO"
            db.commit()
            db.refresh(profesor)
        return profesor


class PadreRepository(CRUDBase[Padre, PadreCreate, PadreUpdate]):
    def __init__(self):
        super().__init__(Padre)

    def get_by_dni(self, db: Session, dni: str) -> Padre | None:
        stmt = select(Padre).where(Padre.dni == dni)
        return db.scalars(stmt).first()


class PadreAlumnoRepository(CRUDBase[PadreAlumno, PadreAlumnoCreate, PadreAlumnoBase]):
    def __init__(self):
        super().__init__(PadreAlumno)

    def get_relacion(
        self, db: Session, id_padre: int, legajo_alumno: int
    ) -> PadreAlumno | None:
        stmt = select(PadreAlumno).where(
            PadreAlumno.id_padre == id_padre,
            PadreAlumno.legajo_alumno == legajo_alumno,
        )
        return db.scalars(stmt).first()

    def get_alumnos_por_padre(self, db: Session, id_padre: int) -> list[PadreAlumno]:
        stmt = select(PadreAlumno).where(PadreAlumno.id_padre == id_padre)
        return list(db.scalars(stmt).all())

    def get_padres_por_alumno(
        self, db: Session, legajo_alumno: int
    ) -> list[PadreAlumno]:
        stmt = select(PadreAlumno).where(PadreAlumno.legajo_alumno == legajo_alumno)
        return list(db.scalars(stmt).all())


alumno_repository = AlumnoRepository()
profesor_repository = ProfesorRepository()
padre_repository = PadreRepository()
padre_alumno_repository = PadreAlumnoRepository()
