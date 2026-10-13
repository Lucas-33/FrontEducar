import flet as ft

# Componentes públicos
from frontend.app.components.footer import create_footer
from frontend.app.components.navbar import create_navbar

# Páginas públicas
from frontend.app.pages.bienestar_estudiantil import get_bienestar_estudiantil_view
from frontend.app.pages.contacto import get_contacto_view
from frontend.app.pages.empleo import get_empleo_view
from frontend.app.pages.home import home_view
from frontend.app.pages.inscripciones import get_inscripcion_view
from frontend.app.pages.login import get_login_view
from frontend.app.pages.niveles import get_niveles_view
from frontend.app.pages.noticias import get_noticias_view
from frontend.app.pages.opiniones import get_opiniones_view
from frontend.app.pages.quienes_somos import get_quienes_somos_view

# Portal Familias / Padres
from frontend.app.pages.padre_dashboard import get_padre_dashboard_view
from frontend.app.pages.padre_deportes import get_padre_deportes_view
from frontend.app.pages.padre_docentes import get_padre_docentes_view
from frontend.app.pages.padre_servicios import get_padre_servicios_view
from frontend.app.pages.padre_inscripcion import get_padre_inscripcion_view

# Páginas administrativas
from frontend.app.pages.admin_alumno_form import get_admin_alumno_form_view
from frontend.app.pages.admin_alumnos import get_admin_alumnos_view
from frontend.app.pages.admin_comedor import get_admin_comedor_view
from frontend.app.pages.admin_cursos import get_admin_cursos_view
from frontend.app.pages.admin_dashboard import get_admin_dashboard_view
from frontend.app.pages.admin_deportes import get_admin_deportes_view
from frontend.app.pages.admin_horarios import get_admin_horarios_view
from frontend.app.pages.admin_inscripciones import get_admin_inscripciones_view
from frontend.app.pages.admin_materias import get_admin_materias_view
from frontend.app.pages.admin_niveles import get_admin_niveles_view
from frontend.app.pages.admin_profesor_form import get_admin_profesor_form_view
from frontend.app.pages.admin_profesores import get_admin_profesores_view
from frontend.app.pages.admin_reportes import get_admin_reportes_view
from frontend.app.pages.admin_transporte import get_admin_transporte_view
from frontend.app.pages.admin_usuarios import get_admin_usuarios_view


# Portal Docentes
from frontend.app.pages.docente_alumnos import get_docente_alumnos_view
from frontend.app.pages.docente_dashboard import get_docente_dashboard_view
from frontend.app.pages.docente_deportes import get_docente_deportes_view
from frontend.app.pages.docente_materias import get_docente_materias_view 

# Portal Alumno / Estudiante
from frontend.app.pages.alumno_dashboard import get_alumno_dashboard_view
from frontend.app.pages.alumno_deportes import get_alumno_deportes_view
from frontend.app.pages.alumno_materias import get_alumno_materias_view
from frontend.app.pages.alumno_servicios import get_alumno_servicios_view

# Reportes
from frontend.app.pages.admin_reporte_alumnos_docentes import (
    get_admin_reporte_alumnos_docentes_view,
)
from frontend.app.pages.admin_reporte_cursos_materias import (
    get_admin_reporte_cursos_materias_view,
)
from frontend.app.pages.admin_reporte_deportes_avanzado import (
    get_admin_reporte_deportes_avanzado_view,
)
from frontend.app.pages.admin_reporte_transporte_pasajeros import (
    get_admin_reporte_transporte_pasajeros_view,
)


