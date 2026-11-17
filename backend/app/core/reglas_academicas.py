"""Reglas de negocio para una matriculación coherente con la edad del alumno.

La edad se calcula como la que el alumno cumple durante el ciclo lectivo
(año actual), de modo que la validación no dependa del mes de inscripción.
Se permite un año de margen para alumnos que repitieron o ingresaron tarde.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date

from fastapi import HTTPException, status

from backend.app.core.fechas import edad_en_anio, parsear_fecha
from backend.app.models.academico import Curso, NivelEducativo

# Un año adicional respecto de la edad teórica, para admitir repitentes.
MARGEN_EDAD_REPITENTE = 1

# Edad teórica con la que se cursa cada grado/año.
_EDADES_POR_CICLO: dict[str, dict[int, int]] = {
    "inicial": {3: 3, 4: 4, 5: 5},
    "primario": {1: 6, 2: 7, 3: 8, 4: 9, 5: 10, 6: 11, 7: 12},
    "secundario": {1: 12, 2: 13, 3: 14, 4: 15, 5: 16, 6: 17, 7: 18},
}

_ETIQUETAS_CICLO = {
    "inicial": "Inicial",
    "primario": "Primario",
    "secundario": "Secundario",
}

_RE_SALA = re.compile(r"\bsala\s*(?:de\s*)?(\d{1,2})\b")
_RE_GRADO = re.compile(
    r"\b(\d{1,2})\s*(?:[°º]|er|ro|do|to|mo|vo|no|ra|da|ta|ma|va)?\.?\s*grado\b"
)
_RE_ANIO = re.compile(
    r"\b(\d{1,2})\s*(?:[°º]|er|ro|do|to|mo|vo|no|ra|da|ta|ma|va)?\.?\s*ano\b"
)


@dataclass(frozen=True)
class RangoEdad:
    """Rango de edades admitido para un curso, nivel o grado."""

    edad_minima: int
    edad_maxima: int
    descripcion: str


def _normalizar(texto: str | None) -> str:
    """Pasa a minúsculas y elimina tildes para comparar nombres de cursos."""
    if not texto:
        return ""
    sin_tildes = unicodedata.normalize("NFKD", str(texto))
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_tildes.casefold()).strip()


def _detectar_grado(nombre: str) -> tuple[str, int] | None:
    """Extrae el ciclo y el número de grado desde el nombre del curso."""
    coincidencia = _RE_SALA.search(nombre)
    if coincidencia:
        return "inicial", int(coincidencia.group(1))

    coincidencia = _RE_GRADO.search(nombre)
    if coincidencia:
        return "primario", int(coincidencia.group(1))

    coincidencia = _RE_ANIO.search(nombre)
    if coincidencia:
        return "secundario", int(coincidencia.group(1))

    return None


def _detectar_ciclo(nombre: str) -> str | None:
    if "inicial" in nombre or "jardin" in nombre:
        return "inicial"
    if "primari" in nombre:
        return "primario"
    if "secundari" in nombre:
        return "secundario"
    return None


def _construir_rango(
    ciclo: str, grado: int | None, referencia: str
) -> RangoEdad:
    edades = _EDADES_POR_CICLO[ciclo]

    if grado is None:
        return RangoEdad(
            edad_minima=min(edades.values()),
            edad_maxima=max(edades.values()) + MARGEN_EDAD_REPITENTE,
            descripcion=f"{_ETIQUETAS_CICLO[ciclo]} (todos los grados)",
        )

    edad_base = edades.get(grado)
    if edad_base is None:
        grados_validos = ", ".join(str(valor) for valor in sorted(edades))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No hay una regla de edad configurada para «{referencia}». "
                f"Los grados válidos para {_ETIQUETAS_CICLO[ciclo]} son: "
                f"{grados_validos}."
            ),
        )

    return RangoEdad(
        edad_minima=edad_base,
        edad_maxima=edad_base + MARGEN_EDAD_REPITENTE,
        descripcion=referencia,
    )


def rango_edad_curso(
    curso: Curso, nivel: NivelEducativo | None = None
) -> RangoEdad:
    """Obtiene el rango de edad esperado para un curso concreto."""
    nombre_curso = _normalizar(curso.nombre)
    detectado = _detectar_grado(nombre_curso)

    if detectado:
        ciclo, grado = detectado
    else:
        ciclo = _detectar_ciclo(nombre_curso) or _detectar_ciclo(
            _normalizar(nivel.nombre if nivel else None)
        )
        grado = None

    if ciclo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No se pudo determinar el nivel educativo del curso «{curso.nombre}». "
                "Use un nombre que incluya el grado o año "
                "(por ejemplo, «1° Grado A» o «2° Año B»)."
            ),
        )

    return _construir_rango(ciclo, grado, curso.nombre)


def rango_edad_nivel(nivel: str) -> RangoEdad:
    """Obtiene el rango de edad esperado para un nivel o grado postulado."""
    nombre = _normalizar(nivel)
    detectado = _detectar_grado(nombre)

    if detectado:
        ciclo, grado = detectado
    else:
        ciclo, grado = _detectar_ciclo(nombre), None

    if ciclo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"El nivel educativo «{nivel}» no es reconocido. "
                "Indique Inicial, Primario o Secundario, junto con la sala, "
                "grado o año cuando corresponda."
            ),
        )

    return _construir_rango(ciclo, grado, nivel)


def _validar_fecha_no_futura(fecha_nacimiento: date) -> None:
    if fecha_nacimiento > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de nacimiento no puede ser posterior a la fecha actual.",
        )


def _validar_edad(
    fecha_nacimiento: date | str | None,
    rango: RangoEdad,
    referencia: str,
    sujeto: str,
) -> int:
    try:
        fecha = parsear_fecha(fecha_nacimiento)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    _validar_fecha_no_futura(fecha)
    edad = edad_en_anio(fecha, date.today().year)

    if edad < rango.edad_minima or edad > rango.edad_maxima:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{sujeto} cumple {edad} años durante el ciclo lectivo y "
                f"«{referencia}» corresponde a estudiantes de "
                f"{rango.edad_minima} a {rango.edad_maxima} años. "
                "No se puede inscribir en un grado que no corresponde a su edad."
            ),
        )

    return edad


def validar_edad_para_curso(
    fecha_nacimiento: date | str | None,
    curso: Curso,
    nivel: NivelEducativo | None = None,
) -> int:
    """Valida que el alumno pueda cursar el curso indicado. Devuelve su edad."""
    rango = rango_edad_curso(curso, nivel)
    return _validar_edad(fecha_nacimiento, rango, curso.nombre, "El alumno")


def validar_edad_para_nivel(
    fecha_nacimiento: date | str | None, nivel: str
) -> int:
    """Valida la edad declarada contra el nivel/grado de una postulación."""
    rango = rango_edad_nivel(nivel)
    return _validar_edad(fecha_nacimiento, rango, nivel, "El postulante")
