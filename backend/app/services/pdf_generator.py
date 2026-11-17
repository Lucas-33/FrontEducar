import os
from datetime import date

from fpdf import FPDF


def generar_pdf_factura(factura, alumno, items) -> str:
    """Genera un PDF con el detalle de la deuda y devuelve la ruta del archivo."""
    pdf = FPDF()
    pdf.add_page()

    # Cabecera Institucional
    pdf.set_font("helvetica", size=16, style="B")
    pdf.set_text_color(11, 79, 79)  # TEAL_DARK
    pdf.cell(
        0,
        10,
        text="Educar para Transformar - SGE",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("helvetica", size=12, style="B")
    pdf.set_text_color(0, 0, 0)
    pdf.cell(
        0,
        10,
        text="LIQUIDACIÓN DE SERVICIOS EDUCATIVOS",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(5)

    # Datos del Alumno y Factura
    pdf.set_font("helvetica", size=11)
    pdf.cell(
        0,
        8,
        text=f"Estudiante: {alumno.apellido}, {alumno.nombre} (Legajo #{alumno.legajo})",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0,
        8,
        text=f"Período Facturado: {factura.mes}/{factura.anio}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0,
        8,
        text=f"Fecha de Emisión: {factura.fecha_emision}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0,
        8,
        text=f"Vencimiento: {factura.fecha_vencimiento}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(5)

    # Tabla de Ítems
    pdf.set_font("helvetica", size=11, style="B")
    pdf.cell(140, 10, text="Concepto", border=1)
    pdf.cell(50, 10, text="Monto", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", size=11)
    for item in items:
        pdf.cell(140, 10, text=item.concepto, border=1)
        pdf.cell(
            50,
            10,
            text=f"$ {item.monto:.2f}",
            border=1,
            align="R",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    # Total
    pdf.ln(5)
    pdf.set_font("helvetica", size=13, style="B")
    pdf.cell(140, 10, text="TOTAL A ABONAR:", align="R")
    pdf.cell(
        50,
        10,
        text=f"$ {factura.total:.2f}",
        border=1,
        align="R",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # Guardar en carpeta temporal
    os.makedirs("temp", exist_ok=True)
    ruta_pdf = f"temp/Factura_{factura.id_factura}_Leg_{alumno.legajo}.pdf"
    pdf.output(ruta_pdf)

    return ruta_pdf


class ReportePDFBase(FPDF):
    """Clase base institucional para exportación de reportes a PDF."""

    def __init__(self, titulo: str, subtitulo: str = ""):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()

    def header(self):
        self.set_fill_color(13, 110, 110)
        self.rect(0, 0, 210, 4, "F")

        self.set_xy(10, 8)
        self.set_font("helvetica", "B", 13)
        self.set_text_color(11, 79, 79)
        self.cell(
            0, 6, text="Educar para Transformar - SGE", new_x="LMARGIN", new_y="NEXT"
        )

        self.set_font("helvetica", "B", 11)
        self.set_text_color(31, 41, 55)
        self.cell(0, 6, text=self.titulo, new_x="LMARGIN", new_y="NEXT")

        if self.subtitulo:
            self.set_font("helvetica", "", 9)
            self.set_text_color(107, 114, 128)
            self.cell(140, 5, text=self.subtitulo)

        self.set_font("helvetica", "I", 8)
        self.set_text_color(107, 114, 128)
        fecha_str = date.today().strftime("%d/%m/%Y")
        self.cell(
            0, 5, text=f"Fecha: {fecha_str}", align="R", new_x="LMARGIN", new_y="NEXT"
        )

        self.set_draw_color(209, 213, 219)
        self.set_line_width(0.3)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(5)

    def footer(self):
        self.set_y(-12)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(156, 163, 175)
        self.cell(
            0,
            10,
            text=f"Página {self.page_no()}/{{nb}} - Educar para Transformar SGE",
            align="C",
        )

    def seccion_titulo(self, texto: str):
        self.ln(3)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(11, 79, 79)
        self.cell(0, 6, text=texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def fila_tabla(
        self,
        anchos: list[int],
        textos: list[str],
        es_encabezado: bool = False,
        alineaciones: list[str] | None = None,
    ):
        if es_encabezado:
            self.set_fill_color(13, 110, 110)
            self.set_text_color(255, 255, 255)
            self.set_font("helvetica", "B", 8)
            altura = 7
        else:
            self.set_text_color(31, 41, 55)
            self.set_font("helvetica", "", 8)
            self.set_fill_color(249, 250, 251)
            altura = 6

        self.set_draw_color(229, 231, 235)
        for i, ancho in enumerate(anchos):
            alig = alineaciones[i] if alineaciones and i < len(alineaciones) else "L"
            txt = str(textos[i]) if i < len(textos) else ""
            max_chars = int(ancho * 0.45)
            if len(txt) > max_chars:
                txt = txt[: max_chars - 2] + ".."
            is_last = i == len(anchos) - 1
            self.cell(
                ancho,
                altura,
                text=txt,
                border=1,
                align=alig,
                fill=es_encabezado,
                new_x="LMARGIN" if is_last else "RIGHT",
                new_y="NEXT" if is_last else "TOP",
            )


def generar_pdf_reporte_alumnos_docentes(
    alumnos: list[dict], profesores: list[dict]
) -> bytes:
    """Genera el reporte PDF consolidado de alumnos y plantel docente."""
    pdf = ReportePDFBase(
        titulo="Nómina Oficial: Alumnos por Curso/Nivel y Docentes",
        subtitulo="Listado oficial emitido desde el Sistema de Gestión Escolar",
    )
    pdf.add_page()

    # Sección Alumnos
    pdf.seccion_titulo(f"1. Nómina de Alumnos Matriculados ({len(alumnos)} registros)")
    anchos_alumnos = [18, 52, 25, 40, 30, 25]
    pdf.fila_tabla(
        anchos_alumnos,
        ["Legajo", "Apellido y Nombre", "DNI", "Curso", "Nivel", "Estado"],
        es_encabezado=True,
    )
    for a in alumnos:
        pdf.fila_tabla(
            anchos_alumnos,
            [
                f"#{a.get('legajo', '')}",
                f"{a.get('apellido', '')}, {a.get('nombre', '')}",
                str(a.get("dni", "-")),
                a.get("curso", "-"),
                a.get("nivel", "-"),
                str(a.get("estado_alumno", "-")),
            ],
        )

    # Sección Docentes
    if profesores:
        pdf.ln(4)
        pdf.seccion_titulo(f"2. Plantel Docente ({len(profesores)} registros)")
        anchos_prof = [18, 55, 25, 62, 30]
        pdf.fila_tabla(
            anchos_prof,
            ["Legajo", "Apellido y Nombre", "DNI", "Especialidad", "Estado"],
            es_encabezado=True,
        )
        for p in profesores:
            pdf.fila_tabla(
                anchos_prof,
                [
                    f"#{p.get('legajo', '')}",
                    f"{p.get('apellido', '')}, {p.get('nombre', '')}",
                    str(p.get("dni", "-")),
                    p.get("especialidad") or "Sin especialidad",
                    str(p.get("estado", "-")),
                ],
            )

    return bytes(pdf.output())


def generar_pdf_reporte_cursos_materias(
    cursos: list[dict], asignaciones: list[dict]
) -> bytes:
    """Genera el reporte PDF de cursos, divisiones y materias asignadas."""
    pdf = ReportePDFBase(
        titulo="Nómina Curricular: Cursos, Divisiones y Asignaciones",
        subtitulo="Resumen académico y distribución docente por materia",
    )
    pdf.add_page()

    # Sección Cursos
    pdf.seccion_titulo(f"1. Cursos y Divisiones por Nivel ({len(cursos)} divisiones)")
    anchos_cursos = [20, 60, 65, 45]
    pdf.fila_tabla(
        anchos_cursos,
        ["ID", "Curso / División", "Nivel Educativo", "Matrícula Alumnos"],
        es_encabezado=True,
        alineaciones=["C", "L", "L", "C"],
    )
    for c in cursos:
        pdf.fila_tabla(
            anchos_cursos,
            [
                str(c.get("id_curso", "")),
                c.get("nombre", "-"),
                c.get("nivel", "-"),
                str(c.get("cantidad_alumnos", 0)),
            ],
            alineaciones=["C", "L", "L", "C"],
        )

    # Sección Asignaciones
    pdf.ln(4)
    pdf.seccion_titulo(
        f"2. Asignaciones Curriculares Docente-Materia ({len(asignaciones)} asignaciones)"
    )
    anchos_asig = [60, 40, 35, 55]
    pdf.fila_tabla(
        anchos_asig,
        ["Materia / Asignatura", "Curso", "Nivel", "Docente a Cargo"],
        es_encabezado=True,
    )
    for a in asignaciones:
        pdf.fila_tabla(
            anchos_asig,
            [
                a.get("materia", "-"),
                a.get("curso", "-"),
                a.get("nivel", "-"),
                a.get("profesor", "-"),
            ],
        )

    return bytes(pdf.output())


def generar_pdf_reporte_deportes(
    grupos: list[dict], inscripciones: list[dict]
) -> bytes:
    """Genera el reporte PDF integral de disciplinas e inscripciones deportivas."""
    pdf = ReportePDFBase(
        titulo="Reporte Integral de Actividades Deportivas",
        subtitulo="Disciplinas, grupos de entrenamiento e inscripciones activas",
    )
    pdf.add_page()

    # Sección Grupos
    pdf.seccion_titulo(f"1. Grupos de Entrenamiento ({len(grupos)} grupos)")
    anchos_grupos = [18, 55, 45, 47, 25]
    pdf.fila_tabla(
        anchos_grupos,
        ["Grupo", "Disciplina", "Nivel", "Horario", "Inscriptos"],
        es_encabezado=True,
        alineaciones=["C", "L", "L", "L", "C"],
    )
    for g in grupos:
        pdf.fila_tabla(
            anchos_grupos,
            [
                str(g.get("id_grupo", "")),
                g.get("deporte", "-"),
                g.get("nivel", "-"),
                g.get("horario", "-"),
                str(g.get("inscriptos", 0)),
            ],
            alineaciones=["C", "L", "L", "L", "C"],
        )

    # Sección Inscripciones
    pdf.ln(4)
    pdf.seccion_titulo(
        f"2. Fichas de Inscripción de Alumnos ({len(inscripciones)} inscriptos)"
    )
    anchos_insc = [75, 65, 50]
    pdf.fila_tabla(
        anchos_insc,
        ["Alumno", "Disciplina Deportiva", "Fecha de Inscripción"],
        es_encabezado=True,
    )
    for i in inscripciones:
        pdf.fila_tabla(
            anchos_insc,
            [
                i.get("alumno", "-"),
                i.get("deporte", "-"),
                i.get("fecha_inscripcion", "-"),
            ],
        )

    return bytes(pdf.output())


def generar_pdf_reporte_transporte(
    recorridos: list[dict], inscripciones: list[dict]
) -> bytes:
    """Genera el reporte PDF de recorridos y hoja de ruta de transporte escolar."""
    pdf = ReportePDFBase(
        titulo="Hoja de Ruta: Recorridos y Pasajeros de Transporte",
        subtitulo="Control operativo de unidades y pasajeros registrados",
    )
    pdf.add_page()

    # Sección Recorridos
    pdf.seccion_titulo(f"1. Recorridos y Circuitos ({len(recorridos)} recorridos)")
    anchos_rec = [25, 115, 50]
    pdf.fila_tabla(
        anchos_rec,
        ["ID", "Descripción del Recorrido", "Pasajeros Activos"],
        es_encabezado=True,
        alineaciones=["C", "L", "C"],
    )
    for r in recorridos:
        pdf.fila_tabla(
            anchos_rec,
            [
                str(r.get("id_recorrido", "")),
                r.get("descripcion", "-"),
                str(r.get("pasajeros_activos", 0)),
            ],
            alineaciones=["C", "L", "C"],
        )

    # Sección Pasajeros
    pdf.ln(4)
    pdf.seccion_titulo(f"2. Planilla de Pasajeros ({len(inscripciones)} registros)")
    anchos_pas = [70, 60, 35, 25]
    pdf.fila_tabla(
        anchos_pas,
        ["Alumno", "Recorrido", "Fecha de Alta", "Estado"],
        es_encabezado=True,
    )
    for p in inscripciones:
        pdf.fila_tabla(
            anchos_pas,
            [
                p.get("alumno", "-"),
                p.get("recorrido", "-"),
                p.get("fecha_alta", "-"),
                p.get("estado", "-"),
            ],
        )

    return bytes(pdf.output())


def generar_pdf_constancia_comprobante(
    id_comprobante: int,
    id_factura: int,
    archivo_url: str,
    estado_comprobante: str,
    fecha_subida: str,
    alumno_datos: dict,
    total_factura: float,
    items: list[dict],
) -> bytes:
    """Genera una constancia digital en PDF con el detalle del pago y la referencia informada."""
    pdf = ReportePDFBase(
        titulo="Constancia Oficial: Comprobante de Pago Informado",
        subtitulo=f"Comprobante #{id_comprobante} · Factura #{id_factura}",
    )
    pdf.add_page()

    # Sección 1: Datos de la Operación
    pdf.seccion_titulo("1. Datos Generales de la Transacción")
    pdf.fila_tabla(
        [55, 135],
        ["N° de Comprobante:", f"#{id_comprobante}"],
        es_encabezado=False,
    )
    pdf.fila_tabla(
        [55, 135],
        ["Estado de Validación:", estado_comprobante.upper()],
        es_encabezado=False,
    )
    pdf.fila_tabla(
        [55, 135],
        ["Fecha / Hora de Registro:", fecha_subida],
        es_encabezado=False,
    )
    pdf.fila_tabla(
        [55, 135],
        ["Referencia / Archivo Informado:", archivo_url],
        es_encabezado=False,
    )

    # Sección 2: Alumno
    pdf.ln(3)
    pdf.seccion_titulo("2. Alumno / Estudiante")
    pdf.fila_tabla(
        [55, 135],
        ["Nombre Completo:", alumno_datos.get("nombre_completo", "-")],
        es_encabezado=False,
    )
    pdf.fila_tabla(
        [55, 135],
        ["Legajo Estudiantil:", str(alumno_datos.get("legajo", "-"))],
        es_encabezado=False,
    )
    pdf.fila_tabla(
        [55, 135],
        ["DNI:", str(alumno_datos.get("dni", "-"))],
        es_encabezado=False,
    )
    pdf.fila_tabla(
        [55, 135],
        ["Curso / División:", str(alumno_datos.get("curso", "-"))],
        es_encabezado=False,
    )

    # Sección 3: Detalle de Conceptos Facturados
    pdf.ln(3)
    pdf.seccion_titulo("3. Detalle de Conceptos Liquidados")
    anchos = [140, 50]
    pdf.fila_tabla(anchos, ["Concepto", "Monto"], es_encabezado=True)
    if items:
        for it in items:
            monto_f = float(it.get("monto", 0))
            pdf.fila_tabla(
                anchos,
                [str(it.get("concepto", "Cuota")), f"$ {monto_f:,.2f}"],
            )
    else:
        pdf.fila_tabla(
            anchos,
            ["Liquidación de servicios educativos", f"$ {total_factura:,.2f}"],
        )

    pdf.ln(2)
    pdf.fila_tabla(
        [140, 50],
        ["TOTAL LIQUIDADO:", f"$ {total_factura:,.2f}"],
        es_encabezado=True,
    )

    pdf.ln(6)
    pdf.set_font("helvetica", "I", 9)
    pdf.set_text_color(107, 114, 128)
    pdf.multi_cell(
        0,
        5,
        "Nota: Este documento certifica los datos del pago declarados por el responsable a través del portal institucional de Educar para Transformar. "
        "La acreditación definitiva y cancelación de la deuda está sujeta a la conciliación del saldo en la cuenta bancaria de la institución.",
    )

    return bytes(pdf.output())
