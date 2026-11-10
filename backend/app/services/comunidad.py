from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.reglas_academicas import validar_edad_para_nivel
from backend.app.models.comunidad import Opinion, SolicitudInscripcion
from backend.app.repositories import (
    mensaje_contacto_repository,
    opinion_repository,
    postulacion_empleo_repository,
    solicitud_inscripcion_repository,
)
from backend.app.schemas.comunidad import (
    MensajeContactoCreate,
    OpinionCreate,
    PostulacionEmpleoCreate,
    SolicitudInscripcionCreate,
)


class ComunidadService:
    # --- SOLICITUDES DE INSCRIPCIÓN ---
    def crear_solicitud(
        self, db: Session, solicitud_in: SolicitudInscripcionCreate
    ) -> SolicitudInscripcion:
        # La edad declarada debe ser coherente con el nivel/grado postulado.
        validar_edad_para_nivel(solicitud_in.fecha_nacimiento, solicitud_in.nivel)
        return solicitud_inscripcion_repository.create(db, solicitud_in)

    def get_solicitudes(self, db: Session) -> list[SolicitudInscripcion]:
        return solicitud_inscripcion_repository.get_multi_ordenadas(db)

    @staticmethod
    def _validar_aptitud_para_aprobar(
        solicitud: SolicitudInscripcion,
    ) -> None:
        """Revalida la edad al aprobar para bloquear solicitudes antiguas inválidas."""
        if not solicitud.fecha_nacimiento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No se puede aprobar la solicitud porque no registra la "
                    "fecha de nacimiento del postulante."
                ),
            )
        validar_edad_para_nivel(solicitud.fecha_nacimiento, solicitud.nivel)

    def cambiar_estado_solicitud(
        self,
        db: Session,
        id_solicitud: int,
        estado: str,
        observaciones: str | None = None,
    ) -> SolicitudInscripcion:
        solicitud = solicitud_inscripcion_repository.get(db, id_solicitud)
        if not solicitud:
            raise HTTPException(
                status_code=404, detail=f"La solicitud #{id_solicitud} no existe"
            )
        if estado == "Aprobado":
            self._validar_aptitud_para_aprobar(solicitud)
        solicitud.estado = estado
        if observaciones is not None:
            solicitud.observaciones = observaciones
        db.commit()
        db.refresh(solicitud)
        return solicitud

    # --- MENSAJES DE CONTACTO ---
    def crear_mensaje(self, db: Session, mensaje_in: MensajeContactoCreate):
        return mensaje_contacto_repository.create(db, mensaje_in)

    def get_mensajes(self, db: Session):
        return mensaje_contacto_repository.get_multi_ordenados(db)

    def marcar_mensaje_leido(self, db: Session, id_mensaje: int):
        mensaje = mensaje_contacto_repository.get(db, id_mensaje)
        if not mensaje:
            raise HTTPException(
                status_code=404, detail=f"El mensaje #{id_mensaje} no existe"
            )
        mensaje.leido = True
        db.commit()
        db.refresh(mensaje)
        return mensaje

    # --- OPINIONES ---
    def crear_opinion(self, db: Session, opinion_in: OpinionCreate) -> Opinion:
        """Toda opinión nueva queda pendiente de moderación."""
        return opinion_repository.create(db, opinion_in)

    def get_opiniones_aprobadas(self, db: Session) -> list[Opinion]:
        return opinion_repository.get_aprobadas(db)

    def get_opiniones(self, db: Session) -> list[Opinion]:
        return opinion_repository.get_multi_ordenadas(db)

    def aprobar_opinion(
        self, db: Session, id_opinion: int, aprobada: bool = True
    ) -> Opinion:
        opinion = opinion_repository.get(db, id_opinion)
        if not opinion:
            raise HTTPException(
                status_code=404, detail=f"La opinión #{id_opinion} no existe"
            )
        opinion.aprobada = aprobada
        db.commit()
        db.refresh(opinion)
        return opinion

    def eliminar_opinion(self, db: Session, id_opinion: int) -> Opinion:
        opinion = opinion_repository.get(db, id_opinion)
        if not opinion:
            raise HTTPException(
                status_code=404, detail=f"La opinión #{id_opinion} no existe"
            )
        opinion_repository.remove(db, id_opinion)
        return opinion

    # --- POSTULACIONES LABORALES ---
    def crear_postulacion(self, db: Session, postulacion_in: PostulacionEmpleoCreate):
        return postulacion_empleo_repository.create(db, postulacion_in)

    def get_postulaciones(self, db: Session):
        return postulacion_empleo_repository.get_multi_ordenadas(db)

    # --- RESUMEN PARA EL DASHBOARD ---
    def resumen(self, db: Session) -> dict:
        return {
            "solicitudes_pendientes": solicitud_inscripcion_repository.count_pendientes(
                db
            ),
            "mensajes_no_leidos": mensaje_contacto_repository.count_no_leidos(db),
            "opiniones_pendientes": opinion_repository.count_pendientes(db),
        }


comunidad_service = ComunidadService()
