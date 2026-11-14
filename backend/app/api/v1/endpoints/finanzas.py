import os
import uuid
from datetime import date, datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.api.deps import bearer_scheme, get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.core.scheduler import tarea_aviso_morosos, tarea_cierre_mensual
from backend.app.models.academico import Curso
from backend.app.models.finanzas import (
    ComprobantePago,
    ConfiguracionFinanciera,
    Factura,
    ItemFactura,
)
from backend.app.models.personas import Alumno, PadreAlumno
from backend.app.models.seguridad import Usuario
from backend.app.schemas.finanzas import (
    ComprobantePagoCreate,
    ConfiguracionUpdate,
    FacturaResponse,
    ItemFacturaResponse,
)
from backend.app.services.finanzas import finanzas_service
from backend.app.services.pdf_generator import generar_pdf_constancia_comprobante
from backend.app.services.seguridad import seguridad_service

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


def _obtener_usuario_comprobante(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    token_form: str | None = Form(None, alias="token"),
    token_query: str | None = Query(None, alias="token"),
    db: Session = Depends(get_db),
) -> Usuario:
    """Permite autorizar la subida de comprobantes tanto por header Bearer como por Form o Query param."""
    raw_token = (
        credentials.credentials
        if (credentials and credentials.credentials)
        else (token_form or token_query)
    )
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = seguridad_service.get_usuario_from_token(db, raw_token)
    rol = seguridad_service.get_rol_nombre(db, user)
    if rol not in ("PARENT", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para subir comprobantes",
        )
    return user


@router.post(
    "/comprobantes/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Subir comprobante de pago en formato PDF desde el dispositivo",
)
def subir_comprobante_archivo(
    id_factura: int = Form(...),
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(_obtener_usuario_comprobante),
    db: Session = Depends(get_db),
):
    """Recibe un archivo PDF de comprobante de transferencia y lo asocia a la factura."""
    factura = db.query(Factura).filter(Factura.id_factura == id_factura).first()
    if not factura:
        raise HTTPException(status_code=404, detail="La factura no existe")

    # Validar que el usuario (padre) sea tutor del alumno de esta factura
    if current_user.id_padre:
        es_tutor = (
            db.query(PadreAlumno)
            .filter(
                PadreAlumno.id_padre == current_user.id_padre,
                PadreAlumno.legajo_alumno == factura.legajo_alumno,
            )
            .first()
        )
        if not es_tutor:
            raise HTTPException(
                status_code=403,
                detail="No tiene permiso para subir comprobantes para esta factura",
            )

    nombre_original = archivo.filename or "comprobante.pdf"
    if not nombre_original.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Formato de archivo inválido. Solo se admiten archivos en formato .PDF",
        )

    # Crear carpeta física de destino si no existe
    upload_dir = os.path.join(os.getcwd(), "uploads", "comprobantes")
    os.makedirs(upload_dir, exist_ok=True)

    # Generar nombre seguro y único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sufijo_random = uuid.uuid4().hex[:6]
    nombre_seguro = f"fac_{id_factura}_{timestamp}_{sufijo_random}.pdf"
    ruta_destino = os.path.join(upload_dir, nombre_seguro)

    # Guardar contenido en disco
    contenido = archivo.file.read()
    if len(contenido) == 0:
        raise HTTPException(
            status_code=400, detail="El archivo PDF seleccionado está vacío"
        )

    with open(ruta_destino, "wb") as f_out:
        f_out.write(contenido)

    # Registrar en base de datos
    url_relativa = f"/uploads/comprobantes/{nombre_seguro}"
    nuevo_comprobante = ComprobantePago(
        id_factura=id_factura,
        archivo_url=url_relativa,
        estado="PENDIENTE",
    )
    db.add(nuevo_comprobante)
    db.commit()
    db.refresh(nuevo_comprobante)

    return {
        "mensaje": "Comprobante PDF recibido correctamente y en revisión por administración",
        "id_comprobante": nuevo_comprobante.id_comprobante,
        "archivo_url": nuevo_comprobante.archivo_url,
        "nombre_original": nombre_original,
    }


