"""Dependencias de autenticación y autorización para la API.

Centraliza la validación del token JWT y el control de acceso por rol,
para que todos los endpoints exijan sesión válida (y rol cuando corresponda).
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.services.seguridad import seguridad_service

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Devuelve el usuario dueño del token Bearer o lanza 401/403."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return seguridad_service.get_usuario_from_token(db, credentials.credentials)


def require_roles(*roles: str):
    """Genera una dependencia que exige que el usuario tenga uno de los roles dados."""

    def verificar_rol(
        current_user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        rol = seguridad_service.get_rol_nombre(db, current_user)
        if rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )
        return current_user

    return verificar_rol
