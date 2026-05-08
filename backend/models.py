"""ORM models for the application.

This module defines SQLAlchemy ORM models used by the backend,
including users, targets, food items, meals, meal entries, and recipes.
"""

from database import Base
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    """Represents an application user.

    Attributes:
        id: Primary key for the user.
        name: Display name for the user.
        target: One-to-one relationship to `UserTarget`.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Default User")
    target = relationship("UserTarget", back_populates="user", uselist=False)


class UserTarget(Base):
    """Stores a user's daily nutrition targets.

    Attributes:
        calories, protein, fat, carbs: Nutritional target values.
        user_id: FK to the owning `User`.
    """
    __tablename__ = "user_targets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    calories = Column(Float, default=2000)
    protein = Column(Float, default=50)
    fat = Column(Float, default=65)
    carbs = Column(Float, default=250)
    user = relationship("User", back_populates="target")


class FoodItem(Base):
    """A food item with nutrition per 100g.

    Attributes include name and macronutrient information per 100 grams.
    """
    __tablename__ = "food_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    carbs_per_100g = Column(Float)


class Meal(Base):
    """A meal instance for a user on a specific date.

    `meal_type` maps to the frontend's meal name. Each meal has multiple entries.
    """
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    date = Column(Date)
    meal_type = Column(String)
    entries = relationship("MealEntry", back_populates="meal", cascade="all, delete-orphan")


class MealEntry(Base):
    """A single food entry within a meal.

    Stores the food reference and quantity in grams.
    """
    __tablename__ = "meal_entries"
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"))
    food_id = Column(Integer, ForeignKey("food_items.id"))
    quantity_grams = Column(Float)
    meal = relationship("Meal", back_populates="entries")
    food = relationship("FoodItem")


class Recipe(Base):
    """Simple recipe record with name, description and instructions."""
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    instructions = Column(String)
