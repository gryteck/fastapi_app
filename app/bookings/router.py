from fastapi import APIRouter, Request, Depends
from fastapi_cache.decorator import cache
from datetime import date

from app.exceptions import RoomCannotBeBookedException
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.users.models import Users
from app.users.dependencies import get_current_user

router = APIRouter(
    prefix='/bookings',
    tags=['Бронирование']
)


@router.get("")
@cache(expire=20)
async def get_booking(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all(user_id=user.id)


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)) -> None:
    await BookingDAO.delete(user_id=user.id, booking_id=booking_id)


@router.post("")
async def add_bookings(room_id: int, date_from: date, date_to: date, user: Users = Depends(get_current_user)):
    booking = await BookingDAO.add(room_id=room_id, date_from=date_from, date_to=date_to, user_id=user.id)
    if not booking:
        raise RoomCannotBeBookedException

