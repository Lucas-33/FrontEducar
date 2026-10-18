from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- CALIFICACIONES ---
class CalificacionBase(BaseModel):
    legajo_alumno: int
    id_materia: int
    id_curso: int
    periodo: str = Field(min_length=2, max_length=30)
    tipo: str = Field(min_length=2, max_length=30)
    nota: float = Field(ge=0, le=10)
    fecha: Optional[date] = None
    observacion: Optional[str] = Field(default=None, max_length=200)

class CalificacionCreate(CalificacionBase):
    pass

class CalificacionUpdate(BaseModel):
    periodo: Optional[str] = Field(default=None, max_length=30)
    tipo: Optional[str] = Field(default=None, max_length=30)
    nota: Optional[float] = Field(default=None, ge=0, le=10)
    fecha: Optional[date] = None
    observacion: Optional[str] = Field(default=None, max_length=200)

class CalificacionResponse(CalificacionBase):
    id_calificacion: int
    legajo_profesor: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class CalificacionDetalleResponse(BaseModel):
    """Calificación con nombres resueltos para las tablas de la interfaz."""
    id_calificacion: int
    legajo_alumno: int
    alumno: str
    id_materia: int
    materia: str
    id_curso: int
    curso: str
    periodo: str
    tipo: str
    nota: float
    fecha: date
    observacion: Optional[str] = None


# --- ASISTENCIA ---
class AsistenciaItemCreate(BaseModel):
    legajo_alumno: int
    estado: str = Field(pattern="^(PRESENTE|AUSENTE|TARDE|JUSTIFICADO)$")
    observacion: Optional[str] = Field(default=None, max_length=200)

class AsistenciaLoteCreate(BaseModel):
    """Carga rápida de asistencia de un curso completo para una fecha."""
    id_curso: int
    fecha: Optional[date] = None
    registros: List[AsistenciaItemCreate] = Field(min_length=1)

class AsistenciaResponse(BaseModel):
    id_asistencia: int
    legajo_alumno: int
    id_curso: int
    fecha: date
    estado: str
    observacion: Optional[str] = None
    legajo_profesor: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class AsistenciaDetalleResponse(BaseModel):
    id_asistencia: int
    legajo_alumno: int
    alumno: str
    id_curso: int
    curso: str
    fecha: date
    estado: str
    observacion: Optional[str] = None

class ResumenAsistenciaResponse(BaseModel):
    legajo_alumno: int
    total: int
    presentes: int
    ausentes: int
    tardes: int
    justificados: int
    porcentaje_presentismo: float
