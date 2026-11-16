from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_check():
    """La API responde en el endpoint de salud."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_documentacion_disponible():
    """La app levanta y expone Swagger (/docs)."""
    assert client.get("/docs").status_code == 200


def test_esquema_openapi_generado():
    """El esquema OpenAPI se genera correctamente."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "Educar para Transformar - API & Web"


def test_endpoints_finanzas_protegidos():
    """Verifica que los endpoints de comprobantes y scheduler exijan autenticación."""
    # Subida de comprobante sin auth debe retornar 401
    resp_upload = client.post("/api/v1/finanzas/comprobantes/upload")
    assert resp_upload.status_code == 401

    # Cierre mensual scheduler sin auth debe retornar 401
    resp_cierre = client.post("/api/v1/finanzas/scheduler/cierre-mensual")
    assert resp_cierre.status_code == 401

    # Aviso a morosos scheduler sin auth debe retornar 401
    resp_aviso = client.post("/api/v1/finanzas/scheduler/aviso-morosos")
    assert resp_aviso.status_code == 401


def test_endpoints_reportes_financieros_protegidos():
    """Verifica que los endpoints de reportes financieros exijan autenticación ADMIN."""
    assert client.get("/api/v1/finanzas/reportes/ingresos").status_code == 401
    assert client.get("/api/v1/finanzas/reportes/pagos-completos").status_code == 401
    assert client.get("/api/v1/finanzas/reportes/pagos-incompletos").status_code == 401
    assert client.get("/api/v1/finanzas/reportes/deportes").status_code == 401
    assert client.get("/api/v1/finanzas/reportes/transporte").status_code == 401

    assert client.get("/api/v1/reportes/ingresos.xlsx").status_code == 401
    assert client.get("/api/v1/reportes/pagos-completos.xlsx").status_code == 401
    assert client.get("/api/v1/reportes/pagos-incompletos.xlsx").status_code == 401
    assert client.get("/api/v1/reportes/pagos-deportes.xlsx").status_code == 401
    assert client.get("/api/v1/reportes/pagos-transporte.xlsx").status_code == 401


def test_ruta_estatica_uploads_montada():
    """Verifica que el directorio de archivos /uploads esté disponible."""
    # Como el archivo inexistente da 404 de StaticFiles y no del catch-all ni 500, confirmamos el montaje
    resp = client.get("/uploads/comprobantes/archivo_inexistente.pdf")
    assert resp.status_code == 404


def test_endpoints_validacion_comprobantes_protegidos():
    """Verifica que los endpoints de validación de comprobantes exijan autenticación ADMIN."""
    assert client.get("/api/v1/finanzas/comprobantes/pendientes").status_code == 401
    assert client.put("/api/v1/finanzas/comprobantes/1/aprobar").status_code == 401
    assert client.put("/api/v1/finanzas/comprobantes/1/rechazar").status_code == 401


def test_endpoints_reportes_pdf_protegidos():
    """Verifica que los endpoints de reportes PDF exijan autenticación ADMIN."""
    assert client.get("/api/v1/reportes/alumnos.pdf").status_code == 401
    assert client.get("/api/v1/reportes/docentes.pdf").status_code == 401
    assert client.get("/api/v1/reportes/cursos-materias.pdf").status_code == 401
    assert client.get("/api/v1/reportes/deportes.pdf").status_code == 401
    assert client.get("/api/v1/reportes/transporte.pdf").status_code == 401


def test_generadores_pdf_reportes():
    """Prueba unitaria de la generación de PDFs institucionales."""
    from backend.app.services.pdf_generator import (
        generar_pdf_reporte_alumnos_docentes,
        generar_pdf_reporte_cursos_materias,
        generar_pdf_reporte_deportes,
        generar_pdf_reporte_transporte,
    )

    # 1. Alumnos y Docentes
    alumnos_mock = [
        {
            "legajo": 1001,
            "apellido": "Gomez",
            "nombre": "Ana",
            "dni": "45123456",
            "curso": "1° Año A",
            "nivel": "Secundario",
            "estado_alumno": "ACTIVO",
        }
    ]
    profesores_mock = [
        {
            "legajo": 201,
            "apellido": "Lopez",
            "nombre": "Carlos",
            "dni": "30123456",
            "especialidad": "Matemática",
            "estado": "ACTIVO",
        }
    ]
    pdf_alumnos = generar_pdf_reporte_alumnos_docentes(alumnos_mock, profesores_mock)
    assert isinstance(pdf_alumnos, bytes)
    assert len(pdf_alumnos) > 500

    # 2. Cursos y Materias
    cursos_mock = [
        {
            "id_curso": 1,
            "nombre": "1° A",
            "nivel": "Secundario",
            "cantidad_alumnos": 30,
        }
    ]
    asig_mock = [
        {
            "materia": "Física",
            "curso": "1° A",
            "nivel": "Secundario",
            "profesor": "Lopez, Carlos",
            "legajo_profesor": 201,
        }
    ]
    pdf_cursos = generar_pdf_reporte_cursos_materias(cursos_mock, asig_mock)
    assert isinstance(pdf_cursos, bytes)
    assert len(pdf_cursos) > 500

    # 3. Deportes
    grupos_mock = [
        {
            "id_grupo": 1,
            "deporte": "Fútbol",
            "nivel": "Primaria",
            "horario": "Lunes 16hs",
            "inscriptos": 15,
        }
    ]
    insc_deporte_mock = [
        {
            "alumno": "Gomez, Ana",
            "deporte": "Fútbol",
            "fecha_inscripcion": "15/03/2026",
        }
    ]
    pdf_deportes = generar_pdf_reporte_deportes(grupos_mock, insc_deporte_mock)
    assert isinstance(pdf_deportes, bytes)
    assert len(pdf_deportes) > 500

    # 4. Transporte
    recorridos_mock = [
        {
            "id_recorrido": 1,
            "descripcion": "Zona Norte",
            "pasajeros_activos": 20,
        }
    ]
    insc_transporte_mock = [
        {
            "alumno": "Gomez, Ana",
            "recorrido": "Zona Norte",
            "fecha_alta": "01/03/2026",
            "estado": "ACTIVO",
        }
    ]
    pdf_transporte = generar_pdf_reporte_transporte(
        recorridos_mock, insc_transporte_mock
    )
    assert isinstance(pdf_transporte, bytes)
    assert len(pdf_transporte) > 500


def test_generar_pdf_constancia_comprobante():
    from backend.app.services.pdf_generator import (
        generar_pdf_constancia_comprobante,
    )

    alumno_datos = {
        "nombre_completo": "Pérez, Juan",
        "legajo": 1002,
        "dni": "45999888",
        "curso": "2° Año B",
    }
    items = [{"concepto": "Cuota Marzo 2026", "monto": 85000.0}]
    pdf_bytes = generar_pdf_constancia_comprobante(
        id_comprobante=1,
        id_factura=10,
        archivo_url="ticket_fac_10.pdf",
        estado_comprobante="PENDIENTE",
        fecha_subida="14/11/2026 18:30",
        alumno_datos=alumno_datos,
        total_factura=85000.0,
        items=items,
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
