from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import schemas
from routers import users
from datetime import datetime


async def get_user_by_id(db, user_id):
    created_user = await db["users"].find_one({"_id": user_id})
    return created_user


async def get_user_by_email(db, user_email):
    return await db["users"].find_one({"email": user_email})


async def create_user(db, user):
    hashed_password = users.get_password_hash(user["password"])
    del user['password'], user['password_confirm']
    user['hashed_password'] = hashed_password
    user['is_active'] = True
    user['created'] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
    return await db["users"].insert_one(user)


async def get_file_by_id(db, file_id):
    created_file = await db["file"].find_one({"_id": file_id})
    return created_file


async def create_file(db, file):
    file['created'] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
    return await db["file"].insert_one(file)


async def get_hashed_file_by_id(db, hash_file_id):
    created_file = await db["file_hash"].find_one({"_id": hash_file_id})
    return created_file


async def create_hashed_file(db, file):
    return await db["file_hash"].insert_one(file)


async def get_hashed_file_by_hash(db, hash_of_file):
    return await db["file_hash"].find_one({"file_hash": hash_of_file})


async def get_user_files(db, user_id):
    files = db["file"].find({"owner_id": user_id})
    files_list = await files.to_list(length=20)
    list_to_return = files_list
    while files_list:
        files_list = await files.to_list(length=20)
        list_to_return = list_to_return + files_list
    return list_to_return
