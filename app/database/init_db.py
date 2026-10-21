from app.database.connection import engine
from app.database.base import Base
from app.database import workshop_models, auth_models


def initialize_database():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")

    except Exception as error:
        print(f"Database initialization failed: {error}")
        raise


if __name__ == "__main__":
    initialize_database()