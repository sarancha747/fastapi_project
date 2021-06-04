import hashlib
import os
import uuid
from typing import List

from fastapi import APIRouter, File, Form, UploadFile, Depends, Header
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
import main
import crud
import schemas
from database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/files/")
async def create_file(title: str = Form(...),
                      description: str = Form(...),
                      upload: UploadFile = File(...),
                      X_CSRF_Token: str = Header(None, convert_underscores=True),
                      Authorize: AuthJWT = Depends(),
                      db: Session = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = crud.get_user_by_email(db, current_user)
    file_hash = check_uploaded_file_hash(upload.file, upload.filename, os.path.join(main.BASE_DIR, main.FILE_DIR), db)
    file_schema = schemas.FileCreate(title=title, description=description, file_title=upload.filename,
                                     upload_id=file_hash.id, owner_id=user.id)
    file = crud.create_file(db, file_schema)
    return {"title": title, "description": description, "file_name": upload.filename}


def check_uploaded_file_hash(file_to_save, file_name, file_dir, db):
    hash_of_file = hashlib.sha256()
    for chunk in iter(lambda: file_to_save.read(4096), b""):
        hash_of_file.update(chunk)
    file_hash = crud.get_file_by_hash(db, hash=hash_of_file.hexdigest())
    if not file_hash:
        local_filename = str(uuid.uuid4())[:9] + file_name
        with open(os.path.join(file_dir, local_filename), "wb") as f:
            file_to_save.seek(0)
            for chunk in iter(lambda: file_to_save.read(4096), b""):
                f.write(chunk)
        file_hash_schema = schemas.FileHashCreate(file_hash=hash_of_file.hexdigest(),
                                                  real_file_name=local_filename,
                                                  real_file_path=os.path.join(file_dir, local_filename))
        return crud.create_file_hash(db, file_hash_schema)
    else:
        return file_hash


@router.get("/user_files/", response_model=List[schemas.File])
async def get_files(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = crud.get_user_by_email(db, current_user)
    return crud.get_user_files(db, user.id)
