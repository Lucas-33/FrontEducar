from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# --- ROL ---
class RolBase(BaseModel):
    nombre: str

class RolCreate(RolBase):
    pass

class RolResponse(RolBase):
    id_rol: int
    model_config = ConfigDict(from_attributes=True)

# --- USUARIO ---
class UsuarioBase(BaseModel):
    username: str
    id_rol: int
    legajo_alumno: Optional[str] = None
    legajo_profesor: Optional[str] = None
    id_padre: Optional[int] = None
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    id_rol: Optional[int] = None
    activo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    creado_en: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# --- AUTENTICACIÓN / JWT ---
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[str] = None