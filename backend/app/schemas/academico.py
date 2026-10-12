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
    legajo_profesor: str

class MateriaCursoProfesorCreate(MateriaCursoProfesorBase):
    pass

class MateriaCursoProfesorResponse(MateriaCursoProfesorBase):
    model_config = ConfigDict(from_attributes=True)