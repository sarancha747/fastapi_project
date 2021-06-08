import hashlib
import os
import uuid
from typing import List, Tuple
from fastapi import APIRouter, File, Form, UploadFile, Depends, Header
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
import crud
import schemas
import settings

router = APIRouter()


@router.post("/files/")
async def create_file(title: str = Form(...),
                      description: str = Form(...),
                      upload: UploadFile = File(...),
                      X_CSRF_Token: str = Header(None, convert_underscores=True),
                      Authorize: AuthJWT = Depends(),
                      session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await crud.get_user_by_email(session, current_user)
    file_hash = await check_uploaded_file_hash(session, upload.file, upload.filename,
                                         os.path.join(settings.BASE_DIR, settings.FILE_DIR))
    file_schema = schemas.FileCreate(title=title, description=description, file_title=upload.filename,
                                     upload_id=file_hash.id, owner_id=user.id)
    file = await crud.create_file(session, file_schema)
    return {"title": title, "description": description, "file_name": upload.filename}


async def check_uploaded_file_hash(session, file_to_save, file_name, file_dir):
    hash_of_file = hashlib.sha256()
    for chunk in iter(lambda: file_to_save.read(4096), b""):
        hash_of_file.update(chunk)
    file_hash = await crud.get_file_by_hash(session, hash_of_file=hash_of_file.hexdigest())
    if not file_hash:
        local_filename = str(uuid.uuid4())[:9] + file_name
        with open(os.path.join(file_dir, local_filename), "wb") as f:
            file_to_save.seek(0)
            for chunk in iter(lambda: file_to_save.read(4096), b""):
                f.write(chunk)
        file_hash_schema = schemas.FileHashCreate(file_hash=hash_of_file.hexdigest(),
                                                  real_file_name=local_filename,
                                                  real_file_path=os.path.join(file_dir, local_filename))
        return await crud.create_file_hash(session, file_hash_schema)
    else:
        return file_hash


@router.get("/user_files/", response_model=List[schemas.File],)
async def get_files(Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await crud.get_user_by_email(session, current_user)
    return await crud.get_user_files(session, user.id)
