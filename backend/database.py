import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    try:
        return os.environ["DATABASE_URL"]
    except KeyError as error:
        raise RuntimeError("DATABASE_URL is not set") from error


def create_database_engine(database_url: str | None = None) -> Engine:
    url = get_database_url() if database_url is None else database_url
    return create_engine(url)


SessionFactory = sessionmaker[Session]


def create_session_factory(engine: Engine) -> SessionFactory:
    return sessionmaker(bind=engine, expire_on_commit=False)


@lru_cache
def get_session_factory() -> SessionFactory:
    return create_session_factory(create_database_engine())
