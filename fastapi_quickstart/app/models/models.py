from pydantic import BaseModel, PositiveInt, EmailStr


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

