"""Diálogo reutilizable para que el usuario autenticado cambie su contraseña."""

import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    TEAL,
    TEAL_DARK,
)


def abrir_cambio_password(page: ft.Page):
    """Abre el diálogo modal de cambio de contraseña del usuario autenticado."""

    actual = ft.TextField(
        label="Contraseña actual",
        password=True,
        can_reveal_password=True,
        width=340,
        border_color=BORDER_COLOR,
    )
    nueva = ft.TextField(
        label="Nueva contraseña (mínimo 6 caracteres)",
        password=True,
        can_reveal_password=True,
        width=340,
        border_color=BORDER_COLOR,
    )
    repetir = ft.TextField(
        label="Repetir nueva contraseña",
        password=True,
        can_reveal_password=True,
        width=340,
        border_color=BORDER_COLOR,
    )
    mensaje = ft.Text("", size=12, color="#EF4444")

    async def guardar(e):
        mensaje.value = ""
        if not actual.value or not nueva.value or not repetir.value:
            mensaje.value = "Complete todos los campos para continuar."
            page.update()
            return
        if nueva.value != repetir.value:
            mensaje.value = "Las contraseñas nuevas no coinciden."
            page.update()
            return

        try:
            await api_client.cambiar_password(actual.value, nueva.value)
        except httpx.HTTPStatusError as error:
            detalle = "No se pudo cambiar la contraseña."
            try:
                detalle = error.response.json().get("detail", detalle)
            except Exception:
                pass
            mensaje.value = detalle
            page.update()
            return
        except Exception:
            mensaje.value = "No se pudo conectar con el servidor."
            page.update()
            return

        page.pop_dialog()
        aviso = ft.SnackBar(
            ft.Text("Contraseña actualizada correctamente.", color="white"),
            bgcolor=TEAL,
        )
        page.show_dialog(aviso)

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=BG_WHITE,
        title=ft.Text(
            "Cambiar mi contraseña", size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK
        ),
        content=ft.Column(
            spacing=14,
            width=360,
            tight=True,
            controls=[
                ft.Text(
                    "La nueva contraseña debe tener al menos 6 caracteres.",
                    size=12,
                    color=MUTED,
                ),
                actual,
                nueva,
                repetir,
                mensaje,
            ],
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
            ft.Button("Guardar", bgcolor=TEAL, color="white", on_click=guardar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialog)
