from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.app.core.database import Base

class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)  # ADMIN, TEACHER, PARENT, STUDENT

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    id_rol = Column(Integer, ForeignKey("rol.id_rol", ondelete="RESTRICT"), nullable=False)
    
    # Vinculación opcional con la entidad real
    legajo_alumno = Column(Integer, ForeignKey("alumno.legajo", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    legajo_profesor = Column(Integer, ForeignKey("profesor.legajo", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    id_padre = Column(Integer, ForeignKey("padre.id_padre", ondelete="SET NULL"), nullable=True)
    
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())