from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.db import ToDoModel
from app.models.models import ToDoData, ToDo


def get_todo(db: Session, todo_id: int):
    return db.query(ToDoModel).filter(ToDoModel.id == todo_id).first()


def create_todo(db: Session, todo: ToDoData):
    db_item = ToDoModel(**todo.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_todo(db: Session, todo: ToDo):
    # get the existing data
    db_item = get_todo(db=db, todo_id=todo.id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Data not found")

    # Update model class variable from requested fields
    for var, value in vars(todo).items():
        setattr(db_item, var, value) if value else None

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_todo(db: Session, todo_id: int):
    item = get_todo(db=db, todo_id=todo_id)
    if not item:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(item)
    db.commit()
    return {"message": "Item successfully deleted"}
