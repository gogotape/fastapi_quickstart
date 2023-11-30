import uuid
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Response, Cookie, Header, Request, HTTPException, Depends, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from app.models.models import User, UserCreate, Product, UserLogin
from app.data.db import sample_products, users_db, sessions


app = FastAPI()
security = HTTPBasic()
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


@app.post("/login")
async def login(user_login: UserLogin, response: Response):
    if users_db.get(user_login.username) and users_db.get(user_login.username) == user_login.password:
        session_token = str(uuid.uuid4())
        sessions[session_token] = user_login
        response.set_cookie(key="session_token", value=session_token, httponly=True)
        return {"message": "куки установлены"}
    else:
        return {"message": "Неверный логин или пароль"}


@app.get("/user")
async def user_info(session_token = Cookie()):
    user = sessions.get(session_token)
    if user:
        return {"message": "Some info about user"}
    else:
        return {"message": "Unauthorized"}


@app.get("/headers")
async def get_headers(request: Request):
    user_agent = request.headers.get("User-Agent")
    accept_language = request.headers.get("Accept-Language")
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Неверный запрос")

    res = {"User-Agent": user_agent, "Accept-Language": accept_language}
    return res


async def auth_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> UserLogin:
    user = credentials.username
    if user not in users_db or users_db.get(user) != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Basic"})
    return UserLogin(**{"username": credentials.username, "password": credentials.password})


@app.get("/login_sec")
async def login_sec(user: UserLogin = Depends(auth_user)):
    return {"message": f"You got my secret, welcome, {user.username}"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
