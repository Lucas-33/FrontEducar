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


async def get_admin_transporte_view(page: ft.Page) -> ft.Row:
    """Vista del Servicio de Transporte Escolar conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    # ==================== 1. ESTADO DE LA VISTA ====================
    estado: dict = {
        "recorridos": [],
        "inscripciones": [],
        "texto": "",
        "recorrido": "Todos",
    }

    try:
        estado["recorridos"] = await api_client.get_recorridos()
    except Exception:
        estado["recorridos"] = []

    try:
        estado["inscripciones"] = await api_client.get_inscripciones_transporte()
    except Exception:
        estado["inscripciones"] = []

    def esta_activo(item: dict) -> bool:
        return (item.get("estado") or "").strip().upper() == "ACTIVO"

    def pasajeros_activos_de(id_recorrido) -> int:
        return len(
            [
                i
                for i in estado["inscripciones"]
                if i.get("id_recorrido") == id_recorrido and esta_activo(i)
            ]
        )

    # ==================== 2. TARJETAS DE RECORRIDOS (DATOS REALES) ====================
    def recorrido_card(num: int, recorrido: dict, activos: int) -> ft.Container:
        descripcion = recorrido.get("descripcion", "-")
        return ft.Container(
            width=280,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        width=28,
                                        height=28,
                                        bgcolor=TEAL_LIGHT,
                                        border_radius=14,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text(
                                            str(num),
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEAL_DARK,
                                        ),
                                    ),
                                    ft.Text(
                                        f"Recorrido {num}",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding(8, 4, 8, 4),
                                bgcolor=TEAL_LIGHT,
                                border_radius=4,
                                content=ft.Text(
                                    f"{activos} activos"
                                    if activos != 1
                                    else "1 activo",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color=TEAL,
                                ),
                            ),
                        ],
                    ),
                    ft.Text(
                        descripcion,
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=TEXT_COLOR,
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Pasajeros activos", size=11, color=MUTED),
                            ft.Row(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        str(activos),
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        icon_size=15,
                                        icon_color=TEAL,
                                        tooltip="Editar recorrido",
                                        padding=0,
                                        on_click=lambda e, r=recorrido: (
                                            abrir_editar_recorrido(r)
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_size=15,
                                        icon_color=BADGE_RED_TXT,
                                        tooltip="Eliminar recorrido",
                                        padding=0,
                                        on_click=lambda e, r=recorrido: (
                                            confirmar_eliminar_recorrido(r)
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

    def construir_banner() -> ft.Control:
        if not estado["recorridos"]:
            return ft.Container(
                bgcolor=BG_WHITE,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=CARD_RADIUS,
                padding=20,
                content=ft.Text(
                    "No hay recorridos cargados. Registre el primero con «Nuevo Recorrido».",
                    size=13,
                    color=MUTED,
                ),
            )
        return ft.Row(
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                recorrido_card(indice, r, pasajeros_activos_de(r.get("id_recorrido")))
                for indice, r in enumerate(estado["recorridos"], start=1)
            ],
        )

    banner_holder = ft.Container()

    # ==================== 3. BARRA DE FILTROS Y ACCIONES ====================
    search_field = ft.TextField(
        hint_text="Buscar alumno o recorrido...",
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

    filtro_recorrido_container = ft.Container(
        width=240,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=ft.Dropdown(
            hint_text="Recorrido: Todos",
            hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
            text_size=14,
            border=ft.InputBorder.NONE,
            content_padding=ft.Padding(12, 0, 8, 12),
            options=[ft.dropdown.Option("Todos")]
            + [
                ft.dropdown.Option(r.get("descripcion", "-"))
                for r in estado["recorridos"]
            ],
        ),
    )
    filtro_recorrido_dropdown: ft.Dropdown = filtro_recorrido_container.content

    btn_nuevo_recorrido = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD_ROAD, size=16, color=TEAL),
                ft.Text(
                    "Nuevo Recorrido", size=14, weight=ft.FontWeight.W_600, color=TEAL
                ),
            ],
        ),
        bgcolor=BG_WHITE,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 12, 20, 12),
            side=ft.BorderSide(1, TEAL),
        ),
    )

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
                controls=[search_input, filtro_recorrido_container],
            ),
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[btn_nuevo_recorrido, btn_inscribir],
            ),
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 4. TABLA DE PASAJEROS ====================
    columnas_transporte = [
        ("Legajo", 100, False),
        ("Estudiante", 240, False),
        ("Recorrido Asignado", 240, False),
        ("Fecha de Alta", 130, False),
        ("Estado", 110, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_transporte)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def pasajero_row(item: dict) -> ft.Container:
        activo = esta_activo(item)

        async def dar_de_baja(e):
            try:
                await api_client.baja_transporte(item["legajo_alumno"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo dar de baja la inscripción."
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
                        width=100,
                        content=ft.Text(
                            f"#{item['legajo_alumno']}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=240,
                        content=ft.Text(
                            _nombre_alumno(item.get("alumno", "")),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=240,
                        content=ft.Text(
                            item.get("recorrido", "-"),
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=TEAL,
                        ),
                    ),
                    ft.Container(
                        width=130,
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
                                    tooltip="Baja del Servicio"
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

    def inscripciones_filtradas() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for i in estado["inscripciones"]:
            if (
                estado["recorrido"] != "Todos"
                and i.get("recorrido") != estado["recorrido"]
            ):
                continue
            if (
                texto
                and texto
                not in f"{i.get('alumno', '')} {i.get('legajo_alumno', '')} {i.get('recorrido', '')}".lower()
            ):
                continue
            resultado.append(i)
        return resultado

    def render():
        banner_holder.content = construir_banner()
        visibles = inscripciones_filtradas()
        activos_totales = len([i for i in estado["inscripciones"] if esta_activo(i)])

        if not estado["inscripciones"]:
            mensaje_vacio = "No hay alumnos inscriptos al transporte todavía."
        else:
            mensaje_vacio = "No hay pasajeros que coincidan con los filtros."

        table_holder.content = create_table_container(
            header=header_table,
            rows=[pasajero_row(i) for i in visibles]
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
                f"Mostrando {len(visibles)} de {len(estado['inscripciones'])} inscripciones "
                f"· {activos_totales} pasajeros activos"
            ),
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    def actualizar_filtro_recorridos():
        descripciones = [r.get("descripcion", "-") for r in estado["recorridos"]]
        filtro_recorrido_dropdown.options = [ft.dropdown.Option("Todos")] + [
            ft.dropdown.Option(d) for d in descripciones
        ]
        if estado["recorrido"] != "Todos" and estado["recorrido"] not in descripciones:
            estado["recorrido"] = "Todos"
            filtro_recorrido_dropdown.value = None

    async def recargar():
        try:
            estado["inscripciones"] = await api_client.get_inscripciones_transporte()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de pasajeros: {err}")
        try:
            estado["recorridos"] = await api_client.get_recorridos()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de recorridos: {err}")
        actualizar_filtro_recorridos()
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_recorrido(e):
        estado["recorrido"] = filtro_recorrido_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_recorrido_dropdown.on_change = on_filtrar_recorrido

    # ==================== 5. DIÁLOGO NUEVO RECORRIDO ====================
    def abrir_nuevo_recorrido(e):
        descripcion_field = ft.TextField(
            label="Descripción del recorrido *",
            hint_text="Ej: Ruta Norte - La Liguria",
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            descripcion = (descripcion_field.value or "").strip()
            if not descripcion:
                error_text.value = "La descripción es obligatoria."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.create_recorrido({"descripcion": descripcion})
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear el recorrido."
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
            title=ft.Text("Nuevo Recorrido", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        "Registre la zona o ruta del servicio de transporte escolar.",
                        size=13,
                        color=MUTED,
                    ),
                    descripcion_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Crear Recorrido", bgcolor=TEAL, color=BG_WHITE, on_click=guardar
                ),
            ],
        )
        page.show_dialog(dlg)

    # ==================== 5b. DIÁLOGOS EDITAR / ELIMINAR RECORRIDO ====================
    def abrir_editar_recorrido(recorrido: dict):
        descripcion_field = ft.TextField(
            label="Descripción del recorrido *",
            value=recorrido.get("descripcion") or "",
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            descripcion = (descripcion_field.value or "").strip()
            if not descripcion:
                error_text.value = "La descripción es obligatoria."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.update_recorrido(
                    recorrido["id_recorrido"], {"descripcion": descripcion}
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al actualizar el recorrido."
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
                f"Editar Recorrido #{recorrido['id_recorrido']}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[descripcion_field, error_text],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Guardar Cambios",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=guardar_edicion,
                ),
            ],
        )
        page.show_dialog(dlg)

    def confirmar_eliminar_recorrido(recorrido: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def eliminar(e):
            try:
                await api_client.delete_recorrido(recorrido["id_recorrido"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo eliminar el recorrido."
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
            title=ft.Text("Eliminar Recorrido", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma eliminar el recorrido «{recorrido.get('descripcion')}»? "
                        "Solo es posible si no tiene pasajeros inscriptos.",
                        size=13,
                        color=TEXT_COLOR,
                    ),
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Eliminar", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=eliminar
                ),
            ],
        )
        page.show_dialog(dlg)

    # ==================== 6. DIÁLOGO INSCRIBIR ALUMNO ====================
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
        recorrido_field = ft.Dropdown(
            label="Recorrido *",
            width=380,
            options=[
                ft.dropdown.Option(
                    key=str(r["id_recorrido"]), text=r.get("descripcion", "-")
                )
                for r in estado["recorridos"]
            ],
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        if not alumnos:
            error_text.value = "⚠️ No hay alumnos activos disponibles para inscribir."
            error_text.visible = True
        elif not estado["recorridos"]:
            error_text.value = (
                "⚠️ No hay recorridos cargados. Cree un recorrido primero."
            )
            error_text.visible = True

        async def guardar(e):
            if not alumno_field.value or not recorrido_field.value:
                error_text.value = "Alumno y recorrido son obligatorios."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.inscribir_transporte(
                    {
                        "legajo_alumno": int(alumno_field.value),
                        "id_recorrido": int(recorrido_field.value),
                    }
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al inscribir al alumno en el transporte."
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
                "Inscribir Alumno al Transporte", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        "Seleccione el alumno y el recorrido que utilizará durante el ciclo lectivo.",
                        size=13,
                        color=MUTED,
                    ),
                    alumno_field,
                    recorrido_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Inscribir", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    btn_nuevo_recorrido.on_click = abrir_nuevo_recorrido
    btn_inscribir.on_click = abrir_inscribir_alumno

    render()

    # ==================== 7. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Servicio de Transporte Escolar",
        active_route="/admin/transporte",
        content_controls=[
            banner_holder,
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
        ],
    )
