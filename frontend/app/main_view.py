import flet as ft
from app.ui.pages.home import home_view

import flet as ft
from app.ui.components.navbar import create_navbar
from app.ui.components.footer import create_footer
from app.ui.pages.home import home_view
from app.ui.pages.quienes_somos import get_quienes_somos_view
from app.ui.pages.inscripciones import get_inscripcion_view
from app.ui.pages.noticias import get_noticias_view
from app.ui.pages.login import get_login_view
from app.ui.pages.niveles import get_niveles_view
from app.ui.pages.admin_dashboard import get_admin_dashboard_view
from app.ui.pages.admin_alumnos import get_admin_alumnos_view
from app.ui.pages.admin_alumno_form import get_admin_alumno_form_view
from app.ui.pages.admin_profesores import get_admin_profesores_view
from app.ui.pages.admin_profesor_form import get_admin_profesor_form_view
from app.ui.pages.admin_reportes import get_admin_reportes_view
from app.ui.pages.admin_deportes import get_admin_deportes_view
from app.ui.pages.admin_transporte import get_admin_transporte_view
from app.ui.pages.admin_comedor import get_admin_comedor_view
from app.ui.pages.admin_niveles import get_admin_niveles_view
from app.ui.pages.admin_cursos import get_admin_cursos_view
from app.ui.pages.admin_materias import get_admin_materias_view
from app.ui.pages.admin_horarios import get_admin_horarios_view
from app.ui.pages.admin_incripciones import get_admin_inscripciones_view
from app.ui.pages.admin_usuarios import get_admin_usuarios_view

from app.ui.pages.admin_reporte_alumnos_docentes import get_admin_reporte_alumnos_docentes_view
from app.ui.pages.admin_reporte_cursos_materias import get_admin_reporte_cursos_materias_view
from app.ui.pages.admin_reporte_deportes_avanzado import get_admin_reporte_deportes_avanzado_view
from app.ui.pages.admin_reporte_transporte_pasajeros import get_admin_reporte_transporte_pasajeros_view

async def main(page: ft.Page):
    page.title = "Educar para Transformar"
    page.padding = 0

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        ruta = (page.route or "/").rstrip("/")
        if not ruta:
            ruta = "/"

    # 1. RUTAS ADMINISTRATIVAS (Sin navbar ni footer público)
        if ruta == "/admin/dashboard":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_dashboard_view(page)],
                )
            )
            page.update()
            return

        elif ruta == "/admin/alumnos":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_alumnos_view(page)],
                )
            )
            page.update()
            return

        elif ruta == "/admin/alumnos/nuevo":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_alumno_form_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/profesores":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_profesores_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/profesores/nuevo":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_profesor_form_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/reportes":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_reportes_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/deportes": 
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_deportes_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/transporte":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_transporte_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/comedor":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_comedor_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/niveles":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_niveles_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/cursos":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_cursos_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/materias":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_materias_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/horarios":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_horarios_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/inscripciones":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_inscripciones_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/usuarios":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_usuarios_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/reporte-alumnos-docentes":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_reporte_alumnos_docentes_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/reporte-cursos-materias":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_reporte_cursos_materias_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/reporte-deportes-avanzado":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_reporte_deportes_avanzado_view(page)],
                )
            )
            page.update()
            return
        elif ruta == "/admin/reporte-transporte-pasajeros":
            page.views.append(
                ft.View(
                    route=ruta,
                    padding=0,
                    controls=[get_admin_reporte_transporte_pasajeros_view(page)],
                )
            )
            page.update()
            return


        # 2. RUTAS PÚBLICAS
        if ruta == "/quienes-somos":
            contenido_central = get_quienes_somos_view(page)
        elif ruta == "/inscripcion":
            contenido_central = get_inscripcion_view(page)
        elif ruta == "/noticias":
            contenido_central = get_noticias_view(page)
        elif ruta == "/niveles":
            contenido_central = get_niveles_view(page)
        elif ruta == "/portal":
            contenido_central = get_login_view(page)
        else:
            contenido_central = home_view(page)

        page.views.append(
            ft.View(
                route=ruta,
                padding=0,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    create_navbar(page, active_route=ruta),
                    *contenido_central,
                    create_footer(page),
                ],
            )
        )
    page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        page.route = top_view.route
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change(None)