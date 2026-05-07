"""Routes for meal CRUD operations."""

from datetime import date

import crud
from database import get_db
from fastapi import APIRouter, Depends
from schemas import DaySummary, MealCreate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/meals", tags=["meals"])


@router.post("/", response_model=dict)
def add_meal(meal: MealCreate, db: Session = Depends(get_db)):
    """Create a meal (with one entry) from the provided `MealCreate` payload."""
    crud.create_meal(db, meal)
    return {"message": "Meal created"}


@router.get("/day/{date_str}", response_model=DaySummary)
def get_day_summary(date_str: str, db: Session = Depends(get_db)):
    """Return a `DaySummary` for the ISO date string `date_str`."""
    day = date.fromisoformat(date_str)
    return crud.get_meals_by_day(db, day)


@router.delete("/{meal_id}")
def remove_meal(meal_id: int, db: Session = Depends(get_db)):
    """Delete a meal by id; returns deletion status."""
    success = crud.delete_meal(db, meal_id)
    return {"deleted": success}
