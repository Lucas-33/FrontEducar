import httpx
import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BG_PAGE_ALT,
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


def get_empleo_view(page: ft.Page) -> list[ft.Control]:
    """Retorna la vista de Oportunidades Laborales con postulación real vía API."""

    vacantes = [
        {"puesto": "Profesor/a de Nivel Secundario — Ciencias Exactas", "area": "Física y Química / Matemática", "jornada": "Jornada Completa", "sede": "Resistencia"},
        {"puesto": "Docente de Idioma Francés / Inglés", "area": "Departamento de Lenguas Extranjeras", "jornada": "Part-Time", "sede": "Resistencia"},
        {"puesto": "Enfermero/a Profesional Matriculado/a", "area": "Gabinete de Salud y Enfermería", "jornada": "Turno Mañana (07:30 a 14:00)", "sede": "Resistencia"},
        {"puesto": "Chofer para Micro Escolar (Licencia D2)", "area": "Servicio de Transporte Institucional", "jornada": "Jornada Extendida", "sede": "Resistencia"},
    ]

    def mostrar_aviso(mensaje: str):
        page.show_dialog(
            ft.SnackBar(ft.Text(mensaje, color="white"), bgcolor=TEAL)
        )

    # ==================== POSTULACIÓN A UNA VACANTE ESPECÍFICA ====================
    def abrir_dialogo_postulacion(vacante: dict):
        campo_nombre_v = ft.TextField(label="Nombre y Apellido *", border_color=BORDER_COLOR, focused_border_color=TEAL, text_size=14, border_radius=BORDER_RADIUS)
        campo_correo_v = ft.TextField(label="Correo Electrónico *", border_color=BORDER_COLOR, focused_border_color=TEAL, text_size=14, border_radius=BORDER_RADIUS)
        campo_telefono_v = ft.TextField(label="Teléfono de contacto", border_color=BORDER_COLOR, focused_border_color=TEAL, text_size=14, border_radius=BORDER_RADIUS)
        campo_mensaje_v = ft.TextField(label="Comentario (opcional)", border_color=BORDER_COLOR, focused_border_color=TEAL, text_size=14, border_radius=BORDER_RADIUS, multiline=True, min_lines=3)
        mensaje_error = ft.Text("", size=12, color="#EF4444")

        async def enviar_postulacion(e):
            mensaje_error.value = ""
            if not campo_nombre_v.value or not campo_correo_v.value:
                mensaje_error.value = "Complete su nombre y correo electrónico."
                page.update()
                return

            payload = {
                "nombre": campo_nombre_v.value.strip(),
                "correo": campo_correo_v.value.strip(),
                "telefono": (campo_telefono_v.value or "").strip() or None,
                "puesto": vacante["puesto"],
                "area": vacante["area"],
                "mensaje": (campo_mensaje_v.value or "").strip() or None,
            }
            try:
                await api_client.enviar_postulacion(payload)
            except httpx.HTTPStatusError:
                mensaje_error.value = "Revise los datos ingresados (nombre y correo son obligatorios)."
                page.update()
                return
            except Exception:
                mensaje_error.value = "No se pudo conectar con el servidor. Intente nuevamente."
                page.update()
                return

            page.pop_dialog()
            mostrar_aviso("¡Postulación enviada! Secretaría se comunicará a la brevedad.")

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text("Postularme a la vacante", size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
            content=ft.Column(
                spacing=14,
                width=420,
                tight=True,
                controls=[
                    ft.Text(vacante["puesto"], size=13, weight=ft.FontWeight.W_600, color=TEAL),
                    ft.Text(vacante["area"], size=12, color=MUTED),
                    campo_nombre_v,
                    campo_correo_v,
                    campo_telefono_v,
                    campo_mensaje_v,
                    mensaje_error,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.Button("Enviar Postulación", bgcolor=TEAL, color=BG_WHITE, on_click=enviar_postulacion),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    def item_vacante(v: dict) -> ft.Container:
        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            padding=20,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(v["puesto"], size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Text(v["area"], size=13, color=MUTED),
                                    ft.Text("•", size=13, color=MUTED),
                                    ft.Text(v["jornada"], size=13, weight=ft.FontWeight.W_500, color=ORANGE),
                                    ft.Text("•", size=13, color=MUTED),
                                    ft.Text(v["sede"], size=13, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                    ft.Button(
                        "POSTULARME",
                        bgcolor=TEAL_LIGHT,
                        color=TEAL_DARK,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                        on_click=lambda e, v=v: abrir_dialogo_postulacion(v),
                    ),
                ],
            ),
        )

    # ==================== FORMULARIO DE POSTULACIÓN ESPONTÁNEA ====================
    campo_nombre = ft.TextField(hint_text="Ej: María Eugenia Romero", border_color=BORDER_COLOR, focused_border_color=TEAL, height=CONTROL_HEIGHT, text_size=14, border_radius=BORDER_RADIUS)
    campo_correo = ft.TextField(hint_text="postulante@ejemplo.com", border_color=BORDER_COLOR, focused_border_color=TEAL, height=CONTROL_HEIGHT, text_size=14, border_radius=BORDER_RADIUS)
    campo_telefono = ft.TextField(hint_text="+54 362 4XXXXXX", border_color=BORDER_COLOR, focused_border_color=TEAL, height=CONTROL_HEIGHT, text_size=14, border_radius=BORDER_RADIUS)
    campo_area = ft.TextField(hint_text="Ej: Ciencias Biológicas, Conducción, Preceptoría", border_color=BORDER_COLOR, focused_border_color=TEAL, height=CONTROL_HEIGHT, text_size=14, border_radius=BORDER_RADIUS)

    def campo_form(label: str, control: ft.Control, col_span: int = 6) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": col_span},
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    control,
                ],
            ),
        )

    async def enviar_antecedentes(e):
        if not campo_nombre.value or not campo_correo.value or not campo_area.value:
            page.show_dialog(
                ft.SnackBar(
                    ft.Text("Complete nombre, correo y área de especialidad.", color="white"),
                    bgcolor="#EF4444",
                )
            )
            return

        payload = {
            "nombre": campo_nombre.value.strip(),
            "correo": campo_correo.value.strip(),
            "telefono": (campo_telefono.value or "").strip() or None,
            "puesto": "Postulación espontánea",
            "area": campo_area.value.strip(),
            "mensaje": None,
        }
        try:
            await api_client.enviar_postulacion(payload)
        except httpx.HTTPStatusError:
            page.show_dialog(
                ft.SnackBar(
                    ft.Text("Revise los datos ingresados e intente nuevamente.", color="white"),
                    bgcolor="#EF4444",
                )
            )
            return
        except Exception:
            page.show_dialog(
                ft.SnackBar(
                    ft.Text("No se pudo conectar con el servidor. Intente más tarde.", color="white"),
                    bgcolor="#EF4444",
                )
            )
            return

        campo_nombre.value = ""
        campo_correo.value = ""
        campo_telefono.value = ""
        campo_area.value = ""
        page.update()
        mostrar_aviso("¡Antecedentes enviados! Su perfil quedó registrado para futuras vacantes.")

    form_postulacion = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Formulario de Postulación Espontánea", size=22, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text("Si su perfil no coincide con las búsquedas abiertas, puede dejarnos sus antecedentes para futuras vacantes.", size=13, color=MUTED),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=16,
                    controls=[
                        campo_form("Nombre y Apellido *", campo_nombre, 6),
                        campo_form("Correo Electrónico *", campo_correo, 6),
                        campo_form("Teléfono de contacto", campo_telefono, 6),
                        campo_form("Área / Especialidad Docente o Técnica *", campo_area, 6),
                        ft.Container(
                            col={"sm": 12, "md": 12},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Adjuntar CV (PDF) — opcional", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.Container(
                                        height=CONTROL_HEIGHT,
                                        bgcolor=BG_PAGE_ALT,
                                        border=ft.Border.all(1, BORDER_COLOR),
                                        border_radius=BORDER_RADIUS,
                                        padding=ft.Padding(12, 0, 12, 0),
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text("Podrá enviar su curriculum al correo de contacto indicado en la respuesta.", size=13, color=MUTED),
                                                ft.Icon(ft.Icons.UPLOAD_FILE_OUTLINED, size=18, color=TEAL),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Button(
                    "ENVIAR ANTECEDENTES",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    height=CONTROL_HEIGHT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                    on_click=enviar_antecedentes,
                ),
            ],
        ),
    )

    main_section = ft.Container(
        bgcolor=BG_PAGE_ALT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.Column(
            spacing=48,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("TRABAJA CON NOSOTROS", size=13, weight=ft.FontWeight.BOLD, color=ORANGE, text_align=ft.TextAlign.CENTER),
                        ft.Text("Oportunidades de Empleo", size=36, weight=ft.FontWeight.BOLD, color=TEAL_DARK, text_align=ft.TextAlign.CENTER),
                        ft.Text("Sumate al equipo de profesionales comprometidos con transformar la educación en el Chaco.", size=15, color=MUTED, text_align=ft.TextAlign.CENTER),
                    ],
                ),
                ft.Column(spacing=12, controls=[item_vacante(v) for v in vacantes]),
                form_postulacion,
            ],
        ),
    )

    return [main_section]
