from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @property
    def id_json(self):
        return {"id": self.id}


class User(Base):
    __tablename__ = "Users"

    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    admin: Mapped[bool] = mapped_column(default=False)

    @property
    def json_user(self):
        return {"id": self.id, "email": self.email}


class Announcement(Base):
    __tablename__ = "Announcements"

    title: Mapped[str]
    description: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))

    @property
    def json_announ(self):
        return {
            "id": self.id,
            "title": self.title,
            "descriptoin": self.description,
            "create_at": self.create_at.isoformat(),
            "user_id": self.user_id,
        }
