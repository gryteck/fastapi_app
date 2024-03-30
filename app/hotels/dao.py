from sqlalchemy import select, func, and_

from app.database import async_session_maker, engine
from app.hotels.models import Hotels, Rooms
from app.bookings.models import Bookings
from app.dao.base import BaseDAO


class HotelsDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, location, date_from, date_to):
        async with async_session_maker() as session:
            rooms_left = (
                select(Bookings.room_id, Rooms.hotel_id, func.count(Bookings.room_id).label('bookings_count'))
                    .join(Rooms, Bookings.room_id == Rooms.id, isouter=True)
                    .group_by(Bookings.room_id, Rooms.hotel_id)
                    .cte('rooms_left')
            )

            hotels_rooms = (
                select(
                    Hotels, Rooms.quantity, func.coalesce(Rooms.quantity - rooms_left.c.bookings_count, Rooms.quantity)
                        .label('rooms_left')
                )
                    .join(Hotels, Rooms.hotel_id == Hotels.id, isouter=True)
                    .join(rooms_left, Rooms.id == rooms_left.c.room_id, isouter=True).cte('hotels_rooms')
            )

            result = select(hotels_rooms.c.id, hotels_rooms.c.name, hotels_rooms.c.location,
                            func.sum(hotels_rooms.c.quantity).label('total_rooms_quantity'), hotels_rooms.c.image_id,
                            func.sum(hotels_rooms.c.rooms_left).label('total_rooms_left')) \
                .filter(hotels_rooms.c.rooms_left > 0, hotels_rooms.c.location.like(f'%{location}%')) \
                .group_by(hotels_rooms.c.id, hotels_rooms.c.name, hotels_rooms.c.location, hotels_rooms.c.image_id)
            # print(result.compile(engine, compile_kwargs={"literal_binds": True}))
            result = await session.execute(result)
            return result.mappings().all()


class RoomsDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def find_all(cls, hotel_id, date_to, date_from):
        """
        WITH rooms_left AS (
            SELECT bookings.room_id, count(bookings.room_id) AS bookings_count
            FROM bookings
            JOIN rooms ON bookings.room_id = rooms.id
            WHERE (date_from <= '2023-06-20' AND date_to >= '2023-05-15')
            GROUP BY room_id, rooms.quantity
            HAVING rooms.quantity > count(bookings.room_id)
        )

        SELECT rooms.*, COALESCE(rooms.quantity - bookings_count, rooms.quantity) AS rooms_left
        FROM rooms
        LEFT JOIN rooms_left on rooms_left.room_id = rooms.id
        WHERE rooms.hotel_id=1
        """
        rooms_left = select(Bookings.room_id, func.count(Bookings.room_id).label('bookings_count')) \
            .join(Rooms, Bookings.room_id == Rooms.id, isouter=True) \
            .where(and_(Bookings.date_from < date_to, Bookings.date_to > date_from)) \
            .group_by(Bookings.room_id, Rooms.quantity) \
            .having(Rooms.quantity > func.count(Bookings.room_id)) \
            .cte('rooms_left')

        rooms = \
            select(
                Rooms, func.coalesce(Rooms.quantity - rooms_left.c.bookings_count, Rooms.quantity).label('rooms_left')
            ) \
                .outerjoin(rooms_left, rooms_left.c.room_id == Rooms.id) \
                .where(Rooms.hotel_id == hotel_id)
        async with async_session_maker() as session:
            result = await session.execute(rooms)
            return result.scalars().all()
