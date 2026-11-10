"""Utilidades compartidas para interpretar fechas ingresadas por los usuarios."""

from datetime import date, datetime

FORMATOS_FECHA = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")

MENSAJE_FECHA_INVALIDA = (
    "La fecha de nacimiento debe tener un formato válido "
    "(por ejemplo, AAAA-MM-DD o DD/MM/AAAA)."
)


def parsear_fecha(valor: date | datetime | str | None) -> date:
    """Convierte los formatos habituales de fecha a ``date``.

    Se aceptan fechas ISO (AAAA-MM-DD) y el formato local (DD/MM/AAAA), ya que
    el formulario público y el panel administrativo no siempre coinciden.
    """
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor

    texto = str(valor or "").strip()
    for formato in FORMATOS_FECHA:
        try:
            return datetime.strptime(texto, formato).date()  # noqa: DTZ007
        except ValueError:
            continue
    raise ValueError(MENSAJE_FECHA_INVALIDA)


def edad_en_anio(fecha_nacimiento: date, anio: int) -> int:
    """Edad que la persona cumple durante el año indicado.

    Se usa el año del ciclo lectivo en lugar de la fecha exacta para que la
    validación no dependa del mes en que se realiza la inscripción.
    """
    return anio - fecha_nacimiento.year
