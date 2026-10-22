"""Entidades de interacción con la comunidad: admisiones, contacto, opiniones y empleo."""

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.core.database import Base


class SolicitudInscripcion(Base):
    """Solicitud de admisión / preinscripción enviada desde el sitio público."""

    __tablename__ = "solicitud_inscripcion"

    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    postulante = Column(String(120), nullable=False)
    dni = Column(String(20), nullable=False)
    fecha_nacimiento = Column(String(20), nullable=True)
    nivel = Column(String(80), nullable=False)
    tutor = Column(String(120), nullable=False)
    telefono = Column(String(50), nullable=True)
    correo = Column(String(120), nullable=True)
    fecha = Column(Date, server_default=func.current_date(), nullable=False)
    estado = Column(
        String(20), default="Pendiente", nullable=False
    )  # Pendiente / Aprobado / Rechazado
    observaciones = Column(String(300), nullable=True)


class MensajeContacto(Base):
    """Consulta enviada desde el formulario público de contacto."""

    __tablename__ = "mensaje_contacto"

    id_mensaje = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    telefono = Column(String(50), nullable=True)
    correo = Column(String(120), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    leido = Column(Boolean, default=False, nullable=False)


class Opinion(Base):
    """Testimonio público enviado por visitantes, sujeto a moderación."""

    __tablename__ = "opinion"

    id_opinion = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    vinculo = Column(String(80), nullable=True)
    comentario = Column(Text, nullable=False)
    estrellas = Column(Integer, default=5, nullable=False)
    fecha = Column(Date, server_default=func.current_date(), nullable=False)
    aprobada = Column(Boolean, default=False, nullable=False)


class PostulacionEmpleo(Base):
    """Postulación laboral (a una vacante o espontánea)."""

    __tablename__ = "postulacion_empleo"

    id_postulacion = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    correo = Column(String(120), nullable=False)
    telefono = Column(String(50), nullable=True)
    puesto = Column(String(150), default="Postulación espontánea", nullable=False)
    area = Column(String(120), nullable=True)
    mensaje = Column(Text, nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
