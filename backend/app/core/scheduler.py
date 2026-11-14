import calendar
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.app.core.database import SessionLocal
from backend.app.services.finanzas import finanzas_service

# from backend.app.services.email import enviar_factura, enviar_aviso_deuda (lo crearemos después)

scheduler = AsyncIOScheduler()


def es_ultimo_dia_habil() -> bool:
    """Calcula matemáticamente si hoy es el último día hábil (lunes a viernes) del mes."""
    hoy = date.today()
    ultimo_dia_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]
    fecha_fin = date(hoy.year, hoy.month, ultimo_dia_del_mes)

    # Si el último día cae Sábado (5), el último hábil es el viernes anterior (-1 día)
    if fecha_fin.weekday() == 5:
        fecha_fin = date(hoy.year, hoy.month, ultimo_dia_del_mes - 1)
    # Si el último día cae Domingo (6), el último hábil es el viernes anterior (-2 días)
    elif fecha_fin.weekday() == 6:
        fecha_fin = date(hoy.year, hoy.month, ultimo_dia_del_mes - 2)

    return hoy == fecha_fin


def tarea_cierre_mensual():
    """Se ejecuta y revisa si es el último día hábil. Genera facturas y las envía por mail."""
    if not es_ultimo_dia_habil():
        return
        
    print("⏰ [SCHEDULER] Ejecutando cierre mensual y envío de facturas...")
    db = SessionLocal() 
    try:
        hoy = date.today()
        # 1. Generar facturas en BD
        finanzas_service.generar_facturas_mes(db, mes=hoy.month, anio=hoy.year)
        
        # 2. Buscar las recién creadas y enviarlas
        facturas = db.query(Factura).filter_by(mes=hoy.month, anio=hoy.year).all()
        for fac in facturas:
            alumno = db.query(Alumno).filter_by(legajo=fac.legajo_alumno).first()
            if alumno and alumno.correo_electronico:
                items = db.query(ItemFactura).filter_by(id_factura=fac.id_factura).all()
                ruta_pdf = generar_pdf_factura(fac, alumno, items)
                
                cuerpo = f"Estimada familia de {alumno.nombre},\n\nAdjuntamos la liquidación de servicios educativos correspondiente al mes {fac.mes}/{fac.anio}.\n\nSaludos cordiales,\nAdministración Educar."
                enviar_correo_con_pdf(
                    destinatario=alumno.correo_electronico, 
                    asunto=f"Nueva Liquidación Mensual - {alumno.apellido}", 
                    cuerpo=cuerpo, 
                    ruta_pdf=ruta_pdf
                )
    except Exception as e:
        print(f"❌ [SCHEDULER] Error en cierre mensual: {e}")
    finally:
        db.close()


def tarea_aviso_morosos():
    """Se ejecuta los días 20 de cada mes. Envía PDF con recordatorio de deuda."""
    print("⏰ [SCHEDULER] Revisando morosos para enviar aviso de deuda...")
    db = SessionLocal()
    try:
        # Buscar todas las facturas impagas
        facturas_adeudadas = db.query(Factura).filter(Factura.estado != "PAGADA").all()
        for fac in facturas_adeudadas:
            alumno = db.query(Alumno).filter_by(legajo=fac.legajo_alumno).first()
            if alumno and alumno.correo_electronico:
                items = db.query(ItemFactura).filter_by(id_factura=fac.id_factura).all()
                ruta_pdf = generar_pdf_factura(fac, alumno, items)
                
                cuerpo = f"Aviso Importante: Saldo Pendiente\n\nEstimada familia de {alumno.nombre},\nLe recordamos que posee un saldo vencido de $ {fac.total:.2f} en su cuenta.\nLe adjuntamos el detalle. Por favor, regularice su situación a la brevedad para evitar recargos.\n\nSaludos."
                enviar_correo_con_pdf(
                    destinatario=alumno.correo_electronico, 
                    asunto="Aviso de Deuda - Educar para Transformar", 
                    cuerpo=cuerpo, 
                    ruta_pdf=ruta_pdf
                )
    except Exception as e:
        print(f"❌ [SCHEDULER] Error avisando a morosos: {e}")
    finally:
        db.close()


def iniciar_scheduler():
    """Registra los disparadores de tiempo y enciende el motor."""
    # Disparador 1: Corre TODOS LOS DÍAS a las 08:00 AM (la función por dentro chequea si es el último día hábil)
    scheduler.add_job(tarea_cierre_mensual, CronTrigger(hour=8, minute=0))

    # Disparador 2: Corre SOLAMENTE el día 20 de cada mes a las 08:00 AM
    scheduler.add_job(tarea_aviso_morosos, CronTrigger(day=20, hour=8, minute=0))

    scheduler.start()
    print("🚀 Planificador de tareas (APScheduler) iniciado en segundo plano.")
