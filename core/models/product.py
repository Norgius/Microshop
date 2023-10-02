from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base


class Product(Base):

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
