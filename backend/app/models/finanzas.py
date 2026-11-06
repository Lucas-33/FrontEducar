"""Entidades para la gestión de cuotas, facturación y pagos (PARTE 3)."""

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from backend.app.core.database import Base


class ConfiguracionFinanciera(Base):
    """Guarda valores fijos administrables, como el precio de la Cuota Base y el Comedor."""

    __tablename__ = "configuracion_financiera"

    id_configuracion = Column(Integer, primary_key=True, autoincrement=True)
    concepto = Column(
        String(50), nullable=False, unique=True
    )  # Ej: "CUOTA_BASE", "COMEDOR"
    valor = Column(Numeric(10, 2), nullable=False)


class Factura(Base):
    """Factura mensual consolidada de un alumno."""

    __tablename__ = "factura"

    id_factura = Column(Integer, primary_key=True, autoincrement=True)
    legajo_alumno = Column(
        Integer, ForeignKey("alumno.legajo", ondelete="CASCADE"), nullable=False
    )
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(
        String(20), default="PENDIENTE", nullable=False
    )  # PENDIENTE, PAGADA, PARCIAL
    fecha_emision = Column(Date, server_default=func.current_date(), nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)


class ItemFactura(Base):
    """Detalle de qué se está cobrando en la factura (Cuota, Vóleibol, Transporte Centro, etc)."""

    __tablename__ = "item_factura"

    id_item = Column(Integer, primary_key=True, autoincrement=True)
    id_factura = Column(
        Integer, ForeignKey("factura.id_factura", ondelete="CASCADE"), nullable=False
    )
    concepto = Column(String(100), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)


class ComprobantePago(Base):
    """Comprobante de transferencia subido por el padre desde la app móvil."""

    __tablename__ = "comprobante_pago"

    id_comprobante = Column(Integer, primary_key=True, autoincrement=True)
    id_factura = Column(
        Integer, ForeignKey("factura.id_factura", ondelete="CASCADE"), nullable=False
    )
    archivo_url = Column(
        String(255), nullable=False
    )  # Ruta física o URL de la imagen/PDF
    estado = Column(
        String(20), default="PENDIENTE", nullable=False
    )  # PENDIENTE, APROBADO, RECHAZADO
    fecha_subida = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
