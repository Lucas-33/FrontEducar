import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
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
    TEXT_COLOR,
)

ESTADO_API = {"Activo": "ACTIVO", "Licencia": "LICENCIA", "Inactivo": "INACTIVO"}


async def get_admin_profesor_form_view(page: ft.Page) -> ft.Row:
    """Vista del formulario de alta de docentes conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    feedback_text = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== CAMPOS DEL FORMULARIO ====================
    dni_field = ft.TextField(
        hint_text="Ej: 32400912",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$"),
    )

    nombres_field = ft.TextField(
        hint_text="Ej: Guillermina",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
        keyboard_type=ft.KeyboardType.NAME,
        input_filter=ft.InputFilter(
            allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]*$"
        ),
    )

    apellidos_field = ft.TextField(
        hint_text="Ej: Sánchez",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
        keyboard_type=ft.KeyboardType.NAME,
        input_filter=ft.InputFilter(
            allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]*$"
        ),
    )

    especialidad_field = ft.TextField(
        hint_text="Ej: Matemática Aplicada, Álgebra",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
        keyboard_type=ft.KeyboardType.TEXT,
    )

    correo_field = ft.TextField(
        hint_text="ejemplo@educar.edu.ar",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
        keyboard_type=ft.KeyboardType.EMAIL,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[a-zA-Z0-9_.@\-]*$"),
    )

    telefono_field = ft.TextField(
        hint_text="3624-XXXXXX",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
        keyboard_type=ft.KeyboardType.PHONE,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\-\+\s]*$"),
    )

    estado_dropdown = ft.Dropdown(
        value="Activo",
        text_size=13,
        options=[
            ft.dropdown.Option("Activo"),
            ft.dropdown.Option("Licencia"),
            ft.dropdown.Option("Inactivo"),
        ],
        bgcolor=TEAL_DARK,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 0, 8, 12),
        height=CONTROL_HEIGHT,
    )

    def envolver_campo(
        label: str, control: ft.Control, expand: bool = True
    ) -> ft.Column:
        return ft.Column(
            spacing=6,
            expand=expand,
            controls=[
                ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                control,
            ],
        )

    # ==================== 1. ENCABEZADO DE ACCIONES ====================
    btn_guardar = ft.Button(
        content=ft.Text(
            "Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
        ),
        bgcolor=TEAL,
        height=37,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 10, 20, 10),
        ),
    )

    async def guardar_profesor(e):
        feedback_text.visible = False
        page.update()

        dni = (dni_field.value or "").strip()
        nombres = (nombres_field.value or "").strip()
        apellidos = (apellidos_field.value or "").strip()
        especialidad = (especialidad_field.value or "").strip()
        correo = (correo_field.value or "").strip()
        telefono = (telefono_field.value or "").strip()
        estado = (estado_dropdown.value or "Activo").strip()

        if not all([dni, nombres, apellidos, especialidad, correo, telefono]):
            feedback_text.value = "⚠️ DNI, Nombres, Apellidos, Especialidad, Correo y Teléfono son obligatorios."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        payload = {
            "dni": dni,
            "nombre": nombres,
            "apellido": apellidos,
            "especialidad": especialidad,
            "correo_electronico": correo,
            "telefono": telefono,
            "estado": ESTADO_API.get(estado, "ACTIVO"),
        }

        btn_guardar.disabled = True
        btn_guardar.content = ft.Text(
            "Guardando...", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
        )
        page.update()

        try:
            await api_client.create_profesor(payload)
            page.go("/admin/profesores")
        except httpx.HTTPStatusError as err:
            btn_guardar.disabled = False
            btn_guardar.content = ft.Text(
                "Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
            )
            detalle = "Error al crear el docente."
            try:
                detalle = err.response.json().get("detail", detalle)
            except Exception:
                pass
            feedback_text.value = f"⚠️ {detalle}"
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
        except httpx.RequestError:
            btn_guardar.disabled = False
            btn_guardar.content = ft.Text(
                "Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
            )
            feedback_text.value = "⚠️ Error de conexión con el backend."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()

    btn_guardar.on_click = guardar_profesor

    header_actions = ft.Column(
        spacing=8,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=36,
                                height=36,
                                bgcolor=BG_WHITE,
                                border=ft.Border.all(1, BORDER_COLOR),
                                border_radius=18,
                                alignment=ft.Alignment(0, 0),
                                tooltip="Volver a la nómina de profesores",
                                on_click=lambda _: page.go("/admin/profesores"),
                                content=ft.Icon(
                                    ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR
                                ),
                            ),
                            ft.Text(
                                "Nuevo Docente",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Button(
                                content=ft.Text(
                                    "Cancelar",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=MUTED,
                                ),
                                bgcolor=BG_WHITE,
                                height=37,
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, BORDER_COLOR),
                                    shape=ft.RoundedRectangleBorder(
                                        radius=BORDER_RADIUS
                                    ),
                                    padding=ft.Padding(20, 10, 20, 10),
                                ),
                                on_click=lambda _: page.go("/admin/profesores"),
                            ),
                            btn_guardar,
                        ],
                    ),
                ],
            ),
            feedback_text,
        ],
    )

    # ==================== 2. COLUMNA IZQUIERDA FLUIDA ====================
    card_info_basica = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    "Información Básica",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("DNI *", dni_field),
                                envolver_campo("Nombres *", nombres_field),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Apellidos *", apellidos_field),
                                envolver_campo(
                                    "Especialidad Principal *", especialidad_field
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Correo Laboral *", correo_field),
                                envolver_campo("Teléfono Particular *", telefono_field),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Estado de Contrato *", estado_dropdown),
                                ft.Container(
                                    expand=True
                                ),  # Placeholder para mantener simetría
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    columna_izquierda = ft.Column(
        expand=True,
        spacing=24,
        controls=[card_info_basica],
    )

    # ==================== 3. COLUMNA DERECHA COMPACTA ====================
    card_materias_cargo = ft.Container(
        width=380,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Materias a Cargo",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.Text(
                            "Asigne las asignaturas correspondientes.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=BORDER_RADIUS,
                    padding=16,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                "El legajo será asignado automáticamente por el sistema al guardar.",
                                size=13,
                                color=MUTED,
                            ),
                            ft.Text(
                                "Guarde el docente y luego asigne materias y cursos desde el módulo "
                                '"Materias" (botón "Asignar Materia").',
                                size=13,
                                color=MUTED,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Ficha de Docente — Alta y Asignación Académica",
        active_route="/admin/profesores",
        content_controls=[
            header_actions,
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[columna_izquierda, card_materias_cargo],
            ),
        ],
    )
