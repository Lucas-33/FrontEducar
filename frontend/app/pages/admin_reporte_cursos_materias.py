import flet as ft

COLOR_TEAL_DARK = "#0B4F4F"
COLOR_TEAL_MED = "#0D6E6E"
COLOR_TEAL_LIGHT = "#E6F2F2"
COLOR_BG = "#F5F7F7"
COLOR_CARD_BG = "#FFFFFF"
COLOR_BORDER = "#EAE6E1"
COLOR_TEXT_MAIN = "#1E2A29"
COLOR_TEXT_MUTED = "#5C6B69"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"

def get_admin_reporte_cursos_materias_view(page: ft.Page) -> ft.Control:
    data_academica = [
        {"nivel": "Secundario", "curso": "1° Año A", "materia": "Matemática", "docente": "Prof. Laura Paez", "horas": "5 hs", "matricula": 32, "aprobados": "84%"},
        {"nivel": "Secundario", "curso": "1° Año A", "materia": "Biología", "docente": "Lic. Mario Rossi", "horas": "3 hs", "matricula": 32, "aprobados": "90%"},
        {"nivel": "Secundario", "curso": "4° Año Naturales", "materia": "Física Cuántica", "docente": "Prof. Carlos Menéndez", "horas": "4 hs", "matricula": 28, "aprobados": "75%"},
        {"nivel": "Primario", "curso": "3° Grado A", "materia": "Lengua y Expresión", "docente": "Prof. Ana Quiroga", "horas": "6 hs", "matricula": 25, "aprobados": "96%"},
        {"nivel": "Primario", "curso": "5° Grado B", "materia": "Ciencias Sociales", "docente": "Prof. Daniel Sosa", "horas": "4 hs", "matricula": 27, "aprobados": "88%"},
        {"nivel": "Inicial", "curso": "Sala 5 Años Verde", "materia": "Iniciación a la Lectura", "docente": "Lic. Carla Duarte", "horas": "4 hs", "matricula": 20, "aprobados": "100%"},
    ]

    dd_nivel = ft.Dropdown(
        label="Nivel Educativo",
        value="Todos",
        width=180,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Inicial"),
            ft.dropdown.Option("Primario"),
            ft.dropdown.Option("Secundario"),
        ],
    )

    tf_filtro = ft.TextField(
        label="Buscar por Curso, Materia o Docente",
        prefix_icon=ft.Icons.FILTER_LIST,
        expand=True,
    )

    table_data = ft.DataTable(
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=8,
        heading_row_color=COLOR_TEAL_LIGHT,
        columns=[
            ft.DataColumn(ft.Text("Nivel", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Curso / División", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Materia", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Docente Titular", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Carga", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Alumnos Inscriptos", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Tasa Aprobación", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
        ],
        rows=[],
    )

    def trigger_export(formato: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Exportando Planilla de Cursos y Materias en formato {formato}..."),
            bgcolor=COLOR_TEAL_DARK,
        )
        page.snack_bar.open = True
        page.update()

    def update_table(e=None):
        nivel_sel = dd_nivel.value
        busqueda = tf_filtro.value.strip().lower() if tf_filtro.value else ""

        rows = []
        for reg in data_academica:
            match_nivel = (nivel_sel == "Todos") or (reg["nivel"] == nivel_sel)
            match_busqueda = (
                busqueda in reg["curso"].lower()
                or busqueda in reg["materia"].lower()
                or busqueda in reg["docente"].lower()
            )

            if match_nivel and match_busqueda:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(reg["nivel"])),
                            ft.DataCell(ft.Text(reg["curso"], weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(reg["materia"], weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
                            ft.DataCell(ft.Text(reg["docente"])),
                            ft.DataCell(ft.Text(reg["horas"])),
                            ft.DataCell(ft.Text(f"{reg['matricula']} alumnos")),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(reg["aprobados"], size=12, color=COLOR_TEXT_MAIN, weight=ft.FontWeight.BOLD),
                                    bgcolor=COLOR_TEAL_LIGHT,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                )
                            ),
                        ]
                    )
                )
        table_data.rows = rows
        page.update()

    dd_nivel.on_change = update_table
    tf_filtro.on_change = update_table
    update_table()

    header_section = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Planillas de Cursos y Asignaturas", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ft.Text("Malla curricular institucional, asignaciones docentes y volúmenes de aula.", size=14, color=COLOR_TEXT_MUTED),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.ElevatedButton(
                        "Planilla Excel",
                        icon=ft.Icons.TABLE_VIEW,
                        style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS, color=COLOR_CARD_BG),
                        on_click=lambda _: trigger_export("Excel (.xlsx)"),
                    ),
                    ft.ElevatedButton(
                        "Imprimir PDF",
                        icon=ft.Icons.PRINT,
                        style=ft.ButtonStyle(bgcolor=COLOR_TEAL_DARK, color=COLOR_CARD_BG),
                        on_click=lambda _: trigger_export("PDF"),
                    ),
                ],
            ),
        ],
    )

    return ft.Container(
        bgcolor=COLOR_BG,
        expand=True,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                header_section,
                ft.Container(
                    bgcolor=COLOR_CARD_BG,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=10,
                    padding=16,
                    content=ft.Row(spacing=16, controls=[dd_nivel, tf_filtro]),
                ),
                ft.Container(
                    bgcolor=COLOR_CARD_BG,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=10,
                    padding=16,
                    content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[table_data]),
                ),
            ],
        ),
    )

if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Reporte Cursos y Materias"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.add(get_admin_reporte_cursos_materias_view(page))

    ft.run(main)