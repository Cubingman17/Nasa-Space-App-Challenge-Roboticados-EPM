from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

try:
    from backend.config import settings
except ModuleNotFoundError:
    from config import settings


class Base(DeclarativeBase):
    pass


database_url = make_url(settings.database_url)
if database_url.get_backend_name() == "sqlite" and database_url.database not in (None, ":memory:"):
    database_path = Path(database_url.database)
    if not database_path.is_absolute():
        database_path = (Path(__file__).resolve().parent / database_path).resolve()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        database_url = database_url.set(database=str(database_path))

connect_args = (
    {"check_same_thread": False}
    if database_url.get_backend_name() == "sqlite"
    else {}
)

engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped database session and always close it."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create application tables and synchronize the 32-metric catalog."""
    try:
        from backend.data.metrics import METRICS
        from backend.models.tables import MetricCatalog
    except ModuleNotFoundError:
        from data.metrics import METRICS
        from models.tables import MetricCatalog

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        for definition in METRICS:
            metric = session.get(MetricCatalog, definition["id"])
            if metric is None:
                metric = MetricCatalog(id=definition["id"])
                session.add(metric)

            metric.name = definition["name"]
            metric.dataset_key = definition["dataset_key"]
            metric.category = definition["category"]
            metric.unit = definition["unit"]
            metric.description = definition["description"]

        session.commit()
