from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.evaluacion import Asistencia, Calificacion
from backend.app.repositories.base import CRUDBase
from backend.app.schemas.evaluacion import (
    AsistenciaLoteCreate,
    CalificacionCreate,
    CalificacionUpdate,
)


class CalificacionRepository(
    CRUDBase[Calificacion, CalificacionCreate, CalificacionUpdate]
):
    def __init__(self):
        super().__init__(Calificacion)

    def get_by_alumno(
        self, db: Session, legajo_alumno: int, limit: int = 500
    ) -> list[Calificacion]:
        stmt = (
            select(Calificacion)
            .where(Calificacion.legajo_alumno == legajo_alumno)
            .order_by(Calificacion.id_calificacion.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def get_by_curso(
        self, db: Session, id_curso: int, limit: int = 500
    ) -> list[Calificacion]:
        stmt = (
            select(Calificacion)
            .where(Calificacion.id_curso == id_curso)
            .order_by(Calificacion.id_calificacion.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def get_by_materia_curso(
        self, db: Session, id_materia: int, id_curso: int, limit: int = 500
    ) -> list[Calificacion]:
        stmt = (
            select(Calificacion)
            .where(
                Calificacion.id_materia == id_materia, Calificacion.id_curso == id_curso
            )
            .order_by(Calificacion.id_calificacion.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())


class AsistenciaRepository(
    CRUDBase[Asistencia, AsistenciaLoteCreate, AsistenciaLoteCreate]
):
    def __init__(self):
        super().__init__(Asistencia)

    def get_by_alumno(
        self, db: Session, legajo_alumno: int, limit: int = 500
    ) -> list[Asistencia]:
        stmt = (
            select(Asistencia)
            .where(Asistencia.legajo_alumno == legajo_alumno)
            .order_by(Asistencia.fecha.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def get_by_curso_fecha(
        self, db: Session, id_curso: int, fecha: date
    ) -> list[Asistencia]:
        stmt = select(Asistencia).where(
            Asistencia.id_curso == id_curso, Asistencia.fecha == fecha
        )
        return list(db.scalars(stmt).all())

    def get_registro(
        self, db: Session, legajo_alumno: int, fecha: date
    ) -> Asistencia | None:
        stmt = select(Asistencia).where(
            Asistencia.legajo_alumno == legajo_alumno, Asistencia.fecha == fecha
        )
        return db.scalars(stmt).first()


calificacion_repository = CalificacionRepository()
asistencia_repository = AsistenciaRepository()
