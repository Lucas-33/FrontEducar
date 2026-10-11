from sqlalchemy import Column, Integer, String, Date, Boolean
from backend.app.core.database import Base

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    legajo = Column(String(50), unique=True, index=True, nullable=False)
    dni = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    domicilio = Column(String(200), nullable=True)
    telefono = Column(String(50), nullable=True)
    correo = Column(String(100), nullable=True)
    nivel = Column(String(50), nullable=False)  # Inicial, Primario, Secundario
    curso = Column(String(50), nullable=False)
    estado = Column(Boolean, default=True)      # Borrado lógico