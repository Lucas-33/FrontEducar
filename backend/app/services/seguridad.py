import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.personas import Padre, PadreAlumno
from backend.app.models.seguridad import Usuario
from backend.app.repositories import (
    alumno_repository,
    padre_alumno_repository,
    padre_repository,
    profesor_repository,
    rol_repository,
    usuario_repository,
)
from backend.app.schemas.personas import PadreCreate
from backend.app.schemas.seguridad import (
    Token,
    UsuarioAdminResponse,
    UsuarioCreate,
    UsuarioUpdate,
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)  # 24 horas


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
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
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

    def change_password(
        self, db: Session, user: Usuario, password_actual: str, password_nueva: str
    ) -> dict:
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

    def _validar_alumnos_vinculables(
        self, db: Session, legajos: list[int]
    ) -> list[int]:
        """Valida que todos los legajos existan y devuelve una lista sin repetidos."""
        resultado: list[int] = []
        for legajo in legajos:
            legajo_int = int(legajo)
            if legajo_int in resultado:
                continue
            if not alumno_repository.get_by_legajo(db, legajo_int):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El alumno con legajo #{legajo_int} no existe",
                )
            resultado.append(legajo_int)
        return resultado

    def _sincronizar_alumnos_tutor(
        self, db: Session, id_padre: int | None, legajos: list[int]
    ):
        """Reemplaza los alumnos vinculados al tutor indicado.

        No hace commit: se confirma junto con el resto de la operación del usuario.
        """
        legajos_validos = self._validar_alumnos_vinculables(db, legajos or [])
        if legajos_validos and not id_padre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe indicar los datos del tutor antes de vincular alumnos",
            )
        if not id_padre:
            return
        if not padre_repository.get(db, id_padre):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El tutor con ID {id_padre} no existe",
            )

        relaciones = padre_alumno_repository.get_alumnos_por_padre(db, id_padre)
        actuales = {relacion.legajo_alumno for relacion in relaciones}
        deseados = set(legajos_validos)

        for relacion in relaciones:
            if relacion.legajo_alumno not in deseados:
                db.delete(relacion)
        for legajo in deseados - actuales:
            db.add(PadreAlumno(id_padre=id_padre, legajo_alumno=legajo))

    def _obtener_o_crear_tutor(self, db: Session, tutor_in: PadreCreate) -> Padre:
        """Reutiliza el tutor con ese DNI o lo crea en la misma transacción."""
        padre = padre_repository.get_by_dni(db, tutor_in.dni)
        if padre:
            for campo, valor in tutor_in.model_dump().items():
                if valor is not None:
                    setattr(padre, campo, valor)
            return padre
        padre = Padre(**tutor_in.model_dump())
        db.add(padre)
        db.flush()
        return padre

    def _actualizar_tutor(
        self, db: Session, padre: Padre, tutor_in: PadreCreate
    ) -> None:
        """Actualiza los datos del tutor vinculado al usuario."""
        existente = padre_repository.get_by_dni(db, tutor_in.dni)
        if existente and existente.id_padre != padre.id_padre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otro tutor con el DNI '{tutor_in.dni}'",
            )
        for campo, valor in tutor_in.model_dump().items():
            setattr(padre, campo, valor)

    def registrar_usuario(self, db: Session, user_in: UsuarioCreate):
        if usuario_repository.get_by_username(db, user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El nombre de usuario '{user_in.username}' ya está registrado",
            )
        rol = rol_repository.get(db, user_in.id_rol)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol con ID {user_in.id_rol} no existe",
            )

        if user_in.tutor is not None:
            if rol.nombre != "PARENT":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo los usuarios con rol Padre / Tutor pueden tener datos de tutor",
                )
            if user_in.id_padre is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Indique un tutor existente o los datos de un tutor nuevo, "
                        "no ambos"
                    ),
                )

        legajos_alumnos = user_in.legajos_alumnos
        if legajos_alumnos:
            if rol.nombre != "PARENT":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo los usuarios con rol Padre / Tutor pueden tener alumnos vinculados",
                )
            if not user_in.id_padre and user_in.tutor is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe indicar los datos del tutor para vincular alumnos",
                )
            self._validar_alumnos_vinculables(db, legajos_alumnos)

        if user_in.tutor is not None:
            padre = self._obtener_o_crear_tutor(db, user_in.tutor)
            user_in = user_in.model_copy(update={"id_padre": padre.id_padre})

        hashed_pwd = self.get_password_hash(user_in.password)
        user = usuario_repository.create_user_with_hash(db, user_in, hashed_pwd)
        if legajos_alumnos:
            self._sincronizar_alumnos_tutor(db, user.id_padre, legajos_alumnos)
        db.commit()
        db.refresh(user)
        return user

    # ================= ADMINISTRACIÓN DE USUARIOS =================
    def get_roles(self, db: Session):
        return rol_repository.get_multi(db)

    def _to_admin_response(self, db: Session, user) -> UsuarioAdminResponse:
        rol = rol_repository.get(db, user.id_rol)
        rol_nombre = rol.nombre if rol else ""

        alumnos_vinculados: list[int] = []
        if user.id_padre:
            alumnos_vinculados = [
                relacion.legajo_alumno
                for relacion in padre_alumno_repository.get_alumnos_por_padre(
                    db, user.id_padre
                )
            ]

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
            cantidad = len(alumnos_vinculados)
            vinculacion += (
                f" · {cantidad} alumno{'s' if cantidad != 1 else ''} vinculado"
                f"{'s' if cantidad != 1 else ''}"
                if cantidad
                else " · Sin alumnos vinculados"
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
            alumnos_vinculados=alumnos_vinculados,
        )

    def get_usuarios(self, db: Session) -> list[UsuarioAdminResponse]:
        usuarios = usuario_repository.get_multi(db, limit=200)
        return [self._to_admin_response(db, u) for u in usuarios]

    def update_usuario(
        self, db: Session, id_usuario: int, user_in: UsuarioUpdate
    ) -> UsuarioAdminResponse:
        user = usuario_repository.get(db, id_usuario)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El usuario con ID {id_usuario} no existe",
            )

        data = user_in.model_dump(exclude_unset=True)
        password = data.pop("password", None)
        legajos_alumnos = data.pop("legajos_alumnos", None)
        tutor_data = data.pop("tutor", None)
        if tutor_data is not None:
            tutor_data = PadreCreate(**tutor_data)
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
        rol_efectivo = (
            rol_repository.get(db, nuevo_rol)
            if nuevo_rol is not None
            else rol_repository.get(db, user.id_rol)
        )
        if nuevo_rol is not None and not rol_efectivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol con ID {nuevo_rol} no existe",
            )

        campos_vinculo = {"legajo_alumno", "legajo_profesor", "id_padre"}

        if tutor_data is not None:
            if not rol_efectivo or rol_efectivo.nombre != "PARENT":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Solo los usuarios con rol Padre / Tutor pueden tener "
                        "datos de tutor"
                    ),
                )
            if campos_vinculo & data.keys():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "No combine los datos del tutor con otros vínculos "
                        "de alumno o docente"
                    ),
                )

            # El usuario queda vinculado al tutor, nunca a un alumno o docente.
            user.legajo_alumno = None
            user.legajo_profesor = None
            if user.id_padre:
                padre = padre_repository.get(db, user.id_padre)
                if not padre:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"El tutor con ID {user.id_padre} no existe",
                    )
                self._actualizar_tutor(db, padre, tutor_data)
            else:
                padre = self._obtener_o_crear_tutor(db, tutor_data)
                user.id_padre = padre.id_padre

        # Los vínculos (alumno/docente/tutor) se gestionan en bloque: si se envía
        # alguno, se limpian los demás para que una cuenta tenga un único vínculo.
        elif campos_vinculo & data.keys():
            vinculos = {campo: data.pop(campo, None) for campo in list(campos_vinculo)}

            if vinculos.get("legajo_alumno") is not None and not (
                alumno_repository.get_by_legajo(db, vinculos["legajo_alumno"])
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"El alumno con legajo #{vinculos['legajo_alumno']} no existe"
                    ),
                )
            if vinculos.get("legajo_profesor") is not None and not (
                profesor_repository.get_by_legajo(db, vinculos["legajo_profesor"])
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        "El docente con legajo "
                        f"#{vinculos['legajo_profesor']} no existe"
                    ),
                )
            if vinculos.get("id_padre") is not None and not (
                padre_repository.get(db, vinculos["id_padre"])
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El tutor con ID {vinculos['id_padre']} no existe",
                )

            for campo in campos_vinculo:
                setattr(user, campo, vinculos.get(campo))

        for field, value in data.items():
            if value is not None:
                setattr(user, field, value)

        if legajos_alumnos is not None:
            if rol_efectivo and rol_efectivo.nombre == "PARENT":
                self._sincronizar_alumnos_tutor(db, user.id_padre, legajos_alumnos)
            elif legajos_alumnos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Solo los usuarios con rol Padre / Tutor pueden tener "
                        "alumnos vinculados"
                    ),
                )

        db.commit()
        db.refresh(user)
        return self._to_admin_response(db, user)


seguridad_service = SeguridadService()
