from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ItemFacturaResponse(BaseModel):
    id_item: int
    concepto: str
    monto: float
    model_config = ConfigDict(from_attributes=True)


class FacturaResponse(BaseModel):
    id_factura: int
    legajo_alumno: int
    mes: int
    anio: int
    total: float
    estado: str
    fecha_emision: date
    fecha_vencimiento: date
    items: list[ItemFacturaResponse] = []  # Detalle de la deuda
    model_config = ConfigDict(from_attributes=True)


class ComprobantePagoCreate(BaseModel):
    id_factura: int
    archivo_url: str  # En la app móvil simularemos la subida subiendo a un bucket/nube y mandando la URL


class ConfiguracionUpdate(BaseModel):
    concepto: str
    valor: float
