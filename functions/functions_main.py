from sqlalchemy.ext.asyncio import async_sessionmaker
from models import Announcement, User
from errors import generate_error
from aiohttp.web import HTTPNotFound, HTTPBadRequest, HTTPInternalServerError
from sqlalchemy.exc import IntegrityError
from config import logger
from sqlalchemy.future import select


async def get_announ_by_id(
        announ_id: int,
        session: async_sessionmaker
) -> Announcement:
    announ = await session.get(Announcement, announ_id)
    if announ is None:
        raise generate_error(HTTPNotFound, "Announcement not found")
    return announ


async def get_user_by_email(email: str, session: async_sessionmaker) -> User:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalars().first()
    if user is None:
        raise generate_error(HTTPNotFound, "User not found")
    return user


async def add_user(user: User, session: async_sessionmaker):
    try:
        session.add(user)
        await session.commit()
    except IntegrityError:
        raise generate_error(HTTPBadRequest, "User already exists")


async def add_announ(announ: Announcement, session: async_sessionmaker):
    try:
        session.add(announ)
        await session.commit()
    except ConnectionRefusedError as e:
        logger.error(f"{ConnectionRefusedError} - {e}")
        raise generate_error(
            HTTPInternalServerError,
            "The server is not available, try again later"
        )
