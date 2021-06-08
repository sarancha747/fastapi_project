from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import schemas
from routers import users


async def get_user(session: AsyncSession, user_id: int):
    user = await session.execute(select(models.User).where(models.User.id == user_id))
    try:
        return user.scalars().one()
    except NoResultFound as e:
        return None


async def get_user_by_email(session: AsyncSession, email: str):
    user = await session.execute(select(models.User).where(models.User.email == email))
    try:
        return user.scalars().one()
    except NoResultFound as e:
        return None

async def create_user(session: AsyncSession, user: schemas.UserCreate):
    hashed_password = users.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def create_file(session: AsyncSession, file: schemas.FileCreate):
    db_file = models.File(title=file.title, description=file.description, file_title=file.file_title,
                          upload_id=file.upload_id, owner_id=file.owner_id)
    session.add(db_file)
    await session.commit()
    await session.refresh(db_file)
    return db_file


async def create_file_hash(session: AsyncSession, file: schemas.FileHashCreate):
    db_file_hash = models.FileHash(file_hash=file.file_hash, real_file_path=file.real_file_path,
                                   real_file_name=file.real_file_name)
    session.add(db_file_hash)
    await session.commit()
    await session.refresh(db_file_hash)
    return db_file_hash


async def get_file_by_hash(session: AsyncSession, hash_of_file: str):
    hash_of_file = await session.execute(select(models.FileHash).where(models.FileHash.file_hash == hash_of_file))
    try:
        return hash_of_file.scalars().one()
    except NoResultFound as e:
        return None


async def get_user_files(session: AsyncSession, user_id: int):
    files = await session.execute(select(models.File).where(models.File.owner_id == user_id))
    return files.scalars().all()
