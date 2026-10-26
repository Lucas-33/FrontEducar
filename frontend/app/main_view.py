import flet as ft

# Componentes públicos
from frontend.app.components.footer import create_footer
from frontend.app.components.navbar import create_navbar

# Páginas administrativas
from frontend.app.pages.admin_alumno_form import get_admin_alumno_form_view
from frontend.app.pages.admin_alumnos import get_admin_alumnos_view
from frontend.app.pages.admin_comedor import get_admin_comedor_view

# Páginas nuevas (seguridad, comunidad y notas)
from frontend.app.pages.admin_comunidad import get_admin_comunidad_view
from frontend.app.pages.admin_cursos import get_admin_cursos_view
from frontend.app.pages.admin_dashboard import get_admin_dashboard_view
from frontend.app.pages.admin_deportes import get_admin_deportes_view
from frontend.app.pages.admin_horarios import get_admin_horarios_view
from frontend.app.pages.admin_inscripciones import get_admin_inscripciones_view
from frontend.app.pages.admin_materias import get_admin_materias_view
from frontend.app.pages.admin_niveles import get_admin_niveles_view
from frontend.app.pages.admin_profesor_form import get_admin_profesor_form_view
from frontend.app.pages.admin_profesores import get_admin_profesores_view

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
from frontend.app.pages.admin_reportes import get_admin_reportes_view
from frontend.app.pages.admin_transporte import get_admin_transporte_view
from frontend.app.pages.admin_usuarios import get_admin_usuarios_view

# Portal Alumno / Estudiante
from frontend.app.pages.alumno_dashboard import get_alumno_dashboard_view
from frontend.app.pages.alumno_deportes import get_alumno_deportes_view
from frontend.app.pages.alumno_materias import get_alumno_materias_view
from frontend.app.pages.alumno_notas import get_alumno_notas_view
from frontend.app.pages.alumno_servicios import get_alumno_servicios_view

# Páginas públicas
from frontend.app.pages.bienestar_estudiantil import get_bienestar_estudiantil_view
from frontend.app.pages.contacto import get_contacto_view

# Portal Docentes
from frontend.app.pages.docente_alumnos import get_docente_alumnos_view
from frontend.app.pages.docente_dashboard import get_docente_dashboard_view
from frontend.app.pages.docente_deportes import get_docente_deportes_view
from frontend.app.pages.docente_materias import get_docente_materias_view
from frontend.app.pages.docente_notas import get_docente_notas_view
from frontend.app.pages.empleo import get_empleo_view
from frontend.app.pages.home import home_view
from frontend.app.pages.inscripciones import get_inscripcion_view
from frontend.app.pages.login import get_login_view
from frontend.app.pages.niveles import get_niveles_view
from frontend.app.pages.noticias import get_noticias_view
from frontend.app.pages.opiniones import get_opiniones_view

# Portal Familias / Padres
from frontend.app.pages.padre_dashboard import get_padre_dashboard_view
from frontend.app.pages.padre_deportes import get_padre_deportes_view
from frontend.app.pages.padre_docentes import get_padre_docentes_view
from frontend.app.pages.padre_inscripcion import get_padre_inscripcion_view
from frontend.app.pages.padre_notas import get_padre_notas_view
from frontend.app.pages.padre_servicios import get_padre_servicios_view
from frontend.app.pages.quienes_somos import get_quienes_somos_view

# Mapa de rol normalizado -> sección de rutas que le corresponde
SECCION_POR_ROL = {
    "ADMIN": "admin",
    "TEACHER": "docente",
    "DOCENTE": "docente",
    "PARENT": "padre",
    "FAMILIA": "padre",
    "STUDENT": "alumno",
    "ALUMNO": "alumno",
}
RUTA_INICIAL_POR_ROL = {
    "admin": "/admin/dashboard",
    "docente": "/portal/docente/dashboard",
    "padre": "/portal/padre/dashboard",
    "alumno": "/portal/alumno/dashboard",
}


