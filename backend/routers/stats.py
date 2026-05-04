from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from schemas import TargetOut, TargetUpdate, WeekSummary
import crud

router = APIRouter(prefix="/api", tags=["stats"])

@router.get("/target", response_model=TargetOut)
def get_target(db: Session = Depends(get_db)):
    target = crud.get_target(db)
    if not target:
        # create default
        target = crud.update_target(db, TargetUpdate(calories=2000, protein=50, fat=65, carbs=250))
    return target

@router.put("/target", response_model=TargetOut)
def update_target(target: TargetUpdate, db: Session = Depends(get_db)):
    return crud.update_target(db, target)

@router.get("/stats/week/{week_start}", response_model=WeekSummary)
def get_week(week_start: str, db: Session = Depends(get_db)):
    start_date = date.fromisoformat(week_start)
    return crud.get_week_stats(db, start_date)