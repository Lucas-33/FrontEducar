from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.finanzas import ConfiguracionFinanciera, Factura, ItemFactura
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


finanzas_service = FinanzasService()
