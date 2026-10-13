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
    CONTROL_HEIGHT,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


# =====================================================================
# CLASE AISLADA: Protege la memoria de los eventos de clic en Flet
# =====================================================================
class FilaAlumno(ft.Container):
    def __init__(self, alumno_data: dict, callback_editar, callback_eliminar):
        super().__init__()
        self.alumno_data = alumno_data
        self.callback_editar = callback_editar
        self.callback_eliminar = callback_eliminar

        # Extracción de datos
        self.legajo = str(alumno_data.get("legajo", ""))
        dni = str(alumno_data.get("dni", ""))
        apellido = alumno_data.get("apellido", "")
        nombre = alumno_data.get("nombre", "")
        curso = str(alumno_data.get("curso") or alumno_data.get("id_curso") or "Sin Asignar")
        telefono = alumno_data.get("telefono") or "-"
        correo = alumno_data.get("correo_electronico") or alumno_data.get("email") or "-"
        
        estado_raw = alumno_data.get("estado")
        estado_texto = "Activo" if (estado_raw is None or estado_raw is True or str(estado_raw).lower() == "activo") else "Inactivo"

        # Diseño de la fila
        self.height = 54
        self.padding = ft.Padding(16, 0, 16, 0)
        self.border = ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR))
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=90, content=ft.Text(self.legajo, size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=110, content=ft.Text(dni, size=13, color=TEXT_COLOR)),
                ft.Container(width=130, content=ft.Text(apellido, size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                ft.Container(width=140, content=ft.Text(nombre, size=14, color=TEXT_COLOR)),
                ft.Container(width=120, content=ft.Text(curso, size=13, color=TEAL)),
                ft.Container(width=120, content=ft.Text(telefono, size=13, color=TEXT_COLOR)),
                ft.Container(width=210, content=ft.Text(correo, size=13, color=MUTED)),
                ft.Container(width=95, content=status_badge(estado_texto)),
                ft.Container(
                    width=110,
                    alignment=ft.Alignment(1, 0),
                    content=ft.Row(
                        spacing=6,
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED, 
                                icon_size=18, 
                                icon_color=TEAL, 
                                tooltip="Editar Alumno",
                                on_click=self.click_editar
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE, 
                                icon_size=18, 
                                icon_color=BADGE_RED_TXT, 
                                tooltip="Dar de Baja",
                                on_click=self.click_eliminar
                            ),
                        ],
                    ),
                ),
            ],
        )

    def click_editar(self, e):
        print(f"🔥 ¡CLIC DETECTADO! Editar alumno legajo: {self.legajo}")
        self.callback_editar(self.alumno_data)

    def click_eliminar(self, e):
        print(f"🔥 ¡CLIC DETECTADO! Eliminar alumno legajo: {self.legajo}")
        self.callback_eliminar(self.alumno_data)


# =====================================================================
# VISTA PRINCIPAL
# =====================================================================
async def get_admin_alumnos_view(page: ft.Page) -> ft.Row:
    # 1. Autenticación
    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    # 2. Obtención de Datos
    alumnos_data: list[dict] = []
    error_servidor = False
    try:
        alumnos_data = await api_client.get_alumnos(solo_activos=True)
    except Exception as e:
        print(f"Error cargando alumnos: {e}")
        error_servidor = True

    # 3. Contenedor de la tabla
    filas_column = ft.Column(spacing=0)

    # 4. Lógica de las acciones
    def accion_editar(alumno_seleccionado: dict):
        page.alumno_en_edicion = alumno_seleccionado
        page.go("/admin/alumnos/editar")

    def accion_eliminar(alumno_seleccionado: dict):
        legajo = str(alumno_seleccionado.get("legajo", ""))
        nombre = alumno_seleccionado.get("nombre", "")
        apellido = alumno_seleccionado.get("apellido", "")

        dlg_baja = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Baja", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"¿Desea dar de baja a {nombre} {apellido} (Legajo: {legajo})?"),
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def cerrar_modal(e=None):
            dlg_baja.open = False
            page.update()
            if dlg_baja in page.overlay:
                page.overlay.remove(dlg_baja)

        async def ejecutar_baja(e):
            dlg_baja.actions[1].disabled = True
            page.update()
            try:
                await api_client.delete_alumno(legajo)
                print(f"✅ Baja confirmada en la BD para legajo {legajo}")
                if alumno_seleccionado in alumnos_data:
                    alumnos_data.remove(alumno_seleccionado)
                cerrar_modal()
                recargar_tabla()
            except Exception as err:
                print(f"❌ Error al borrar en la API: {err}")
                dlg_baja.actions[1].disabled = False
                page.update()

        dlg_baja.actions = [
            ft.TextButton("Cancelar", on_click=cerrar_modal),
            ft.Button("Confirmar Baja", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=lambda ev: asyncio.create_task(ejecutar_baja(ev)))
        ]

        if dlg_baja not in page.overlay:
            page.overlay.append(dlg_baja)
        dlg_baja.open = True
        page.update()

    # 5. Generador y refresco de tabla
    def recargar_tabla():
        filas_column.controls.clear()
        if error_servidor:
            filas_column.controls.append(ft.Container(padding=24, content=ft.Text("⚠️ Error de conexión con API.", color=BADGE_RED_TXT)))
        elif not alumnos_data:
            filas_column.controls.append(ft.Container(padding=24, content=ft.Text("No hay alumnos activos.", color=MUTED)))
        else:
            for a in alumnos_data:
                filas_column.controls.append(FilaAlumno(a, accion_editar, accion_eliminar))
        
        # Bloque try/except para evadir el crash de Flet en la carga inicial
        try:
            filas_column.update()
        except Exception:
            pass

    # Carga inicial de filas
    recargar_tabla()

    # 6. UI Superior
    search_input = ft.Container(
        width=280, height=CONTROL_HEIGHT, bgcolor=BG_WHITE, border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS, padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
            ft.TextField(hint_text="Buscar por apellido...", text_size=14, border=ft.InputBorder.NONE, expand=True),
        ]),
    )

    btn_nuevo_alumno = ft.Button(
        content=ft.Row(spacing=8, controls=[ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE), ft.Text("Nuevo Alumno", color=BG_WHITE)]),
        bgcolor=TEAL, height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS), padding=ft.Padding(24, 12, 24, 12)),
        on_click=lambda _: page.go("/admin/alumnos/nuevo"),
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[search_input, btn_nuevo_alumno],
    )

    columnas_alumnos = [
        ("Legajo", 90, False), ("DNI", 110, False), ("Apellido", 130, False), ("Nombre", 140, False),
        ("Curso", 120, False), ("Teléfono", 120, False), ("Correo", 210, False), ("Estado", 95, False), ("Acciones", 110, True)
    ]
    header_table = create_table_header(columnas_alumnos)

    table_container = create_table_container(
        header=header_table,
        rows=[filas_column],
        min_width=1125,
    )

    pagination_bar = create_pagination_bar(
        texto_info=f"Total: {len(alumnos_data)} estudiantes",
        pagina_actual=1,
        total_paginas=1,
    )

    return admin_layout(
        page=page,
        titulo="Directorio de Estudiantes",
        active_route="/admin/alumnos",
        content_controls=[filters_bar, table_container, pagination_bar],
    )