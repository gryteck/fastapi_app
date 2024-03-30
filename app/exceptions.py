from fastapi import APIRouter, HTTPException, status

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already exists"
)

IncorrectEmailOrPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password"
)

RoomCannotBeBookedException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Room can not be booked"
)

