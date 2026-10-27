import pytest
import flet as ft
from unittest.mock import AsyncMock, patch


# --- MOCK DE LA VISTA DE FLET ---
# Aquí simulamos cómo se comporta tu botón de inscribir y el texto de error
async def componente_inscripcion_mock(api_client_mock):
    # Componentes visuales
    feedback_text = ft.Text("", visible=False)

    async def btn_inscribir_click(e):
        try:
            # Intenta llamar a la API
            await api_client_mock.inscribir_deporte(legajo=1001, id_deporte=3)
        except Exception as err:
            # Captura el error de la API y lo muestra en la UI
            feedback_text.value = str(err)
            feedback_text.visible = True

    btn_inscribir = ft.Button("Inscribir", on_click=btn_inscribir_click)

    return btn_inscribir, feedback_text


@pytest.mark.asyncio
async def test_ui_rechazo_tercer_deporte():
    """
    Prueba Dinámica Flet (HU2 / RF03):
    Simula el clic del usuario y verifica que el texto de error se renderice en pantalla.
    """
    # 1. Preparamos el mock de la API para que devuelva el error del límite
    api_client_mock = AsyncMock()
    error_esperado = "El alumno ya alcanzó el límite máximo de dos deportes simultáneos"
    api_client_mock.inscribir_deporte.side_effect = Exception(error_esperado)

    # 2. Renderizamos los controles de Flet virtualmente
    btn_inscribir, feedback_text = await componente_inscripcion_mock(api_client_mock)

    # 3. Simulamos la acción del usuario (clic en el botón de Básquetbol)
    # Le pasamos None porque en el test no necesitamos el evento real del mouse
    await btn_inscribir.on_click(None)

    # 4. Verificación (Assert): Comprobamos que el texto de error cambió y se hizo visible
    assert feedback_text.visible is True
    assert feedback_text.value == error_esperado
