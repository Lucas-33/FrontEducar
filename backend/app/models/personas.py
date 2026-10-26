from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text

from backend.app.core.database import Base


class Alumno(Base):
    __tablename__ = "alumno"

    legajo = Column(Integer, primary_key=True, index=True)
    dni = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    domicilio = Column(Text, nullable=False)
    telefono = Column(String(50), nullable=True)
    correo_electronico = Column(String(100), nullable=True)
    id_curso = Column(
        Integer, ForeignKey("curso.id_curso", ondelete="RESTRICT"), nullable=False
    )
    estado_alumno = Column(String(20), default="ACTIVO", nullable=False)


class Profesor(Base):
    __tablename__ = "profesor"

    legajo = Column(Integer, primary_key=True, index=True)
    dni = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    especialidad = Column(String(100), nullable=False)
    correo_electronico = Column(String(100), nullable=False)
    telefono = Column(String(50), nullable=False)
    estado = Column(String(20), default="ACTIVO", nullable=False)


class Padre(Base):
    __tablename__ = "padre"

    id_padre = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(50), nullable=True)
    correo_electronico = Column(String(100), nullable=True)


class PadreAlumno(Base):
    __tablename__ = "padre_alumno"

    id_padre = Column(
        Integer, ForeignKey("padre.id_padre", ondelete="CASCADE"), primary_key=True
    )
    legajo_alumno = Column(
        Integer,
        ForeignKey("alumno.legajo", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
