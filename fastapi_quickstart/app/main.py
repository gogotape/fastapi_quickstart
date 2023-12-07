import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Annotated

from jose import JWTError, jwt
import uvicorn
from fastapi import FastAPI, Response, Cookie, Request, HTTPException, Depends, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from uvicorn.config import LOGGING_CONFIG

from app.crud import crud
from database.db import engine, async_session

from app.models.models import User, UserCreate, Product, UserLogin, UserInDB, TokenData, Token, UserInfo, ToDo, ToDoData
from app.data.db import sample_products, users_db, sessions, fake_users_db

from database.db import Base


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI()
message_format = '[%(asctime)s] [%(levelname)s] [%(name)s]:\t%(message)s'
LOGGING_CONFIG["formatters"]["access"]["fmt"] = message_format

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


# OAuth2 with Password (and hashing), Bearer with JWT tokens\


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "ebaaa2a642b890245c9559dc43e9746e4e994fb8806ad1b3a48eb51e3107613c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = 15):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[UserInfo, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=UserInfo)
async def read_users_me(
        current_user: Annotated[UserInfo, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[UserInfo, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.post("/create_todo", response_model=ToDo)
async def create_todo(todo: ToDoData, session: AsyncSession = Depends(get_session)):
    todo = await crud.create_todo(session=session, todo=todo)
    return todo


@app.get("/todo/{todo_id}", response_model=ToDo)
async def get_todo(todo_id: int, session: AsyncSession = Depends(get_session)):
    db_todo = await crud.get_todo(session=session, todo_id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    return db_todo


@app.put("/update_todo/", response_model=ToDo)
async def update_todo(todo: ToDo, session: AsyncSession = Depends(get_session)):
    return await crud.update_todo(session=session, todo=todo)


@app.delete("/delete/{todo_id}")
async def delete_todo(todo_id: int, session: AsyncSession = Depends(get_session)):
    return await crud.delete_todo(session=session, todo_id=todo_id)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
