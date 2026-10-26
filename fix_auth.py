import os

import bcrypt
from sqlalchemy import create_engine, text

# 1. Generar hash criptográfico real para 'password123'
pwd_plana = "password123"
hash_real = bcrypt.hashpw(pwd_plana.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
print(f"--> Hash real calculado en tu máquina:\n    {hash_real}\n")

# 2. Autodetectar la sesión o el motor (engine) del backend
SessionLocal = None
engine = None

modulos_posibles = [
    "backend.app.database",
    "backend.app.db.database",
    "backend.app.core.database",
    "backend.app.core.db",
    "backend.app.db.session",
]

for mod_name in modulos_posibles:
    try:
        mod = __import__(mod_name, fromlist=["SessionLocal", "engine"])
        SessionLocal = getattr(mod, "SessionLocal", None)
        engine = getattr(mod, "engine", None)
        if SessionLocal or engine:
            print(f"--> Conexión detectada en: '{mod_name}'")
            break
    except Exception:
        continue

# 3. Si no encontró el módulo, leer DATABASE_URL desde settings o .env
if not SessionLocal and not engine:
    db_url = None
    try:
        from backend.app.core.config import settings

        db_url = getattr(settings, "DATABASE_URL", None) or getattr(
            settings, "SQLALCHEMY_DATABASE_URI", None
        )
    except Exception:
        pass

    if not db_url and os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    db_url = line.strip().split("=", 1)[1].strip('"').strip("'")
                    break

    if db_url:
        print("--> Conexión creada desde variable de entorno.")
        engine = create_engine(str(db_url))

# 4. Ejecutar la actualización en PostgreSQL
if SessionLocal:
    db = SessionLocal()
elif engine:
    db = engine.connect()
else:
    print("❌ No se pudo localizar la conexión a la base de datos automáticamente.")
    print("   Copiá el hash mostrado arriba y ejecutá el UPDATE en pgAdmin.")
    exit(1)

try:
    db.execute(
        text(
            "UPDATE usuario SET password_hash = :hash, activo = TRUE WHERE username = 'admin_gral'"
        ),
        {"hash": hash_real},
    )
    if hasattr(db, "commit"):
        db.commit()
    print("✅ Base de datos actualizada con éxito.")

    # Verificación en caliente
    valido = bcrypt.checkpw(pwd_plana.encode("utf-8"), hash_real.encode("utf-8"))
    if valido:
        print("✅ VERIFICACIÓN MATEMÁTICA EXITOSA: 'admin_gral' + 'password123'")
finally:
    db.close()
