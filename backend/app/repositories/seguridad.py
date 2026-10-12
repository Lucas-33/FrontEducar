from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.seguridad import Rol, Usuario
from backend.app.schemas.seguridad import RolCreate, RolBase, UsuarioCreate, UsuarioUpdate
from backend.app.repositories.base import CRUDBase

class RolRepository(CRUDBase[Rol, RolCreate, RolBase]):
    def __init__(self):
        super().__init__(Rol)

    def get_by_nombre(self, db: Session, nombre: str) -> Optional[Rol]:
        stmt = select(Rol).where(Rol.nombre == nombre)
        return db.scalars(stmt).first()

class UsuarioRepository(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    def __init__(self):
        super().__init__(Usuario)

    def get_by_username(self, db: Session, username: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.username == username)
        return db.scalars(stmt).first()

    def create_user_with_hash(self, db: Session, obj_in: UsuarioCreate, password_hash: str) -> Usuario:
        user_data = obj_in.model_dump(exclude={"password"})
        user_data["password_hash"] = password_hash
        db_user = Usuario(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

rol_repository = RolRepository()
usuario_repository = UsuarioRepository()