import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
import models
from main import app
import crud


def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def override_get_db(session):
    def _get_db():
        try:
            yield session
        finally:
            pass
    return _get_db


def test_api_endpoints_flow():
    session = make_session()
    # seed minimal user and food
    user = models.User(name="APIUser")
    session.add(user)
    session.commit()
    session.refresh(user)

    food = models.FoodItem(name="APIApple", calories_per_100g=52, protein_per_100g=0.3, fat_per_100g=0.2, carbs_per_100g=14)
    session.add(food)
    session.commit()
    session.refresh(food)

    # Call router functions directly with the test session to avoid TestClient
    from routers.foods import list_foods
    from routers.meals import add_meal, get_day_summary, remove_meal
    from routers.stats import get_target, update_target, get_week

    foods_list = list_foods(search="API", db=session)
    assert any("APIApple" in f.name for f in foods_list)

    # Add a meal via router function
    from schemas import MealCreate
    mc = MealCreate(date=date.today(), name="Lunch", food_id=food.id, quantity=100)
    resp = add_meal(mc, db=session)
    assert resp.get("message") == "Meal created"

    # Get day summary
    summary = get_day_summary(date.today().isoformat(), db=session)
    assert summary.meals and summary.total["calories"] > 0

    # delete the created meal (get id from returned meals)
    meal_id = summary.meals[0].id
    deleted = remove_meal(meal_id, db=session)
    assert deleted.get("deleted") is True

    # Target endpoints: GET should create default if missing
    t = get_target(db=session)
    assert t.calories == 2000

    # Update target
    from schemas import TargetUpdate
    new_t = TargetUpdate(calories=1500, protein=70, fat=50, carbs=180)
    updated = update_target(new_t, db=session)
    assert updated.calories == 1500

    # week stats
    week = get_week(date.today().isoformat(), db=session)
    assert hasattr(week, "daily_stats")
