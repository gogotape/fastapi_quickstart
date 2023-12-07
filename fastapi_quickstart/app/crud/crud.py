from fastapi import HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import ToDoModel
from app.models.models import ToDoData, ToDo


async def get_todo(session: AsyncSession, todo_id: int):
    db_item = await session.get(ToDoModel, todo_id)
    return db_item


async def create_todo(session: AsyncSession, todo: ToDoData):
    db_item = ToDoModel(**todo.model_dump())
    session.add(db_item)
    await session.commit()
    return db_item


async def update_todo(session: AsyncSession, todo: ToDo):
    statement = (
        update(ToDoModel).
        where(ToDoModel.id == todo.id).
        values(todo.model_dump(exclude_unset=True)).
        returning(ToDoModel)
    )
    result = await session.execute(statement)
    item = result.first()
    if not item:
        raise HTTPException(404, "Data not found!")
    await session.commit()
    return item


async def delete_todo(session: AsyncSession, todo_id: int):
    item = await session.execute(delete(ToDoModel).where(ToDoModel.id == todo_id).returning(ToDoModel.id))
    if not item.scalar():
        raise HTTPException(status_code=404, detail="Data not found")
    await session.commit()
    return {"message": "Item successfully deleted"}
