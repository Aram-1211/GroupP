from sqlalchemy.orm import Session
from datetime import date, timedelta
from models import User, UserTarget, FoodItem, Meal, MealEntry, Recipe
from schemas import MealCreate, TargetUpdate, MealOut, DaySummary, DailyStat, WeekSummary
import math

def get_user(db: Session, user_id: int = 1):
    return db.query(User).filter(User.id == user_id).first()

def get_target(db: Session, user_id: int = 1):
    user = get_user(db, user_id)
    if not user or not user.target:
        return None
    return user.target

def update_target(db: Session, target_data: TargetUpdate, user_id: int = 1):
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
    query = db.query(FoodItem)
    if search:
        query = query.filter(FoodItem.name.ilike(f"%{search}%"))
    return query.all()

def create_food(db: Session, food_data):
    protein = food_data.protein_per_100g * 4
    fat = food_data.fat_per_100g * 9
    carbs = food_data.carbs_per_100g * 4
    calories = protein + fat + carbs

    food = FoodItem(
        name=food_data.name,
        calories_per_100g=calories,
        protein_per_100g=food_data.protein_per_100g,
        fat_per_100g=food_data.fat_per_100g,
        carbs_per_100g=food_data.carbs_per_100g
    )
    db.add(food)
    db.commit()
    db.refresh(food)
    return food 

def create_meal(db: Session, meal_data: MealCreate, user_id: int = 1):
    meal = Meal(date=meal_data.date, meal_type=meal_data.name, user_id=user_id)
    db.add(meal)
    db.flush()  # get meal.id
    entry = MealEntry(meal_id=meal.id, food_id=meal_data.food_id, quantity_grams=meal_data.quantity)
    db.add(entry)
    db.commit()
    db.refresh(meal)
    return meal

def get_meals_by_day(db: Session, day: date, user_id: int = 1):
    meals = db.query(Meal).filter(Meal.date == day, Meal.user_id == user_id).all()
    total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    meal_list = []
    for meal in meals:
        for entry in meal.entries:
            food = entry.food
            q = entry.quantity_grams / 100
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
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user_id).first()
    if meal:
        db.delete(meal)
        db.commit()
        return True
    return False

def get_week_stats(db: Session, week_start: date, user_id: int = 1):
    week_end = week_start + timedelta(days=6)
    daily_stats = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        summary = get_meals_by_day(db, day, user_id)
        day_name = day.strftime("%A")[:3]  # Mon, Tue...
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
    return db.query(Recipe).all()