from datetime import date
from typing import List

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Food
class FoodItemOut(BaseModel):
    """Output schema for a food item.
    
    Attributes:
        id: Unique identifier for the food item.
        name: Name of the food.
        calories_per_100g: Total calories per 100g.
        protein_per_100g: Protein in grams per 100g.
        fat_per_100g: Fat in grams per 100g.
        carbs_per_100g: Carbohydrates in grams per 100g.
    """
    id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    model_config = {"from_attributes": True}

# Create New Food
class FoodCreate(BaseModel):
    """Input schema for creating a new food item.
    
    Attributes:
        name: Name of the food.
        calories_per_100g: Total calories per 100g.
        protein_per_100g: Protein in grams per 100g.
        fat_per_100g: Fat in grams per 100g.
        carbs_per_100g: Carbohydrates in grams per 100g.
    """
    name: str
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float

# Target
class TargetOut(BaseModel):
    """Output schema for nutrition targets.
    
    Attributes:
        calories: Daily calorie target.
        protein: Daily protein target in grams.
        fat: Daily fat target in grams.
        carbs: Daily carbohydrates target in grams.
    """
    calories: float
    protein: float
    fat: float
    carbs: float
    model_config = {"from_attributes": True}

class TargetUpdate(BaseModel):
    """Input schema for updating nutrition targets.
    
    Attributes:
        calories: Daily calorie target.
        protein: Daily protein target in grams.
        fat: Daily fat target in grams.
        carbs: Daily carbohydrates target in grams.
    """
    calories: float
    protein: float
    fat: float
    carbs: float

# Meal
class MealCreate(BaseModel):
    """Input schema for creating a meal.
    
    Attributes:
        date: Date of the meal (ISO format).
        name: Type of meal (e.g., breakfast, lunch, dinner).
        food_id: ID of the food item.
        quantity: Quantity of food in grams.
    """
    date: date
    name: str          # 对应 meal_type
    food_id: int
    quantity: float

class MealOut(BaseModel):
    """Output schema for a meal with nutritional breakdown.
    
    Attributes:
        id: Unique identifier for the meal.
        name: Type of meal.
        food_name: Name of the food item.
        quantity: Quantity in grams.
        calories: Total calories for this serving.
        protein: Total protein in grams.
        fat: Total fat in grams.
        carbs: Total carbohydrates in grams.
    """
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
    """Daily summary of meals and nutrition totals.
    
    Attributes:
        date: Date of the summary.
        total: Dictionary with total calories, protein, fat, and carbs.
        meals: List of meals for this day.
    """
    date: date
    total: dict        # {"calories": float, "protein": ..., "fat": ..., "carbs": ...}
    meals: List[MealOut]

class DailyStat(BaseModel):
    """Daily nutrition statistics for a single day.
    
    Attributes:
        date: Date of the statistics.
        day_name: Short day name (e.g., Mon, Tue).
        calories: Total calories for the day.
        protein: Total protein in grams.
        fat: Total fat in grams.
        carbs: Total carbohydrates in grams.
    """
    date: date
    day_name: str
    calories: float
    protein: float
    fat: float
    carbs: float

class WeekSummary(BaseModel):
    """Weekly summary of nutrition statistics.
    
    Attributes:
        week_start: ISO date of the first day of the week.
        week_end: ISO date of the last day of the week.
        daily_stats: List of DailyStat objects for each day.
    """
    week_start: date
    week_end: date
    daily_stats: List[DailyStat]

# Recipes
class RecipeOut(BaseModel):
    """Output schema for a recipe.
    
    Attributes:
        id: Unique identifier for the recipe.
        name: Name of the recipe.
        description: Brief description of the recipe.
        instructions: Step-by-step cooking instructions.
    """
    id: int
    name: str
    description: str
    instructions: str
    model_config = {"from_attributes": True}