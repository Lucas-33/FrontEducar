import asyncio
import flet as ft
import httpx
from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
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

# Respaldo seguro de color de fondo
try:
    from frontend.app.components.constants import BG_PAGE
except ImportError:
    BG_PAGE = "#f8fafc"


async def get_admin_alumno_form_view(page: ft.Page) -> ft.Row:
    """Formulario unificado para Alta y Edición de Alumnos conectado a la API."""

    alumno_editar: dict | None = getattr(page, "alumno_en_edicion", None)
    es_edicion = alumno_editar is not None

    titulo_pagina = (
        f"Editar Ficha — Legajo {alumno_editar.get('legajo')}"
        if es_edicion
        else "Ficha de Alumno — Alta de Matrícula K-12"
    )

    # 1. Cargar cursos desde el backend
    cursos_opciones: list[ft.dropdown.Option] = []
    try:
        cursos_data = await api_client.get_cursos()
        for c in cursos_data:
            id_c = str(c.get("id_curso", ""))
            nombre = c.get("nombre", "")
            division = c.get("division", "")
            texto = f"{nombre} {division}".strip()
            cursos_opciones.append(ft.dropdown.Option(key=id_c, text=texto))
    except (httpx.RequestError, httpx.HTTPStatusError):
        cursos_opciones = []

    # 2. Precarga de valores si es edición
    legajo_val = str(alumno_editar.get("legajo", "")) if es_edicion else ""
    dni_val = str(alumno_editar.get("dni", "")) if es_edicion else ""
    nombres_val = str(alumno_editar.get("nombre", "")) if es_edicion else ""
    apellidos_val = str(alumno_editar.get("apellido", "")) if es_edicion else ""
    fecha_nac_val = str(alumno_editar.get("fecha_nacimiento", "") or "") if es_edicion else ""
    domicilio_val = str(alumno_editar.get("domicilio", "") or "") if es_edicion else ""
    telefono_val = str(alumno_editar.get("telefono", "") or "") if es_edicion else ""
    email_val = str(alumno_editar.get("correo_electronico", "") or alumno_editar.get("email", "") or "") if es_edicion else ""

    curso_inicial = None
    if es_edicion:
        c_id = alumno_editar.get("id_curso")
        if c_id is not None:
            curso_inicial = str(c_id)

    # 3. Controles del formulario
    legajo_field = ft.TextField(
        value=legajo_val,
        disabled=es_edicion,
        hint_text="Autogenerado o manual (ej: 10255)",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        bgcolor=BG_PAGE if es_edicion else BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 10, 12, 10),
        height=CONTROL_HEIGHT,
    )

    dni_field = ft.TextField(
        value=dni_val,
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
    )

    nombres_field = ft.TextField(
        value=nombres_val,
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
    )

    apellidos_field = ft.TextField(
        value=apellidos_val,
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
    )

    fecha_nac_field = ft.TextField(
        value=fecha_nac_val,
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
    )

    domicilio_field = ft.TextField(
        value=domicilio_val,
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
    )

    telefono_field = ft.TextField(
        value=telefono_val,
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
    )

    email_field = ft.TextField(
        value=email_val,
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
    )

    curso_dropdown = ft.Dropdown(
        value=curso_inicial,
        hint_text="Seleccione un curso...",
        hint_style=ft.TextStyle(size=13, color=MUTED),
        text_size=13,
        options=cursos_opciones,
        bgcolor=BG_WHITE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 0, 8, 12),
        height=CONTROL_HEIGHT,
    )

    feedback_text = ft.Text("", size=13, weight=ft.FontWeight.W_600, visible=False)

    def envolver_campo(label: str, control: ft.Control, expand: bool = True) -> ft.Column:
        return ft.Column(
            spacing=6,
            expand=expand,
            controls=[
                ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                control,
            ],
        )

    def volver_al_listado(e):
        page.alumno_en_edicion = None
        page.go("/admin/alumnos")

    texto_guardar = "Actualizar Alumno" if es_edicion else "Guardar Alumno"
    btn_guardar = ft.Button(
        content=ft.Text(texto_guardar, size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
        bgcolor=TEAL,
        height=37,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 10, 20, 10),
        ),
    )

    async def guardar_o_actualizar(e):
        feedback_text.visible = False
        page.update()

        dni = (dni_field.value or "").strip()
        nombres = (nombres_field.value or "").strip()
        apellidos = (apellidos_field.value or "").strip()
        fecha_nac = (fecha_nac_field.value or "").strip()
        id_curso = curso_dropdown.value

        if not dni or not nombres or not apellidos:
            feedback_text.value = "⚠️ DNI, Nombres y Apellidos son obligatorios."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        payload = {
            "dni": dni,
            "nombre": nombres,
            "apellido": apellidos,
            "domicilio": (domicilio_field.value or "").strip() or None,
            "telefono": (telefono_field.value or "").strip() or None,
            "correo_electronico": (email_field.value or "").strip() or None,
        }

        if fecha_nac:
            payload["fecha_nacimiento"] = fecha_nac

        if id_curso:
            try:
                payload["id_curso"] = int(id_curso)
            except ValueError:
                payload["id_curso"] = id_curso

        btn_guardar.disabled = True
        btn_guardar.content = ft.Text("Guardando...", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE)
        page.update()

        try:
            if es_edicion:
                leg_id = str(alumno_editar["legajo"])
                await api_client.update_alumno(leg_id, payload)
            else:
                leg_in = (legajo_field.value or "").strip()
                if leg_in:
                    try:
                        payload["legajo"] = int(leg_in)
                    except ValueError:
                        payload["legajo"] = leg_in
                await api_client.create_alumno(payload)

            page.alumno_en_edicion = None
            page.go("/admin/alumnos")

        except httpx.HTTPStatusError as err:
            btn_guardar.disabled = False
            btn_guardar.content = ft.Text(texto_guardar, size=14, weight=ft.FontWeight.W_600, color=BG_WHITE)
            det = "Error al procesar la solicitud."
            try:
                det = err.response.json().get("detail", det)
            except Exception:
                pass
            feedback_text.value = f"⚠️ {det}"
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
        except httpx.RequestError:
            btn_guardar.disabled = False
            btn_guardar.content = ft.Text(texto_guardar, size=14, weight=ft.FontWeight.W_600, color=BG_WHITE)
            feedback_text.value = "⚠️ Error de conexión con el backend."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()

    btn_guardar.on_click = lambda ev: asyncio.create_task(guardar_o_actualizar(ev))

    # Botón dar de baja dentro del formulario (solo en edición)
    btn_eliminar_form = None
    if es_edicion:
        async def dar_de_baja_form(e):
            try:
                await api_client.delete_alumno(legajo_val)
                page.alumno_en_edicion = None
                page.go("/admin/alumnos")
            except Exception as err:
                feedback_text.value = f"⚠️ Error al dar de baja: {err}"
                feedback_text.color = BADGE_RED_TXT
                feedback_text.visible = True
                page.update()

        btn_eliminar_form = ft.Button(
            content=ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=BADGE_RED_TXT),
                    ft.Text("Dar de Baja Alumno", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT),
                ],
            ),
            bgcolor=ft.Colors.with_opacity(0.12, BADGE_RED_TXT),
            height=37,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                padding=ft.Padding(16, 10, 16, 10),
            ),
            on_click=lambda ev: asyncio.create_task(dar_de_baja_form(ev)),
        )

    acciones_header = [
        feedback_text,
        ft.Button(
            content=ft.Text("Cancelar", size=14, weight=ft.FontWeight.W_600, color=MUTED),
            bgcolor=BG_WHITE,
            height=37,
            style=ft.ButtonStyle(
                side=ft.BorderSide(1, BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                padding=ft.Padding(20, 10, 20, 10),
            ),
            on_click=volver_al_listado,
        ),
    ]

    if btn_eliminar_form:
        acciones_header.append(btn_eliminar_form)
    acciones_header.append(btn_guardar)

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
                        on_click=volver_al_listado,
                        content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
                    ),
                    ft.Text(
                        titulo_pagina,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                ],
            ),
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=acciones_header,
            ),
        ],
    )

    card_info_personal = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Información Personal", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Legajo", legajo_field),
                                envolver_campo("DNI *", dni_field),
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
                                envolver_campo("Fecha de Nacimiento", fecha_nac_field),
                                envolver_campo("Domicilio Real", domicilio_field),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                envolver_campo("Teléfono de Contacto", telefono_field),
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
                ft.Text("Información Académica", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
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

    card_instrucciones = ft.Container(
        width=360,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Pautas del Registro", size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text(
                    "1. En modo edición el legajo no puede alterarse para preservar el historial.\n\n"
                    "2. Cambiar de curso actualizará las asignaturas asociadas en PostgreSQL.\n\n"
                    "3. 'Dar de Baja Alumno' realiza una baja lógica sin borrar datos históricos.",
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
                            ft.Text("Los cambios se impactan en tiempo real en la base de datos.", size=12, color=TEAL_DARK),
                        ],
                    ),
                ),
            ],
        ),
    )

    return admin_layout(
        page=page,
        titulo=titulo_pagina,
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