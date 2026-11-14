from datetime import date
from unittest.mock import MagicMock, patch

from backend.app.core.scheduler import (
    es_ultimo_dia_habil,
    tarea_aviso_morosos,
    tarea_cierre_mensual,
)


def test_es_ultimo_dia_habil_viernes():
    """Prueba que detecte correctamente cuando el último día del mes cae fin de semana."""
    with patch("backend.app.core.scheduler.date") as mock_date:
        mock_date.today.return_value = date(2026, 10, 30)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert es_ultimo_dia_habil() is True


def test_no_es_ultimo_dia_habil():
    """Prueba un día normal a mitad de mes."""
    with patch("backend.app.core.scheduler.date") as mock_date:
        mock_date.today.return_value = date(2026, 10, 15)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert es_ultimo_dia_habil() is False


@patch("backend.app.core.scheduler.finanzas_service")
@patch("backend.app.core.scheduler.es_ultimo_dia_habil", return_value=True)
def test_tarea_cierre_mensual_se_ejecuta(mock_es_ultimo_dia, mock_finanzas_service):
    """Verifica que si es el último día hábil, se llame al servicio de generar facturas."""
    mock_finanzas_service.generar_facturas_mes.return_value = {
        "mensaje": "Facturas generadas"
    }

    resultado = tarea_cierre_mensual()

    mock_finanzas_service.generar_facturas_mes.assert_called_once()
    assert resultado["ejecutado"] is True


@patch("backend.app.core.scheduler.finanzas_service")
@patch("backend.app.core.scheduler.es_ultimo_dia_habil", return_value=False)
def test_tarea_cierre_mensual_se_aborta(mock_es_ultimo_dia, mock_finanzas_service):
    """Verifica que si NO es el último día hábil, la tarea se cancele y no facture nada."""
    resultado = tarea_cierre_mensual(forzar=False)

    mock_finanzas_service.generar_facturas_mes.assert_not_called()
    assert resultado["ejecutado"] is False


@patch("backend.app.core.scheduler.SessionLocal")
def test_tarea_aviso_morosos_sin_deudores(mock_session_local):
    """Verifica que tarea_aviso_morosos maneje correctamente cuando no hay morosos."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    resultado = tarea_aviso_morosos(forzar=True)

    assert resultado["ejecutado"] is True
    assert resultado["facturas_adeudadas"] == 0
    assert resultado["correos_enviados"] == 0
    mock_db.close.assert_called_once()


@patch("backend.app.core.scheduler.enviar_correo_con_pdf", return_value=True)
@patch("backend.app.core.scheduler.generar_pdf_factura", return_value="temp/test.pdf")
@patch("backend.app.core.scheduler.SessionLocal")
def test_tarea_aviso_morosos_con_deudores(mock_session_local, mock_gen_pdf, mock_email):
    """Verifica el envío de aviso el día 20 a facturas adeudadas con desglose y PDF."""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    # Factura adeudada mock
    mock_factura = MagicMock()
    mock_factura.id_factura = 1
    mock_factura.legajo_alumno = 1001
    mock_factura.mes = 10
    mock_factura.anio = 2026
    mock_factura.total = 85000.00
    mock_factura.estado = "PENDIENTE"
    mock_factura.fecha_vencimiento = date(2026, 11, 10)

    # Alumno mock
    mock_alumno = MagicMock()
    mock_alumno.legajo = 1001
    mock_alumno.nombre = "Juan"
    mock_alumno.apellido = "Pérez"
    mock_alumno.correo_electronico = "juan@educar.test"

    # Items mock
    mock_item = MagicMock()
    mock_item.concepto = "Cuota Base Mensual"
    mock_item.monto = 85000.00

    # Configuración de respuestas de query
    def mock_query(model):
        m = MagicMock()
        if hasattr(model, "__tablename__") and model.__tablename__ == "factura":
            m.filter.return_value.order_by.return_value.all.return_value = [
                mock_factura
            ]
        elif hasattr(model, "__tablename__") and model.__tablename__ == "alumno":
            m.filter_by.return_value.first.return_value = mock_alumno
        elif hasattr(model, "__tablename__") and model.__tablename__ == "item_factura":
            m.filter_by.return_value.all.return_value = [mock_item]
        elif hasattr(model, "__tablename__") and model.__tablename__ == "padre":
            m.join.return_value.filter.return_value.all.return_value = []
        return m

    mock_db.query.side_effect = mock_query

    resultado = tarea_aviso_morosos(forzar=True)

    assert resultado["ejecutado"] is True
    assert resultado["facturas_adeudadas"] == 1
    assert resultado["correos_enviados"] == 1
    mock_email.assert_called_once()
    assert "85,000.00" in mock_email.call_args.kwargs["cuerpo"]
    assert "Cuota Base Mensual" in mock_email.call_args.kwargs["cuerpo"]
