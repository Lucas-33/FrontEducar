import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.portal_layout import portal_layout


def get_padre_deportes_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de Inscripción Deportiva con control estricto de máximo 2 deportes y sin conflicto horario."""

    catalogo_deportes = [
        {"id": 1, "nombre": "Natación Climatizada", "profesor": "Prof. Vargas, Esteban", "dias": "Lun y Mié", "horario": "16:30 - 18:00 hs", "lugar": "Natatorio Olímpico", "seleccionado": True},
        {"id": 2, "nombre": "Fútbol Campo", "profesor": "Prof. Acuña, Germán", "dias": "Mar y Jue", "horario": "16:30 - 18:00 hs", "lugar": "Cancha 1 Sintético", "seleccionado": True},
        {"id": 3, "nombre": "Atletismo de Pista", "profesor": "Prof. Ríos, Marcos", "dias": "Lun y Mié", "horario": "15:00 - 16:30 hs", "lugar": "Pista Profesional", "seleccionado": False},
        {"id": 4, "nombre": "Artes Marciales (Taekwondo)", "profesor": "Sensei Navarro, Hiroshi", "dias": "Viernes", "horario": "16:30 - 18:30 hs", "lugar": "Dojo Cubierto", "seleccionado": False},
        {"id": 5, "nombre": "Básquetbol", "profesor": "Prof. Pérez, Daniel", "dias": "Mar y Jue", "horario": "15:00 - 16:30 hs", "lugar": "Gimnasio Cubierto", "seleccionado": False},
        {"id": 6, "nombre": "Danza Contemporánea", "profesor": "Prof. Sosa, Valeria", "dias": "Mié y Vie", "horario": "16:30 - 18:00 hs", "lugar": "Salón de Expresión", "seleccionado": False},
        {"id": 7, "nombre": "Vóleibol Formativo", "profesor": "Prof. López, Andrea", "dias": "Mar y Jue", "horario": "16:30 - 18:00 hs", "lugar": "Gimnasio Cubierto 2", "seleccionado": False},
        {"id": 8, "nombre": "Ajedrez Estratégico", "profesor": "Maestro Blanco, Jorge", "dias": "Lunes", "horario": "16:30 - 18:00 hs", "lugar": "Biblioteca Central", "seleccionado": False},
    ]

    mensaje_alerta = ft.Text("", size=13, weight=ft.FontWeight.W_600)
    contador_texto = ft.Text("2 de 2 disciplinas seleccionadas", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)

    def actualizar_seleccion(e, deporte):
        seleccionados = [d for d in catalogo_deportes if d["seleccionado"]]

        if not deporte["seleccionado"]:
            # Regla: Máximo 2 deportes simultáneos[cite: 6]
            if len(seleccionados) >= 2:
                mensaje_alerta.value = "⚠️ Límite alcanzado: Cada estudiante puede inscribirse en hasta dos deportes simultáneamente."
                mensaje_alerta.color = ORANGE
                e.control.value = False
                e.control.update()
                mensaje_alerta.update()
                return

            # Regla: Control de conflicto de horarios[cite: 6]
            for s in seleccionados:
                if s["dias"] == deporte["dias"] and s["horario"] == deporte["horario"]:
                    mensaje_alerta.value = f"⚠️ Conflicto de horario: {deporte['nombre']} se superpone con {s['nombre']} ({s['dias']} {s['horario']})."
                    mensaje_alerta.color = "#EF4444"
                    e.control.value = False
                    e.control.update()
                    mensaje_alerta.update()
                    return

            deporte["seleccionado"] = True
            mensaje_alerta.value = f"Inscripción actualizada para {deporte['nombre']}."
            mensaje_alerta.color = TEAL
        else:
            deporte["seleccionado"] = False
            mensaje_alerta.value = f"Se canceló la selección de {deporte['nombre']}."
            mensaje_alerta.color = MUTED

        cant = len([d for d in catalogo_deportes if d["seleccionado"]])
        contador_texto.value = f"{cant} de 2 disciplinas seleccionadas"
        contador_texto.update()
        mensaje_alerta.update()

    def tarjeta_deporte(d: dict) -> ft.Container:
        checkbox = ft.Checkbox(
            value=d["seleccionado"],
            active_color=TEAL,
            on_change=lambda e: actualizar_seleccion(e, d),
        )
        return ft.Container(
            col={"sm": 12, "md": 6},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        expand=True,
                        controls=[
                            ft.Text(d["nombre"], size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(d["profesor"], size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.SCHEDULE, size=14, color=ORANGE),
                                    ft.Text(f"{d['dias']} · {d['horario']}", size=12, color=MUTED),
                                ],
                            ),
                            ft.Text(f"Lugar: {d['lugar']}", size=11, color=MUTED),
                        ],
                    ),
                    checkbox,
                ],
            ),
        )

    encabezado_info = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                        ft.Text("Alumno: Santiago Almirón (5to Año B) · Máximo 2 disciplinas deportivas permitidas", size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                    ],
                ),
                contador_texto,
            ],
        ),
    )

    return portal_layout(
        page=page,
        titulo="Inscripción y Horarios Deportivos",
        active_route="/portal/padre/deportes",
        rol="Padre",
        content_controls=[
            encabezado_info,
            mensaje_alerta,
            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[tarjeta_deporte(d) for d in catalogo_deportes],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.Button(
                        "GUARDAR ASIGNACIÓN DE DEPORTES",
                        bgcolor=TEAL,
                        color="white",
                        height=CONTROL_HEIGHT,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                        on_click=lambda _: None,
                    ),
                ],
            ),
        ],
    )