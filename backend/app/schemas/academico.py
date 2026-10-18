from typing import Optional
from pydantic import BaseModel, ConfigDict

# --- NIVEL EDUCATIVO ---
class NivelEducativoBase(BaseModel):
    nombre: str

class NivelEducativoCreate(NivelEducativoBase):
    pass

class NivelEducativoResponse(NivelEducativoBase):
    id_nivel: int
    model_config = ConfigDict(from_attributes=True)

# --- CURSO ---
class CursoBase(BaseModel):
    nombre: str
    id_nivel: int

class CursoCreate(CursoBase):
    pass

class CursoResponse(CursoBase):
    id_curso: int
    model_config = ConfigDict(from_attributes=True)

# --- MATERIA ---
class MateriaBase(BaseModel):
    nombre: str

class MateriaCreate(MateriaBase):
    pass

class MateriaResponse(MateriaBase):
    id_materia: int
    model_config = ConfigDict(from_attributes=True)

# --- MATERIA CURSO PROFESOR ---
class MateriaCursoProfesorBase(BaseModel):
    id_materia: int
    id_curso: int
    legajo_profesor: int

class MateriaCursoProfesorCreate(MateriaCursoProfesorBase):
    pass

class MateriaCursoProfesorResponse(MateriaCursoProfesorBase):
    model_config = ConfigDict(from_attributes=True)

# --- ASIGNACIÓN CON DETALLE (materia + curso + nivel + profesor) ---
class AsignacionDetalleResponse(BaseModel):
    id_materia: int
    materia: str
    id_curso: int
    curso: str
    id_nivel: int
    nivel: str
    legajo_profesor: int
    profesor: str

# --- ACTUALIZACIONES (PUT) ---
class NivelEducativoUpdate(BaseModel):
    nombre: Optional[str] = None

class CursoUpdate(BaseModel):
    nombre: Optional[str] = None
    id_nivel: Optional[int] = None

class MateriaUpdate(BaseModel):
    nombre: Optional[str] = None

class MateriaCursoProfesorUpdate(BaseModel):
    id_materia: Optional[int] = None
    id_curso: Optional[int] = None
    legajo_profesor: Optional[int] = None