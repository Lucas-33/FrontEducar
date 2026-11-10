"""Tests unitarios de las reglas de edad para la matriculación."""

from datetime import date, timedelta

import pytest
from fastapi import HTTPException

from backend.app.core.fechas import parsear_fecha
from backend.app.core.reglas_academicas import (
    rango_edad_curso,
    rango_edad_nivel,
    validar_edad_para_curso,
    validar_edad_para_nivel,
)
from backend.app.models.academico import Curso, NivelEducativo


def _curso(nombre: str, id_nivel: int = 1) -> Curso:
    return Curso(id_curso=1, nombre=nombre, id_nivel=id_nivel)


def _nivel(nombre: str) -> NivelEducativo:
    return NivelEducativo(id_nivel=1, nombre=nombre)


def _fecha_con_edad(edad: int) -> date:
    """Fecha de nacimiento que cumple ``edad`` en el ciclo lectivo actual."""
    return date(date.today().year - edad, 1, 1)


def test_parsear_fecha_acepta_formatos_habituales():
    assert parsear_fecha("2020-05-10") == date(2020, 5, 10)
    assert parsear_fecha("10/05/2020") == date(2020, 5, 10)
    assert parsear_fecha(date(2020, 5, 10)) == date(2020, 5, 10)


def test_parsear_fecha_rechaza_valores_invalidos():
    with pytest.raises(ValueError):
        parsear_fecha("31/02/2020")
    with pytest.raises(ValueError):
        parsear_fecha(None)


@pytest.mark.parametrize(
    ("nombre_curso", "rango_esperado"),
    [
        ("Sala de 3", (3, 4)),
        ("Sala de 4", (4, 5)),
        ("1° Grado A", (6, 7)),
        ("6to Grado B", (11, 12)),
        ("1° Año A", (12, 13)),
        ("5° Año B", (16, 17)),
    ],
)
def test_rango_edad_por_curso(nombre_curso, rango_esperado):
    rango = rango_edad_curso(_curso(nombre_curso), _nivel("Nivel genérico"))
    assert (rango.edad_minima, rango.edad_maxima) == rango_esperado


def test_curso_sin_grado_usa_el_nivel_como_respaldo():
    rango = rango_edad_curso(_curso("Curso Azul"), _nivel("Primario"))
    assert rango.edad_minima == 6
    assert rango.edad_maxima == 13


def test_curso_sin_nivel_reconocible_no_permite_matricular():
    with pytest.raises(HTTPException) as exc_info:
        rango_edad_curso(_curso("Curso Azul"), _nivel("Nivel genérico"))
    assert exc_info.value.status_code == 400


@pytest.mark.parametrize(
    ("nivel", "rango_esperado"),
    [
        ("Inicial (Jardín)", (3, 6)),
        ("Inicial - Sala de 4", (4, 5)),
        ("Primario", (6, 13)),
        ("Secundario - 5° Año", (16, 17)),
    ],
)
def test_rango_edad_por_nivel_postulado(nivel, rango_esperado):
    rango = rango_edad_nivel(nivel)
    assert (rango.edad_minima, rango.edad_maxima) == rango_esperado


def test_validar_edad_para_curso_acepta_edad_correspondiente():
    curso = _curso("1° Grado A")
    edad = validar_edad_para_curso(_fecha_con_edad(6), curso, _nivel("Primario"))
    assert edad == 6


def test_validar_edad_para_curso_rechaza_alumno_mayor():
    curso = _curso("1° Grado A")
    with pytest.raises(HTTPException) as exc_info:
        validar_edad_para_curso(_fecha_con_edad(20), curso, _nivel("Primario"))
    assert exc_info.value.status_code == 400
    assert "no corresponde a su edad" in exc_info.value.detail


def test_validar_edad_para_curso_rechaza_alumno_menor():
    curso = _curso("5° Año B")
    with pytest.raises(HTTPException) as exc_info:
        validar_edad_para_curso(_fecha_con_edad(5), curso, _nivel("Secundario"))
    assert exc_info.value.status_code == 400


def test_validar_edad_rechaza_fecha_futura():
    curso = _curso("1° Grado A")
    with pytest.raises(HTTPException) as exc_info:
        validar_edad_para_curso(
            date.today() + timedelta(days=1), curso, _nivel("Primario")
        )
    assert exc_info.value.status_code == 400
    assert "posterior a la fecha actual" in exc_info.value.detail


def test_validar_edad_para_nivel_rechaza_postulante_mayor():
    with pytest.raises(HTTPException) as exc_info:
        validar_edad_para_nivel(_fecha_con_edad(30), "Inicial - Sala de 4")
    assert exc_info.value.status_code == 400
    assert "no corresponde a su edad" in exc_info.value.detail


def test_validar_edad_para_nivel_rechaza_nivel_desconocido():
    with pytest.raises(HTTPException) as exc_info:
        validar_edad_para_nivel(_fecha_con_edad(4), "Nivel inexistente")
    assert exc_info.value.status_code == 400
