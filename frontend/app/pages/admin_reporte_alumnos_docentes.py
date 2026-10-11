import flet as ft

# Tokens de Diseño
COLOR_TEAL_DARK = "#0B4F4F"
COLOR_TEAL_MED = "#0D6E6E"
COLOR_TEAL_LIGHT = "#E6F2F2"
COLOR_BG = "#F5F7F7"
COLOR_CARD_BG = "#FFFFFF"
COLOR_BORDER = "#EAE6E1"
COLOR_TEXT_MAIN = "#1E2A29"
COLOR_TEXT_MUTED = "#5C6B69"
COLOR_SUCCESS = "#10B981"
COLOR_ACCENT = "#D97736"

def get_admin_reporte_alumnos_docentes_view(page: ft.Page) -> ft.Control:
    # Datos de demostración
    data_alumnos = [
        {"legajo": "AL-2024-001", "nombre": "Sofía Martínez", "tipo": "Alumno", "detalle": "4° Año A - Secundaria", "estado": "Regular", "promedio": "8.85"},
        {"legajo": "AL-2024-002", "nombre": "Mateo Benítez", "tipo": "Alumno", "detalle": "2° Grado B - Primaria", "estado": "Regular", "promedio": "9.20"},
        {"legajo": "AL-2023-104", "nombre": "Valentina Gómez", "tipo": "Alumno", "detalle": "Sala 5 Años - Inicial", "estado": "Regular", "promedio": "S/C"},
    ]

    data_docentes = [
        {"legajo": "DOC-102", "nombre": "Prof. Carlos Menéndez", "tipo": "Docente", "detalle": "Física y Química (18 hs)", "estado": "Activo", "promedio": "Titular"},
        {"legajo": "DOC-108", "nombre": "Lic. Mariana Vega", "tipo": "Docente", "detalle": "Lengua y Literatura (24 hs)", "estado": "Activo", "promedio": "Titular"},
        {"legajo": "DOC-115", "nombre": "Prof. Lucas Toledo", "tipo": "Docente", "detalle": "Ed. Física (12 hs)", "estado": "Licencia", "promedio": "Suplente"},
    ]

    # Controles de Filtro
    dd_entidad = ft.Dropdown(
        label="Tipo de Entidad",
        value="Todos",
        width=200,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Alumnos"),
            ft.dropdown.Option("Docentes"),
        ],
    )

    tf_search = ft.TextField(
        label="Buscar por Legajo o Nombre",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
    )

    dd_estado = ft.Dropdown(
        label="Estado",
        value="Todos",
        width=180,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Regular / Activo"),
            ft.dropdown.Option("Licencia / Inactivo"),
        ],
    )

    table_data = ft.DataTable(
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=8,
        heading_row_color=COLOR_TEAL_LIGHT,
        columns=[
            ft.DataColumn(ft.Text("Legajo", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Curso / Carga Horaria", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Régimen / Prom.", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
        ],
        rows=[],
    )

    def trigger_export(formato: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Exportando Reporte de Alumnos/Docentes en formato {formato}..."),
            bgcolor=COLOR_TEAL_DARK,
        )
        page.snack_bar.open = True
        page.update()

    def update_table(e=None):
        filtro_tipo = dd_entidad.value
        filtro_busqueda = tf_search.value.strip().lower() if tf_search.value else ""
        filtro_estado = dd_estado.value

        pool = []
        if filtro_tipo in ["Todos", "Alumnos"]:
            pool.extend(data_alumnos)
        if filtro_tipo in ["Todos", "Docentes"]:
            pool.extend(data_docentes)

        rows = []
        for item in pool:
            match_search = (filtro_busqueda in item["nombre"].lower()) or (filtro_busqueda in item["legajo"].lower())
            
            match_estado = True
            if filtro_estado == "Regular / Activo":
                match_estado = item["estado"] in ["Regular", "Activo"]
            elif filtro_estado == "Licencia / Inactivo":
                match_estado = item["estado"] in ["Licencia", "Inactivo"]

            if match_search and match_estado:
                badge_color = COLOR_SUCCESS if item["estado"] in ["Regular", "Activo"] else COLOR_ACCENT
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item["legajo"], weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(item["nombre"])),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(item["tipo"], size=12, color=COLOR_CARD_BG),
                                    bgcolor=COLOR_TEAL_MED if item["tipo"] == "Docente" else COLOR_TEAL_DARK,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                )
                            ),
                            ft.DataCell(ft.Text(item["detalle"])),
                            ft.DataCell(ft.Text(item["promedio"])),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(item["estado"], size=12, color=badge_color, weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(1, badge_color),
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                )
                            ),
                        ]
                    )
                )
        table_data.rows = rows
        page.update()

    dd_entidad.on_change = update_table
    tf_search.on_change = update_table
    dd_estado.on_change = update_table

    update_table()

    header_section = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Reportes Institucionales: Alumnos y Docentes", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ft.Text("Padrón unificado de nómina directiva, legajos y condición académica/laboral.", size=14, color=COLOR_TEXT_MUTED),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.ElevatedButton(
                        "Exportar Excel",
                        icon=ft.Icons.TABLE_VIEW,
                        style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS, color=COLOR_CARD_BG),
                        on_click=lambda _: trigger_export("Excel (.xlsx)"),
                    ),
                    ft.ElevatedButton(
                        "Exportar PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        style=ft.ButtonStyle(bgcolor=COLOR_TEAL_DARK, color=COLOR_CARD_BG),
                        on_click=lambda _: trigger_export("PDF"),
                    ),
                ],
            ),
        ],
    )

    filters_card = ft.Container(
        bgcolor=COLOR_CARD_BG,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=10,
        padding=16,
        content=ft.Row(
            spacing=16,
            controls=[dd_entidad, tf_search, dd_estado],
        ),
    )

    table_container = ft.Container(
        bgcolor=COLOR_CARD_BG,
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=10,
        padding=16,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[table_data],
        ),
    )

    return ft.Container(
        bgcolor=COLOR_BG,
        expand=True,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                header_section,
                filters_card,
                table_container,
            ],
        ),
    )

if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Reporte Alumnos y Docentes"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.add(get_admin_reporte_alumnos_docentes_view(page))

    ft.run(main)