from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
