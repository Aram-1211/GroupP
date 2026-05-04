from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Default User")
    target = relationship("UserTarget", back_populates="user", uselist=False)

class UserTarget(Base):
    __tablename__ = "user_targets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    calories = Column(Float, default=2000)
    protein = Column(Float, default=50)
    fat = Column(Float, default=65)
    carbs = Column(Float, default=250)
    user = relationship("User", back_populates="target")

class FoodItem(Base):
    __tablename__ = "food_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    carbs_per_100g = Column(Float)

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    date = Column(Date)
    meal_type = Column(String)  # 前端发送的 "name"
    entries = relationship("MealEntry", back_populates="meal", cascade="all, delete-orphan")

class MealEntry(Base):
    __tablename__ = "meal_entries"
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"))
    food_id = Column(Integer, ForeignKey("food_items.id"))
    quantity_grams = Column(Float)
    meal = relationship("Meal", back_populates="entries")
    food = relationship("FoodItem")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    instructions = Column(String)