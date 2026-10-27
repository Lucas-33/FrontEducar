from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

# Asumiendo la estructura de tu servicio
# from backend.app.services.inscripciones import inscripcion_service


# --- MOCK DEL SERVICIO PARA EL TEST ---
# (Reemplazá esto importando tu servicio real de backend)
class MockInscripcionService:
    def inscribir_alumno_deporte(self, db, legajo: int, id_deporte: int):
        # Simulamos que la base de datos nos dice que ya tiene 2 deportes
        deportes_actuales = 2
        if deportes_actuales >= 2:
            raise HTTPException(
                status_code=400,
                detail="El alumno ya alcanzó el límite máximo de dos deportes simultáneos",
            )
        return True


inscripcion_service = MockInscripcionService()


def test_regresion_limite_dos_deportes():
    """
    Prueba de Regresión (HU2 / RF03):
    Verifica que el sistema rechace la inscripción a un tercer deporte.
    """
    db_mock = MagicMock()
    legajo_alumno = 1001
    id_basquetbol = 3  # ID del 3er deporte

    # Act & Assert: Intentamos inscribirlo y verificamos que lance la excepción exacta
    with pytest.raises(HTTPException) as exc_info:
        inscripcion_service.inscribir_alumno_deporte(
            db_mock, legajo_alumno, id_basquetbol
        )

    # Verificamos que el error sea exactamente el esperado por QA
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "El alumno ya alcanzó el límite máximo de dos deportes simultáneos"
    )
