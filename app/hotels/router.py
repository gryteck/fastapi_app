import asyncio
from datetime import date

from fastapi import Request, APIRouter
from fastapi_cache.decorator import cache

from app.hotels.schemas import SHotels, SRooms
from app.hotels.dao import HotelsDAO, RoomsDAO

router = APIRouter(prefix="/hotels", tags=['Отели, Номера'])


@router.get('/{location}')
@cache(expire=20)
async def find_all(location: str, date_from: date, date_to: date):
    return await HotelsDAO.find_all(date_from=date_from, date_to=date_to, location=location)


@router.get('/{hotel_id}/rooms')
@cache(expire=20)
async def get_rooms(hotel_id: int, date_from: date, date_to: date):
    return await RoomsDAO.find_all(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
