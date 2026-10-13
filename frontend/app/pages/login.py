import flet as ft
import httpx
from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_PAGE_ALT as BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)


def get_login_view(page: ft.Page) -> list[ft.Control]:
    """Retorna la vista de inicio de sesión conectada a la API de autenticación."""

    # Feedback de errores
    error_banner = ft.Text(
        "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        text_align=ft.TextAlign.CENTER,
        visible=False,
    )

    btn_submit = ft.Button(
        "INGRESAR A LA PLATAFORMA",
        bgcolor=TEAL,
        color=BG_WHITE,
        height=41,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(
                size=14,
                weight=ft.FontWeight.W_600,
            ),
        ),
    )

    def redirigir_por_rol(rol: str):
        rol_upper = (rol or "").strip().upper()
        rutas_por_rol = {
            "ADMIN": "/admin/dashboard",
            "TEACHER": "/portal/docente/dashboard",
            "DOCENTE": "/portal/docente/dashboard",
            "PARENT": "/portal/padre/dashboard",
            "FAMILIA": "/portal/padre/dashboard",
            "STUDENT": "/portal/alumno/dashboard",
            "ALUMNO": "/portal/alumno/dashboard",
        }
        return rutas_por_rol.get(rol_upper, "/admin/dashboard")

    def on_submit(e):
        username = usuario_field.value.strip()
        password = password_field.value.strip()

        if not username or not password:
            error_banner.value = "Por favor, complete todos los campos obligatorios."
            error_banner.visible = True
            error_banner.update()
            return

        btn_submit.disabled = True
        btn_submit.text = "VERIFICANDO CREDENCIALES..."
        error_banner.visible = False
        page.update()

        try:
            data = api_client.login(username, password)
            token = data.get("access_token")
            rol = data.get("rol", "")
            user = data.get("username", username)

            # Persistencia de credenciales y perfil en el almacenamiento local del cliente
            if token:
                page.client_storage.set("auth_token", token)
                page.client_storage.set("auth_rol", rol)
                page.client_storage.set("auth_user", user)

            ruta_destino = redirigir_por_rol(rol)
            page.go(ruta_destino)

        except httpx.HTTPStatusError as err:
            btn_submit.disabled = False
            btn_submit.text = "INGRESAR A LA PLATAFORMA"
            if err.response.status_code == 401:
                error_banner.value = "Usuario o contraseña incorrectos."
            else:
                error_banner.value = f"Error del servidor ({err.response.status_code}). Intente nuevamente."
            error_banner.visible = True
            page.update()

        except httpx.RequestError:
            btn_submit.disabled = False
            btn_submit.text = "INGRESAR A LA PLATAFORMA"
            error_banner.value = "No se pudo conectar con el servidor backend en http://127.0.0.1:8000."
            error_banner.visible = True
            page.update()

    btn_submit.on_click = on_submit

    # Entradas del formulario
    usuario_field = ft.TextField(
        hint_text="ejemplo@educar.edu.ar o usuario",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_PAGE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=8,
        content_padding=ft.Padding(12, 12, 12, 12),
        height=41,
        on_submit=on_submit,
    )

    password_field = ft.TextField(
        hint_text="••••••••••••",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        password=True,
        can_reveal_password=True,
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_PAGE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=8,
        content_padding=ft.Padding(12, 12, 12, 12),
        height=41,
        on_submit=on_submit,
    )

    login_card = ft.Container(
        width=460,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=44,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=16,
            color=ft.Colors.with_opacity(0.04, "#000000"),
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            spacing=24,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Portal de Acceso",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Ingrese sus credenciales institucionales",
                            size=14,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
                error_banner,
                ft.Column(
                    spacing=18,
                    controls=[
                        ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text(
                                    "Usuario o Identificador",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_COLOR,
                                ),
                                usuario_field,
                            ],
                        ),
                        ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            "Contraseña",
                                            size=13,
                                            weight=ft.FontWeight.W_600,
                                            color=TEXT_COLOR,
                                        ),
                                        ft.TextButton(
                                            "¿Olvidó su clave?",
                                            style=ft.ButtonStyle(
                                                padding=0,
                                                color=ORANGE,
                                                overlay_color="transparent",
                                            ),
                                            on_click=lambda _: None,
                                        ),
                                    ],
                                ),
                                password_field,
                            ],
                        ),
                        btn_submit,
                    ],
                ),
                ft.Text(
                    "Centro Educativo Educar para Transformar · Resistencia",
                    size=12,
                    color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    main_section = ft.Container(
        bgcolor=BG_PAGE,
        alignment=ft.Alignment(0, 0),
        padding=ft.Padding.symmetric(horizontal=40, vertical=80),
        content=login_card,
    )

    return [main_section]