@router.get(
    "/comprobantes/pendientes",
    summary="Listar comprobantes de pago en revisión (Administrador)",
)
def listar_comprobantes_pendientes(
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Devuelve la nómina de comprobantes bancarios subidos por tutores que esperan validación."""
    return finanzas_service.listar_comprobantes_pendientes(db)


@router.get(
    "/comprobantes/{id_comprobante}/archivo",
    summary="Descargar o visualizar archivo PDF de comprobante de pago",
)
def obtener_archivo_comprobante(
    id_comprobante: int,
    current_user: Usuario = Depends(_obtener_usuario_comprobante),
    db: Session = Depends(get_db),
):
    """Permite visualizar el comprobante bancario subido o genera una constancia digital en PDF."""
    comp = (
        db.query(ComprobantePago)
        .filter(ComprobantePago.id_comprobante == id_comprobante)
        .first()
    )
    if not comp:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    factura = db.query(Factura).filter(Factura.id_factura == comp.id_factura).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura asociada no encontrada")

    rol = seguridad_service.get_rol_nombre(db, current_user)
    if rol == "PARENT":
        alumno_check = (
            db.query(PadreAlumno)
            .filter(
                PadreAlumno.id_padre == current_user.id_usuario,
                PadreAlumno.legajo_alumno == factura.legajo_alumno,
            )
            .first()
        )
        if not alumno_check:
            raise HTTPException(
                status_code=403,
                detail="No tiene permiso para ver comprobantes de este alumno",
            )

    # 1. Verificar si existe un archivo físico real en disco
    archivo_rel = (comp.archivo_url or "").strip()
    archivo_limpio = archivo_rel.replace("\\", "/")
    if archivo_limpio.startswith("/uploads/"):
        archivo_limpio = archivo_limpio[len("/uploads/") :]
    elif archivo_limpio.startswith("uploads/"):
        archivo_limpio = archivo_limpio[len("uploads/") :]

    posibles_rutas = [
        os.path.join(os.getcwd(), "uploads", archivo_limpio),
        os.path.join(os.getcwd(), "uploads", "comprobantes", archivo_limpio),
        os.path.join(
            os.getcwd(),
            "uploads",
            "comprobantes",
            os.path.basename(archivo_limpio),
        ),
        archivo_rel,
    ]

    for ruta in posibles_rutas:
        if os.path.isfile(ruta):
            media_type = "application/pdf"
            if ruta.lower().endswith((".png", ".jpg", ".jpeg")):
                media_type = (
                    "image/png" if ruta.lower().endswith(".png") else "image/jpeg"
                )
            return FileResponse(
                path=ruta,
                media_type=media_type,
                filename=os.path.basename(ruta),
            )

    # 2. Si no hay archivo físico (ej. cargado con referencia manual o entorno demo),
    # generamos dinámicamente la constancia institucional oficial en PDF
    alumno = db.query(Alumno).filter(Alumno.legajo == factura.legajo_alumno).first()
    curso = (
        db.query(Curso).filter(Curso.id_curso == alumno.id_curso).first()
        if alumno and alumno.id_curso
        else None
    )
    items = (
        db.query(ItemFactura).filter(ItemFactura.id_factura == factura.id_factura).all()
    )

    alumno_datos = {
        "nombre_completo": f"{alumno.apellido}, {alumno.nombre}"
        if alumno
        else f"Legajo #{factura.legajo_alumno}",
        "legajo": alumno.legajo if alumno else factura.legajo_alumno,
        "dni": alumno.dni if alumno else "-",
        "curso": curso.nombre if curso else "Sin Curso",
    }
    items_datos = [{"concepto": it.concepto, "monto": float(it.monto)} for it in items]
    fecha_subida_str = (
        comp.fecha_subida.strftime("%d/%m/%Y %H:%M") if comp.fecha_subida else "-"
    )

    pdf_bytes = generar_pdf_constancia_comprobante(
        id_comprobante=comp.id_comprobante,
        id_factura=factura.id_factura,
        archivo_url=comp.archivo_url,
        estado_comprobante=comp.estado,
        fecha_subida=fecha_subida_str,
        alumno_datos=alumno_datos,
        total_factura=float(factura.total),
        items=items_datos,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=comprobante_{comp.id_comprobante}.pdf"
        },
    )


@router.put(
    "/comprobantes/{id_comprobante}/aprobar",
    summary="Aprobar comprobante y cancelar cuota (Administrador)",
)
def aprobar_comprobante(
    id_comprobante: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Aprueba el comprobante de transferencia y pasa la factura a PAGADA."""
    return finanzas_service.aprobar_comprobante(db, id_comprobante)


@router.put(
    "/comprobantes/{id_comprobante}/rechazar",
    summary="Rechazar comprobante de pago (Administrador)",
)
def rechazar_comprobante(
    id_comprobante: int,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Rechaza el comprobante y restablece la factura a PENDIENTE."""
    return finanzas_service.rechazar_comprobante(db, id_comprobante)


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

    # 5. Formatear y devolver al Frontend (Flet) con desglose de ítems y comprobantes
    lista_facturas = []
    for f in facturas_db:
        items_db = (
            db.query(ItemFactura).filter(ItemFactura.id_factura == f.id_factura).all()
        )
        comprobantes_db = (
            db.query(ComprobantePago)
            .filter(ComprobantePago.id_factura == f.id_factura)
            .order_by(ComprobantePago.id_comprobante.desc())
            .all()
        )
        lista_facturas.append(
            {
                "id": f.id_factura,
                "mes": f.mes,
                "anio": f.anio,
                "legajo_alumno": f.legajo_alumno,
                "alumno_nombre": nombres_alumnos.get(f.legajo_alumno, "Estudiante"),
                "fecha_emision": f.fecha_emision.strftime("%d/%m/%Y")
                if f.fecha_emision
                else "-",
                "fecha_vencimiento": f.fecha_vencimiento.strftime("%d/%m/%Y")
                if f.fecha_vencimiento
                else "-",
                "total": float(f.total),
                "estado": f.estado.upper() if f.estado else "PENDIENTE",
                "items": [
                    {
                        "id_item": it.id_item,
                        "concepto": it.concepto,
                        "monto": float(it.monto),
                    }
                    for it in items_db
                ],
                "comprobantes": [
                    {
                        "id_comprobante": c.id_comprobante,
                        "archivo_url": c.archivo_url,
                        "estado": c.estado.upper() if c.estado else "PENDIENTE",
                        "fecha_subida": c.fecha_subida.strftime("%d/%m/%Y %H:%M")
                        if c.fecha_subida
                        else "-",
                    }
                    for c in comprobantes_db
                ],
            }
        )

    return lista_facturas


@router.post(
    "/scheduler/cierre-mensual",
    summary="Ejecutar cierre mensual y emisión de facturas con envío por correo (Admin)",
)
def ejecutar_cierre_mensual_endpoint(
    mes: int | None = None,
    anio: int | None = None,
    current_user: Usuario = Depends(require_roles("ADMIN")),
):
    """Fuerza la ejecución del cierre mensual, detallando los conceptos facturados y enviando el PDF por correo."""
    return tarea_cierre_mensual(forzar=True, mes=mes, anio=anio)


@router.post(
    "/scheduler/aviso-morosos",
    summary="Ejecutar envío de avisos a morosos del día 20 por correo (Admin)",
)
def ejecutar_aviso_morosos_endpoint(
    current_user: Usuario = Depends(require_roles("ADMIN")),
):
    """Fuerza la ejecución del aviso de saldo pendiente con factura detallada en PDF a las familias con deuda."""
    return tarea_aviso_morosos(forzar=True)


# ==================== REPORTES FINANCIEROS Y DE PAGOS ====================
@router.get(
    "/reportes/ingresos",
    summary="Listado de ingresos por período de tiempo (Admin)",
)
def reporte_ingresos(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    mes: int | None = None,
    anio: int | None = None,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Devuelve el total recaudado y las facturas cobradas en el período con su detalle."""
    return finanzas_service.obtener_reporte_ingresos(
        db, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, mes=mes, anio=anio
    )


@router.get(
    "/reportes/pagos-completos",
    summary="Listado de pagos completos por período discriminado por año y alumno (Admin)",
)
def reporte_pagos_completos(
    anio: int | None = None,
    mes: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Devuelve los pagos completos realizados en el período, discriminados por año y curso/alumno."""
    return finanzas_service.obtener_reporte_pagos_completos(
        db, anio=anio, mes=mes, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
    )


@router.get(
    "/reportes/pagos-incompletos",
    summary="Listado de pagos incompletos/morosos por período discriminado por año y alumno (Admin)",
)
def reporte_pagos_incompletos(
    anio: int | None = None,
    mes: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Devuelve las deudas y pagos incompletos del período, discriminados por año y curso/alumno."""
    return finanzas_service.obtener_reporte_pagos_incompletos(
        db, anio=anio, mes=mes, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
    )


@router.get(
    "/reportes/deportes",
    summary="Listado de pagos de alumnos por deporte, nivel, horario y profesor a cargo (Admin)",
)
def reporte_pagos_deportes(
    mes: int | None = None,
    anio: int | None = None,
    id_deporte: int | None = None,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Devuelve el estado de cobro de deportes por disciplina, nivel, horario y profesor responsable."""
    return finanzas_service.obtener_reporte_pagos_deportes(
        db, mes=mes, anio=anio, id_deporte=id_deporte
    )


@router.get(
    "/reportes/transporte",
    summary="Listado de pagos de alumnos por recorrido del servicio de transporte (Admin)",
)
def reporte_pagos_transporte(
    mes: int | None = None,
    anio: int | None = None,
    id_recorrido: int | None = None,
    current_user: Usuario = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    """Devuelve el estado de cobro del transporte escolar por recorrido contratado."""
    return finanzas_service.obtener_reporte_pagos_transporte(
        db, mes=mes, anio=anio, id_recorrido=id_recorrido
    )