async def main(page: ft.Page):
    page.title = "Educar para Transformar"
    page.padding = 0

    async def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        ruta = (page.route or "/").rstrip("/")
        if not ruta:
            ruta = "/"

        # ==================== 1. GUARDIAS DE SESIÓN Y ROL ====================
        if ruta.startswith("/admin") or ruta.startswith("/portal/"):
            token = getattr(page, "auth_token", None)
            if not token:
                # Sin sesión activa: se muestra el login
                ruta = "/portal"
            else:
                rol = (getattr(page, "auth_rol", "") or "").upper()
                seccion_permitida = SECCION_POR_ROL.get(rol)
                if ruta.startswith("/admin"):
                    seccion_requerida = "admin"
                elif "/docente/" in ruta:
                    seccion_requerida = "docente"
                elif "/padre/" in ruta:
                    seccion_requerida = "padre"
                else:
                    seccion_requerida = "alumno"
                if seccion_permitida != seccion_requerida:
                    # El rol no corresponde a esta sección: se deriva a su panel
                    ruta = RUTA_INICIAL_POR_ROL.get(seccion_permitida or "", "/portal")

        # ==================== 2. RUTAS ADMINISTRATIVAS ====================
        if ruta == "/admin/dashboard":
            vista_dash = await get_admin_dashboard_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_dash]))
            page.update()
            return
        elif ruta == "/admin/alumnos":
            vista_alumnos = await get_admin_alumnos_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_alumnos]))
            page.update()
            return
        elif ruta == "/admin/alumnos/nuevo":
            vista_form = await get_admin_alumno_form_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_form]))
            page.update()
            return
        elif ruta == "/admin/profesores":
            vista_profesores = await get_admin_profesores_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_profesores])
            )
            page.update()
            return
        elif ruta == "/admin/profesores/nuevo":
            vista_profesor_form = await get_admin_profesor_form_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_profesor_form])
            )
            page.update()
            return
        elif ruta == "/admin/reportes":
            vista_reportes = await get_admin_reportes_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_reportes]))
            page.update()
            return
        elif ruta == "/admin/deportes":
            vista_deportes = await get_admin_deportes_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_deportes]))
            page.update()
            return
        elif ruta == "/admin/transporte":
            vista_transporte = await get_admin_transporte_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_transporte])
            )
            page.update()
            return
        elif ruta == "/admin/comedor":
            vista_comedor = await get_admin_comedor_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_comedor]))
            page.update()
            return
        elif ruta == "/admin/niveles":
            vista_niveles = await get_admin_niveles_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_niveles]))
            page.update()
            return
        elif ruta == "/admin/cursos":
            vista_cursos = await get_admin_cursos_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_cursos]))
            page.update()
            return
        elif ruta == "/admin/materias":
            vista_materias = await get_admin_materias_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_materias]))
            page.update()
            return
        elif ruta == "/admin/horarios":
            vista_horarios = await get_admin_horarios_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_horarios]))
            page.update()
            return
        elif ruta == "/admin/inscripciones":
            vista_inscripciones = await get_admin_inscripciones_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_inscripciones])
            )
            page.update()
            return
        elif ruta == "/admin/comunidad":
            vista_comunidad = await get_admin_comunidad_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_comunidad])
            )
            page.update()
            return
        elif ruta == "/admin/usuarios":
            vista_usuarios = await get_admin_usuarios_view(page)
            page.views.append(ft.View(route=ruta, padding=0, controls=[vista_usuarios]))
            page.update()
            return
        elif ruta == "/admin/reporte-alumnos-docentes":
            vista_reporte_ad = await get_admin_reporte_alumnos_docentes_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_reporte_ad])
            )
            page.update()
            return
        elif ruta == "/admin/reporte-cursos-materias":
            vista_reporte_cm = await get_admin_reporte_cursos_materias_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_reporte_cm])
            )
            page.update()
            return
        elif ruta == "/admin/reporte-deportes-avanzado":
            vista_reporte_dep = await get_admin_reporte_deportes_avanzado_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_reporte_dep])
            )
            page.update()
            return
        elif ruta == "/admin/reporte-transporte-pasajeros":
            vista_reporte_trans = await get_admin_reporte_transporte_pasajeros_view(
                page
            )
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_reporte_trans])
            )
            page.update()
            return
        # ==================== 3. RUTAS DEL PORTAL FAMILIAS ====================
        if ruta == "/portal/padre/dashboard":
            vista_padre_dash = await get_padre_dashboard_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_padre_dash])
            )
            page.update()
            return
        elif ruta == "/portal/padre/inscripcion":
            vista_padre_insc = await get_padre_inscripcion_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_padre_insc])
            )
            page.update()
            return
        elif ruta == "/portal/padre/deportes":
            vista_padre_dep = await get_padre_deportes_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_padre_dep])
            )
            page.update()
            return
        elif ruta == "/portal/padre/servicios":
            vista_padre_serv = await get_padre_servicios_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_padre_serv])
            )
            page.update()
            return
        elif ruta == "/portal/padre/docentes":
            vista_padre_doc = await get_padre_docentes_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_padre_doc])
            )
            page.update()
            return
        elif ruta == "/portal/padre/notas":
            vista_padre_notas = await get_padre_notas_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_padre_notas])
            )
            page.update()
            return
        # ==================== 4. RUTAS DEL PORTAL DOCENTE ====================
        if ruta == "/portal/docente/dashboard":
            vista_docente_dash = await get_docente_dashboard_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_docente_dash])
            )
            page.update()
            return
        elif ruta == "/portal/docente/materias":
            vista_docente_mat = await get_docente_materias_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_docente_mat])
            )
            page.update()
            return
        elif ruta == "/portal/docente/alumnos":
            vista_docente_alu = await get_docente_alumnos_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_docente_alu])
            )
            page.update()
            return
        elif ruta == "/portal/docente/deportes":
            vista_docente_dep = await get_docente_deportes_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_docente_dep])
            )
            page.update()
            return
        elif ruta == "/portal/docente/notas":
            vista_docente_notas = await get_docente_notas_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_docente_notas])
            )
            page.update()
            return
        # ==================== 5. RUTAS DEL PORTAL ESTUDIANTE ====================
        if ruta == "/portal/alumno/dashboard":
            vista_alumno_dash = await get_alumno_dashboard_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_alumno_dash])
            )
            page.update()
            return
        elif ruta == "/portal/alumno/materias":
            vista_alumno_mat = await get_alumno_materias_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_alumno_mat])
            )
            page.update()
            return
        elif ruta == "/portal/alumno/deportes":
            vista_alumno_dep = await get_alumno_deportes_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_alumno_dep])
            )
            page.update()
            return
        elif ruta == "/portal/alumno/servicios":
            vista_alumno_serv = await get_alumno_servicios_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_alumno_serv])
            )
            page.update()
            return
        elif ruta == "/portal/alumno/notas":
            vista_alumno_notas = await get_alumno_notas_view(page)
            page.views.append(
                ft.View(route=ruta, padding=0, controls=[vista_alumno_notas])
            )
            page.update()
            return

        # ==================== 6. RUTAS PÚBLICAS INSTITUCIONALES ====================
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
            contenido_central = await get_opiniones_view(page)
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
