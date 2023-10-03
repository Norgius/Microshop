from pathlib import Path
from typing import Annotated

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Product
from . import crud
from core.models import db_helper


async def get_product_by_id(
    product_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Product:
    product = await crud.get_product(session=session, product_id=product_id)
    if product:
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product {product_id} not found!",
        )
