"""Script de utilidad para testear la integración de Gmail y el envío de correos.

Requerimientos cubiertos:
1. Emisión mensual de facturas: detalle de composición del valor + factura PDF adjunta.
2. Aviso a morosos del día 20: detalle de deuda pendiente + factura de deuda PDF adjunta.

Uso:
    uv run python scripts/test_envio_correos.py --probar tu_correo@gmail.com
    uv run python scripts/test_envio_correos.py --cierre [--email-override tu_correo@gmail.com]
    uv run python scripts/test_envio_correos.py --morosos [--email-override tu_correo@gmail.com]
    uv run python scripts/test_envio_correos.py (modo interactivo)
"""

import argparse
import os
import sys

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

from backend.app.core.scheduler import tarea_aviso_morosos, tarea_cierre_mensual
from backend.app.services.email_service import (
    es_modo_simulado,
    obtener_config_smtp,
    probar_conexion_email,
)


def mostrar_estado_smtp():
    servidor, puerto, remitente, clave = obtener_config_smtp()
    simulado = es_modo_simulado(remitente, clave)
    print("\n" + "=" * 65)
    print(" ESTADO DE CONFIGURACIÓN DE CORREO ELECTRÓNICO (SMTP)")
    print("=" * 65)
    print(f" • Servidor SMTP:   {servidor}:{puerto}")
    print(f" • Remitente:       {remitente or '(No configurado)'}")
    print(
        f" • Clave:           {'*' * len(clave)} ({len(clave)} letras)"
        if clave
        else " • Clave:           (No configurada)"
    )
    if clave and len(clave) != 16:
        print(
            f" ⚠️  ADVERTENCIA: La clave configurada tiene {len(clave)} caracteres. "
            "Las Contraseñas de Aplicación de Google siempre tienen exactamente 16 caracteres (ej: abcd efgh ijkl mnop)."
        )
    if simulado:
        print(" • Modo de Trabajo: ⚠️  SIMULACIÓN (Consola / Logs)")
        print("   (Para enviar a casillas reales de Gmail, configura EMAIL_SENDER y")
        print("    EMAIL_PASSWORD con una Contraseña de Aplicación en tu .env)")
    else:
        print(" • Modo de Trabajo: 🌐 REAL (Conexión SMTP activa)")
    print("=" * 65 + "\n")


def ejecutar_prueba_directa(destinatario: str):
    print(f"📤 Enviando correo de diagnóstico a '{destinatario}' vía SMTP...")
    resultado = probar_conexion_email(destinatario=destinatario)
    print("\nResultado:")
    for k, v in resultado.items():
        print(f"  • {k}: {v}")
    if resultado.get("exito"):
        print("\n✅ ¡Prueba exitosa! Revisá tu bandeja de entrada en Gmail.")
    else:
        print("\n❌ La prueba falló. Verificá las credenciales en tu archivo .env.")


def ejecutar_prueba_cierre(email_override: str | None = None):
    print("\n🚀 [REQUERIMIENTO 1] Ejecutando cierre mensual y emisión de facturas...")
    print(
        "   - Se calcula la composición del valor (cuota, deportes, comedor, transporte)."
    )
    print("   - Se genera la factura oficial en formato PDF.")
    print("   - Se envía por correo a cada familia con el PDF adjunto.")
    if email_override:
        print(
            f"   - 💡 [MODO TEST] Todos los correos se redirigirán a: {email_override}"
        )

    resultado = tarea_cierre_mensual(forzar=True, email_override=email_override)
    print("\nResumen de ejecución:")
    print(f"  • Ejecutado: {resultado.get('ejecutado')}")
    print(f"  • Período: {resultado.get('periodo')}")
    print(f"  • Facturas procesadas: {resultado.get('facturas_procesadas')}")
    print(f"  • Correos enviados: {resultado.get('correos_enviados')}")
    if resultado.get("detalles"):
        print("  • Primeros envíos procesados:")
        for det in resultado["detalles"][:5]:
            print(
                f"    - Alumno: {det.get('alumno')} | Total: $ {det.get('total'):,.2f} | Destinatarios: {det.get('destinatarios')}"
            )


