"""CRUD helper functions for database operations.

This module contains functions used by API endpoints to query and
manipulate user data, foods, meals and recipes.
"""

from sqlalchemy.orm import Session
from datetime import date, timedelta
from models import User, UserTarget, FoodItem, Meal, MealEntry, Recipe
from schemas import MealCreate, TargetUpdate, MealOut, DaySummary, DailyStat, WeekSummary
import math


def get_user(db: Session, user_id: int = 1):
    """Return a `User` by id (defaults to user 1)."""
    return db.query(User).filter(User.id == user_id).first()

def get_target(db: Session, user_id: int = 1):
    """Get a user's `UserTarget` or None if not set."""
    user = get_user(db, user_id)
    if not user or not user.target:
        return None
    return user.target

def update_target(db: Session, target_data: TargetUpdate, user_id: int = 1):
    """Create or update a user's nutrition target from `TargetUpdate`.

    Returns the created/updated `UserTarget` instance.
    """
    target = get_target(db, user_id)
    if not target:
        target = UserTarget(user_id=user_id, **target_data.model_dump())
        db.add(target)
        db.commit()
        db.refresh(target)
        return target
    for field, value in target_data.model_dump().items():
        setattr(target, field, value)
    db.commit()
    db.refresh(target)
    return target

def get_foods(db: Session, search: str = None):
    """Return a list of `FoodItem` optionally filtered by name (case-insensitive)."""
    query = db.query(FoodItem)
    if search:
        query = query.filter(FoodItem.name.ilike(f"%{search}%"))
    return query.all()

def create_meal(db: Session, meal_data: MealCreate, user_id: int = 1):
    """Create a `Meal` and a single `MealEntry` from `MealCreate`.

    Returns the created `Meal` instance.
    """
    meal = Meal(date=meal_data.date, meal_type=meal_data.name, user_id=user_id)
    db.add(meal)
    db.flush()  # populate meal.id after insert
    entry = MealEntry(meal_id=meal.id, food_id=meal_data.food_id, quantity_grams=meal_data.quantity)
    db.add(entry)
    db.commit()
    db.refresh(meal)
    return meal

def get_meals_by_day(db: Session, day: date, user_id: int = 1):
    """Aggregate meals for a given day and return a `DaySummary`.

    Computes macronutrient totals and returns a `DaySummary` schema object.
    """
    meals = db.query(Meal).filter(Meal.date == day, Meal.user_id == user_id).all()
    total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    meal_list = []
    for meal in meals:
        for entry in meal.entries:
            food = entry.food
            # Convert the per-100g nutrition values to the actual serving size.
            # `quantity_grams` is the recorded serving size in grams; dividing by
            # 100 gives the multiplier to apply to the per-100g nutrition fields.
            q = entry.quantity_grams / 100
            # Multiply per-100g values by the multiplier to get per-serving values.
            calorie = food.calories_per_100g * q
            protein = food.protein_per_100g * q
            fat = food.fat_per_100g * q
            carbs = food.carbs_per_100g * q
            total["calories"] += calorie
            total["protein"] += protein
            total["fat"] += fat
            total["carbs"] += carbs
            meal_list.append(MealOut(
                id=meal.id,
                name=meal.meal_type,
                food_name=food.name,
                quantity=entry.quantity_grams,
                calories=round(calorie, 1),
                protein=round(protein, 1),
                fat=round(fat, 1),
                carbs=round(carbs, 1)
            ))
    return DaySummary(date=day, total=total, meals=meal_list)

def delete_meal(db: Session, meal_id: int, user_id: int = 1):
    """Delete a meal owned by `user_id`. Returns True if deleted."""
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user_id).first()
    if meal:
        db.delete(meal)
        db.commit()
        return True
    return False

def get_week_stats(db: Session, week_start: date, user_id: int = 1):
    """Return `WeekSummary` for the week starting at `week_start`.

    Aggregates daily statistics for seven days starting from `week_start`.
    """
    week_end = week_start + timedelta(days=6)
    daily_stats = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        summary = get_meals_by_day(db, day, user_id)
        # Use a short weekday label for compact chart/table display.
        day_name = day.strftime("%A")[:3]
        # Round aggregated totals to one decimal place for consistent UI display
        # and to avoid floating point noise in charts or reports.
        daily_stats.append(DailyStat(
            date=day,
            day_name=day_name,
            calories=round(summary.total["calories"], 1),
            protein=round(summary.total["protein"], 1),
            fat=round(summary.total["fat"], 1),
            carbs=round(summary.total["carbs"], 1)
        ))
    return WeekSummary(week_start=week_start, week_end=week_end, daily_stats=daily_stats)

def get_recipes(db: Session):
    """Return all `Recipe` records."""
    return db.query(Recipe).all()