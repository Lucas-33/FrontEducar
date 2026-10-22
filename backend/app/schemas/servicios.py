from datetime import date

from pydantic import BaseModel, ConfigDict


# --- HORARIO ---
class HorarioBase(BaseModel):
    descripcion: str


class HorarioCreate(HorarioBase):
    pass


class HorarioUpdate(BaseModel):
    descripcion: str | None = None


class HorarioResponse(HorarioBase):
    id_horario: int
    model_config = ConfigDict(from_attributes=True)


# --- DEPORTE ---
class DeporteBase(BaseModel):
    nombre: str
    legajo_profesor_responsable: int | None = None


class DeporteCreate(DeporteBase):
    pass


class DeporteUpdate(BaseModel):
    nombre: str | None = None
    legajo_profesor_responsable: int | None = None


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


class GrupoDeporteUpdate(BaseModel):
    id_deporte: int | None = None
    id_nivel: int | None = None
    id_horario: int | None = None


class GrupoDeporteResponse(GrupoDeporteBase):
    id_grupo: int
    model_config = ConfigDict(from_attributes=True)


# --- INSCRIPCION DEPORTE ---
class InscripcionDeporteCreate(BaseModel):
    legajo_alumno: int
    id_grupo: int


class InscripcionDeporteResponse(InscripcionDeporteCreate):
    fecha_inscripcion: date
    model_config = ConfigDict(from_attributes=True)


# --- TRANSPORTE ---
class RecorridoTransporteBase(BaseModel):
    descripcion: str


class RecorridoTransporteCreate(RecorridoTransporteBase):
    pass


class RecorridoTransporteUpdate(BaseModel):
    descripcion: str | None = None


class RecorridoTransporteResponse(RecorridoTransporteBase):
    id_recorrido: int
    model_config = ConfigDict(from_attributes=True)


class InscripcionTransporteCreate(BaseModel):
    legajo_alumno: int
    id_recorrido: int


class InscripcionTransporteResponse(InscripcionTransporteCreate):
    fecha_alta: date
    estado: str
    model_config = ConfigDict(from_attributes=True)


# --- COMEDOR ---
class InscripcionComedorCreate(BaseModel):
    legajo_alumno: int


class InscripcionComedorResponse(InscripcionComedorCreate):
    fecha_alta: date
    estado: str
    model_config = ConfigDict(from_attributes=True)


# --- DETALLES (con nombres resueltos para las tablas del panel admin) ---
class GrupoDeporteDetalleResponse(BaseModel):
    id_grupo: int
    id_deporte: int
    deporte: str
    id_nivel: int
    nivel: str
    id_horario: int
    horario: str


class InscripcionDeporteDetalleResponse(BaseModel):
    legajo_alumno: int
    alumno: str
    id_grupo: int
    deporte: str
    fecha_inscripcion: date


class InscripcionTransporteDetalleResponse(BaseModel):
    legajo_alumno: int
    alumno: str
    id_recorrido: int
    recorrido: str
    fecha_alta: date
    estado: str


class InscripcionComedorDetalleResponse(BaseModel):
    legajo_alumno: int
    alumno: str
    fecha_alta: date
    estado: str
