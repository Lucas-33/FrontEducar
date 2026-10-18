import httpx
import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import dropdown_con_label, input_con_label

# El backend (y la BD) espera los estados en mayúsculas
ESTADO_API = {"Activo": "ACTIVO", "Licencia": "LICENCIA", "Inactivo": "INACTIVO"}


def _valor(campo: ft.Column) -> str:
    """Extrae el valor del control interno de input_con_label / dropdown_con_label."""
    return (campo.controls[1].content.value or "").strip()


async def get_admin_profesor_form_view(page: ft.Page) -> ft.Row:
    """Vista del formulario de alta de docentes conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    feedback_text = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False)

    # ==================== CAMPOS DEL FORMULARIO ====================
    campo_legajo = input_con_label("Legajo *", "Ej: 2005")
    campo_dni = input_con_label("DNI *", "Ej: 32.400.912")
    campo_nombres = input_con_label("Nombres *", "Ej: Guillermina")
    campo_apellidos = input_con_label("Apellidos *", "Ej: Sánchez")
    campo_especialidad = input_con_label("Especialidad Principal *", "Ej: Matemática Aplicada, Álgebra")
    campo_estado = dropdown_con_label("Estado de Contrato *", "Activo", ["Activo", "Licencia", "Inactivo"])
    campo_correo = input_con_label("Correo Laboral *", "ejemplo@educar.edu.ar")
    campo_telefono = input_con_label("Teléfono Particular *", "3624-XXXXXX")

    # ==================== 1. ENCABEZADO DE ACCIONES ====================
    btn_guardar = ft.Button(
        content=ft.Text("Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
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

        legajo = _valor(campo_legajo)
        dni = _valor(campo_dni)
        nombres = _valor(campo_nombres)
        apellidos = _valor(campo_apellidos)
        especialidad = _valor(campo_especialidad)
        estado = (campo_estado.controls[1].content.value or "Activo").strip()
        correo = _valor(campo_correo)
        telefono = _valor(campo_telefono)

        if not all([legajo, dni, nombres, apellidos, especialidad, correo, telefono]):
            feedback_text.value = "⚠️ Legajo, DNI, Nombres, Apellidos, Especialidad, Correo y Teléfono son obligatorios."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        try:
            legajo_int = int(legajo)
        except ValueError:
            feedback_text.value = "⚠️ El legajo debe ser un número entero."
            feedback_text.color = BADGE_RED_TXT
            feedback_text.visible = True
            page.update()
            return

        payload = {
            "legajo": legajo_int,
            "dni": dni,
            "nombre": nombres,
            "apellido": apellidos,
            "especialidad": especialidad,
            "correo_electronico": correo,
            "telefono": telefono,
            "estado": ESTADO_API.get(estado, "ACTIVO"),
        }

        btn_guardar.disabled = True
        btn_guardar.content = ft.Text("Guardando...", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE)
        page.update()

        try:
            await api_client.create_profesor(payload)
            page.go("/admin/profesores")
        except httpx.HTTPStatusError as err:
            btn_guardar.disabled = False
            btn_guardar.content = ft.Text("Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE)
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
            btn_guardar.content = ft.Text("Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE)
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
                                content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
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
                                content=ft.Text("Cancelar", size=14, weight=ft.FontWeight.W_600, color=MUTED),
                                bgcolor=BG_WHITE,
                                height=37,
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, BORDER_COLOR),
                                    shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
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
                ft.Text("Información Básica", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=16,
                            controls=[campo_legajo, campo_dni],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[campo_nombres, campo_apellidos],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[campo_especialidad, campo_estado],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[campo_correo, campo_telefono],
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
                        ft.Text("Materias a Cargo", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.Text("Asigne las asignaturas correspondientes.", size=12, color=MUTED),
                    ],
                ),
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=BORDER_RADIUS,
                    padding=16,
                    content=ft.Text(
                        "Guarde el docente y luego asigne materias y cursos desde el módulo "
                        "\"Materias\" (botón \"Asignar Materia\").",
                        size=13,
                        color=MUTED,
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
