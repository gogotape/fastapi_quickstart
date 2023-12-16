from fastapi import HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import ToDoModel, Product
from app.schemas.schemas import ToDoData, ToDo, MyProduct, ProductData
from exceptions.exceptions import ProductNotFoundException


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


async def create_product(session: AsyncSession, product_data: ProductData):
    product_item = Product(**product_data.model_dump())
    session.add(product_item)
    await session.commit()
    return product_item


async def get_product(session: AsyncSession, product_id: int):
    item = await session.get(Product, product_id)
    if not item:
        raise ProductNotFoundException(errors="Продукт не найден")
    return item


async def get_all_products(session: AsyncSession):
    result = await session.execute(select(Product))
    return result.scalars().all()
