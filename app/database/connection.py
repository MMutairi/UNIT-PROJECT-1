from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "autocare.db"

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


engine = create_engine(DATABASE_URL,echo=False,)
SessionLocal = sessionmaker(bind = engine,autocommit=False,autoflush=False)