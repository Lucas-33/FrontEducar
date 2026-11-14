"""Exportación de reportes a Excel (.xlsx).

Estos endpoints se invocan desde el navegador (botones "Exportar Excel"), por
lo que el JWT se recibe como parámetro de consulta `?token=...` en lugar del
encabezado Authorization.
"""

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.seguridad import Usuario
from backend.app.repositories import (
    alumno_repository,
    curso_repository,
    grupo_deporte_repository,
    inscripcion_comedor_repository,
    inscripcion_transporte_repository,
    materia_repository,
    nivel_repository,
    profesor_repository,
)
from backend.app.services.academico import academico_service
from backend.app.services.comunidad import comunidad_service
from backend.app.services.finanzas import finanzas_service
from backend.app.services.pdf_generator import (
    generar_pdf_reporte_alumnos_docentes,
    generar_pdf_reporte_cursos_materias,
    generar_pdf_reporte_deportes,
    generar_pdf_reporte_transporte,
)
from backend.app.services.seguridad import seguridad_service
from backend.app.services.servicios import servicios_escolares_service

router = APIRouter()

ENCABEZADO_FILL = PatternFill(
    start_color="0D6E6E", end_color="0D6E6E", fill_type="solid"
)
ENCABEZADO_FONT = Font(color="FFFFFF", bold=True)


def _autorizar_admin(db: Session, token: str | None) -> Usuario:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación",
        )
    usuario = seguridad_service.get_usuario_from_token(db, token)
    if seguridad_service.get_rol_nombre(db, usuario) != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden exportar reportes",
        )
    return usuario


def _agregar_hoja(wb: Workbook, titulo: str, encabezados: list[str], filas: list[list]):
    ws = wb.create_sheet(title=titulo[:31])
    ws.append(encabezados)
    for celda in ws[1]:
        celda.fill = ENCABEZADO_FILL
        celda.font = ENCABEZADO_FONT
        celda.alignment = Alignment(horizontal="center")
    for fila in filas:
        ws.append(fila)
    for indice, _ in enumerate(encabezados, start=1):
        letra = get_column_letter(indice)
        ancho = max(
            (
                len(str(ws.cell(row=fila, column=indice).value or ""))
                for fila in range(1, ws.max_row + 1)
            ),
            default=10,
        )
        ws.column_dimensions[letra].width = min(ancho + 4, 48)
    ws.freeze_panes = "A2"


def _respuesta_xlsx(wb: Workbook, nombre_archivo: str) -> StreamingResponse:
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )


def _respuesta_pdf(pdf_bytes: bytes, nombre_archivo: str) -> StreamingResponse:
    buffer = BytesIO(pdf_bytes)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nombre_archivo}"'},
    )


def _nombre_curso(db: Session, id_curso: int) -> str:
    curso = curso_repository.get(db, id_curso)
    return curso.nombre if curso else f"Curso #{id_curso}"


def _nombre_nivel_de_curso(db: Session, id_curso: int) -> str:
    curso = curso_repository.get(db, id_curso)
    if not curso:
        return "-"
    nivel = nivel_repository.get(db, curso.id_nivel)
    return nivel.nombre if nivel else "-"


