import flet as ft

from mobile.api_client import mobile_api
from mobile.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def get_servicios_page(page: ft.Page) -> list[ft.Control]:
    """Pantalla móvil de Gestión de Servicios (Comedor, Transporte y Deportes)."""

    id_padre = getattr(page, "auth_padre_id", None)
    lista_servicios_col = ft.Column(spacing=14)

    async def cargar_servicios():
        try:
            if not id_padre:
                lista_servicios_col.controls = [
                    ft.Text(
                        "Inicie sesión con un usuario tutor para gestionar servicios.",
                        size=12,
                        color=MUTED,
                    )
                ]
                page.update()
                return

            hijos = await mobile_api.get_hijos(id_padre)
            recorridos = await mobile_api.get_recorridos_transporte()
            recorridos_map = {
                r["id_recorrido"]: r.get("descripcion", "-") for r in recorridos
            }

            insc_transporte = await mobile_api.get_inscripciones_transporte()
            insc_comedor = await mobile_api.get_inscripciones_comedor()
            insc_deportes = await mobile_api.get_inscripciones_deporte()
            deportes = await mobile_api.get_deportes()
            deportes_map = {d["id_deporte"]: d.get("nombre", "-") for d in deportes}

            tarjetas = []
            for h in hijos:
                legajo = h.get("legajo")
                nombre = f"{h.get('apellido', '')}, {h.get('nombre', '')}"

                # Transporte
                trans = next(
                    (
                        t
                        for t in insc_transporte
                        if t.get("legajo_alumno") == legajo
                        and t.get("estado") == "ACTIVO"
                    ),
                    None,
                )
                # Comedor
                comed = next(
                    (
                        c
                        for c in insc_comedor
                        if c.get("legajo_alumno") == legajo
                        and c.get("estado") == "ACTIVO"
                    ),
                    None,
                )
                # Deportes
                deps_alumno = [
                    d
                    for d in insc_deportes
                    if d.get("legajo_alumno") == legajo and d.get("estado") == "ACTIVO"
                ]

                async def toggle_comedor(e, leg=legajo, activo=bool(comed)):
                    try:
                        if activo:
                            await mobile_api.baja_comedor(leg)
                        else:
                            await mobile_api.inscribir_comedor({"legajo_alumno": leg})
                        await cargar_servicios()
                    except Exception as ex:
                        snack = ft.SnackBar(
                            ft.Text(f"Error: {ex}"), bgcolor=BADGE_RED_TXT
                        )
                        page.overlay.append(snack)
                        snack.open = True
                        page.update()

                tarjeta_hijo = ft.Container(
                    bgcolor=BG_WHITE,
                    padding=16,
                    border_radius=CARD_RADIUS,
                    border=ft.Border.all(1, BORDER_COLOR),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Container(
                                                width=32,
                                                height=32,
                                                border_radius=16,
                                                bgcolor=TEAL_LIGHT,
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Icon(
                                                    ft.Icons.SCHOOL,
                                                    color=TEAL_DARK,
                                                    size=16,
                                                ),
                                            ),
                                            ft.Column(
                                                spacing=0,
                                                controls=[
                                                    ft.Text(
                                                        nombre,
                                                        size=14,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=TEXT_COLOR,
                                                    ),
                                                    ft.Text(
                                                        f"Legajo #{legajo}",
                                                        size=11,
                                                        color=MUTED,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                            # Ítem Comedor
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.RESTAURANT_OUTLINED,
                                                color=ORANGE,
                                                size=18,
                                            ),
                                            ft.Column(
                                                spacing=1,
                                                controls=[
                                                    ft.Text(
                                                        "Comedor Escolar",
                                                        size=12,
                                                        weight=ft.FontWeight.W_600,
                                                        color=TEXT_COLOR,
                                                    ),
                                                    ft.Text(
                                                        "Almuerzo y colación diaria",
                                                        size=10,
                                                        color=MUTED,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Switch(
                                        value=bool(comed),
                                        active_color=TEAL,
                                        on_change=toggle_comedor,
                                    ),
                                ],
                            ),
                            # Ítem Transporte
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.DIRECTIONS_BUS_OUTLINED,
                                                color=TEAL,
                                                size=18,
                                            ),
                                            ft.Column(
                                                spacing=1,
                                                controls=[
                                                    ft.Text(
                                                        "Transporte Institucional",
                                                        size=12,
                                                        weight=ft.FontWeight.W_600,
                                                        color=TEXT_COLOR,
                                                    ),
                                                    ft.Text(
                                                        recorridos_map.get(
                                                            trans.get("id_recorrido"),
                                                            "Activo",
                                                        )
                                                        if trans
                                                        else "No contratado",
                                                        size=10,
                                                        color=ONLINE_GREEN
                                                        if trans
                                                        else MUTED,
                                                        weight=ft.FontWeight.BOLD
                                                        if trans
                                                        else ft.FontWeight.NORMAL,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Container(
                                        bgcolor=BADGE_GREEN_BG if trans else BG_PAGE,
                                        padding=ft.Padding(8, 3, 8, 3),
                                        border_radius=8,
                                        content=ft.Text(
                                            "ACTIVO" if trans else "INACTIVO",
                                            size=9,
                                            weight=ft.FontWeight.BOLD,
                                            color=BADGE_GREEN_TXT if trans else MUTED,
                                        ),
                                    ),
                                ],
                            ),
                            # Ítem Deportes
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.FITNESS_CENTER_OUTLINED,
                                                color=TEAL_DARK,
                                                size=18,
                                            ),
                                            ft.Text(
                                                "Actividades Deportivas:",
                                                size=12,
                                                weight=ft.FontWeight.W_600,
                                                color=TEXT_COLOR,
                                            ),
                                        ],
                                    ),
                                    ft.Text(
                                        f"{len(deps_alumno)}/2 deportes inscriptos"
                                        if deps_alumno
                                        else "Sin actividades extracurriculares",
                                        size=11,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
                tarjetas.append(tarjeta_hijo)

            lista_servicios_col.controls = (
                tarjetas
                if tarjetas
                else [
                    ft.Text(
                        "No hay alumnos asociados a este tutor.", size=12, color=MUTED
                    )
                ]
            )

        except Exception as ex:
            lista_servicios_col.controls = [
                ft.Text(
                    f"Error al cargar servicios: {ex}", size=12, color=BADGE_RED_TXT
                )
            ]

        page.update()

    page.run_task(cargar_servicios)

    return [
        ft.Text(
            "Servicios Escolares", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK
        ),
        ft.Text(
            "Gestioná el comedor, transporte y deportes contratados para tus hijos:",
            size=12,
            color=MUTED,
        ),
        lista_servicios_col,
    ]
