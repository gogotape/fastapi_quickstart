import uvicorn
from fastapi import FastAPI
from app.models.models import User, UserCreate, Product
from app.data.db import sample_products


app = FastAPI()
user1 = User(name="John Doe", age=15)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/custom")
async def read_custom_message():
    return {"message": "This is a custom message!"}


@app.get("/users", response_model=User)
async def users():
    return user1


@app.post("/user")
async def is_user_adult(user: User):
    return {"name": user.name,
            "age": user.age,
            "is_adult": user.age >= 18}


@app.post("/create_user")
async def create_user(user: UserCreate):
    return user


@app.get("/product/{product_id}")
async def get_product(product_id: int) -> Product:
    product = [item for item in sample_products if item['product_id'] == product_id]
    return product[0]


@app.get("/products/search")
async def search_product(keyword: str, category: str = None, limit: int = 10):
    return list(filter(lambda x: x["category"] == category and keyword in x["name"], sample_products[:limit]))


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
