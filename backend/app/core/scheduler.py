import calendar
import os
from datetime import date
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.app.core.database import SessionLocal
from backend.app.models.finanzas import Factura, ItemFactura
from backend.app.models.personas import Alumno, Padre, PadreAlumno
from backend.app.services.email_service import enviar_correo_con_pdf
from backend.app.services.finanzas import finanzas_service
from backend.app.services.pdf_generator import generar_pdf_factura

scheduler = AsyncIOScheduler()


def es_ultimo_dia_habil(referencia: date | None = None) -> bool:
    """Calcula matemáticamente si una fecha dada es el último día hábil (lunes a viernes) del mes."""
    hoy = referencia or date.today()
    ultimo_dia_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]
    fecha_fin = date(hoy.year, hoy.month, ultimo_dia_del_mes)

    # Si el último día cae Sábado (5), el último hábil es el viernes anterior (-1 día)
    if fecha_fin.weekday() == 5:
        fecha_fin = date(hoy.year, hoy.month, ultimo_dia_del_mes - 1)
    # Si el último día cae Domingo (6), el último hábil es el viernes anterior (-2 días)
    elif fecha_fin.weekday() == 6:
        fecha_fin = date(hoy.year, hoy.month, ultimo_dia_del_mes - 2)

    return hoy == fecha_fin


def _obtener_destinatarios_factura(
    db, legajo_alumno: int, alumno: Alumno | None
) -> list[str]:
    """Obtiene los correos electrónicos de los padres asociados o del alumno como fallback."""
    padres = (
        db.query(Padre)
        .join(PadreAlumno, Padre.id_padre == PadreAlumno.id_padre)
        .filter(PadreAlumno.legajo_alumno == legajo_alumno)
        .all()
    )
    destinatarios = [p.correo_electronico for p in padres if p.correo_electronico]

    if not destinatarios and alumno and alumno.correo_electronico:
        destinatarios = [alumno.correo_electronico]

    return list(set(destinatarios))


def _formatear_desglose_items(items: list[ItemFactura]) -> str:
    """Genera el texto con la composición detallada de los conceptos cobrados."""
    if not items:
        return "  • Cuota consolidada escolar"
    lineas = []
    for item in items:
        lineas.append(f"  • {item.concepto}: $ {float(item.monto):,.2f}")
    return "\n".join(lineas)


