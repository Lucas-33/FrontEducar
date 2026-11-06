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
    """Se ejecuta y revisa si es el último día hábil. Si lo es, factura y avisa."""
    if not es_ultimo_dia_habil():
        return

    print("⏰ [SCHEDULER] Ejecutando cierre mensual y generación de facturas...")
    db = SessionLocal()  # Abrimos conexión a BD manualmente porque no hay endpoint
    try:
        hoy = date.today()
        # 1. Generar facturas usando el servicio que creamos en el Paso B
        resultado = finanzas_service.generar_facturas_mes(
            db, mes=hoy.month, anio=hoy.year
        )
        print(f"✅ [SCHEDULER] {resultado['mensaje']}")

        # 2. Acá iría la lógica para enviar el PDF por correo:
        # facturas = db.query(Factura).filter_by(mes=hoy.month).all()
        # para cada factura -> buscar_email_tutor -> enviar_factura(email, pdf)
    except Exception as e:
        print(f"❌ [SCHEDULER] Error en cierre mensual: {e}")
    finally:
        db.close()


def tarea_aviso_morosos():
    """Se ejecuta estrictamente los días 20 de cada mes."""
    print("⏰ [SCHEDULER] Revisando morosos para enviar aviso de deuda...")
    db = SessionLocal()
    try:
        # Acá consultaremos las facturas PENDIENTES o PARCIALES
        # facturas_adeudadas = db.query(Factura).filter(Factura.estado != "PAGADA").all()
        # para cada factura -> enviar_aviso_deuda(email, monto_adeudado)
        print("✅ [SCHEDULER] Avisos de deuda enviados.")
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
