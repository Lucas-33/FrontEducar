from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.repositories import (
    horario_repository,
    deporte_repository,
    grupo_deporte_repository,
    inscripcion_deporte_repository,
    recorrido_transporte_repository,
    inscripcion_transporte_repository,
    inscripcion_comedor_repository,
    alumno_repository,
    nivel_repository,
)
from backend.app.schemas.servicios import (
    DeporteCreate, GrupoDeporteCreate, InscripcionDeporteCreate,
    RecorridoTransporteCreate, InscripcionTransporteCreate, InscripcionComedorCreate
)

class ServiciosEscolaresService:
    # --- DEPORTES Y GRUPOS ---
    def create_deporte(self, db: Session, deporte_in: DeporteCreate):
        return deporte_repository.create(db, deporte_in)

    def get_deportes(self, db: Session):
        return deporte_repository.get_multi(db)

    def create_grupo_deporte(self, db: Session, grupo_in: GrupoDeporteCreate):
        if not deporte_repository.get(db, grupo_in.id_deporte):
            raise HTTPException(status_code=404, detail="Deporte no encontrado")
        if not nivel_repository.get(db, grupo_in.id_nivel):
            raise HTTPException(status_code=404, detail="Nivel educativo no encontrado")
        if not horario_repository.get(db, grupo_in.id_horario):
            raise HTTPException(status_code=404, detail="Horario no encontrado")
        return grupo_deporte_repository.create(db, grupo_in)

    def inscribir_deporte(self, db: Session, inscripcion_in: InscripcionDeporteCreate):
        if not alumno_repository.get_by_legajo(db, inscripcion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")
        if not grupo_deporte_repository.get(db, inscripcion_in.id_grupo):
            raise HTTPException(status_code=404, detail="El grupo deportivo no existe")
        if inscripcion_deporte_repository.get_inscripcion(db, inscripcion_in.legajo_alumno, inscripcion_in.id_grupo):
            raise HTTPException(status_code=400, detail="El alumno ya está inscripto en este grupo")
        return inscripcion_deporte_repository.create(db, inscripcion_in)

    # --- TRANSPORTE ---
    def create_recorrido(self, db: Session, recorrido_in: RecorridoTransporteCreate):
        return recorrido_transporte_repository.create(db, recorrido_in)

    def get_recorridos(self, db: Session):
        return recorrido_transporte_repository.get_multi(db)

    def inscribir_transporte(self, db: Session, inscripcion_in: InscripcionTransporteCreate):
        if not alumno_repository.get_by_legajo(db, inscripcion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")
        if not recorrido_transporte_repository.get(db, inscripcion_in.id_recorrido):
            raise HTTPException(status_code=404, detail="El recorrido no existe")
        
        existente = inscripcion_transporte_repository.get_by_alumno(db, inscripcion_in.legajo_alumno)
        if existente and existente.estado == "ACTIVO":
            raise HTTPException(status_code=400, detail="El alumno ya cuenta con inscripción activa en transporte")
        return inscripcion_transporte_repository.create(db, inscripcion_in)

    def baja_transporte(self, db: Session, legajo_alumno: str):
        res = inscripcion_transporte_repository.soft_delete(db, legajo_alumno)
        if not res:
            raise HTTPException(status_code=404, detail="Inscripción de transporte no encontrada")
        return res

    # --- COMEDOR ---
    def inscribir_comedor(self, db: Session, inscripcion_in: InscripcionComedorCreate):
        if not alumno_repository.get_by_legajo(db, inscripcion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")
        
        existente = inscripcion_comedor_repository.get_by_alumno(db, inscripcion_in.legajo_alumno)
        if existente and existente.estado == "ACTIVO":
            raise HTTPException(status_code=400, detail="El alumno ya cuenta con inscripción activa en comedor")
        return inscripcion_comedor_repository.create(db, inscripcion_in)

    def baja_comedor(self, db: Session, legajo_alumno: str):
        res = inscripcion_comedor_repository.soft_delete(db, legajo_alumno)
        if not res:
            raise HTTPException(status_code=404, detail="Inscripción de comedor no encontrada")
        return res

servicios_escolares_service = ServiciosEscolaresService()