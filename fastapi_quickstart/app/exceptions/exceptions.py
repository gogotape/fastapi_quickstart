from fastapi import HTTPException
from starlette import status


class CustomExceptionA(HTTPException):
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)


class ProductNotFoundException(HTTPException):
    def __init__(self, errors):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.errors = errors


class InvalidProductDataException(HTTPException):
    def __init__(self, detail: str, status_code: int):
        super().__init__(status_code=status_code, detail=detail)
