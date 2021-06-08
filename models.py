from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    files = relationship("File", back_populates="owner")


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    file_title = Column(String)
    created = Column(DateTime, default=func.now())
    upload_id = Column(Integer, ForeignKey("filehash.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="files")
    hash = relationship("FileHash", back_populates="files")


class FileHash(Base):
    __tablename__ = "filehash"
    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, index=True, unique=True)
    real_file_path = Column(String)
    real_file_name = Column(String)
    files = relationship("File", back_populates="hash")
