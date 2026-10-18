from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

# --- ALUMNO ---
class AlumnoBase(BaseModel):
    legajo: int
    dni: str
    nombre: str
    apellido: str
    fecha_nacimiento: date
    domicilio: str
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None
    id_curso: int
    estado_alumno: str = "ACTIVO"

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None
    id_curso: Optional[int] = None
    estado_alumno: Optional[str] = None

class AlumnoResponse(AlumnoBase):
    model_config = ConfigDict(from_attributes=True)

# --- PROFESOR ---
class ProfesorBase(BaseModel):
    legajo: int
    dni: str
    nombre: str
    apellido: str
    especialidad: str
    correo_electronico: str
    telefono: str
    estado: str = "ACTIVO"

class ProfesorCreate(ProfesorBase):
    pass

class ProfesorUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    especialidad: Optional[str] = None
    correo_electronico: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None

class ProfesorResponse(ProfesorBase):
    model_config = ConfigDict(from_attributes=True)

# --- PADRE / TUTOR ---
class PadreBase(BaseModel):
    dni: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None

class PadreCreate(PadreBase):
    pass

class PadreUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None

class PadreResponse(PadreBase):
    id_padre: int
    model_config = ConfigDict(from_attributes=True)

# --- PADRE_ALUMNO ---
class PadreAlumnoBase(BaseModel):
    id_padre: int
    legajo_alumno: int

class PadreAlumnoCreate(PadreAlumnoBase):
    pass

class PadreAlumnoResponse(PadreAlumnoBase):
    model_config = ConfigDict(from_attributes=True)