import flet as ft

# Paleta y tokens visuales del CSS
BG_WHITE = "#FFFFFF"
BG_SEARCH = "#F5F7F7"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"


def create_topbar(
    page: ft.Page,
    titulo: str = "Tablero Principal de Control",
    usuario_nombre: str = "M. Estela Gómez",
    usuario_rol: str = "Supervisora General",
    avatar_url: str = "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=100&h=100&fit=crop",
    on_search=None,
    on_help=None,
    on_notifications=None,
) -> ft.Container:
    """Genera la barra superior (TopBar) del panel interno de control Educar SGE."""

    # 1. Buscador estilo píldora (195px x 26px aprox)
    search_input = ft.TextField(
        hint_text="Buscar legajo, DNI o curso...",
        hint_style=ft.TextStyle(size=12, color=MUTED),
        text_size=12,
        color=TEXT_COLOR,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 8),
        expand=True,
        on_submit=on_search,
    )

    search_bar = ft.Container(
        width=195,
        height=32,
        bgcolor=BG_SEARCH,
        border_radius=100,
        padding=ft.Padding(12, 4, 12, 4),
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=14, color=MUTED),
                search_input,
            ],
        ),
    )

    # 2. Botón circular de ayuda (36x36px, fondo #E6F2F2)
    help_button = ft.Container(
        width=36,
        height=36,
        bgcolor=TEAL_LIGHT,
        border_radius=18,
        alignment=ft.Alignment(0, 0),
        tooltip="Centro de Ayuda",
        on_click=on_help,
        content=ft.Icon(ft.Icons.HELP_OUTLINE, size=18, color=TEAL),
    )

    # 3. Botón circular de notificaciones (36x36px, fondo #E6F2F2)
    notifications_button = ft.Container(
        width=36,
        height=36,
        bgcolor=TEAL_LIGHT,
        border_radius=18,
        alignment=ft.Alignment(0, 0),
        tooltip="Notificaciones",
        on_click=on_notifications,
        content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE_OUTLINED, size=18, color=TEAL),
    )

    # 4. Sección de Usuario (Avatar 36x36px + Nombre y Cargo)
    user_avatar = ft.Container(
        width=36,
        height=36,
        border_radius=18,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Image(
            src=avatar_url,
            fit="cover",
            width=36,
            height=36,
        ),
    )

    user_info = ft.Column(
        spacing=1,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Text(
                usuario_nombre,
                size=13,
                weight=ft.FontWeight.W_600,
                color=TEXT_COLOR,
            ),
            ft.Text(
                usuario_rol,
                size=10,
                weight=ft.FontWeight.W_400,
                color=MUTED,
            ),
        ],
    )

    user_section = ft.Row(
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[user_avatar, user_info],
    )

    # Contenedor derecho agrupado (gap: 16px)
    acciones_derecha = ft.Row(
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_bar,
            help_button,
            notifications_button,
            user_section,
        ],
    )

    # Barra principal (alto: 70px, padding horizontal: 32px)
    return ft.Container(
        height=70,
        bgcolor=BG_WHITE,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding.symmetric(horizontal=32),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    titulo,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                acciones_derecha,
            ],
        ),
    )