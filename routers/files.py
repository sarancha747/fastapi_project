import hashlib
import os
import uuid
from typing import List

from bson import ObjectId
from fastapi import APIRouter, File, Form, UploadFile, Depends, Header, Body, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
import crud
import schemas
import settings
import motor.motor_asyncio

router = APIRouter()
client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client.trainee_project


@router.post("/add-file/", response_model=schemas.File)
async def create_file(title: str = Form(...),
                      description: str = Form(...),
                      upload: UploadFile = File(...),
                      X_CSRF_Token: str = Header(None, convert_underscores=True),
                      Authorize: AuthJWT = Depends(), ):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await crud.get_user_by_email(db, current_user)
    file_hash = await check_uploaded_file_hash(upload.file, upload.filename,
                                               os.path.join(settings.BASE_DIR, settings.FILE_DIR))
    file_schema = schemas.FileCreate(title=title, description=description, file_title=upload.filename,
                                     upload_id=file_hash["_id"],
                                     owner_id=user["_id"])
    new_file = await crud.create_file(db, jsonable_encoder(file_schema))
    return await crud.get_file_by_id(db, new_file.inserted_id)


async def check_uploaded_file_hash(file_to_save, file_name, file_dir):
    hash_of_file = hashlib.sha256()
    for chunk in iter(lambda: file_to_save.read(4096), b""):
        hash_of_file.update(chunk)
    file_hash = await crud.get_hashed_file_by_hash(db, hash_of_file=hash_of_file.hexdigest())
    if not file_hash:
        local_filename = str(uuid.uuid4())[:9] + file_name
        with open(os.path.join(file_dir, local_filename), "wb") as f:
            file_to_save.seek(0)
            for chunk in iter(lambda: file_to_save.read(4096), b""):
                f.write(chunk)
        file_hash_schema = schemas.FileHashCreate(file_hash=hash_of_file.hexdigest(),
                                                  real_file_name=local_filename,
                                                  real_file_path=os.path.join(file_dir, local_filename))
        created_file = await crud.create_hashed_file(db, jsonable_encoder(file_hash_schema))
        return await crud.get_hashed_file_by_id(db, created_file.inserted_id)
    else:
        return file_hash


@router.get("/user-files/", response_model=List[schemas.File], )
async def get_files(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await crud.get_user_by_email(db, current_user)
    return await crud.get_user_files(db, str(user["_id"]))


@router.delete("/delete-file/{file_id}")
async def delete_file(file_id: str, X_CSRF_Token: str = Header(None, convert_underscores=True),
                      Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    try:
        file_id = ObjectId(file_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Wrong file Id")
    file = await crud.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=400, detail="Wrong file Id")
    user = await crud.get_user_by_email(db, current_user)
    if ObjectId(file["owner_id"]) == user["_id"]:
        await crud.delete_file_by_id(db, file["_id"])
    else:
        raise HTTPException(status_code=400, detail="Wrong file Id")
    return {"msg": "Successfully deleted"}


@router.put("/update-file/{file_id}")
async def update_file(file_id: str, updated_file: schemas.FileUpdate,
                      X_CSRF_Token: str = Header(None, convert_underscores=True),
                      Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    try:
        file_id = ObjectId(file_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Wrong file Id")
    file = await crud.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=400, detail="Wrong file Id")
    user = await crud.get_user_by_email(db, current_user)
    if ObjectId(file["owner_id"]) == user["_id"]:
        await crud.update_file_by_id(db, file["_id"], jsonable_encoder(updated_file))
    else:
        raise HTTPException(status_code=400, detail="Wrong file Id")
    return {"msg": "Successfully updated"}
