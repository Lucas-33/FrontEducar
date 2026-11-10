"""Inicializa una base PostgreSQL (por ejemplo Neon) con el esquema y datos demo.

Uso:
    DATABASE_URL='postgresql://...' python scripts/init_db.py --reset
    DATABASE_URL='postgresql://...' python scripts/init_db.py --schema-only

Opciones:
    --reset        Borra las tablas existentes y las vuelve a crear.
                   ¡ATENCIÓN! Elimina todos los datos actuales.
    --schema-only  Solo ejecuta Creacion_tablas.pgsql (no carga datos demo).
    --seed-only    Solo ejecuta Insercion_datosDB.pgsql (el esquema ya debe existir).

También lee DATABASE_URL desde el archivo .env de la raíz del proyecto.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT_ESQUEMA = "Creacion_tablas.pgsql"
SCRIPT_DATOS = "Insercion_datosDB.pgsql"


def _leer_sql(nombre: str) -> str:
    ruta = RAIZ / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró {ruta}")
    return ruta.read_text(encoding="utf-8")


def _url_para_psycopg(url: str) -> str:
    """psycopg2 no entiende el sufijo `+psycopg2` que usa SQLAlchemy."""
    return url.replace("postgresql+psycopg2://", "postgresql://", 1)


def _existe_tabla_usuario(cur) -> bool:
    cur.execute("SELECT to_regclass('public.usuario')")
    return cur.fetchone()[0] is not None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crea el esquema y carga los datos demo en PostgreSQL/Neon."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra las tablas existentes antes de recrearlas (pierde datos).",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Solo crea el esquema, sin cargar datos demo.",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Solo carga los datos demo (el esquema ya debe existir).",
    )
    args = parser.parse_args()

    load_dotenv(RAIZ / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print(
            "ERROR: definí DATABASE_URL en el entorno o en el archivo .env",
            file=sys.stderr,
        )
        return 1

    try:
        with psycopg2.connect(_url_para_psycopg(database_url)) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                if args.seed_only:
                    if not _existe_tabla_usuario(cur):
                        print(
                            "ERROR: las tablas no existen. Corré primero sin "
                            "--seed-only (o con --reset).",
                            file=sys.stderr,
                        )
                        return 1
                else:
                    existe = _existe_tabla_usuario(cur)
                    if existe and not args.reset:
                        print(
                            "La tabla 'usuario' ya existe. No se hizo nada.\n"
                            "Si querés recrear todo desde cero (BORRANDO DATOS), "
                            "usá: python scripts/init_db.py --reset",
                            file=sys.stderr,
                        )
                        return 1

                    if args.reset and existe:
                        print(
                            "ATENCIÓN: --reset eliminará las tablas y todos sus datos.",
                            file=sys.stderr,
                        )

                    cur.execute(_leer_sql(SCRIPT_ESQUEMA))
                    print(f"OK: esquema cargado desde {SCRIPT_ESQUEMA}")

                if not args.schema_only:
                    cur.execute(_leer_sql(SCRIPT_DATOS))
                    print(f"OK: datos demo cargados desde {SCRIPT_DATOS}")

                cur.execute("SELECT COUNT(*) FROM usuario")
                usuarios = cur.fetchone()[0]
                print(f"Base inicializada. Usuarios disponibles: {usuarios}")
                print("Usuarios de prueba: admin_gral / password123")
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR al inicializar la base: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