# ==================== ALUMNOS Y DOCENTES ====================
@router.get(
    "/alumnos.xlsx", summary="Nómina de alumnos y docentes en Excel (solo ADMIN)"
)
@router.get(
    "/docentes.xlsx", summary="Nómina de alumnos y docentes en Excel (solo ADMIN)"
)
def exportar_alumnos_docentes(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    alumnos = alumno_repository.get_multi(db, limit=2000)
    filas_alumnos = [
        [
            a.legajo,
            a.apellido,
            a.nombre,
            a.dni,
            _nombre_curso(db, a.id_curso),
            _nombre_nivel_de_curso(db, a.id_curso),
            a.estado_alumno,
            a.telefono or "-",
            a.correo_electronico or "-",
        ]
        for a in sorted(alumnos, key=lambda x: (x.apellido, x.nombre))
    ]
    _agregar_hoja(
        wb,
        "Alumnos",
        [
            "Legajo",
            "Apellido",
            "Nombre",
            "DNI",
            "Curso",
            "Nivel",
            "Estado",
            "Teléfono",
            "Correo",
        ],
        filas_alumnos,
    )

    profesores = profesor_repository.get_multi(db, limit=2000)
    filas_profesores = [
        [
            p.legajo,
            p.apellido,
            p.nombre,
            p.dni,
            p.especialidad,
            p.estado,
            p.telefono,
            p.correo_electronico,
        ]
        for p in sorted(profesores, key=lambda x: (x.apellido, x.nombre))
    ]
    _agregar_hoja(
        wb,
        "Docentes",
        [
            "Legajo",
            "Apellido",
            "Nombre",
            "DNI",
            "Especialidad",
            "Estado",
            "Teléfono",
            "Correo",
        ],
        filas_profesores,
    )
    return _respuesta_xlsx(wb, "nomina_alumnos_docentes.xlsx")


@router.get("/alumnos.pdf", summary="Nómina de alumnos y docentes en PDF (solo ADMIN)")
@router.get("/docentes.pdf", summary="Plantel docente en PDF (solo ADMIN)")
def exportar_alumnos_docentes_pdf(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    alumnos = alumno_repository.get_multi(db, limit=2000)
    lista_alumnos = [
        {
            "legajo": a.legajo,
            "apellido": a.apellido,
            "nombre": a.nombre,
            "dni": a.dni,
            "curso": _nombre_curso(db, a.id_curso),
            "nivel": _nombre_nivel_de_curso(db, a.id_curso),
            "estado_alumno": a.estado_alumno,
        }
        for a in sorted(alumnos, key=lambda x: (x.apellido, x.nombre))
    ]
    profesores = profesor_repository.get_multi(db, limit=2000)
    lista_profesores = [
        {
            "legajo": p.legajo,
            "apellido": p.apellido,
            "nombre": p.nombre,
            "dni": p.dni,
            "especialidad": p.especialidad,
            "estado": p.estado,
        }
        for p in sorted(profesores, key=lambda x: (x.apellido, x.nombre))
    ]
    pdf_bytes = generar_pdf_reporte_alumnos_docentes(lista_alumnos, lista_profesores)
    return _respuesta_pdf(pdf_bytes, "nomina_alumnos_docentes.pdf")


# ==================== CURSOS Y MATERIAS ====================
@router.get(
    "/cursos-materias.xlsx",
    summary="Cursos, materias y docentes a cargo en Excel (solo ADMIN)",
)
def exportar_cursos_materias(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    cursos = curso_repository.get_multi(db, limit=1000)
    filas_cursos = []
    for c in cursos:
        nivel = nivel_repository.get(db, c.id_nivel)
        cantidad = len(alumno_repository.get_by_curso(db, c.id_curso))
        filas_cursos.append(
            [c.id_curso, c.nombre, nivel.nombre if nivel else "-", cantidad]
        )
    _agregar_hoja(wb, "Cursos", ["ID", "Curso", "Nivel", "Alumnos"], filas_cursos)

    asignaciones = academico_service.get_asignaciones(db)
    filas_asig = [
        [a.materia, a.curso, a.nivel, a.profesor, a.legajo_profesor]
        for a in sorted(asignaciones, key=lambda x: (x.nivel, x.curso, x.materia))
    ]
    _agregar_hoja(
        wb,
        "Asignaciones",
        ["Materia", "Curso", "Nivel", "Docente", "Legajo docente"],
        filas_asig,
    )

    materias = materia_repository.get_multi(db, limit=1000)
    _agregar_hoja(
        wb,
        "Materias",
        ["ID", "Materia"],
        [[m.id_materia, m.nombre] for m in sorted(materias, key=lambda x: x.nombre)],
    )
    return _respuesta_xlsx(wb, "cursos_y_materias.xlsx")


@router.get(
    "/cursos-materias.pdf",
    summary="Cursos y materias en PDF (solo ADMIN)",
)
@router.get(
    "/cursos.pdf",
    summary="Cursos en PDF (solo ADMIN)",
)
@router.get(
    "/materias.pdf",
    summary="Materias en PDF (solo ADMIN)",
)
def exportar_cursos_materias_pdf(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    cursos = curso_repository.get_multi(db, limit=1000)
    lista_cursos = []
    for c in cursos:
        nivel = nivel_repository.get(db, c.id_nivel)
        cantidad = len(alumno_repository.get_by_curso(db, c.id_curso))
        lista_cursos.append(
            {
                "id_curso": c.id_curso,
                "nombre": c.nombre,
                "nivel": nivel.nombre if nivel else "-",
                "cantidad_alumnos": cantidad,
            }
        )
    asignaciones = academico_service.get_asignaciones(db)
    lista_asig = [
        {
            "materia": a.materia,
            "curso": a.curso,
            "nivel": a.nivel,
            "profesor": a.profesor,
            "legajo_profesor": a.legajo_profesor,
        }
        for a in sorted(asignaciones, key=lambda x: (x.nivel, x.curso, x.materia))
    ]
    pdf_bytes = generar_pdf_reporte_cursos_materias(lista_cursos, lista_asig)
    return _respuesta_pdf(pdf_bytes, "cursos_y_materias.pdf")


# ==================== DEPORTES ====================
@router.get(
    "/deportes.xlsx", summary="Reporte integral de deportes en Excel (solo ADMIN)"
)
def exportar_deportes(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    grupos = servicios_escolares_service.get_grupos_deporte(db)
    inscripciones = servicios_escolares_service.get_inscripciones_deporte(db)
    inscriptos_por_grupo = {}
    for i in inscripciones:
        inscriptos_por_grupo[i.id_grupo] = inscriptos_por_grupo.get(i.id_grupo, 0) + 1

    _agregar_hoja(
        wb,
        "Grupos",
        ["Grupo", "Disciplina", "Nivel", "Horario", "Inscriptos"],
        [
            [
                g.id_grupo,
                g.deporte,
                g.nivel,
                g.horario,
                inscriptos_por_grupo.get(g.id_grupo, 0),
            ]
            for g in grupos
        ],
    )
    _agregar_hoja(
        wb,
        "Inscripciones",
        ["Alumno", "Disciplina", "Fecha de inscripción"],
        [
            [i.alumno, i.deporte, i.fecha_inscripcion.strftime("%d/%m/%Y")]
            for i in inscripciones
        ],
    )
    return _respuesta_xlsx(wb, "reporte_deportes.xlsx")


@router.get("/deportes.pdf", summary="Reporte integral de deportes en PDF (solo ADMIN)")
def exportar_deportes_pdf(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    grupos = servicios_escolares_service.get_grupos_deporte(db)
    inscripciones = servicios_escolares_service.get_inscripciones_deporte(db)
    inscriptos_por_grupo = {}
    for i in inscripciones:
        inscriptos_por_grupo[i.id_grupo] = inscriptos_por_grupo.get(i.id_grupo, 0) + 1

    lista_grupos = [
        {
            "id_grupo": g.id_grupo,
            "deporte": g.deporte,
            "nivel": g.nivel,
            "horario": g.horario,
            "inscriptos": inscriptos_por_grupo.get(g.id_grupo, 0),
        }
        for g in grupos
    ]
    lista_inscripciones = [
        {
            "alumno": i.alumno,
            "deporte": i.deporte,
            "fecha_inscripcion": i.fecha_inscripcion.strftime("%d/%m/%Y"),
        }
        for i in inscripciones
    ]
    pdf_bytes = generar_pdf_reporte_deportes(lista_grupos, lista_inscripciones)
    return _respuesta_pdf(pdf_bytes, "reporte_deportes.pdf")


# ==================== TRANSPORTE ====================
@router.get(
    "/transporte.xlsx", summary="Hoja de ruta de transporte en Excel (solo ADMIN)"
)
def exportar_transporte(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    recorridos = servicios_escolares_service.get_recorridos(db)
    inscripciones = servicios_escolares_service.get_inscripciones_transporte(db)
    activos_por_recorrido = {}
    for i in inscripciones:
        if i.estado == "ACTIVO":
            activos_por_recorrido[i.id_recorrido] = (
                activos_por_recorrido.get(i.id_recorrido, 0) + 1
            )

    _agregar_hoja(
        wb,
        "Recorridos",
        ["ID", "Recorrido", "Pasajeros activos"],
        [
            [
                r.id_recorrido,
                r.descripcion,
                activos_por_recorrido.get(r.id_recorrido, 0),
            ]
            for r in recorridos
        ],
    )
    _agregar_hoja(
        wb,
        "Pasajeros",
        ["Alumno", "Recorrido", "Fecha de alta", "Estado"],
        [
            [i.alumno, i.recorrido, i.fecha_alta.strftime("%d/%m/%Y"), i.estado]
            for i in sorted(inscripciones, key=lambda x: x.alumno)
        ],
    )
    return _respuesta_xlsx(wb, "transporte_pasajeros.xlsx")


@router.get("/transporte.pdf", summary="Hoja de ruta de transporte en PDF (solo ADMIN)")
def exportar_transporte_pdf(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    recorridos = servicios_escolares_service.get_recorridos(db)
    inscripciones = servicios_escolares_service.get_inscripciones_transporte(db)
    activos_por_recorrido = {}
    for i in inscripciones:
        if i.estado == "ACTIVO":
            activos_por_recorrido[i.id_recorrido] = (
                activos_por_recorrido.get(i.id_recorrido, 0) + 1
            )

    lista_recorridos = [
        {
            "id_recorrido": r.id_recorrido,
            "descripcion": r.descripcion,
            "pasajeros_activos": activos_por_recorrido.get(r.id_recorrido, 0),
        }
        for r in recorridos
    ]
    lista_inscripciones = [
        {
            "alumno": i.alumno,
            "recorrido": i.recorrido,
            "fecha_alta": i.fecha_alta.strftime("%d/%m/%Y"),
            "estado": i.estado,
        }
        for i in sorted(inscripciones, key=lambda x: x.alumno)
    ]
    pdf_bytes = generar_pdf_reporte_transporte(lista_recorridos, lista_inscripciones)
    return _respuesta_pdf(pdf_bytes, "transporte_pasajeros.pdf")


# ==================== SOLICITUDES DE ADMISIÓN ====================
@router.get(
    "/solicitudes.xlsx",
    summary="Listado de solicitudes de admisión en Excel (solo ADMIN)",
)
def exportar_solicitudes(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    solicitudes = comunidad_service.get_solicitudes(db)
    _agregar_hoja(
        wb,
        "Solicitudes",
        [
            "N°",
            "Fecha",
            "Postulante",
            "DNI",
            "Nivel",
            "Tutor",
            "Teléfono",
            "Correo",
            "Estado",
            "Observaciones",
        ],
        [
            [
                f"#SOL-{s.fecha.year}-{s.id_solicitud:04d}",
                s.fecha.strftime("%d/%m/%Y"),
                s.postulante,
                s.dni,
                s.nivel,
                s.tutor,
                s.telefono or "-",
                s.correo or "-",
                s.estado,
                s.observaciones or "",
            ]
            for s in solicitudes
        ],
    )
    return _respuesta_xlsx(wb, "solicitudes_admision.xlsx")


# ==================== RESUMEN GENERAL ====================
@router.get("/resumen.xlsx", summary="Resumen general de gestión en Excel (solo ADMIN)")
def exportar_resumen(
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    comunidad = comunidad_service.resumen(db)
    transporte = [
        i
        for i in inscripcion_transporte_repository.get_multi(db, limit=1000)
        if i.estado == "ACTIVO"
    ]
    comedor = [
        i
        for i in inscripcion_comedor_repository.get_multi(db, limit=1000)
        if i.estado == "ACTIVO"
    ]

    metricas = [
        ["Alumnos activos", len(alumno_repository.get_activos(db, limit=1000))],
        ["Docentes activos", len(profesor_repository.get_activos(db, limit=1000))],
        ["Cursos", len(curso_repository.get_multi(db, limit=500))],
        ["Niveles educativos", len(nivel_repository.get_multi(db, limit=100))],
        ["Grupos de deporte", len(grupo_deporte_repository.get_multi(db, limit=300))],
        ["Pasajeros de transporte activos", len(transporte)],
        ["Inscriptos al comedor activos", len(comedor)],
        ["Solicitudes de admisión pendientes", comunidad["solicitudes_pendientes"]],
        ["Mensajes de contacto sin leer", comunidad["mensajes_no_leidos"]],
        ["Opiniones pendientes de moderación", comunidad["opiniones_pendientes"]],
    ]
    _agregar_hoja(wb, "Resumen", ["Métrica", "Valor"], metricas)
    return _respuesta_xlsx(wb, "resumen_general.xlsx")


# ==================== REPORTES FINANCIEROS EN EXCEL ====================
@router.get(
    "/ingresos.xlsx", summary="Exportar listado de ingresos en Excel (solo ADMIN)"
)
def exportar_ingresos_xlsx(
    token: str | None = Query(None),
    mes: int | None = Query(None),
    anio: int | None = Query(None),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    f_desde = None
    f_hasta = None
    try:
        from datetime import date

        if fecha_desde:
            f_desde = date.fromisoformat(fecha_desde)
        if fecha_hasta:
            f_hasta = date.fromisoformat(fecha_hasta)
    except Exception:
        pass

    datos = finanzas_service.obtener_reporte_ingresos(
        db, fecha_desde=f_desde, fecha_hasta=f_hasta, mes=mes, anio=anio
    )

    filas = [
        [
            it["id_factura"],
            f"{it['mes']:02d}/{it['anio']}",
            it["fecha_emision"],
            it["legajo_alumno"],
            it["alumno_nombre"],
            it["dni"],
            it["curso"],
            it["nivel"],
            ", ".join(
                f"{c['concepto']} (${c['monto']:,.0f})" for c in it.get("items", [])
            ),
            it["total"],
        ]
        for it in datos["items"]
    ]
    if filas:
        filas.append(
            ["", "", "", "", "TOTAL RECAUDADO", "", "", "", "", datos["total_ingresos"]]
        )

    _agregar_hoja(
        wb,
        "Ingresos",
        [
            "N° Factura",
            "Período",
            "Fecha Cobro",
            "Legajo",
            "Alumno",
            "DNI",
            "Curso",
            "Nivel",
            "Conceptos Cobrados",
            "Monto Total ($)",
        ],
        filas,
    )
    return _respuesta_xlsx(wb, "reporte_ingresos.xlsx")


@router.get(
    "/pagos-completos.xlsx", summary="Exportar pagos completos en Excel (solo ADMIN)"
)
def exportar_pagos_completos_xlsx(
    token: str | None = Query(None),
    anio: int | None = Query(None),
    mes: int | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    datos = finanzas_service.obtener_reporte_pagos_completos(db, anio=anio, mes=mes)

    filas = [
        [
            it["anio"],
            it["mes"],
            it["id_factura"],
            it["legajo"],
            it["alumno"],
            it["curso"],
            it["monto"],
            it["fecha"],
            it["conceptos"],
        ]
        for it in datos["items_planos"]
    ]
    if filas:
        filas.append(
            ["", "", "", "", "TOTAL PAGADO", "", datos["total_recaudado"], "", ""]
        )

    _agregar_hoja(
        wb,
        "Pagos Completos",
        [
            "Año Calendario",
            "Mes",
            "N° Factura",
            "Legajo",
            "Alumno",
            "Curso / Año Escolar",
            "Monto Abonado ($)",
            "Fecha de Pago",
            "Detalle de Conceptos",
        ],
        filas,
    )
    return _respuesta_xlsx(wb, "pagos_completos.xlsx")


@router.get(
    "/pagos-incompletos.xlsx",
    summary="Exportar pagos incompletos en Excel (solo ADMIN)",
)
def exportar_pagos_incompletos_xlsx(
    token: str | None = Query(None),
    anio: int | None = Query(None),
    mes: int | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    datos = finanzas_service.obtener_reporte_pagos_incompletos(db, anio=anio, mes=mes)

    filas = [
        [
            it["anio"],
            it["mes"],
            it["id_factura"],
            it["legajo"],
            it["alumno"],
            it["curso"],
            it["monto"],
            it["vencimiento"],
            it["dias_mora"],
            it["estado"],
            it["conceptos"],
        ]
        for it in datos["items_planos"]
    ]
    if filas:
        filas.append(
            ["", "", "", "", "TOTAL DEUDA", "", datos["total_deuda"], "", "", "", ""]
        )

    _agregar_hoja(
        wb,
        "Pagos Incompletos",
        [
            "Año Calendario",
            "Mes",
            "N° Factura",
            "Legajo",
            "Alumno",
            "Curso / Año Escolar",
            "Saldo Pendiente ($)",
            "Fecha Vencimiento",
            "Días Mora",
            "Estado",
            "Conceptos Adeudados",
        ],
        filas,
    )
    return _respuesta_xlsx(wb, "pagos_incompletos.xlsx")


@router.get(
    "/pagos-deportes.xlsx", summary="Exportar pagos de deportes en Excel (solo ADMIN)"
)
def exportar_pagos_deportes_xlsx(
    token: str | None = Query(None),
    mes: int | None = Query(None),
    anio: int | None = Query(None),
    id_deporte: int | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    datos = finanzas_service.obtener_reporte_pagos_deportes(
        db, mes=mes, anio=anio, id_deporte=id_deporte
    )

    filas = [
        [
            it["deporte"],
            it["nivel"],
            it["horario"],
            it["profesor"],
            it["legajo_alumno"],
            it["alumno_nombre"],
            it["curso"],
            it["precio_deporte"],
            it["estado_pago"],
            it["fecha_referencia"],
        ]
        for it in datos["items"]
    ]
    if filas:
        filas.append(
            [
                "",
                "",
                "",
                "",
                "",
                "TOTAL RECAUDADO",
                "",
                datos["total_recaudado"],
                "",
                "",
            ]
        )

    _agregar_hoja(
        wb,
        "Pagos Deportes",
        [
            "Deporte",
            "Nivel",
            "Horario",
            "Profesor a Cargo",
            "Legajo",
            "Alumno",
            "Curso",
            "Cuota Mensual ($)",
            "Estado de Pago",
            "Fecha Ref",
        ],
        filas,
    )
    return _respuesta_xlsx(wb, "pagos_deportes.xlsx")


@router.get(
    "/pagos-transporte.xlsx",
    summary="Exportar pagos de transporte en Excel (solo ADMIN)",
)
def exportar_pagos_transporte_xlsx(
    token: str | None = Query(None),
    mes: int | None = Query(None),
    anio: int | None = Query(None),
    id_recorrido: int | None = Query(None),
    db: Session = Depends(get_db),
):
    _autorizar_admin(db, token)
    wb = Workbook()
    wb.remove(wb.active)

    datos = finanzas_service.obtener_reporte_pagos_transporte(
        db, mes=mes, anio=anio, id_recorrido=id_recorrido
    )

    filas = [
        [
            it["recorrido"],
            it["precio_mensual"],
            it["legajo_alumno"],
            it["alumno_nombre"],
            it["dni"],
            it["curso"],
            it["estado_pago"],
            it["fecha_referencia"],
        ]
        for it in datos["items"]
    ]
    if filas:
        filas.append(
            ["", "TOTAL RECAUDADO", "", "", "", "", datos["total_recaudado"], ""]
        )

    _agregar_hoja(
        wb,
        "Pagos Transporte",
        [
            "Recorrido del Servicio",
            "Tarifa Mensual ($)",
            "Legajo",
            "Alumno",
            "DNI",
            "Curso",
            "Estado de Pago",
            "Fecha Ref",
        ],
        filas,
    )
    return _respuesta_xlsx(wb, "pagos_transporte.xlsx")
