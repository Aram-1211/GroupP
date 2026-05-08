# GroupP

GroupP is a nutrition tracking web application built with FastAPI, SQLite, and a browser-based frontend served from the backend directory. It provides food search, meal logging, daily and weekly nutrition summaries, target management, and recipe browsing. This group #76 have TWO menbers only, Aram Ajib & Yiming Xu.

## Features

- Browse and search food items
- Log meals by date and meal type
- View daily meal summaries and weekly nutrition stats
- Read and update daily nutrition targets
- Browse built-in recipes
- Serve the frontend and API from the same FastAPI application

## Project Structure

- `backend/main.py` - application entry point and route registration
- `backend/crud.py` - database access helpers
- `backend/database.py` - SQLAlchemy engine and session setup
- `backend/models.py` - ORM models
- `backend/schemas.py` - Pydantic schemas
- `backend/routers/` - API route modules
- `backend/index.html`, `backend/app.js`, `backend/styles.css` - frontend assets
- `backend/tests/` - test suite

## Requirements

- Python 3.12 or newer
- pip

## Installation

Change into the backend directory and install the dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Running the Application

Start the application from the same directory:

```bash
python main.py
```

The app will be available at `http://0.0.0.0:8000`. In a browser, you can usually open `http://localhost:8000`.

## Testing

Run the test suite from the backend directory:

```bash
pytest
```

## API Overview

The backend exposes these main endpoints:

- `GET /api/foods/` - list food items, optionally filtered by search text
- `POST /api/foods/` - create a food item
- `POST /api/meals/` - create a meal entry
- `GET /api/meals/day/{date}` - get a daily summary
- `DELETE /api/meals/{meal_id}` - delete a meal
- `GET /api/target` - get the current nutrition target
- `PUT /api/target` - update the nutrition target
- `GET /api/stats/week/{week_start}` - get weekly nutrition statistics
- `GET /api/recipes/` - list recipes

## Data and Startup Behavior

- The application uses a local SQLite database at `backend/nutrition.db`.
- Database tables are created automatically on startup.
- Default user, nutrition target, foods, and recipes are seeded when the database is empty.

