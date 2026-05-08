from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import FoodItemOut, FoodCreate
import crud

router = APIRouter(prefix="/api/foods", tags=["foods"])

@router.get("/", response_model=List[FoodItemOut])
def list_foods(search: str = None, db: Session = Depends(get_db)):
    """List all food items, optionally filtered by name search.
    
    Args:
        search: Optional substring to filter food names.
        db: Database session dependency.
        
    Returns:
        List of FoodItemOut objects.
    """
    return crud.get_foods(db, search)

@router.post("/", response_model=FoodItemOut)
def create_food(food_data: FoodCreate, db: Session = Depends(get_db)):
    """Create a new food item.
    
    Args:
        food_data: FoodCreate schema with nutritional values per 100g.
        db: Database session dependency.
        
    Returns:
        Created FoodItemOut object.
        
    Raises:
        HTTPException: If a food with the same name already exists.
    """
    return crud.create_food(db, food_data)