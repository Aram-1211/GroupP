from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import FoodItemOut, FoodCreate
import crud

router = APIRouter(prefix="/api/foods", tags=["foods"])

@router.get("/", response_model=List[FoodItemOut])
def list_foods(search: str = None, db: Session = Depends(get_db)):
    return crud.get_foods(db, search)

@router.post("/", response_model=FoodItemOut)
def create_food(food_data: FoodCreate, db: Session = Depends(get_db)):
    return crud.create_food(db, food_data)