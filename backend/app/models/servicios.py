from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func
from backend.app.core.database import Base

class Horario(Base):
    __tablename__ = "horario"

    id_horario = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(100), nullable=False)

class Deporte(Base):
    __tablename__ = "deporte"

    id_deporte = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    legajo_profesor_responsable = Column(Integer, ForeignKey("profesor.legajo", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)

class GrupoDeporte(Base):
    __tablename__ = "grupo_deporte"

    id_grupo = Column(Integer, primary_key=True, autoincrement=True)
    id_deporte = Column(Integer, ForeignKey("deporte.id_deporte", ondelete="CASCADE"), nullable=False)
    id_nivel = Column(Integer, ForeignKey("nivel_educativo.id_nivel", ondelete="RESTRICT"), nullable=False)
    id_horario = Column(Integer, ForeignKey("horario.id_horario", ondelete="RESTRICT"), nullable=False)

class InscripcionDeporte(Base):
    __tablename__ = "inscripcion_deporte"

    legajo_alumno = Column(Integer, ForeignKey("alumno.legajo", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id_grupo = Column(Integer, ForeignKey("grupo_deporte.id_grupo", ondelete="CASCADE"), primary_key=True)
    fecha_inscripcion = Column(Date, server_default=func.current_date(), nullable=False)

class RecorridoTransporte(Base):
    __tablename__ = "recorrido_transporte"

    id_recorrido = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(100), nullable=False)

class InscripcionTransporte(Base):
    __tablename__ = "inscripcion_transporte"

    legajo_alumno = Column(Integer, ForeignKey("alumno.legajo", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id_recorrido = Column(Integer, ForeignKey("recorrido_transporte.id_recorrido", ondelete="RESTRICT"), nullable=False)
    fecha_alta = Column(Date, server_default=func.current_date(), nullable=False)
    estado = Column(String(20), default="ACTIVO", nullable=False)

class InscripcionComedor(Base):
    __tablename__ = "inscripcion_comedor"

    legajo_alumno = Column(Integer, ForeignKey("alumno.legajo", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    fecha_alta = Column(Date, server_default=func.current_date(), nullable=False)
    estado = Column(String(20), default="ACTIVO", nullable=False)