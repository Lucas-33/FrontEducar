import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.repositories import usuario_repository, rol_repository
from backend.app.schemas.seguridad import UsuarioCreate, UsuarioUpdate, Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "educar_secret_key_super_segura_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas

class SeguridadService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def authenticate_user(self, db: Session, username: str, password: str):
        user = usuario_repository.get_by_username(db, username=username)
        if not user or not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario se encuentra inactivo",
            )
        return user

    def login(self, db: Session, username: str, password: str) -> Token:
        user = self.authenticate_user(db, username, password)
        rol = rol_repository.get(db, user.id_rol)
        rol_nombre = rol.nombre if rol else "USER"
        
        token_data = {
            "sub": user.username,
            "id_usuario": user.id_usuario,
            "rol": rol_nombre,
        }
        access_token = self.create_access_token(data=token_data)
        return Token(
            access_token=access_token,
            token_type="bearer",
            rol=rol_nombre,
            username=user.username,
        )

    def registrar_usuario(self, db: Session, user_in: UsuarioCreate):
        if usuario_repository.get_by_username(db, user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El nombre de usuario '{user_in.username}' ya está registrado",
            )
        if not rol_repository.get(db, user_in.id_rol):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol con ID {user_in.id_rol} no existe",
            )
        hashed_pwd = self.get_password_hash(user_in.password)
        return usuario_repository.create_user_with_hash(db, user_in, hashed_pwd)

seguridad_service = SeguridadService()