from fastapi import HTTPException, Request, Depends, status
from jose import jwt

from app.config import settings

from app.users.dao import UsersDAO


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.JWT_KEY, settings.JWT_ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'{e}')
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found in db")
    user = await UsersDAO.find_one_or_none(id=int(user_id))
    return user
