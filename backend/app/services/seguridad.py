import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.seguridad import Usuario
from backend.app.repositories import (
    usuario_repository,
    rol_repository,
    alumno_repository,
    profesor_repository,
    padre_repository,
)
from backend.app.schemas.seguridad import (
    UsuarioCreate, UsuarioUpdate, Token, UsuarioAdminResponse,
)

SECRET_KEY = os.getenv("SECRET_KEY", "educar_secret_key_super_segura_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas


class SeguridadService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña plana contra el hash bcrypt almacenado."""
        if not plain_password or not hashed_password:
            return False
        try:
            password_bytes = plain_password.encode("utf-8")[:72]
            hashed_bytes = (
                hashed_password.encode("utf-8")
                if isinstance(hashed_password, str)
                else hashed_password
            )
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera un hash bcrypt seguro en formato string ($2b$)."""
        password_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

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

    def get_usuario_from_token(self, db: Session, token: str) -> Usuario:
        """Decodifica el JWT y devuelve la entidad Usuario. Lanza 401/403 si no es válido."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token expiró. Inicie sesión nuevamente.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        user = usuario_repository.get_by_username(db, username) if username else None
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El usuario del token no existe",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario se encuentra inactivo",
            )
        return user

    def get_rol_nombre(self, db: Session, user: Usuario) -> str:
        """Devuelve el nombre del rol (ADMIN, TEACHER, PARENT, STUDENT) del usuario."""
        rol = rol_repository.get(db, user.id_rol)
        return rol.nombre if rol else ""

    def get_perfil_from_token(self, db: Session, token: str) -> UsuarioAdminResponse:
        """Decodifica el JWT y devuelve el perfil del usuario autenticado."""
        user = self.get_usuario_from_token(db, token)
        return self._to_admin_response(db, user)

    def change_password(self, db: Session, user: Usuario, password_actual: str, password_nueva: str) -> dict:
        """Cambia la contraseña del propio usuario autenticado."""
        if not self.verify_password(password_actual, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual no es correcta",
            )
        if len(password_nueva or "") < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe tener al menos 6 caracteres",
            )
        user.password_hash = self.get_password_hash(password_nueva)
        db.commit()
        return {"detail": "Contraseña actualizada correctamente"}

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

    # ================= ADMINISTRACIÓN DE USUARIOS =================
    def get_roles(self, db: Session):
        return rol_repository.get_multi(db)

    def _to_admin_response(self, db: Session, user) -> UsuarioAdminResponse:
        rol = rol_repository.get(db, user.id_rol)
        rol_nombre = rol.nombre if rol else ""

        if user.legajo_alumno:
            alumno = alumno_repository.get_by_legajo(db, user.legajo_alumno)
            vinculacion = (
                f"Alumno: {alumno.apellido}, {alumno.nombre} (#{alumno.legajo})"
                if alumno
                else f"Alumno #{user.legajo_alumno}"
            )
        elif user.legajo_profesor:
            profesor = profesor_repository.get_by_legajo(db, user.legajo_profesor)
            vinculacion = (
                f"Docente: {profesor.apellido}, {profesor.nombre} (#{profesor.legajo})"
                if profesor
                else f"Docente #{user.legajo_profesor}"
            )
        elif user.id_padre:
            padre = padre_repository.get(db, user.id_padre)
            vinculacion = (
                f"Tutor: {padre.apellido}, {padre.nombre}"
                if padre
                else f"Tutor #{user.id_padre}"
            )
        elif rol_nombre == "ADMIN":
            vinculacion = "Acceso Total"
        else:
            vinculacion = "Sin vínculo"

        return UsuarioAdminResponse(
            id_usuario=user.id_usuario,
            username=user.username,
            id_rol=user.id_rol,
            legajo_alumno=user.legajo_alumno,
            legajo_profesor=user.legajo_profesor,
            id_padre=user.id_padre,
            activo=user.activo,
            creado_en=user.creado_en,
            rol=rol_nombre,
            vinculacion=vinculacion,
        )

    def get_usuarios(self, db: Session) -> List[UsuarioAdminResponse]:
        usuarios = usuario_repository.get_multi(db, limit=200)
        return [self._to_admin_response(db, u) for u in usuarios]

    def update_usuario(self, db: Session, id_usuario: int, user_in: UsuarioUpdate) -> UsuarioAdminResponse:
        user = usuario_repository.get(db, id_usuario)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El usuario con ID {id_usuario} no existe",
            )

        data = user_in.model_dump(exclude_unset=True)
        password = data.pop("password", None)
        if password:
            user.password_hash = self.get_password_hash(password)

        nuevo_username = data.get("username")
        if nuevo_username and nuevo_username != user.username:
            if usuario_repository.get_by_username(db, nuevo_username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El nombre de usuario '{nuevo_username}' ya está registrado",
                )

        nuevo_rol = data.get("id_rol")
        if nuevo_rol is not None and not rol_repository.get(db, nuevo_rol):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol con ID {nuevo_rol} no existe",
            )

        for field, value in data.items():
            if value is not None:
                setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return self._to_admin_response(db, user)


seguridad_service = SeguridadService()