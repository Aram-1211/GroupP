import sys
from datetime import date, timedelta
from pathlib import Path

import crud
from database import Base
from models import FoodItem, Recipe, User
from schemas import MealCreate, TargetUpdate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


def make_session():
    """Create an in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:",
                           connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False,
                                bind=engine)
    return SessionLocal()


def test_update_and_get_target():
    """Test updating and retrieving user targets."""
    db = make_session()
    # Create a user
    user = User(name="Tester")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Update target for user
    t = TargetUpdate(calories=1800, protein=60, fat=60, carbs=200)
    updated = crud.update_target(db, t, user_id=user.id)
    assert updated is not None
    assert updated.calories == 1800

    # Retrieve target
    got = crud.get_target(db, user_id=user.id)
    assert got is not None
    assert got.protein == 60


def test_create_meal_and_get_meals_by_day():
    """Test meal creation and daily summary."""
    db = make_session()
    # seed user and food
    user = User(name="MealUser")
    db.add(user)
    db.commit()
    db.refresh(user)

    food = FoodItem(name="TestFood", calories_per_100g=200,
                    protein_per_100g=10, fat_per_100g=5,
                    carbs_per_100g=20)
    db.add(food)
    db.commit()
    db.refresh(food)

    # Create a meal via crud
    mc = MealCreate(date=date.today(), name="Lunch", food_id=food.id,
                    quantity=150)
    meal = crud.create_meal(db, mc, user_id=user.id)
    assert meal is not None

    # Get meals by day and check totals
    summary = crud.get_meals_by_day(db, date.today(), user_id=user.id)
    assert summary is not None
    # 150g of TestFood -> 1.5 * 200 = 300 calories
    assert any(m.food_name == "TestFood" for m in summary.meals)
    assert round(summary.total["calories"]) == 300


def test_get_week_stats_and_delete_meal():
    """Test weekly stats and meal deletion."""
    db = make_session()
    # create user and food
    user = User(name="WeekUser")
    db.add(user)
    db.commit()
    db.refresh(user)

    food = FoodItem(name="WeekFood", calories_per_100g=100,
                    protein_per_100g=5, fat_per_100g=2,
                    carbs_per_100g=10)
    db.add(food)
    db.commit()
    db.refresh(food)

    # create meals on three different days within the same week
    today = date.today()
    for i in range(3):
        d = today - timedelta(days=i)
        mc = MealCreate(date=d, name=f"Meal{i}", food_id=food.id,
                        quantity=100)
        m = crud.create_meal(db, mc, user_id=user.id)

    week_start = today - timedelta(days=today.weekday())
    week = crud.get_week_stats(db, week_start, user_id=user.id)
    assert week is not None
    # there should be at least one DailyStat with non-zero calories
    assert any(ds.calories > 0 for ds in week.daily_stats)

    # delete one meal and ensure deletion returns True
    assert crud.delete_meal(db, m.id, user_id=user.id) is True
    # deleting again should return False
    assert crud.delete_meal(db, m.id, user_id=user.id) is False


def test_get_foods_and_recipes():
    """Test fetching foods and recipes."""
    db = make_session()
    # seed food and recipe
    f1 = FoodItem(name="Apple", calories_per_100g=52,
                  protein_per_100g=0.3, fat_per_100g=0.2,
                  carbs_per_100g=14)
    db.add(f1)
    r = Recipe(name="TestRecipe", description="Desc",
               instructions="Do things")
    db.add(r)
    db.commit()

    foods = crud.get_foods(db, search="App")
    assert any("Apple" in x.name for x in foods)

    recs = crud.get_recipes(db)
    assert any(isinstance(x, Recipe) for x in recs)
