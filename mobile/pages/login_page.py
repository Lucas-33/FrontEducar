import flet as ft
import httpx

from mobile.api_client import mobile_api
from mobile.components.constants import (
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def get_login_page(page: ft.Page, on_login_success) -> ft.Container:
    """Pantalla de inicio de sesión 100% móvil."""

    error_banner = ft.Container(
        visible=False,
        bgcolor="#FEE2E2",
        padding=10,
        border_radius=8,
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=BADGE_RED_TXT, size=18),
                ft.Text(
                    "",
                    size=12,
                    weight=ft.FontWeight.W_500,
                    color=BADGE_RED_TXT,
                    expand=True,
                ),
            ],
        ),
    )

    error_text = error_banner.content.controls[1]

    usuario_field = ft.TextField(
        label="Usuario institucional",
        hint_text="Ej: rmartinez o aperez",
        value="rmartinez",
        height=CONTROL_HEIGHT,
        text_size=14,
        border_radius=BORDER_RADIUS,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
    )

    password_field = ft.TextField(
        label="Contraseña",
        hint_text="••••••••••••",
        value="password123",
        password=True,
        can_reveal_password=True,
        height=CONTROL_HEIGHT,
        text_size=14,
        border_radius=BORDER_RADIUS,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )

    btn_ingresar = ft.Button(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.LOGIN_ROUNDED, size=18, color=BG_WHITE),
                ft.Text(
                    "INGRESAR A LA APP",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=BG_WHITE,
                ),
            ],
        ),
        bgcolor=TEAL,
        height=48,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
        ),
    )

    # Configuración de IP para pruebas en dispositivo móvil físico
    ip_field = ft.TextField(
        label="URL o IP del Servidor API",
        value=mobile_api.base_url,
        text_size=12,
        height=38,
        border_radius=BORDER_RADIUS,
    )

    def guardar_ip_servidor(_):
        if ip_field.value:
            mobile_api.set_base_url(ip_field.value)
            dialogo_config.open = False
            snack = ft.SnackBar(
                ft.Text(f"Servidor configurado: {mobile_api.base_url}"),
                bgcolor=TEAL,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()

    dialogo_config = ft.AlertDialog(
        shape=ft.RoundedRectangleBorder(radius=CARD_RADIUS),
        title=ft.Text("Configurar Servidor", size=16, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True,
            spacing=10,
            controls=[
                ft.Text(
                    "Si probás desde un celular físico por WiFi, colocá la IP de tu PC (ej: http://192.168.1.15:8000/api/v1):",
                    size=12,
                    color=MUTED,
                ),
                ip_field,
            ],
        ),
        actions=[
            ft.TextButton(
                "Cancelar",
                on_click=lambda _: setattr(dialogo_config, "open", False)
                or page.update(),
            ),
            ft.Button(
                "Guardar", bgcolor=TEAL, color="white", on_click=guardar_ip_servidor
            ),
        ],
    )

    def abrir_config_servidor(_):
        if dialogo_config not in page.overlay:
            page.overlay.append(dialogo_config)
        dialogo_config.open = True
        page.update()

    async def on_submit_login(_):
        username = (usuario_field.value or "").strip()
        password = (password_field.value or "").strip()

        if not username or not password:
            error_text.value = "Complete su usuario y contraseña."
            error_banner.visible = True
            page.update()
            return

        btn_ingresar.disabled = True
        error_banner.visible = False
        page.update()

        try:
            data = await mobile_api.login(username, password)
            token = data.get("access_token")
            rol = (data.get("rol") or "").upper()
            user = data.get("username", username)

            if token:
                page.auth_token = token
                page.auth_rol = rol
                page.auth_user = user

                # Obtener el perfil completo para saber el id_padre o legajo
                perfil = await mobile_api.get_mi_perfil()
                page.auth_padre_id = perfil.get("id_padre")
                page.auth_legajo_alumno = perfil.get("legajo_alumno")

                on_login_success()

        except httpx.HTTPStatusError as err:
            btn_ingresar.disabled = False
            if err.response.status_code == 401:
                error_text.value = "Usuario o contraseña incorrectos."
            else:
                error_text.value = f"Error del servidor ({err.response.status_code})."
            error_banner.visible = True
            page.update()

        except httpx.RequestError as ex:
            btn_ingresar.disabled = False
            error_text.value = f"No se pudo conectar a {mobile_api.base_url}. Verifique que el backend esté activo y configure la IP."
            error_banner.visible = True
            page.update()

    btn_ingresar.on_click = on_submit_login
    usuario_field.on_submit = on_submit_login
    password_field.on_submit = on_submit_login

    return ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        alignment=ft.Alignment(0, 0),
        padding=24,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Container(
                    width=68,
                    height=68,
                    bgcolor=TEAL_LIGHT,
                    border_radius=34,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=TEAL_DARK, size=36),
                ),
                ft.Column(
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Educar Móvil",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.Text(
                            "Portal de Familias y Estudiantes",
                            size=13,
                            color=MUTED,
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=BG_WHITE,
                    padding=24,
                    border_radius=CARD_RADIUS,
                    border=ft.Border.all(1, BORDER_COLOR),
                    content=ft.Column(
                        spacing=14,
                        controls=[
                            error_banner,
                            usuario_field,
                            password_field,
                            btn_ingresar,
                        ],
                    ),
                ),
                ft.TextButton(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.SETTINGS_ETHERNET, size=14, color=MUTED),
                            ft.Text("Configurar IP de Conexión", size=12, color=MUTED),
                        ],
                    ),
                    on_click=abrir_config_servidor,
                ),
            ],
        ),
    )
