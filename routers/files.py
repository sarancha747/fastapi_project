from datetime import timedelta
from typing import List
from fastapi import Depends, HTTPException, status, APIRouter
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from validate_email import validate_email
from fastapi_jwt_auth import AuthJWT
import main
import crud
import models
import schemas
from database import engine, SessionLocal

router = APIRouter()