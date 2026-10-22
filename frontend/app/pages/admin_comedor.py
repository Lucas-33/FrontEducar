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
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def _fecha_corta(iso: str | None) -> str:
    """Convierte un ISO timestamp del backend en dd/mm/aaaa."""
    if not iso or len(iso) < 10:
        return "-"
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"


def _nombre_alumno(valor: str) -> str:
    """Quita el sufijo '(#legajo)' para mostrar el nombre simple en la columna Estudiante."""
    texto = (valor or "").strip()
    if " (#" in texto:
        texto = texto.rsplit(" (#", 1)[0].strip()
    return texto or "-"


async def get_admin_comedor_view(page: ft.Page) -> ft.Row:
    """Vista de Inscripción y Control del Servicio de Comedor conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    # ==================== 1. ESTADO DE LA VISTA ====================
    estado: dict = {"inscripciones": [], "texto": "", "estado_inscripcion": "Todos"}

    try:
        estado["inscripciones"] = await api_client.get_inscripciones_comedor()
    except Exception:
        estado["inscripciones"] = []

    def esta_activo(item: dict) -> bool:
        return (item.get("estado") or "").strip().upper() == "ACTIVO"

    # ==================== 2. ENCABEZADO ====================
    encabezado_seccion = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Gestión de Servicios Complementarios y Nutrición",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Inscripción al Servicio de Comedor Escolar",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Registre el alta de los estudiantes al comedor institucional, consulte los inscriptos y gestione las bajas del servicio.",
                        size=14,
                        color=MUTED,
                    ),
                ],
            ),
            ft.Container(
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=TEAL_LIGHT,
                border_radius=4,
                content=ft.Text(
                    "Servicio Activo", size=12, weight=ft.FontWeight.W_600, color=TEAL
                ),
            ),
        ],
    )

    # ==================== 3. BARRA DE FILTROS Y ACCIÓN ====================
    search_field = ft.TextField(
        hint_text="Buscar alumno o legajo...",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 10),
        expand=True,
    )
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
                search_field,
            ],
        ),
    )

    filtro_estado_container = ft.Container(
        width=170,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=ft.Dropdown(
            hint_text="Estado: Todos",
            hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
            text_size=14,
            border=ft.InputBorder.NONE,
            content_padding=ft.Padding(12, 0, 8, 12),
            options=[
                ft.dropdown.Option(opc) for opc in ["Todos", "Activo", "Inactivo"]
            ],
        ),
    )
    filtro_estado_dropdown: ft.Dropdown = filtro_estado_container.content

    btn_inscribir = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.PERSON_ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Inscribir Alumno",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=BG_WHITE,
                ),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[search_input, filtro_estado_container],
            ),
            btn_inscribir,
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 4. TABLA DE INSCRIPTOS ====================
    columnas_comedor = [
        ("Estudiante", 260, False),
        ("Legajo", 110, False),
        ("Fecha de Alta", 140, False),
        ("Estado", 110, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_comedor)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def inscripto_row(item: dict) -> ft.Container:
        activo = esta_activo(item)

        async def dar_de_baja(e):
            try:
                await api_client.baja_comedor(item["legajo_alumno"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo dar de baja la inscripción al comedor."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                mostrar_error(detalle)
                return
            except httpx.RequestError:
                mostrar_error("Error de conexión con el backend.")
                return
            await recargar()

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=260,
                        content=ft.Text(
                            _nombre_alumno(item.get("alumno", "")),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            f"#{item['legajo_alumno']}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=140,
                        content=ft.Text(
                            _fecha_corta(item.get("fecha_alta")), size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=status_badge("Activo" if activo else "Inactivo"),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=BADGE_RED_TXT
                                    if activo
                                    else BORDER_COLOR,
                                    tooltip="Baja del Comedor"
                                    if activo
                                    else "Inscripción ya dada de baja",
                                    padding=0,
                                    disabled=not activo,
                                    on_click=dar_de_baja if activo else None,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def inscriptos_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for i in estado["inscripciones"]:
            estado_legible = "Activo" if esta_activo(i) else "Inactivo"
            if (
                estado["estado_inscripcion"] != "Todos"
                and estado_legible != estado["estado_inscripcion"]
            ):
                continue
            if (
                texto
                and texto
                not in f"{i.get('alumno', '')} {i.get('legajo_alumno', '')}".lower()
            ):
                continue
            resultado.append(i)
        return resultado

    def render():
        visibles = inscriptos_filtrados()
        activos_totales = len([i for i in estado["inscripciones"] if esta_activo(i)])

        if not estado["inscripciones"]:
            mensaje_vacio = "No hay alumnos inscriptos al comedor todavía."
        else:
            mensaje_vacio = "No hay inscriptos que coincidan con los filtros."

        table_holder.content = create_table_container(
            header=header_table,
            rows=[inscripto_row(i) for i in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(mensaje_vacio, size=13, color=MUTED),
                )
            ],
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=(
                f"Mostrando {len(visibles)} de {len(estado['inscripciones'])} inscriptos "
                f"· {activos_totales} con servicio activo"
            ),
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["inscripciones"] = await api_client.get_inscripciones_comedor()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de inscriptos: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_estado(e):
        estado["estado_inscripcion"] = filtro_estado_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_estado_dropdown.on_change = on_filtrar_estado

    # ==================== 5. DIÁLOGO INSCRIBIR ALUMNO ====================
    async def abrir_inscribir_alumno(e):
        try:
            alumnos = await api_client.get_alumnos(solo_activos=True)
        except Exception:
            alumnos = []

        alumno_field = ft.Dropdown(
            label="Alumno *",
            width=380,
            options=[
                ft.dropdown.Option(
                    key=str(a["legajo"]),
                    text=f"{a.get('apellido', '')}, {a.get('nombre', '')} (#{a['legajo']})",
                )
                for a in alumnos
            ],
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        if not alumnos:
            error_text.value = "⚠️ No hay alumnos activos disponibles para inscribir."
            error_text.visible = True

        async def guardar(e):
            if not alumno_field.value:
                error_text.value = "Debe seleccionar un alumno."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.inscribir_comedor(
                    {"legajo_alumno": int(alumno_field.value)}
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al inscribir al alumno en el comedor."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Inscribir Alumno al Comedor", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        "El alta quedará registrada con la fecha del día y habilitará la vianda institucional.",
                        size=13,
                        color=MUTED,
                    ),
                    alumno_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Inscribir", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    btn_inscribir.on_click = abrir_inscribir_alumno

    # ==================== 6. AVISO OPERATIVO ====================
    aviso_servicio = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.Icons.RESTAURANT_OUTLINED, size=18, color=TEAL),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(
                            "Registro del Servicio de Comedor",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                        ft.Text(
                            "Las altas se registran con la fecha del día. Las bajas conservan el historial del alumno y pasan su estado a Inactivo.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
            ],
        ),
    )

    render()

    # ==================== 7. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Comedor — Inscripción al servicio",
        active_route="/admin/comedor",
        spacing=20,
        content_controls=[
            encabezado_seccion,
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
            aviso_servicio,
        ],
    )
