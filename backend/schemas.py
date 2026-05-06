"""Pydantic schema (DTO) definitions for API input/output.

Defines request and response models used by the FastAPI endpoints.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


# Food schemas
class FoodItemOut(BaseModel):
    """Output schema for a food item with nutrition per 100g."""
    id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    model_config = {"from_attributes": True}

# Target schemas
class TargetOut(BaseModel):
    """Output schema for user's nutrition targets."""
    calories: float
    protein: float
    fat: float
    carbs: float
    model_config = {"from_attributes": True}

class TargetUpdate(BaseModel):
    """Input schema used to update a user's nutrition target."""
    calories: float
    protein: float
    fat: float
    carbs: float

# Meal schemas
class MealCreate(BaseModel):
    """Input model for creating a meal with a single entry."""
    date: date
    name: str
    food_id: int
    quantity: float

class MealOut(BaseModel):
    """Output schema for a meal entry with computed nutrition values."""
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
    """Aggregated daily summary including totals and list of meals."""
    date: date
    total: dict        # {"calories": float, "protein": ..., "fat": ..., "carbs": ...}
    meals: List[MealOut]

class DailyStat(BaseModel):
    """Per-day stat used in week summaries."""
    date: date
    day_name: str
    calories: float
    protein: float
    fat: float
    carbs: float

class WeekSummary(BaseModel):
    """Weekly aggregation containing a list of `DailyStat`."""
    week_start: date
    week_end: date
    daily_stats: List[DailyStat]

# Recipe schemas
class RecipeOut(BaseModel):
    """Output schema for recipe records."""
    id: int
    name: str
    description: str
    instructions: str
    model_config = {"from_attributes": True}