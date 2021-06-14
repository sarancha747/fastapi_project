from pydantic import BaseModel, Field
from bson.objectid import ObjectId as BsonObjectId


class PydanticObjectId(BaseModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, BsonObjectId):
            raise TypeError('ObjectId required')
        return str(v)


class UserCreate(BaseModel):
    email: str
    password: str
    password_confirm: str


class User(BaseModel):
    id: PydanticObjectId = Field(..., alias='_id')
    email: str
    is_active: bool
    created: str


class TokenGet(BaseModel):
    email: str
    password: str


class File(BaseModel):
    id: PydanticObjectId = Field(..., alias='_id')
    title: str
    description: str
    file_title: str
    created: str
    upload_id: str
    owner_id: str


class FileCreate(BaseModel):
    title: str
    description: str
    file_title: str
    upload_id: PydanticObjectId
    owner_id: PydanticObjectId


class FileUpdate(BaseModel):
    title: str
    description: str


class FileHashCreate(BaseModel):
    file_hash: str
    real_file_path: str
    real_file_name: str
