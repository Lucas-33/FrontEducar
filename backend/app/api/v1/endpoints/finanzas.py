from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.personas import Alumno, PadreAlumno

from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.finanzas import (
    ComprobantePago,
    ConfiguracionFinanciera,
    Factura,
    ItemFactura,
)
from backend.app.models.seguridad import Usuario
from backend.app.schemas.finanzas import (
    ComprobantePagoCreate,
    ConfiguracionUpdate,
    FacturaResponse,
    ItemFacturaResponse,
)

router = APIRouter()


@router.get(
    "/facturas/{legajo_alumno}",
    response_model=list[FacturaResponse],
    summary="Historial de deuda/facturas (Padres)",
)
def listar_facturas(
    legajo_alumno: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve las facturas de un alumno, discriminando los ítems de deuda."""
    # Nota: Acá deberíamos validar que el current_user (padre) sea el tutor de este legajo.

    facturas_db = (
        db.query(Factura)
        .filter(Factura.legajo_alumno == legajo_alumno)
        .order_by(Factura.id_factura.desc())
        .all()
    )

    resultado = []
    for f in facturas_db:
        items_db = (
            db.query(ItemFactura).filter(ItemFactura.id_factura == f.id_factura).all()
        )

        # Convertimos la BD al Schema de respuesta
        factura_dict = f.__dict__.copy()
        factura_dict["items"] = [
            ItemFacturaResponse.model_validate(i) for i in items_db
        ]
        resultado.append(FacturaResponse(**factura_dict))

    return resultado


@router.post(
    "/comprobantes",
    status_code=status.HTTP_201_CREATED,
    summary="Subir comprobante de pago (Padres)",
)
def subir_comprobante(
    comprobante_in: ComprobantePagoCreate,
    current_user: Usuario = Depends(require_roles("PARENT")),
    db: Session = Depends(get_db),
):
    """Vincula un ticket de transferencia bancaria a una factura pendiente."""
    factura = (
        db.query(Factura)
        .filter(Factura.id_factura == comprobante_in.id_factura)
        .first()
    )
    if not factura:
        raise HTTPException(status_code=404, detail="La factura no existe")

    nuevo_comprobante = ComprobantePago(
        id_factura=comprobante_in.id_factura,
        archivo_url=comprobante_in.archivo_url,
        estado="PENDIENTE",  # El administrador web luego lo aprobará
    )
    db.add(nuevo_comprobante)
    db.commit()
    return {"mensaje": "Comprobante enviado exitosamente a la administración"}


@router.put("/configuracion", summary="Actualizar precios base (Administrador)")
def actualizar_precio(
    config_in: ConfiguracionUpdate,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Permite al administrador modificar valores como CUOTA_BASE o COMEDOR."""
    config = (
        db.query(ConfiguracionFinanciera).filter_by(concepto=config_in.concepto).first()
    )
    if config:
        config.valor = config_in.valor
    else:
        config = ConfiguracionFinanciera(
            concepto=config_in.concepto, valor=config_in.valor
        )
        db.add(config)

    db.commit()
    return {
        "mensaje": f"Precio de {config_in.concepto} actualizado a ${config_in.valor}"
    }


@router.get("/configuracion/{concepto}", summary="Obtener precio base (Administrador)")
def obtener_precio(
    concepto: str,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Devuelve el valor actual de CUOTA_BASE o COMEDOR."""
    config = db.query(ConfiguracionFinanciera).filter_by(concepto=concepto).first()
    return {"valor": float(config.valor) if config else 0.0}


@router.get(
    "/mis-facturas", summary="Obtiene las facturas reales del tutor autenticado"
)
def obtener_facturas_padre(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    # 1. Validar que el usuario sea un tutor (que tenga un id_padre asignado)
    if not current_user.id_padre:
        return []

    # 2. Buscar los legajos de los hijos asociados a este padre
    relaciones = (
        db.query(PadreAlumno)
        .filter(PadreAlumno.id_padre == current_user.id_padre)
        .all()
    )
    legajos_hijos = [rel.legajo_alumno for rel in relaciones]

    if not legajos_hijos:
        return []

    # 3. Buscar los datos de los alumnos para sacar el nombre
    alumnos = db.query(Alumno).filter(Alumno.legajo.in_(legajos_hijos)).all()
    nombres_alumnos = {a.legajo: f"{a.apellido}, {a.nombre}" for a in alumnos}

    # 4. Buscar las facturas de esos legajos en PostgreSQL
    facturas_db = (
        db.query(Factura)
        .filter(Factura.legajo_alumno.in_(legajos_hijos))
        .order_by(Factura.fecha_vencimiento.desc())
        .all()
    )

    # 5. Formatear y devolver al Frontend (Flet)
    lista_facturas = []
    for f in facturas_db:
        lista_facturas.append(
            {
                "id": f.id_factura,
                "mes": f.mes,
                "anio": f.anio,
                "alumno_nombre": nombres_alumnos.get(f.legajo_alumno, "Estudiante"),
                "fecha_vencimiento": f.fecha_vencimiento.strftime("%d/%m/%Y")
                if f.fecha_vencimiento
                else "-",
                "total": float(f.total),
                "estado": f.estado.upper() if f.estado else "PENDIENTE",
            }
        )

    return lista_facturas
