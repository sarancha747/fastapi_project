from datetime import timedelta
import motor.motor_asyncio
from fastapi import Depends, HTTPException, status, APIRouter, Header
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from validate_email import validate_email
from fastapi_jwt_auth import AuthJWT
import settings
import crud
import schemas


router = APIRouter()
client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client.trainee_project

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(email, password):
    user = await crud.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


@router.post("/token")
async def login_for_access_token(login_data: schemas.TokenGet, Authorize: AuthJWT = Depends()):
    user = await authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = Authorize.create_access_token(subject=user["email"], expires_time=expires)
    refresh_token = Authorize.create_refresh_token(subject=user["email"])
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return {"msg": "Successfully login"}


@router.get('/refresh')
async def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    Authorize.set_access_cookies(new_access_token)
    return {"msg": "The token has been refresh"}


@router.delete('/logout')
async def logout(Authorize: AuthJWT = Depends(), X_CSRF_Token: str = Header(None, convert_underscores=True)):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return {"msg": "Successfully logout"}


@router.post("/create-users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate):
    if user.password == "":
        raise HTTPException(status_code=400, detail="Password is empty")
    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Password mismatch")
    if not validate_email(user.email):
        raise HTTPException(status_code=400, detail="Email is invalid")
    if await crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = jsonable_encoder(user)
    new_user = await crud.create_user(db, user)
    return await crud.get_user_by_id(db, new_user.inserted_id)
