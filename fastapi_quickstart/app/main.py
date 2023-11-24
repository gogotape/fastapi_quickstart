import uvicorn
from fastapi import FastAPI
from app.models.models import User


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


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
