import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def _normalizar_database_url(url: str) -> str:
    """Adapta la URL que entregan Neon/Render al driver de SQLAlchemy.

    Neon suele entregar `postgresql://...` (o `postgres://...`) y esa URL no
    declara el driver. La normalizamos a `postgresql+psycopg2://...` para que
    SQLAlchemy use el driver que ya está instalado.
    """
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://") :]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://") :]

    # Neon exige SSL. Si la URL no lo declara, lo agregamos automáticamente.
    if "neon.tech" in url and "sslmode=" not in url:
        url += "&sslmode=require" if "?" in url else "?sslmode=require"

    return url


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en el archivo .env ni en el entorno")

DATABASE_URL = _normalizar_database_url(DATABASE_URL)

# pool_pre_ping evita errores cuando Neon suspende/reinicia la conexión;
# pool_recycle renueva conexiones viejas antes de que el proveedor las corte.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"connect_timeout": 10},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependencia para inyectar en los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
