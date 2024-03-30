from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from app.config import settings
from app.users.dao import UsersDAO
from app.users.models import Users

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(d: dict):
    to_encode = d.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.JWT_KEY, settings.JWT_ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str) -> Users | None:
    user = await UsersDAO.find_one_or_none(email=email)
    if user and verify_password(password, user.hashed_password):
        return user
