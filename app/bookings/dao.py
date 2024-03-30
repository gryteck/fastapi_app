from sqlalchemy import select, insert, or_, and_, func, delete

from app.bookings.models import Bookings
from app.database import async_session_maker
from app.hotels.models import Hotels, Rooms
from app.dao.base import BaseDAO


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def find_all(cls, user_id: int):
        """
        SELECT * FROM bookings INNER JOIN rooms ON bookings.room_id = rooms.id
        WHERE user_id={user_id}
        """
        async with async_session_maker() as session:
            query = select(Bookings, Rooms).join(
                Rooms, Bookings.room_id == Rooms.id
            ).filter(
                Bookings.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, room_id, date_from, date_to, user_id):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = {room_id} AND
            (date_from <= {date_to} AND date_to >= {date_from})
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = {room_id}
        GROUP BY rooms.quantity, booked_rooms.room_id
        """

        booked_rooms = select(Bookings).where(
            and_(
                Bookings.room_id == room_id,
                and_(
                    Bookings.date_from < date_to,
                    Bookings.date_to > date_from
                )
            )).cte("booked_rooms")

        get_rooms_left = select(
            Rooms.quantity - func.count(
                booked_rooms.c.room_id
            )
        ).select_from(Rooms)\
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)\
            .where(Rooms.id == room_id)\
            .group_by(Rooms.quantity, booked_rooms.c.room_id
        )
        async with async_session_maker() as session:
            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()

            if rooms_left:
                get_price: int = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = insert(Bookings)\
                    .values(room_id=room_id, user_id=user_id, date_from=date_from, date_to=date_to, price=price)\
                    .returning(Bookings)

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking
            else:
                return None

    @classmethod
    async def delete(cls, user_id, booking_id):
        """
        DELETE FROM bookings WHERE user_id={user_id} AND id={booking_id}
        """
        async with async_session_maker() as session:
            query = delete(Bookings).filter(and_(Bookings.user_id == user_id, Bookings.id == booking_id))
            await session.execute(query)
            await session.commit()

