from datetime import datetime
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
    TEAL_LIGHT,
    TEXT_COLOR,
)


async def get_admin_alumno_form_view(page: ft.Page) -> ft.Row:
    """Retorna la vista asíncrona de alta de alumno conectada con la API."""

    # ==================== 1. CARGA INICIAL DE CURSOS ====================
    cursos_opciones: list[ft.dropdown.Option] = []
    try:
        cursos_data = await api_client.get_cursos()
        for c in cursos_data:
            id_curso = str(c.get("id_curso", ""))
            nombre = c.get("nombre", "")
            division = c.get("division", "")
            texto = f"{nombre} {division}".strip()
            cursos_opciones.append(ft.dropdown.Option(key=id_curso, text=texto))
    except (httpx.RequestError, httpx.HTTPStatusError):
        cursos_opciones = []

    # ==================== 2. CAMPOS DEL FORMULARIO ====================
    dni_field = ft.TextField(
        hint_text="Ej: 46124990",
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
        hint_text="Ej: Sofía Valentina",
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
        hint_text="Ej: Díaz",
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

    def format_fecha(e):
        valor_actual = e.control.value or ""
        numeros = "".join(filter(str.isdigit, valor_actual))

        formateado = ""
        if len(numeros) > 0:
            formateado += numeros[:4]
        if len(numeros) >= 5:
            formateado += "-" + numeros[4:6]
        if len(numeros) >= 7:
            formateado += "-" + numeros[6:8]

        if e.control.value != formateado:
            e.control.value = formateado
            e.control.update()

    fecha_nac_field = ft.TextField(
        hint_text="AAAA-MM-DD (ej: 2012-05-18)",
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
        on_change=format_fecha,
    )

    domicilio_field = ft.TextField(
        hint_text="Av. Sarmiento 450, Resistencia",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
        keyboard_type=ft.KeyboardType.STREET_ADDRESS,
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

    email_field = ft.TextField(
        hint_text="contacto@familia.com",
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

    curso_dropdown = ft.Dropdown(
        hint_text="Seleccione un curso...",
        hint_style=ft.TextStyle(size=13, color=MUTED),
        text_size=13,
        options=cursos_opciones,
        bgcolor=TEAL_DARK,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 0, 8, 12),
        height=CONTROL_HEIGHT,
    )

    feedback_text = ft.Text("", size=13, weight=ft.FontWeight.W_600, visible=False)

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

    # ==================== 3. LÓGICA DE GUARDADO ====================
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

    async def guardar_alumno(e):
        feedback_text.visible = False
        page.update()

        dni = (dni_field.value or "").strip()
        nombres = (nombres_field.value or "").strip()
        apellidos = (apellidos_field.value or "").strip()
        fecha_nac = (fecha_nac_field.value or "").strip()
        domicilio = (domicilio_field.value or "").strip()
        id_curso = curso_dropdown.value

        if not all([dni, nombres, apellidos, fecha_nac, domicilio, id_curso]):
            feedback_text.value = (
                "⚠️ DNI, Nombres, Apellidos, Fecha, Domicilio y Curso son obligatorios."
            )
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        if len(fecha_nac) != 10:
            feedback_text.value = (
                "⚠️ La fecha debe estar completa con el formato AAAA-MM-DD."
            )
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        try:
            datetime.strptime(fecha_nac, "%Y-%m-%d")
        except ValueError:
            feedback_text.value = "⚠️ La fecha ingresada no existe en el calendario."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        try:
            id_curso_int = int(id_curso)
        except ValueError:
            feedback_text.value = "⚠️ El curso seleccionado es inválido."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        payload = {
            "dni": dni,
            "nombre": nombres,
            "apellido": apellidos,
            "fecha_nacimiento": fecha_nac,
            "domicilio": domicilio,
            "telefono": (telefono_field.value or "").strip() or None,
            "correo_electronico": (email_field.value or "").strip() or None,
            "id_curso": id_curso_int,
        }

        btn_guardar.disabled = True
        btn_guardar.content = ft.Text(
            "Guardando...", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
        )
        page.update()

        try:
            await api_client.create_alumno(payload)
            page.go("/admin/alumnos")
        except httpx.HTTPStatusError as err:
            btn_guardar.disabled = False
            btn_guardar.content = ft.Text(
                "Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
            )
            detalle = "Error al crear el alumno."
            try:
                data_err = err.response.json()
                detalle = data_err.get("detail", detalle)
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

    btn_guardar.on_click = guardar_alumno

    # ==================== 4. ACCIONES SUPERIORES ====================
    header_actions = ft.Row(
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
                        tooltip="Volver al listado",
                        on_click=lambda _: page.go("/admin/alumnos"),
                        content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
                    ),
                    ft.Text(
                        "Nuevo Alumno (Ciclo Lectivo)",
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
                    feedback_text,
                    ft.Button(
                        content=ft.Text(
                            "Cancelar", size=14, weight=ft.FontWeight.W_600, color=MUTED
                        ),
                        bgcolor=BG_WHITE,
                        height=37,
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1, BORDER_COLOR),
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                            padding=ft.Padding(20, 10, 20, 10),
                        ),
                        on_click=lambda _: page.go("/admin/alumnos"),
                    ),
                    btn_guardar,
                ],
            ),
        ],
    )

    # ==================== 5. COLUMNAS Y FORMULARIO ====================
    card_info_personal = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    "Información Personal",
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
                                envolver_campo(
                                    "Fecha de Nacimiento *", fecha_nac_field
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Nombres *", nombres_field),
                                envolver_campo("Apellidos *", apellidos_field),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Domicilio Real *", domicilio_field),
                                envolver_campo("Teléfono de Contacto", telefono_field),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Correo Electrónico Tutor", email_field),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    card_info_academica = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    "Información Académica",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        envolver_campo("Curso Asignado *", curso_dropdown),
                    ],
                ),
            ],
        ),
    )

    columna_izquierda = ft.Column(
        expand=True,
        spacing=24,
        controls=[card_info_personal, card_info_academica],
    )

    # Lateral informativo
    card_instrucciones = ft.Container(
        width=360,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "Pautas de Matriculación",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Text(
                    "1. El DNI debe ingresarse sin puntos ni caracteres especiales.\n\n"
                    "2. La fecha de nacimiento sigue el formato estándar AAAA-MM-DD.\n\n"
                    "3. El curso asignará automáticamente las materias y turnos predeterminados.",
                    size=13,
                    color=MUTED,
                ),
                ft.Container(
                    bgcolor=TEAL_LIGHT,
                    border_radius=BORDER_RADIUS,
                    padding=14,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=TEAL),
                            ft.Text(
                                "El legajo será asignado automáticamente por el sistema al guardar la ficha.",
                                size=12,
                                color=TEAL_DARK,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    return admin_layout(
        page=page,
        titulo="Ficha de Alumno — Alta de Matrícula K-12",
        active_route="/admin/alumnos",
        content_controls=[
            header_actions,
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[columna_izquierda, card_instrucciones],
            ),
        ],
    )
