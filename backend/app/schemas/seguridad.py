from datetime import datetime

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
    legajo_alumno: int | None = None
    legajo_profesor: int | None = None
    id_padre: int | None = None
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    id_rol: int | None = None
    activo: bool | None = None


class UsuarioResponse(UsuarioBase):
    id_usuario: int
    creado_en: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class UsuarioAdminResponse(UsuarioBase):
    """Vista administrativa: incluye el nombre del rol y el vínculo resuelto."""

    id_usuario: int
    rol: str = ""
    vinculacion: str = "-"
    creado_en: datetime | None = None


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
    username: str | None = None
    rol: str | None = None


class CambioPasswordRequest(BaseModel):
    """Cambio de contraseña del propio usuario autenticado."""

    password_actual: str
    password_nueva: str
