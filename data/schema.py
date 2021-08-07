import os
import sys
import asyncio

from sqlalchemy import Column, Integer, Float, String, Boolean, Text

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey


Base = declarative_base()


class UsersTable(Base):
    __tablename__ = 'users'
    email = Column(String, primary_key=True)
    visited_places = relationship(
        "UserPlacesTable",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )
    feedbacks = relationship(
        "UserFeedbacksTable",
        cascade="all,delete-orphan",
        passive_deletes=True,
    )


class PlacesTable(Base):
    __tablename__ = 'places'
    uid = Column(String, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class UserPlacesTable(Base):
    __tablename__ = 'user_places'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    place_uid = Column(String, ForeignKey('places.uid'), nullable=False)
    with_feedback = Column(Boolean, nullable=False, default=False)


class UserFeedbacksTable(Base):
    __tablename__ = 'user_feedbacks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    place_uid = Column(String, ForeignKey('places.uid'), nullable=False)
    rate = Column(Integer, nullable=False, default=0)
    feedback_text = Column(Text, nullable=False, default='')


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


asyncio.get_event_loop().run_until_complete(main())
