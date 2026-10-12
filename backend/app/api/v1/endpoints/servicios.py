from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.servicios import (
    DeporteCreate, DeporteResponse,
    GrupoDeporteCreate, GrupoDeporteResponse,
    InscripcionDeporteCreate, InscripcionDeporteResponse,
    RecorridoTransporteCreate, RecorridoTransporteResponse,
    InscripcionTransporteCreate, InscripcionTransporteResponse,
    InscripcionComedorCreate, InscripcionComedorResponse,
)
from backend.app.services.servicios import servicios_escolares_service

router = APIRouter()

# --- DEPORTES ---
@router.get("/deportes", response_model=List[DeporteResponse], summary="Listar deportes")
def listar_deportes(db: Session = Depends(get_db)):
    return servicios_escolares_service.get_deportes(db)

@router.post("/deportes", response_model=DeporteResponse, status_code=status.HTTP_201_CREATED, summary="Crear deporte")
def crear_deporte(deporte_in: DeporteCreate, db: Session = Depends(get_db)):
    return servicios_escolares_service.create_deporte(db, deporte_in)

@router.post("/deportes/grupos", response_model=GrupoDeporteResponse, status_code=status.HTTP_201_CREATED, summary="Crear grupo de deporte")
def crear_grupo_deporte(grupo_in: GrupoDeporteCreate, db: Session = Depends(get_db)):
    return servicios_escolares_service.create_grupo_deporte(db, grupo_in)

@router.post("/deportes/inscripciones", response_model=InscripcionDeporteResponse, status_code=status.HTTP_201_CREATED, summary="Inscribir alumno a deporte")
def inscribir_deporte(inscripcion_in: InscripcionDeporteCreate, db: Session = Depends(get_db)):
    return servicios_escolares_service.inscribir_deporte(db, inscripcion_in)

# --- TRANSPORTE ---
@router.get("/transporte/recorridos", response_model=List[RecorridoTransporteResponse], summary="Listar recorridos de transporte")
def listar_recorridos(db: Session = Depends(get_db)):
    return servicios_escolares_service.get_recorridos(db)

@router.post("/transporte/recorridos", response_model=RecorridoTransporteResponse, status_code=status.HTTP_201_CREATED, summary="Crear recorrido de transporte")
def crear_recorrido(recorrido_in: RecorridoTransporteCreate, db: Session = Depends(get_db)):
    return servicios_escolares_service.create_recorrido(db, recorrido_in)

@router.post("/transporte/inscripciones", response_model=InscripcionTransporteResponse, status_code=status.HTTP_201_CREATED, summary="Inscribir alumno a transporte")
def inscribir_transporte(inscripcion_in: InscripcionTransporteCreate, db: Session = Depends(get_db)):
    return servicios_escolares_service.inscribir_transporte(db, inscripcion_in)

@router.delete("/transporte/inscripciones/{legajo_alumno}", response_model=InscripcionTransporteResponse, summary="Baja de transporte")
def baja_transporte(legajo_alumno: str, db: Session = Depends(get_db)):
    return servicios_escolares_service.baja_transporte(db, legajo_alumno)

# --- COMEDOR ---
@router.post("/comedor/inscripciones", response_model=InscripcionComedorResponse, status_code=status.HTTP_201_CREATED, summary="Inscribir alumno a comedor")
def inscribir_comedor(inscripcion_in: InscripcionComedorCreate, db: Session = Depends(get_db)):
    return servicios_escolares_service.inscribir_comedor(db, inscripcion_in)

@router.delete("/comedor/inscripciones/{legajo_alumno}", response_model=InscripcionComedorResponse, summary="Baja de comedor")
def baja_comedor(legajo_alumno: str, db: Session = Depends(get_db)):
    return servicios_escolares_service.baja_comedor(db, legajo_alumno)