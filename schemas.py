from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    password_confirm: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class TokenGet(BaseModel):
    email: str
    password: str
