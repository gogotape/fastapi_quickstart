from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# "check_same_thread" is needed only for SQLite. It's not needed for other databases.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ToDoModel(Base):
    __tablename__ = "ToDoModel"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