def ejecutar_prueba_morosos(email_override: str | None = None):
    print("\n⚠️  [REQUERIMIENTO 2] Ejecutando aviso a morosos del día 20...")
    print("   - Se identifican las cuentas que no registraron pago completo.")
    print("   - Se desglosa la deuda pendiente con conceptos adeudados.")
    print("   - Se adjunta la factura/liquidación en formato PDF.")
    if email_override:
        print(
            f"   - 💡 [MODO TEST] Todos los avisos se redirigirán a: {email_override}"
        )

    resultado = tarea_aviso_morosos(forzar=True, email_override=email_override)
    print("\nResumen de ejecución:")
    print(f"  • Ejecutado: {resultado.get('ejecutado')}")
    print(f"  • Facturas con saldo pendiente: {resultado.get('facturas_adeudadas')}")
    print(f"  • Correos de aviso enviados: {resultado.get('correos_enviados')}")
    if resultado.get("detalles"):
        print("  • Primeros avisos enviados:")
        for det in resultado["detalles"][:5]:
            print(
                f"    - Alumno: {det.get('alumno')} | Deuda: $ {det.get('deuda'):,.2f} | Destinatarios: {det.get('destinatarios')}"
            )


def modo_interactivo():
    mostrar_estado_smtp()
    print("Seleccioná la prueba que deseás realizar:")
    print(" 1) Probar conexión SMTP directa con tu cuenta de Gmail")
    print(
        " 2) Probar Requerimiento 1: Emisión mensual con desglose y factura PDF adjunta"
    )
    print(
        " 3) Probar Requerimiento 2: Aviso a morosos del día 20 con deuda y factura PDF adjunta"
    )
    print(" 4) Salir")

    opcion = input("\nIngresá una opción (1-4): ").strip()
    if opcion == "1":
        dest = input(
            "Ingresá tu correo de Gmail donde querés recibir la prueba: "
        ).strip()
        if dest:
            ejecutar_prueba_directa(dest)
    elif opcion == "2":
        dest = input(
            "¿Deseás redirigir todos los correos a tu casilla de test? (Enter para omitir o escribí tu email): "
        ).strip()
        ejecutar_prueba_cierre(email_override=dest or None)
    elif opcion == "3":
        dest = input(
            "¿Deseás redirigir todos los avisos a tu casilla de test? (Enter para omitir o escribí tu email): "
        ).strip()
        ejecutar_prueba_morosos(email_override=dest or None)
    else:
        print("Saliendo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Herramienta de prueba de envío de correos y tareas programadas."
    )
    parser.add_argument(
        "--probar",
        type=str,
        help="Dirección de correo a la que enviar un mensaje de prueba SMTP.",
    )
    parser.add_argument(
        "--cierre",
        action="store_true",
        help="Fuerza la ejecución del cierre mensual (Req. 1: facturas + desglose + PDF).",
    )
    parser.add_argument(
        "--morosos",
        action="store_true",
        help="Fuerza la ejecución del aviso del día 20 (Req. 2: deuda + desglose + PDF).",
    )
    parser.add_argument(
        "--email-override",
        type=str,
        help="Redirige los envíos a esta casilla de correo para pruebas.",
    )

    args = parser.parse_args()

    if args.probar:
        mostrar_estado_smtp()
        ejecutar_prueba_directa(args.probar)
    elif args.cierre:
        mostrar_estado_smtp()
        ejecutar_prueba_cierre(email_override=args.email_override)
    elif args.morosos:
        mostrar_estado_smtp()
        ejecutar_prueba_morosos(email_override=args.email_override)
    else:
        modo_interactivo()
