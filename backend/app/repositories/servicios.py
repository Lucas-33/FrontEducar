from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.servicios import (
    Horario, Deporte, GrupoDeporte, InscripcionDeporte,
    RecorridoTransporte, InscripcionTransporte, InscripcionComedor,
)
from backend.app.schemas.servicios import (
    HorarioCreate, HorarioBase,
    DeporteCreate, DeporteBase,
    GrupoDeporteCreate, GrupoDeporteBase,
    InscripcionDeporteCreate,
    RecorridoTransporteCreate, RecorridoTransporteBase,
    InscripcionTransporteCreate,
    InscripcionComedorCreate,
)
from backend.app.repositories.base import CRUDBase

class HorarioRepository(CRUDBase[Horario, HorarioCreate, HorarioBase]):
    def __init__(self):
        super().__init__(Horario)

class DeporteRepository(CRUDBase[Deporte, DeporteCreate, DeporteBase]):
    def __init__(self):
        super().__init__(Deporte)

class GrupoDeporteRepository(CRUDBase[GrupoDeporte, GrupoDeporteCreate, GrupoDeporteBase]):
    def __init__(self):
        super().__init__(GrupoDeporte)

    def get_by_deporte(self, db: Session, id_deporte: int) -> List[GrupoDeporte]:
        stmt = select(GrupoDeporte).where(GrupoDeporte.id_deporte == id_deporte)
        return list(db.scalars(stmt).all())

class InscripcionDeporteRepository(CRUDBase[InscripcionDeporte, InscripcionDeporteCreate, InscripcionDeporteCreate]):
    def __init__(self):
        super().__init__(InscripcionDeporte)

    def get_inscripcion(self, db: Session, legajo_alumno: int, id_grupo: int) -> Optional[InscripcionDeporte]:
        stmt = select(InscripcionDeporte).where(
            InscripcionDeporte.legajo_alumno == legajo_alumno,
            InscripcionDeporte.id_grupo == id_grupo,
        )
        return db.scalars(stmt).first()

    def get_by_alumno(self, db: Session, legajo_alumno: int) -> List[InscripcionDeporte]:
        stmt = select(InscripcionDeporte).where(InscripcionDeporte.legajo_alumno == legajo_alumno)
        return list(db.scalars(stmt).all())

class RecorridoTransporteRepository(CRUDBase[RecorridoTransporte, RecorridoTransporteCreate, RecorridoTransporteBase]):
    def __init__(self):
        super().__init__(RecorridoTransporte)

class InscripcionTransporteRepository(CRUDBase[InscripcionTransporte, InscripcionTransporteCreate, InscripcionTransporteCreate]):
    def __init__(self):
        super().__init__(InscripcionTransporte)

    def get_by_alumno(self, db: Session, legajo_alumno: int) -> Optional[InscripcionTransporte]:
        return db.get(InscripcionTransporte, legajo_alumno)

    def soft_delete(self, db: Session, legajo_alumno: int) -> Optional[InscripcionTransporte]:
        inscripcion = self.get_by_alumno(db, legajo_alumno)
        if inscripcion:
            inscripcion.estado = "INACTIVO"
            db.commit()
            db.refresh(inscripcion)
        return inscripcion

class InscripcionComedorRepository(CRUDBase[InscripcionComedor, InscripcionComedorCreate, InscripcionComedorCreate]):
    def __init__(self):
        super().__init__(InscripcionComedor)

    def get_by_alumno(self, db: Session, legajo_alumno: int) -> Optional[InscripcionComedor]:
        return db.get(InscripcionComedor, legajo_alumno)

    def soft_delete(self, db: Session, legajo_alumno: int) -> Optional[InscripcionComedor]:
        inscripcion = self.get_by_alumno(db, legajo_alumno)
        if inscripcion:
            inscripcion.estado = "INACTIVO"
            db.commit()
            db.refresh(inscripcion)
        return inscripcion

horario_repository = HorarioRepository()
deporte_repository = DeporteRepository()
grupo_deporte_repository = GrupoDeporteRepository()
inscripcion_deporte_repository = InscripcionDeporteRepository()
recorrido_transporte_repository = RecorridoTransporteRepository()
inscripcion_transporte_repository = InscripcionTransporteRepository()
inscripcion_comedor_repository = InscripcionComedorRepository()