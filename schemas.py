from datetime import datetime
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


class File(BaseModel):
    id: int
    title: str
    description: str
    file_title: str
    created: datetime

    class Config:
        orm_mode = True


class FileCreate(BaseModel):
    title: str
    description: str
    file_title: str
    upload_id: int
    owner_id: int


class FileHashCreate(BaseModel):
    file_hash: str
    real_file_path: str
    real_file_name: str

    class Config:
        orm_mode = True
