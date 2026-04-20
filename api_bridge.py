# -*- coding: utf-8 -*-
"""
api_bridge.py — REST API bridge for Base44 migration.
Exposes all db.py data + handler.py logic over HTTP as clean JSON.

Run:
    uvicorn api_bridge:app --reload --port 8000

Docs (auto-generated):
    http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List

import db
import handler
from handler import RECIPES, _target, _tdee, estimate_nutrition

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Nutrition Bot API",
    description="REST bridge for Base44 — wraps db.py and handler.py",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

security = HTTPBearer()


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validates Bearer token (stored in remember_tokens table).
    Returns the phone/uid on success, raises 401 otherwise.
    """
    token = creds.credentials
    phone = db.verify_remember_token(token)
    if not phone:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")
    return phone


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class UpdateProfileRequest(BaseModel):
    weight_kg:     Optional[float] = None
    disliked_foods: Optional[str]  = None
    is_kosher:     Optional[int]   = None   # 1 or 0
    carb_pref:     Optional[str]   = None   # "carbs" | "fats"
    spice_pref:    Optional[str]   = None   # "spicy" | "mild"

class LogMealRequest(BaseModel):
    meal_id:   str
    meal_name: str
    meal_type: str = "pareve"   # "meat" | "dairy" | "pareve"
    category:  str              # "breakfast" | "lunch" | "dinner" | "snack"
    calories:  int = 0

class LogWeightRequest(BaseModel):
    weight_kg: float

class FeedPostRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class ShareRecipeRequest(BaseModel):
    name:         str
    description:  Optional[str]  = ""
    ingredients:  str
    instructions: Optional[str]  = ""
    category:     str = "lunch"  # breakfast | lunch | dinner | snack
    calories:     int = 0
    protein:      int = 0
    carbs:        int = 0
    fat:          int = 0
    media_url:    Optional[str]  = ""
    prep_time:    Optional[str]  = ""
    difficulty:   Optional[str]  = ""   # "" | "קל" | "בינוני" | "קשה"

class EstimateNutritionRequest(BaseModel):
    ingredients_text: str


# ---------------------------------------------------------------------------
# AUTH endpoints  /auth/*
# ---------------------------------------------------------------------------

@app.post("/auth/login", tags=["Auth"])
def login(body: LoginRequest):
    """
    Authenticate with username + password.
    Returns a Bearer token valid for 30 days.
    """
    ok, result = db.authenticate(body.username, body.password)
    if not ok:
        raise HTTPException(status_code=401, detail=result)
    phone = result
    token = db.create_remember_token(phone)
    username = db.get_username_by_phone(phone)
    user = db.get_user(phone)
    return {
        "token":    token,
        "phone":    phone,
        "username": username,
        "profile_complete": user.get("state") == "COMPLETED" if user else False,
    }


@app.post("/auth/register", tags=["Auth"])
def register(body: RegisterRequest):
    """
    Create a new account.
    Returns a Bearer token so the caller can immediately set up the profile.
    """
    ok, result = db.create_account(body.username, body.password)
    if not ok:
        raise HTTPException(status_code=400, detail=result)
    phone = result
    token = db.create_remember_token(phone)
    return {
        "token":    token,
        "phone":    phone,
        "username": body.username.strip().lower(),
        "profile_complete": False,
    }


@app.post("/auth/logout", tags=["Auth"])
def logout(phone: str = Depends(get_current_user),
           creds: HTTPAuthorizationCredentials = Depends(security)):
    """Revoke the current Bearer token."""
    db.delete_remember_token(creds.credentials)
    return {"ok": True}


# ---------------------------------------------------------------------------
# USER endpoints  /users/*
# ---------------------------------------------------------------------------

