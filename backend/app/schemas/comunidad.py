from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- SOLICITUD DE INSCRIPCIÓN ---
class SolicitudInscripcionCreate(BaseModel):
    postulante: str = Field(min_length=3, max_length=120)
    dni: str = Field(min_length=6, max_length=20)
    fecha_nacimiento: Optional[str] = Field(default=None, max_length=20)
    nivel: str = Field(min_length=3, max_length=80)
    tutor: str = Field(min_length=3, max_length=120)
    telefono: Optional[str] = Field(default=None, max_length=50)
    correo: Optional[str] = Field(default=None, max_length=120)

class SolicitudInscripcionEstadoUpdate(BaseModel):
    estado: str = Field(pattern="^(Pendiente|Aprobado|Rechazado)$")
    observaciones: Optional[str] = Field(default=None, max_length=300)

class SolicitudInscripcionResponse(BaseModel):
    id_solicitud: int
    postulante: str
    dni: str
    fecha_nacimiento: Optional[str] = None
    nivel: str
    tutor: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    fecha: date
    estado: str
    observaciones: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# --- MENSAJE DE CONTACTO ---
class MensajeContactoCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    telefono: Optional[str] = Field(default=None, max_length=50)
    correo: str = Field(min_length=5, max_length=120)
    mensaje: str = Field(min_length=5)

class MensajeContactoResponse(BaseModel):
    id_mensaje: int
    nombre: str
    telefono: Optional[str] = None
    correo: str
    mensaje: str
    fecha: datetime
    leido: bool
    model_config = ConfigDict(from_attributes=True)


# --- OPINIÓN ---
class OpinionCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    vinculo: Optional[str] = Field(default=None, max_length=80)
    comentario: str = Field(min_length=5)
    estrellas: int = Field(default=5, ge=1, le=5)

class OpinionResponse(BaseModel):
    id_opinion: int
    nombre: str
    vinculo: Optional[str] = None
    comentario: str
    estrellas: int
    fecha: date
    aprobada: bool
    model_config = ConfigDict(from_attributes=True)


# --- POSTULACIÓN LABORAL ---
class PostulacionEmpleoCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    correo: str = Field(min_length=5, max_length=120)
    telefono: Optional[str] = Field(default=None, max_length=50)
    puesto: str = Field(default="Postulación espontánea", max_length=150)
    area: Optional[str] = Field(default=None, max_length=120)
    mensaje: Optional[str] = None

class PostulacionEmpleoResponse(BaseModel):
    id_postulacion: int
    nombre: str
    correo: str
    telefono: Optional[str] = None
    puesto: str
    area: Optional[str] = None
    mensaje: Optional[str] = None
    fecha: datetime
    model_config = ConfigDict(from_attributes=True)
