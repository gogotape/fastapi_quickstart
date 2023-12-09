from sqlalchemy import Column, String, Integer, Boolean, Float
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base


hostname = "localhost"
database = "demo"
username = "user"
pwd = "password"
port = "5432"

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/demo"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class ToDoModel(Base):
    __tablename__ = "ToDoModel"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)


class Product(Base):
    __tablename__ = "Product"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    title = Column(String)
    price = Column(Float)
    count = Column(Integer)
    description = Column(String)