def tarea_cierre_mensual(
    forzar: bool = False,
    mes: int | None = None,
    anio: int | None = None,
    email_override: str | None = None,
) -> dict[str, Any]:
    """Se ejecuta y revisa si es el último día hábil del mes (o si forzar=True).

    Genera las facturas correspondientes y envía un correo a cada familia con:
    1. El total a abonar.
    2. La composición detallada del valor (cuota base, comedor, transporte, deportes).
    3. La factura adjunta en formato PDF.
    Si se proporciona email_override, todos los correos se redirigen a esa dirección (ideal para pruebas).
    """
    hoy = date.today()
    if not forzar and not es_ultimo_dia_habil(hoy):
        return {
            "ejecutado": False,
            "motivo": f"Hoy ({hoy}) no es el último día hábil del mes.",
        }

    mes_objetivo = mes or hoy.month
    anio_objetivo = anio or hoy.year

    print(
        f"⏰ [SCHEDULER] Iniciando cierre mensual y emisión de facturas para {mes_objetivo}/{anio_objetivo}..."
    )
    db = SessionLocal()
    correos_enviados = 0
    facturas_procesadas = 0
    detalles_envio: list[dict[str, Any]] = []

    try:
        # 1. Generar facturas en BD (si no existen aún)
        resultado_generacion = finanzas_service.generar_facturas_mes(
            db, mes=mes_objetivo, anio=anio_objetivo
        )
        print(f"📊 [SCHEDULER] {resultado_generacion.get('mensaje')}")

        # 2. Buscar facturas del período
        facturas = (
            db.query(Factura).filter_by(mes=mes_objetivo, anio=anio_objetivo).all()
        )

        for fac in facturas:
            facturas_procesadas += 1
            alumno = db.query(Alumno).filter_by(legajo=fac.legajo_alumno).first()
            items = db.query(ItemFactura).filter_by(id_factura=fac.id_factura).all()
            destinatarios = (
                [email_override.strip()]
                if email_override
                else _obtener_destinatarios_factura(db, fac.legajo_alumno, alumno)
            )

            if not alumno or not destinatarios:
                continue

            desglose = _formatear_desglose_items(items)
            venc_str = (
                fac.fecha_vencimiento.strftime("%d/%m/%Y")
                if fac.fecha_vencimiento
                else "A definir"
            )

            # Generar factura PDF adjunta
            ruta_pdf = generar_pdf_factura(fac, alumno, items)

            cuerpo = (
                f"Estimada familia de {alumno.nombre} {alumno.apellido}:\n\n"
                f"Le informamos que se encuentra disponible la liquidación correspondiente al período {fac.mes:02d}/{fac.anio}.\n\n"
                f"TOTAL A ABONAR: $ {float(fac.total):,.2f}\n"
                f"Fecha límite de vencimiento: {venc_str}\n\n"
                f"COMPOSICIÓN DEL VALOR:\n"
                f"--------------------------------------------------\n"
                f"{desglose}\n"
                f"--------------------------------------------------\n"
                f"Total liquidado: $ {float(fac.total):,.2f}\n\n"
                f"Adjuntamos a este correo la factura oficial en formato PDF.\n\n"
                f"Medios de Pago (Transferencia Bancaria):\n"
                f"  • Banco: Banco de la Nación Argentina\n"
                f"  • CBU: 0110599520000012345678\n"
                f"  • Alias: EDUCAR.COLEGIO.TRANS\n\n"
                f"Podrá cargar el comprobante en formato PDF directamente desde la aplicación móvil o el portal web familiar.\n\n"
                f"Saludos cordiales,\n"
                f"Administración - Educar para Transformar"
            )

            asunto = f"Liquidación de Cuota Escolar {fac.mes:02d}/{fac.anio} - {alumno.apellido}, {alumno.nombre}"

            enviado = enviar_correo_con_pdf(
                destinatario=destinatarios,
                asunto=asunto,
                cuerpo=cuerpo,
                ruta_pdf=ruta_pdf,
                borrar_despues=False,
            )

            # Limpiar PDF temporal generado para este envío
            if ruta_pdf and os.path.exists(ruta_pdf):
                try:
                    os.remove(ruta_pdf)
                except Exception:
                    pass

            if enviado:
                correos_enviados += len(destinatarios)
                detalles_envio.append(
                    {
                        "id_factura": fac.id_factura,
                        "alumno": f"{alumno.apellido}, {alumno.nombre}",
                        "destinatarios": destinatarios,
                        "total": float(fac.total),
                    }
                )

        return {
            "ejecutado": True,
            "periodo": f"{mes_objetivo}/{anio_objetivo}",
            "facturas_procesadas": facturas_procesadas,
            "correos_enviados": correos_enviados,
            "detalles": detalles_envio,
        }

    except Exception as e:
        print(f"❌ [SCHEDULER] Error en cierre mensual: {e}")
        return {
            "ejecutado": False,
            "error": str(e),
            "facturas_procesadas": facturas_procesadas,
            "correos_enviados": correos_enviados,
        }
    finally:
        db.close()


