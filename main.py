from datetime import timedelta
from typing import List
from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi_jwt_auth.exceptions import AuthJWTException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from validate_email import validate_email
from fastapi_jwt_auth import AuthJWT
from routers import users, files

import crud
import models
import schemas
from database import engine, SessionLocal

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1
app = FastAPI()


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = True


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


app.include_router(users.router, tags=['users'])
app.include_router(files.router, tags=['items'])
