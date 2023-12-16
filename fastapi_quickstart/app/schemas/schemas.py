from pydantic import BaseModel, PositiveInt, EmailStr, Field


class User(BaseModel):
    name: str
    age: int


class UserCreate(BaseModel):
    name: str
    age: PositiveInt = None
    email: EmailStr
    is_subscribed: bool = None


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserInfo(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(UserInfo):
    hashed_password: str


class ToDoData(BaseModel):
    title: str
    description: str


class ToDo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False


# Pydantic модель ответов на ошибки
class ErrorResponse(BaseModel):
    error_code: int
    error_details: str


class ProductData(BaseModel):
    title: str
    price: float
    count: int
    description: str


class MyProduct(ProductData):
    id: int


class ErrorResponseModel(BaseModel):
    status_code: int
    message: str
    error_code: int
