from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.seguridad import LoginRequest, Token, UsuarioCreate, UsuarioResponse
from backend.app.services.seguridad import seguridad_service

router = APIRouter()

@router.post("/login", response_model=Token, summary="Iniciar sesión y obtener token JWT")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return seguridad_service.login(
        db=db,
        username=credentials.username,
        password=credentials.password,
    )

@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, summary="Registrar nuevo usuario")
def registrar_usuario(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    return seguridad_service.registrar_usuario(db=db, user_in=user_in)