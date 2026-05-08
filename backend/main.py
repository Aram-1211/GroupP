from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base, get_db
from routers import foods, meals, stats, recipes
from models import *  # noqa: Ensure table registration
from sqlalchemy.orm import Session
from models import User, UserTarget, FoodItem, Recipe
import os

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
    from database import SessionLocal
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            user = User(name="Default User")
            db.add(user)
            db.flush()
            target = UserTarget(user_id=user.id, calories=2000, protein=50, fat=65, carbs=250)
            db.add(target)
            db.commit()
        if db.query(FoodItem).count() == 0:
            foods = [
                # Academic Honesty Disclaimer: These food items were generated using Generative AI in order to create a comprehensive list of basic food items for the user
                # Proteins
                FoodItem(name="Egg Whole", calories_per_100g=155, protein_per_100g=13, fat_per_100g=11, carbs_per_100g=1.1),
                FoodItem(name="Egg White", calories_per_100g=52, protein_per_100g=11, fat_per_100g=0.2, carbs_per_100g=0.7),
                FoodItem(name="Chicken Breast Raw", calories_per_100g=165, protein_per_100g=31, fat_per_100g=3.6, carbs_per_100g=0),
                FoodItem(name="Chicken Thigh Raw", calories_per_100g=177, protein_per_100g=24, fat_per_100g=8, carbs_per_100g=0),
                FoodItem(name="Chicken Drumstick Raw", calories_per_100g=172, protein_per_100g=28, fat_per_100g=6, carbs_per_100g=0),
                FoodItem(name="Turkey Breast Raw", calories_per_100g=114, protein_per_100g=24, fat_per_100g=1.5, carbs_per_100g=0),
                FoodItem(name="Turkey Mince Raw", calories_per_100g=189, protein_per_100g=27, fat_per_100g=8, carbs_per_100g=0),
                FoodItem(name="Beef Sirloin Steak Raw", calories_per_100g=206, protein_per_100g=23, fat_per_100g=12, carbs_per_100g=0),
                FoodItem(name="Beef Ribeye Steak Raw", calories_per_100g=291, protein_per_100g=24, fat_per_100g=21, carbs_per_100g=0),
                FoodItem(name="Beef Tenderloin Steak Raw", calories_per_100g=187, protein_per_100g=21, fat_per_100g=11, carbs_per_100g=0),
                FoodItem(name="Beef Mince 5 Percent Fat Raw", calories_per_100g=137, protein_per_100g=21, fat_per_100g=5, carbs_per_100g=0),
                FoodItem(name="Beef Mince 10 Percent Fat Raw", calories_per_100g=217, protein_per_100g=26, fat_per_100g=12, carbs_per_100g=0),
                FoodItem(name="Lamb Leg Raw", calories_per_100g=206, protein_per_100g=20, fat_per_100g=14, carbs_per_100g=0),
                FoodItem(name="Lamb Chops Raw", calories_per_100g=282, protein_per_100g=25, fat_per_100g=20, carbs_per_100g=0),
                FoodItem(name="Salmon Raw", calories_per_100g=208, protein_per_100g=20, fat_per_100g=13, carbs_per_100g=0),
                FoodItem(name="Tuna Raw", calories_per_100g=132, protein_per_100g=29, fat_per_100g=1, carbs_per_100g=0),
                FoodItem(name="Cod Raw", calories_per_100g=82, protein_per_100g=18, fat_per_100g=0.7, carbs_per_100g=0),
                FoodItem(name="Shrimp Raw", calories_per_100g=99, protein_per_100g=24, fat_per_100g=0.3, carbs_per_100g=0.2),
                FoodItem(name="Sardines", calories_per_100g=208, protein_per_100g=25, fat_per_100g=11, carbs_per_100g=0),
                FoodItem(name="Greek Yogurt Plain", calories_per_100g=59, protein_per_100g=10, fat_per_100g=0.4, carbs_per_100g=3.6),
                FoodItem(name="Cottage Cheese", calories_per_100g=98, protein_per_100g=11, fat_per_100g=4.3, carbs_per_100g=3.4),
                FoodItem(name="Cheddar Cheese", calories_per_100g=402, protein_per_100g=25, fat_per_100g=33, carbs_per_100g=1.3),
                FoodItem(name="Mozzarella Cheese", calories_per_100g=280, protein_per_100g=28, fat_per_100g=17, carbs_per_100g=3.1),
                FoodItem(name="Halloumi Cheese", calories_per_100g=321, protein_per_100g=22, fat_per_100g=25, carbs_per_100g=2.2),
                FoodItem(name="Milk Whole", calories_per_100g=61, protein_per_100g=3.2, fat_per_100g=3.3, carbs_per_100g=4.8),
                FoodItem(name="Milk Skimmed", calories_per_100g=34, protein_per_100g=3.4, fat_per_100g=0.1, carbs_per_100g=5),
                FoodItem(name="Whey Protein Powder", calories_per_100g=400, protein_per_100g=80, fat_per_100g=7, carbs_per_100g=8),

                # Carbohydrates
                FoodItem(name="White Rice Cooked", calories_per_100g=130, protein_per_100g=2.7, fat_per_100g=0.3, carbs_per_100g=28),
                FoodItem(name="Brown Rice Cooked", calories_per_100g=123, protein_per_100g=2.7, fat_per_100g=1, carbs_per_100g=25),
                FoodItem(name="Basmati Rice Cooked", calories_per_100g=121, protein_per_100g=3.5, fat_per_100g=0.4, carbs_per_100g=25),
                FoodItem(name="Jasmine Rice Cooked", calories_per_100g=129, protein_per_100g=2.9, fat_per_100g=0.4, carbs_per_100g=28),
                FoodItem(name="White Pasta Cooked", calories_per_100g=157, protein_per_100g=5.8, fat_per_100g=0.9, carbs_per_100g=31),
                FoodItem(name="Whole Wheat Pasta Cooked", calories_per_100g=149, protein_per_100g=5.5, fat_per_100g=1.1, carbs_per_100g=30),
                FoodItem(name="Oats", calories_per_100g=389, protein_per_100g=17, fat_per_100g=7, carbs_per_100g=66),
                FoodItem(name="Granola", calories_per_100g=471, protein_per_100g=10, fat_per_100g=20, carbs_per_100g=64),
                FoodItem(name="Potato", calories_per_100g=77, protein_per_100g=2, fat_per_100g=0.1, carbs_per_100g=17),
                FoodItem(name="Sweet Potato", calories_per_100g=86, protein_per_100g=1.6, fat_per_100g=0.1, carbs_per_100g=20),
                FoodItem(name="Bread White", calories_per_100g=265, protein_per_100g=9, fat_per_100g=3.2, carbs_per_100g=49),
                FoodItem(name="Bread Wholemeal", calories_per_100g=247, protein_per_100g=13, fat_per_100g=4.2, carbs_per_100g=41),
                FoodItem(name="Bagel Plain", calories_per_100g=250, protein_per_100g=10, fat_per_100g=1.5, carbs_per_100g=49),
                FoodItem(name="Rice Cakes", calories_per_100g=387, protein_per_100g=8, fat_per_100g=3, carbs_per_100g=81),
                FoodItem(name="Corn Flakes", calories_per_100g=357, protein_per_100g=7.5, fat_per_100g=0.4, carbs_per_100g=84),

                # Fruits
                FoodItem(name="Banana", calories_per_100g=89, protein_per_100g=1.1, fat_per_100g=0.3, carbs_per_100g=23),
                FoodItem(name="Apple", calories_per_100g=52, protein_per_100g=0.3, fat_per_100g=0.2, carbs_per_100g=14),
                FoodItem(name="Blueberries", calories_per_100g=57, protein_per_100g=0.7, fat_per_100g=0.3, carbs_per_100g=14),
                FoodItem(name="Strawberries", calories_per_100g=32, protein_per_100g=0.7, fat_per_100g=0.3, carbs_per_100g=7.7),
                FoodItem(name="Raspberries", calories_per_100g=52, protein_per_100g=1.2, fat_per_100g=0.7, carbs_per_100g=12),
                FoodItem(name="Orange", calories_per_100g=47, protein_per_100g=0.9, fat_per_100g=0.1, carbs_per_100g=12),
                FoodItem(name="Mango", calories_per_100g=60, protein_per_100g=0.8, fat_per_100g=0.4, carbs_per_100g=15),
                FoodItem(name="Pineapple", calories_per_100g=50, protein_per_100g=0.5, fat_per_100g=0.1, carbs_per_100g=13),
                FoodItem(name="Watermelon", calories_per_100g=30, protein_per_100g=0.6, fat_per_100g=0.2, carbs_per_100g=8),
                FoodItem(name="Dates", calories_per_100g=282, protein_per_100g=2.5, fat_per_100g=0.4, carbs_per_100g=75),
                FoodItem(name="Avocado", calories_per_100g=160, protein_per_100g=2, fat_per_100g=15, carbs_per_100g=9),

                # Vegetables
                FoodItem(name="Broccoli", calories_per_100g=35, protein_per_100g=2.4, fat_per_100g=0.4, carbs_per_100g=7),
                FoodItem(name="Spinach", calories_per_100g=23, protein_per_100g=2.9, fat_per_100g=0.4, carbs_per_100g=3.6),
                FoodItem(name="Tomato", calories_per_100g=18, protein_per_100g=0.9, fat_per_100g=0.2, carbs_per_100g=3.9),
                FoodItem(name="Cucumber", calories_per_100g=15, protein_per_100g=0.7, fat_per_100g=0.1, carbs_per_100g=3.6),
                FoodItem(name="Onion", calories_per_100g=40, protein_per_100g=1.1, fat_per_100g=0.1, carbs_per_100g=9.3),
                FoodItem(name="Lettuce", calories_per_100g=15, protein_per_100g=1.4, fat_per_100g=0.2, carbs_per_100g=2.9),
                FoodItem(name="Carrot", calories_per_100g=41, protein_per_100g=0.9, fat_per_100g=0.2, carbs_per_100g=10),
                FoodItem(name="Bell Pepper", calories_per_100g=31, protein_per_100g=1, fat_per_100g=0.3, carbs_per_100g=6),
                FoodItem(name="Mushrooms", calories_per_100g=22, protein_per_100g=3.1, fat_per_100g=0.3, carbs_per_100g=3.3),
                FoodItem(name="Zucchini", calories_per_100g=17, protein_per_100g=1.2, fat_per_100g=0.3, carbs_per_100g=3.1),

                # Fats / Nuts / Extras
                FoodItem(name="Olive Oil", calories_per_100g=884, protein_per_100g=0, fat_per_100g=100, carbs_per_100g=0),
                FoodItem(name="Butter", calories_per_100g=717, protein_per_100g=0.9, fat_per_100g=81, carbs_per_100g=0.1),
                FoodItem(name="Peanut Butter", calories_per_100g=588, protein_per_100g=25, fat_per_100g=50, carbs_per_100g=20),
                FoodItem(name="Almonds", calories_per_100g=579, protein_per_100g=21, fat_per_100g=50, carbs_per_100g=22),
                FoodItem(name="Walnuts", calories_per_100g=654, protein_per_100g=15, fat_per_100g=65, carbs_per_100g=14),
                FoodItem(name="Cashews", calories_per_100g=553, protein_per_100g=18, fat_per_100g=44, carbs_per_100g=30),
                FoodItem(name="Dark Chocolate 70 Percent", calories_per_100g=598, protein_per_100g=8, fat_per_100g=43, carbs_per_100g=46),
                FoodItem(name="Honey", calories_per_100g=304, protein_per_100g=0.3, fat_per_100g=0, carbs_per_100g=82)
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
    finally:
        db.close()

init_data()

# Register Route (must be before static files mount)
app.include_router(foods.router)
app.include_router(meals.router)
app.include_router(stats.router)
app.include_router(recipes.router)

# Mount static files (last, as catch-all)
app.mount("/", StaticFiles(directory=os.path.dirname(__file__), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)