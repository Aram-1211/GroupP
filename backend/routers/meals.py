from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from schemas import MealCreate, DaySummary
import crud

router = APIRouter(prefix="/api/meals", tags=["meals"])

@router.post("/", response_model=dict)
def add_meal(meal: MealCreate, db: Session = Depends(get_db)):
    crud.create_meal(db, meal)
    return {"message": "Meal created"}

@router.get("/day/{date_str}", response_model=DaySummary)
def get_day_summary(date_str: str, db: Session = Depends(get_db)):
    day = date.fromisoformat(date_str)
    return crud.get_meals_by_day(db, day)

@router.delete("/{meal_id}")
def remove_meal(meal_id: int, db: Session = Depends(get_db)):
    success = crud.delete_meal(db, meal_id)
    return {"deleted": success}