import flet as ft

from mobile.api_client import mobile_api
from mobile.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
    RED_STATE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def get_perfil_page(page: ft.Page, on_cerrar_sesion) -> list[ft.Control]:
    """Pantalla móvil de Perfil del Usuario, Cambio de Contraseña y Cierre de Sesión."""

    usuario = getattr(page, "auth_user", "Usuario")
    rol = getattr(page, "auth_rol", "PARENT")
    iniciales = (usuario[:2] if usuario else "US").upper()

    # Formulario de cambio de contraseña
    pass_actual = ft.TextField(
        label="Contraseña actual",
        password=True,
        can_reveal_password=True,
        height=CONTROL_HEIGHT,
        text_size=13,
        border_radius=BORDER_RADIUS,
    )
    pass_nueva = ft.TextField(
        label="Nueva contraseña (mínimo 6 caracteres)",
        password=True,
        can_reveal_password=True,
        height=CONTROL_HEIGHT,
        text_size=13,
        border_radius=BORDER_RADIUS,
    )

    btn_guardar_pass = ft.Button(
        "Cambiar Contraseña",
        icon=ft.Icons.LOCK_RESET,
        bgcolor=TEAL,
        color=BG_WHITE,
        height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
    )

    async def cambiar_clave_click(_):
        act = (pass_actual.value or "").strip()
        nue = (pass_nueva.value or "").strip()

        if not act or not nue:
            snack = ft.SnackBar(
                ft.Text("Complete ambos campos de contraseña."), bgcolor=BADGE_RED_TXT
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return

        try:
            btn_guardar_pass.disabled = True
            page.update()

            await mobile_api.cambiar_password(act, nue)
            pass_actual.value = ""
            pass_nueva.value = ""

            snack = ft.SnackBar(
                ft.Text("¡Contraseña actualizada correctamente!"), bgcolor=ONLINE_GREEN
            )
            page.overlay.append(snack)
            snack.open = True

        except Exception as ex:
            snack = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=BADGE_RED_TXT)
            page.overlay.append(snack)
            snack.open = True
        finally:
            btn_guardar_pass.disabled = False
            page.update()

    btn_guardar_pass.on_click = cambiar_clave_click

    tarjeta_perfil = ft.Container(
        bgcolor=BG_WHITE,
        padding=20,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, BORDER_COLOR),
        content=ft.Row(
            spacing=14,
            controls=[
                ft.Container(
                    width=54,
                    height=54,
                    bgcolor=TEAL_DARK,
                    border_radius=27,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        iniciales, size=20, weight=ft.FontWeight.BOLD, color="white"
                    ),
                ),
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            usuario,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_COLOR,
                        ),
                        ft.Text(
                            "Tutor Responsable / Familia"
                            if rol in ["PARENT", "FAMILIA"]
                            else f"Rol: {rol}",
                            size=12,
                            color=MUTED,
                        ),
                        ft.Text(
                            f"Servidor: {mobile_api.base_url}", size=10, color=MUTED
                        ),
                    ],
                ),
            ],
        ),
    )

    tarjeta_seguridad = ft.Container(
        bgcolor=BG_WHITE,
        padding=18,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, BORDER_COLOR),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    "Seguridad de la Cuenta",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Text(
                    "Actualizá tu clave de acceso institucional:", size=11, color=MUTED
                ),
                pass_actual,
                pass_nueva,
                btn_guardar_pass,
            ],
        ),
    )

    btn_logout = ft.Button(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.LOGOUT, size=18, color=RED_STATE),
                ft.Text(
                    "Cerrar Sesión", size=14, weight=ft.FontWeight.BOLD, color=RED_STATE
                ),
            ],
        ),
        bgcolor=BG_WHITE,
        height=46,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            side=ft.BorderSide(1, RED_STATE),
        ),
        on_click=lambda _: on_cerrar_sesion(),
    )

    return [
        ft.Text("Mi Perfil", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
        tarjeta_perfil,
        tarjeta_seguridad,
        btn_logout,
    ]
