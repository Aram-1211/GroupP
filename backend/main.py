from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
from routers import foods, meals, stats, recipes
from models import *  # noqa: Ensure table registration
from sqlalchemy.orm import Session
from models import User, UserTarget, FoodItem, Recipe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create table
Base.metadata.create_all(bind=engine)

# Initialize seed data (if the database is empty)
def init_data():
    db: Session = next(get_db())
    if db.query(User).count() == 0:
        user = User(name="Default User")
        db.add(user)
        db.flush()
        target = UserTarget(user_id=user.id, calories=2000, protein=50, fat=65, carbs=250)
        db.add(target)
        db.commit()
    if db.query(FoodItem).count() == 0:
        foods = [
            FoodItem(name="Egg", calories_per_100g=155, protein_per_100g=13, fat_per_100g=11, carbs_per_100g=1.1),
            FoodItem(name="Chicken Breast", calories_per_100g=165, protein_per_100g=31, fat_per_100g=3.6, carbs_per_100g=0),
            FoodItem(name="White Rice (cooked)", calories_per_100g=130, protein_per_100g=2.7, fat_per_100g=0.3, carbs_per_100g=28),
            FoodItem(name="Olive Oil", calories_per_100g=884, protein_per_100g=0, fat_per_100g=100, carbs_per_100g=0),
            FoodItem(name="Banana", calories_per_100g=89, protein_per_100g=1.1, fat_per_100g=0.3, carbs_per_100g=23),
            FoodItem(name="Milk (whole)", calories_per_100g=61, protein_per_100g=3.2, fat_per_100g=3.3, carbs_per_100g=4.8),
            FoodItem(name="Bread (white)", calories_per_100g=265, protein_per_100g=9, fat_per_100g=3.2, carbs_per_100g=49),
            FoodItem(name="Salmon", calories_per_100g=208, protein_per_100g=20, fat_per_100g=13, carbs_per_100g=0),
        ]
        db.add_all(foods)
        db.commit()
    if db.query(Recipe).count() == 0:
        recipes = [
            Recipe(
                name="Simple Chicken Salad",
                description="A quick, healthy salad with grilled chicken.",
                instructions="1. Grill chicken breast and slice.\n2. Mix with lettuce, tomatoes, and cucumber.\n3. Drizzle with olive oil and lemon juice."
            ),
            Recipe(
                name="Banana Oat Pancakes",
                description="Easy pancakes using banana and oats.",
                instructions="1. Mash 1 banana.\n2. Mix with 1 cup oats, 1 egg, and a splash of milk.\n3. Fry in a non-stick pan."
            )
        ]
        db.add_all(recipes)
        db.commit()
    db.close()

init_data()

# Register Route
app.include_router(foods.router)
app.include_router(meals.router)
app.include_router(stats.router)
app.include_router(recipes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)