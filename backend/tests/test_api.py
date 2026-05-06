import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import models  # noqa: E402
from database import Base  # noqa: E402
from routers.foods import list_foods  # noqa: E402
from routers.meals import add_meal, get_day_summary, remove_meal  # noqa: E402
from routers.stats import get_target, get_week, update_target  # noqa: E402
from schemas import MealCreate, TargetUpdate  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402


def make_session():
    """Create an in-memory SQLite session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False,
        bind=engine
    )
    return SessionLocal()


def test_api_endpoints_flow():
    """Test API endpoints through router functions."""
    session = make_session()
    # seed minimal user and food
    user = models.User(name="APIUser")
    session.add(user)
    session.commit()
    session.refresh(user)

    food = models.FoodItem(
        name="APIApple", calories_per_100g=52,
        protein_per_100g=0.3, fat_per_100g=0.2,
        carbs_per_100g=14
    )
    session.add(food)
    session.commit()
    session.refresh(food)

    # Test list_foods endpoint
    foods_list = list_foods(search="API", db=session)
    assert any("APIApple" in f.name for f in foods_list)

    # Add a meal via router function
    mc = MealCreate(
        date=date.today(), name="Lunch", food_id=food.id,
        quantity=100
    )
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
    new_t = TargetUpdate(calories=1500, protein=70, fat=50, carbs=180)
    updated = update_target(new_t, db=session)
    assert updated.calories == 1500

    # week stats
    week = get_week(date.today().isoformat(), db=session)
    assert hasattr(week, "daily_stats")
