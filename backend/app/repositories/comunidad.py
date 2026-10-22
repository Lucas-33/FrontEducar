from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.models.comunidad import (
    MensajeContacto,
    Opinion,
    PostulacionEmpleo,
    SolicitudInscripcion,
)
from backend.app.repositories.base import CRUDBase
from backend.app.schemas.comunidad import (
    MensajeContactoCreate,
    OpinionCreate,
    PostulacionEmpleoCreate,
    SolicitudInscripcionCreate,
)


class SolicitudInscripcionRepository(
    CRUDBase[
        SolicitudInscripcion, SolicitudInscripcionCreate, SolicitudInscripcionCreate
    ]
):
    def __init__(self):
        super().__init__(SolicitudInscripcion)

    def get_multi_ordenadas(
        self, db: Session, limit: int = 300
    ) -> list[SolicitudInscripcion]:
        stmt = (
            select(SolicitudInscripcion)
            .order_by(desc(SolicitudInscripcion.id_solicitud))
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def count_pendientes(self, db: Session) -> int:
        stmt = select(SolicitudInscripcion).where(
            SolicitudInscripcion.estado == "Pendiente"
        )
        return len(list(db.scalars(stmt).all()))


class MensajeContactoRepository(
    CRUDBase[MensajeContacto, MensajeContactoCreate, MensajeContactoCreate]
):
    def __init__(self):
        super().__init__(MensajeContacto)

    def get_multi_ordenados(
        self, db: Session, limit: int = 200
    ) -> list[MensajeContacto]:
        stmt = (
            select(MensajeContacto)
            .order_by(desc(MensajeContacto.id_mensaje))
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def count_no_leidos(self, db: Session) -> int:
        stmt = select(MensajeContacto).where(MensajeContacto.leido.is_(False))
        return len(list(db.scalars(stmt).all()))


class OpinionRepository(CRUDBase[Opinion, OpinionCreate, OpinionCreate]):
    def __init__(self):
        super().__init__(Opinion)

    def get_aprobadas(self, db: Session, limit: int = 50) -> list[Opinion]:
        stmt = (
            select(Opinion)
            .where(Opinion.aprobada.is_(True))
            .order_by(desc(Opinion.id_opinion))
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def get_multi_ordenadas(self, db: Session, limit: int = 200) -> list[Opinion]:
        stmt = select(Opinion).order_by(desc(Opinion.id_opinion)).limit(limit)
        return list(db.scalars(stmt).all())

    def count_pendientes(self, db: Session) -> int:
        stmt = select(Opinion).where(Opinion.aprobada.is_(False))
        return len(list(db.scalars(stmt).all()))


class PostulacionEmpleoRepository(
    CRUDBase[PostulacionEmpleo, PostulacionEmpleoCreate, PostulacionEmpleoCreate]
):
    def __init__(self):
        super().__init__(PostulacionEmpleo)

    def get_multi_ordenadas(
        self, db: Session, limit: int = 200
    ) -> list[PostulacionEmpleo]:
        stmt = (
            select(PostulacionEmpleo)
            .order_by(desc(PostulacionEmpleo.id_postulacion))
            .limit(limit)
        )
        return list(db.scalars(stmt).all())


solicitud_inscripcion_repository = SolicitudInscripcionRepository()
mensaje_contacto_repository = MensajeContactoRepository()
opinion_repository = OpinionRepository()
postulacion_empleo_repository = PostulacionEmpleoRepository()
