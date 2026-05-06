"""Routes for recipe access."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import RecipeOut
import crud


router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("/", response_model=List[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    """Return a list of all recipes."""
    return crud.get_recipes(db)