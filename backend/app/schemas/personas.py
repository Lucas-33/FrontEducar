from datetime import date

from pydantic import BaseModel, ConfigDict


# --- ALUMNO ---
class AlumnoBase(BaseModel):
    legajo: int
    dni: str
    nombre: str
    apellido: str
    fecha_nacimiento: date
    domicilio: str
    telefono: str | None = None
    correo_electronico: str | None = None
    id_curso: int
    estado_alumno: str = "ACTIVO"


class AlumnoCreate(AlumnoBase):
    legajo: int | None = None  # Permite que llegue vacío desde el frontend


class AlumnoUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    fecha_nacimiento: date | None = None
    domicilio: str | None = None
    telefono: str | None = None
    correo_electronico: str | None = None
    id_curso: int | None = None
    estado_alumno: str | None = None


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
    legajo: int | None = None  # Permite que llegue vacío desde el frontend


class ProfesorUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    especialidad: str | None = None
    correo_electronico: str | None = None
    telefono: str | None = None
    estado: str | None = None


class ProfesorResponse(ProfesorBase):
    model_config = ConfigDict(from_attributes=True)


# --- PADRE / TUTOR ---
class PadreBase(BaseModel):
    dni: str
    nombre: str
    apellido: str
    telefono: str | None = None
    correo_electronico: str | None = None


class PadreCreate(PadreBase):
    pass


class PadreUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    telefono: str | None = None
    correo_electronico: str | None = None


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
