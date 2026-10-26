from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.schemas.seguridad import (
    CambioPasswordRequest,
    LoginRequest,
    RolResponse,
    Token,
    UsuarioAdminResponse,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from backend.app.services.seguridad import seguridad_service

router = APIRouter()


@router.post(
    "/login", response_model=Token, summary="Iniciar sesión y obtener token JWT"
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return seguridad_service.login(
        db=db,
        username=credentials.username,
        password=credentials.password,
    )


@router.get(
    "/me", response_model=UsuarioAdminResponse, summary="Perfil del usuario autenticado"
)
def obtener_perfil(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return seguridad_service._to_admin_response(db, current_user)


@router.put("/me/password", summary="Cambiar la contraseña del usuario autenticado")
def cambiar_password(
    payload: CambioPasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return seguridad_service.change_password(
        db=db,
        user=current_user,
        password_actual=payload.password_actual,
        password_nueva=payload.password_nueva,
    )


@router.get(
    "/roles", response_model=list[RolResponse], summary="Listar roles disponibles"
)
def listar_roles(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return seguridad_service.get_roles(db)


@router.get(
    "/usuarios",
    response_model=list[UsuarioAdminResponse],
    summary="Listar usuarios del sistema (solo ADMIN)",
)
def listar_usuarios(
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return seguridad_service.get_usuarios(db)


@router.post(
    "/usuarios",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario (solo ADMIN)",
)
def registrar_usuario(
    user_in: UsuarioCreate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return seguridad_service.registrar_usuario(db=db, user_in=user_in)


@router.put(
    "/usuarios/{id_usuario}",
    response_model=UsuarioAdminResponse,
    summary="Actualizar usuario: rol, estado o contraseña (solo ADMIN)",
)
def actualizar_usuario(
    id_usuario: int,
    user_in: UsuarioUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    return seguridad_service.update_usuario(
        db=db, id_usuario=id_usuario, user_in=user_in
    )
