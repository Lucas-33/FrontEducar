from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.repositories import (
    alumno_repository,
    profesor_repository,
    padre_repository,
    padre_alumno_repository,
    curso_repository,
)
from backend.app.schemas.personas import (
    AlumnoCreate, AlumnoUpdate,
    ProfesorCreate, ProfesorUpdate,
    PadreCreate, PadreUpdate,
    PadreAlumnoCreate,
)

class PersonasService:
    # ================= ALUMNOS =================
    def get_alumnos(self, db: Session, solo_activos: bool = True, skip: int = 0, limit: int = 100):
        if solo_activos:
            return alumno_repository.get_activos(db, skip=skip, limit=limit)
        return alumno_repository.get_multi(db, skip=skip, limit=limit)

    def get_alumno(self, db: Session, legajo: int):
        alumno = alumno_repository.get_by_legajo(db, legajo)
        if not alumno:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alumno con legajo '{legajo}' no encontrado")
        return alumno

    def create_alumno(self, db: Session, alumno_in: AlumnoCreate):
        if alumno_repository.get_by_legajo(db, alumno_in.legajo):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un alumno con legajo '{alumno_in.legajo}'")
        if alumno_repository.get_by_dni(db, alumno_in.dni):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un alumno registrado con el DNI '{alumno_in.dni}'")
        if not curso_repository.get(db, alumno_in.id_curso):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El curso con ID {alumno_in.id_curso} no existe")

        return alumno_repository.create(db, alumno_in)

    def update_alumno(self, db: Session, legajo: int, alumno_in: AlumnoUpdate):
        alumno = self.get_alumno(db, legajo)
        if alumno_in.id_curso and not curso_repository.get(db, alumno_in.id_curso):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El curso con ID {alumno_in.id_curso} no existe")
        return alumno_repository.update(db, alumno, alumno_in)

    def delete_alumno(self, db: Session, legajo: int):
        self.get_alumno(db, legajo)
        return alumno_repository.soft_delete(db, legajo)

    # ================= PROFESORES =================
    def get_profesores(self, db: Session, solo_activos: bool = True, skip: int = 0, limit: int = 100):
        if solo_activos:
            return profesor_repository.get_activos(db, skip=skip, limit=limit)
        return profesor_repository.get_multi(db, skip=skip, limit=limit)

    def get_profesor(self, db: Session, legajo: int):
        profesor = profesor_repository.get_by_legajo(db, legajo)
        if not profesor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profesor con legajo '{legajo}' no encontrado")
        return profesor

    def create_profesor(self, db: Session, profesor_in: ProfesorCreate):
        if profesor_repository.get_by_legajo(db, profesor_in.legajo):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un profesor con legajo '{profesor_in.legajo}'")
        if profesor_repository.get_by_dni(db, profesor_in.dni):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un profesor con DNI '{profesor_in.dni}'")
        return profesor_repository.create(db, profesor_in)

    def update_profesor(self, db: Session, legajo: int, profesor_in: ProfesorUpdate):
        profesor = self.get_profesor(db, legajo)
        return profesor_repository.update(db, profesor, profesor_in)

    def delete_profesor(self, db: Session, legajo: int):
        self.get_profesor(db, legajo)
        return profesor_repository.soft_delete(db, legajo)

    # ================= PADRES / TUTORES =================
    def get_padres(self, db: Session, skip: int = 0, limit: int = 100):
        return padre_repository.get_multi(db, skip=skip, limit=limit)

    def get_alumnos_de_padre(self, db: Session, id_padre: int) -> List:
        """Devuelve los alumnos (hijos) vinculados a un tutor."""
        if not padre_repository.get(db, id_padre):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El tutor con ID {id_padre} no existe",
            )
        relaciones = padre_alumno_repository.get_alumnos_por_padre(db, id_padre)
        alumnos = []
        for relacion in relaciones:
            alumno = alumno_repository.get_by_legajo(db, relacion.legajo_alumno)
            if alumno:
                alumnos.append(alumno)
        return alumnos

    def create_padre(self, db: Session, padre_in: PadreCreate):
        if padre_repository.get_by_dni(db, padre_in.dni):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un padre con DNI '{padre_in.dni}'")
        return padre_repository.create(db, padre_in)

    def asociar_padre_alumno(self, db: Session, relacion_in: PadreAlumnoCreate):
        if not padre_repository.get(db, relacion_in.id_padre):
            raise HTTPException(status_code=404, detail="El padre especificado no existe")
        if not alumno_repository.get_by_legajo(db, relacion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno especificado no existe")
        if padre_alumno_repository.get_relacion(db, relacion_in.id_padre, relacion_in.legajo_alumno):
            raise HTTPException(status_code=400, detail="Esta relación ya existe")
        return padre_alumno_repository.create(db, relacion_in)

personas_service = PersonasService()