def tarea_aviso_morosos(
    forzar: bool = False, email_override: str | None = None
) -> dict[str, Any]:
    """Se ejecuta los días 20 de cada mes (o si forzar=True).

    Envía a cada padre con saldo pendiente el recordatorio de deuda,
    detallando los ítems adeudados y adjuntando la liquidación en formato PDF.
    Si se proporciona email_override, todos los correos se redirigen a esa dirección (ideal para pruebas).
    """
    print(
        "⏰ [SCHEDULER] Revisando cuentas con saldo pendiente para aviso del día 20..."
    )
    db = SessionLocal()
    correos_enviados = 0
    facturas_adeudadas_count = 0
    detalles_envio: list[dict[str, Any]] = []

    try:
        # Buscar todas las facturas impagas (PENDIENTE o PARCIAL)
        facturas_adeudadas = (
            db.query(Factura)
            .filter(Factura.estado != "PAGADA")
            .order_by(Factura.fecha_vencimiento.asc())
            .all()
        )

        for fac in facturas_adeudadas:
            facturas_adeudadas_count += 1
            alumno = db.query(Alumno).filter_by(legajo=fac.legajo_alumno).first()
            items = db.query(ItemFactura).filter_by(id_factura=fac.id_factura).all()
            destinatarios = (
                [email_override.strip()]
                if email_override
                else _obtener_destinatarios_factura(db, fac.legajo_alumno, alumno)
            )

            if not alumno or not destinatarios:
                continue

            desglose = _formatear_desglose_items(items)
            venc_str = (
                fac.fecha_vencimiento.strftime("%d/%m/%Y")
                if fac.fecha_vencimiento
                else "Vencida"
            )

            # Generar el PDF adjunto de deuda
            ruta_pdf = generar_pdf_factura(fac, alumno, items)

            cuerpo = (
                f"AVISO DE SALDO PENDIENTE - Educar para Transformar\n\n"
                f"Estimada familia de {alumno.nombre} {alumno.apellido}:\n\n"
                f"Le informamos que a la fecha registra un saldo pendiente de pago por la suma de $ {float(fac.total):,.2f}, correspondiente a la liquidación del período {fac.mes:02d}/{fac.anio} (Fecha de vencimiento: {venc_str}).\n\n"
                f"DETALLE DE LA DEUDA PENDIENTE:\n"
                f"--------------------------------------------------\n"
                f"{desglose}\n"
                f"--------------------------------------------------\n"
                f"Saldo total adeudado: $ {float(fac.total):,.2f}\n\n"
                f"Le solicitamos regularizar la situación a la brevedad para evitar recargos administrativos.\n"
                f"Adjuntamos a este correo la factura en formato PDF con la liquidación detallada.\n\n"
                f"Puede abonar mediante transferencia y adjuntar su comprobante en formato PDF desde la aplicación móvil:\n"
                f"  • Banco: Banco de la Nación Argentina\n"
                f"  • CBU: 0110599520000012345678\n"
                f"  • Alias: EDUCAR.COLEGIO.TRANS\n\n"
                f"Si ya realizó el pago y envió el comprobante, por favor desestime este aviso.\n\n"
                f"Saludos cordiales,\n"
                f"Departamento de Cobranzas - Educar para Transformar"
            )

            asunto = f"Aviso de Saldo Pendiente - Cuota {fac.mes:02d}/{fac.anio} - {alumno.apellido}, {alumno.nombre}"

            enviado = enviar_correo_con_pdf(
                destinatario=destinatarios,
                asunto=asunto,
                cuerpo=cuerpo,
                ruta_pdf=ruta_pdf,
                borrar_despues=False,
            )

            # Limpiar PDF temporal generado
            if ruta_pdf and os.path.exists(ruta_pdf):
                try:
                    os.remove(ruta_pdf)
                except Exception:
                    pass

            if enviado:
                correos_enviados += len(destinatarios)
                detalles_envio.append(
                    {
                        "id_factura": fac.id_factura,
                        "alumno": f"{alumno.apellido}, {alumno.nombre}",
                        "destinatarios": destinatarios,
                        "deuda": float(fac.total),
                        "periodo": f"{fac.mes:02d}/{fac.anio}",
                    }
                )

        return {
            "ejecutado": True,
            "facturas_adeudadas": facturas_adeudadas_count,
            "correos_enviados": correos_enviados,
            "detalles": detalles_envio,
        }

    except Exception as e:
        print(f"❌ [SCHEDULER] Error enviando avisos de deuda: {e}")
        return {
            "ejecutado": False,
            "error": str(e),
            "facturas_adeudadas": facturas_adeudadas_count,
            "correos_enviados": correos_enviados,
        }
    finally:
        db.close()


def iniciar_scheduler():
    """Registra los disparadores de tiempo y enciende el motor APScheduler."""
    # Disparador 1: Corre TODOS LOS DÍAS a las 08:00 AM (la función por dentro chequea si es el último día hábil)
    scheduler.add_job(
        tarea_cierre_mensual,
        CronTrigger(hour=8, minute=0),
        id="cierre_mensual_facturas",
        replace_existing=True,
    )

    # Disparador 2: Corre SOLAMENTE el día 20 de cada mes a las 08:00 AM
    scheduler.add_job(
        tarea_aviso_morosos,
        CronTrigger(day=20, hour=8, minute=0),
        id="aviso_morosos_mensual",
        replace_existing=True,
    )

    if not scheduler.running:
        scheduler.start()
        print("🚀 Planificador de tareas (APScheduler) iniciado en segundo plano.")
