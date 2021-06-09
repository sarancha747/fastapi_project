import asyncio
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from routers import users, files
import settings
from database import init_models

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_models()


class Settings(BaseModel):
    authjwt_secret_key: str = settings.SECRET_KEY
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