@app.get("/users/me", tags=["Users"])
def get_me(phone: str = Depends(get_current_user)):
    """Return the full profile of the authenticated user."""
    user = db.get_user(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    username = db.get_username_by_phone(phone)
    target_cal = int(_target(user)) if user.get("state") == "COMPLETED" else None
    return {**user, "username": username, "target_cal": target_cal}


@app.patch("/users/me", tags=["Users"])
def update_me(body: UpdateProfileRequest, phone: str = Depends(get_current_user)):
    """Update editable profile fields (weight, kosher, preferences, etc.)."""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "weight_kg" in updates:
        new_tdee = None
        user = db.get_user(phone)
        if user and user.get("height_cm") and user.get("age") and user.get("sex"):
            new_tdee = int(_tdee(updates["weight_kg"], float(user["height_cm"]),
                                 int(user["age"]), str(user["sex"]),
                                 int(user.get("activity", 2))))
        db.log_weight(phone, updates["weight_kg"])
        if new_tdee:
            updates["tdee"] = new_tdee
    db.update_user(phone, **updates)
    return {"ok": True, "updated": list(updates.keys())}


# ---------------------------------------------------------------------------
# DAILY CALORIES  /users/me/calories
# ---------------------------------------------------------------------------

@app.get("/users/me/calories", tags=["Calories"])
def get_calories(phone: str = Depends(get_current_user)):
    """Return today's consumed calories and the daily target."""
    consumed = db.get_daily_calories(phone)
    user = db.get_user(phone)
    target = int(_target(user)) if user else 0
    return {
        "consumed": consumed,
        "target":   target,
        "remaining": max(target - consumed, 0),
        "pct": round(min(consumed / target, 1.0) * 100, 1) if target else 0,
    }


@app.post("/users/me/calories", tags=["Calories"])
def add_calories(amount: int, phone: str = Depends(get_current_user)):
    """Add `amount` calories to today's count."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")
    db.add_daily_calories(phone, amount)
    return {"ok": True, "added": amount}


# ---------------------------------------------------------------------------
# MEAL LOGS  /users/me/meals
# ---------------------------------------------------------------------------

@app.get("/users/me/meals", tags=["Meals"])
def get_today_meals(phone: str = Depends(get_current_user)):
    """Return all meal log entries for today."""
    return db.get_today_logs(phone)


@app.post("/users/me/meals", tags=["Meals"])
def log_meal(body: LogMealRequest, phone: str = Depends(get_current_user)):
    """Log a meal and add its calories to the daily total."""
    db.log_meal(phone, body.meal_id, body.meal_name,
                body.meal_type, body.category, body.calories)
    db.add_daily_calories(phone, body.calories)
    if body.meal_type == "meat":
        from datetime import datetime
        db.update_user(phone, last_meat_ts=datetime.utcnow().isoformat())
    return {"ok": True}


# ---------------------------------------------------------------------------
# WEIGHT  /users/me/weight
# ---------------------------------------------------------------------------

@app.get("/users/me/weight", tags=["Weight"])
def get_weight_history(days: int = 30, phone: str = Depends(get_current_user)):
    """Return weight log entries for the last `days` days (max 365)."""
    return db.get_weight_history(phone, days=min(days, 365))


@app.post("/users/me/weight", tags=["Weight"])
def log_weight(body: LogWeightRequest, phone: str = Depends(get_current_user)):
    """Add a new weight measurement."""
    db.log_weight(phone, body.weight_kg)
    return {"ok": True, "weight_kg": body.weight_kg}


# ---------------------------------------------------------------------------
# CALORIE HISTORY  /users/me/calorie-history
# ---------------------------------------------------------------------------

@app.get("/users/me/calorie-history", tags=["Calories"])
def get_calorie_history(days: int = 7, phone: str = Depends(get_current_user)):
    """Return daily calorie totals for the last `days` days."""
    return db.get_calorie_history(phone, days=min(days, 90))


# ---------------------------------------------------------------------------
# LOCAL RECIPES  /recipes/local
# ---------------------------------------------------------------------------

@app.get("/recipes/local", tags=["Recipes"])
def list_local_recipes(
    category: Optional[str] = None,
    phone: str = Depends(get_current_user),
):
    """
    Return all built-in local recipes from handler.RECIPES.
    Optionally filter by category: breakfast | lunch | dinner | snack.
    """
    user = db.get_user(phone)
    out = []
    for key, r in RECIPES.items():
        if category and r.get("cat") != category:
            continue
        out.append({
            "id":          key,
            "name":        r.get("name"),
            "category":    r.get("cat"),
            "calories":    r.get("cal", 0),
            "protein":     r.get("pro", 0),
            "carbs":       r.get("carb", 0),
            "fat":         r.get("fat", 0),
            "prep":        r.get("prep", ""),
            "type":        r.get("type", "pareve"),
            "ingredients": r.get("ingredients", []),
            "steps":       r.get("steps", []),
        })
    return out


# ---------------------------------------------------------------------------
# COMMUNITY RECIPES  /recipes/community
# ---------------------------------------------------------------------------

@app.get("/recipes/community", tags=["Community Recipes"])
def list_community_recipes(limit: int = 50, phone: str = Depends(get_current_user)):
    """Return shared community recipes, newest first."""
    liked_ids = set(db.get_liked_recipe_ids(phone))
    saved_ids = set(db.get_saved_recipe_ids(phone))
    recipes = db.get_community_recipes(min(limit, 200))
    for r in recipes:
        r["liked_by_me"] = r["id"] in liked_ids
        r["saved_by_me"] = r["id"] in saved_ids
    return recipes


@app.post("/recipes/community", tags=["Community Recipes"])
def share_recipe(body: ShareRecipeRequest, phone: str = Depends(get_current_user)):
    """Share a new community recipe."""
    username = db.get_username_by_phone(phone)
    db.share_recipe(
        phone, username,
        body.name, body.description or "",
        body.ingredients, body.instructions or "",
        body.category,
        body.calories, body.protein, body.carbs, body.fat,
        media_url=body.media_url or "",
        prep_time=body.prep_time or "",
        difficulty=body.difficulty or "",
    )
    return {"ok": True}


@app.get("/recipes/community/top", tags=["Community Recipes"])
def get_top_recipes(
    category: Optional[str] = None,
    limit: int = 3,
    phone: str = Depends(get_current_user),
):
    """Return top-liked community recipes, optionally filtered by category."""
    return db.get_top_community_recipes(category=category, limit=min(limit, 20))


@app.post("/recipes/community/{recipe_id}/like", tags=["Community Recipes"])
def toggle_like(recipe_id: int, phone: str = Depends(get_current_user)):
    """Toggle like on a community recipe. Returns new liked state."""
    db.toggle_like(recipe_id, phone)
    liked_ids = db.get_liked_recipe_ids(phone)
    return {"liked": recipe_id in liked_ids}


@app.post("/recipes/community/{recipe_id}/save", tags=["Community Recipes"])
def toggle_save(recipe_id: int, phone: str = Depends(get_current_user)):
    """Toggle save on a community recipe. Returns new saved state."""
    db.toggle_save(recipe_id, phone)
    saved_ids = db.get_saved_recipe_ids(phone)
    return {"saved": recipe_id in saved_ids}


@app.get("/users/me/recipes", tags=["Community Recipes"])
def my_recipes(phone: str = Depends(get_current_user)):
    """Return all recipes shared by the authenticated user."""
    return db.get_recipes_by_user(phone)


@app.get("/users/me/saved-recipes", tags=["Community Recipes"])
def saved_recipes(phone: str = Depends(get_current_user)):
    """Return all recipes saved by the authenticated user."""
    return db.get_saved_recipes(phone)


# ---------------------------------------------------------------------------
# COMMUNITY FEED  /feed
# ---------------------------------------------------------------------------

@app.get("/feed", tags=["Feed"])
def get_feed(limit: int = 40, phone: str = Depends(get_current_user)):
    """Return community feed posts, newest first."""
    return db.get_feed_posts(min(limit, 100))


@app.post("/feed", tags=["Feed"])
def create_post(body: FeedPostRequest, phone: str = Depends(get_current_user)):
    """Publish a new feed post."""
    username = db.get_username_by_phone(phone)
    db.add_feed_post(phone, username, body.content)
    return {"ok": True}


@app.delete("/feed/{post_id}", tags=["Feed"])
def delete_post(post_id: int, phone: str = Depends(get_current_user)):
    """Delete a feed post (only if it belongs to the authenticated user)."""
    db.delete_feed_post(post_id, phone)
    return {"ok": True}


@app.get("/users/me/posts", tags=["Feed"])
def my_posts(phone: str = Depends(get_current_user)):
    """Return all feed posts by the authenticated user."""
    return db.get_posts_by_user(phone)


# ---------------------------------------------------------------------------
# NUTRITION ESTIMATE  /nutrition/estimate
# ---------------------------------------------------------------------------

@app.post("/nutrition/estimate", tags=["Nutrition"])
def estimate(body: EstimateNutritionRequest, phone: str = Depends(get_current_user)):
    """
    Estimate macro breakdown from a free-text ingredients list.
    Example body: { "ingredients_text": "200g chicken, 1 avocado, 1 cup rice" }
    """
    cal, pro, carb, fat = estimate_nutrition(body.ingredients_text)
    return {"calories": cal, "protein": pro, "carbs": carb, "fat": fat}


# ---------------------------------------------------------------------------
# WATER TRACKING  /users/me/water
# ---------------------------------------------------------------------------

@app.get("/users/me/water", tags=["Water"])
def get_water(phone: str = Depends(get_current_user)):
    """Return today's water intake count."""
    from datetime import date
    user = db.get_user(phone)
    today = date.today().isoformat()
    cups = user.get("water_cups", 0) if user and user.get("water_date") == today else 0
    return {"cups": cups, "goal": 8}


@app.post("/users/me/water", tags=["Water"])
def add_water(phone: str = Depends(get_current_user)):
    """Add one cup of water to today's count."""
    db.add_water_cup(phone)
    return {"ok": True}
