from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

# --- HORARIO ---
class HorarioBase(BaseModel):
    descripcion: str

class HorarioCreate(HorarioBase):
    pass

class HorarioResponse(HorarioBase):
    id_horario: int
    model_config = ConfigDict(from_attributes=True)

# --- DEPORTE ---
class DeporteBase(BaseModel):
    nombre: str
    legajo_profesor_responsable: Optional[str] = None

class DeporteCreate(DeporteBase):
    pass

class DeporteResponse(DeporteBase):
    id_deporte: int
    model_config = ConfigDict(from_attributes=True)

# --- GRUPO DEPORTE ---
class GrupoDeporteBase(BaseModel):
    id_deporte: int
    id_nivel: int
    id_horario: int

class GrupoDeporteCreate(GrupoDeporteBase):
    pass

class GrupoDeporteResponse(GrupoDeporteBase):
    id_grupo: int
    model_config = ConfigDict(from_attributes=True)

# --- INSCRIPCION DEPORTE ---
class InscripcionDeporteCreate(BaseModel):
    legajo_alumno: str
    id_grupo: int

class InscripcionDeporteResponse(InscripcionDeporteCreate):
    fecha_inscripcion: date
    model_config = ConfigDict(from_attributes=True)

# --- TRANSPORTE ---
class RecorridoTransporteBase(BaseModel):
    descripcion: str

class RecorridoTransporteCreate(RecorridoTransporteBase):
    pass

class RecorridoTransporteResponse(RecorridoTransporteBase):
    id_recorrido: int
    model_config = ConfigDict(from_attributes=True)

class InscripcionTransporteCreate(BaseModel):
    legajo_alumno: str
    id_recorrido: int

class InscripcionTransporteResponse(InscripcionTransporteCreate):
    fecha_alta: date
    estado: str
    model_config = ConfigDict(from_attributes=True)

# --- COMEDOR ---
class InscripcionComedorCreate(BaseModel):
    legajo_alumno: str

class InscripcionComedorResponse(InscripcionComedorCreate):
    fecha_alta: date
    estado: str
    model_config = ConfigDict(from_attributes=True)