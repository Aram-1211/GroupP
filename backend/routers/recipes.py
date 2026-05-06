"""Routes for recipe access."""

from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends
from schemas import RecipeOut
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("/", response_model=List[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    """Return a list of all recipes."""
    return crud.get_recipes(db)
