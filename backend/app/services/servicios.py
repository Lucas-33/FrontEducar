from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.repositories import (
    alumno_repository,
    deporte_repository,
    grupo_deporte_repository,
    horario_repository,
    inscripcion_comedor_repository,
    inscripcion_deporte_repository,
    inscripcion_transporte_repository,
    nivel_repository,
    recorrido_transporte_repository,
)
from backend.app.schemas.servicios import (
    DeporteCreate,
    DeporteUpdate,
    GrupoDeporteCreate,
    GrupoDeporteDetalleResponse,
    GrupoDeporteUpdate,
    InscripcionComedorCreate,
    InscripcionComedorDetalleResponse,
    InscripcionDeporteCreate,
    InscripcionDeporteDetalleResponse,
    InscripcionTransporteCreate,
    InscripcionTransporteDetalleResponse,
    RecorridoTransporteCreate,
    RecorridoTransporteUpdate,
)


class ServiciosEscolaresService:
    # --- DEPORTES Y GRUPOS ---
    def create_deporte(self, db: Session, deporte_in: DeporteCreate):
        return deporte_repository.create(db, deporte_in)

    def get_deportes(self, db: Session):
        return deporte_repository.get_multi(db)

    def update_deporte(self, db: Session, id_deporte: int, deporte_in: DeporteUpdate):
        deporte = deporte_repository.get(db, id_deporte)
        if not deporte:
            raise HTTPException(
                status_code=404, detail=f"El deporte con ID {id_deporte} no existe"
            )
        return deporte_repository.update(db, deporte, deporte_in)

    def delete_deporte(self, db: Session, id_deporte: int):
        deporte = deporte_repository.get(db, id_deporte)
        if not deporte:
            raise HTTPException(
                status_code=404, detail=f"El deporte con ID {id_deporte} no existe"
            )
        try:
            deporte_repository.remove(db, id_deporte)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar el deporte porque tiene grupos o inscriptos asociados",
            )
        return deporte

    def create_grupo_deporte(self, db: Session, grupo_in: GrupoDeporteCreate):
        if not deporte_repository.get(db, grupo_in.id_deporte):
            raise HTTPException(status_code=404, detail="Deporte no encontrado")
        if not nivel_repository.get(db, grupo_in.id_nivel):
            raise HTTPException(status_code=404, detail="Nivel educativo no encontrado")
        if not horario_repository.get(db, grupo_in.id_horario):
            raise HTTPException(status_code=404, detail="Horario no encontrado")
        return grupo_deporte_repository.create(db, grupo_in)

    def update_grupo_deporte(
        self, db: Session, id_grupo: int, grupo_in: GrupoDeporteUpdate
    ):
        grupo = grupo_deporte_repository.get(db, id_grupo)
        if not grupo:
            raise HTTPException(
                status_code=404, detail=f"El grupo con ID {id_grupo} no existe"
            )
        datos = grupo_in.model_dump(exclude_unset=True)
        if datos.get("id_deporte") is not None and not deporte_repository.get(
            db, datos["id_deporte"]
        ):
            raise HTTPException(status_code=404, detail="Deporte no encontrado")
        if datos.get("id_nivel") is not None and not nivel_repository.get(
            db, datos["id_nivel"]
        ):
            raise HTTPException(status_code=404, detail="Nivel educativo no encontrado")
        if datos.get("id_horario") is not None and not horario_repository.get(
            db, datos["id_horario"]
        ):
            raise HTTPException(status_code=404, detail="Horario no encontrado")
        return grupo_deporte_repository.update(db, grupo, grupo_in)

    def delete_grupo_deporte(self, db: Session, id_grupo: int):
        grupo = grupo_deporte_repository.get(db, id_grupo)
        if not grupo:
            raise HTTPException(
                status_code=404, detail=f"El grupo con ID {id_grupo} no existe"
            )
        try:
            grupo_deporte_repository.remove(db, id_grupo)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar el grupo porque tiene alumnos inscriptos",
            )
        return grupo

    def inscribir_deporte(self, db: Session, inscripcion_in: InscripcionDeporteCreate):
        if not alumno_repository.get_by_legajo(db, inscripcion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")

        nuevo_grupo = grupo_deporte_repository.get(db, inscripcion_in.id_grupo)
        if not nuevo_grupo:
            raise HTTPException(status_code=404, detail="El grupo deportivo no existe")

        if inscripcion_deporte_repository.get_inscripcion(
            db, inscripcion_in.legajo_alumno, inscripcion_in.id_grupo
        ):
            raise HTTPException(
                status_code=400, detail="El alumno ya está inscripto en este grupo"
            )

        # 1. Validar límite máximo de 2 deportes (RF03)
        inscripciones_actuales = inscripcion_deporte_repository.get_by_alumno(
            db, inscripcion_in.legajo_alumno
        )
        if len(inscripciones_actuales) >= 2:
            raise HTTPException(
                status_code=400,
                detail="El alumno ya alcanzó el límite máximo de dos deportes simultáneos",
            )

        # 2. Controlar conflictos de horario (RF07)
        for inscripcion in inscripciones_actuales:
            grupo_actual = grupo_deporte_repository.get(db, inscripcion.id_grupo)
            if grupo_actual and grupo_actual.id_horario == nuevo_grupo.id_horario:
                raise HTTPException(
                    status_code=409,
                    detail="Existe un conflicto de horarios con otro deporte en el que el alumno ya está inscripto",
                )

        return inscripcion_deporte_repository.create(db, inscripcion_in)

    # --- TRANSPORTE ---
    def create_recorrido(self, db: Session, recorrido_in: RecorridoTransporteCreate):
        return recorrido_transporte_repository.create(db, recorrido_in)

    def get_recorridos(self, db: Session):
        return recorrido_transporte_repository.get_multi(db)

    def update_recorrido(
        self, db: Session, id_recorrido: int, recorrido_in: RecorridoTransporteUpdate
    ):
        recorrido = recorrido_transporte_repository.get(db, id_recorrido)
        if not recorrido:
            raise HTTPException(
                status_code=404, detail=f"El recorrido con ID {id_recorrido} no existe"
            )
        return recorrido_transporte_repository.update(db, recorrido, recorrido_in)

    def delete_recorrido(self, db: Session, id_recorrido: int):
        recorrido = recorrido_transporte_repository.get(db, id_recorrido)
        if not recorrido:
            raise HTTPException(
                status_code=404, detail=f"El recorrido con ID {id_recorrido} no existe"
            )
        try:
            recorrido_transporte_repository.remove(db, id_recorrido)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar el recorrido porque tiene pasajeros asociados",
            )
        return recorrido

    def inscribir_transporte(
        self, db: Session, inscripcion_in: InscripcionTransporteCreate
    ):
        if not alumno_repository.get_by_legajo(db, inscripcion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")
        if not recorrido_transporte_repository.get(db, inscripcion_in.id_recorrido):
            raise HTTPException(status_code=404, detail="El recorrido no existe")

        existente = inscripcion_transporte_repository.get_by_alumno(
            db, inscripcion_in.legajo_alumno
        )
        if existente and existente.estado == "ACTIVO":
            raise HTTPException(
                status_code=400,
                detail="El alumno ya cuenta con inscripción activa en transporte",
            )
        return inscripcion_transporte_repository.create(db, inscripcion_in)

    def baja_transporte(self, db: Session, legajo_alumno: int):
        res = inscripcion_transporte_repository.soft_delete(db, legajo_alumno)
        if not res:
            raise HTTPException(
                status_code=404, detail="Inscripción de transporte no encontrada"
            )
        return res

    # --- COMEDOR ---
    def inscribir_comedor(self, db: Session, inscripcion_in: InscripcionComedorCreate):
        if not alumno_repository.get_by_legajo(db, inscripcion_in.legajo_alumno):
            raise HTTPException(status_code=404, detail="El alumno no existe")

        existente = inscripcion_comedor_repository.get_by_alumno(
            db, inscripcion_in.legajo_alumno
        )
        if existente and existente.estado == "ACTIVO":
            raise HTTPException(
                status_code=400,
                detail="El alumno ya cuenta con inscripción activa en comedor",
            )
        return inscripcion_comedor_repository.create(db, inscripcion_in)

    def baja_comedor(self, db: Session, legajo_alumno: int):
        res = inscripcion_comedor_repository.soft_delete(db, legajo_alumno)
        if not res:
            raise HTTPException(
                status_code=404, detail="Inscripción de comedor no encontrada"
            )
        return res

    # ================= DETALLES PARA EL PANEL ADMIN =================
    @staticmethod
    def _nombre_alumno(db: Session, legajo_alumno: int) -> str:
        alumno = alumno_repository.get_by_legajo(db, legajo_alumno)
        if not alumno:
            return f"Legajo #{legajo_alumno}"
        return f"{alumno.apellido}, {alumno.nombre} (#{alumno.legajo})"

    def get_grupos_deporte(self, db: Session) -> list[GrupoDeporteDetalleResponse]:
        grupos: list[GrupoDeporteDetalleResponse] = []
        for grupo in grupo_deporte_repository.get_multi(db, limit=200):
            deporte = deporte_repository.get(db, grupo.id_deporte)
            nivel = nivel_repository.get(db, grupo.id_nivel)
            horario = horario_repository.get(db, grupo.id_horario)
            grupos.append(
                GrupoDeporteDetalleResponse(
                    id_grupo=grupo.id_grupo,
                    id_deporte=grupo.id_deporte,
                    deporte=deporte.nombre
                    if deporte
                    else f"Deporte #{grupo.id_deporte}",
                    id_nivel=grupo.id_nivel,
                    nivel=nivel.nombre if nivel else f"Nivel #{grupo.id_nivel}",
                    id_horario=grupo.id_horario,
                    horario=horario.descripcion
                    if horario
                    else f"Horario #{grupo.id_horario}",
                )
            )
        return grupos

    def get_inscripciones_deporte(
        self, db: Session
    ) -> list[InscripcionDeporteDetalleResponse]:
        inscripciones: list[InscripcionDeporteDetalleResponse] = []
        for inscripcion in inscripcion_deporte_repository.get_multi(db, limit=500):
            grupo = grupo_deporte_repository.get(db, inscripcion.id_grupo)
            deporte = deporte_repository.get(db, grupo.id_deporte) if grupo else None
            inscripciones.append(
                InscripcionDeporteDetalleResponse(
                    legajo_alumno=inscripcion.legajo_alumno,
                    alumno=self._nombre_alumno(db, inscripcion.legajo_alumno),
                    id_grupo=inscripcion.id_grupo,
                    deporte=deporte.nombre
                    if deporte
                    else f"Grupo #{inscripcion.id_grupo}",
                    fecha_inscripcion=inscripcion.fecha_inscripcion,
                )
            )
        return inscripciones

    def get_inscripciones_transporte(
        self, db: Session
    ) -> list[InscripcionTransporteDetalleResponse]:
        inscripciones: list[InscripcionTransporteDetalleResponse] = []
        for inscripcion in inscripcion_transporte_repository.get_multi(db, limit=500):
            recorrido = recorrido_transporte_repository.get(
                db, inscripcion.id_recorrido
            )
            inscripciones.append(
                InscripcionTransporteDetalleResponse(
                    legajo_alumno=inscripcion.legajo_alumno,
                    alumno=self._nombre_alumno(db, inscripcion.legajo_alumno),
                    id_recorrido=inscripcion.id_recorrido,
                    recorrido=recorrido.descripcion
                    if recorrido
                    else f"Recorrido #{inscripcion.id_recorrido}",
                    fecha_alta=inscripcion.fecha_alta,
                    estado=inscripcion.estado,
                )
            )
        return inscripciones

    def get_inscripciones_comedor(
        self, db: Session
    ) -> list[InscripcionComedorDetalleResponse]:
        inscripciones: list[InscripcionComedorDetalleResponse] = []
        for inscripcion in inscripcion_comedor_repository.get_multi(db, limit=500):
            inscripciones.append(
                InscripcionComedorDetalleResponse(
                    legajo_alumno=inscripcion.legajo_alumno,
                    alumno=self._nombre_alumno(db, inscripcion.legajo_alumno),
                    fecha_alta=inscripcion.fecha_alta,
                    estado=inscripcion.estado,
                )
            )
        return inscripciones


servicios_escolares_service = ServiciosEscolaresService()
