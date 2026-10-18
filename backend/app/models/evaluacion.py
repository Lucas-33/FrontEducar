"""Calificaciones y asistencia: registro académico de los alumnos."""
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.sql import func

from backend.app.core.database import Base


class Calificacion(Base):
    """Nota de un alumno en una materia/curso para un período y tipo de evaluación."""

    __tablename__ = "calificacion"

    id_calificacion = Column(Integer, primary_key=True, autoincrement=True)
    legajo_alumno = Column(
        Integer,
        ForeignKey("alumno.legajo", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    id_materia = Column(Integer, ForeignKey("materia.id_materia", ondelete="CASCADE"), nullable=False)
    id_curso = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"), nullable=False)
    periodo = Column(String(30), nullable=False)  # 1er Trimestre, 2do Trimestre, ...
    tipo = Column(String(30), nullable=False)  # Parcial, Trabajo Práctico, Oral, Final, Concepto
    nota = Column(Numeric(4, 2), nullable=False)  # escala 0.00 a 10.00
    fecha = Column(Date, server_default=func.current_date(), nullable=False)
    observacion = Column(String(200), nullable=True)
    legajo_profesor = Column(
        Integer,
        ForeignKey("profesor.legajo", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )


class Asistencia(Base):
    """Estado de asistencia diaria de un alumno."""

    __tablename__ = "asistencia"
    __table_args__ = (
        UniqueConstraint("legajo_alumno", "fecha", name="uq_asistencia_alumno_fecha"),
    )

    id_asistencia = Column(Integer, primary_key=True, autoincrement=True)
    legajo_alumno = Column(
        Integer,
        ForeignKey("alumno.legajo", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    id_curso = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)  # PRESENTE, AUSENTE, TARDE, JUSTIFICADO
    observacion = Column(String(200), nullable=True)
    legajo_profesor = Column(
        Integer,
        ForeignKey("profesor.legajo", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
