import flet as ft
from frontend.app.components.constants import (
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
    """Retorna el contenedor principal de la vista de inicio de sesión."""

    # Estado del rol seleccionado (por defecto Familias)
    rol_seleccionado = {"valor": "Familias"}

    roles = ["Alumnos", "Familias", "Docentes", "Admin"]
    botones_roles: dict[str, ft.Container] = {}

    def seleccionar_rol(e):
        nuevo_rol = e.control.data
        rol_seleccionado["valor"] = nuevo_rol

        for rol, container in botones_roles.items():
            activo = rol == nuevo_rol
            container.bgcolor = BG_WHITE if activo else "transparent"
            container.shadow = (
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.06, "#000000"),
                    offset=ft.Offset(0, 1),
                )
                if activo
                else None
            )
            container.content.color = TEAL_DARK if activo else MUTED
            container.content.weight = (
                ft.FontWeight.W_600 if activo else ft.FontWeight.W_500
            )

        selector_roles.update()

    # Selector de roles segmentado
    tabs_controls = []
    for rol in roles:
        activo = rol == rol_seleccionado["valor"]
        btn_rol = ft.Container(
            data=rol,
            expand=True,
            height=32,
            bgcolor=BG_WHITE if activo else "transparent",
            border_radius=6,
            alignment=ft.Alignment(0, 0),
            shadow=(
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.06, "#000000"),
                    offset=ft.Offset(0, 1),
                )
                if activo
                else None
            ),
            on_click=seleccionar_rol,
            content=ft.Text(
                rol,
                size=13,
                weight=ft.FontWeight.W_600 if activo else ft.FontWeight.W_500,
                color=TEAL_DARK if activo else MUTED,
            ),
        )
        botones_roles[rol] = btn_rol
        tabs_controls.append(btn_rol)

    selector_roles = ft.Container(
        width=384,
        height=40,
        bgcolor=BG_PAGE,
        border_radius=8,
        padding=4,
        content=ft.Row(
            spacing=4,
            controls=tabs_controls,
        ),
    )

    def on_submit(e):
        rol = rol_seleccionado["valor"]

        # Redirección dinámica basada en el rol seleccionado
        rutas_por_rol = {
            "Admin": "/admin/dashboard",
            "Familias": "/portal/padre/dashboard",
            "Docentes": "/portal/docente/dashboard",
            "Alumnos": "/portal/alumno/dashboard",
        }

        destino = rutas_por_rol.get(rol, "/admin/dashboard")
        page.go(destino)

    # Entradas del formulario
    usuario_field = ft.TextField(
        hint_text="ejemplo@educar.edu.ar",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_PAGE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=8,
        content_padding=ft.Padding(12, 12, 12, 12),
        height=41,
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

    # Tarjeta de inicio de sesión
    login_card = ft.Container(
        width=480,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=48,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=16,
            color=ft.Colors.with_opacity(0.03, "#000000"),
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            spacing=32,
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
                            "Seleccione su rol para ingresar a la plataforma",
                            size=14,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
                selector_roles,
                ft.Column(
                    spacing=20,
                    controls=[
                        ft.Column(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    "Usuario o Email",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_COLOR,
                                ),
                                usuario_field,
                            ],
                        ),
                        ft.Column(
                            spacing=8,
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
                                            on_click=lambda _: page.go("/recuperar-clave"),
                                        ),
                                    ],
                                ),
                                password_field,
                            ],
                        ),
                        ft.Button(
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
                            on_click=on_submit,
                        ),
                    ],
                ),
                ft.Text(
                    "¿No tiene usuario asignado? Diríjase a Secretaría para solicitar su alta institucional.",
                    size=13,
                    color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    main_section = ft.Container(
        bgcolor=BG_PAGE,
        alignment=ft.Alignment(0, 0),
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=login_card,
    )

    return [main_section]