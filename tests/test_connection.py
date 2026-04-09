import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def test_database_connection() -> None:
    """
    Test whether the PostgreSQL database connection works.
    """
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1;"))
        value = result.scalar()

    assert value == 1