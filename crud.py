from sqlalchemy.orm import Session
import models
import schemas
from routers import users


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = users.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_file(db: Session, file: schemas.FileCreate):
    db_file = models.File(title=file.title, description=file.description, file_title=file.file_title,
                          upload_id=file.upload_id, owner_id=file.owner_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def create_file_hash(db: Session, file: schemas.FileHashCreate):
    db_file_hash = models.FileHash(file_hash=file.file_hash, real_file_path=file.real_file_path,
                                   real_file_name=file.real_file_name)
    db.add(db_file_hash)
    db.commit()
    db.refresh(db_file_hash)
    return db_file_hash


def get_file_by_hash(db: Session, hash_of_file: str):
    hash_of_file = db.query(models.FileHash).filter(models.FileHash.file_hash == hash_of_file).first()
    if hash_of_file:
        return hash_of_file


def get_user_files(db: Session, user_id: int):
    return db.query(models.File).filter(models.File.owner_id == user_id).all()
