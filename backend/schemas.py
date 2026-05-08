from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Food
class FoodItemOut(BaseModel):
    id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    model_config = {"from_attributes": True}

# Create New Food
class FoodCreate(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float

# Target
class TargetOut(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float
    model_config = {"from_attributes": True}

class TargetUpdate(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float

# Meal
class MealCreate(BaseModel):
    date: date
    name: str          # 对应 meal_type
    food_id: int
    quantity: float

class MealOut(BaseModel):
    id: int
    name: str          # meal_type
    food_name: str
    quantity: float
    calories: float
    protein: float
    fat: float
    carbs: float
    model_config = {"from_attributes": True}

class DaySummary(BaseModel):
    date: date
    total: dict        # {"calories": float, "protein": ..., "fat": ..., "carbs": ...}
    meals: List[MealOut]

class DailyStat(BaseModel):
    date: date
    day_name: str
    calories: float
    protein: float
    fat: float
    carbs: float

class WeekSummary(BaseModel):
    week_start: date
    week_end: date
    daily_stats: List[DailyStat]

# Recipes
class RecipeOut(BaseModel):
    id: int
    name: str
    description: str
    instructions: str
    model_config = {"from_attributes": True}