from datetime import timedelta
from fastapi import Depends, HTTPException, status, APIRouter, Header
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from validate_email import validate_email
from fastapi_jwt_auth import AuthJWT
import settings
import crud
import schemas
from database import get_session

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(session, email: str, password: str):
    user = await crud.get_user_by_email(session, email)
    print("##########", user)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post("/token")
async def login_for_access_token(login_data: schemas.TokenGet, Authorize: AuthJWT = Depends(),
                                 session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = Authorize.create_access_token(subject=user.email, expires_time=expires)
    refresh_token = Authorize.create_refresh_token(subject=user.email)
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
async def logout(Authorize: AuthJWT = Depends(),X_CSRF_Token: str = Header(None, convert_underscores=True),):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return {"msg": "Successfully logout"}


@router.post("/create-users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    if user.password == "":
        raise HTTPException(status_code=400, detail="Password is empty")
    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Password mismatch")
    if not validate_email(user.email):
        raise HTTPException(status_code=400, detail="Email is invalid")
    db_user = await crud.get_user_by_email(session, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = await crud.create_user(session, user=user)
    return created_user
