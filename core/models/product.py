from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .order import Order
    from .order_product_association import OrderProductAssociation


class Product(Base):

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]

    orders: Mapped[list[Order]] = relationship(
        secondary='order_product_association',
        back_populates='products',
    )

    # association between Order -> Association -> Product
    orders_details: Mapped[list[OrderProductAssociation]] = relationship(
        back_populates='product'
    )
