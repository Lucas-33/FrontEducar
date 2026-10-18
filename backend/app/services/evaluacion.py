from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.repositories import (
    alumno_repository,
    asistencia_repository,
    calificacion_repository,
    curso_repository,
    materia_repository,
    padre_alumno_repository,
)
from backend.app.schemas.evaluacion import (
    AsistenciaDetalleResponse,
    AsistenciaLoteCreate,
    CalificacionCreate,
    CalificacionDetalleResponse,
    CalificacionUpdate,
    ResumenAsistenciaResponse,
)


class EvaluacionService:
    # ================= CALIFICACIONES =================
    def create_calificacion(
        self,
        db: Session,
        calificacion_in: CalificacionCreate,
        legajo_profesor: Optional[int] = None,
    ):
        if not alumno_repository.get_by_legajo(db, calificacion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")
        if not materia_repository.get(db, calificacion_in.id_materia):
            raise HTTPException(status_code=404, detail="La materia no existe")
        if not curso_repository.get(db, calificacion_in.id_curso):
            raise HTTPException(status_code=404, detail="El curso no existe")

        datos = calificacion_in.model_dump()
        datos["legajo_profesor"] = legajo_profesor
        if datos.get("fecha") is None:
            datos["fecha"] = date.today()

        from backend.app.models.evaluacion import Calificacion

        registro = Calificacion(**datos)
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    def get_calificacion(self, db: Session, id_calificacion: int):
        registro = calificacion_repository.get(db, id_calificacion)
        if not registro:
            raise HTTPException(status_code=404, detail=f"La calificación #{id_calificacion} no existe")
        return registro

    def update_calificacion(self, db: Session, id_calificacion: int, calificacion_in: CalificacionUpdate):
        registro = self.get_calificacion(db, id_calificacion)
        return calificacion_repository.update(db, registro, calificacion_in)

    def delete_calificacion(self, db: Session, id_calificacion: int):
        registro = self.get_calificacion(db, id_calificacion)
        calificacion_repository.remove(db, id_calificacion)
        return registro

    def _nombre_alumno(self, db: Session, legajo: int) -> str:
        alumno = alumno_repository.get_by_legajo(db, legajo)
        if not alumno:
            return f"Legajo #{legajo}"
        return f"{alumno.apellido}, {alumno.nombre}"

    def get_calificaciones_detalle(
        self,
        db: Session,
        legajo_alumno: Optional[int] = None,
        legajos_permitidos: Optional[List[int]] = None,
        id_materia: Optional[int] = None,
        id_curso: Optional[int] = None,
        periodo: Optional[str] = None,
    ) -> List[CalificacionDetalleResponse]:
        if legajo_alumno is not None:
            registros = calificacion_repository.get_by_alumno(db, legajo_alumno)
        elif id_materia is not None and id_curso is not None:
            registros = calificacion_repository.get_by_materia_curso(db, id_materia, id_curso)
        elif id_curso is not None:
            registros = calificacion_repository.get_by_curso(db, id_curso)
        else:
            registros = calificacion_repository.get_multi(db, limit=1000)

        if legajos_permitidos is not None:
            registros = [r for r in registros if r.legajo_alumno in legajos_permitidos]
        if id_materia is not None:
            registros = [r for r in registros if r.id_materia == id_materia]
        if id_curso is not None:
            registros = [r for r in registros if r.id_curso == id_curso]
        if periodo:
            registros = [r for r in registros if r.periodo == periodo]

        resultado: List[CalificacionDetalleResponse] = []
        cache_materias = {}
        cache_cursos = {}
        for r in registros:
            if r.id_materia not in cache_materias:
                materia = materia_repository.get(db, r.id_materia)
                cache_materias[r.id_materia] = materia.nombre if materia else f"Materia #{r.id_materia}"
            if r.id_curso not in cache_cursos:
                curso = curso_repository.get(db, r.id_curso)
                cache_cursos[r.id_curso] = curso.nombre if curso else f"Curso #{r.id_curso}"
            resultado.append(
                CalificacionDetalleResponse(
                    id_calificacion=r.id_calificacion,
                    legajo_alumno=r.legajo_alumno,
                    alumno=self._nombre_alumno(db, r.legajo_alumno),
                    id_materia=r.id_materia,
                    materia=cache_materias[r.id_materia],
                    id_curso=r.id_curso,
                    curso=cache_cursos[r.id_curso],
                    periodo=r.periodo,
                    tipo=r.tipo,
                    nota=float(r.nota),
                    fecha=r.fecha,
                    observacion=r.observacion,
                )
            )
        return resultado

    # ================= ASISTENCIA =================
    def registrar_asistencia_lote(
        self,
        db: Session,
        lote_in: AsistenciaLoteCreate,
        legajo_profesor: Optional[int] = None,
    ) -> List[AsistenciaDetalleResponse]:
        if not curso_repository.get(db, lote_in.id_curso):
            raise HTTPException(status_code=404, detail="El curso no existe")

        fecha = lote_in.fecha or date.today()
        for item in lote_in.registros:
            if not alumno_repository.get_by_legajo(db, item.legajo_alumno):
                raise HTTPException(
                    status_code=404, detail=f"El alumno con legajo #{item.legajo_alumno} no existe"
                )
            existente = asistencia_repository.get_registro(db, item.legajo_alumno, fecha)
            if existente:
                existente.estado = item.estado
                existente.observacion = item.observacion
                existente.id_curso = lote_in.id_curso
                existente.legajo_profesor = legajo_profesor
            else:
                db.add(
                    asistencia_repository.model(
                        legajo_alumno=item.legajo_alumno,
                        id_curso=lote_in.id_curso,
                        fecha=fecha,
                        estado=item.estado,
                        observacion=item.observacion,
                        legajo_profesor=legajo_profesor,
                    )
                )
        db.commit()
        return self.get_asistencia_detalle(
            db, id_curso=lote_in.id_curso, fecha=fecha
        )

    def get_asistencia_detalle(
        self,
        db: Session,
        id_curso: Optional[int] = None,
        fecha: Optional[date] = None,
        legajo_alumno: Optional[int] = None,
        legajos_permitidos: Optional[List[int]] = None,
    ) -> List[AsistenciaDetalleResponse]:
        if legajo_alumno is not None:
            registros = asistencia_repository.get_by_alumno(db, legajo_alumno)
        else:
            registros = asistencia_repository.get_multi(db, limit=2000)

        if id_curso is not None:
            registros = [r for r in registros if r.id_curso == id_curso]
        if fecha is not None:
            registros = [r for r in registros if r.fecha == fecha]
        if legajos_permitidos is not None:
            registros = [r for r in registros if r.legajo_alumno in legajos_permitidos]

        cache_cursos = {}
        resultado: List[AsistenciaDetalleResponse] = []
        for r in registros:
            if r.id_curso not in cache_cursos:
                curso = curso_repository.get(db, r.id_curso)
                cache_cursos[r.id_curso] = curso.nombre if curso else f"Curso #{r.id_curso}"
            resultado.append(
                AsistenciaDetalleResponse(
                    id_asistencia=r.id_asistencia,
                    legajo_alumno=r.legajo_alumno,
                    alumno=self._nombre_alumno(db, r.legajo_alumno),
                    id_curso=r.id_curso,
                    curso=cache_cursos[r.id_curso],
                    fecha=r.fecha,
                    estado=r.estado,
                    observacion=r.observacion,
                )
            )
        resultado.sort(key=lambda x: x.fecha, reverse=True)
        return resultado

    def delete_asistencia(self, db: Session, id_asistencia: int):
        registro = asistencia_repository.get(db, id_asistencia)
        if not registro:
            raise HTTPException(status_code=404, detail=f"El registro de asistencia #{id_asistencia} no existe")
        asistencia_repository.remove(db, id_asistencia)
        return registro

    def resumen_asistencia(self, db: Session, legajo_alumno: int) -> ResumenAsistenciaResponse:
        if not alumno_repository.get_by_legajo(db, legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")
        registros = asistencia_repository.get_by_alumno(db, legajo_alumno, limit=2000)
        total = len(registros)
        presentes = sum(1 for r in registros if r.estado == "PRESENTE")
        ausentes = sum(1 for r in registros if r.estado == "AUSENTE")
        tardes = sum(1 for r in registros if r.estado == "TARDE")
        justificados = sum(1 for r in registros if r.estado == "JUSTIFICADO")
        porcentaje = round(((presentes + tardes + justificados) / total) * 100, 1) if total else 0.0
        return ResumenAsistenciaResponse(
            legajo_alumno=legajo_alumno,
            total=total,
            presentes=presentes,
            ausentes=ausentes,
            tardes=tardes,
            justificados=justificados,
            porcentaje_presentismo=porcentaje,
        )

    # Útil para endpoints: hijos del tutor autenticado
    def legajos_de_padre(self, db: Session, id_padre: Optional[int]) -> List[int]:
        if not id_padre:
            return []
        return [rel.legajo_alumno for rel in padre_alumno_repository.get_alumnos_por_padre(db, id_padre)]


evaluacion_service = EvaluacionService()
