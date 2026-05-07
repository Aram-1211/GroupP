"""Routes for accessing food items."""

from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends
from schemas import FoodItemOut
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/foods", tags=["foods"])


@router.get("/", response_model=List[FoodItemOut])
def list_foods(search: str = None, db: Session = Depends(get_db)):
    """List food items; optionally filter by `search` string."""
    return crud.get_foods(db, search)
