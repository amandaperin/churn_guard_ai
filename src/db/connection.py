import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


# Load environment variables from the .env file
load_dotenv()


def get_engine():
    """
    Create and return a SQLAlchemy engine for PostgreSQL connection.
    """
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    engine = create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    return engine