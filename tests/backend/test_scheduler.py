from datetime import date
from unittest.mock import MagicMock, patch

from backend.app.core.scheduler import (
    es_ultimo_dia_habil,
    tarea_aviso_morosos,
    tarea_cierre_mensual,
)


def test_es_ultimo_dia_habil_viernes():
    """Prueba que detecte correctamente cuando el último día del mes cae fin de semana (Ej: Octubre 2026 tiene 31 el sábado, el viernes 30 es el último hábil)."""
    with patch("backend.app.core.scheduler.date") as mock_date:
        # Engañamos al sistema diciendo que hoy es Viernes 30 de Octubre de 2026
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
    # Configuramos el mock para que simule una respuesta exitosa
    mock_finanzas_service.generar_facturas_mes.return_value = {
        "mensaje": "Facturas generadas"
    }

    tarea_cierre_mensual()

    # Comprobamos que el scheduler efectivamente haya llamado a la función interna
    mock_finanzas_service.generar_facturas_mes.assert_called_once()


@patch("backend.app.core.scheduler.finanzas_service")
@patch("backend.app.core.scheduler.es_ultimo_dia_habil", return_value=False)
def test_tarea_cierre_mensual_se_aborta(mock_es_ultimo_dia, mock_finanzas_service):
    """Verifica que si NO es el último día hábil, la tarea se cancele y no facture nada."""
    tarea_cierre_mensual()

    # Comprobamos que NO se haya llamado a la base de datos
    mock_finanzas_service.generar_facturas_mes.assert_not_called()
