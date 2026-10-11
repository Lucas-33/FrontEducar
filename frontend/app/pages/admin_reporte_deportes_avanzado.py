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
COLOR_ALERT = "#EF4444"

def get_admin_reporte_deportes_avanzado_view(page: ft.Page) -> ft.Control:
    data_talleres = [
        {"deporte": "Fútbol", "nivel": "Primario", "horario": "Lun/Mié 16:30 - 18:00", "profesor": "Prof. Lucas Toledo", "inscriptos": 25, "cupo_max": 25, "aptos_al_dia": "24/25"},
        {"deporte": "Fútbol", "nivel": "Secundario", "horario": "Mar/Jue 17:00 - 18:30", "profesor": "Prof. Lucas Toledo", "inscriptos": 22, "cupo_max": 25, "aptos_al_dia": "22/22"},
        {"deporte": "Básquet", "nivel": "Secundario", "horario": "Lun/Mié 18:00 - 19:30", "profesor": "Prof. Marcos Paz", "inscriptos": 18, "cupo_max": 20, "aptos_al_dia": "16/18"},
        {"deporte": "Vóley", "nivel": "Primario", "horario": "Mar/Jue 16:30 - 17:45", "profesor": "Lic. Romina Luna", "inscriptos": 15, "cupo_max": 20, "aptos_al_dia": "15/15"},
        {"deporte": "Gimnasia Artística", "nivel": "Inicial", "horario": "Viernes 15:30 - 17:00", "profesor": "Lic. Romina Luna", "inscriptos": 12, "cupo_max": 15, "aptos_al_dia": "12/12"},
        {"deporte": "Natación", "nivel": "Primario", "horario": "Sábados 09:30 - 11:30", "profesor": "Prof. Lucas Toledo", "inscriptos": 20, "cupo_max": 20, "aptos_al_dia": "19/20"},
    ]

    dd_deporte = ft.Dropdown(
        label="Deporte",
        value="Todos",
        width=170,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Fútbol"),
            ft.dropdown.Option("Básquet"),
            ft.dropdown.Option("Vóley"),
            ft.dropdown.Option("Natación"),
            ft.dropdown.Option("Gimnasia Artística"),
        ],
    )

    dd_nivel = ft.Dropdown(
        label="Nivel Educativo",
        value="Todos",
        width=160,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Inicial"),
            ft.dropdown.Option("Primario"),
            ft.dropdown.Option("Secundario"),
        ],
    )

    dd_profesor = ft.Dropdown(
        label="Profesor Responsable",
        value="Todos",
        width=200,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Prof. Lucas Toledo"),
            ft.dropdown.Option("Prof. Marcos Paz"),
            ft.dropdown.Option("Lic. Romina Luna"),
        ],
    )

    table_data = ft.DataTable(
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=8,
        heading_row_color=COLOR_TEAL_LIGHT,
        columns=[
            ft.DataColumn(ft.Text("Disciplina", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Nivel", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Días y Horarios", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Profesor a Cargo", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Ocupación Cupo", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Apto Médico", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
        ],
        rows=[],
    )

    def trigger_export(formato: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Exportando Padrón Deportivo y Certificados ({formato})..."),
            bgcolor=COLOR_TEAL_DARK,
        )
        page.snack_bar.open = True
        page.update()

    def update_table(e=None):
        dep = dd_deporte.value
        niv = dd_nivel.value
        prof = dd_profesor.value

        rows = []
        for t in data_talleres:
            match_dep = (dep == "Todos") or (t["deporte"] == dep)
            match_niv = (niv == "Todos") or (t["nivel"] == niv)
            match_prof = (prof == "Todos") or (t["profesor"] == prof)

            if match_dep and match_niv and match_prof:
                ratio = t["inscriptos"] / t["cupo_max"]
                is_full = ratio >= 1.0

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(t["deporte"], weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(t["nivel"])),
                            ft.DataCell(ft.Text(t["horario"])),
                            ft.DataCell(ft.Text(t["profesor"])),
                            ft.DataCell(
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Text(f"{t['inscriptos']}/{t['cupo_max']}", weight=ft.FontWeight.W_500),
                                        ft.Container(
                                            content=ft.Text("LLENO" if is_full else "DISP.", size=10, color=COLOR_CARD_BG, weight=ft.FontWeight.BOLD),
                                            bgcolor=COLOR_ALERT if is_full else COLOR_SUCCESS,
                                            border_radius=3,
                                            padding=ft.padding.symmetric(horizontal=4, vertical=2),
                                        ),
                                    ],
                                )
                            ),
                            ft.DataCell(
                                ft.Text(t["aptos_al_dia"], color=COLOR_TEAL_MED, weight=ft.FontWeight.BOLD)
                            ),
                        ]
                    )
                )
        table_data.rows = rows
        page.update()

    dd_deporte.on_change = update_table
    dd_nivel.on_change = update_table
    dd_profesor.on_change = update_table
    update_table()

    header_section = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Matriz de Deportes y Talleres Extracurriculares", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ft.Text("Listados cruzados: Disciplina × Nivel × Franja Horaria × Docente.", size=14, color=COLOR_TEXT_MUTED),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.ElevatedButton(
                        "Planilla Excel",
                        icon=ft.Icons.TABLE_VIEW,
                        style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS, color=COLOR_CARD_BG),
                        on_click=lambda _: trigger_export("Excel"),
                    ),
                    ft.ElevatedButton(
                        "Reporte PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
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
                    content=ft.Row(
                        spacing=16,
                        wrap=True,
                        controls=[dd_deporte, dd_nivel, dd_profesor],
                    ),
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
        page.title = "Educar SGE - Reporte Avanzado Deportes"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.add(get_admin_reporte_deportes_avanzado_view(page))

    ft.run(main)