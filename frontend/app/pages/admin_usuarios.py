import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def get_admin_usuarios_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de Usuarios, Control de Acceso RBAC y Permisos Familiares."""

    # ==================== 1. FILTROS Y ACCIÓN ====================
    search_input = ft.Container(
        width=280,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                ft.TextField(
                    hint_text="Buscar usuario, email o DNI...",
                    hint_style=ft.TextStyle(size=14, color=MUTED),
                    text_size=14,
                    color=TEXT_COLOR,
                    border=ft.InputBorder.NONE,
                    content_padding=ft.Padding(0, 0, 0, 10),
                    expand=True,
                ),
            ],
        ),
    )

    def filtro_dropdown(hint: str, width: int, opciones: list[str]) -> ft.Container:
        return ft.Container(
            width=width,
            height=CONTROL_HEIGHT,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            content=ft.Dropdown(
                hint_text=hint,
                hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
                text_size=14,
                border=ft.InputBorder.NONE,
                content_padding=ft.Padding(12, 0, 8, 12),
                options=[ft.dropdown.Option(opc) for opc in opciones],
            ),
        )

    btn_nuevo_usuario = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.PERSON_ADD_ALT_1_OUTLINED, size=16, color=BG_WHITE),
                ft.Text("Nuevo Usuario", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
        on_click=lambda _: None,
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    search_input,
                    filtro_dropdown("Rol: Todos", 150, ["Todos", "Administrador", "Docente", "Padre / Tutor", "Alumno"]),
                    filtro_dropdown("Estado: Activo", 140, ["Todos", "Activo", "Bloqueado", "Inactivo"]),
                ],
            ),
            btn_nuevo_usuario,
        ],
    )

    # ==================== 2. TABLA DE USUARIOS Y ROLES ====================
    usuarios_data = [
        {"usuario": "m.gomez", "email": "m.gomez@educar.edu.ar", "nombre": "M. Estela Gómez", "rol": "Administrador", "vinculacion": "Acceso Total", "ultimo_acceso": "Hoy, 10:45 hs", "estado": "Activo"},
        {"usuario": "r.martinez", "email": "r.martinez@educar.edu.ar", "nombre": "Román Alberto Martínez", "rol": "Docente", "vinculacion": "Legajo #20101", "ultimo_acceso": "Ayer, 18:30 hs", "estado": "Activo"},
        {"usuario": "martin.gomez", "email": "tutor.gomez@gmail.com", "nombre": "Martín Gómez", "rol": "Padre / Tutor", "vinculacion": "Hijo: Santiago (#10245)", "ultimo_acceso": "12/10/2026", "estado": "Activo"},
        {"usuario": "santiago.almiron", "email": "s.almiron@estudiantes.edu.ar", "nombre": "Santiago Almirón", "rol": "Alumno", "vinculacion": "Legajo #10245 (5to B)", "ultimo_acceso": "11/10/2026", "estado": "Activo"},
        {"usuario": "g.sanchez", "email": "g.sanchez@educar.edu.ar", "nombre": "Guillermina Sánchez", "rol": "Docente", "vinculacion": "Legajo #20102", "ultimo_acceso": "Hoy, 08:15 hs", "estado": "Activo"},
        {"usuario": "carla.morales", "email": "c.morales@tutor.com", "nombre": "Carla Morales", "rol": "Padre / Tutor", "vinculacion": "Hija: Valentina (#10248)", "ultimo_acceso": "10/10/2026", "estado": "Activo"},
    ]

    columnas_usuarios = [
        ("Usuario / Email", 220, False),
        ("Nombre Completo", 190, False),
        ("Rol Asignado", 140, False),
        ("Vinculación / Perfil", 200, False),
        ("Última Conexión", 140, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_usuarios)

    def rol_badge(rol: str) -> ft.Container:
        colores = {
            "Administrador": (TEAL_DARK, BG_WHITE),
            "Docente": (TEAL_LIGHT, TEAL_DARK),
            "Padre / Tutor": ("#FFF3E7", ORANGE),
            "Alumno": ("#EBFEE6", "#10B981"),
        }
        bg, color = colores.get(rol, (TEAL_LIGHT, TEAL_DARK))
        return ft.Container(
            padding=ft.Padding(8, 3, 8, 3),
            bgcolor=bg,
            border_radius=4,
            content=ft.Text(rol, size=11, weight=ft.FontWeight.BOLD, color=color),
        )

    def usuario_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=2,
                        width=220,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(item["usuario"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                            ft.Text(item["email"], size=11, color=MUTED),
                        ],
                    ),
                    ft.Container(width=190, content=ft.Text(item["nombre"], size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=140, content=rol_badge(item["rol"])),
                    ft.Container(width=200, content=ft.Text(item["vinculacion"], size=13, color=MUTED)),
                    ft.Container(width=140, content=ft.Text(item["ultimo_acceso"], size=12, color=MUTED)),
                    ft.Container(width=100, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.KEY_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Restablecer Contraseña", padding=0),
                                ft.IconButton(icon=ft.Icons.FAMILY_RESTROOM_OUTLINED, icon_size=16, icon_color=ORANGE, tooltip="Vincular Hijos/Alumnos", padding=0),
                                ft.IconButton(icon=ft.Icons.BLOCK_OUTLINED, icon_size=16, icon_color=BADGE_RED_TXT, tooltip="Bloquear Acceso", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[usuario_row(u) for u in usuarios_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-6 de 1,420 cuentas registradas",
        pagina_actual=1,
        total_paginas=237,
    )

    aviso_seguridad = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=18, color=TEAL),
                ft.Text(
                    "Seguridad y Privacidad: Cada rol accede únicamente a las secciones autorizadas. Los padres solo pueden consultar y gestionar información de sus propios hijos vinculados.",
                    size=13,
                    color=TEAL_DARK,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Control de Acceso, Usuarios y Permisos RBAC",
        active_route="/admin/usuarios",
        content_controls=[
            aviso_seguridad,
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )