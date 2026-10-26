
"""AutoCare database connection."""

from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


# Store the database in app/database/
DATABASE_DIR = Path(__file__).resolve().parent
DB_PATH = DATABASE_DIR / "autocare.db"

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


engine = create_engine(
    DATABASE_URL,
    echo=False,
)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    """Enable SQLite foreign key constraints."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
