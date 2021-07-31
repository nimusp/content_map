import os
import sys
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker


Base = declarative_base()


async def main():
    dsn = os.getenv('DSN')
    if not dsn:
        sys.exit('empty DSN not allowed!')

    engine = create_async_engine(dsn)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db_conn_sessionmaker():
    dsn = os.getenv('DSN')
    if not dsn:
        sys.exit('empty DSN not allowed!')

    engine = create_async_engine(dsn)
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


asyncio.new_event_loop().run_until_complete(main())
