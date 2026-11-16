from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.academico import Curso, NivelEducativo
from backend.app.models.finanzas import (
    ComprobantePago,
    ConfiguracionFinanciera,
    Factura,
    ItemFactura,
)
from backend.app.models.personas import Alumno, Profesor
from backend.app.models.servicios import (
    Deporte,
    GrupoDeporte,
    Horario,
    InscripcionDeporte,
    InscripcionTransporte,
    RecorridoTransporte,
)
from backend.app.repositories import (
    alumno_repository,
    deporte_repository,
    grupo_deporte_repository,
    inscripcion_comedor_repository,
    inscripcion_deporte_repository,
    inscripcion_transporte_repository,
    recorrido_transporte_repository,
)


class FinanzasService:
    def get_valor_configuracion(self, db: Session, concepto: str) -> float:
        """Obtiene un valor fijo de la configuración (Ej: CUOTA_BASE)."""
        config = db.query(ConfiguracionFinanciera).filter_by(concepto=concepto).first()
        return float(config.valor) if config else 0.0

    def generar_facturas_mes(self, db: Session, mes: int, anio: int):
        """Genera las facturas detalladas para todos los alumnos activos."""

        # 1. Obtener valores fijos (Cuota y Comedor)
        precio_cuota_base = self.get_valor_configuracion(db, "CUOTA_BASE")
        precio_comedor = self.get_valor_configuracion(db, "COMEDOR")

        if precio_cuota_base == 0:
            raise HTTPException(
                status_code=400,
                detail="Debe configurar el valor de CUOTA_BASE en el sistema",
            )

        alumnos = alumno_repository.get_activos(db, limit=5000)
        facturas_generadas = 0

        # El vencimiento de la factura será el día 10 del mes siguiente
        mes_vencimiento = 1 if mes == 12 else mes + 1
        anio_vencimiento = anio + 1 if mes == 12 else anio
        vencimiento = date(anio_vencimiento, mes_vencimiento, 10)

        for alumno in alumnos:
            # Evitar duplicar la factura si ya se generó este mes
            existe = (
                db.query(Factura)
                .filter_by(legajo_alumno=alumno.legajo, mes=mes, anio=anio)
                .first()
            )
            if existe:
                continue

            items = []
            total = 0.0

            # A. Agregar Cuota Base (Obligatorio)
            items.append(
                ItemFactura(concepto="Cuota Base Mensual", monto=precio_cuota_base)
            )
            total += precio_cuota_base

            # B. Agregar Comedor (Si está activo)
            insc_comedor = inscripcion_comedor_repository.get_by_alumno(
                db, alumno.legajo
            )
            if insc_comedor and insc_comedor.estado == "ACTIVO" and precio_comedor > 0:
                items.append(
                    ItemFactura(concepto="Servicio de Comedor", monto=precio_comedor)
                )
                total += precio_comedor

            # C. Agregar Transporte (Si está activo)
            insc_transporte = inscripcion_transporte_repository.get_by_alumno(
                db, alumno.legajo
            )
            if insc_transporte and insc_transporte.estado == "ACTIVO":
                recorrido = recorrido_transporte_repository.get(
                    db, insc_transporte.id_recorrido
                )
                if recorrido and recorrido.precio_mensual > 0:
                    items.append(
                        ItemFactura(
                            concepto=f"Transporte: {recorrido.descripcion}",
                            monto=recorrido.precio_mensual,
                        )
                    )
                    total += float(recorrido.precio_mensual)

            # D. Agregar Deportes (Máximo 2, según regla de negocio)
            insc_deportes = inscripcion_deporte_repository.get_by_alumno(
                db, alumno.legajo
            )
            for insc_dep in insc_deportes:
                grupo = grupo_deporte_repository.get(db, insc_dep.id_grupo)
                if grupo:
                    deporte = deporte_repository.get(db, grupo.id_deporte)
                    if deporte and deporte.precio_mensual > 0:
                        items.append(
                            ItemFactura(
                                concepto=f"Deporte: {deporte.nombre}",
                                monto=deporte.precio_mensual,
                            )
                        )
                        total += float(deporte.precio_mensual)

            # 3. Crear la factura en la BD
            factura = Factura(
                legajo_alumno=alumno.legajo,
                mes=mes,
                anio=anio,
                total=total,
                estado="PENDIENTE",
                fecha_emision=date.today(),
                fecha_vencimiento=vencimiento,
            )
            db.add(factura)
            db.flush()  # Guarda temporalmente para que PostgreSQL asigne el id_factura

            # 4. Vincular el detalle (los ítems) a la factura creada
            for item in items:
                item.id_factura = factura.id_factura
                db.add(item)

            facturas_generadas += 1

        # Confirmar todos los cambios en la base de datos de una sola vez
        db.commit()
        return {
            "mensaje": f"Proceso finalizado. Se generaron {facturas_generadas} facturas nuevas."
        }

    def obtener_reporte_ingresos(
        self,
        db: Session,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        mes: int | None = None,
        anio: int | None = None,
    ) -> dict:
        """Listado de ingresos por período de tiempo (facturas cobradas con desglose)."""
        query = db.query(Factura).filter(Factura.estado == "PAGADA")
        if fecha_desde:
            query = query.filter(Factura.fecha_emision >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Factura.fecha_emision <= fecha_hasta)
        if mes:
            query = query.filter(Factura.mes == mes)
        if anio:
            query = query.filter(Factura.anio == anio)

        facturas = query.order_by(
            Factura.fecha_emision.desc(), Factura.id_factura.desc()
        ).all()

        alumnos_ids = {f.legajo_alumno for f in facturas}
        alumnos = (
            {
                a.legajo: a
                for a in db.query(Alumno).filter(Alumno.legajo.in_(alumnos_ids)).all()
            }
            if alumnos_ids
            else {}
        )
        cursos_ids = {a.id_curso for a in alumnos.values() if a.id_curso}
        cursos = (
            {
                c.id_curso: c
                for c in db.query(Curso).filter(Curso.id_curso.in_(cursos_ids)).all()
            }
            if cursos_ids
            else {}
        )
        niveles_ids = {c.id_nivel for c in cursos.values() if c.id_nivel}
        niveles = (
            {
                n.id_nivel: n
                for n in db.query(NivelEducativo)
                .filter(NivelEducativo.id_nivel.in_(niveles_ids))
                .all()
            }
            if niveles_ids
            else {}
        )

        facturas_ids = [f.id_factura for f in facturas]
        items_db = (
            db.query(ItemFactura).filter(ItemFactura.id_factura.in_(facturas_ids)).all()
            if facturas_ids
            else []
        )
        items_por_factura: dict[int, list[dict]] = {}
        for it in items_db:
            items_por_factura.setdefault(it.id_factura, []).append(
                {
                    "concepto": it.concepto,
                    "monto": float(it.monto),
                }
            )

        lista = []
        total_ingresos = 0.0
        for f in facturas:
            al = alumnos.get(f.legajo_alumno)
            cur = cursos.get(al.id_curso) if al and al.id_curso else None
            niv = niveles.get(cur.id_nivel) if cur and cur.id_nivel else None
            monto = float(f.total)
            total_ingresos += monto
            lista.append(
                {
                    "id_factura": f.id_factura,
                    "legajo_alumno": f.legajo_alumno,
                    "alumno_nombre": f"{al.apellido}, {al.nombre}"
                    if al
                    else f"Legajo #{f.legajo_alumno}",
                    "dni": al.dni if al else "-",
                    "curso": cur.nombre if cur else "Sin Curso",
                    "nivel": niv.nombre if niv else "-",
                    "mes": f.mes,
                    "anio": f.anio,
                    "fecha_emision": f.fecha_emision.strftime("%d/%m/%Y")
                    if f.fecha_emision
                    else "-",
                    "fecha_vencimiento": f.fecha_vencimiento.strftime("%d/%m/%Y")
                    if f.fecha_vencimiento
                    else "-",
                    "total": monto,
                    "estado": f.estado,
                    "items": items_por_factura.get(f.id_factura, []),
                }
            )

        return {
            "total_ingresos": total_ingresos,
            "cantidad_cobros": len(lista),
            "promedio_cobro": round(total_ingresos / len(lista), 2) if lista else 0.0,
            "items": lista,
        }

    def obtener_reporte_pagos_completos(
        self,
        db: Session,
        anio: int | None = None,
        mes: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> dict:
        """Listado de pagos completos realizados por período, discriminado por año y curso/alumno."""
        query = db.query(Factura).filter(Factura.estado == "PAGADA")
        if anio:
            query = query.filter(Factura.anio == anio)
        if mes:
            query = query.filter(Factura.mes == mes)
        if fecha_desde:
            query = query.filter(Factura.fecha_emision >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Factura.fecha_emision <= fecha_hasta)

        facturas = query.order_by(Factura.anio.desc(), Factura.mes.desc()).all()

        alumnos_ids = {f.legajo_alumno for f in facturas}
        alumnos = (
            {
                a.legajo: a
                for a in db.query(Alumno).filter(Alumno.legajo.in_(alumnos_ids)).all()
            }
            if alumnos_ids
            else {}
        )
        cursos_ids = {a.id_curso for a in alumnos.values() if a.id_curso}
        cursos = (
            {
                c.id_curso: c
                for c in db.query(Curso).filter(Curso.id_curso.in_(cursos_ids)).all()
            }
            if cursos_ids
            else {}
        )
        niveles_ids = {c.id_nivel for c in cursos.values() if c.id_nivel}
        niveles = (
            {
                n.id_nivel: n
                for n in db.query(NivelEducativo)
                .filter(NivelEducativo.id_nivel.in_(niveles_ids))
                .all()
            }
            if niveles_ids
            else {}
        )

        items_db = (
            db.query(ItemFactura)
            .filter(ItemFactura.id_factura.in_([f.id_factura for f in facturas]))
            .all()
            if facturas
            else []
        )
        items_por_factura: dict[int, list[str]] = {}
        for it in items_db:
            items_por_factura.setdefault(it.id_factura, []).append(
                f"{it.concepto} (${float(it.monto):,.0f})"
            )

        grupos_anio: dict[str, dict] = {}
        total_general = 0.0

        for f in facturas:
            al = alumnos.get(f.legajo_alumno)
            cur = cursos.get(al.id_curso) if al and al.id_curso else None
            niv = niveles.get(cur.id_nivel) if cur and cur.id_nivel else None
            nom_curso = cur.nombre if cur else "Sin Asignar"
            monto = float(f.total)
            total_general += monto

            reg = {
                "id_factura": f.id_factura,
                "mes": f.mes,
                "anio": f.anio,
                "legajo_alumno": f.legajo_alumno,
                "alumno_nombre": f"{al.apellido}, {al.nombre}"
                if al
                else f"Legajo #{f.legajo_alumno}",
                "dni": al.dni if al else "-",
                "curso": nom_curso,
                "nivel": niv.nombre if niv else "-",
                "monto_pagado": monto,
                "fecha_pago": f.fecha_emision.strftime("%d/%m/%Y")
                if f.fecha_emision
                else "-",
                "conceptos": ", ".join(items_por_factura.get(f.id_factura, ["Cuota"])),
            }

            key_anio = str(f.anio)
            if key_anio not in grupos_anio:
                grupos_anio[key_anio] = {
                    "anio": f.anio,
                    "subtotal": 0.0,
                    "cursos": {},
                }
            grupos_anio[key_anio]["subtotal"] += monto

            if nom_curso not in grupos_anio[key_anio]["cursos"]:
                grupos_anio[key_anio]["cursos"][nom_curso] = {
                    "curso": nom_curso,
                    "subtotal": 0.0,
                    "alumnos": [],
                }
            grupos_anio[key_anio]["cursos"][nom_curso]["subtotal"] += monto
            grupos_anio[key_anio]["cursos"][nom_curso]["alumnos"].append(reg)

        return {
            "total_recaudado": total_general,
            "cantidad_pagos": len(facturas),
            "grupos_anio": [
                {
                    "anio": g["anio"],
                    "subtotal": g["subtotal"],
                    "cursos": list(g["cursos"].values()),
                }
                for g in grupos_anio.values()
            ],
            "items_planos": [
                {
                    "id_factura": f.id_factura,
                    "anio": f.anio,
                    "mes": f.mes,
                    "legajo": f.legajo_alumno,
                    "alumno": f"{alumnos.get(f.legajo_alumno).apellido}, {alumnos.get(f.legajo_alumno).nombre}"
                    if alumnos.get(f.legajo_alumno)
                    else "-",
                    "curso": cursos.get(alumnos.get(f.legajo_alumno).id_curso).nombre
                    if alumnos.get(f.legajo_alumno)
                    and alumnos.get(f.legajo_alumno).id_curso
                    and cursos.get(alumnos.get(f.legajo_alumno).id_curso)
                    else "-",
                    "monto": float(f.total),
                    "fecha": f.fecha_emision.strftime("%d/%m/%Y")
                    if f.fecha_emision
                    else "-",
                    "conceptos": ", ".join(items_por_factura.get(f.id_factura, [])),
                }
                for f in facturas
            ],
        }

    def obtener_reporte_pagos_incompletos(
        self,
        db: Session,
        anio: int | None = None,
        mes: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> dict:
        """Listado de pagos incompletos / deudas por período, discriminado por año y curso/alumno."""
        query = db.query(Factura).filter(Factura.estado != "PAGADA")
        if anio:
            query = query.filter(Factura.anio == anio)
        if mes:
            query = query.filter(Factura.mes == mes)
        if fecha_desde:
            query = query.filter(Factura.fecha_vencimiento >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Factura.fecha_vencimiento <= fecha_hasta)

        facturas = query.order_by(Factura.anio.desc(), Factura.mes.desc()).all()

        alumnos_ids = {f.legajo_alumno for f in facturas}
        alumnos = (
            {
                a.legajo: a
                for a in db.query(Alumno).filter(Alumno.legajo.in_(alumnos_ids)).all()
            }
            if alumnos_ids
            else {}
        )
        cursos_ids = {a.id_curso for a in alumnos.values() if a.id_curso}
        cursos = (
            {
                c.id_curso: c
                for c in db.query(Curso).filter(Curso.id_curso.in_(cursos_ids)).all()
            }
            if cursos_ids
            else {}
        )
        niveles_ids = {c.id_nivel for c in cursos.values() if c.id_nivel}
        niveles = (
            {
                n.id_nivel: n
                for n in db.query(NivelEducativo)
                .filter(NivelEducativo.id_nivel.in_(niveles_ids))
                .all()
            }
            if niveles_ids
            else {}
        )

        items_db = (
            db.query(ItemFactura)
            .filter(ItemFactura.id_factura.in_([f.id_factura for f in facturas]))
            .all()
            if facturas
            else []
        )
        items_por_factura: dict[int, list[str]] = {}
        for it in items_db:
            items_por_factura.setdefault(it.id_factura, []).append(
                f"{it.concepto} (${float(it.monto):,.0f})"
            )

        grupos_anio: dict[str, dict] = {}
        total_deuda = 0.0
        hoy = date.today()

        for f in facturas:
            al = alumnos.get(f.legajo_alumno)
            cur = cursos.get(al.id_curso) if al and al.id_curso else None
            niv = niveles.get(cur.id_nivel) if cur and cur.id_nivel else None
            nom_curso = cur.nombre if cur else "Sin Asignar"
            monto = float(f.total)
            total_deuda += monto
            dias_mora = (
                (hoy - f.fecha_vencimiento).days
                if f.fecha_vencimiento and hoy > f.fecha_vencimiento
                else 0
            )

            reg = {
                "id_factura": f.id_factura,
                "mes": f.mes,
                "anio": f.anio,
                "legajo_alumno": f.legajo_alumno,
                "alumno_nombre": f"{al.apellido}, {al.nombre}"
                if al
                else f"Legajo #{f.legajo_alumno}",
                "dni": al.dni if al else "-",
                "curso": nom_curso,
                "nivel": niv.nombre if niv else "-",
                "saldo_pendiente": monto,
                "estado": f.estado,
                "fecha_vencimiento": f.fecha_vencimiento.strftime("%d/%m/%Y")
                if f.fecha_vencimiento
                else "-",
                "dias_mora": dias_mora,
                "conceptos": ", ".join(items_por_factura.get(f.id_factura, ["Cuota"])),
            }

            key_anio = str(f.anio)
            if key_anio not in grupos_anio:
                grupos_anio[key_anio] = {
                    "anio": f.anio,
                    "subtotal": 0.0,
                    "cursos": {},
                }
            grupos_anio[key_anio]["subtotal"] += monto

            if nom_curso not in grupos_anio[key_anio]["cursos"]:
                grupos_anio[key_anio]["cursos"][nom_curso] = {
                    "curso": nom_curso,
                    "subtotal": 0.0,
                    "alumnos": [],
                }
            grupos_anio[key_anio]["cursos"][nom_curso]["subtotal"] += monto
            grupos_anio[key_anio]["cursos"][nom_curso]["alumnos"].append(reg)

        return {
            "total_deuda": total_deuda,
            "cantidad_incompletos": len(facturas),
            "grupos_anio": [
                {
                    "anio": g["anio"],
                    "subtotal": g["subtotal"],
                    "cursos": list(g["cursos"].values()),
                }
                for g in grupos_anio.values()
            ],
            "items_planos": [
                {
                    "id_factura": f.id_factura,
                    "anio": f.anio,
                    "mes": f.mes,
                    "legajo": f.legajo_alumno,
                    "alumno": f"{alumnos.get(f.legajo_alumno).apellido}, {alumnos.get(f.legajo_alumno).nombre}"
                    if alumnos.get(f.legajo_alumno)
                    else "-",
                    "curso": cursos.get(alumnos.get(f.legajo_alumno).id_curso).nombre
                    if alumnos.get(f.legajo_alumno)
                    and alumnos.get(f.legajo_alumno).id_curso
                    and cursos.get(alumnos.get(f.legajo_alumno).id_curso)
                    else "-",
                    "monto": float(f.total),
                    "vencimiento": f.fecha_vencimiento.strftime("%d/%m/%Y")
                    if f.fecha_vencimiento
                    else "-",
                    "dias_mora": (hoy - f.fecha_vencimiento).days
                    if f.fecha_vencimiento and hoy > f.fecha_vencimiento
                    else 0,
                    "estado": f.estado,
                    "conceptos": ", ".join(items_por_factura.get(f.id_factura, [])),
                }
                for f in facturas
            ],
        }

    def obtener_reporte_pagos_deportes(
        self,
        db: Session,
        mes: int | None = None,
        anio: int | None = None,
        id_deporte: int | None = None,
    ) -> dict:
        """Listado de pagos de alumnos discriminado por deporte, nivel, horario y profesor a cargo."""
        q_grupos = db.query(GrupoDeporte)
        if id_deporte:
            q_grupos = q_grupos.filter(GrupoDeporte.id_deporte == id_deporte)
        grupos = q_grupos.all()

        deportes = {d.id_deporte: d for d in db.query(Deporte).all()}
        niveles = {n.id_nivel: n for n in db.query(NivelEducativo).all()}
        horarios = {h.id_horario: h for h in db.query(Horario).all()}
        profesores = {p.legajo: p for p in db.query(Profesor).all()}
        alumnos = {a.legajo: a for a in db.query(Alumno).all()}
        cursos = {c.id_curso: c for c in db.query(Curso).all()}

        grupos_ids = [g.id_grupo for g in grupos]
        inscripciones = (
            db.query(InscripcionDeporte)
            .filter(InscripcionDeporte.id_grupo.in_(grupos_ids))
            .all()
            if grupos_ids
            else []
        )

        hoy = date.today()
        mes_filtro = mes or hoy.month
        anio_filtro = anio or hoy.year

        legajos_inscritos = [i.legajo_alumno for i in inscripciones]
        facturas_mes = (
            db.query(Factura)
            .filter(
                Factura.legajo_alumno.in_(legajos_inscritos),
                Factura.mes == mes_filtro,
                Factura.anio == anio_filtro,
            )
            .all()
            if legajos_inscritos
            else []
        )
        factura_por_legajo = {f.legajo_alumno: f for f in facturas_mes}

        lista = []
        total_recaudado = 0.0
        total_al_dia = 0
        total_pendientes = 0

        grupos_dict = {g.id_grupo: g for g in grupos}

        for i in inscripciones:
            grupo = grupos_dict.get(i.id_grupo)
            if not grupo:
                continue
            dep = deportes.get(grupo.id_deporte)
            niv = niveles.get(grupo.id_nivel)
            hor = horarios.get(grupo.id_horario)
            prof = (
                profesores.get(dep.legajo_profesor_responsable)
                if dep and dep.legajo_profesor_responsable
                else None
            )
            al = alumnos.get(i.legajo_alumno)
            cur = cursos.get(al.id_curso) if al and al.id_curso else None

            precio_deporte = float(dep.precio_mensual) if dep else 0.0
            fac = factura_por_legajo.get(i.legajo_alumno)

            if fac:
                estado_pago = "PAGADO" if fac.estado == "PAGADA" else "PENDIENTE"
                fecha_ref = (
                    fac.fecha_emision.strftime("%d/%m/%Y")
                    if fac.estado == "PAGADA"
                    else (
                        fac.fecha_vencimiento.strftime("%d/%m/%Y")
                        if fac.fecha_vencimiento
                        else "-"
                    )
                )
            else:
                estado_pago = "NO FACTURADO"
                fecha_ref = "-"

            if estado_pago == "PAGADO":
                total_recaudado += precio_deporte
                total_al_dia += 1
            elif estado_pago == "PENDIENTE":
                total_pendientes += 1

            lista.append(
                {
                    "deporte": dep.nombre if dep else "-",
                    "id_deporte": dep.id_deporte if dep else 0,
                    "nivel": niv.nombre if niv else "-",
                    "horario": hor.descripcion if hor else "-",
                    "profesor": f"{prof.apellido}, {prof.nombre}"
                    if prof
                    else "Sin asignar",
                    "legajo_profesor": prof.legajo if prof else None,
                    "legajo_alumno": i.legajo_alumno,
                    "alumno_nombre": f"{al.apellido}, {al.nombre}"
                    if al
                    else f"Legajo #{i.legajo_alumno}",
                    "curso": cur.nombre if cur else "Sin Curso",
                    "precio_deporte": precio_deporte,
                    "estado_pago": estado_pago,
                    "fecha_referencia": fecha_ref,
                    "mes": mes_filtro,
                    "anio": anio_filtro,
                }
            )

        lista.sort(key=lambda x: (x["deporte"], x["nivel"], x["alumno_nombre"]))

        return {
            "mes": mes_filtro,
            "anio": anio_filtro,
            "total_recaudado": total_recaudado,
            "total_inscriptos": len(lista),
            "al_dia": total_al_dia,
            "morosos": total_pendientes,
            "items": lista,
        }

    def obtener_reporte_pagos_transporte(
        self,
        db: Session,
        mes: int | None = None,
        anio: int | None = None,
        id_recorrido: int | None = None,
    ) -> dict:
        """Listado de pagos de alumnos por recorrido del servicio de transporte escolar."""
        q_recorridos = db.query(RecorridoTransporte)
        if id_recorrido:
            q_recorridos = q_recorridos.filter(
                RecorridoTransporte.id_recorrido == id_recorrido
            )
        recorridos = q_recorridos.all()
        recorridos_dict = {r.id_recorrido: r for r in recorridos}

        recorridos_ids = list(recorridos_dict.keys())
        inscripciones = (
            db.query(InscripcionTransporte)
            .filter(
                InscripcionTransporte.id_recorrido.in_(recorridos_ids),
                InscripcionTransporte.estado == "ACTIVO",
            )
            .all()
            if recorridos_ids
            else []
        )

        alumnos = {a.legajo: a for a in db.query(Alumno).all()}
        cursos = {c.id_curso: c for c in db.query(Curso).all()}

        hoy = date.today()
        mes_filtro = mes or hoy.month
        anio_filtro = anio or hoy.year

        legajos_inscritos = [i.legajo_alumno for i in inscripciones]
        facturas_mes = (
            db.query(Factura)
            .filter(
                Factura.legajo_alumno.in_(legajos_inscritos),
                Factura.mes == mes_filtro,
                Factura.anio == anio_filtro,
            )
            .all()
            if legajos_inscritos
            else []
        )
        factura_por_legajo = {f.legajo_alumno: f for f in facturas_mes}

        lista = []
        total_recaudado = 0.0
        total_al_dia = 0
        total_pendientes = 0

        for i in inscripciones:
            rec = recorridos_dict.get(i.id_recorrido)
            if not rec:
                continue
            al = alumnos.get(i.legajo_alumno)
            cur = cursos.get(al.id_curso) if al and al.id_curso else None

            precio_transporte = float(rec.precio_mensual)
            fac = factura_por_legajo.get(i.legajo_alumno)

            if fac:
                estado_pago = "PAGADO" if fac.estado == "PAGADA" else "PENDIENTE"
                fecha_ref = (
                    fac.fecha_emision.strftime("%d/%m/%Y")
                    if fac.estado == "PAGADA"
                    else (
                        fac.fecha_vencimiento.strftime("%d/%m/%Y")
                        if fac.fecha_vencimiento
                        else "-"
                    )
                )
            else:
                estado_pago = "NO FACTURADO"
                fecha_ref = "-"

            if estado_pago == "PAGADO":
                total_recaudado += precio_transporte
                total_al_dia += 1
            elif estado_pago == "PENDIENTE":
                total_pendientes += 1

            lista.append(
                {
                    "recorrido": rec.descripcion,
                    "id_recorrido": rec.id_recorrido,
                    "precio_mensual": precio_transporte,
                    "legajo_alumno": i.legajo_alumno,
                    "alumno_nombre": f"{al.apellido}, {al.nombre}"
                    if al
                    else f"Legajo #{i.legajo_alumno}",
                    "dni": al.dni if al else "-",
                    "curso": cur.nombre if cur else "Sin Curso",
                    "estado_pago": estado_pago,
                    "fecha_referencia": fecha_ref,
                    "mes": mes_filtro,
                    "anio": anio_filtro,
                }
            )

        lista.sort(key=lambda x: (x["recorrido"], x["alumno_nombre"]))

        return {
            "mes": mes_filtro,
            "anio": anio_filtro,
            "total_recaudado": total_recaudado,
            "total_pasajeros": len(lista),
            "al_dia": total_al_dia,
            "morosos": total_pendientes,
            "items": lista,
        }

    def listar_comprobantes_pendientes(self, db: Session) -> list[dict]:
        """Devuelve los comprobantes de pago subidos por tutores que esperan validación del administrador."""
        comprobantes = (
            db.query(ComprobantePago)
            .filter(ComprobantePago.estado == "PENDIENTE")
            .order_by(ComprobantePago.id_comprobante.desc())
            .all()
        )
        if not comprobantes:
            return []

        facturas_ids = {c.id_factura for c in comprobantes}
        facturas = {
            f.id_factura: f
            for f in db.query(Factura)
            .filter(Factura.id_factura.in_(facturas_ids))
            .all()
        }
        alumnos_legajos = {f.legajo_alumno for f in facturas.values()}
        alumnos = (
            {
                a.legajo: a
                for a in db.query(Alumno)
                .filter(Alumno.legajo.in_(alumnos_legajos))
                .all()
            }
            if alumnos_legajos
            else {}
        )
        cursos_ids = {a.id_curso for a in alumnos.values() if a.id_curso}
        cursos = (
            {
                c.id_curso: c
                for c in db.query(Curso).filter(Curso.id_curso.in_(cursos_ids)).all()
            }
            if cursos_ids
            else {}
        )
        items_db = (
            db.query(ItemFactura).filter(ItemFactura.id_factura.in_(facturas_ids)).all()
            if facturas_ids
            else []
        )
        items_por_fac: dict[int, list[str]] = {}
        for it in items_db:
            items_por_fac.setdefault(it.id_factura, []).append(
                f"{it.concepto} (${float(it.monto):,.0f})"
            )

        resultado = []
        for c in comprobantes:
            fac = facturas.get(c.id_factura)
            if not fac:
                continue
            al = alumnos.get(fac.legajo_alumno)
            cur = cursos.get(al.id_curso) if al and al.id_curso else None

            resultado.append(
                {
                    "id_comprobante": c.id_comprobante,
                    "id_factura": c.id_factura,
                    "archivo_url": c.archivo_url,
                    "estado": c.estado,
                    "fecha_subida": c.fecha_subida.strftime("%d/%m/%Y %H:%M")
                    if c.fecha_subida
                    else "-",
                    "legajo_alumno": fac.legajo_alumno,
                    "alumno_nombre": f"{al.apellido}, {al.nombre}"
                    if al
                    else f"Legajo #{fac.legajo_alumno}",
                    "dni": al.dni if al else "-",
                    "curso": cur.nombre if cur else "Sin Curso",
                    "mes": fac.mes,
                    "anio": fac.anio,
                    "total": float(fac.total),
                    "estado_factura": fac.estado,
                    "conceptos": ", ".join(
                        items_por_fac.get(fac.id_factura, ["Cuota mensual"])
                    ),
                }
            )
        return resultado

    def aprobar_comprobante(self, db: Session, id_comprobante: int) -> dict:
        """Aprueba un comprobante de pago y pasa la factura asociada a estado PAGADA."""
        comp = (
            db.query(ComprobantePago)
            .filter(ComprobantePago.id_comprobante == id_comprobante)
            .first()
        )
        if not comp:
            raise HTTPException(status_code=404, detail="El comprobante no existe")

        fac = db.query(Factura).filter(Factura.id_factura == comp.id_factura).first()
        if not fac:
            raise HTTPException(
                status_code=404, detail="La factura vinculada no existe"
            )

        comp.estado = "APROBADO"
        fac.estado = "PAGADA"
        fac.fecha_emision = date.today()
        db.commit()
        db.refresh(comp)
        db.refresh(fac)

        return {
            "mensaje": f"Comprobante #{comp.id_comprobante} aprobado exitosamente. Factura #{fac.id_factura} cancelada.",
            "id_comprobante": comp.id_comprobante,
            "id_factura": fac.id_factura,
            "nuevo_estado_factura": fac.estado,
            "nuevo_estado_comprobante": comp.estado,
        }

    def rechazar_comprobante(
        self, db: Session, id_comprobante: int, motivo: str | None = None
    ) -> dict:
        """Rechaza un comprobante de pago y restablece la factura a estado PENDIENTE."""
        comp = (
            db.query(ComprobantePago)
            .filter(ComprobantePago.id_comprobante == id_comprobante)
            .first()
        )
        if not comp:
            raise HTTPException(status_code=404, detail="El comprobante no existe")

        fac = db.query(Factura).filter(Factura.id_factura == comp.id_factura).first()
        if not fac:
            raise HTTPException(
                status_code=404, detail="La factura vinculada no existe"
            )

        comp.estado = "RECHAZADO"
        fac.estado = "PENDIENTE"
        db.commit()
        db.refresh(comp)
        db.refresh(fac)

        return {
            "mensaje": f"Comprobante #{comp.id_comprobante} rechazado. La factura #{fac.id_factura} continúa pendiente.",
            "id_comprobante": comp.id_comprobante,
            "id_factura": fac.id_factura,
            "nuevo_estado_factura": fac.estado,
            "nuevo_estado_comprobante": comp.estado,
        }


finanzas_service = FinanzasService()
