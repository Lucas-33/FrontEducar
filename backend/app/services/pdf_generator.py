import os
from datetime import date

from fpdf import FPDF


def generar_pdf_factura(factura, alumno, items) -> str:
    """Genera un PDF con el detalle de la deuda y devuelve la ruta del archivo."""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabecera Institucional
    pdf.set_font("helvetica", size=16, style="B")
    pdf.set_text_color(11, 79, 79) # TEAL_DARK
    pdf.cell(0, 10, txt="Educar para Transformar - SGE", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", size=12, style="B")
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt="LIQUIDACIÓN DE SERVICIOS EDUCATIVOS", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Datos del Alumno y Factura
    pdf.set_font("helvetica", size=11)
    pdf.cell(0, 8, txt=f"Estudiante: {alumno.apellido}, {alumno.nombre} (Legajo #{alumno.legajo})", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, txt=f"Período Facturado: {factura.mes}/{factura.anio}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, txt=f"Fecha de Emisión: {factura.fecha_emision}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, txt=f"Vencimiento: {factura.fecha_vencimiento}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Tabla de Ítems
    pdf.set_font("helvetica", size=11, style="B")
    pdf.cell(140, 10, txt="Concepto", border=1)
    pdf.cell(50, 10, txt="Monto", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", size=11)
    for item in items:
        pdf.cell(140, 10, txt=item.concepto, border=1)
        pdf.cell(50, 10, txt=f"$ {item.monto:.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
        
    # Total
    pdf.ln(5)
    pdf.set_font("helvetica", size=13, style="B")
    pdf.cell(140, 10, txt="TOTAL A ABONAR:", align='R')
    pdf.cell(50, 10, txt=f"$ {factura.total:.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
    
    # Guardar en carpeta temporal
    os.makedirs("temp", exist_ok=True)
    ruta_pdf = f"temp/Factura_{factura.id_factura}_Leg_{alumno.legajo}.pdf"
    pdf.output(ruta_pdf)
    
    return ruta_pdf