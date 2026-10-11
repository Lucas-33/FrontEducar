import flet as ft
from app.ui.components.sidebar import create_sidebar
from app.ui.components.topbar import create_topbar

# Paleta cromática y tokens visuales del sistema
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
BADGE_WARN_BG = "#FFF3E7"
BADGE_WARN_TXT = "#A94C16"


def get_admin_usuarios_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Gestión de Usuarios, Roles y Permisos de Acceso."""

    # ==================== 1. ENCABEZADO Y ACCIÓN PRINCIPAL ====================
    encabezado_modulo = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Seguridad, Roles y Control de Accesos al Sistema",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Usuarios, Permisos y Credenciales",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Gestione los niveles de acceso de directivos, docentes, preceptores, personal administrativo y cuentas del Portal de Familias.",
                        size=14,
                        color=MUTED,
                    ),
                ],
            ),
            ft.Button(
                content=ft.Row(
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                        ft.Text("Nuevo Usuario", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                    ],
                ),
                bgcolor=TEAL,
                height=41,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(16, 11, 16, 11),
                ),
                on_click=lambda _: None,
            ),
        ],
    )

    # ==================== 2. BÚSQUEDA Y FILTROS ====================
    search_bar = ft.Container(
        height=43,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=8,
        padding=ft.Padding(12, 0, 12, 0),
        expand=True,
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                ft.TextField(
                    hint_text="Buscar usuario por nombre, correo electrónico o rol asignado...",
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

    def filtro_desplegable(texto: str, ancho: int) -> ft.Container:
        return ft.Container(
            width=ancho,
            height=43,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=8,
            padding=ft.Padding(12, 0, 12, 0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(texto, size=14, color=TEXT_COLOR),
                    ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=14, color=MUTED),
                ],
            ),
        )

    filtros_fila = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_bar,
            filtro_desplegable("Rol: Todos", 111),
            filtro_desplegable("Estado: Activo", 135),
        ],
    )

    # ==================== 3. TABLA DE REGISTROS DE USUARIOS ====================
    cabecera_tabla_usuarios = ft.Container(
        height=42,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 13, 16, 13),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=451, expand=True, content=ft.Text("Usuario e Identidad", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=135, content=ft.Text("Rol del Sistema", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=275, content=ft.Text("Último Acceso Registrado", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=100, content=ft.Text("Estado", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=75, content=ft.Text("Acciones", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    usuarios_data = [
        {"nombre": "Gómez, María Estela", "email": "m.gomez@educar.edu.ar", "rol": "Super Administrador", "acceso": "Hoy, 09:42 hs (Sesión actual)", "estado": "Activo", "seleccionado": False},
        {"nombre": "Sánchez, Guillermina", "email": "g.sanchez@educar.edu.ar", "rol": "Cuerpo Docente", "acceso": "Ayer, 18:30 hs", "estado": "Activo", "seleccionado": False},
        {"nombre": "Martínez, Román Alberto", "email": "r.martinez@educar.edu.ar", "rol": "Cuerpo Docente", "acceso": "Ayer, 14:15 hs", "estado": "Activo", "seleccionado": False},
        {"nombre": "Benítez, Roberto", "email": "r.benitez@educar.edu.ar", "rol": "Preceptor / Tutor", "acceso": "Hoy, 07:45 hs", "estado": "Activo", "seleccionado": True},
        {"nombre": "Almirón, Carlos Alberto", "email": "c.almiron@tutor.com", "rol": "Familias / Tutores", "acceso": "10/10/2026 09:14 hs", "estado": "Activo", "seleccionado": False},
        {"nombre": "Capra, Jorge Andrés", "email": "j.capra@educar.edu.ar", "rol": "Cuerpo Docente", "acceso": "Pendiente de primer ingreso", "estado": "Pendiente", "seleccionado": False},
    ]

    def usuario_row(item: dict) -> ft.Container:
        es_activo = item["estado"] == "Activo"
        badge_bg = TEAL_LIGHT if es_activo else BADGE_WARN_BG
        badge_txt = TEAL if es_activo else BADGE_WARN_TXT

        return ft.Container(
            height=64,
            bgcolor=TEAL_LIGHT if item["seleccionado"] else BG_WHITE,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 14, 16, 14),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=3,
                        width=451,
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(item["nombre"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                            ft.Text(item["email"], size=11, color=MUTED),
                        ],
                    ),
                    ft.Container(
                        width=135,
                        content=ft.Text(item["rol"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=275,
                        content=ft.Text(item["acceso"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    padding=ft.Padding(8, 4, 8, 4),
                                    bgcolor=badge_bg,
                                    border_radius=4,
                                    content=ft.Text(item["estado"], size=12, weight=ft.FontWeight.W_600, color=badge_txt),
                                ),
                            ]
                        ),
                    ),
                    ft.Container(
                        width=75,
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE_RED_EYE_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Ver detalle",
                                    padding=0,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_NOTE_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Modificar permisos",
                                    padding=0,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    tabla_usuarios_contenedor = ft.Container(
        height=426,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                cabecera_tabla_usuarios,
                *[usuario_row(u) for u in usuarios_data],
            ],
        ),
    )

    nota_tabla_usuarios = ft.Text(
        "Haga clic en una cuenta para auditar el historial de accesos, bloquear credenciales o reasignar roles de seguridad.",
        size=12,
        color=MUTED,
    )

    # ==================== 4. MATRIZ DE PERMISOS POR ROL ====================
    encabezado_roles = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Matriz de Permisos por Rol", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
            ft.Container(
                height=41,
                bgcolor=BG_WHITE,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=8,
                padding=ft.Padding(16, 11, 16, 11),
                content=ft.Text("Modificar Roles", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                on_click=lambda _: None,
            ),
        ],
    )

    cabecera_tabla_roles = ft.Container(
        height=42,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 13, 16, 13),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=145, content=ft.Text("Rol", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=326.5, expand=True, content=ft.Text("Módulos Habilitados", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=326.5, expand=True, content=ft.Text("Permisos de Edición", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=250, content=ft.Text("Alcance Geográfico / Sede", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    roles_data = [
        {"rol": "Super Administrador", "modulos": "Acceso total a todos los módulos y ajustes", "edicion": "Crear, editar, eliminar y auditar registros", "alcance": "Todas las sedes y niveles"},
        {"rol": "Equipo Directivo", "modulos": "Alumnos, Cursos, Materias, Horarios y Reportes", "edicion": "Validar inscripciones y aprobar calificaciones", "alcance": "Nivel asignado (Inicial / Primario / Sec)"},
        {"rol": "Cuerpo Docente", "modulos": "Calificaciones, Asistencia y Horarios de cátedra", "edicion": "Cargar notas, partes de clase y observaciones", "alcance": "Cursos y materias a cargo"},
        {"rol": "Familias / Tutores", "modulos": "Portal de Familias, Boletín, Comedor y Transporte", "edicion": "Consulta de legajo y solicitud de trámites", "alcance": "Exclusivo hijos vinculados"},
    ]

    def rol_row(item: dict) -> ft.Container:
        return ft.Container(
            height=62,
            bgcolor=BG_WHITE,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 14, 16, 14),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=145, content=ft.Text(item["rol"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=326.5, expand=True, content=ft.Text(item["modulos"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=326.5, expand=True, content=ft.Text(item["edicion"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=250, content=ft.Text(item["alcance"], size=13, color=TEXT_COLOR)),
                ],
            ),
        )

    tabla_roles_contenedor = ft.Container(
        height=290,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                cabecera_tabla_roles,
                *[rol_row(r) for r in roles_data],
            ],
        ),
    )

    seccion_permisos_rol = ft.Column(
        spacing=12,
        controls=[
            encabezado_roles,
            tabla_roles_contenedor,
        ],
    )

    # ==================== 5. ASOCIACIÓN FAMILIAR Y PRIVACIDAD ====================
    def tarjeta_hijo_vinculado(nombre: str, curso: str) -> ft.Container:
        return ft.Container(
            expand=True,
            height=98,
            bgcolor=BG_PAGE,
            border_radius=8,
            padding=14,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(nombre, size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    ft.Text(curso, size=12, color=MUTED),
                    ft.Container(
                        padding=ft.Padding(8, 4, 8, 4),
                        bgcolor=TEAL_LIGHT,
                        border_radius=4,
                        content=ft.Text("Acceso a boletín y pagos habilitado", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                    ),
                ],
            ),
        )

    panel_asociacion_familiar = ft.Container(
        width=776,
        height=258,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Vinculación de Tutor / Familia — Carlos Alberto Almirón", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Cuenta con permisos activos para consultar legajos académicos, solicitar comedor y autorizar salidas.",
                            size=13,
                            color=TEXT_COLOR,
                            expand=True,
                        ),
                        ft.Container(
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=TEAL_LIGHT,
                            border_radius=4,
                            content=ft.Text("2 Hijos vinculados", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        tarjeta_hijo_vinculado("Santiago Almirón", "5to Año B · Secundario — Legajo #10245"),
                        tarjeta_hijo_vinculado("Valentina Almirón", "2do Grado A · Primario — Legajo #11082"),
                    ],
                ),
                ft.Text(
                    "Las modificaciones en la patria potestad o tutoría legal deben ser respaldadas por documentación judicial.",
                    size=12,
                    color=MUTED,
                ),
            ],
        ),
    )

    panel_seguridad_privacidad = ft.Container(
        width=320,
        height=266,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Seguridad y Privacidad", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Icon(ft.Icons.SHIELD_OUTLINED, size=24, color=TEAL),
                ft.Text("Autenticación de Dos Factores (2FA)", size=13, color=TEXT_COLOR),
                ft.Text(
                    "Obligatoria para roles con privilegios de modificación de notas, cobros y datos personales sensibles.",
                    size=13,
                    color=MUTED,
                ),
                ft.Text("Configurar políticas de contraseñas", size=12, weight=ft.FontWeight.W_600, color=TEAL),
            ],
        ),
    )

    fila_asociacion_privacidad = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[panel_asociacion_familiar, panel_seguridad_privacidad],
    )

    nota_final = ft.Text(
        "* La asignación y uso de credenciales se rige bajo la Ley de Protección de Datos Personales (Ley N° 25.326).",
        size=11,
        color=MUTED,
    )

    # ==================== 6. ENSAMBLE DEL LAYOUT GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/usuarios")
    topbar = create_topbar(page, titulo="Usuarios y Permisos — Accesos y roles")

    main_content = ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        content=ft.Column(
            spacing=0,
            controls=[
                topbar,
                ft.Container(
                    expand=True,
                    padding=32,
                    content=ft.Column(
                        spacing=20,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            encabezado_modulo,
                            filtros_fila,
                            tabla_usuarios_contenedor,
                            nota_tabla_usuarios,
                            seccion_permisos_rol,
                            fila_asociacion_privacidad,
                            nota_final,
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[sidebar, main_content],
    )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Usuarios y Permisos"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_usuarios_view(page))

    ft.run(main)