async def main(page: ft.Page):
    page.title = "Educar para Transformar"
    page.padding = 0

    async def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        ruta = (page.route or "/").rstrip("/")
        if not ruta:
            ruta = "/"

        # ==================== 1. RUTAS DEL PORTAL FAMILIAS ====================
        if ruta == "/portal/padre/dashboard":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_dashboard_view(page)]))
            page.update()
            return
        elif ruta == "/portal/padre/deportes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_deportes_view(page)]))
            page.update()
            return
        elif ruta == "/portal/padre/servicios":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_servicios_view(page)]))
            page.update()
            return
        elif ruta == "/portal/padre/docentes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_docentes_view(page)]))
            page.update()
            return

        # ==================== 2. RUTAS ADMINISTRATIVAS ====================
        if ruta == "/admin/dashboard":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_dashboard_view(page)]))
            page.update()
            return
        elif ruta == "/admin/alumnos":
            vista_alumnos = await get_admin_alumnos_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_alumnos]))
            page.update()
            return
        elif ruta == "/admin/alumnos/nuevo":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_alumno_form_view(page)]))
            page.update()
            return
        elif ruta == "/admin/profesores":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_profesores_view(page)]))
            page.update()
            return
        elif ruta == "/admin/profesores/nuevo":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_profesor_form_view(page)]))
            page.update()
            return
        elif ruta == "/admin/reportes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_reportes_view(page)]))
            page.update()
            return
        elif ruta == "/admin/deportes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_deportes_view(page)]))
            page.update()
            return
        elif ruta == "/admin/transporte":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_transporte_view(page)]))
            page.update()
            return
        elif ruta == "/admin/comedor":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_comedor_view(page)]))
            page.update()
            return
        elif ruta == "/admin/niveles":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_niveles_view(page)]))
            page.update()
            return
        elif ruta == "/admin/cursos":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_cursos_view(page)]))
            page.update()
            return
        elif ruta == "/admin/materias":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_materias_view(page)]))
            page.update()
            return
        elif ruta == "/admin/horarios":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_horarios_view(page)]))
            page.update()
            return
        elif ruta == "/admin/inscripciones":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_inscripciones_view(page)]))
            page.update()
            return
        elif ruta == "/admin/usuarios":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_usuarios_view(page)]))
            page.update()
            return
        elif ruta == "/admin/reporte-alumnos-docentes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_reporte_alumnos_docentes_view(page)]))
            page.update()
            return
        elif ruta == "/admin/reporte-cursos-materias":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_reporte_cursos_materias_view(page)]))
            page.update()
            return
        elif ruta == "/admin/reporte-deportes-avanzado":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_reporte_deportes_avanzado_view(page)]))
            page.update()
            return
        elif ruta == "/admin/reporte-transporte-pasajeros":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_admin_reporte_transporte_pasajeros_view(page)]))
            page.update()
            return
        # ==================== 1. RUTAS DEL PORTAL FAMILIAS ====================
        if ruta == "/portal/padre/dashboard":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_dashboard_view(page)]))
            page.update()
            return
        elif ruta == "/portal/padre/inscripcion":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_inscripcion_view(page)]))
            page.update()
            return
        elif ruta == "/portal/padre/deportes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_deportes_view(page)]))
            page.update()
            return
        elif ruta == "/portal/padre/servicios":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_servicios_view(page)]))
            page.update()
            return
        elif ruta == "/portal/padre/docentes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_padre_docentes_view(page)]))
            page.update()
            return
        # ==================== 2. RUTAS DEL PORTAL DOCENTE ====================
        if ruta == "/portal/docente/dashboard":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_docente_dashboard_view(page)]))
            page.update()
            return
        elif ruta == "/portal/docente/materias":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_docente_materias_view(page)]))
            page.update()
            return
        elif ruta == "/portal/docente/alumnos":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_docente_alumnos_view(page)]))
            page.update()
            return
        elif ruta == "/portal/docente/deportes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_docente_deportes_view(page)]))
            page.update()
            return
        # ==================== 3. RUTAS DEL PORTAL ESTUDIANTE ====================
        if ruta == "/portal/alumno/dashboard":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_alumno_dashboard_view(page)]))
            page.update()
            return
        elif ruta == "/portal/alumno/materias":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_alumno_materias_view(page)]))
            page.update()
            return
        elif ruta == "/portal/alumno/deportes":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_alumno_deportes_view(page)]))
            page.update()
            return
        elif ruta == "/portal/alumno/servicios":
            page.views.append(ft.View(route=ruta, padding=0, controls=[get_alumno_servicios_view(page)]))
            page.update()
            return

            
            
        # ==================== 3. RUTAS PÚBLICAS INSTITUCIONALES ====================
        if ruta == "/quienes-somos":
            contenido_central = get_quienes_somos_view(page)
        elif ruta == "/inscripcion":
            contenido_central = get_inscripcion_view(page)
        elif ruta == "/noticias":
            contenido_central = get_noticias_view(page)
        elif ruta == "/niveles":
            contenido_central = get_niveles_view(page)
        elif ruta == "/bienestar-estudiantil":
            contenido_central = get_bienestar_estudiantil_view(page)
        elif ruta == "/opiniones":
            contenido_central = get_opiniones_view(page)
        elif ruta == "/empleo":
            contenido_central = get_empleo_view(page)
        elif ruta == "/contacto":
            contenido_central = get_contacto_view(page)
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

    await route_change(None)