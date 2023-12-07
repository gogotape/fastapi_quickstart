from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

hostname = "localhost"
database = "demo"
username = "user"
pwd = "password"
port = "5432"

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/demo"

engine = create_async_engine(DATABASE_URL, echo=True)

Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class ToDoModel(Base):
    __tablename__ = "ToDoModel"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
