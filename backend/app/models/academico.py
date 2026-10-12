from sqlalchemy import Column, Integer, String, ForeignKey
from backend.app.core.database import Base

class NivelEducativo(Base):
    __tablename__ = "nivel_educativo"

    id_nivel = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)  # Inicial, Primario, Secundario

class Curso(Base):
    __tablename__ = "curso"

    id_curso = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    id_nivel = Column(Integer, ForeignKey("nivel_educativo.id_nivel", ondelete="RESTRICT"), nullable=False)

class Materia(Base):
    __tablename__ = "materia"

    id_materia = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

class MateriaCursoProfesor(Base):
    __tablename__ = "materia_curso_profesor"

    id_materia = Column(Integer, ForeignKey("materia.id_materia", ondelete="CASCADE"), primary_key=True)
    id_curso = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"), primary_key=True)
    legajo_profesor = Column(String(50), ForeignKey("profesor.legajo", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)