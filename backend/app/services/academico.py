from typing import List
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.repositories import (
    nivel_repository,
    curso_repository,
    materia_repository,
    materia_curso_profesor_repository,
    profesor_repository,
    horario_repository,
)
from backend.app.schemas.academico import (
    NivelEducativoCreate, NivelEducativoUpdate,
    CursoCreate, CursoUpdate,
    MateriaCreate, MateriaUpdate,
    MateriaCursoProfesorCreate, MateriaCursoProfesorUpdate,
    AsignacionDetalleResponse,
)
from backend.app.schemas.servicios import HorarioCreate, HorarioUpdate

def _conflicto_integridad(db: Session, mensaje: str):
    """Revierte la transacción y devuelve un 409 explicando que hay registros relacionados."""
    db.rollback()
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=mensaje)

class AcademicoService:
    # --- NIVELES ---
    def get_niveles(self, db: Session):
        return nivel_repository.get_multi(db)

    def create_nivel(self, db: Session, nivel_in: NivelEducativoCreate):
        return nivel_repository.create(db, nivel_in)

    def update_nivel(self, db: Session, id_nivel: int, nivel_in: NivelEducativoUpdate):
        nivel = nivel_repository.get(db, id_nivel)
        if not nivel:
            raise HTTPException(status_code=404, detail=f"El nivel educativo con ID {id_nivel} no existe")
        return nivel_repository.update(db, nivel, nivel_in)

    def delete_nivel(self, db: Session, id_nivel: int):
        nivel = nivel_repository.get(db, id_nivel)
        if not nivel:
            raise HTTPException(status_code=404, detail=f"El nivel educativo con ID {id_nivel} no existe")
        try:
            nivel_repository.remove(db, id_nivel)
        except IntegrityError:
            _conflicto_integridad(
                db,
                "No se puede eliminar el nivel porque tiene cursos o grupos asociados",
            )
        return nivel

    # --- CURSOS ---
    def get_cursos(self, db: Session, id_nivel: int = None):
        if id_nivel:
            return curso_repository.get_by_nivel(db, id_nivel)
        return curso_repository.get_multi(db)

    def create_curso(self, db: Session, curso_in: CursoCreate):
        if not nivel_repository.get(db, curso_in.id_nivel):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El nivel educativo con ID {curso_in.id_nivel} no existe",
            )
        return curso_repository.create(db, curso_in)

    def update_curso(self, db: Session, id_curso: int, curso_in: CursoUpdate):
        curso = curso_repository.get(db, id_curso)
        if not curso:
            raise HTTPException(status_code=404, detail=f"El curso con ID {id_curso} no existe")
        datos = curso_in.model_dump(exclude_unset=True)
        nuevo_nivel = datos.get("id_nivel")
        if nuevo_nivel is not None and not nivel_repository.get(db, nuevo_nivel):
            raise HTTPException(status_code=404, detail=f"El nivel educativo con ID {nuevo_nivel} no existe")
        return curso_repository.update(db, curso, curso_in)

    def delete_curso(self, db: Session, id_curso: int):
        curso = curso_repository.get(db, id_curso)
        if not curso:
            raise HTTPException(status_code=404, detail=f"El curso con ID {id_curso} no existe")
        try:
            curso_repository.remove(db, id_curso)
        except IntegrityError:
            _conflicto_integridad(
                db,
                "No se puede eliminar el curso porque tiene alumnos o materias asignadas",
            )
        return curso

    # --- MATERIAS ---
    def get_materias(self, db: Session):
        return materia_repository.get_multi(db)

    def create_materia(self, db: Session, materia_in: MateriaCreate):
        return materia_repository.create(db, materia_in)

    def update_materia(self, db: Session, id_materia: int, materia_in: MateriaUpdate):
        materia = materia_repository.get(db, id_materia)
        if not materia:
            raise HTTPException(status_code=404, detail=f"La materia con ID {id_materia} no existe")
        return materia_repository.update(db, materia, materia_in)

    def delete_materia(self, db: Session, id_materia: int):
        materia = materia_repository.get(db, id_materia)
        if not materia:
            raise HTTPException(status_code=404, detail=f"La materia con ID {id_materia} no existe")
        try:
            materia_repository.remove(db, id_materia)
        except IntegrityError:
            _conflicto_integridad(
                db,
                "No se puede eliminar la materia porque está asignada a cursos o tiene calificaciones",
            )
        return materia

    # --- MATERIA - CURSO - PROFESOR ---
    def asignar_materia_profesor(self, db: Session, asignacion_in: MateriaCursoProfesorCreate):
        if not materia_repository.get(db, asignacion_in.id_materia):
            raise HTTPException(status_code=404, detail="La materia especificada no existe")
        if not curso_repository.get(db, asignacion_in.id_curso):
            raise HTTPException(status_code=404, detail="El curso especificado no existe")
        if not profesor_repository.get_by_legajo(db, asignacion_in.legajo_profesor):
            raise HTTPException(status_code=404, detail="El profesor especificado no existe")

        existente = materia_curso_profesor_repository.get_by_materia_y_curso(
            db, asignacion_in.id_materia, asignacion_in.id_curso
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta materia ya se encuentra asignada en este curso",
            )
        return materia_curso_profesor_repository.create(db, asignacion_in)

    def update_asignacion(self, db: Session, id_materia: int, id_curso: int, asignacion_in: MateriaCursoProfesorUpdate):
        existente = materia_curso_profesor_repository.get_by_materia_y_curso(db, id_materia, id_curso)
        if not existente:
            raise HTTPException(
                status_code=404,
                detail=f"No existe la asignación materia #{id_materia} / curso #{id_curso}",
            )
        datos = asignacion_in.model_dump(exclude_unset=True)
        nuevo_id_materia = datos.get("id_materia", id_materia)
        nuevo_id_curso = datos.get("id_curso", id_curso)
        nuevo_legajo = datos.get("legajo_profesor", existente.legajo_profesor)

        if not materia_repository.get(db, nuevo_id_materia):
            raise HTTPException(status_code=404, detail="La materia especificada no existe")
        if not curso_repository.get(db, nuevo_id_curso):
            raise HTTPException(status_code=404, detail="El curso especificado no existe")
        if not profesor_repository.get_by_legajo(db, nuevo_legajo):
            raise HTTPException(status_code=404, detail="El profesor especificado no existe")

        if (nuevo_id_materia, nuevo_id_curso) != (id_materia, id_curso):
            # La clave primaria no se puede modificar en sitio: se elimina y se recrea
            duplicado = materia_curso_profesor_repository.get_by_materia_y_curso(
                db, nuevo_id_materia, nuevo_id_curso
            )
            if duplicado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La materia y el curso destino ya tienen una asignación existente",
                )
            materia_curso_profesor_repository.remove(db, (id_materia, id_curso))
            return materia_curso_profesor_repository.create(
                db,
                MateriaCursoProfesorCreate(
                    id_materia=nuevo_id_materia,
                    id_curso=nuevo_id_curso,
                    legajo_profesor=nuevo_legajo,
                ),
            )

        return materia_curso_profesor_repository.update(db, existente, {"legajo_profesor": nuevo_legajo})

    def delete_asignacion(self, db: Session, id_materia: int, id_curso: int):
        existente = materia_curso_profesor_repository.get_by_materia_y_curso(db, id_materia, id_curso)
        if not existente:
            raise HTTPException(
                status_code=404,
                detail=f"No existe la asignación materia #{id_materia} / curso #{id_curso}",
            )
        try:
            materia_curso_profesor_repository.remove(db, (id_materia, id_curso))
        except IntegrityError:
            _conflicto_integridad(
                db,
                "No se puede quitar la asignación porque tiene calificaciones registradas",
            )
        return existente

    def get_asignaciones(self, db: Session) -> List[AsignacionDetalleResponse]:
        """Lista las asignaciones materia-curso con los nombres resueltos para el panel admin."""
        resultado: List[AsignacionDetalleResponse] = []
        for asignacion in materia_curso_profesor_repository.get_multi(db, limit=500):
            materia = materia_repository.get(db, asignacion.id_materia)
            curso = curso_repository.get(db, asignacion.id_curso)
            nivel = nivel_repository.get(db, curso.id_nivel) if curso else None
            profesor = profesor_repository.get_by_legajo(db, asignacion.legajo_profesor)
            resultado.append(
                AsignacionDetalleResponse(
                    id_materia=asignacion.id_materia,
                    materia=materia.nombre if materia else f"Materia #{asignacion.id_materia}",
                    id_curso=asignacion.id_curso,
                    curso=curso.nombre if curso else f"Curso #{asignacion.id_curso}",
                    id_nivel=nivel.id_nivel if nivel else 0,
                    nivel=nivel.nombre if nivel else "-",
                    legajo_profesor=asignacion.legajo_profesor,
                    profesor=f"{profesor.apellido}, {profesor.nombre}" if profesor else f"Legajo #{asignacion.legajo_profesor}",
                )
            )
        return resultado

    # --- HORARIOS ---
    def get_horarios(self, db: Session):
        return horario_repository.get_multi(db, limit=200)

    def create_horario(self, db: Session, horario_in: HorarioCreate):
        return horario_repository.create(db, horario_in)

    def update_horario(self, db: Session, id_horario: int, horario_in: HorarioUpdate):
        horario = horario_repository.get(db, id_horario)
        if not horario:
            raise HTTPException(status_code=404, detail=f"El horario con ID {id_horario} no existe")
        return horario_repository.update(db, horario, horario_in)

    def delete_horario(self, db: Session, id_horario: int):
        horario = horario_repository.get(db, id_horario)
        if not horario:
            raise HTTPException(status_code=404, detail=f"El horario con ID {id_horario} no existe")
        try:
            horario_repository.remove(db, id_horario)
        except IntegrityError:
            _conflicto_integridad(
                db,
                "No se puede eliminar el horario porque está asociado a grupos con inscriptos",
            )
        return horario

academico_service = AcademicoService()