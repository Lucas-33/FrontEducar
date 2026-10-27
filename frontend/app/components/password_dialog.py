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

    # El token en memoria puede haberse perdido si el backend se reinició.
    token = getattr(page, "auth_token", None)
    if token and api_client.token != token:
        api_client.set_token(token)

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

    btn_guardar = ft.Button("Guardar", bgcolor=TEAL, color="white")

    async def guardar(e):
        mensaje.value = ""
        password_actual = (actual.value or "").strip()
        password_nueva = (nueva.value or "").strip()
        password_repetida = (repetir.value or "").strip()

        if not password_actual or not password_nueva or not password_repetida:
            mensaje.value = "Complete todos los campos para continuar."
            page.update()
            return
        if len(password_nueva) < 6:
            mensaje.value = "La nueva contraseña debe tener al menos 6 caracteres."
            page.update()
            return
        if password_nueva != password_repetida:
            mensaje.value = "Las contraseñas nuevas no coinciden."
            page.update()
            return

        btn_guardar.disabled = True
        btn_guardar.text = "Guardando..."
        page.update()

        try:
            await api_client.cambiar_password(password_actual, password_nueva)
        except httpx.HTTPStatusError as error:
            detalle = "No se pudo cambiar la contraseña."
            try:
                detalle = error.response.json().get("detail", detalle)
            except Exception:
                pass
            mensaje.value = detalle
            btn_guardar.disabled = False
            btn_guardar.text = "Guardar"
            page.update()
            return
        except Exception:
            mensaje.value = "No se pudo conectar con el servidor."
            btn_guardar.disabled = False
            btn_guardar.text = "Guardar"
            page.update()
            return

        page.pop_dialog()
        page.show_dialog(
            ft.SnackBar(
                ft.Text(
                    "Contraseña actualizada correctamente. "
                    "Use la nueva clave en su próximo inicio de sesión.",
                    color="white",
                ),
                bgcolor=TEAL,
            )
        )

    btn_guardar.on_click = guardar

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
            btn_guardar,
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialog)
