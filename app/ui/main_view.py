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